# 🔧 Debug Steps - Gemini API Key Error

## Vấn đề hiện tại:

```
☁️ Loading Gemini API keys from server...
❌ Failed to get Gemini keys: Internal server error
```

## ✅ Đã sửa:

1. ✅ SQL syntax "NULLS FIRST" → Dùng CASE WHEN (compatible với SQL Server)
2. ✅ Thêm logging chi tiết để debug
3. ✅ Tạo test endpoint để kiểm tra database

---

## 🔍 BƯỚC 1: Kiểm tra Database có keys chưa

### Option A: Dùng Browser (Dễ nhất)

**Server đang chạy ở port nào?** (thường là 3000 hoặc 3001)

Mở browser và vào:
```
http://localhost:3000/api/test-gemini-db
```

Hoặc:
```
http://localhost:3001/api/test-gemini-db
```

**Kết quả mong đợi:**
```json
{
  "success": true,
  "tableExists": true,
  "totalKeys": 3,
  "statusCounts": [
    { "status": "active", "count": 3 }
  ],
  "keys": [
    {
      "id": 1,
      "api_key_preview": "AIzaSyDoCll...jcNNIKI",
      "key_length": 39,
      "name": "Key 1",
      "status": "active"
    },
    ...
  ]
}
```

**Nếu lỗi:**

### Case 1: `"tableExists": false`
→ Chạy database init script:
```sql
-- Xem file: admin-panel/lib/db.ts để tìm CREATE TABLE script
-- Hoặc tôi sẽ tạo script riêng
```

### Case 2: `"totalKeys": 0`
→ Chưa có keys trong database
→ Thêm keys qua Admin Panel UI

### Case 3: `"status": "inactive"`
→ Keys bị inactive
→ Update status:
```sql
UPDATE [dbo].[gemini_keys]
SET [status] = 'active'
WHERE [id] IN (1, 2, 3);
```

### Case 4: `"key_length": != 39`
→ Keys có vấn đề format
→ Chạy clean script:
```bash
admin-panel/scripts/clean_gemini_keys.sql
```

---

## 🔍 BƯỚC 2: Kiểm tra Server Logs

Mở terminal nơi server đang chạy, xem có lỗi gì:

```bash
cd admin-panel
npm run dev
```

Tìm dòng:
```
Get Gemini keys error: ...
Error details: ...
```

**Các lỗi thường gặp:**

### Lỗi 1: Connection refused
```
Error: Failed to connect to database
```
→ Kiểm tra connection string trong `.env.local`
→ Đảm bảo SQL Server đang chạy

### Lỗi 2: Invalid object name 'gemini_keys'
```
Error: Invalid object name 'dbo.gemini_keys'
```
→ Bảng chưa tồn tại
→ Chạy init script

### Lỗi 3: Column does not exist
```
Error: Invalid column name 'api_key'
```
→ Schema table không đúng
→ Recreate table

---

## 🔍 BƯỚC 3: Test trực tiếp bằng SQL

Mở SSMS và chạy:

```sql
-- Test 1: Kiểm tra table tồn tại
SELECT * FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_NAME = 'gemini_keys';

-- Test 2: Xem tất cả keys
SELECT 
    [id],
    LEFT([api_key], 12) + '...' as preview,
    LEN([api_key]) as length,
    [status],
    [created_at]
FROM [dbo].[gemini_keys];

-- Test 3: Đếm keys active
SELECT COUNT(*) as active_count
FROM [dbo].[gemini_keys]
WHERE [status] = 'active';

-- Test 4: Kiểm tra keys có whitespace không
SELECT 
    [id],
    CASE 
        WHEN [api_key] LIKE '% %' THEN 'Has space'
        WHEN [api_key] LIKE '%' + CHAR(10) + '%' THEN 'Has newline'
        WHEN [api_key] LIKE '%' + CHAR(9) + '%' THEN 'Has tab'
        ELSE 'Clean'
    END as status
FROM [dbo].[gemini_keys];
```

---

## 🔍 BƯỚC 4: Thêm Keys Thủ Công (nếu cần)

Nếu database rỗng, thêm keys bằng SQL:

```sql
-- Thêm 3 keys (thay YOUR_KEY_HERE bằng key thật từ Google AI Studio)
INSERT INTO [dbo].[gemini_keys] 
    ([api_key], [name], [status], [created_by])
VALUES 
    ('YOUR_KEY_1_HERE', 'Gemini Key 1', 'active', 1),
    ('YOUR_KEY_2_HERE', 'Gemini Key 2', 'active', 1),
    ('YOUR_KEY_3_HERE', 'Gemini Key 3', 'active', 1);

-- Verify
SELECT * FROM [dbo].[gemini_keys];
```

---

## 🔍 BƯỚC 5: Test lại từ Client

Sau khi fix database:

1. **Restart admin panel server**
   ```bash
   # Stop server (Ctrl+C)
   cd admin-panel
   npm run dev
   ```

2. **Test endpoint từ browser:**
   ```
   http://localhost:3000/api/tool/gemini
   ```
   
   Cần login trước! Hoặc dùng curl:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        http://localhost:3000/api/tool/gemini
   ```

3. **Load keys từ WorkFlow Tool:**
   - Đăng nhập
   - Vào Image Generator tab
   - Click "🔑 Load Keys"
   - Xem console logs

---

## 📊 Checklist Debug:

- [ ] Server đang chạy (port 3000 hoặc 3001)
- [ ] Test endpoint `/api/test-gemini-db` → Success
- [ ] Database có bảng `gemini_keys`
- [ ] Bảng có ít nhất 1 key với `status='active'`
- [ ] Keys có `length=39`
- [ ] Keys không có whitespace
- [ ] Endpoint `/api/tool/gemini` return keys thành công
- [ ] Client load keys thành công

---

## 🆘 Nếu vẫn lỗi:

Gửi cho tôi:

1. **Kết quả từ `/api/test-gemini-db`:**
   ```json
   { ... paste here ... }
   ```

2. **Server logs:**
   ```
   ... paste error logs here ...
   ```

3. **SQL query result:**
   ```sql
   SELECT * FROM [dbo].[gemini_keys];
   ```

4. **Environment:**
   - SQL Server version: ?
   - Node.js version: ?
   - Next.js dev hoặc production: ?

---

**Good luck debugging!** 🔍





