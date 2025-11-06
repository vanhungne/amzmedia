# 🚀 Hướng Dẫn Sửa Lỗi Gemini API Key - Quick Guide

## ❌ Lỗi bạn gặp phải:

```
Error: 400 INVALID_ARGUMENT
'API key not valid. Please pass a valid API key.'
```

## ✅ Nguyên nhân & Giải pháp:

### Vấn đề 1: Code dùng hardcoded keys thay vì load từ server
**→ ĐÃ SỬA:** Code giờ load keys từ Admin Panel server

### Vấn đề 2: Keys có thể có khoảng trắng/ký tự thừa
**→ ĐÃ SỬA:** Keys được clean tự động ở cả server và client

---

## 🔧 BƯỚC 1: Clean Keys Trong Database (QUAN TRỌNG!)

### Option A: Chạy SQL Script (Recommended)

1. Mở **SQL Server Management Studio (SSMS)**
2. Connect tới database của bạn
3. Mở file: `admin-panel/scripts/clean_gemini_keys.sql`
4. Chạy script
5. Xem kết quả - keys đã được clean

### Option B: Thêm Keys Mới Qua UI

1. Vào **Admin Panel** → Dashboard → **Gemini Keys**
2. **Xóa** tất cả keys cũ
3. **Thêm lại** 3 keys mới từ Google AI Studio
4. Keys mới sẽ tự động được clean khi lưu

---

## 🔧 BƯỚC 2: Restart Admin Panel Server

Nếu bạn đang chạy dev server:

```bash
cd admin-panel
npm run dev
# hoặc
yarn dev
```

Nếu production:
```bash
npm run build
npm start
```

---

## 🔧 BƯỚC 3: Test Lại

### 3.1. Đăng nhập WorkFlow Tool
- Mở application
- Đăng nhập với tài khoản của bạn
- Đợi 2 giây

### 3.2. Kiểm tra Keys Đã Load
Bạn sẽ thấy thông báo popup:
```
✅ Loaded 3 Gemini API keys from server!
Keys are ready for image generation.
🔒 Keys are stored securely in memory.
```

### 3.3. Xem Console Logs
Console sẽ hiển thị:
```
☁️ Loading Gemini API keys from server...
🔑 Loaded key 1: AIzaSyDo...jcNNIKI (length: 39)
🔑 Loaded key 2: AIzaSyCz...X99k (length: 39)
🔑 Loaded key 3: AIzaSyAS...kkoM (length: 39)
✅ Loaded 3 Gemini API keys from server successfully
📝 Keys are ready for use. First key starts with: AIzaSyDoCll...
```

**Chú ý:** Length của Google AI API key thường là **39 ký tự**

### 3.4. Test Generate Image
1. Vào tab **Image Generator**
2. Thêm một prompt: "A beautiful sunset over the ocean"
3. Click **▶️ Run Selected**
4. Image sẽ được generate thành công! ✅

---

## ❓ Vẫn Còn Lỗi?

### Kiểm tra 1: Keys có đúng format không?

Google AI Studio API keys có format:
- Bắt đầu bằng: `AIza`
- Length: 39 ký tự
- Chỉ chứa: chữ cái, số, dấu gạch ngang, gạch dưới
- **KHÔNG có** khoảng trắng, newline, tab

Ví dụ keys ĐÚNG:
```
AIzaSyDoCllssgPY3ucNV6mTemLRWJg9jcNNIKI
```

Ví dụ keys SAI:
```
AIzaSyDoCllssgPY3ucNV6mTemLRWJg9jcNNIKI   ← có space cuối
AIzaSyDoCllssgPY3ucNV6mTem
LRWJg9jcNNIKI                             ← có newline
```

### Kiểm tra 2: Keys có active trên Google AI Studio không?

1. Vào https://aistudio.google.com/app/apikey
2. Kiểm tra keys còn active
3. Nếu bị revoke → Tạo keys mới

### Kiểm tra 3: Database có keys không?

Chạy SQL:
```sql
SELECT 
    [id],
    [api_key],
    LEN([api_key]) as length,
    [status]
FROM [dbo].[gemini_keys]
WHERE [status] = 'active';
```

Phải có ít nhất 1 key với:
- `status = 'active'`
- `length = 39`

### Kiểm tra 4: Server có chạy không?

Test endpoint:
```bash
curl http://localhost:3001/api/health
```

Hoặc mở browser: `http://localhost:3001`

---

## 📝 Tóm tắt các files đã sửa:

1. ✅ **image_tab_full.py**
   - Thêm `api_client` parameter
   - Thêm method `load_gemini_keys_from_server()`
   - Thêm button "🔑 Load Keys"
   - Clean keys khi load

2. ✅ **GenVideoPro.py**
   - Pass `api_client` cho ImageGeneratorTab
   - Auto-load keys sau login (2s delay)

3. ✅ **admin-panel/app/api/tool/gemini/route.ts**
   - Clean keys trước khi trả về cho client

4. ✅ **admin-panel/app/api/gemini/route.ts**
   - Clean keys trước khi lưu vào database

5. ✅ **admin-panel/scripts/clean_gemini_keys.sql**
   - Script để clean keys hiện có trong database

---

## 🎯 Kết quả mong đợi:

**TRƯỚC:**
```
❌ Error: 400 INVALID_ARGUMENT - API key not valid
```

**SAU:**
```
✅ Loaded 3 Gemini API keys from server!
✅ Generate image successfully!
```

---

## 📞 Cần hỗ trợ thêm?

Nếu sau tất cả các bước trên vẫn lỗi, cung cấp thông tin:

1. **Console logs** khi load keys
2. **SQL query result** từ database
3. **API key format** (8 ký tự đầu + 8 ký tự cuối)
4. **Server logs** nếu có

---

**Good luck!** 🚀

