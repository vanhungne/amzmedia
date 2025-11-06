import { NextRequest, NextResponse } from 'next/server';
import { getDb } from '@/lib/db';

/**
 * GET /api/test-gemini-db
 * Test endpoint to verify Gemini keys table and data
 * For debugging only - remove in production
 */
export async function GET(req: NextRequest) {
  try {
    const db = await getDb();
    
    // Check if table exists
    const tableCheck = await db.request().query(`
      SELECT COUNT(*) as count
      FROM INFORMATION_SCHEMA.TABLES 
      WHERE TABLE_NAME = 'gemini_keys'
    `);
    
    if (tableCheck.recordset[0].count === 0) {
      return NextResponse.json({
        success: false,
        error: 'Table gemini_keys does not exist',
        hint: 'Run database initialization script'
      });
    }
    
    // Get all keys (including inactive)
    const result = await db.request().query(`
      SELECT 
        [id],
        LEFT([api_key], 12) + '...' + RIGHT([api_key], 8) as api_key_preview,
        LEN([api_key]) as key_length,
        [name],
        [status],
        [last_used],
        [created_at]
      FROM [dbo].[gemini_keys]
      ORDER BY [id]
    `);
    
    // Count by status
    const statusCount = await db.request().query(`
      SELECT 
        [status],
        COUNT(*) as count
      FROM [dbo].[gemini_keys]
      GROUP BY [status]
    `);
    
    return NextResponse.json({
      success: true,
      tableExists: true,
      totalKeys: result.recordset.length,
      statusCounts: statusCount.recordset,
      keys: result.recordset,
      message: 'Database check completed'
    });
    
  } catch (error: any) {
    console.error('Test Gemini DB error:', error);
    return NextResponse.json({
      success: false,
      error: 'Database error',
      details: error.message,
      stack: error.stack
    }, { status: 500 });
  }
}

