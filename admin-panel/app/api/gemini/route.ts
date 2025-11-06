import { NextRequest, NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/middleware';
import { getDb } from '@/lib/db';
import sql from 'mssql';

/**
 * GET /api/gemini
 * Get all Gemini API keys (Admin only)
 */
async function getGeminiKeys(req: NextRequest) {
  try {
    const db = await getDb();
    const result = await db.request().query(`
      SELECT 
        k.[id],
        k.[api_key],
        k.[name],
        k.[assigned_user_id],
        k.[status],
        k.[last_used],
        k.[last_error],
        k.[created_at],
        k.[updated_at],
        u.[username] as assigned_username,
        creator.[username] as created_by_username
      FROM [dbo].[gemini_keys] k
      LEFT JOIN [dbo].[users] u ON k.[assigned_user_id] = u.[id]
      LEFT JOIN [dbo].[users] creator ON k.[created_by] = creator.[id]
      ORDER BY k.[created_at] DESC
    `);
    
    return NextResponse.json({
      keys: result.recordset
    });
  } catch (error: any) {
    console.error('Get Gemini keys error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * POST /api/gemini
 * Create new Gemini API key (Admin only)
 */
async function createGeminiKey(req: NextRequest) {
  try {
    const userId = (req as any).user.userId;
    const body = await req.json();
    let { api_key, name, assigned_user_id } = body;
    
    if (!api_key) {
      return NextResponse.json(
        { error: 'API key is required' },
        { status: 400 }
      );
    }
    
    // Clean and trim API key before saving
    api_key = api_key.trim().replace(/[\r\n\t]/g, '');
    
    if (!api_key) {
      return NextResponse.json(
        { error: 'API key is invalid after cleaning' },
        { status: 400 }
      );
    }
    
    const db = await getDb();
    
    // Check if key already exists
    const existing = await db.request()
      .input('api_key', sql.NVarChar(500), api_key)
      .query(`SELECT [id] FROM [dbo].[gemini_keys] WHERE [api_key] = @api_key`);
    
    if (existing.recordset.length > 0) {
      return NextResponse.json(
        { error: 'API key already exists' },
        { status: 400 }
      );
    }
    
    // Insert new key
    const result = await db.request()
      .input('api_key', sql.NVarChar(500), api_key)
      .input('name', sql.NVarChar(255), name || null)
      .input('assigned_user_id', sql.Int, assigned_user_id || null)
      .input('created_by', sql.Int, userId)
      .query(`
        INSERT INTO [dbo].[gemini_keys] 
          ([api_key], [name], [assigned_user_id], [created_by])
        OUTPUT INSERTED.*
        VALUES 
          (@api_key, @name, @assigned_user_id, @created_by)
      `);
    
    return NextResponse.json({
      success: true,
      key: result.recordset[0]
    });
  } catch (error: any) {
    console.error('Create Gemini key error:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    );
  }
}

export const GET = requireAdmin(getGeminiKeys);
export const POST = requireAdmin(createGeminiKey);

