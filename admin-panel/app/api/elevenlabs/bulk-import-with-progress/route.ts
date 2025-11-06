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
 * Process keys in background
 */
async function processKeysInBackground(
  operationId: string,
  keys: string[],
  assigned_user_id: number | undefined,
  created_by: number
) {
  const pool = await getDb();
  let successCount = 0;
  let errorCount = 0;

  try {
    for (let i = 0; i < keys.length; i++) {
      const key = keys[i];
      
      try {
        // Update progress
        updateProgress(
          operationId,
          i + 1,
          `Đang import key ${i + 1}/${keys.length}: ${key.substring(0, 10)}...`
        );

        // Check if key already exists
        const existing = await pool.request()
          .input('api_key', key)
          .query('SELECT id FROM elevenlabs_keys WHERE api_key = @api_key');

        if (existing.recordset.length > 0) {
          addError(operationId, key.substring(0, 10), 'Key đã tồn tại');
          errorCount++;
          continue;
        }

        // Insert key
        await pool.request()
          .input('api_key', key)
          .input('assigned_user_id', assigned_user_id || null)
          .input('status', 'active')
          .input('created_by', created_by)
          .query(`
            INSERT INTO elevenlabs_keys 
            (api_key, assigned_user_id, status, created_by, created_at, updated_at)
            VALUES 
            (@api_key, @assigned_user_id, @status, @created_by, GETDATE(), GETDATE())
          `);

        successCount++;

        // Add small delay để tránh overwhelm database
        if (i % 10 === 0) {
          await new Promise(resolve => setTimeout(resolve, 100));
        }

      } catch (error: any) {
        console.error(`Error importing key ${key}:`, error);
        addError(operationId, key.substring(0, 10), error.message);
        errorCount++;
      }
    }

    // Complete operation
    completeOperation(
      operationId,
      `✅ Import hoàn thành! Thành công: ${successCount}, Lỗi: ${errorCount}`
    );

  } catch (error: any) {
    console.error('Critical error in background processing:', error);
    failOperation(operationId, `Lỗi nghiêm trọng: ${error.message}`);
  }
}




