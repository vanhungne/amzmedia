import sql from 'mssql';
import { hashPassword } from './auth';

const config: sql.config = {
  user: process.env.DB_USER || 'sa',
  password: process.env.DB_PASSWORD || '',
  server: process.env.DB_SERVER || 'localhost',
  port: parseInt(process.env.DB_PORT || '1433'),
  database: process.env.DB_NAME || 'WorkFlowAdmin',
  options: {
    encrypt: process.env.DB_ENCRYPT === 'true', // Azure SQL
    trustServerCertificate: process.env.DB_TRUST_CERT === 'true', // Local dev
    enableArithAbort: true,
  },
  pool: {
    max: 10,
    min: 0,
    idleTimeoutMillis: 30000,
  },
};

let pool: sql.ConnectionPool | null = null;

export async function getDb(): Promise<sql.ConnectionPool> {
  if (!pool) {
    pool = await sql.connect(config);
    console.log('✅ Connected to SQL Server');
  }
  return pool;
}

export async function initDatabase(): Promise<void> {
  const db = await getDb();
  
  // Create tables if not exist
  await db.request().query(`
    IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[users]') AND type in (N'U'))
    CREATE TABLE [dbo].[users] (
      [id] INT IDENTITY(1,1) PRIMARY KEY,
      [username] NVARCHAR(100) NOT NULL UNIQUE,
      [email] NVARCHAR(255),
      [password_hash] NVARCHAR(255) NOT NULL,
      [role] NVARCHAR(20) NOT NULL DEFAULT 'user', -- 'admin' or 'user'
      [is_active] BIT NOT NULL DEFAULT 1,
      [total_keys_received] INT NOT NULL DEFAULT 0, -- Total keys ever assigned to this user
      [total_keys_used] INT NOT NULL DEFAULT 0, -- Total keys that have been used (last_used IS NOT NULL)
      [created_at] DATETIME2 DEFAULT GETDATE(),
      [updated_at] DATETIME2 DEFAULT GETDATE()
    );
    
    -- Add tracking columns if table exists but columns don't
    IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[users]') AND type in (N'U'))
    BEGIN
      IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('[dbo].[users]') AND name = 'total_keys_received')
        ALTER TABLE [dbo].[users] ADD [total_keys_received] INT NOT NULL DEFAULT 0;
      
      IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('[dbo].[users]') AND name = 'total_keys_used')
        ALTER TABLE [dbo].[users] ADD [total_keys_used] INT NOT NULL DEFAULT 0;
      
      -- Device lock columns
      IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('[dbo].[users]') AND name = 'device_id')
        ALTER TABLE [dbo].[users] ADD [device_id] NVARCHAR(255) NULL;
      
      IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('[dbo].[users]') AND name = 'device_name')
        ALTER TABLE [dbo].[users] ADD [device_name] NVARCHAR(255) NULL;
      
      IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('[dbo].[users]') AND name = 'device_locked_at')
        ALTER TABLE [dbo].[users] ADD [device_locked_at] DATETIME2 NULL;
    END;

    IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[projects]') AND type in (N'U'))
    CREATE TABLE [dbo].[projects] (
      [id] INT IDENTITY(1,1) PRIMARY KEY,
      [project_id] NVARCHAR(50) NOT NULL UNIQUE, -- UUID from Python tool
      [channel_name] NVARCHAR(255) NOT NULL,
      [script_template] NVARCHAR(MAX), -- System prompt for Groq
      [num_prompts] INT DEFAULT 12,
      [voice_id] NVARCHAR(100), -- ElevenLabs voice ID
      [auto_workflow] BIT DEFAULT 1,
      [created_by] INT FOREIGN KEY REFERENCES [dbo].[users]([id]),
      [created_at] DATETIME2 DEFAULT GETDATE(),
      [updated_at] DATETIME2 DEFAULT GETDATE()
    );

    IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[sessions]') AND type in (N'U'))
    CREATE TABLE [dbo].[sessions] (
      [id] INT IDENTITY(1,1) PRIMARY KEY,
      [user_id] INT NOT NULL FOREIGN KEY REFERENCES [dbo].[users]([id]),
      [token] NVARCHAR(500) NOT NULL UNIQUE,
      [expires_at] DATETIME2 NOT NULL,
      [created_at] DATETIME2 DEFAULT GETDATE()
    );

    IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[elevenlabs_keys]') AND type in (N'U'))
    CREATE TABLE [dbo].[elevenlabs_keys] (
      [id] INT IDENTITY(1,1) PRIMARY KEY,
      [api_key] NVARCHAR(500) NOT NULL UNIQUE,
      [name] NVARCHAR(255), -- Friendly name for the key
      [assigned_user_id] INT NULL FOREIGN KEY REFERENCES [dbo].[users]([id]) ON DELETE SET NULL,
      [status] NVARCHAR(20) NOT NULL DEFAULT 'active', -- 'active', 'dead', 'out_of_credit'
      [credit_balance] INT NULL, -- Remaining credits (if available)
      [last_used] DATETIME2 NULL,
      [last_error] NVARCHAR(MAX) NULL,
      [created_by] INT NOT NULL FOREIGN KEY REFERENCES [dbo].[users]([id]),
      [created_at] DATETIME2 DEFAULT GETDATE(),
      [updated_at] DATETIME2 DEFAULT GETDATE()
    );

    IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[proxy_keys]') AND type in (N'U'))
    CREATE TABLE [dbo].[proxy_keys] (
      [id] INT IDENTITY(1,1) PRIMARY KEY,
      [proxy_key] NVARCHAR(500) NOT NULL UNIQUE, -- Proxy key/URL
      [name] NVARCHAR(255), -- Friendly name
      [assigned_user_id] INT NULL FOREIGN KEY REFERENCES [dbo].[users]([id]) ON DELETE SET NULL,
      [status] NVARCHAR(20) NOT NULL DEFAULT 'active', -- 'active', 'dead'
      [last_validated] DATETIME2 NULL,
      [last_error] NVARCHAR(MAX) NULL,
      [created_by] INT NOT NULL FOREIGN KEY REFERENCES [dbo].[users]([id]),
      [created_at] DATETIME2 DEFAULT GETDATE(),
      [updated_at] DATETIME2 DEFAULT GETDATE()
    );

    IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[activity_logs]') AND type in (N'U'))
    CREATE TABLE [dbo].[activity_logs] (
      [id] INT IDENTITY(1,1) PRIMARY KEY,
      [user_id] INT NOT NULL FOREIGN KEY REFERENCES [dbo].[users]([id]) ON DELETE CASCADE,
      [action] NVARCHAR(100) NOT NULL, -- 'login', 'logout', 'generate_voice', 'generate_image', 'create_project', 'edit_project', 'key_used', 'proxy_used', etc.
      [category] NVARCHAR(50) NOT NULL, -- 'auth', 'project', 'generation', 'api', 'system'
      [details] NVARCHAR(MAX) NULL, -- JSON data with additional info
      [status] NVARCHAR(20) DEFAULT 'success', -- 'success', 'failed', 'error'
      [ip_address] NVARCHAR(50) NULL,
      [device_name] NVARCHAR(255) NULL,
      [created_at] DATETIME2 DEFAULT GETDATE()
    );

    -- Index for faster queries
    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_activity_logs_user_id' AND object_id = OBJECT_ID('[dbo].[activity_logs]'))
    CREATE INDEX IX_activity_logs_user_id ON [dbo].[activity_logs]([user_id]);
    
    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_activity_logs_created_at' AND object_id = OBJECT_ID('[dbo].[activity_logs]'))
    CREATE INDEX IX_activity_logs_created_at ON [dbo].[activity_logs]([created_at] DESC);

    IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[gemini_keys]') AND type in (N'U'))
    CREATE TABLE [dbo].[gemini_keys] (
      [id] INT IDENTITY(1,1) PRIMARY KEY,
      [api_key] NVARCHAR(500) NOT NULL UNIQUE,
      [name] NVARCHAR(255),
      [assigned_user_id] INT NULL FOREIGN KEY REFERENCES [dbo].[users]([id]) ON DELETE SET NULL,
      [status] NVARCHAR(20) NOT NULL DEFAULT 'active', -- 'active', 'dead'
      [last_used] DATETIME2 NULL,
      [last_error] NVARCHAR(MAX) NULL,
      [created_by] INT NOT NULL FOREIGN KEY REFERENCES [dbo].[users]([id]),
      [created_at] DATETIME2 DEFAULT GETDATE(),
      [updated_at] DATETIME2 DEFAULT GETDATE()
    );

    IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[openai_keys]') AND type in (N'U'))
    CREATE TABLE [dbo].[openai_keys] (
      [id] INT IDENTITY(1,1) PRIMARY KEY,
      [api_key] NVARCHAR(500) NOT NULL UNIQUE,
      [name] NVARCHAR(255),
      [assigned_user_id] INT NULL FOREIGN KEY REFERENCES [dbo].[users]([id]) ON DELETE SET NULL,
      [status] NVARCHAR(20) NOT NULL DEFAULT 'active', -- 'active', 'dead'
      [last_used] DATETIME2 NULL,
      [last_error] NVARCHAR(MAX) NULL,
      [created_by] INT NOT NULL FOREIGN KEY REFERENCES [dbo].[users]([id]),
      [created_at] DATETIME2 DEFAULT GETDATE(),
      [updated_at] DATETIME2 DEFAULT GETDATE()
    );

  `);
  
  // Không tự động tạo admin - admin phải được tạo thủ công
  // Hệ thống chỉ có 1 admin duy nhất
  
  console.log('✅ Database initialized');
}

export async function closeDb(): Promise<void> {
  if (pool) {
    await pool.close();
    pool = null;
    console.log('✅ Database connection closed');
  }
}

