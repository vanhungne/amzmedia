import { NextRequest, NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/middleware';
import { getDb } from '@/lib/db';
import sql from 'mssql';

/**
 * GET /api/users/[id]/stats
 * Get detailed statistics for a user's API key usage
 * Admin only
 */
async function getUserStats(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const userId = parseInt(id);
    const db = await getDb();
    
    // Get user basic info
    const userResult = await db.request()
      .input('user_id', sql.Int, userId)
      .query(`
        SELECT 
          [id],
          [username],
          [email],
          [role],
          [is_active],
          [total_keys_received],
          [total_keys_used],
          [created_at]
        FROM [dbo].[users]
        WHERE [id] = @user_id
      `);
    
    if (userResult.recordset.length === 0) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }
    
    const user = userResult.recordset[0];
    
    // Get current assigned keys statistics
    const keysStatsResult = await db.request()
      .input('user_id', sql.Int, userId)
      .query(`
        SELECT 
          COUNT(*) as total_assigned,
          SUM(CASE WHEN [status] = 'active' THEN 1 ELSE 0 END) as active_keys,
          SUM(CASE WHEN [status] = 'dead' THEN 1 ELSE 0 END) as dead_keys,
          SUM(CASE WHEN [status] = 'out_of_credit' THEN 1 ELSE 0 END) as out_of_credit_keys,
          SUM(CASE WHEN [last_used] IS NOT NULL THEN 1 ELSE 0 END) as used_keys,
          SUM(CASE WHEN [last_used] IS NULL THEN 1 ELSE 0 END) as unused_keys,
          SUM(CASE WHEN [credit_balance] IS NOT NULL THEN [credit_balance] ELSE 0 END) as total_credits,
          AVG(CASE WHEN [credit_balance] IS NOT NULL AND [status] = 'active' THEN [credit_balance] ELSE NULL END) as avg_credit_per_active_key
        FROM [dbo].[elevenlabs_keys]
        WHERE [assigned_user_id] = @user_id
      `);
    
    const keysStats = keysStatsResult.recordset[0];
    
    // Get keys with credit > 800 (ready to use)
    const readyKeysResult = await db.request()
      .input('user_id', sql.Int, userId)
      .query(`
        SELECT COUNT(*) as ready_keys
        FROM [dbo].[elevenlabs_keys]
        WHERE [assigned_user_id] = @user_id
          AND [status] = 'active'
          AND ([credit_balance] IS NULL OR [credit_balance] > 800)
      `);
    
    const readyKeys = readyKeysResult.recordset[0].ready_keys;
    
    // Get recent key usage (last 10 keys used)
    const recentUsageResult = await db.request()
      .input('user_id', sql.Int, userId)
      .query(`
        SELECT TOP 10
          [id],
          [name],
          [status],
          [credit_balance],
          [last_used],
          [last_error]
        FROM [dbo].[elevenlabs_keys]
        WHERE [assigned_user_id] = @user_id
          AND [last_used] IS NOT NULL
        ORDER BY [last_used] DESC
      `);
    
    return NextResponse.json({
      user: {
        id: user.id,
        username: user.username,
        email: user.email,
        role: user.role,
        is_active: user.is_active,
        member_since: user.created_at
      },
      lifetime_stats: {
        total_keys_received: user.total_keys_received,
        total_keys_used: user.total_keys_used,
        usage_rate: user.total_keys_received > 0 
          ? ((user.total_keys_used / user.total_keys_received) * 100).toFixed(1) + '%'
          : '0%'
      },
      current_keys: {
        total_assigned: keysStats.total_assigned || 0,
        active: keysStats.active_keys || 0,
        dead: keysStats.dead_keys || 0,
        out_of_credit: keysStats.out_of_credit_keys || 0,
        used: keysStats.used_keys || 0,
        unused: keysStats.unused_keys || 0,
        ready_to_use: readyKeys || 0 // Keys with credit > 800
      },
      credits: {
        total_available: keysStats.total_credits || 0,
        avg_per_active_key: keysStats.avg_credit_per_active_key 
          ? Math.round(keysStats.avg_credit_per_active_key)
          : 0
      },
      recent_usage: recentUsageResult.recordset
    });
    
  } catch (error: any) {
    console.error('Get user stats error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export const GET = requireAdmin(getUserStats);

