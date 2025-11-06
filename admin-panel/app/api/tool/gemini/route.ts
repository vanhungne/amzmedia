import { NextRequest, NextResponse } from 'next/server';
import { requireAuth } from '@/lib/middleware';
import { getDb } from '@/lib/db';
import sql from 'mssql';

/**
 * GET /api/tool/gemini
 * Get all active Gemini keys (shared by all users)
 */
async function getMyGeminiKeys(req: NextRequest) {
  try {
    const db = await getDb();
    const result = await db.request()
      .query(`
        SELECT 
          [id],
          [api_key],
          [name],
          [status]
        FROM [dbo].[gemini_keys]
        WHERE [status] = 'active'
        ORDER BY [last_used] ASC NULLS FIRST, [id] ASC
      `);
    
    // Clean and trim API keys before returning
    const cleanedKeys = result.recordset.map(record => ({
      ...record,
      api_key: (record.api_key || '').trim().replace(/[\r\n\t]/g, '')
    }));
    
    return NextResponse.json({
      success: true,
      keys: cleanedKeys
    });
  } catch (error: any) {
    console.error('Get Gemini keys error:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * POST /api/tool/gemini
 * Report Gemini key status (any authenticated user can report)
 */
async function reportGeminiStatus(req: NextRequest) {
  try {
    const body = await req.json();
    const { key_id, status, error_message } = body;
    
    if (!key_id || !status) {
      return NextResponse.json(
        { success: false, error: 'key_id and status are required' },
        { status: 400 }
      );
    }
    
    const db = await getDb();
    
    // Verify key exists (no need to check user assignment since keys are shared)
    const keyCheck = await db.request()
      .input('key_id', sql.Int, key_id)
      .query(`
        SELECT [id] FROM [dbo].[gemini_keys] 
        WHERE [id] = @key_id
      `);
    
    if (keyCheck.recordset.length === 0) {
      return NextResponse.json(
        { success: false, error: 'Key not found' },
        { status: 404 }
      );
    }
    
    // Update key status
    await db.request()
      .input('key_id', sql.Int, key_id)
      .input('status', sql.NVarChar(20), status)
      .input('error_message', sql.NVarChar(sql.MAX), error_message || null)
      .query(`
        UPDATE [dbo].[gemini_keys]
        SET 
          [status] = @status,
          [last_used] = GETDATE(),
          [last_error] = @error_message,
          [updated_at] = GETDATE()
        WHERE [id] = @key_id
      `);
    
    return NextResponse.json({
      success: true,
      message: 'Gemini key status updated'
    });
  } catch (error: any) {
    console.error('Report Gemini status error:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export const GET = requireAuth(getMyGeminiKeys);
export const POST = requireAuth(reportGeminiStatus);

