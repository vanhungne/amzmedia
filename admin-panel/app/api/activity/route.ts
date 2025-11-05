import { NextRequest, NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/middleware';
import { getDb } from '@/lib/db';
import sql from 'mssql';

/**
 * GET /api/activity
 * Get activity logs (Admin only)
 * Query params: user_id, category, limit, offset
 */
async function getActivityLogs(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const userId = searchParams.get('user_id');
    const category = searchParams.get('category');
    const limit = parseInt(searchParams.get('limit') || '100');
    const offset = parseInt(searchParams.get('offset') || '0');
    
    const db = await getDb();
    
    let query = `
      SELECT 
        a.[id],
        a.[user_id],
        a.[action],
        a.[category],
        a.[details],
        a.[status],
        a.[ip_address],
        a.[device_name],
        a.[created_at],
        u.[username]
      FROM [dbo].[activity_logs] a
      LEFT JOIN [dbo].[users] u ON a.[user_id] = u.[id]
      WHERE 1=1
    `;
    
    const request = db.request();
    
    if (userId) {
      query += ` AND a.[user_id] = @user_id`;
      request.input('user_id', sql.Int, parseInt(userId));
    }
    
    if (category) {
      query += ` AND a.[category] = @category`;
      request.input('category', sql.NVarChar(50), category);
    }
    
    query += `
      ORDER BY a.[created_at] DESC
      OFFSET @offset ROWS
      FETCH NEXT @limit ROWS ONLY
    `;
    
    request
      .input('limit', sql.Int, limit)
      .input('offset', sql.Int, offset);
    
    const result = await request.query(query);
    
    // Get total count
    let countQuery = `SELECT COUNT(*) as total FROM [dbo].[activity_logs] WHERE 1=1`;
    const countRequest = db.request();
    
    if (userId) {
      countQuery += ` AND [user_id] = @user_id`;
      countRequest.input('user_id', sql.Int, parseInt(userId));
    }
    
    if (category) {
      countQuery += ` AND [category] = @category`;
      countRequest.input('category', sql.NVarChar(50), category);
    }
    
    const countResult = await countRequest.query(countQuery);
    const total = countResult.recordset[0].total;
    
    return NextResponse.json({
      logs: result.recordset,
      pagination: {
        total,
        limit,
        offset,
        hasMore: offset + limit < total
      }
    });
    
  } catch (error: any) {
    console.error('Get activity logs error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export const GET = requireAdmin(getActivityLogs);



