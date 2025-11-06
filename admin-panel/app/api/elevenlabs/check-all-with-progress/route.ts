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
 * Check keys in background
 */
async function checkKeysInBackground(
  operationId: string,
  keys: any[]
) {
  const pool = await getDb();
  let successCount = 0;
  let deadCount = 0;
  let errorCount = 0;

  try {
    for (let i = 0; i < keys.length; i++) {
      const key = keys[i];

      try {
        // Update progress
        updateProgress(
          operationId,
          i + 1,
          `Đang kiểm tra key ${i + 1}/${keys.length}: ${key.name || key.api_key.substring(0, 10)}...`
        );

        // Call ElevenLabs API to check key
        const response = await fetch('https://api.elevenlabs.io/v1/user/subscription', {
          headers: {
            'xi-api-key': key.api_key,
          },
        });

        if (response.ok) {
          const data = await response.json();
          const creditBalance = data.character_count || 0;

          // Update key status
          await pool.request()
            .input('id', key.id)
            .input('credit_balance', creditBalance)
            .input('status', creditBalance > 0 ? 'active' : 'out_of_credit')
            .query(`
              UPDATE elevenlabs_keys 
              SET credit_balance = @credit_balance,
                  status = @status,
                  last_used = GETDATE(),
                  last_error = NULL,
                  updated_at = GETDATE()
              WHERE id = @id
            `);

          successCount++;
        } else {
          // Key is dead or invalid
          await pool.request()
            .input('id', key.id)
            .input('last_error', `HTTP ${response.status}`)
            .query(`
              UPDATE elevenlabs_keys 
              SET status = 'dead',
                  last_error = @last_error,
                  updated_at = GETDATE()
              WHERE id = @id
            `);

          deadCount++;
          addError(operationId, key.name || key.api_key.substring(0, 10), 'Key không hợp lệ');
        }

        // Rate limiting: delay giữa các requests
        await new Promise(resolve => setTimeout(resolve, 200));

      } catch (error: any) {
        console.error(`Error checking key ${key.id}:`, error);
        errorCount++;
        addError(operationId, key.name || key.api_key.substring(0, 10), error.message);

        // Update key with error
        try {
          await pool.request()
            .input('id', key.id)
            .input('last_error', error.message)
            .query(`
              UPDATE elevenlabs_keys 
              SET last_error = @last_error,
                  updated_at = GETDATE()
              WHERE id = @id
            `);
        } catch (updateError) {
          console.error('Error updating key error:', updateError);
        }
      }
    }

    // Complete operation
    completeOperation(
      operationId,
      `✅ Kiểm tra hoàn thành! Hợp lệ: ${successCount}, Dead: ${deadCount}, Lỗi: ${errorCount}`
    );

  } catch (error: any) {
    console.error('Critical error in background checking:', error);
    failOperation(operationId, `Lỗi nghiêm trọng: ${error.message}`);
  }
}




