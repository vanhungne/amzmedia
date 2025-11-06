# 🌐 Fix Gemini API Key Error - Server Đã Deploy

## 📍 Bạn đang dùng server deploy (không phải localhost)

---

## 🔍 BƯỚC 1: Kiểm tra Database trên Server

### Thay `YOUR_DEPLOY_URL` bằng URL server của bạn:

Ví dụ:
- `https://admin.yourdomain.com`
- `http://103.x.x.x:3000`
- `https://workflow-admin.vercel.app`

### Test endpoint để check database:

Mở browser và vào:
```
https://YOUR_DEPLOY_URL/api/test-gemini-db
```

**VÍ DỤ:**
```
https://admin.yourdomain.com/api/test-gemini-db
```

---

## 📊 Kết quả có thể gặp:

### ✅ **Trường hợp 1: Database có keys**

```json
{
  "success": true,
  "tableExists": true,
  "totalKeys": 3,
  "statusCounts": [
    { "status": "active", "count": 3 }
  ]
}
```

**→ Database ổn!** 

**Vấn đề có thể là:**
- Keys có whitespace/ký tự thừa
- Cần clean keys

**Giải pháp:**
1. SSH vào server
2. Chạy clean script (xem bước 3)
3. Restart server

---

### ⚠️ **Trường hợp 2: Không có keys**

```json
{
  "success": true,
  "tableExists": true,
  "totalKeys": 0
}
```

**→ Cần thêm keys!**

**Giải pháp:**
1. Vào Admin Panel: `https://YOUR_DEPLOY_URL`
2. Đăng nhập
3. Dashboard → Gemini Keys → Add Key
4. Thêm 3 keys từ Google AI Studio

---

### ❌ **Trường hợp 3: Table không tồn tại**

```json
{
  "success": false,
  "error": "Table gemini_keys does not exist"
}
```

**→ Cần tạo table!**

**Giải pháp:** Xem BƯỚC 2 bên dưới

---

## 🔧 BƯỚC 2: SSH vào Server và Fix Database

### 2.1. SSH vào server:

```bash
ssh user@your-server-ip
# Hoặc
ssh user@your-domain.com
```

### 2.2. Di chuyển vào thư mục project:

```bash
cd /path/to/your/admin-panel
# Ví dụ: cd /var/www/admin-panel
```

### 2.3. Kiểm tra database connection:

```bash
# Xem environment variables
cat .env.production
# hoặc
cat .env.local
```

Đảm bảo có:
```
DATABASE_URL="Server=...;Database=...;User Id=...;Password=..."
```

---

## 🔧 BƯỚC 3: Chạy Database Scripts

### Nếu table chưa tồn tại - Tạo table:

**Option A: Dùng SQL Server Management Studio (SSMS)**
1. Connect tới SQL Server của production
2. Mở file: `admin-panel/scripts/init_gemini_keys_table.sql`
3. Chạy script

**Option B: Dùng sqlcmd trên server**
```bash
# Trên server
sqlcmd -S localhost -U sa -P 'YourPassword' -d WorkFlow \
  -i scripts/init_gemini_keys_table.sql
```

### Nếu keys có whitespace - Clean keys:

**Option A: Dùng SSMS**
1. Connect tới SQL Server
2. Mở file: `admin-panel/scripts/clean_gemini_keys.sql`
3. Chạy script

**Option B: Dùng sqlcmd**
```bash
sqlcmd -S localhost -U sa -P 'YourPassword' -d WorkFlow \
  -i scripts/clean_gemini_keys.sql
```

---

## 🔄 BƯỚC 4: Restart Server

Tùy vào cách deploy của bạn:

### Nếu dùng PM2:
```bash
pm2 restart admin-panel
# hoặc
pm2 restart all
```

### Nếu dùng systemd:
```bash
sudo systemctl restart admin-panel
```

### Nếu dùng Docker:
```bash
docker restart admin-panel
# hoặc
docker-compose restart
```

### Nếu dùng Vercel/Netlify:
- Trigger redeploy từ dashboard
- Hoặc: `git push` để trigger auto-deploy

---

## 🧪 BƯỚC 5: Test Lại

### Test 1: Verify database:
```
https://YOUR_DEPLOY_URL/api/test-gemini-db
```

Phải thấy:
```json
{
  "success": true,
  "totalKeys": 3
}
```

