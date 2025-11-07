# 🚨 Fix "Internal Server Error" khi Load Gemini Keys

## ❌ Lỗi hiện tại:

```
☁️ Loading Gemini API keys from server...
❌ Failed to get Gemini keys: Internal server error
⚠️ No Gemini keys found on server or failed to load
```

---

## ✅ Nguyên nhân & Giải pháp:

### Có thể 1 trong các vấn đề sau:

1. ✅ **SQL syntax không tương thích** → ĐÃ SỬA (NULLS FIRST → CASE WHEN)
2. ⚠️ **Database chưa có bảng `gemini_keys`** → CẦN KIỂM TRA
3. ⚠️ **Bảng rỗng (không có keys)** → CẦN THÊM KEYS
4. ⚠️ **Database connection error** → CẦN KIỂM TRA CONNECTION

---

## 🔍 BƯỚC 1: Kiểm tra Database (QUAN TRỌNG!)

### Cách 1: Dùng Test Endpoint (Nhanh nhất)

Server của bạn đang chạy ở port nào? (kiểm tra terminal)

Mở browser và vào:
```
http://localhost:3000/api/test-gemini-db
```

**HOẶC** (nếu port khác):
```
http://localhost:3001/api/test-gemini-db
```

---

### 📊 Kết quả có thể gặp:

#### ✅ **Trường hợp 1: Table tồn tại, có keys**

```json
{
  "success": true,
  "tableExists": true,
  "totalKeys": 3,
  "statusCounts": [
    { "status": "active", "count": 3 }
  ],
  "keys": [...]
}
```

**→ TUYỆT!** Database ổn, vấn đề có thể ở chỗ khác.

**Tiếp tục:**
- Restart server: `Ctrl+C` → `npm run dev`
- Test lại load keys từ client
- Nếu vẫn lỗi, gửi **server logs** cho tôi

---

#### ⚠️ **Trường hợp 2: Table tồn tại, NHƯNG không có keys**

```json
{
  "success": true,
  "tableExists": true,
  "totalKeys": 0,
  "keys": []
}
```

**→ CẦN THÊM KEYS!**

**Giải pháp:** Chọn 1 trong 2

**Option A - Qua Admin Panel UI (Dễ):**
1. Mở Admin Panel: `http://localhost:3000`
2. Đăng nhập
3. Vào: **Dashboard** → **Gemini Keys**
4. Click **"Add Key"**
5. Paste API key từ Google AI Studio
6. Lặp lại cho 3 keys

**Option B - Qua SQL (Nhanh):**
```sql
-- Thay YOUR_KEY_HERE bằng keys thật
INSERT INTO [dbo].[gemini_keys] ([api_key], [name], [status], [created_by])
VALUES 
    ('AIzaSy...key1...', 'Gemini Key 1', 'active', 1),
    ('AIzaSy...key2...', 'Gemini Key 2', 'active', 1),
    ('AIzaSy...key3...', 'Gemini Key 3', 'active', 1);
```

---

#### ❌ **Trường hợp 3: Table KHÔNG tồn tại**

```json
{
  "success": false,
  "error": "Table gemini_keys does not exist"
}
```

**→ CẦN TẠO TABLE!**

**Giải pháp:**

1. **Mở SQL Server Management Studio (SSMS)**
2. **Connect tới database của bạn**
3. **Chạy script:** `admin-panel/scripts/init_gemini_keys_table.sql`
4. **Verify:** Script sẽ hiển thị "✅ Table created successfully"
5. **Thêm keys** (xem Trường hợp 2 ở trên)

---

#### ❌ **Trường hợp 4: Database connection error**

```json
{
  "success": false,
  "error": "Database error",
  "details": "Failed to connect..."
}
```

**→ KIỂM TRA CONNECTION!**

**Giải pháp:**

1. **Kiểm tra SQL Server đang chạy:**
   - Mở **SQL Server Configuration Manager**
   - Đảm bảo **SQL Server service** đang chạy

2. **Kiểm tra connection string:**
   - File: `admin-panel/.env.local`
   - Biến: `DATABASE_URL`
   - Format: `Server=localhost;Database=WorkFlow;User Id=sa;Password=...;`

3. **Test connection từ SSMS:**
   - Thử connect với cùng thông tin
   - Nếu connect được → connection string sai
   - Nếu không connect được → SQL Server issue

---

## 🔧 BƯỚC 2: Restart Server

Sau khi sửa database:

```bash
cd admin-panel

# Stop server (nếu đang chạy)
# Ctrl + C

# Start lại
npm run dev
```

Đợi thấy:
```
✓ Ready in Xs
○ Local:   http://localhost:3000
```

---

## 🧪 BƯỚC 3: Test Lại

### Test 1: Verify endpoint hoạt động

```
http://localhost:3000/api/test-gemini-db
```

Phải thấy:
```json
{
  "success": true,
  "totalKeys": 3,
  ...
}
```

### Test 2: Load keys từ WorkFlow Tool

1. **Mở WorkFlow Tool**
2. **Đăng nhập**
3. **Vào tab Image Generator**
4. **Click "🔑 Load Keys"**
5. **Xem console logs:**

```
☁️ Loading Gemini API keys from server...
🔑 Loaded key 1: AIzaSyDo...jcNNIKI (length: 39)
🔑 Loaded key 2: AIzaSyCz...X99k (length: 39)
🔑 Loaded key 3: AIzaSyAS...kkoM (length: 39)
✅ Loaded 3 Gemini API keys from server successfully
```

### Test 3: Generate Image

1. **Thêm prompt:** "A beautiful sunset"
2. **Click ▶️ Run Selected**
3. **Image generated!** ✅

---

## 📋 Checklist:

- [ ] Server đang chạy (npm run dev)
- [ ] Test endpoint `/api/test-gemini-db` → Success
- [ ] Database có bảng `gemini_keys` ✅
- [ ] Bảng có 3 keys với `status='active'` ✅
- [ ] Keys có length = 39 ✅
- [ ] Restart server ✅
- [ ] Load keys từ client thành công ✅
- [ ] Generate image thành công ✅

---

## 🆘 Vẫn lỗi? Gửi cho tôi:

### 1. Kết quả test endpoint:
```
http://localhost:3000/api/test-gemini-db
```
→ Copy toàn bộ JSON response

### 2. Server logs:
```bash
cd admin-panel
npm run dev
```
→ Copy error logs (màu đỏ)

### 3. SQL query kết quả:
```sql
SELECT * FROM [dbo].[gemini_keys];
```
→ Screenshot hoặc copy text

### 4. Environment info:
- **SQL Server version:** ?
- **Node.js version:** `node --version`
- **npm version:** `npm --version`
- **Port đang dùng:** ?

---

## 📝 Files liên quan:

1. ✅ `admin-panel/app/api/tool/gemini/route.ts` - API endpoint (ĐÃ SỬA)
2. ✅ `admin-panel/app/api/test-gemini-db/route.ts` - Test endpoint (MỚI)
3. 📄 `admin-panel/scripts/init_gemini_keys_table.sql` - Create table
4. 📄 `admin-panel/scripts/clean_gemini_keys.sql` - Clean keys
5. 📄 `DEBUG_STEPS.md` - Chi tiết debug steps

---

**Làm theo từng bước và sẽ fix được!** 💪





