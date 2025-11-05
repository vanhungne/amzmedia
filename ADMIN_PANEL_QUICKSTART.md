# 🚀 Admin Panel Quick Start (5 phút)

## Bước 1: Cài Đặt (1 phút)

```bash
cd admin-panel
npm install
```

## Bước 2: Cấu Hình Database (30 giây)

Tạo file `.env`:

```env
DB_USER=sa
DB_PASSWORD=YourPassword123
DB_SERVER=localhost
DB_NAME=WorkFlowAdmin
DB_ENCRYPT=false
DB_TRUST_CERT=true
JWT_SECRET=change-this-secret-key
```

## Bước 3: Chạy Admin Panel (10 giây)

```bash
npm run dev
```

Mở: **http://localhost:3000**

## Bước 4: Đăng Nhập (10 giây)

- Username: `admin`
- Password: `admin123`

## Bước 5: Tạo Project Đầu Tiên (1 phút)

1. Vào tab **Projects**
2. Click **➕ Tạo Project Mới**
3. Điền:
   - Channel Name: "My Channel"
   - Script Template: (paste Groq prompt)
   - Num Prompts: 12
   - Voice ID: "uju3wxzG5OhpWcoi3SMy"
4. Click **Tạo Project**

## Bước 6: Tạo User (30 giây)

1. Vào tab **Users**
2. Click **➕ Tạo User Mới**
3. Điền:
   - Username: "user1"
   - Password: "password123"
   - Role: User
4. Click **Tạo User**

## Bước 7: Kết Nối Từ Python Tool (1 phút)

1. Mở **GenVideoPro.py**
2. Vào tab **📁 Projects**
3. Click **🔐 Connect to Admin Panel**
4. Nhập: admin / admin123
5. Click **☁️ Load Projects from Server**
6. Chọn project "My Channel"
7. Click **📜 Import Script**
8. Chọn file script.txt
9. **Done!** Workflow tự động chạy! 🎉

---

## 📊 Kết Quả

✅ Admin panel running
✅ Database initialized
✅ Projects created
✅ Users created
✅ Python tool connected
✅ Auto workflow ready!

**Total time: ~5 phút** ⏱️

---

## 🔧 Troubleshooting Nhanh

### Cannot connect to database
```bash
# Check SQL Server running
# For Docker:
docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=YourPassword123" \
   -p 1433:1433 --name sqlserver \
   -d mcr.microsoft.com/mssql/server:2022-latest
```

### Port 3000 already in use
```bash
# Change port in package.json
"dev": "next dev -p 3001"
```

### Python tool cannot connect
- Ensure admin panel is running (`npm run dev`)
- Check URL: `http://localhost:3000`
- Re-authenticate in tool

---

## 📖 Chi Tiết Đầy Đủ

Xem file `ADMIN_PANEL_GUIDE.md` để biết thêm chi tiết!






