# 🚀 Deploy Fix lên amz.io.vn

## ✅ Đã kiểm tra - Database hoàn toàn ổn!

Kết quả test từ `https://amz.io.vn/api/test-gemini-db`:
- ✅ Table `gemini_keys` tồn tại
- ✅ 3 keys với status='active'
- ✅ Keys có length=39 (đúng format)

**→ Vấn đề: CODE trên server chưa được update!**

---

## 🔧 Các file cần deploy lên server:

### Files đã sửa:
1. ✅ `admin-panel/app/api/tool/gemini/route.ts` - Fixed SQL syntax
2. ✅ `admin-panel/app/api/gemini/route.ts` - Clean keys khi save
3. ✅ `image_tab_full.py` - Load keys từ server
4. ✅ `GenVideoPro.py` - Auto-load keys

### Files mới tạo:
5. ✅ `admin-panel/app/api/test-gemini-db/route.ts` - Test endpoint
6. 📄 `admin-panel/scripts/clean_gemini_keys.sql` - Clean script (optional)
7. 📄 Documentation files (optional)

---

## 📦 Cách 1: Deploy qua Git (Recommended)

### Từ máy local:

```bash
# 1. Commit tất cả changes
git add .
git commit -m "Fix Gemini API keys: clean whitespace, fix SQL syntax, add server integration"

# 2. Push lên repository
git push origin main
# hoặc
git push origin master
```

### Trên server amz.io.vn:

```bash
# 1. SSH vào server
ssh user@amz.io.vn
# (nhập password/key)

# 2. Di chuyển vào thư mục project
cd /var/www/admin-panel
# hoặc đường dẫn thật của project

# 3. Pull code mới nhất
git pull origin main

# 4. Install dependencies (nếu có thay đổi package.json)
npm install

# 5. Build production
npm run build

# 6. Restart server
pm2 restart admin-panel
# hoặc
pm2 restart all
# hoặc
systemctl restart admin-panel
```

### Verify:
```bash
# Check logs
pm2 logs admin-panel --lines 50

# Test endpoint
curl http://localhost:3000/api/test-gemini-db
```

---

## 📦 Cách 2: CI/CD tự động (nếu có)

Nếu server có setup auto-deploy (GitHub Actions, GitLab CI, etc.):

```bash
# Chỉ cần push
git push origin main

# Server sẽ tự động:
# 1. Detect changes
# 2. Pull code
# 3. Build
# 4. Restart
```

**Monitor deploy:**
- Check GitHub Actions tab
- Hoặc xem logs deploy tool của bạn
- Đợi status = "Success" ✅

---

## 📦 Cách 3: Upload Manual (nếu không dùng Git)

### Upload qua FTP/SFTP:

Dùng FileZilla hoặc WinSCP:

**Upload các files đã sửa:**
1. `/app/api/tool/gemini/route.ts`
2. `/app/api/gemini/route.ts`
3. `/app/api/test-gemini-db/route.ts` (new file)

**Đường dẫn trên server:**
```
/var/www/admin-panel/app/api/...
```

### Sau khi upload:

```bash
# SSH vào server
ssh user@amz.io.vn

# Build lại
cd /var/www/admin-panel
npm run build

# Restart
pm2 restart admin-panel
```

---

## 🧪 Test sau khi Deploy

### Test 1: Health check
```bash
curl https://amz.io.vn/api/health
```

### Test 2: Database test (đã OK)
```bash
curl https://amz.io.vn/api/test-gemini-db
```

### Test 3: Gemini keys endpoint (CẦN TOKEN)

#### Lấy token:
1. Mở browser → `https://amz.io.vn`
2. Đăng nhập Admin Panel
3. F12 → Console tab
4. Chạy: `localStorage.getItem('token')`
5. Copy token

#### Test:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     https://amz.io.vn/api/tool/gemini
```

**Mong đợi:**
```json
{
  "success": true,
  "keys": [
    {
      "id": 1,
      "api_key": "AIzaSyDoClls...",
      "status": "active"
    },
    ...
  ]
}
```

### Test 4: Load từ WorkFlow Tool

1. Mở WorkFlow Tool
2. Đăng nhập (server: `https://amz.io.vn`)
3. Vào Image Generator tab
4. Click "🔑 Load Keys"

**Console logs mong đợi:**
```
☁️ Loading Gemini API keys from server...
🔑 Loaded key 1: AIzaSyDo...NNIKI (length: 39)
🔑 Loaded key 2: AIzaSyBt...uZUE (length: 39)
🔑 Loaded key 3: AIzaSyBM...LWXM (length: 39)
✅ Loaded 3 Gemini API keys from server successfully
📝 Keys are ready for use. First key starts with: AIzaSyDoClls...
```

### Test 5: Generate Image
1. Thêm prompt: "A beautiful sunset"
2. Click ▶️ Run Selected
3. Should generate successfully! ✅

---

## 🔍 Troubleshooting

### Nếu vẫn lỗi sau deploy:

#### Check 1: Code đã update chưa?
```bash
# SSH vào server
cd /var/www/admin-panel

# Check file đã update
cat app/api/tool/gemini/route.ts | grep "CASE WHEN"
# Phải thấy: CASE WHEN [last_used] IS NULL...
# Không còn: NULLS FIRST
```

#### Check 2: Server đã restart chưa?
```bash
pm2 list
# Check uptime - phải là mới (vài phút)

# Nếu uptime lâu → restart lại
pm2 restart admin-panel
```

#### Check 3: Build có thành công không?
```bash
cd /var/www/admin-panel
npm run build

# Xem có error không
```

#### Check 4: Port và process
```bash
# Check process
ps aux | grep node

# Check port
netstat -tlnp | grep :3000
```

---

## 📋 Checklist Deploy:

- [ ] Code đã commit & push
- [ ] SSH vào server thành công
- [ ] `git pull` thành công
- [ ] `npm run build` thành công (no errors)
- [ ] Server đã restart
- [ ] Test endpoint `/api/test-gemini-db` → Success ✅
- [ ] Test endpoint `/api/tool/gemini` → Success (với token)
- [ ] WorkFlow Tool load keys thành công
- [ ] Generate image thành công

---

## 🆘 Cần thêm hỗ trợ?

Gửi cho tôi:

1. **Cách deploy bạn đang dùng:**
   - [ ] Git pull
   - [ ] CI/CD
   - [ ] Manual upload
   - [ ] Khác: ___

2. **Có quyền SSH không:**
   - [ ] Có
   - [ ] Không

3. **Server logs** (sau khi restart):
```bash
pm2 logs admin-panel --lines 100
```

4. **Build output:**
```bash
npm run build
# Copy output
```

---

## ✅ Kết quả mong đợi:

**TRƯỚC (hiện tại):**
```
❌ Failed to get Gemini keys: Internal server error
```

**SAU (sau deploy):**
```
✅ Loaded 3 Gemini API keys from server!
✅ Generate image successfully!
```

---

**Server:** https://amz.io.vn  
**Database:** ✅ OK (3 active keys)  
**Cần làm:** Deploy code fix lên server

Good luck! 🚀



