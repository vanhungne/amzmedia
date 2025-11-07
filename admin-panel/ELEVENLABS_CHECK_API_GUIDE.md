# 🔍 Hướng Dẫn Check Credit API ElevenLabs

## Tổng Quan

Hệ thống Admin Panel đã được bổ sung tính năng **Check Credit và Status của API keys** trực tiếp từ server ElevenLabs. Admin có thể:

1. ✅ **Check từng key riêng lẻ** - Kiểm tra credit và trạng thái của 1 key
2. ✅ **Check tất cả keys** - Kiểm tra hàng loạt tất cả keys trong hệ thống
3. ✅ **Tự động cập nhật database** - Status và credit balance được cập nhật tự động
4. ✅ **Hiển thị chi tiết subscription** - Xem tier, limits, và các thông tin khác

---

## 📡 API Endpoints Mới

### 1. Check Credit của 1 Key

**Endpoint:** `POST /api/elevenlabs/[id]/check`

**Quyền truy cập:** Admin only

**Request:**
```http
POST /api/elevenlabs/123/check
Authorization: Cookie (session)
```

**Response (Success):**
```json
{
  "success": true,
  "status": "active",
  "credit_balance": 50000,
  "subscription_info": {
    "tier": "starter",
    "character_count": 10000,
    "character_limit": 60000,
    "can_extend_character_limit": false,
    "allowed_to_extend_character_limit": false,
    "next_character_count_reset_unix": 1730419200,
    "voice_limit": 30,
    "professional_voice_limit": 0,
    "can_use_instant_voice_cloning": true,
    "can_use_professional_voice_cloning": false
  },
  "warning": null,
  "checked_at": "2025-10-31T10:30:00.000Z"
}
```

**Response (Failed):**
```json
{
  "success": false,
  "status": "dead",
  "error": "Invalid API key",
  "checked_at": "2025-10-31T10:30:00.000Z"
}
```

---

### 2. Check Tất Cả Keys

**Endpoint:** `POST /api/elevenlabs/check-all`

**Quyền truy cập:** Admin only

**Request:**
```http
POST /api/elevenlabs/check-all
Authorization: Cookie (session)
```

**Response:**
```json
{
  "success": true,
  "summary": {
    "total": 50,
    "active": 42,
    "dead": 5,
    "out_of_credit": 3,
    "errors": 0
  },
  "results": [
    {
      "id": 1,
      "name": "Key #1",
      "success": true,
      "status": "active",
      "credit_balance": 50000,
      "tier": "starter",
      "warning": null
    },
    {
      "id": 2,
      "name": "Key #2",
      "success": false,
      "status": "dead",
      "error": "Invalid API key"
    }
  ],
  "checked_at": "2025-10-31T10:30:00.000Z"
}
```

---

## 🖥️ Sử Dụng Trên Giao Diện Admin

### 1. Check 1 Key

1. Đăng nhập vào Admin Panel
2. Vào trang **ElevenLabs API Keys**
3. Tìm key cần check trong bảng
4. Click vào icon **🔄 (Refresh)** ở cột Actions
5. Hệ thống sẽ:
   - Gọi API của ElevenLabs
   - Lấy thông tin subscription
   - Cập nhật credit balance và status
   - Hiển thị popup với thông tin chi tiết

**Kết quả hiển thị:**
```
✅ Key đang hoạt động!

Status: active
Credit Balance: 50,000
Tier: starter

⚠️ Low credits warning (nếu < 1000)
```

---

### 2. Check Tất Cả Keys (với Realtime Progress)

1. Đăng nhập vào Admin Panel
2. Vào trang **ElevenLabs API Keys**
3. Click nút **"Check All Keys"** ở góc trên bên phải
4. Xác nhận trong popup
5. **Modal Progress sẽ hiển thị realtime:**
   - ✅ **Progress Bar** - Thanh tiến trình với %
   - ✅ **Current Key** - Key đang được check hiện tại
   - ✅ **Results List** - Danh sách kết quả realtime (cuộn được)
   - ✅ **Color Coding** - Xanh (active), Đỏ (dead), Vàng (out of credit)
   - ✅ **Summary** - Tổng kết khi hoàn tất
6. Hệ thống sẽ:
   - Streaming progress từ server qua SSE (Server-Sent Events)
   - Check từng key một (delay 500ms giữa các lần)
   - Cập nhật database cho tất cả keys
   - Hiển thị từng kết quả ngay khi có

