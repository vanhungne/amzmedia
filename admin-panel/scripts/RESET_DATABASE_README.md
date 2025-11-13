# 🔄 Reset Database - Hướng Dẫn

## ⚠️ Lưu Ý Quan Trọng

Script này sẽ **XÓA TẤT CẢ DỮ LIỆU** trong database, chỉ giữ lại **1 admin user**.

## 🚀 Cách Chạy

### 1. Đảm bảo SQL Server đang chạy

**Windows:**
```powershell
# Kiểm tra SQL Server service
Get-Service | Where-Object {$_.Name -like "*SQL*"}

# Nếu chưa chạy, start service:
# Services → SQL Server (MSSQLSERVER) → Start
```

### 2. Kiểm tra Connection String

Đảm bảo file `.env` (hoặc `.env.local`) có đúng config:

```env
DB_SERVER=localhost
DB_PORT=1433
DB_USER=sa
DB_PASSWORD=your_password
DB_NAME=WorkFlowAdmin
DB_TRUST_CERT=true
```

### 3. Chạy Script

```bash
cd admin-panel
npx tsx scripts/reset-database.ts
```

## 📋 Script Sẽ Làm Gì

1. ✅ Xóa tất cả **activity_logs**
2. ✅ Xóa tất cả **sessions**
3. ✅ Xóa tất cả **elevenlabs_keys**
4. ✅ Xóa tất cả **proxy_keys**
5. ✅ Xóa tất cả **gemini_keys**
6. ✅ Xóa tất cả **projects**
7. ✅ Xóa tất cả **users** TRỪ admin
8. ✅ Reset counters của admin về 0
9. ✅ Reset IDENTITY columns về đầu

## 👤 Admin User

### Nếu KHÔNG có admin user:
- Script sẽ tự động tạo admin mới
- **Username:** `admin`
- **Password:** `admin123`

### Nếu ĐÃ có admin user:
- Script sẽ giữ lại admin user đầu tiên (theo ID)
- Xóa tất cả users khác
- Reset counters về 0
- **Password giữ nguyên** (không đổi)

## ⚠️ Cảnh Báo

- **KHÔNG THỂ HOÀN TÁC** - Dữ liệu sẽ bị xóa vĩnh viễn
- Backup database trước khi chạy nếu cần
- Đảm bảo bạn đang ở môi trường đúng (dev/test)

## 🐛 Troubleshooting

### Lỗi: "Failed to connect to localhost:1433"

**Giải pháp:**
1. Kiểm tra SQL Server đang chạy
2. Kiểm tra port 1433 có mở không
3. Kiểm tra firewall
4. Kiểm tra connection string trong `.env`

### Lỗi: "Login failed for user"

**Giải pháp:**
1. Kiểm tra username/password trong `.env`
2. Đảm bảo SQL Server cho phép SQL Authentication
3. Thử đăng nhập bằng SQL Server Management Studio

### Lỗi: "Cannot find database"

**Giải pháp:**
1. Tạo database `WorkFlowAdmin` trước
2. Hoặc chạy migration: `npm run migrate`

## ✅ Sau Khi Reset

1. Database sẽ clean như mới
2. Chỉ có 1 admin user
3. Tất cả counters = 0
4. Sẵn sàng để test lại từ đầu

## 🎯 Test Sau Khi Reset

1. Login với admin: `admin` / `admin123`
2. Tạo users mới
3. Import keys
4. Test bulk assign với progress tracking
5. Test các features khác

---

**💡 Tip:** Nếu muốn test nhiều lần, có thể tạo alias trong PowerShell:

```powershell
# Thêm vào PowerShell profile
function Reset-DB {
    cd admin-panel
    npx tsx scripts/reset-database.ts
}
```

Sau đó chỉ cần gõ: `Reset-DB`
































