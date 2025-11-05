import { NextRequest, NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/middleware';
import { createUser, getUserByUsername } from '@/lib/auth';
import { getDb } from '@/lib/db';

// GET all users with key statistics
async function getUsers(req: NextRequest) {
  try {
    const db = await getDb();
    
    // First, check if new columns exist, if not return simple query
    const columnCheck = await db.request().query(`
      SELECT COUNT(*) as col_count
      FROM sys.columns 
      WHERE object_id = OBJECT_ID('[dbo].[users]') 
      AND name IN ('total_keys_received', 'total_keys_used')
    `);
    
    const hasNewColumns = columnCheck.recordset[0].col_count === 2;
    
    if (!hasNewColumns) {
      // Fallback to simple query without new columns
      const result = await db.request().query(`
        SELECT 
          u.[id],
          u.[username],
          u.[email],
          u.[role],
          u.[is_active],
          0 as total_keys_received,
          0 as total_keys_used,
          u.[created_at],
          u.[updated_at],
          COUNT(k.[id]) as current_assigned_keys,
          SUM(CASE WHEN k.[status] = 'active' THEN 1 ELSE 0 END) as active_keys_count,
          SUM(CASE WHEN k.[status] = 'active' AND (k.[credit_balance] IS NULL OR k.[credit_balance] > 800) THEN 1 ELSE 0 END) as ready_keys_count
        FROM [dbo].[users] u
        LEFT JOIN [dbo].[elevenlabs_keys] k ON k.[assigned_user_id] = u.[id]
        GROUP BY u.[id], u.[username], u.[email], u.[role], u.[is_active], u.[created_at], u.[updated_at]
        ORDER BY u.[created_at] DESC
      `);
      return NextResponse.json({ users: result.recordset });
    }
    
    // Full query with new columns
    const result = await db.request().query(`
      SELECT 
        u.[id],
        u.[username],
        u.[email],
        u.[role],
        u.[is_active],
        ISNULL(u.[total_keys_received], 0) as total_keys_received,
        ISNULL(u.[total_keys_used], 0) as total_keys_used,
        u.[device_id],
        u.[device_name],
        u.[device_locked_at],
        u.[created_at],
        u.[updated_at],
        COUNT(k.[id]) as current_assigned_keys,
        SUM(CASE WHEN k.[status] = 'active' THEN 1 ELSE 0 END) as active_keys_count,
        SUM(CASE WHEN k.[status] = 'active' AND (k.[credit_balance] IS NULL OR k.[credit_balance] > 800) THEN 1 ELSE 0 END) as ready_keys_count
      FROM [dbo].[users] u
      LEFT JOIN [dbo].[elevenlabs_keys] k ON k.[assigned_user_id] = u.[id]
      GROUP BY u.[id], u.[username], u.[email], u.[role], u.[is_active], u.[total_keys_received], u.[total_keys_used], u.[device_id], u.[device_name], u.[device_locked_at], u.[created_at], u.[updated_at]
      ORDER BY u.[created_at] DESC
    `);
    
    return NextResponse.json({ users: result.recordset });
  } catch (error: any) {
    console.error('Get users error:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    );
  }
}

// POST create new user (admin only)
async function createUserHandler(req: NextRequest) {
  try {
    const body = await req.json();
    const { username, password, email, role } = body;
    
    if (!username || !password) {
      return NextResponse.json(
        { error: 'Username and password are required' },
        { status: 400 }
      );
    }
    
    // Check if user exists
    const existing = await getUserByUsername(username);
    if (existing) {
      return NextResponse.json(
        { error: 'Username already exists' },
        { status: 400 }
      );
    }
    
    const user = await createUser(username, password, email || null, role || 'user');
    
    return NextResponse.json({
      id: user.id,
      username: user.username,
      email: user.email,
      role: user.role,
      is_active: user.is_active,
    }, { status: 201 });
  } catch (error: any) {
    console.error('Create user error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export const GET = requireAdmin(getUsers);
export const POST = requireAdmin(createUserHandler);






