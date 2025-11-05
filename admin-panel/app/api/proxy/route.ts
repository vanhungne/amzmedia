import { NextRequest, NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/middleware';
import { getDb } from '@/lib/db';
import sql from 'mssql';

/**
 * GET /api/proxy
 * Get all proxy keys (Admin only)
 */
async function getProxyKeys(req: NextRequest) {
  try {
    const db = await getDb();
    const result = await db.request().query(`
      SELECT 
        p.[id],
        p.[proxy_key],
        p.[name],
        p.[assigned_user_id],
        p.[status],
        p.[last_validated],
        p.[last_error],
        p.[created_at],
        p.[updated_at],
        u.[username] as assigned_username,
        c.[username] as created_by_username
      FROM [dbo].[proxy_keys] p
      LEFT JOIN [dbo].[users] u ON p.[assigned_user_id] = u.[id]
      LEFT JOIN [dbo].[users] c ON p.[created_by] = c.[id]
      ORDER BY p.[created_at] DESC
    `);
    
    return NextResponse.json({ keys: result.recordset });
  } catch (error: any) {
    console.error('Get proxy keys error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * POST /api/proxy
 * Create new proxy key (Admin only)
 */
async function createProxyKey(req: NextRequest) {
  try {
    const body = await req.json();
    const { proxy_key, name, assigned_user_id } = body;
    const userId = (req as any).user.userId;
    
    if (!proxy_key) {
      return NextResponse.json(
        { error: 'proxy_key is required' },
        { status: 400 }
      );
    }
    
    const db = await getDb();
    
    // Check if key already exists
    const existing = await db.request()
      .input('proxy_key', sql.NVarChar(500), proxy_key)
      .query('SELECT id FROM [dbo].[proxy_keys] WHERE proxy_key = @proxy_key');
    
    if (existing.recordset.length > 0) {
      return NextResponse.json(
        { error: 'Proxy key already exists' },
        { status: 400 }
      );
    }
    
    const result = await db.request()
      .input('proxy_key', sql.NVarChar(500), proxy_key)
      .input('name', sql.NVarChar(255), name || null)
      .input('assigned_user_id', sql.Int, assigned_user_id || null)
      .input('created_by', sql.Int, userId)
      .query(`
        INSERT INTO [dbo].[proxy_keys] ([proxy_key], [name], [assigned_user_id], [created_by])
        OUTPUT INSERTED.*
        VALUES (@proxy_key, @name, @assigned_user_id, @created_by)
      `);
    
    return NextResponse.json({ key: result.recordset[0] });
  } catch (error: any) {
    console.error('Create proxy key error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export const GET = requireAdmin(getProxyKeys);
export const POST = requireAdmin(createProxyKey);






