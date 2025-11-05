import { NextRequest, NextResponse } from 'next/server';
import { authenticateUser } from '@/lib/auth';
import { initDatabase, getDb } from '@/lib/db';
import sql from 'mssql';

/**
 * API endpoint for Python tool to authenticate users
 * POST /api/tool/auth
 * Body: { username, password, device_id, device_name }
 * Returns: { success, token, user }
 * 
 * Device Lock Logic:
 * - If user has no device_id: register this device (first login)
 * - If user has device_id:
 *   - If matches: allow login and update device_name
 *   - If doesn't match: reject with error message
 */
export async function POST(req: NextRequest) {
  try {
    await initDatabase();
    
    const { username, password, device_id, device_name } = await req.json();
    
    if (!username || !password) {
      return NextResponse.json(
        { success: false, error: 'Username and password are required' },
        { status: 400 }
      );
    }
    
    if (!device_id) {
      return NextResponse.json(
        { success: false, error: 'Device ID is required' },
        { status: 400 }
      );
    }
    
    const result = await authenticateUser(username, password);
    
    if (!result) {
      return NextResponse.json(
        { success: false, error: 'Invalid credentials' },
        { status: 401 }
      );
    }
    
    // Check device lock
    const db = await getDb();
    const userDevice = await db.request()
      .input('user_id', sql.Int, result.user.id)
      .query(`
        SELECT [device_id], [device_name] 
        FROM [dbo].[users] 
        WHERE [id] = @user_id
      `);
    
    const existingDeviceId = userDevice.recordset[0]?.device_id;
    
    if (existingDeviceId) {
      // User already has a registered device
      if (existingDeviceId !== device_id) {
        // Different device - reject login
        console.log(`[DEVICE LOCK] User ${username} attempted login from different device`);
        console.log(`  Expected: ${existingDeviceId}`);
        console.log(`  Got: ${device_id}`);
        
        return NextResponse.json(
          { 
            success: false, 
            error: '🔒 This account is registered on another device.\n\nPlease contact your administrator to change device.' 
          },
          { status: 403 }
        );
      }
      
      // Same device - update device_name and last login time
      await db.request()
        .input('user_id', sql.Int, result.user.id)
        .input('device_name', sql.NVarChar(255), device_name || null)
        .query(`
          UPDATE [dbo].[users]
          SET [device_name] = @device_name,
              [device_locked_at] = GETDATE(),
              [updated_at] = GETDATE()
          WHERE [id] = @user_id
        `);
      
      console.log(`[DEVICE LOCK] User ${username} logged in from registered device: ${device_name}`);
      
    } else {
      // No device registered yet - register this device
      await db.request()
        .input('user_id', sql.Int, result.user.id)
        .input('device_id', sql.NVarChar(255), device_id)
        .input('device_name', sql.NVarChar(255), device_name || null)
        .query(`
          UPDATE [dbo].[users]
          SET [device_id] = @device_id,
              [device_name] = @device_name,
              [device_locked_at] = GETDATE(),
              [updated_at] = GETDATE()
          WHERE [id] = @user_id
        `);
      
      console.log(`[DEVICE LOCK] User ${username} registered new device: ${device_name} (${device_id})`);
    }
    
    // Return token and user info for Python tool
    return NextResponse.json({
      success: true,
      token: result.token,
      user: {
        id: result.user.id,
        username: result.user.username,
        email: result.user.email,
        role: result.user.role,
      },
    });
  } catch (error: any) {
    console.error('Tool auth error:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}






