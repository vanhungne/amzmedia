import { NextRequest, NextResponse } from 'next/server';
import { requireAuth } from '@/lib/middleware';
import { getDb } from '@/lib/db';
import sql from 'mssql';

/**
 * POST /api/tool/activity
 * Log user activity from Python tool
 * Body: { action, category, details, status }
 */
async function logActivity(req: NextRequest) {
  try {
    const userId = (req as any).user.userId;
    const body = await req.json();
    const { action, category, details, status, device_name } = body;
    
    if (!action || !category) {
      return NextResponse.json(
        { success: false, error: 'action and category are required' },
        { status: 400 }
      );
    }
    
    const db = await getDb();
    
    // Get IP from headers (if behind proxy)
    const ip = req.headers.get('x-forwarded-for') || 
                req.headers.get('x-real-ip') || 
                'unknown';
    
    await db.request()
      .input('user_id', sql.Int, userId)
      .input('action', sql.NVarChar(100), action)
      .input('category', sql.NVarChar(50), category)
      .input('details', sql.NVarChar(sql.MAX), details ? JSON.stringify(details) : null)
      .input('status', sql.NVarChar(20), status || 'success')
      .input('ip_address', sql.NVarChar(50), ip)
      .input('device_name', sql.NVarChar(255), device_name || null)
      .query(`
        INSERT INTO [dbo].[activity_logs] 
          ([user_id], [action], [category], [details], [status], [ip_address], [device_name])
        VALUES 
          (@user_id, @action, @category, @details, @status, @ip_address, @device_name)
      `);
    
    return NextResponse.json({
      success: true,
      message: 'Activity logged'
    });
    
  } catch (error: any) {
    console.error('Log activity error:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export const POST = requireAuth(logActivity);



