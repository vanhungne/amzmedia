# 🔄 Cách Chạy Reset Database

## ⚠️ SQL Server không kết nối được?

Có 2 cách để reset database:

---

## 🎯 Cách 1: Chạy SQL Script Trực Tiếp (KHUYẾN NGHỊ)

### Bước 1: Mở SQL Server Management Studio (SSMS)

### Bước 2: Kết nối đến SQL Server

### Bước 3: Chọn database `WorkFlowAdmin`

### Bước 4: Mở file `scripts/reset-database.sql`

### Bước 5: Chạy script (F5 hoặc Execute)

**Script sẽ:**
- ✅ Xóa tất cả dữ liệu
- ✅ Giữ lại 1 admin user
- ✅ Reset counters về 0

---

## 🎯 Cách 2: Chạy Script TypeScript (Nếu SQL Server đang chạy)

### Bước 1: Đảm bảo SQL Server đang chạy

```powershell
# Kiểm tra service
Get-Service | Where-Object {$_.Name -like "*SQL*"}

# Start nếu chưa chạy
Start-Service MSSQLSERVER
```

### Bước 2: Kiểm tra config `.env`

```env
DB_SERVER=localhost
DB_PORT=1433
DB_USER=sa
DB_PASSWORD=your_password
DB_NAME=WorkFlowAdmin
DB_TRUST_CERT=true
```

### Bước 3: Chạy script

```powershell
cd admin-panel
npx tsx scripts/reset-database.ts
```

---

## ⚠️ Lưu Ý

1. **Không thể hoàn tác** - Dữ liệu sẽ bị xóa vĩnh viễn
2. **Backup trước** nếu cần
3. **Admin password** - Nếu tạo admin mới, cần reset password bằng app hoặc dùng reset password script

---

## ✅ Sau Khi Reset

1. Database clean như mới
2. Chỉ có 1 admin user
3. Tất cả counters = 0
4. Sẵn sàng test lại từ đầu

**Khuyến nghị:** Dùng **Cách 1** (SQL Script) vì đơn giản và không cần config `.env`

