**Giao diện Progress Modal:**
```
┌────────────────────────────────────────┐
│ 🔄 Checking All API Keys         [X]  │ (Header)
├────────────────────────────────────────┤
│ Progress: 25 / 50          50%         │
│ ████████████░░░░░░░░░░░░ 50%         │ (Progress Bar)
│                                        │
│ 🔄 Đang check: Key #25                │ (Current Key)
│                                        │
│ Kết quả:                              │
│ ┌──────────────────────────────────┐  │
│ │ ✅ Key #1 - ACTIVE               │  │
│ │    • 50,000 credits • starter    │  │
│ │ ✅ Key #2 - ACTIVE               │  │
│ │ ❌ Key #3 - DEAD                 │  │
│ │    Invalid API key                │  │
│ │ ⚠️  Key #4 - OUT_OF_CREDIT       │  │
│ │    • 0 credits                    │  │
│ │ ...                               │  │
│ └──────────────────────────────────┘  │
│                                        │
│ 📊 Tổng Kết:                          │
│   Total: 50  Active: 42  Dead: 5      │
│   Out of Credit: 3  Errors: 0         │
│                                        │
│                    [Đóng]             │
└────────────────────────────────────────┘
```

---

## 🔧 Cách Hoạt Động

### Flow của Check 1 Key:

```
1. Admin click "Check" button
   ↓
2. Frontend gọi API endpoint
   ↓
3. Backend lấy API key từ database
   ↓
4. Backend gọi ElevenLabs API:
   GET https://api.elevenlabs.io/v1/user/subscription
   Header: xi-api-key: <api_key>
   ↓
5. ElevenLabs trả về subscription info
   ↓
6. Backend tính toán:
   - Available credits = character_limit - character_count
   - Status = active/out_of_credit/dead
   ↓
7. Backend cập nhật database:
   - credit_balance
   - status
   - last_used
   - last_error (nếu có)
   ↓
8. Frontend hiển thị kết quả
```

### Flow của Check All Keys (Realtime Streaming):

```
1. Admin click "Check All Keys"
   ↓
2. Frontend mở Progress Modal
   ↓
3. Frontend gọi API với streaming
   ↓
4. Backend bắt đầu stream SSE:
   
   ┌─────────────────────────────┐
   │ type: 'start'               │ → Modal shows total
   │ total: 50                   │
   └─────────────────────────────┘
   
   Loop for each key:
   ┌─────────────────────────────┐
   │ type: 'progress'            │ → Update progress bar
   │ current: 1                  │ → Show current key
   │ keyName: "Key #1"           │
   └─────────────────────────────┘
   
   ↓ Check ElevenLabs API
   
   ┌─────────────────────────────┐
   │ type: 'result'              │ → Add to results list
   │ id: 1                       │ → Realtime update!
   │ status: 'active'            │
   │ credit_balance: 50000       │
   └─────────────────────────────┘
   
   ↓ Wait 500ms (rate limit protection)
   ↓ Repeat for next key...
   
   ┌─────────────────────────────┐
   │ type: 'complete'            │ → Show summary
   │ summary: {...}              │ → Enable close button
   └─────────────────────────────┘
   
5. Frontend nhận từng message:
   - Cập nhật progress bar realtime
   - Thêm result vào list ngay lập tức
   - Auto scroll xuống result mới nhất
   - Hiển thị summary khi xong
   ↓
6. Admin xem kết quả và đóng modal
```

---

## 📊 Database Updates

Khi check key, các fields sau được cập nhật tự động:

| Field | Mô Tả | Ví Dụ |
|-------|-------|-------|
| `status` | Trạng thái key | `active`, `dead`, `out_of_credit` |
| `credit_balance` | Số credits còn lại | `50000` |
| `last_used` | Thời gian check cuối | `2025-10-31 10:30:00` |
| `last_error` | Lỗi cuối (nếu có) | `Invalid API key` |
| `updated_at` | Thời gian cập nhật | `2025-10-31 10:30:00` |

---

## 🎯 Status Mapping

| ElevenLabs Response | Status trong DB | Ý Nghĩa |
|---------------------|-----------------|---------|
| HTTP 200, credits > 0 | `active` | Key hoạt động bình thường |
| HTTP 200, credits = 0 | `out_of_credit` | Key hết credit |
| HTTP 401 | `dead` | Key không hợp lệ |
| HTTP 429 | `active` | Rate limit (key vẫn active) |
| Network error | Không đổi | Lỗi kết nối, giữ nguyên status cũ |

---

## 🚨 Warning System

Hệ thống sẽ cảnh báo khi:

- ✅ Credits < 1000: **"Low credits warning"**
- ❌ Credits = 0: Status = **"out_of_credit"**
- ❌ HTTP 401: Status = **"dead"**

---

## ⚡ Performance

### Check 1 Key:
- Thời gian: ~1-2 giây
- API call: 1 request đến ElevenLabs

