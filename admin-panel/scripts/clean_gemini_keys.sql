-- Clean existing Gemini API keys in database
-- This script removes whitespace, newlines, tabs from api_key column
-- Run this ONCE to clean existing keys

-- Backup first (optional)
-- SELECT * INTO gemini_keys_backup FROM [dbo].[gemini_keys]

-- Clean all keys: trim and remove newlines, tabs, carriage returns
UPDATE [dbo].[gemini_keys]
SET [api_key] = REPLACE(REPLACE(REPLACE(LTRIM(RTRIM([api_key])), CHAR(13), ''), CHAR(10), ''), CHAR(9), '')
WHERE [api_key] IS NOT NULL;

-- Verify cleaned keys
SELECT 
    [id],
    [api_key],
    LEN([api_key]) as key_length,
    [name],
    [status]
FROM [dbo].[gemini_keys]
ORDER BY [id];

-- Check for any keys with unusual characters
SELECT 
    [id],
    [api_key],
    'Key contains space' as issue
FROM [dbo].[gemini_keys]
WHERE [api_key] LIKE '% %'

UNION ALL

SELECT 
    [id],
    [api_key],
    'Key contains newline' as issue
FROM [dbo].[gemini_keys]
WHERE [api_key] LIKE '%' + CHAR(10) + '%' OR [api_key] LIKE '%' + CHAR(13) + '%'

UNION ALL

SELECT 
    [id],
    [api_key],
    'Key contains tab' as issue
FROM [dbo].[gemini_keys]
WHERE [api_key] LIKE '%' + CHAR(9) + '%';

PRINT 'Gemini API keys cleaned successfully!';

