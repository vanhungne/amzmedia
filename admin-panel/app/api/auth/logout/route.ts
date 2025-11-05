import { NextRequest, NextResponse } from 'next/server';
import sql from 'mssql';
import { getDb } from '@/lib/db';

export async function POST(req: NextRequest) {
  try {
    const token = req.cookies.get('auth_token')?.value;
    
    if (token) {
      // Delete session from database
      const db = await getDb();
      await db.request()
        .input('token', sql.NVarChar(500), token)
        .query(`DELETE FROM [dbo].[sessions] WHERE [token] = @token`);
    }
    
    const response = NextResponse.json({ success: true });
    response.cookies.delete('auth_token');
    return response;
  } catch (error: any) {
    console.error('Logout error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