### Test 2: Test API endpoint:

**Cần token!** Get token bằng cách:
1. Mở Dev Tools (F12) trong browser
2. Đăng nhập Admin Panel
3. Console tab → chạy:
```javascript
localStorage.getItem('token')
```
4. Copy token

**Test với curl:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://YOUR_DEPLOY_URL/api/tool/gemini
```

Phải thấy:
```json
{
  "success": true,
  "keys": [
    {
      "id": 1,
      "api_key": "AIzaSy...",
      "status": "active"
    },
    ...
  ]
}
```

### Test 3: Load từ WorkFlow Tool:

1. Mở WorkFlow Tool
2. Đăng nhập (dùng deployed server URL)
3. Vào Image Generator tab
4. Click "🔑 Load Keys"
5. Xem console logs

**Mong đợi:**
```
☁️ Loading Gemini API keys from server...
🔑 Loaded key 1: AIzaSyDo...jcNNIKI (length: 39)
✅ Loaded 3 Gemini API keys from server successfully
```

---

## 🚨 QUAN TRỌNG: Cập nhật Code trên Server

Đảm bảo server đã có code mới nhất với các fix:

### Option A: Git pull (Recommended)

```bash
# SSH vào server
cd /path/to/admin-panel

# Pull latest code
git pull origin main

# Install dependencies (nếu có thay đổi)
npm install

# Build lại
npm run build

# Restart server
pm2 restart admin-panel
```

### Option B: Redeploy

Nếu dùng CI/CD (Vercel, Netlify, etc.):
```bash
# Từ máy local
git add .
git commit -m "Fix Gemini API key loading"
git push origin main

# Server sẽ tự động redeploy
```

---

## 📋 Checklist cho Server Deploy:

- [ ] Code mới nhất đã deploy lên server
- [ ] Environment variables (.env) đúng
- [ ] Database connection hoạt động
- [ ] Table `gemini_keys` đã tồn tại
- [ ] Table có ít nhất 1 key với status='active'
- [ ] Keys đã được clean (length=39, không có whitespace)
- [ ] Server đã restart
- [ ] Test endpoint `/api/test-gemini-db` → Success
- [ ] Test endpoint `/api/tool/gemini` → Success (với token)
- [ ] Client load keys thành công

---

## 🆘 Debugging trên Server

### Xem logs:

**Nếu dùng PM2:**
```bash
pm2 logs admin-panel
# hoặc
pm2 logs admin-panel --lines 100
```

**Nếu dùng systemd:**
```bash
sudo journalctl -u admin-panel -f
```

**Nếu dùng Docker:**
```bash
docker logs admin-panel -f
```

### Kiểm tra server có chạy không:

```bash
# Check process
ps aux | grep node

# Check port
netstat -tlnp | grep :3000

# Test local trên server
curl http://localhost:3000/api/health
```

---

## 🔐 Nếu không thể SSH vào Server

### Option 1: Dùng Admin Panel UI

1. Vào: `https://YOUR_DEPLOY_URL`
2. Đăng nhập as Admin
3. Dashboard → Gemini Keys
4. Xóa tất cả keys cũ
5. Thêm 3 keys mới từ Google AI Studio
6. Keys mới sẽ tự động clean khi lưu

### Option 2: Dùng Database Management Tool

Nếu có quyền truy cập SQL Server:
1. Connect với Azure Data Studio hoặc SSMS
2. Chạy scripts:
   - `init_gemini_keys_table.sql` (nếu chưa có table)
   - `clean_gemini_keys.sql` (nếu keys có vấn đề)

---

## 📝 Thông tin cần cung cấp (nếu vẫn lỗi):

1. **URL server deploy:** `https://...`
2. **Kết quả test endpoint:**
   ```
   https://YOUR_URL/api/test-gemini-db
   ```
3. **Deployment platform:** Vercel / VPS / Docker / PM2 / ...
4. **Server logs:** (xem phần Debugging ở trên)
5. **Có quyền SSH không:** Yes / No
6. **Database type:** SQL Server version?

---

**Cho tôi biết:**
1. URL server deploy của bạn là gì?
2. Kết quả khi test endpoint `/api/test-gemini-db`?
3. Bạn có quyền SSH vào server không?

Tôi sẽ hướng dẫn cụ thể hơn! 🚀

