# 🧪 Testing Guide - Realtime Progress UI

## Cách Test Tính Năng

### 1. Start Server
```bash
npm run dev
```

### 2. Login as Admin
- URL: `http://localhost:3000`
- Username: `admin`
- Password: `admin123`

### 3. Navigate to ElevenLabs Page
- Click vào menu **"ElevenLabs API Keys"**
- Hoặc truy cập trực tiếp: `http://localhost:3000/dashboard/elevenlabs`

### 4. Test Check 1 Key
**Steps:**
1. Tìm một key trong bảng
2. Click icon **🔄** ở cột Actions
3. Đợi 1-2 giây
4. Xem popup alert với thông tin chi tiết

**Expected Result:**
```
✅ Key đang hoạt động!

Status: active
Credit Balance: 50,000
Tier: starter
```

### 5. Test Check All Keys (Realtime Progress)
**Steps:**
1. Click nút **"Check All Keys"** ở góc trên phải
2. Confirm trong popup
3. Modal xuất hiện ngay lập tức

**Expected Behavior - Modal sẽ hiển thị:**

#### 5.1. Initial State (0-1 giây)
```
Progress: 0 / 50                    0%
[████████████████████████████░░░░]

Chưa có kết quả...
```

#### 5.2. First Key Being Checked (1-2 giây)
```
Progress: 1 / 50                    2%
[█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]  2%

🔄 Đang check: Key #1

Kết quả:
(still empty, waiting...)
```

#### 5.3. First Result Appears (~2-3 giây)
```
Progress: 1 / 50                    2%
[█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]  2%

🔄 Đang check: Key #2

Kết quả:
┌──────────────────────────────┐
│ ✅ Key #1                    │
│    ACTIVE • 50,000 credits   │
│    • starter                  │
└──────────────────────────────┘
```

#### 5.4. Multiple Results (~10 giây, 20 keys checked)
```
Progress: 20 / 50                   40%
[████████████░░░░░░░░░░░░░░░░░░]  40%

🔄 Đang check: Key #21

Kết quả:
┌──────────────────────────────┐
│ ✅ Key #1 - ACTIVE           │
│ ✅ Key #2 - ACTIVE           │
│ ❌ Key #3 - DEAD             │
│ ✅ Key #4 - ACTIVE           │
│ ⚠️  Key #5 - OUT_OF_CREDIT  │
│ ✅ Key #6 - ACTIVE           │
│ ...                           │
│ (scrollable)                  │
└──────────────────────────────┘
```

#### 5.5. Complete State (~25 giây, all 50 keys done)
```
Progress: 50 / 50                   100%
[████████████████████████████████] 100%

Kết quả:
┌──────────────────────────────┐
│ ✅ Key #1 - ACTIVE           │
│ ...                           │
│ ✅ Key #50 - ACTIVE          │
└──────────────────────────────┘

📊 Tổng Kết:
Total: 50    Active: 42    Dead: 5
Out of Credit: 3    Errors: 0

                        [Đóng]
```

## ✅ Checklist - What to Verify

### Visual Elements:
- [ ] Progress bar xuất hiện và tăng dần
- [ ] Số % cập nhật (0% → 2% → 4% → ... → 100%)
- [ ] Text "Progress: X / Y" cập nhật realtime
- [ ] Box "🔄 Đang check: Key #X" hiển thị và thay đổi
- [ ] Results list cập nhật từng dòng ngay lập tức
- [ ] Color coding đúng:
  - Xanh (green) cho active
  - Đỏ (red) cho dead
  - Vàng (yellow) cho out_of_credit
- [ ] Icons hiển thị đúng (✅ ❌ ⚠️)
- [ ] Summary box xuất hiện khi hoàn tất
- [ ] Button "Đóng" xuất hiện khi xong

### Functional:
- [ ] Modal không đóng được khi đang check
- [ ] Modal đóng được sau khi hoàn tất
- [ ] Progress bar smooth (không giật lag)
- [ ] Results list scroll được khi nhiều items
- [ ] Spinner animation hoạt động (🔄 quay)
- [ ] Header gradient background hiển thị đẹp
- [ ] Database cập nhật (refresh trang → xem credit_balance mới)

### Performance:
- [ ] UI không bị freeze/lag
- [ ] Mỗi key xuất hiện trong ~500ms
- [ ] Tổng thời gian = số keys × 0.5 giây (+ overhead)
- [ ] Browser không crash với 50-100 keys

## 🐛 Common Issues & Solutions

### Issue: "Failed to start checking"
**Cause:** Not logged in as admin
**Solution:** Login với account admin

### Issue: Modal không xuất hiện
**Cause:** No keys in database
**Solution:** Add some test keys first

### Issue: Stream bị disconnect
**Cause:** Server timeout or error
**Solution:** 
- Check server logs
- Restart dev server
- Check database connection

### Issue: Progress bar không tăng
**Cause:** SSE messages không đến
**Solution:**
- Mở DevTools → Network tab
- Tìm request `check-all` với type `eventsource`
- Xem messages có đến không

## 🔍 Debugging

### Open Browser DevTools:

#### 1. Network Tab
- Filter: `check-all`
- Type: `eventsource` hoặc `other`
- Click vào request
- Tab "Response" → Xem messages realtime

Expected messages:
```
data: {"type":"start","total":50}

data: {"type":"progress","current":1,"total":50,"keyId":1,"keyName":"Key #1","status":"checking"}

data: {"type":"result","id":1,"name":"Key #1","success":true,"status":"active","credit_balance":50000,"tier":"starter","warning":null}

...

data: {"type":"complete","summary":{...}}
```

#### 2. Console Tab
- Check for errors
- Look for `console.log` outputs

#### 3. React DevTools
- Components → Find `ElevenLabsPage`
- State → Look at `progressData`
- Verify state updates in realtime

## 📹 Expected Timeline (50 keys example)

```
0:00 - Click "Check All Keys"
0:00 - Modal appears immediately
0:01 - Progress: 1/50, first key checking
0:02 - First result appears ✅
0:03 - Progress: 2/50, second result ✅
0:04 - Progress: 3/50, third result ❌
...
0:25 - Progress: 50/50, all done
0:25 - Summary appears
0:25 - "Đóng" button enabled
```

**Average time per key:** 500ms (0.5 seconds)
**Total for 50 keys:** ~25 seconds
**Total for 100 keys:** ~50 seconds

## 🎯 Success Criteria

✅ **Test passed if:**
1. Modal hiển thị ngay khi click
2. Progress bar tăng smooth từ 0% → 100%
3. Mỗi result xuất hiện ngay sau khi check xong
4. Không có UI freeze/lag
5. Summary hiển thị đúng số liệu
6. Database được cập nhật đúng

## 🚀 Next Steps After Testing

If everything works:
1. ✅ Commit changes
2. ✅ Deploy to production
3. ✅ Train admin users
4. ✅ Monitor performance

If issues found:
1. Note the issue in detail
2. Check logs (server + browser)
3. Report with screenshots
4. Debug using DevTools

---

**Happy Testing! 🧪**