### Check All Keys:
- Thời gian: ~30 giây cho 50 keys
- API call: 50 requests với delay 500ms giữa các lần
- Lý do delay: Tránh bị rate limit từ ElevenLabs

---

## 🔐 Security

1. **Admin Only**: Chỉ admin mới được phép check keys
2. **Authentication**: Sử dụng session cookie
3. **Database Protection**: API key không bao giờ được trả về frontend
4. **Rate Limiting**: Delay 500ms giữa các lần check để tránh spam

---

## 💡 Use Cases

### 1. Kiểm Tra Key Mới Nhập
Sau khi import keys từ file TXT, admin có thể check ngay để:
- Xác nhận keys còn hoạt động
- Lọc bỏ keys dead
- Xem credit balance

### 2. Kiểm Tra Định Kỳ
Admin có thể check all keys hàng tuần để:
- Phát hiện keys hết credit
- Cập nhật status mới nhất
- Lập báo cáo tình trạng keys

### 3. Debug Khi User Báo Lỗi
Khi user báo key không hoạt động, admin có thể:
- Check lại key ngay lập tức
- Xem last_error để biết nguyên nhân
- Assign key mới nếu cần

---

## 🐛 Troubleshooting

### Lỗi: "Failed to connect to ElevenLabs API"
**Nguyên nhân:** Lỗi network hoặc ElevenLabs server down

**Giải pháp:**
- Kiểm tra internet connection
- Thử lại sau vài phút
- Check status ElevenLabs API: https://status.elevenlabs.io

---

### Lỗi: "Invalid API key"
**Nguyên nhân:** Key đã bị revoke hoặc không hợp lệ

**Giải pháp:**
- Xóa key khỏi database
- Thêm key mới

---

### Lỗi: "Rate limit exceeded"
**Nguyên nhân:** Quá nhiều requests trong thời gian ngắn

**Giải pháp:**
- Đợi 1-2 phút
- Hệ thống tự động delay 500ms giữa các lần check

---

## 📝 Code Integration

### Sử dụng trong TypeScript/JavaScript:

```typescript
import { checkElevenLabsKey, checkAllElevenLabsKeys } from '@/lib/api';

// Check 1 key
const result = await checkElevenLabsKey(123);
console.log(result);

// Check all keys
const allResults = await checkAllElevenLabsKeys();
console.log(allResults.summary);
```

---

## 🎨 UI Components

### Button "Check"
- Icon: RefreshCw (từ lucide-react)
- Color: Blue (#2563eb)
- Animation: Spin khi đang check
- Tooltip: "Check credit từ ElevenLabs server"

### Button "Check All Keys"
- Icon: RefreshCw
- Color: Secondary
- Text: "Checking..." khi đang chạy
- Confirmation: Popup xác nhận trước khi chạy

---

## 📈 Future Enhancements

Có thể thêm sau:

1. **Auto Check Schedule**: Tự động check keys mỗi ngày
2. **Email Notifications**: Gửi email khi key hết credit
3. **Credit Threshold**: Set ngưỡng cảnh báo custom cho từng key
4. **History Tracking**: Lưu lịch sử check và credit changes
5. **Batch Operations**: Check theo user hoặc theo status

---

## ✅ Summary

Bạn đã có đầy đủ tính năng check credit từ server với **Realtime Progress UI**:

### Backend:
- ✅ **API endpoints hoàn chỉnh** (check 1 key + check all keys)
- ✅ **Server-Sent Events (SSE)** streaming realtime
- ✅ **Auto update database** cho tất cả keys
- ✅ **Error handling** đầy đủ
- ✅ **Admin only access** bảo mật
- ✅ **Rate limiting protection** (delay 500ms)

### Frontend:
- ✅ **Progress Modal** với design đẹp
- ✅ **Progress Bar** animated với %
- ✅ **Realtime updates** - Hiển thị ngay khi có kết quả
- ✅ **Color coding** - Xanh/Đỏ/Vàng theo status
- ✅ **Current key indicator** - Biết đang check key nào
- ✅ **Scrollable results** - Xem được tất cả kết quả
- ✅ **Summary statistics** - Tổng kết cuối cùng
- ✅ **Loading states** - Spinner animations

### User Experience:
- 🎯 **Không phải chờ đợi** - Xem progress realtime
- 🎯 **Không bị block UI** - Modal riêng biệt
- 🎯 **Biết tiến độ chính xác** - Progress bar với số %
- 🎯 **Xem kết quả ngay** - Không phải đợi hết mới biết
- 🎯 **Có thể đóng khi xong** - Button "Đóng" xuất hiện sau khi hoàn tất

**Trải nghiệm như YouTube upload progress - Professional & Smooth! 🚀**

