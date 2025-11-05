import { NextRequest, NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/middleware';
import { getDb } from '@/lib/db';
import sql from 'mssql';

/**
 * GET /api/elevenlabs
 * Get all ElevenLabs API keys (Admin only)
 */
async function getElevenLabsKeys(req: NextRequest) {
  try {
    const db = await getDb();
    const result = await db.request().query(`
      SELECT 
        k.[id],
        k.[api_key],
        k.[name],
        k.[assigned_user_id],
        k.[status],
        k.[credit_balance],
        k.[last_used],
        k.[last_error],
        k.[created_at],
        k.[updated_at],
        u.[username] as assigned_username,
        c.[username] as created_by_username
      FROM [dbo].[elevenlabs_keys] k
      LEFT JOIN [dbo].[users] u ON k.[assigned_user_id] = u.[id]
      LEFT JOIN [dbo].[users] c ON k.[created_by] = c.[id]
      ORDER BY k.[created_at] DESC
    `);
    
    return NextResponse.json({ keys: result.recordset });
  } catch (error: any) {
    console.error('Get ElevenLabs keys error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * POST /api/elevenlabs
 * Create new ElevenLabs API key (Admin only)
 */
async function createElevenLabsKey(req: NextRequest) {
  try {
    const body = await req.json();
    const { api_key, name, assigned_user_id } = body;
    const userId = (req as any).user.userId;
    
    if (!api_key) {
      return NextResponse.json(
        { error: 'API key is required' },
        { status: 400 }
      );
    }
    
    // Validate API key format (starts with sk_)
    if (!api_key.startsWith('sk_')) {
      return NextResponse.json(
        { error: 'Invalid ElevenLabs API key format (should start with sk_)' },
        { status: 400 }
      );
    }
    
    const db = await getDb();
    
    // Check if key already exists
    const existingKey = await db.request()
      .input('api_key', sql.NVarChar(500), api_key)
      .query(`SELECT [id] FROM [dbo].[elevenlabs_keys] WHERE [api_key] = @api_key`);
    
    if (existingKey.recordset.length > 0) {
      return NextResponse.json(
        { error: 'This API key already exists' },
        { status: 400 }
      );
    }
    
    const result = await db.request()
      .input('api_key', sql.NVarChar(500), api_key)
      .input('name', sql.NVarChar(255), name || null)
      .input('assigned_user_id', sql.Int, assigned_user_id || null)
      .input('created_by', sql.Int, userId)
      .query(`
        INSERT INTO [dbo].[elevenlabs_keys] 
        ([api_key], [name], [assigned_user_id], [created_by])
        OUTPUT INSERTED.*
        VALUES (@api_key, @name, @assigned_user_id, @created_by)
      `);
    
    return NextResponse.json({ key: result.recordset[0] }, { status: 201 });
  } catch (error: any) {
    console.error('Create ElevenLabs key error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export const GET = requireAdmin(getElevenLabsKeys);
export const POST = requireAdmin(createElevenLabsKey);


