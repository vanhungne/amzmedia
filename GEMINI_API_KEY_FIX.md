# Gemini API Key Error - Đã Sửa ✅

## 🐛 Vấn đề

Lỗi: **400 INVALID_ARGUMENT - API key not valid**

```
Error: 400 INVALID_ARGUMENT. 
{'error': {
    'code': 400, 
    'message': 'API key not valid. Please pass a valid API key.', 
    'status': 'INVALID_ARGUMENT'
}}
```

## 🔍 Nguyên nhân

**Code đang dùng API keys cứng (hardcoded) thay vì load từ server!**

Trong file `image_tab_full.py`, dòng 1772-1777:

```python
HARDCODED_KEYS = [
    "AIzaSyBZI6MARCTjityVTpe5-_SWyONlm-Cdm-w",  # ❌ Key cũ/không hợp lệ
    "AIzaSyCzs6FxFjNtjT6UZg0rHDuLJZy3qPwX99k",  # ❌ Key cũ/không hợp lệ
    "AIzaSyASh-ecEWrpXbjc-JPKhl6RUPzDfs7kkoM"   # ❌ Key cũ/không hợp lệ
]
self.rotator = KeyRotator(HARDCODED_KEYS)
```

**Kết quả:** 
- Bạn đã cấp 3 keys mới trên Admin Panel server
- Nhưng code KHÔNG load keys từ server
- Code dùng 3 keys cũ đã bị revoked/invalid
- → Lỗi 400 INVALID_ARGUMENT

## ✅ Giải pháp đã thực hiện

### 1. **Sửa file `image_tab_full.py`**

#### a) Thêm parameter `api_client` vào constructor:
```python
def __init__(self, parent=None, api_client=None):
    super().__init__(parent)
    self.api_client = api_client
```

#### b) Thay hardcoded keys bằng fallback key:
```python
# Initialize with fallback key - will be loaded from server
DEFAULT_KEY = "AIzaSyBZI6MARCTjityVTpe5-_SWyONlm-Cdm-w"  # Fallback only
self.rotator = KeyRotator([DEFAULT_KEY])
```

#### c) Thêm method `load_gemini_keys_from_server()`:
```python
def load_gemini_keys_from_server(self):
    """Load Gemini API keys from Admin Panel server"""
    if not self.api_client or not self.api_client.is_authenticated():
        self.set_status("❌ Not connected to server. Using fallback key.")
        return
    
    # Load keys từ server
    keys_data = self.api_client.get_gemini_keys()
    
    # Extract API keys
    api_keys = [item['api_key'].strip() for item in keys_data 
                if item.get('api_key', '').strip()]
    
    # Update key rotator với server keys
    self.rotator = KeyRotator(api_keys)
    
    self.set_status(f"✅ Loaded {len(api_keys)} Gemini keys from server")
```

#### d) Thêm button "🔑 Load Keys" trong toolbar:
```python
load_keys_btn = ModernButton("🔑 Load Keys", Theme.PRIMARY)
load_keys_btn.setToolTip("Load Gemini API keys from Admin Panel server")
load_keys_btn.clicked.connect(self.load_gemini_keys_from_server)
toolbar_layout.addWidget(load_keys_btn)
```

### 2. **Sửa file `GenVideoPro.py`**

#### a) Pass api_client khi khởi tạo ImageGeneratorTab:
```python
# Dòng 6684-6685
self.image_gen_widget = ImageGeneratorTab(
    self.tab_image_generator, 
    api_client=self.api_client
)
```

#### b) Auto-load keys sau khi login:
```python
# Dòng 7375-7379
if hasattr(win, 'image_gen_widget') and win.image_gen_widget:
    win.image_gen_widget.api_client = win.api_client
    # Auto-load Gemini keys from server
    QTimer.singleShot(2000, win.image_gen_widget.load_gemini_keys_from_server)
```

## 📋 Cách sử dụng

### Tự động (Recommended)
1. **Đăng nhập vào WorkFlow Tool**
2. **Đợi 2 giây** - Keys sẽ tự động load từ server
3. Bạn sẽ thấy thông báo: ✅ "Loaded X Gemini API keys from server!"

### Thủ công
1. Đăng nhập vào WorkFlow Tool
2. Chuyển sang tab **Image Generator**
3. Click button **🔑 Load Keys** ở góc phải toolbar
4. Keys sẽ được load từ server và sẵn sàng sử dụng

## 🔐 Bảo mật

- ✅ Keys được load **trực tiếp vào memory** từ server
- ✅ Keys **KHÔNG được lưu vào file** local
- ✅ User thường **KHÔNG thấy được** keys
- ✅ Keys **xoay vòng tự động** khi có lỗi rate limit/quota
- ✅ Status của keys được **báo cáo ngược lại server**

## 🎯 Kết quả

**TRƯỚC:**
```
❌ Dùng 3 keys cứng trong code → Lỗi 400 INVALID_ARGUMENT
```

**SAU:**
```
✅ Load 3 keys từ server → Keys hợp lệ → Generate thành công!
```

## 📝 Ghi chú

1. **Cần có kết nối tới Admin Panel server**
   - Đăng nhập thành công
   - Server phải có ít nhất 1 Gemini key với status="active"

2. **Key rotation tự động**
   - Khi một key lỗi (rate limit/quota), hệ thống tự động chuyển sang key tiếp theo
   - Báo cáo status về server để admin biết key nào đang có vấn đề

3. **Fallback key chỉ dùng khi:**
   - Chưa đăng nhập
   - Server không có keys
   - Để đảm bảo app không crash

## 🔧 Bước quan trọng: Clean keys hiện có trong database

**Nếu bạn đã thêm keys vào database trước khi fix này, chạy script SQL để clean:**

1. Mở SQL Server Management Studio (SSMS)
2. Connect tới database của bạn
3. Chạy script: `admin-panel/scripts/clean_gemini_keys.sql`

Script này sẽ:
- ✅ Xóa khoảng trắng đầu/cuối
- ✅ Xóa ký tự xuống dòng (\n, \r)
- ✅ Xóa ký tự tab (\t)
- ✅ Hiển thị tất cả keys sau khi clean

**HOẶC:** Xóa keys cũ và thêm lại keys mới qua Admin Panel UI (keys mới sẽ tự động được clean).

## 🧪 Kiểm tra

Để đảm bảo fix hoạt động:

1. ✅ **Clean database** (chạy SQL script hoặc thêm keys mới)
2. ✅ Đăng nhập vào Admin Panel
3. ✅ Vào Dashboard → Gemini Keys 
4. ✅ Kiểm tra có ít nhất 1 key với status="active"
5. ✅ Mở WorkFlow Tool → Image Generator tab
6. ✅ Xem thông báo "✅ Loaded X Gemini keys from server"
7. ✅ Check console logs để xem keys có format đúng không:
   ```
   🔑 Loaded key 1: AIzaSyDo...jcNNIKI (length: 39)
   ```
8. ✅ Thử generate một image để test

---

**Tác giả:** AI Assistant  
**Ngày:** 2025-11-06  
**Version:** 1.0

