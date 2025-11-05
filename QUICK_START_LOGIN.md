# 🚀 Quick Start - Hệ Thống Đăng Nhập

## Bắt Đầu Nhanh (5 phút)

### Bước 1: Khởi động Admin Panel
```bash
cd admin-panel
npm run dev
```
✅ Admin Panel chạy tại: http://localhost:3000

### Bước 2: Chạy WorkFlow Tool
```bash
python GenVideoPro.py
```

### Bước 3: Đăng nhập
**Thông tin đăng nhập mặc định:**
- Server: `http://localhost:3000`
- Username: `admin`
- Password: `admin123`

✅ Đăng nhập thành công → Tool mở ra!

---

## Phân Quyền

### 👑 Admin
- ✅ Tạo/Sửa/Xóa projects
- ✅ Load projects
- ✅ Import script

### 👤 User
- ❌ KHÔNG được tạo/sửa/xóa projects
- ✅ Chỉ load và sử dụng projects có sẵn
- ✅ Import script

---

## Tạo Tài Khoản User Mới

1. Truy cập Admin Panel: http://localhost:3000/dashboard/users
2. Click "Add User"
3. Nhập:
   - Username: `user1`
   - Password: `user123`
   - Role: `user`
4. Save

---

## Test Hệ Thống

### Kiểm tra tất cả:
```bash
python verify_login_system.py
```

### Test login riêng:
```bash
python test_login.py
```

---

## Xử Lý Lỗi Nhanh

### "Cannot connect to admin panel"
```bash
cd admin-panel
npm run dev
```

### "Authentication failed"
- Kiểm tra username/password
- Tạo user trong Admin Panel

### "Login dialog not showing"
- Kiểm tra PySide6: `pip install PySide6`
- Kiểm tra requests: `pip install requests`

---

## Files Quan Trọng

| File | Mô tả |
|------|-------|
| `login_dialog.py` | UI đăng nhập |
| `GenVideoPro.py` | Main application (đã tích hợp login) |
| `tool_api_client.py` | API client |
| `LOGIN_GUIDE.md` | Hướng dẫn đầy đủ |
| `verify_login_system.py` | Script kiểm tra |

---

## Tính Năng Mới

✅ **Đăng nhập bắt buộc** - Không đăng nhập = không dùng được tool
✅ **Phân quyền rõ ràng** - Admin vs User
✅ **Ghi nhớ đăng nhập** - Không cần nhập lại
✅ **Logout an toàn** - Xóa credentials khi thoát
✅ **UI đẹp** - Material design inspired

---

## Support

📖 Đọc thêm: `LOGIN_GUIDE.md`
🔍 Kiểm tra: `python verify_login_system.py`
🧪 Test: `python test_login.py`

---

**Version 2.0 - Login System**
**Status: ✅ READY TO USE**

