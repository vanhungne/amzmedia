import { NextRequest, NextResponse } from 'next/server';
import { verifyToken } from './auth';

export interface AuthRequest extends NextRequest {
  user?: {
    userId: number;
    username: string;
    role: string;
  };
}

export function requireAuth(
  handler: (req: AuthRequest, context?: any) => Promise<NextResponse>,
  roles: ('admin' | 'user')[] = ['admin', 'user']
) {
  return async (req: NextRequest, context?: any): Promise<NextResponse> => {
    const token = req.headers.get('authorization')?.replace('Bearer ', '') ||
                  req.cookies.get('auth_token')?.value;
    
    if (!token) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }
    
    const decoded = verifyToken(token);
    if (!decoded) {
      return NextResponse.json({ error: 'Invalid token' }, { status: 401 });
    }
    
    if (!roles.includes(decoded.role as 'admin' | 'user')) {
      return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
    }
    
    (req as AuthRequest).user = decoded;
    return handler(req as AuthRequest, context);
  };
}

export function requireAdmin(
  handler: (req: AuthRequest, context?: any) => Promise<NextResponse>
) {
  return requireAuth(handler, ['admin']);
}

