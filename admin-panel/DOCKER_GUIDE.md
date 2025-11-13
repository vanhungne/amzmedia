# 🐳 Docker Setup Guide cho Admin Panel

Hướng dẫn build và chạy Admin Panel bằng Docker.

## 📋 Yêu Cầu

- Docker Desktop (Windows/Mac) hoặc Docker Engine (Linux)
- Docker Compose (thường đi kèm với Docker Desktop)

## 🚀 Cách Sử Dụng

### 1. Build và Chạy với Docker Compose (Khuyến nghị)

```bash
cd admin-panel
docker-compose up -d
```

Lệnh này sẽ:
- Build image cho admin panel
- Tạo và chạy SQL Server container
- Tạo và chạy admin panel container
- Tự động kết nối giữa các services

### 2. Xem Logs

```bash
# Xem logs của tất cả services
docker-compose logs -f

# Xem logs của admin panel
docker-compose logs -f admin-panel

# Xem logs của database
docker-compose logs -f sqlserver
```

### 3. Dừng Services

```bash
docker-compose down
```

### 4. Dừng và Xóa Volumes (Xóa dữ liệu database)

```bash
docker-compose down -v
```

### 5. Rebuild sau khi thay đổi code

```bash
docker-compose up -d --build
```

## 🔧 Cấu Hình

### Thay Đổi Environment Variables

Chỉnh sửa file `docker-compose.yml`:

```yaml
admin-panel:
  environment:
    - DB_PASSWORD=YourNewPassword123!
    - JWT_SECRET=your-new-secret-key
    - DB_NAME=YourDatabaseName
```

Sau đó rebuild:

```bash
docker-compose up -d --build
```

### Thay Đổi Port

Nếu port 3000 đã được sử dụng, thay đổi trong `docker-compose.yml`:

```yaml
admin-panel:
  ports:
    - "8080:3000"  # Sử dụng port 8080 thay vì 3000
```

## 📦 Build Image Riêng Lẻ

Nếu chỉ muốn build Docker image:

```bash
cd admin-panel
docker build -t admin-panel:latest .
```

Chạy container:

```bash
docker run -d \
  -p 3000:3000 \
  -e DB_USER=sa \
  -e DB_PASSWORD=YourPassword123! \
  -e DB_SERVER=sqlserver \
  -e DB_NAME=WorkFlowAdmin \
  -e DB_ENCRYPT=false \
  -e DB_TRUST_CERT=true \
  -e JWT_SECRET=your-secret-key \
  --name admin-panel \
  admin-panel:latest
```

## 🌐 Truy Cập

Sau khi chạy thành công:

- **Admin Panel**: http://localhost:3000
- **Default Login**:
  - Username: `admin`
  - Password: `admin123`

⚠️ **Quan trọng**: Đổi mật khẩu ngay sau lần đăng nhập đầu tiên!

## 🔍 Troubleshooting

### Container không start được

```bash
# Kiểm tra logs
docker-compose logs admin-panel

# Kiểm tra status
docker-compose ps
```

### Database connection error

Đảm bảo SQL Server container đã sẵn sàng:

```bash
# Kiểm tra health status
docker-compose ps

# Kiểm tra database logs
docker-compose logs sqlserver
```

### Port đã được sử dụng

```bash
# Kiểm tra port nào đang sử dụng
netstat -ano | findstr :3000  # Windows
lsof -i :3000                  # Mac/Linux

# Thay đổi port trong docker-compose.yml
```

### Rebuild từ đầu

```bash
# Dừng và xóa tất cả
docker-compose down -v

# Xóa images
docker rmi admin-panel_admin-panel

# Build lại
docker-compose up -d --build
```

## 📝 Lưu Ý

1. **Mật khẩu Database**: Đổi `YourPassword123!` trong production
2. **JWT Secret**: Đổi `JWT_SECRET` trong production
3. **Data Persistence**: Database data được lưu trong Docker volume `sqlserver_data`
4. **Network**: Các containers giao tiếp qua network `admin-panel-network`

## 🎯 Production Deployment

Để deploy lên production server:

1. Thay đổi tất cả passwords và secrets
2. Sử dụng environment variables từ file `.env` hoặc secrets manager
3. Cấu hình reverse proxy (nginx) nếu cần
4. Setup SSL/TLS certificates
5. Cấu hình backup cho database volume

