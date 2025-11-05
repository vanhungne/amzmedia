import { NextRequest, NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/middleware';
import { getDb } from '@/lib/db';
import sql from 'mssql';

/**
 * PUT /api/proxy/[id]
 * Update proxy key (Admin only)
 */
async function updateProxyKey(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const body = await req.json();
    const { proxy_key, name, assigned_user_id, status } = body;
    
    const db = await getDb();
    const result = await db.request()
      .input('id', sql.Int, parseInt(id))
      .input('proxy_key', sql.NVarChar(500), proxy_key)
      .input('name', sql.NVarChar(255), name || null)
      .input('assigned_user_id', sql.Int, assigned_user_id || null)
      .input('status', sql.NVarChar(20), status)
      .query(`
        UPDATE [dbo].[proxy_keys]
        SET 
          [proxy_key] = @proxy_key,
          [name] = @name,
          [assigned_user_id] = @assigned_user_id,
          [status] = @status,
          [updated_at] = GETDATE()
        WHERE [id] = @id
      `);
    
    if (result.rowsAffected[0] === 0) {
      return NextResponse.json(
        { error: 'Proxy key not found' },
        { status: 404 }
      );
    }
    
    return NextResponse.json({ success: true });
  } catch (error: any) {
    console.error('Update proxy key error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * DELETE /api/proxy/[id]
 * Delete proxy key (Admin only)
 */
async function deleteProxyKey(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const db = await getDb();
    
    await db.request()
      .input('id', sql.Int, parseInt(id))
      .query('DELETE FROM [dbo].[proxy_keys] WHERE [id] = @id');
    
    return NextResponse.json({ success: true });
  } catch (error: any) {
    console.error('Delete proxy key error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export const PUT = requireAdmin(updateProxyKey);
export const DELETE = requireAdmin(deleteProxyKey);






