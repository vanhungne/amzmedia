import { NextRequest, NextResponse } from 'next/server';
import { requireAuth } from '@/lib/middleware';
import { getDb } from '@/lib/db';
import sql from 'mssql';

/**
 * GET /api/tool/proxy
 * Get proxy keys assigned to current user
 * For Python tool to fetch proxies
 */
async function getMyProxyKeys(req: NextRequest) {
  try {
    const userId = (req as any).user.userId;
    const db = await getDb();
    
    const result = await db.request()
      .input('user_id', sql.Int, userId)
      .query(`
        SELECT 
          [id],
          [proxy_key],
          [name],
          [status]
        FROM [dbo].[proxy_keys]
        WHERE [assigned_user_id] = @user_id 
          AND [status] = 'active'
        ORDER BY [last_validated] ASC, [id] ASC
      `);
    
    return NextResponse.json({
      success: true,
      keys: result.recordset
    });
  } catch (error: any) {
    console.error('Get my proxy keys error:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * POST /api/tool/proxy/status
 * Report proxy key status from Python tool
 * Body: { key_id, status, error_message }
 */
async function reportProxyStatus(req: NextRequest) {
  try {
    const userId = (req as any).user.userId;
    const body = await req.json();
    const { key_id, status, error_message } = body;
    
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
        SELECT [id] FROM [dbo].[proxy_keys] 
        WHERE [id] = @key_id AND [assigned_user_id] = @user_id
      `);
    
    if (keyCheck.recordset.length === 0) {
      return NextResponse.json(
        { success: false, error: 'Key not found or not assigned to you' },
        { status: 403 }
      );
    }
    
    // Update proxy status
    await db.request()
      .input('key_id', sql.Int, key_id)
      .input('status', sql.NVarChar(20), status)
      .input('error_message', sql.NVarChar(sql.MAX), error_message || null)
      .query(`
        UPDATE [dbo].[proxy_keys]
        SET 
          [status] = @status,
          [last_validated] = GETDATE(),
          [last_error] = @error_message,
          [updated_at] = GETDATE()
        WHERE [id] = @key_id
      `);
    
    return NextResponse.json({
      success: true,
      message: 'Proxy status updated'
    });
  } catch (error: any) {
    console.error('Report proxy status error:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export const GET = requireAuth(getMyProxyKeys);
export const POST = requireAuth(reportProxyStatus);






