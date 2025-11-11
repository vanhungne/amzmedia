import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import sql from 'mssql';
import { getDb } from './db';

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-in-production';
const JWT_EXPIRES_IN = '7d';

export interface User {
  id: number;
  username: string;
  email: string | null;
  role: 'admin' | 'user' | 'manager';
  is_active: boolean;
  created_at: Date;
}

export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 10);
}

export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash);
}

export function generateToken(userId: number, username: string, role: string): string {
  return jwt.sign(
    { userId, username, role },
    JWT_SECRET,
    { expiresIn: JWT_EXPIRES_IN }
  );
}

export function verifyToken(token: string): { userId: number; username: string; role: string } | null {
  try {
    return jwt.verify(token, JWT_SECRET) as { userId: number; username: string; role: string };
  } catch {
    return null;
  }
}

export async function createUser(
  username: string,
  password: string,
  email: string | null = null,
  role: 'admin' | 'user' | 'manager' = 'user'
): Promise<User> {
  const db = await getDb();
  const passwordHash = await hashPassword(password);
  
  const result = await db.request()
    .input('username', sql.NVarChar(100), username)
    .input('email', sql.NVarChar(255), email)
    .input('password_hash', sql.NVarChar(255), passwordHash)
    .input('role', sql.NVarChar(20), role)
    .query(`
      INSERT INTO [dbo].[users] ([username], [email], [password_hash], [role])
      OUTPUT INSERTED.id, INSERTED.username, INSERTED.email, INSERTED.role, INSERTED.is_active, INSERTED.created_at
      VALUES (@username, @email, @password_hash, @role)
    `);
  
  return result.recordset[0] as User;
}

export async function getUserByUsername(username: string): Promise<User | null> {
  const db = await getDb();
  const result = await db.request()
    .input('username', sql.NVarChar(100), username)
    .query(`
      SELECT [id], [username], [email], [password_hash], [role], [is_active], [created_at]
      FROM [dbo].[users]
      WHERE [username] = @username
    `);
  
  if (result.recordset.length === 0) return null;
  return result.recordset[0] as User;
}

export async function getUserById(id: number): Promise<User | null> {
  const db = await getDb();
  const result = await db.request()
    .input('id', sql.Int, id)
    .query(`
      SELECT [id], [username], [email], [role], [is_active], [created_at]
      FROM [dbo].[users]
      WHERE [id] = @id
    `);
  
  if (result.recordset.length === 0) return null;
  return result.recordset[0] as User;
}

export async function authenticateUser(username: string, password: string): Promise<{ user: User; token: string } | null> {
  try {
    const user = await getUserByUsername(username);
    if (!user) {
      console.log(`[AUTH] User not found: ${username}`);
      return null;
    }
    
    if (!user.is_active) {
      console.log(`[AUTH] User is inactive: ${username}`);
      return null;
    }
    
    const db = await getDb();
    const result = await db.request()
      .input('username', sql.NVarChar(100), username)
      .query(`SELECT [password_hash] FROM [dbo].[users] WHERE [username] = @username`);
    
    if (!result.recordset || result.recordset.length === 0 || !result.recordset[0].password_hash) {
      console.error(`[AUTH] Password hash not found for user: ${username}`);
      return null;
    }
    
    const passwordHash = result.recordset[0].password_hash;
    const isValid = await verifyPassword(password, passwordHash);
    
    if (!isValid) {
      console.log(`[AUTH] Invalid password for user: ${username}`);
      return null;
    }
    
    const token = generateToken(user.id, user.username, user.role);
    
    // Save session
    await db.request()
      .input('user_id', sql.Int, user.id)
      .input('token', sql.NVarChar(500), token)
      .input('expires_at', sql.DateTime2, new Date(Date.now() + 7 * 24 * 60 * 60 * 1000))
      .query(`
        INSERT INTO [dbo].[sessions] ([user_id], [token], [expires_at])
        VALUES (@user_id, @token, @expires_at)
      `);
    
    console.log(`[AUTH] Successfully authenticated user: ${username}`);
    return { user, token };
  } catch (error: any) {
    console.error(`[AUTH] Authentication error for user ${username}:`, error);
    return null;
  }
}

