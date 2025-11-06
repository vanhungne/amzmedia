import { NextRequest, NextResponse } from 'next/server';
import { requireAuth } from '@/lib/middleware';
import { getDb } from '@/lib/db';
import sql from 'mssql';

/**
 * GET /api/tool/openai
 * Get all active OpenAI (ChatGPT) keys (shared by all users)
 */
async function getOpenAIKeys(req: NextRequest) {
  try {
    const db = await getDb();
    const result = await db
      .request()
      .query(`
        SELECT [id], [api_key], [name], [status]
        FROM [dbo].[openai_keys]
        WHERE [status] = 'active'
        ORDER BY 
          CASE WHEN [last_used] IS NULL THEN 0 ELSE 1 END,
          [last_used] ASC,
          [id] ASC
      `);

    // Clean and trim API keys before returning
    const cleaned = result.recordset.map((r: any) => ({
      ...r,
      api_key: (r.api_key || '').trim().replace(/[\r\n\t]/g, ''),
    }));

    return NextResponse.json({ success: true, keys: cleaned });
  } catch (error: any) {
    console.error('Get OpenAI keys error:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error', details: error.message },
      { status: 500 }
    );
  }
}

export const GET = requireAuth(getOpenAIKeys);


