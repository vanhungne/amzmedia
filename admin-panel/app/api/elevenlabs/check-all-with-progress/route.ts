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
import { parallelLimit } from '@/lib/performance';

/**
 * POST /api/elevenlabs/check-all-with-progress
 * Kiểm tra tất cả ElevenLabs keys với progress tracking
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

    // Get all keys
    const pool = await getDb();
    const result = await pool.request().query(`
      SELECT id, api_key, name, status 
      FROM elevenlabs_keys 
      WHERE status != 'dead'
      ORDER BY id
    `);

    const keys = result.recordset;

    if (keys.length === 0) {
      return NextResponse.json({ message: 'No keys to check' });
    }

    // Create operation
    const operationId = generateOperationId('check_all_keys');
    createOperation(operationId, keys.length);

    // Start checking in background
    checkKeysInBackground(operationId, keys);

    // Return operation ID immediately
    return NextResponse.json({
      operationId,
      message: `Bắt đầu kiểm tra ${keys.length} keys`,
      totalKeys: keys.length,
    });

  } catch (error) {
    console.error('Error starting check all keys:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * Check keys in background with parallel processing (rate limited for external API)
 */
async function checkKeysInBackground(
  operationId: string,
  keys: any[]
) {
  const pool = await getDb();
  const checkedKeyIds: number[] = [];
  const progressLock = { count: 0 };

  // Lower concurrent limit for external API calls (5 concurrent)
  const CONCURRENT_LIMIT = 5;

  // Helper to update progress atomically
  const updateProgressSafe = () => {
    progressLock.count++;
    updateProgress(
      operationId,
      progressLock.count,
      `Đang kiểm tra... ${progressLock.count}/${keys.length} keys`
    );
  };

  try {
    // Process each key in parallel with limit
    const results = await parallelLimit(
      keys.map((key, index) => ({ key, index })),
      async ({ key, index }) => {
        try {
          // Call ElevenLabs API to check key
          const response = await fetch('https://api.elevenlabs.io/v1/user/subscription', {
            headers: {
              'xi-api-key': key.api_key,
            },
            signal: AbortSignal.timeout(10000), // 10 second timeout
          });

          if (response.ok) {
            const data = await response.json();
            const creditBalance = data.character_count || 0;

            // Update key status
            const updateResult = await pool.request()
              .input('id', sql.Int, key.id)
              .input('credit_balance', sql.Int, creditBalance)
              .input('status', sql.NVarChar(20), creditBalance > 0 ? 'active' : 'out_of_credit')
              .query(`
                UPDATE elevenlabs_keys 
                SET credit_balance = @credit_balance,
                    status = @status,
                    last_used = GETDATE(),
                    last_error = NULL,
                    updated_at = GETDATE()
                WHERE id = @id
              `);

            // Verify update was successful
            if (updateResult.rowsAffected[0] > 0) {
              checkedKeyIds.push(key.id);
              updateProgressSafe();
              return { success: true, keyId: key.id, status: 'active' };
            } else {
              console.warn(`[Check All] Failed to update key ${key.id}`);
              addError(operationId, key.name || key.api_key.substring(0, 10), 'Không thể cập nhật trạng thái');
              updateProgressSafe();
              return { success: false, keyId: key.id, status: 'error', error: 'Update failed' };
            }
          } else {
            // Key is dead or invalid
            const updateResult = await pool.request()
              .input('id', sql.Int, key.id)
              .input('last_error', sql.NVarChar(sql.MAX), `HTTP ${response.status}`)
              .query(`
                UPDATE elevenlabs_keys 
                SET status = 'dead',
                    last_error = @last_error,
                    updated_at = GETDATE()
                WHERE id = @id
              `);

            if (updateResult.rowsAffected[0] > 0) {
              checkedKeyIds.push(key.id);
            }
            addError(operationId, key.name || key.api_key.substring(0, 10), 'Key không hợp lệ');
            updateProgressSafe();
            return { success: true, keyId: key.id, status: 'dead' };
          }

        } catch (error: any) {
          console.error(`Error checking key ${key.id}:`, error);
          addError(operationId, key.name || key.api_key.substring(0, 10), error.message);

          // Update key with error
          try {
            await pool.request()
              .input('id', sql.Int, key.id)
              .input('last_error', sql.NVarChar(sql.MAX), error.message)
              .query(`
                UPDATE elevenlabs_keys 
                SET last_error = @last_error,
                    updated_at = GETDATE()
                WHERE id = @id
              `);
          } catch (updateError) {
            console.error('Error updating key error:', updateError);
          }
          
          updateProgressSafe();
          return { success: false, keyId: key.id, status: 'error', error: error.message };
        }
      },
      CONCURRENT_LIMIT
    );

    // Count results after all operations complete
    const successCount = results.filter(r => r?.success && r?.status === 'active').length;
    const deadCount = results.filter(r => r?.success && r?.status === 'dead').length;
    const errorCount = results.filter(r => !r?.success || r?.status === 'error').length;

    // Final progress update before completion
    updateProgress(
      operationId,
      keys.length,
      `Đang xác minh... Đã kiểm tra ${keys.length}/${keys.length} keys (Hợp lệ: ${successCount}, Dead: ${deadCount}, Lỗi: ${errorCount})`
    );

    // Small delay to ensure all DB operations are committed
    await new Promise(resolve => setTimeout(resolve, 200));

    // Complete operation only after all items processed
    completeOperation(
      operationId,
      `✅ Kiểm tra hoàn thành! Hợp lệ: ${successCount}, Dead: ${deadCount}, Lỗi: ${errorCount}`
    );

  } catch (error: any) {
    console.error('Critical error in background checking:', error);
    failOperation(operationId, `Lỗi nghiêm trọng: ${error.message}`);
  }
}




