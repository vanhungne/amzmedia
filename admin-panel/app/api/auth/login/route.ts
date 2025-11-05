import { NextRequest, NextResponse } from 'next/server';
import { authenticateUser } from '@/lib/auth';
import { initDatabase } from '@/lib/db';

export async function POST(req: NextRequest) {
  try {
    // Clear any existing auth cookie first
    const existingToken = req.cookies.get('auth_token')?.value;
    if (existingToken) {
      console.log('[LOGIN] Clearing existing auth token');
    }
    
    // Initialize database on first request
    await initDatabase();
    
    const { username, password } = await req.json();
    
    if (!username || !password) {
      console.log('[LOGIN] Missing username or password');
      return NextResponse.json(
        { error: 'Username and password are required' },
        { status: 400 }
      );
    }
    
    console.log(`[LOGIN] Attempting login for user: ${username}`);
    const result = await authenticateUser(username, password);
    
    if (!result) {
      console.log(`[LOGIN] Authentication failed for user: ${username}`);
      return NextResponse.json(
        { error: 'Invalid credentials' },
        { status: 401 }
      );
    }
    
    console.log(`[LOGIN] Login successful for user: ${username}`);
    
    const response = NextResponse.json({
      success: true,
      user: {
        id: result.user.id,
        username: result.user.username,
        email: result.user.email,
        role: result.user.role,
      },
      token: result.token,
    });
    
    // Clear old cookie first, then set new one
    response.cookies.delete('auth_token');
    response.cookies.set('auth_token', result.token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 7, // 7 days
      path: '/',
    });
    
    return response;
  } catch (error: any) {
    console.error('Login error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

