import { NextRequest, NextResponse } from 'next/server';
import { requireAuth } from '@/lib/middleware';
import { getDb } from '@/lib/db';
import sql from 'mssql';

/**
 * GET /api/tool/elevenlabs
 * Get ElevenLabs API keys assigned to current user
 * For Python tool to fetch keys
 */
async function getMyElevenLabsKeys(req: NextRequest) {
  try {
    const userId = (req as any).user.userId;
    const db = await getDb();
    
    // Only return keys with status = 'active' AND credit > 800
    // Key hết credit (<= 800) không được tính là active
    const result = await db.request()
      .input('user_id', sql.Int, userId)
      .query(`
        SELECT 
          [id],
          [api_key],
          [name],
          [status],
          [credit_balance]
        FROM [dbo].[elevenlabs_keys]
        WHERE [assigned_user_id] = @user_id 
          AND [status] = 'active'
          AND ([credit_balance] IS NULL OR [credit_balance] > 800)
        ORDER BY [last_used] ASC, [id] ASC
      `);
    
    return NextResponse.json({
      success: true,
      keys: result.recordset
    });
  } catch (error: any) {
    console.error('Get my ElevenLabs keys error:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * POST /api/tool/elevenlabs/status
 * Report ElevenLabs API key status from Python tool
 * Body: { key_id, status, error_message, credit_balance }
 */
async function reportKeyStatus(req: NextRequest) {
  try {
    const userId = (req as any).user.userId;
    const body = await req.json();
    const { key_id, status, error_message, credit_balance } = body;
    
    if (!key_id || !status) {
      return NextResponse.json(
        { success: false, error: 'key_id and status are required' },
        { status: 400 }
      );
    }
    
    const db = await getDb();
    
    // Verify the key belongs to this user
    const keyCheck = await db.request()
      .input('key_id', sql.Int, key_id)
      .input('user_id', sql.Int, userId)
      .query(`
        SELECT [id] FROM [dbo].[elevenlabs_keys] 
        WHERE [id] = @key_id AND [assigned_user_id] = @user_id
      `);
    
    if (keyCheck.recordset.length === 0) {
      return NextResponse.json(
        { success: false, error: 'Key not found or not assigned to you' },
        { status: 403 }
      );
    }
    
    // Get key info before update to check if this is first use
    const keyBefore = await db.request()
      .input('key_id', sql.Int, key_id)
      .query(`
        SELECT [last_used], [assigned_user_id]
        FROM [dbo].[elevenlabs_keys]
        WHERE [id] = @key_id
      `);
    
    const wasNeverUsed = keyBefore.recordset[0]?.last_used === null;
    const assignedUserId = keyBefore.recordset[0]?.assigned_user_id;
    
    // Update key status with credit balance check
    // Khi tool vứt key và báo về server, status sẽ được đổi theo
    let finalStatus = status;
    
    // Nếu tool báo key là 'dead' hoặc 'out_of_credit', luôn chấp nhận status đó
    if (status === 'dead' || status === 'out_of_credit') {
      finalStatus = status; // Giữ nguyên status từ tool
    } else if (status === 'active') {
      // Nếu tool báo 'active' nhưng credit <= 800, đổi thành 'out_of_credit'
      if (credit_balance !== null && credit_balance !== undefined && credit_balance <= 800) {
        finalStatus = 'out_of_credit';
      }
    }
    
    console.log(`[Report Status] Key ${key_id}: tool reported status=${status}, credit_balance=${credit_balance}, finalStatus=${finalStatus}`);
    
    // Update key status
    await db.request()
      .input('key_id', sql.Int, key_id)
      .input('status', sql.NVarChar(20), finalStatus)
      .input('error_message', sql.NVarChar(sql.MAX), error_message || null)
      .input('credit_balance', sql.Int, credit_balance !== null && credit_balance !== undefined ? credit_balance : null)
      .query(`
        UPDATE [dbo].[elevenlabs_keys]
        SET 
          [status] = @status,
          [last_used] = GETDATE(),
          [last_error] = @error_message,
          [credit_balance] = COALESCE(@credit_balance, [credit_balance]),
          [updated_at] = GETDATE()
        WHERE [id] = @key_id
      `);
    
    // If this is the first use, increment user's total_keys_used counter
    if (wasNeverUsed && assignedUserId) {
      await db.request()
        .input('user_id', sql.Int, assignedUserId)
        .query(`
          UPDATE [dbo].[users]
          SET [total_keys_used] = [total_keys_used] + 1,
              [updated_at] = GETDATE()
          WHERE [id] = @user_id
        `);
    }
    
    return NextResponse.json({
      success: true,
      message: 'Key status updated',
      first_use: wasNeverUsed
    });
  } catch (error: any) {
    console.error('Report key status error:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export const GET = requireAuth(getMyElevenLabsKeys);
export const POST = requireAuth(reportKeyStatus);


