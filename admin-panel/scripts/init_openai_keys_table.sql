-- =============================================
-- Initialize OpenAI Keys Table
-- Run this if table doesn't exist
-- =============================================

-- Check if table exists
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'openai_keys')
BEGIN
    PRINT 'Creating openai_keys table...';
    
    CREATE TABLE [dbo].[openai_keys] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [api_key] NVARCHAR(500) NOT NULL UNIQUE,
        [name] NVARCHAR(255) NULL,
        [assigned_user_id] INT NULL,
        [status] NVARCHAR(20) NOT NULL DEFAULT 'active',
        [last_used] DATETIME NULL,
        [last_error] NVARCHAR(MAX) NULL,
        [created_by] INT NULL,
        [created_at] DATETIME NOT NULL DEFAULT GETDATE(),
        [updated_at] DATETIME NOT NULL DEFAULT GETDATE(),
        
        -- Foreign key constraints
        CONSTRAINT [FK_openai_keys_assigned_user] 
            FOREIGN KEY ([assigned_user_id]) 
            REFERENCES [dbo].[users]([id]) 
            ON DELETE SET NULL,
        
        CONSTRAINT [FK_openai_keys_created_by] 
            FOREIGN KEY ([created_by]) 
            REFERENCES [dbo].[users]([id]) 
            ON DELETE SET NULL,
        
        -- Check constraints
        CONSTRAINT [CK_openai_keys_status] 
            CHECK ([status] IN ('active', 'dead'))
    );
    
    -- Create indexes for better performance
    CREATE INDEX [IX_openai_keys_status] ON [dbo].[openai_keys]([status]);
    CREATE INDEX [IX_openai_keys_last_used] ON [dbo].[openai_keys]([last_used]);
    
    PRINT '✅ Table openai_keys created successfully!';
END
ELSE
BEGIN
    PRINT '⚠️ Table openai_keys already exists.';
END

-- Display table structure
PRINT '';
PRINT 'Table structure:';
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'openai_keys'
ORDER BY ORDINAL_POSITION;

