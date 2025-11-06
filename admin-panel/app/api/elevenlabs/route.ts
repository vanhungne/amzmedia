import { NextRequest, NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/middleware';
import { getDb } from '@/lib/db';
import sql from 'mssql';

// Disable caching for this route
export const dynamic = 'force-dynamic';
export const revalidate = 0;

/**
 * GET /api/elevenlabs
 * Get all ElevenLabs API keys (Admin only)
 * Query params: page, limit, status, assigned_user_id, search
 */
async function getElevenLabsKeys(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '50');
    const status = searchParams.get('status');
    const assignedUserId = searchParams.get('assigned_user_id');
    const search = searchParams.get('search');
    const offset = (page - 1) * limit;
    
    const db = await getDb();
    
    let query = `
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
      WHERE 1=1
    `;
    
    const request = db.request();
    
    // Filter by status
    if (status) {
      query += ` AND k.[status] = @status`;
      request.input('status', sql.NVarChar(50), status);
    }
    
    // Filter by assigned user
    if (assignedUserId) {
      const userId = parseInt(assignedUserId);
      if (userId === 0) {
        // Unassigned keys
        query += ` AND k.[assigned_user_id] IS NULL`;
      } else {
        query += ` AND k.[assigned_user_id] = @assigned_user_id`;
        request.input('assigned_user_id', sql.Int, userId);
      }
    }
    
    // Search by name or API key
    if (search) {
      query += ` AND (k.[name] LIKE @search OR k.[api_key] LIKE @search)`;
      request.input('search', sql.NVarChar(500), `%${search}%`);
    }
    
    query += ` ORDER BY k.[created_at] DESC
      OFFSET @offset ROWS
      FETCH NEXT @limit ROWS ONLY
    `;
    
    request
      .input('offset', sql.Int, offset)
      .input('limit', sql.Int, limit);
    
    const result = await request.query(query);
    
    // Get total count with same filters
    let countQuery = `SELECT COUNT(*) as total FROM [dbo].[elevenlabs_keys] k WHERE 1=1`;
    const countRequest = db.request();
    
    if (status) {
      countQuery += ` AND k.[status] = @status`;
      countRequest.input('status', sql.NVarChar(50), status);
    }
    
    if (assignedUserId) {
      const userId = parseInt(assignedUserId);
      if (userId === 0) {
        countQuery += ` AND k.[assigned_user_id] IS NULL`;
      } else {
        countQuery += ` AND k.[assigned_user_id] = @assigned_user_id`;
        countRequest.input('assigned_user_id', sql.Int, userId);
      }
    }
    
    if (search) {
      countQuery += ` AND (k.[name] LIKE @search OR k.[api_key] LIKE @search)`;
      countRequest.input('search', sql.NVarChar(500), `%${search}%`);
    }
    
    const countResult = await countRequest.query(countQuery);
    const total = countResult.recordset[0].total;
    
    // Get summary stats (total, active, assigned, unassigned)
    // ALWAYS get full stats from entire table, not filtered
    // This query should return the TOTAL count from the entire table regardless of filters
    const statsQuery = `
      SELECT 
        COUNT(*) as total,
        ISNULL(SUM(CASE WHEN [status] = 'active' THEN 1 ELSE 0 END), 0) as active,
        ISNULL(SUM(CASE WHEN [assigned_user_id] IS NOT NULL THEN 1 ELSE 0 END), 0) as assigned,
        ISNULL(SUM(CASE WHEN [assigned_user_id] IS NULL AND [status] = 'active' THEN 1 ELSE 0 END), 0) as unassigned
      FROM [dbo].[elevenlabs_keys]
    `;
    
    console.log('[ElevenLabs API] Getting full stats from entire table (no filters)');
    const statsResult = await db.request().query(statsQuery);
    
    // Ensure stats are numbers, not null
    const stats = statsResult.recordset[0] || {};
    const finalStats = {
      total: parseInt(stats.total) || 0,
      active: parseInt(stats.active) || 0,
      assigned: parseInt(stats.assigned) || 0,
      unassigned: parseInt(stats.unassigned) || 0
    };
    
    console.log('[ElevenLabs API] Full stats:', finalStats);
    
    const response = NextResponse.json({
      keys: result.recordset,
      pagination: {
        total,
        page,
        limit,
        offset,
        hasMore: offset + limit < total,
        totalPages: Math.ceil(total / limit)
      },
      stats: finalStats
    });
    
    // DISABLE ALL CACHING
    response.headers.set('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0');
    response.headers.set('Pragma', 'no-cache');
    response.headers.set('Expires', '0');
    
    return response;
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


