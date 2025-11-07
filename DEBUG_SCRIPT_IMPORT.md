# 🐛 Debug Script Import Issues

## Vấn đề: "Analyzing script..." nhưng không tạo ra prompts

### ✅ Đã fix trong version này:

1. **Added extensive debug logging** 
   - Tất cả output sẽ hiện trong console/terminal
   - Xem được raw response từ Groq AI
   - Track từng bước filter prompts

2. **Relaxed filtering rules**
   - Cũ: Chỉ accept prompts bắt đầu bằng "ultra-realistic", "a ", "the ", etc.
   - Mới: Accept hầu hết, chỉ skip headers và translation

3. **Fallback mechanism**
   - Nếu filter bỏ hết → Return all prompts
   - Không bao giờ để trống

---

## 🔍 Cách debug:

### 1. Chạy từ Command Line (xem logs):

**Windows:**
```cmd
cd D:\Tools\WorkFlow
python GenVideoPro.py
```

**Hoặc PowerShell:**
```powershell
cd D:\Tools\WorkFlow
python GenVideoPro.py
```

### 2. Import script và xem console output:

Sau khi click "Import Script" và chọn file, bạn sẽ thấy logs như:

```
[WORKER] Starting analysis with 12 parts
[WORKER] Script length: 1234 chars
[WORKER] Script preview: Sarah arrives at her anniversary party...
[WORKER] Using Groq key: gsk_abc123xyz...
[GROQ AI RAW RESPONSE]:
Ultra-realistic photo, 16:9. A woman (fair skin, wearing elegant navy blue dress...
================================================================================
[PARSED PROMPTS COUNT]: 12
[ACCEPT 0]: Ultra-realistic photo, 16:9. A woman (fair skin, wearing elegant navy blue...
[ACCEPT 1]: Ultra-realistic photo, 16:9. A woman (fair skin, wearing elegant navy blue...
...
[FINAL PROMPTS COUNT]: 12
[WORKER] Got 12 prompts from AI
[SUCCESS HANDLER] Received 12 prompts
[FIRST PROMPT PREVIEW]: Ultra-realistic photo, 16:9. A woman (fair skin, wearing...
[ADDING ROW 1]: Ultra-realistic photo, 16:9. A woman (fair skin, wearing...
[ADDING ROW 2]: Ultra-realistic photo, 16:9. A woman (fair skin, wearing...
...
[STATUS] Starting generation for 12 prompts
[GENERATING] 12 rows
```

---

## 🚨 Nếu vẫn gặp lỗi:

### Lỗi 1: `[PARSED PROMPTS COUNT]: 0`
**Nguyên nhân:** AI không trả về gì hoặc format lỗi

**Giải pháp:**
- Check `[GROQ AI RAW RESPONSE]` có content không
- Nếu trống → Groq API key hết quota hoặc lỗi
- Thử key khác hoặc regenerate key

---

### Lỗi 2: `[FINAL PROMPTS COUNT]: 0` nhưng `[PARSED PROMPTS COUNT]: 10`
**Nguyên nhân:** Filter bỏ hết prompts

**Giải pháp:**
- Xem các dòng `[SKIP HEADER]`, `[SKIP SHORT]`, `[SKIP TRANSLATION]`
- Nếu tất cả bị skip → AI format sai
- Copy `[GROQ AI RAW RESPONSE]` và gửi cho dev để fix filter

---

### Lỗi 3: `[WORKER ERROR] ...`
**Nguyên nhân:** Exception trong quá trình xử lý

**Giải pháp:**
- Đọc error message
- Common errors:
  - `401 Unauthorized` → API key sai
  - `429 Rate Limit` → Quá nhiều requests, đợi 1 phút
  - `Timeout` → Mạng chậm hoặc script quá dài
  - `JSON decode error` → Groq response lỗi format

---

### Lỗi 4: `[SUCCESS HANDLER] Received 0 prompts`
**Nguyên nhân:** Fallback cũng trả về empty

**Giải pháy:**
- Check lại response từ Groq
- Script có thể quá ngắn hoặc không phù hợp
- Thử script khác (example_script.txt)

---

## 📝 Test Script:

### Script đơn giản để test:
```
Sarah walks into a party. She sees her husband with another woman. 
Everyone stops and stares. The husband starts yelling. 
Sarah stays calm and leaves with dignity.
```

### Expected output:
- 5 prompts (nếu Script Parts = 5)
- Mỗi prompt > 50 chars
- Tất cả bắt đầu với "Ultra-realistic photo, 16:9"

---

## 🔧 Advanced: Disable Filter Temporarily

Nếu muốn test xem AI trả về gì mà không bị filter:

**Edit `image_tab_full.py` line ~278:**
```python
# Comment out filter, return all
return prompts  # <-- Force return all, no filter
```

Sau đó restart app và test lại.

---

## 📞 Still Not Working?

**Gửi thông tin sau:**

1. **Console output** (toàn bộ từ `[WORKER]` đến `[GENERATING]`)
2. **Groq API key** (20 ký tự đầu): `gsk_abc...`
3. **Script length**: X characters
4. **Script Parts**: X
5. **Error message** (nếu có)

---

## ✅ Success Indicators:

Khi thành công, bạn sẽ thấy:

✅ Console:
```
[FINAL PROMPTS COUNT]: 12
[SUCCESS HANDLER] Received 12 prompts
```

✅ UI:
- Status: "✅ Imported 12 prompts from script. Generating..."
- 12 rows hiện trong queue
- Mỗi row có status: QUEUE → PROCESSING → DONE

✅ Output folder:
- Ảnh bắt đầu được tạo: `01_001.png`, `01_002.png`, ...

---

**Happy debugging! 🎬**


