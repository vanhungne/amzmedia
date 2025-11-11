# 🔧 Hướng dẫn Fix vấn đề Cache và xem đủ 1000 Keys

## Vấn đề
- Database có 1000 keys nhưng frontend chỉ hiển thị 50 keys
- **Nguyên nhân:** Next.js App Router có caching behavior mặc định

## ✅ Đã Fix
1. ✅ Tắt cache cho API route
2. ✅ Tắt cache cho fetch client-side  
3. ✅ Tăng limit mặc định từ 50 → 100 keys/page
4. ✅ Thêm nút "Refresh" để reload dữ liệu
5. ✅ Pagination đã hoạt động tốt

## 🚀 Cách sử dụng (sau khi fix)

### Bước 1: Restart Dev Server
```bash
# Dừng server hiện tại (Ctrl+C)
# Sau đó chạy lại:
cd admin-panel
npm run dev
```

### Bước 2: Hard Refresh Browser
- **Windows:** `Ctrl + Shift + R` hoặc `Ctrl + F5`
- **Mac:** `Cmd + Shift + R`

### Bước 3: Click nút "Refresh" trên UI
- Trang ElevenLabs có nút **"Refresh"** màu xanh
- Click để reload data từ database

### Bước 4: Sử dụng Pagination
Sau khi refresh, bạn sẽ thấy:

#### 📊 Stats (đầu trang):
```
Total Keys: 1000      ← Tổng số keys trong database
Active Keys: 1000     ← Keys đang hoạt động
Assigned Keys: 200    ← Keys đã cấp phát cho users
Unassigned Keys: 800  ← Keys chưa cấp phát
```

#### 📄 Pagination (cuối trang):
```
Trang 1 / 10 • Hiển thị 1 - 100 trong tổng số 1,000 keys

Hiển thị: [25] [50] [100] [200] [500] keys/trang
          ↑ Dropdown để chọn số lượng hiển thị

[<<] [< Trước] [1] [2] [3] [4] [5] ... [10] [Sau >] [>>]
 ↑      ↑                                      ↑       ↑
First Previous                               Next    Last
```

### Bước 5: Xem tất cả 1000 keys
**Cách 1: Tăng số keys/page**
- Click dropdown "Hiển thị: 100"
- Chọn **500 keys/trang**
- Sẽ hiển thị 500 keys, chỉ cần 2 trang để xem hết 1000 keys

**Cách 2: Dùng pagination**
- Giữ nguyên 100 keys/page
- Click nút **"Sau"** hoặc số trang để xem tiếp
- Có tổng 10 trang (1000 keys ÷ 100 = 10 pages)

### 🔍 Filter và Search
Bạn cũng có thể filter để tìm keys cụ thể:
- **Search:** Tìm theo tên hoặc API key
- **Status:** Active / Dead / Out of Credit  
- **User:** Filter theo user đã được assign

## ⚠️ Warning
Nếu bạn vẫn thấy 50 keys sau khi làm các bước trên:
1. Clear browser cache (Settings → Clear browsing data)
2. Thử browser khác (Chrome, Firefox, Edge)
3. Kiểm tra console log trong DevTools (F12)
   - Tìm log: `[ElevenLabs Page] Stats total (full): 1000`
   - Nếu không thấy số 1000 → API vẫn bị cache

## 📊 Verify Stats
Để verify database thực sự có 1000 keys, chạy:
```bash
cd admin-panel

# Tạo script test
node -e "
const sql = require('mssql');
require('dotenv').config();
(async () => {
  const pool = await sql.connect({
    user: process.env.DB_USER || 'sa',
    password: process.env.DB_PASSWORD,
    server: process.env.DB_SERVER || 'localhost',
    port: parseInt(process.env.DB_PORT || '1433'),
    database: process.env.DB_NAME || 'WorkFlowAdmin',
    options: { encrypt: false, trustServerCertificate: true }
  });
  const result = await pool.request().query('SELECT COUNT(*) as total FROM elevenlabs_keys');
  console.log('Total Keys:', result.recordset[0].total);
  await pool.close();
})();
"
```

Kết quả nên là: `Total Keys: 1000`

## 🎯 Tóm tắt
- ✅ Code đã được fix để không cache
- ✅ Pagination đã hoạt động tốt  
- ✅ Stats hiển thị chính xác từ database
- ✅ Có nút Refresh để reload data
- 🔄 **CHỈ CẦN:** Restart server + Hard refresh browser!
























