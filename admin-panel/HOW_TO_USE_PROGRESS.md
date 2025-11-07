# 🎯 Cách Sử Dụng Progress Tracking

## ✨ Tính Năng Mới: Bulk Assign với Progress Bar

### 📍 Đã Implement:
1. ✅ **Real-time progress bar** cho bulk assign keys
2. ✅ **Toast notifications** đẹp mắt thay alert()
3. ✅ **Background processing** không block UI
4. ✅ **Error tracking** chi tiết

---

## 🚀 Test Ngay

### Bước 1: Start dev server
```bash
cd admin-panel
npm run dev
```

### Bước 2: Vào trang ElevenLabs Keys
```
http://localhost:3000/dashboard/elevenlabs
```

### Bước 3: Click "Bulk Assign"
1. Chọn User từ dropdown
2. Nhập số lượng keys (ví dụ: 100)
3. Click "Assign Keys"

### Bước 4: Xem progress bar magic! ✨
- Modal popup với progress bar
- Hiển thị % hoàn thành (0-100%)
- Hiển thị items processed (10/100)
- Ước tính thời gian còn lại (~2m 30s)
- Danh sách errors (nếu có)

### Bước 5: Khi hoàn thành
- Progress bar đạt 100%
- Toast notification hiện lên: "✅ Assign keys hoàn thành!"
- Data tự động refresh

---

## 📊 Screenshots Concept

### 1. Bulk Assign Modal
```
┌──────────────────────────────────┐
│  Bulk Assign Keys to User    [X]│
├──────────────────────────────────┤
│                                  │
│  Select User: [bong (user)  ▼] │
│                                  │
│  Số Lượng Keys: [100        ]   │
│                                  │
│  ℹ️ Hệ thống sẽ tự động assign  │
│  N keys chưa được cấp phát      │
│                                  │
│  Available: 347 unassigned keys │
│                                  │
│      [Hủy]    [Assign Keys]     │
└──────────────────────────────────┘
```

### 2. Progress Modal
```
┌──────────────────────────────────┐
│  Assign Keys cho bong        [X]│
├──────────────────────────────────┤
│                                  │
│  Progress: 45 / 100         45% │
│  ████████████░░░░░░░░░░░░░      │
│                                  │
│  ⚙️ Đang assign key 45/100...   │
│                                  │
│  Ước tính còn lại: ~1m 30s      │
│                                  │
│  0 lỗi xảy ra                    │
│                                  │
│  ℹ️ Đợi đến khi hoàn thành      │
└──────────────────────────────────┘
```

### 3. Complete State
```
┌──────────────────────────────────┐
│  Assign Keys cho bong        [X]│
├──────────────────────────────────┤
│                                  │
│  Progress: 100 / 100       100% │
│  ████████████████████████████   │
│                                  │
│  ✅ Hoàn thành!                 │
│  Đã assign 100 keys cho bong.   │
│                                  │
│  Thời gian: 3m 15s              │
│                                  │
│                         [Đóng]  │
└──────────────────────────────────┘
```

### 4. Toast Notification
```
┌────────────────────────────┐
│ ✅  Assign keys hoàn thành!│
│                        [X] │
└────────────────────────────┘
```

---

## 🔧 Technical Details

### API Endpoint mới
```
POST /api/elevenlabs/bulk-assign-with-progress
```

**Request:**
```json
{
  "user_id": 1,
  "quantity": 100
}
```

**Response:**
```json
{
  "operationId": "bulk_assign_1699999999999_abc123",
  "message": "Bắt đầu assign 100 keys cho user bong",
  "totalKeys": 100
}
```

### Polling Endpoint
```
GET /api/operations/{operationId}/status
```

**Response:**
```json
{
  "operationId": "bulk_assign_...",
  "progress": 45,
  "status": "processing",
  "message": "Đang assign key 45/100...",
  "currentItem": 45,
  "totalItems": 100,
  "errors": [],
  "startedAt": "2024-01-01T00:00:00Z"
}
```

---

## 🎨 UI Components Được Sử Dụng

1. **BulkOperationModal** - Modal với progress bar
2. **ProgressBar** - Progress bar component với polling
3. **Toast** - Notification system
4. **LoadingSpinner** - Loading states (optional)

---

## ⚡ Performance

### Không có progress tracking:
```typescript
// User clicks button
handleBulkAssign() → API call → ... 2 minutes ... → alert("Done!")
// ❌ User không biết gì, tưởng web treo
```

### Có progress tracking:
```typescript
// User clicks button
handleBulkAssign() → API returns operationId → Show modal
// User sees:
// ⚙️ 0% → 10% → 20% → ... → 100% ✅
// Real-time updates mỗi 500ms
```

---

## 🐛 Troubleshooting

### Progress không update?
1. Check Network tab (F12) - có requests tới `/api/operations/*/status` không?
2. Check console - có errors không?
3. Verify operationId được return từ API

### Modal không hiện?
1. Check state `showProgressModal` = true
2. Check `operationId` không null
3. Check console errors

### Toast không hiện?
1. Verify `<ToastContainer />` được render
2. Check `useToast()` hook được gọi

---

## 💡 Extend cho features khác

Áp dụng tương tự cho:
- ✅ Bulk Import Keys (đã có: `bulk-import-with-progress`)
- ✅ Check All Keys (đang dùng custom progress modal)
- 🔜 Bulk Delete Keys
- 🔜 Bulk Update Status
- 🔜 Export Large Dataset

**Template:**
1. Tạo API route: `/api/xxx/bulk-xxx-with-progress/route.ts`
2. Copy code từ `bulk-assign-with-progress`
3. Update logic xử lý
4. Frontend: gọi API → lấy operationId → show modal

---

**🎉 Enjoy smooth UX!**

















