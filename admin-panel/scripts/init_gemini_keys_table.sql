-- =============================================
-- Initialize Gemini Keys Table
-- Run this if table doesn't exist
-- =============================================

-- Check if table exists
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'gemini_keys')
BEGIN
    PRINT 'Creating gemini_keys table...';
    
    CREATE TABLE [dbo].[gemini_keys] (
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
        CONSTRAINT [FK_gemini_keys_assigned_user] 
            FOREIGN KEY ([assigned_user_id]) 
            REFERENCES [dbo].[users]([id]) 
            ON DELETE SET NULL,
        
        CONSTRAINT [FK_gemini_keys_created_by] 
            FOREIGN KEY ([created_by]) 
            REFERENCES [dbo].[users]([id]) 
            ON DELETE SET NULL,
        
        -- Check constraints
        CONSTRAINT [CK_gemini_keys_status] 
            CHECK ([status] IN ('active', 'dead', 'quota_exceeded'))
    );
    
    -- Create indexes for better performance
    CREATE INDEX [IX_gemini_keys_status] ON [dbo].[gemini_keys]([status]);
    CREATE INDEX [IX_gemini_keys_last_used] ON [dbo].[gemini_keys]([last_used]);
    
    PRINT '✅ Table gemini_keys created successfully!';
END
ELSE
BEGIN
    PRINT '⚠️ Table gemini_keys already exists.';
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
WHERE TABLE_NAME = 'gemini_keys'
ORDER BY ORDINAL_POSITION;

-- Display current data count
PRINT '';
PRINT 'Current data:';
DECLARE @count INT;
SELECT @count = COUNT(*) FROM [dbo].[gemini_keys];
PRINT 'Total keys: ' + CAST(@count AS NVARCHAR(10));

-- Display sample data if exists
IF @count > 0
BEGIN
    PRINT '';
    PRINT 'Sample keys:';
    SELECT TOP 5
        [id],
        LEFT([api_key], 12) + '...' + RIGHT([api_key], 8) as api_key_preview,
        LEN([api_key]) as key_length,
        [name],
        [status],
        [created_at]
    FROM [dbo].[gemini_keys]
    ORDER BY [id];
END
ELSE
BEGIN
    PRINT '';
    PRINT '⚠️ No keys found. You need to add keys via:';
    PRINT '   1. Admin Panel UI, OR';
    PRINT '   2. SQL INSERT statements';
    PRINT '';
    PRINT 'Example INSERT:';
    PRINT 'INSERT INTO [dbo].[gemini_keys] ([api_key], [name], [status], [created_by])';
    PRINT 'VALUES (''AIzaSy...'', ''Gemini Key 1'', ''active'', 1);';
END

GO























