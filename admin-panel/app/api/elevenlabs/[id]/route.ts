import { NextRequest, NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/middleware';
import { getDb } from '@/lib/db';
import sql from 'mssql';

/**
 * GET /api/elevenlabs/[id]
 * Get single ElevenLabs API key (Admin only)
 */
async function getElevenLabsKey(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const db = await getDb();
    const result = await db.request()
      .input('id', sql.Int, parseInt(id))
      .query(`
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
          u.[username] as assigned_username
        FROM [dbo].[elevenlabs_keys] k
        LEFT JOIN [dbo].[users] u ON k.[assigned_user_id] = u.[id]
        WHERE k.[id] = @id
      `);
    
    if (result.recordset.length === 0) {
      return NextResponse.json({ error: 'Key not found' }, { status: 404 });
    }
    
    return NextResponse.json({ key: result.recordset[0] });
  } catch (error: any) {
    console.error('Get ElevenLabs key error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * PUT /api/elevenlabs/[id]
 * Update ElevenLabs API key (Admin only)
 */
async function updateElevenLabsKey(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const body = await req.json();
    const { api_key, name, assigned_user_id, status, credit_balance } = body;
    
    const db = await getDb();
    
    // Check if key exists
    const existing = await db.request()
      .input('id', sql.Int, parseInt(id))
      .query(`SELECT [id] FROM [dbo].[elevenlabs_keys] WHERE [id] = @id`);
    
    if (existing.recordset.length === 0) {
      return NextResponse.json({ error: 'Key not found' }, { status: 404 });
    }
    
    // Check for duplicate API key (if changing)
    if (api_key) {
      const duplicate = await db.request()
        .input('id', sql.Int, parseInt(id))
        .input('api_key', sql.NVarChar(500), api_key)
        .query(`
          SELECT [id] FROM [dbo].[elevenlabs_keys] 
          WHERE [api_key] = @api_key AND [id] != @id
        `);
      
      if (duplicate.recordset.length > 0) {
        return NextResponse.json(
          { error: 'This API key already exists' },
          { status: 400 }
        );
      }
    }
    
    const result = await db.request()
      .input('id', sql.Int, parseInt(id))
      .input('api_key', sql.NVarChar(500), api_key)
      .input('name', sql.NVarChar(255), name || null)
      .input('assigned_user_id', sql.Int, assigned_user_id || null)
      .input('status', sql.NVarChar(20), status || 'active')
      .input('credit_balance', sql.Int, credit_balance || null)
      .query(`
        UPDATE [dbo].[elevenlabs_keys]
        SET 
          [api_key] = @api_key,
          [name] = @name,
          [assigned_user_id] = @assigned_user_id,
          [status] = @status,
          [credit_balance] = @credit_balance,
          [updated_at] = GETDATE()
        WHERE [id] = @id
      `);
    
    if (result.rowsAffected[0] === 0) {
      return NextResponse.json({ error: 'Key not found' }, { status: 404 });
    }
    
    // Get updated key
    const updated = await db.request()
      .input('id', sql.Int, parseInt(id))
      .query(`SELECT * FROM [dbo].[elevenlabs_keys] WHERE [id] = @id`);
    
    return NextResponse.json({ key: updated.recordset[0] });
  } catch (error: any) {
    console.error('Update ElevenLabs key error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * DELETE /api/elevenlabs/[id]
 * Delete ElevenLabs API key (Admin only)
 */
async function deleteElevenLabsKey(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const db = await getDb();
    
    const result = await db.request()
      .input('id', sql.Int, parseInt(id))
      .query(`DELETE FROM [dbo].[elevenlabs_keys] WHERE [id] = @id`);
    
    if (result.rowsAffected[0] === 0) {
      return NextResponse.json({ error: 'Key not found' }, { status: 404 });
    }
    
    return NextResponse.json({ message: 'Key deleted successfully' });
  } catch (error: any) {
    console.error('Delete ElevenLabs key error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export const GET = requireAdmin(getElevenLabsKey);
export const PUT = requireAdmin(updateElevenLabsKey);
export const DELETE = requireAdmin(deleteElevenLabsKey);


