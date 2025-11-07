# 🔧 Migration Guide - Add User Key Tracking Columns

## Problem

Nếu bạn gặp lỗi `500 Internal Server Error` khi load Users page, có thể database chưa có columns mới.

## Solution

### Option 1: Auto Migration (Recommended)

Server tự động thêm columns khi start. Chỉ cần restart server:

```bash
# Stop server (Ctrl+C)
# Then start again
npm run dev
```

Server sẽ tự động chạy migration trong `lib/db.ts` function `initDatabase()`.

---

### Option 2: Manual Migration Script

Nếu auto migration không chạy, run manual script:

```bash
npx tsx scripts/add-user-key-tracking.ts
```

**Output sẽ là:**
```
🔄 Starting migration: Add user key tracking columns...
✅ Added column: total_keys_received
✅ Added column: total_keys_used
✅ Migration completed successfully!

📊 Summary:
   - Added: total_keys_received (INT)
   - Added: total_keys_used (INT)
   - Initialized counters from existing data
```

---

### Option 3: Manual SQL (If needed)

Nếu cả 2 cách trên không work, chạy SQL trực tiếp trong SQL Server:

```sql
-- Add columns if they don't exist
IF NOT EXISTS (
  SELECT * FROM sys.columns 
  WHERE object_id = OBJECT_ID('[dbo].[users]') 
  AND name = 'total_keys_received'
)
BEGIN
  ALTER TABLE [dbo].[users]
  ADD [total_keys_received] INT NOT NULL DEFAULT 0;
END

IF NOT EXISTS (
  SELECT * FROM sys.columns 
  WHERE object_id = OBJECT_ID('[dbo].[users]') 
  AND name = 'total_keys_used'
)
BEGIN
  ALTER TABLE [dbo].[users]
  ADD [total_keys_used] INT NOT NULL DEFAULT 0;
END

-- Initialize counters from existing data
UPDATE u
SET u.total_keys_received = (
  SELECT COUNT(*) 
  FROM [dbo].[elevenlabs_keys] k 
  WHERE k.assigned_user_id = u.id
)
FROM [dbo].[users] u;

UPDATE u
SET u.total_keys_used = (
  SELECT COUNT(*) 
  FROM [dbo].[elevenlabs_keys] k 
  WHERE k.assigned_user_id = u.id 
  AND k.last_used IS NOT NULL
)
FROM [dbo].[users] u;
```

---

## Verify Migration Success

### Check in SQL Server:

```sql
-- Check if columns exist
SELECT 
  COLUMN_NAME, 
  DATA_TYPE, 
  IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'users'
  AND COLUMN_NAME IN ('total_keys_received', 'total_keys_used');
```

**Expected output:**
```
COLUMN_NAME            DATA_TYPE    IS_NULLABLE
total_keys_received    int          NO
total_keys_used        int          NO
```

### Check in Browser:

1. Open: `http://localhost:3000/dashboard/users`
2. Table should show columns:
   - Assigned
   - Active
   - Ready (>800)
   - **Ever Received** ← New!
   - **Ever Used** ← New!
3. No 500 errors

---

## Troubleshooting

### Error: "Column already exists"
✅ **Good!** Columns đã có rồi, skip migration.

### Error: "Invalid column name 'total_keys_received'"
❌ Migration chưa chạy. Try:
1. Restart server
2. Run manual script
3. Run SQL manually

### Error: "500 Internal Server Error"
Có thể là:
1. Database connection issue → Check `.env`
2. Columns chưa có → Run migration
3. Permission issue → Check SQL user permissions

Check server logs:
```bash
# Windows PowerShell
Get-Content .next/server/app-paths-manifest.json
```

### API Still Returns Error
The `/api/users` endpoint now has **automatic fallback**:
- If columns exist → Use them
- If columns don't exist → Return 0 for tracking fields
- No more 500 errors!

---

## Rollback (If needed)

Nếu muốn xóa columns:

```sql
ALTER TABLE [dbo].[users] DROP COLUMN [total_keys_received];
ALTER TABLE [dbo].[users] DROP COLUMN [total_keys_used];
```

⚠️ **Warning:** Sẽ mất data tracking!

---

## Summary

**Recommended flow:**
1. ✅ Restart server (auto migration)
2. ✅ Refresh browser
3. ✅ If still error → Run `npx tsx scripts/add-user-key-tracking.ts`
4. ✅ If still error → Run SQL manually
5. ✅ Contact support với screenshot lỗi

**API is now safe:**
- Auto-detects if columns exist
- Fallback to zeros if not
- No breaking changes!

---

**Need help?** Check server logs for detailed error messages.

