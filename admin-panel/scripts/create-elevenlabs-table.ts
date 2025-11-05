import { getDb } from '../lib/db';
import sql from 'mssql';

async function createElevenLabsTable() {
  try {
    console.log('🔧 Creating elevenlabs_keys table...');
    
    const db = await getDb();
    
    await db.request().query(`
      IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[elevenlabs_keys]') AND type in (N'U'))
      BEGIN
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
        PRINT '✅ Table [dbo].[elevenlabs_keys] created successfully';
      END
      ELSE
      BEGIN
        PRINT 'ℹ️  Table [dbo].[elevenlabs_keys] already exists';
      END
    `);
    
    console.log('✅ Migration completed successfully!');
    process.exit(0);
  } catch (error) {
    console.error('❌ Migration failed:', error);
    process.exit(1);
  }
}

createElevenLabsTable();


