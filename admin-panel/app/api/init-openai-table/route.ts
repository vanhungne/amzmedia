import { NextRequest, NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/middleware';
import { getDb } from '@/lib/db';

/**
 * POST /api/init-openai-table
 * Initialize openai_keys table (Admin only)
 * This is a one-time migration endpoint
 */
async function initOpenAITable(req: NextRequest) {
  try {
    const db = await getDb();
    
    // Check if table exists
    const checkResult = await db.request().query(`
      SELECT COUNT(*) as count 
      FROM INFORMATION_SCHEMA.TABLES 
      WHERE TABLE_NAME = 'openai_keys'
    `);
    
    if (checkResult.recordset[0].count > 0) {
      return NextResponse.json({ 
        success: true, 
        message: 'Table openai_keys already exists',
        alreadyExists: true
      });
    }
    
    // Create table
    await db.request().query(`
      CREATE TABLE [dbo].[openai_keys] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [api_key] NVARCHAR(500) NOT NULL UNIQUE,
        [name] NVARCHAR(255),
        [assigned_user_id] INT NULL FOREIGN KEY REFERENCES [dbo].[users]([id]) ON DELETE SET NULL,
        [status] NVARCHAR(20) NOT NULL DEFAULT 'active',
        [last_used] DATETIME2 NULL,
        [last_error] NVARCHAR(MAX) NULL,
        [created_by] INT NOT NULL FOREIGN KEY REFERENCES [dbo].[users]([id]),
        [created_at] DATETIME2 DEFAULT GETDATE(),
        [updated_at] DATETIME2 DEFAULT GETDATE()
      );
      
      -- Create indexes
      CREATE INDEX IX_openai_keys_status ON [dbo].[openai_keys]([status]);
      CREATE INDEX IX_openai_keys_last_used ON [dbo].[openai_keys]([last_used]);
    `);
    
    // Verify
    const verifyResult = await db.request().query(`
      SELECT COUNT(*) as count 
      FROM INFORMATION_SCHEMA.TABLES 
      WHERE TABLE_NAME = 'openai_keys'
    `);
    
    if (verifyResult.recordset[0].count > 0) {
      return NextResponse.json({ 
        success: true, 
        message: 'Table openai_keys created successfully',
        alreadyExists: false
      });
    } else {
      return NextResponse.json({ 
        success: false, 
        error: 'Failed to create table' 
      }, { status: 500 });
    }
  } catch (error: any) {
    console.error('Init OpenAI table error:', error);
    return NextResponse.json({ 
      success: false,
      error: 'Internal server error', 
      details: error.message 
    }, { status: 500 });
  }
}

export const POST = requireAdmin(initOpenAITable);

