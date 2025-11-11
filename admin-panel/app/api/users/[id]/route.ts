import { NextRequest, NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/middleware';
import { getDb } from '@/lib/db';
import sql from 'mssql';
import { hashPassword } from '@/lib/auth';

// PUT update user
async function updateUser(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let body: any = {};
  
  try {
    body = await req.json();
    const { username, email, role, is_active, password } = body;
    
    const db = await getDb();
    const userId = parseInt(id);
    
    // Check if username already exists (excluding current user)
    if (username) {
      const existingUser = await db.request()
        .input('username', sql.NVarChar(100), username)
        .input('id', sql.Int, userId)
        .query(`
          SELECT [id] FROM [dbo].[users] 
          WHERE [username] = @username AND [id] != @id
        `);
      
      if (existingUser.recordset.length > 0) {
        return NextResponse.json(
          { error: 'Username already exists' },
          { status: 400 }
        );
      }
    }
    
    // Kiểm tra: Hệ thống chỉ có 1 admin duy nhất
    if (role === 'admin') {
      // Lấy role hiện tại của user
      const currentUser = await db.request()
        .input('id', sql.Int, userId)
        .query(`SELECT [role] FROM [dbo].[users] WHERE [id] = @id`);
      
      if (currentUser.recordset.length === 0) {
        return NextResponse.json({ error: 'User not found' }, { status: 404 });
      }
      
      const currentRole = currentUser.recordset[0].role;
      
      // Nếu user hiện tại không phải admin, và đang cố gắng đổi thành admin
      if (currentRole !== 'admin') {
        // Kiểm tra xem đã có admin chưa
        const adminCheck = await db.request().query(`
          SELECT COUNT(*) as count FROM [dbo].[users] WHERE [role] = 'admin'
        `);
        
        if (adminCheck.recordset[0].count > 0) {
          return NextResponse.json(
            { error: 'Hệ thống chỉ cho phép 1 admin duy nhất. Đã có admin trong hệ thống.' },
            { status: 400 }
          );
        }
      }
    }
    
    if (password) {
      // Update password
      const passwordHash = await hashPassword(password);
      await db.request()
        .input('id', sql.Int, userId)
        .input('password_hash', sql.NVarChar(255), passwordHash)
        .query(`UPDATE [dbo].[users] SET [password_hash] = @password_hash WHERE [id] = @id`);
    }
    
    // Update other fields
    const result = await db.request()
      .input('id', sql.Int, userId)
      .input('username', sql.NVarChar(100), username)
      .input('email', sql.NVarChar(255), email || null)
      .input('role', sql.NVarChar(20), role)
      .input('is_active', sql.Bit, is_active !== false)
      .query(`
        UPDATE [dbo].[users]
        SET 
          [username] = @username,
          [email] = @email,
          [role] = @role,
          [is_active] = @is_active,
          [updated_at] = GETDATE()
        WHERE [id] = @id
      `);
    
    if (result.rowsAffected[0] === 0) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }
    
    // Get updated user
    const updated = await db.request()
      .input('id', sql.Int, userId)
      .query(`
        SELECT [id], [username], [email], [role], [is_active], [created_at]
        FROM [dbo].[users] WHERE [id] = @id
      `);
    
    return NextResponse.json({ user: updated.recordset[0] });
  } catch (error: any) {
    console.error('Update user error (detailed):', {
      message: error.message,
      code: error.code,
      number: error.number,
      state: error.state,
      userId: id,
      body: body
    });
    
    // Handle specific SQL errors
    if (error.message?.includes('UNIQUE') || error.message?.includes('duplicate')) {
      return new NextResponse(
        JSON.stringify({ error: 'Username already exists' }),
        { 
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }
    
    const errorMessage = error.message || 'Internal server error';
    return new NextResponse(
      JSON.stringify({ error: errorMessage }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// DELETE user
async function deleteUser(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const db = await getDb();
    
    // Don't allow deleting yourself
    const currentUserId = (req as any).user?.userId;
    const userId = parseInt(id);
    
    if (currentUserId && userId === currentUserId) {
      return NextResponse.json(
        { error: 'Cannot delete your own account' },
        { status: 400 }
      );
    }
    
    // Kiểm tra: Không cho phép xóa admin nếu đó là admin duy nhất
    const userToDelete = await db.request()
      .input('id', sql.Int, userId)
      .query(`SELECT [role] FROM [dbo].[users] WHERE [id] = @id`);
    
    if (userToDelete.recordset.length === 0) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }
    
    if (userToDelete.recordset[0].role === 'admin') {
      // Kiểm tra xem có bao nhiêu admin
      const adminCount = await db.request().query(`
        SELECT COUNT(*) as count FROM [dbo].[users] WHERE [role] = 'admin'
      `);
      
      if (adminCount.recordset[0].count <= 1) {
        return NextResponse.json(
          { error: 'Không thể xóa admin. Hệ thống phải có ít nhất 1 admin.' },
          { status: 400 }
        );
      }
    }
    
    console.log(`Attempting to delete user ID: ${userId}`);
    
    // Delete related sessions first (to avoid FK constraint)
    try {
      const sessionsDeleted = await db.request()
        .input('user_id', sql.Int, userId)
        .query(`DELETE FROM [dbo].[sessions] WHERE [user_id] = @user_id`);
      console.log(`Deleted ${sessionsDeleted.rowsAffected[0]} sessions for user ${userId}`);
    } catch (sessionError: any) {
      console.log('Sessions table error (may not exist):', sessionError.message);
      // Continue even if sessions table doesn't exist
    }
    
    // Update projects to set created_by to NULL (preserve projects)
    try {
      const projectsUpdated = await db.request()
        .input('user_id', sql.Int, userId)
        .query(`UPDATE [dbo].[projects] SET [created_by] = NULL WHERE [created_by] = @user_id`);
      console.log(`Updated ${projectsUpdated.rowsAffected[0]} projects for user ${userId}`);
    } catch (projectError: any) {
      console.log('Projects table error (may not exist):', projectError.message);
      // Continue even if projects table doesn't exist
    }
    
    // Delete user
    const result = await db.request()
      .input('id', sql.Int, userId)
      .query(`DELETE FROM [dbo].[users] WHERE [id] = @id`);
    
    if (result.rowsAffected[0] === 0) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }
    
    console.log(`Successfully deleted user ${userId}`);
    return NextResponse.json({ success: true });
  } catch (error: any) {
    console.error('Delete user error (detailed):', {
      message: error.message,
      code: error.code,
      number: error.number,
      state: error.state,
      stack: error.stack
    });
    
    // Return proper JSON error
    const errorMessage = error.message || 'Internal server error';
    console.error('Returning error:', errorMessage);
    
    return new NextResponse(
      JSON.stringify({ error: errorMessage }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

export const PUT = requireAdmin(updateUser);
export const DELETE = requireAdmin(deleteUser);






