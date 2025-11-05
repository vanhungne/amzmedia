# 🔐 Hướng Dẫn Hệ Thống Đăng Nhập WorkFlow Tool

## Tổng Quan

WorkFlow Tool giờ đây yêu cầu đăng nhập bằng username và password trước khi sử dụng. Hệ thống có phân quyền **Admin** và **User** với các quyền hạn khác nhau.

## Phân Quyền

### 👑 Admin
- **Quyền đầy đủ:**
  - ➕ Tạo project mới
  - ✏️ Chỉnh sửa project
  - 🗑️ Xóa project
  - 📜 Import script và tự động tạo workflow
  - 📊 Xem và load tất cả projects

### 👤 User (Thường)
- **Quyền giới hạn:**
  - 📊 Xem danh sách projects
  - 📂 Load project để sử dụng
  - 📜 Import script và tự động tạo workflow
  - ❌ **KHÔNG** được tạo/sửa/xóa project

## Cách Sử Dụng

### 1. Khởi Động Admin Panel

Trước khi chạy tool, bạn cần khởi động Admin Panel:

```bash
cd admin-panel
npm run dev
```

Admin Panel sẽ chạy tại: `http://localhost:3000`

### 2. Chạy WorkFlow Tool

```bash
python GenVideoPro.py
```

### 3. Đăng Nhập

Khi tool khởi động, màn hình đăng nhập sẽ hiện ra:

![Login Dialog](https://via.placeholder.com/400x300?text=Login+Dialog)

**Thông tin đăng nhập mặc định:**
- **Server:** `http://localhost:3000`
- **Admin Account:**
  - Username: `admin`
  - Password: `admin123`
- **User Account (nếu đã tạo):**
  - Username: `user1`
  - Password: `user123`

**Tính năng:**
- ✅ Ghi nhớ đăng nhập (checkbox "Ghi nhớ đăng nhập")
- 🔄 Tự động điền thông tin đã lưu
- 🔒 Bảo mật password (hiển thị dấu *)

### 4. Sử Dụng Tool

Sau khi đăng nhập thành công:

#### Với Admin:
- Tất cả các nút đều hiển thị
- Có thể quản lý projects đầy đủ
- Hiển thị: **👑 Admin: [username]**

#### Với User:
- Chỉ hiển thị nút "📜 Import Script" và "🔄 Refresh"
- Nút "➕ New Project", "✏️ Edit Project", "🗑️ Delete Project" bị ẩn
- Hiển thị: **👤 User: [username]**

### 5. Đăng Xuất

Nhấn nút **🚪 Logout** ở góc trên bên phải để đăng xuất. Tool sẽ đóng và yêu cầu đăng nhập lại khi khởi động.

## Quản Lý Tài Khoản

### Tạo Tài Khoản Mới (Admin Panel)

1. Truy cập: `http://localhost:3000/dashboard/users`
2. Nhấn "Add User"
3. Điền thông tin:
   - Username
   - Password
   - Role: `admin` hoặc `user`
4. Lưu

### Thay Đổi Mật Khẩu

1. Truy cập Admin Panel
2. Vào Users → Chọn user cần đổi
3. Nhập password mới
4. Lưu

## Kiểm Tra Hệ Thống

### Test Login Dialog

Chạy script test độc lập:

```bash
python test_login.py
```

Script này sẽ:
- ✅ Test kết nối đến Admin Panel
- ✅ Test đăng nhập với credentials
- ✅ Test fetch projects
- ✅ Hiển thị thông tin user và role

### Kiểm Tra Phân Quyền

1. **Test Admin:**
   - Đăng nhập với `admin/admin123`
   - Kiểm tra tất cả nút có hiển thị
   - Thử tạo/sửa/xóa project

2. **Test User:**
   - Đăng nhập với tài khoản user
   - Kiểm tra chỉ có nút Load và Import Script
   - Thử load project và import script

## Xử Lý Lỗi

### Lỗi: "Failed to connect to admin panel"

**Nguyên nhân:**
- Admin Panel chưa chạy
- Sai địa chỉ server

**Giải pháp:**
```bash
cd admin-panel
npm run dev
```

### Lỗi: "Authentication failed"

**Nguyên nhân:**
- Sai username hoặc password
- Tài khoản không tồn tại

**Giải pháp:**
- Kiểm tra lại credentials
- Tạo tài khoản mới trong Admin Panel

### Lỗi: "API Client not available"

**Nguyên nhân:**
- Module `tool_api_client.py` không tìm thấy
- Lỗi import

**Giải pháp:**
- Kiểm tra file `tool_api_client.py` tồn tại
- Cài đặt dependencies: `pip install requests`

## Bảo Mật

### Lưu Ý Quan Trọng

⚠️ **Credentials được lưu trong file `.workflow_creds`**
- File này chứa username và password (chưa mã hóa)
- Nên thêm vào `.gitignore`
- Trong production, nên mã hóa password

### Khuyến Nghị

1. **Đổi password mặc định** của admin
2. **Không share credentials** với người khác
3. **Đăng xuất** khi không sử dụng
4. **Backup database** định kỳ

## API Endpoints

Tool sử dụng các API endpoints sau:

### Authentication
- `POST /api/tool/auth` - Đăng nhập
  ```json
  {
    "username": "admin",
    "password": "admin123"
  }
  ```

### Projects
- `GET /api/tool/projects` - Lấy danh sách projects
  - Headers: `Authorization: Bearer <token>`

### ElevenLabs Keys
- `GET /api/tool/elevenlabs` - Lấy API keys
- `POST /api/tool/elevenlabs` - Report key status

## Troubleshooting

### Debug Mode

Bật debug để xem chi tiết:

```python
# Trong GenVideoPro.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Files

Check console output để xem:
- ✅ Login status
- 📊 User info
- 🔑 Token (partial)
- ⚠️ Errors

## Cập Nhật

### Version 2.0 - Login System
- ✅ Login dialog với username/password
- ✅ Phân quyền Admin/User
- ✅ Ẩn/hiện nút theo role
- ✅ Logout functionality
- ✅ Remember me feature
- ✅ User info display

## Support

Nếu gặp vấn đề:
1. Kiểm tra Admin Panel đang chạy
2. Xem console log
3. Chạy `test_login.py` để debug
4. Kiểm tra database có tài khoản

---

**Made with ❤️ for WorkFlow Team**

