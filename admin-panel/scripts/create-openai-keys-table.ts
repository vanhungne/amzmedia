import { getDb } from '../lib/db';
import sql from 'mssql';

async function createOpenAIKeysTable() {
  try {
    console.log('🔧 Creating openai_keys table...');
    
    const db = await getDb();
    
    await db.request().query(`
      IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[openai_keys]') AND type in (N'U'))
      BEGIN
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
        
        -- Create indexes for better performance
        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_openai_keys_status' AND object_id = OBJECT_ID('[dbo].[openai_keys]'))
        CREATE INDEX IX_openai_keys_status ON [dbo].[openai_keys]([status]);
        
        IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_openai_keys_last_used' AND object_id = OBJECT_ID('[dbo].[openai_keys]'))
        CREATE INDEX IX_openai_keys_last_used ON [dbo].[openai_keys]([last_used]);
        
        PRINT '✅ Table [dbo].[openai_keys] created successfully';
      END
      ELSE
      BEGIN
        PRINT 'ℹ️  Table [dbo].[openai_keys] already exists';
      END
    `);
    
    // Verify table was created
    const checkResult = await db.request().query(`
      SELECT COUNT(*) as count 
      FROM INFORMATION_SCHEMA.TABLES 
      WHERE TABLE_NAME = 'openai_keys'
    `);
    
    if (checkResult.recordset[0].count > 0) {
      console.log('✅ Table openai_keys exists in database');
      
      // Show table structure
      const columns = await db.request().query(`
        SELECT 
          COLUMN_NAME,
          DATA_TYPE,
          CHARACTER_MAXIMUM_LENGTH,
          IS_NULLABLE,
          COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'openai_keys'
        ORDER BY ORDINAL_POSITION
      `);
      
      console.log('\n📋 Table structure:');
      columns.recordset.forEach((col: any) => {
        console.log(`  - ${col.COLUMN_NAME}: ${col.DATA_TYPE}${col.CHARACTER_MAXIMUM_LENGTH ? `(${col.CHARACTER_MAXIMUM_LENGTH})` : ''} ${col.IS_NULLABLE === 'YES' ? 'NULL' : 'NOT NULL'}`);
      });
    } else {
      console.log('❌ Table openai_keys was not created');
    }
    
    console.log('\n✅ Migration completed successfully!');
    process.exit(0);
  } catch (error: any) {
    console.error('❌ Migration failed:', error);
    console.error('Error details:', error.message);
    if (error.stack) {
      console.error('Stack trace:', error.stack);
    }
    process.exit(1);
  }
}

createOpenAIKeysTable();

