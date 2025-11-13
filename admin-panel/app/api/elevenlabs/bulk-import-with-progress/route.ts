import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { verifyToken } from '@/lib/auth';
import { 
  generateOperationId, 
  createOperation, 
  updateProgress, 
  completeOperation, 
  failOperation,
  addError 
} from '@/lib/progressTracking';
import { getDb } from '@/lib/db';
import sql from 'mssql';
import { parallelLimit, chunk } from '@/lib/performance';

/**
 * POST /api/elevenlabs/bulk-import-with-progress
 * Import nhiều ElevenLabs keys với progress tracking
 */
export async function POST(request: NextRequest) {
  try {
    // Verify authentication
    const cookieStore = cookies();
    const token = cookieStore.get('auth_token')?.value;
    
    if (!token) {
      return NextResponse.json({ error: 'Not authenticated' }, { status: 401 });
    }

    const user = verifyToken(token);
    if (!user || user.role !== 'admin') {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 403 });
    }

    const body = await request.json();
    const { keys_text, assigned_user_id } = body;

    if (!keys_text) {
      return NextResponse.json({ error: 'keys_text is required' }, { status: 400 });
    }

    // Parse keys
    const keys = keys_text
      .split('\n')
      .map((line: string) => line.trim())
      .filter((line: string) => line.length > 0);

    if (keys.length === 0) {
      return NextResponse.json({ error: 'No keys found' }, { status: 400 });
    }

    // Create operation
    const operationId = generateOperationId('bulk_import');
    createOperation(operationId, keys.length);

    // Start processing in background (don't await)
    processKeysInBackground(operationId, keys, assigned_user_id, user.userId);

    // Return operation ID immediately
    return NextResponse.json({
      operationId,
      message: `Bắt đầu import ${keys.length} keys`,
      totalKeys: keys.length,
    });

  } catch (error) {
    console.error('Error starting bulk import:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * Process keys in background with parallel processing
 */
async function processKeysInBackground(
  operationId: string,
  keys: string[],
  assigned_user_id: number | undefined,
  created_by: number
) {
  const pool = await getDb();
  const processedKeys: string[] = [];
  const progressLock = { count: 0 };

  // Process keys in parallel (10 concurrent operations)
  const CONCURRENT_LIMIT = 10;

  // Helper to update progress atomically
  const updateProgressSafe = () => {
    progressLock.count++;
    updateProgress(
      operationId,
      progressLock.count,
      `Đang xử lý... ${progressLock.count}/${keys.length} keys`
    );
  };

  try {
    // Process each key in parallel with limit
    const results = await parallelLimit(
      keys.map((key, index) => ({ key, index })),
      async ({ key, index }) => {
        try {
          // Check if key already exists
          const existing = await pool.request()
            .input('api_key', sql.NVarChar(500), key)
            .query('SELECT id FROM elevenlabs_keys WHERE api_key = @api_key');

          if (existing.recordset.length > 0) {
            addError(operationId, key.substring(0, 10), 'Key đã tồn tại');
            updateProgressSafe();
            return { success: false, key, error: 'Key đã tồn tại' };
          }

          // Insert key
          const insertRequest = pool.request()
            .input('api_key', sql.NVarChar(500), key)
            .input('status', sql.NVarChar(20), 'active')
            .input('created_by', sql.Int, created_by);
          
          if (assigned_user_id) {
            insertRequest.input('assigned_user_id', sql.Int, assigned_user_id);
          } else {
            insertRequest.input('assigned_user_id', sql.Int, null);
          }
          
          const insertResult = await insertRequest.query(`
            INSERT INTO elevenlabs_keys 
            (api_key, assigned_user_id, status, created_by, created_at, updated_at)
            VALUES 
            (@api_key, @assigned_user_id, @status, @created_by, GETDATE(), GETDATE())
          `);

          // Verify insert was successful
          if (insertResult.rowsAffected[0] > 0) {
            processedKeys.push(key);
            updateProgressSafe();
            return { success: true, key };
          } else {
            throw new Error('Insert failed - no rows affected');
          }

        } catch (error: any) {
          console.error(`Error importing key ${key}:`, error);
          addError(operationId, key.substring(0, 10), error.message);
          updateProgressSafe();
          return { success: false, key, error: error.message };
        }
      },
      CONCURRENT_LIMIT
    );

    // Count results after all operations complete
    const successCount = results.filter(r => r?.success).length;
    const errorCount = results.filter(r => !r?.success).length;

    // Final progress update
    updateProgress(
      operationId,
      keys.length,
      `Đang xác minh... Đã xử lý ${keys.length}/${keys.length} keys (Thành công: ${successCount}, Lỗi: ${errorCount})`
    );

    // Verification step: Verify all successful keys were actually inserted
    let verifiedCount = successCount;
    if (processedKeys.length > 0) {
      try {
        // Build parameterized query for verification
        const verifyRequest = pool.request();
        const placeholders: string[] = [];
        processedKeys.forEach((k, idx) => {
          const paramName = `key${idx}`;
          verifyRequest.input(paramName, sql.NVarChar(500), k);
          placeholders.push(`@${paramName}`);
        });
        
        const verifyResult = await verifyRequest.query(`
          SELECT COUNT(*) as count 
          FROM elevenlabs_keys 
          WHERE api_key IN (${placeholders.join(', ')})
        `);
        
        verifiedCount = verifyResult.recordset[0]?.count || 0;
        
        if (verifiedCount !== successCount) {
          console.warn(`[Bulk Import] Verification mismatch: Expected ${successCount}, found ${verifiedCount}`);
        }
      } catch (verifyError) {
        console.error('Verification error (non-critical):', verifyError);
        // Don't fail the operation if verification fails
        verifiedCount = successCount; // Assume all were successful
      }
    }

    // Final progress update before completion
    updateProgress(
      operationId,
      keys.length,
      `Đang hoàn tất... Đã xử lý ${keys.length}/${keys.length} keys`
    );

    // Small delay to ensure all DB operations are committed
    await new Promise(resolve => setTimeout(resolve, 200));

    // Complete operation only after all items processed and verified
    completeOperation(
      operationId,
      `✅ Import hoàn thành! Thành công: ${successCount}${verifiedCount !== successCount ? ` (Đã xác minh: ${verifiedCount})` : ''}, Lỗi: ${errorCount}`
    );

  } catch (error: any) {
    console.error('Critical error in background processing:', error);
    failOperation(operationId, `Lỗi nghiêm trọng: ${error.message}`);
  }
}




