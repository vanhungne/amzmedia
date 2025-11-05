import { NextRequest, NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/middleware';
import { getDb } from '@/lib/db';
import sql from 'mssql';

/**
 * POST /api/users/[id]/reset-device
 * Reset device lock for a user (Admin only)
 * Allows user to login from a new device
 */
async function resetUserDevice(req: NextRequest, { params }: { params: { id: string } }) {
  try {
    const { id } = params;
    const db = await getDb();
    
    // Check if user exists
    const userCheck = await db.request()
      .input('id', sql.Int, id)
      .query(`SELECT [id], [username], [device_name] FROM [dbo].[users] WHERE [id] = @id`);
    
    if (userCheck.recordset.length === 0) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }
    
    const user = userCheck.recordset[0];
    
    // Reset device lock
    await db.request()
      .input('id', sql.Int, id)
      .query(`
        UPDATE [dbo].[users]
        SET [device_id] = NULL,
            [device_name] = NULL,
            [device_locked_at] = NULL,
            [updated_at] = GETDATE()
        WHERE [id] = @id
      `);
    
    console.log(`[ADMIN] Reset device for user: ${user.username}`);
    
    return NextResponse.json({
      success: true,
      message: `Device lock reset for user: ${user.username}`,
      user: {
        id: user.id,
        username: user.username
      }
    });
    
  } catch (error: any) {
    console.error('Reset device error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export const POST = requireAdmin(resetUserDevice);



