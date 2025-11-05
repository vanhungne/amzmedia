# 🌐 Hướng Dẫn Thay Đổi Server URL

## Cách Đổi Server

### Bước 1: Mở File
Mở file `login_dialog.py`

### Bước 2: Tìm Phần Configuration
Tìm đến dòng 19-23:

```python
# ============================================================
# SERVER CONFIGURATION - Thay đổi URL server tại đây
# ============================================================
DEFAULT_SERVER_URL = "http://localhost:3000"
# Để đổi server, sửa URL ở trên, ví dụ:
# DEFAULT_SERVER_URL = "http://192.168.1.100:3000"
# DEFAULT_SERVER_URL = "https://api.workflow.com"
# ============================================================
```

### Bước 3: Sửa URL
Thay đổi giá trị của `DEFAULT_SERVER_URL`

## Ví Dụ

### 1. Server Local (Mặc định)
```python
DEFAULT_SERVER_URL = "http://localhost:3000"
```

### 2. Server Mạng LAN
```python
DEFAULT_SERVER_URL = "http://192.168.1.100:3000"
```

### 3. Server Online
```python
DEFAULT_SERVER_URL = "https://api.workflow.com"
```

### 4. Server Với Port Khác
```python
DEFAULT_SERVER_URL = "http://localhost:5000"
```

## Lưu Ý

### ✅ Đúng:
```python
DEFAULT_SERVER_URL = "http://localhost:3000"
DEFAULT_SERVER_URL = "https://api.example.com"
DEFAULT_SERVER_URL = "http://192.168.1.50:8080"
```

### ❌ Sai:
```python
DEFAULT_SERVER_URL = "localhost:3000"  # Thiếu http://
DEFAULT_SERVER_URL = "http://localhost:3000/"  # Không cần / cuối
DEFAULT_SERVER_URL = ""  # Không được để trống
```

## Sau Khi Đổi

1. **Lưu file** `login_dialog.py`
2. **Khởi động lại** ứng dụng
3. **Đăng nhập** với server mới

## Kiểm Tra Server

### Test Server Có Hoạt Động:
```bash
# Windows
curl http://localhost:3000

# Hoặc mở browser
http://localhost:3000
```

### Nếu Server Không Kết Nối:
1. ✅ Kiểm tra Admin Panel đang chạy
2. ✅ Kiểm tra URL đúng
3. ✅ Kiểm tra firewall
4. ✅ Kiểm tra port có bị chiếm

## Troubleshooting

### Lỗi: "Cannot connect to admin panel"
**Nguyên nhân:**
- Server chưa chạy
- URL sai
- Port bị block

**Giải pháp:**
```bash
# Kiểm tra server đang chạy
cd admin-panel
npm run dev

# Kiểm tra port
netstat -ano | findstr :3000
```

### Lỗi: "Authentication failed"
**Nguyên nhân:**
- Server đúng nhưng credentials sai
- Database chưa có user

**Giải pháp:**
- Kiểm tra username/password
- Tạo user trong Admin Panel

## Advanced: Đổi Server Động

Nếu muốn cho phép user nhập server (không khuyến nghị):

### Cách 1: Truyền Parameter
```python
# Trong GenVideoPro.py
login_dialog = LoginDialog(server_url="http://custom-server.com:3000")
```

### Cách 2: Environment Variable
```python
# Trong login_dialog.py
import os
DEFAULT_SERVER_URL = os.getenv("WORKFLOW_SERVER_URL", "http://localhost:3000")
```

Sau đó set biến môi trường:
```bash
# Windows
set WORKFLOW_SERVER_URL=http://192.168.1.100:3000
python GenVideoPro.py
```

## Deployment

### Production Server:
```python
DEFAULT_SERVER_URL = "https://workflow-api.yourcompany.com"
```

### Staging Server:
```python
DEFAULT_SERVER_URL = "https://staging-api.yourcompany.com"
```

### Development Server:
```python
DEFAULT_SERVER_URL = "http://localhost:3000"
```

## Security Notes

⚠️ **Quan trọng:**
- Sử dụng HTTPS cho production
- Không hardcode credentials trong code
- Sử dụng environment variables cho sensitive data

## Quick Reference

| Environment | URL Example |
|-------------|-------------|
| Local Dev | `http://localhost:3000` |
| LAN | `http://192.168.1.100:3000` |
| Staging | `https://staging.api.com` |
| Production | `https://api.workflow.com` |

---

**File cần sửa:** `login_dialog.py`
**Dòng cần sửa:** Line 19
**Variable:** `DEFAULT_SERVER_URL`

---

**Updated:** 2025-11-01
**Version:** 2.1

