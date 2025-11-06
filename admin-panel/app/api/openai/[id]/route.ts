import { NextRequest, NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/middleware';
import { getDb } from '@/lib/db';
import sql from 'mssql';

/**
 * PUT /api/openai/[id]
 * Update OpenAI API key
 */
async function updateOpenAIKey(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const keyId = parseInt(id);
    if (isNaN(keyId)) return NextResponse.json({ error: 'Invalid key ID' }, { status: 400 });

    const body = await req.json();
    const { name, assigned_user_id, status } = body;

    const db = await getDb();
    const result = await db
      .request()
      .input('id', sql.Int, keyId)
      .input('name', sql.NVarChar(255), name || null)
      .input('assigned_user_id', sql.Int, assigned_user_id || null)
      .input('status', sql.NVarChar(20), status || 'active')
      .query(`
        UPDATE [dbo].[openai_keys]
        SET [name]=@name, [assigned_user_id]=@assigned_user_id, [status]=@status, [updated_at]=GETDATE()
        OUTPUT INSERTED.*
        WHERE [id]=@id
      `);

    if (result.recordset.length === 0) return NextResponse.json({ error: 'Key not found' }, { status: 404 });
    return NextResponse.json({ success: true, key: result.recordset[0] });
  } catch (error: any) {
    console.error('Update OpenAI key error:', error);
    return NextResponse.json({ error: 'Internal server error', details: error.message }, { status: 500 });
  }
}

/**
 * DELETE /api/openai/[id]
 */
async function deleteOpenAIKey(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const keyId = parseInt(id);
    if (isNaN(keyId)) return NextResponse.json({ error: 'Invalid key ID' }, { status: 400 });

    const db = await getDb();
    const result = await db
      .request()
      .input('id', sql.Int, keyId)
      .query(`DELETE FROM [dbo].[openai_keys] WHERE [id]=@id`);

    return NextResponse.json({ success: true });
  } catch (error: any) {
    console.error('Delete OpenAI key error:', error);
    return NextResponse.json({ error: 'Internal server error', details: error.message }, { status: 500 });
  }
}

export const PUT = requireAdmin(updateOpenAIKey);
export const DELETE = requireAdmin(deleteOpenAIKey);


