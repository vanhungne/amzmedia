# Test Key Format - Verify dấu 3 chấm không ảnh hưởng

## 🔍 Kiểm tra key format

### Test endpoint `/api/test-gemini-db`:
- ✅ Dùng `api_key_preview` → có dấu `...` (để bảo mật)
- ✅ Format: `LEFT(12) + '...' + RIGHT(8)`

### Test endpoint `/api/tool/gemini`:
- ✅ Trả về `api_key` FULL (không có `...`)
- ✅ Client nhận key đầy đủ 39 ký tự

---

## 🧪 Cách test trực tiếp:

### Bước 1: Lấy token

Mở browser → Console (F12):
```javascript
// Đăng nhập vào https://amz.io.vn trước
localStorage.getItem('token')
```

Copy token.

### Bước 2: Test API

**Linux/Mac:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://amz.io.vn/api/tool/gemini
```

**Windows PowerShell:**
```powershell
curl -H "Authorization: Bearer YOUR_TOKEN" `
     https://amz.io.vn/api/tool/gemini
```

**Hoặc dùng browser với Extension như ModHeader:**
1. Install ModHeader extension
2. Add header: `Authorization: Bearer YOUR_TOKEN`
3. Visit: `https://amz.io.vn/api/tool/gemini`

### Kết quả mong đợi:

```json
{
  "success": true,
  "keys": [
    {
      "id": 1,
      "api_key": "AIzaSyDoCllssgPY3ucNV6mTemLRWJg9jcNNIKI",
      "name": null,
      "status": "active"
    },
    {
      "id": 2,
      "api_key": "AIzaSyBtcUzmE9Vr...FULL_KEY_HERE...EWw5uZUE",
      "name": null,
      "status": "active"
    }
  ]
}
```

**CHÚ Ý:** `api_key` sẽ là FULL 39 ký tự, KHÔNG có dấu `...`

---

## ✅ Verify trong Code

### File: admin-panel/app/api/test-gemini-db/route.ts
```typescript
// Line 31-35 - CHỈ dùng cho TEST endpoint
SELECT 
  [id],
  LEFT([api_key], 12) + '...' + RIGHT([api_key], 8) as api_key_preview,
  //                      ^^^
  //                  Preview only!
```

### File: admin-panel/app/api/tool/gemini/route.ts
```typescript
// Line 15-19 - API THẬT cho client
SELECT 
  [id],
  [api_key],  // ← FULL KEY, không preview
  [name],
  [status]
```

---

## 🎯 Kết luận:

| Endpoint | Field | Format | Có dấu `...`? |
|----------|-------|--------|---------------|
| `/api/test-gemini-db` | `api_key_preview` | `AIza...NNIKI` | ✅ Có (bảo mật) |
| `/api/tool/gemini` | `api_key` | Full 39 chars | ❌ KHÔNG |
| Database | `[api_key]` | Full 39 chars | ❌ KHÔNG |

**→ Client nhận key FULL, không có dấu 3 chấm!**

---

## 📝 Nếu muốn xem key FULL trong test endpoint:

Sửa file `admin-panel/app/api/test-gemini-db/route.ts`:

```typescript
// Change this:
LEFT([api_key], 12) + '...' + RIGHT([api_key], 8) as api_key_preview,

// To this:
[api_key] as api_key_full,
```

**NHƯNG KHÔNG NÊN** - vì test endpoint có thể bị xem public, dễ lộ key!

---

## ✅ Tóm lại:

1. **Test endpoint** (`/api/test-gemini-db`):
   - Dùng preview `AIza...NNIKI` (bảo mật)
   - KHÔNG ảnh hưởng key thật

2. **Client API** (`/api/tool/gemini`):
   - Trả về key FULL 39 chars
   - KHÔNG có dấu 3 chấm

3. **Database**:
   - Lưu key FULL
   - KHÔNG có dấu 3 chấm

**→ Hoàn toàn an toàn! Dấu 3 chấm chỉ là hiển thị, không phải data thật.**



