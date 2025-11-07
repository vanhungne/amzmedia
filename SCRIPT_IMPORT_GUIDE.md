# 📜 Script Import Feature - Hướng Dẫn Sử Dụng

## 🎯 Tính năng mới: Import Script & Auto Generate Prompts

Tính năng này cho phép bạn import kịch bản (script) tiếng Anh và tự động tạo ra các prompt chuẩn cho việc tạo ảnh, theo đúng quy tắc của video cảm xúc dành cho YouTube tại Mỹ.

---

## 🔧 Cài đặt ban đầu

### 1. Thêm Groq API Key

**Bước 1:** Lấy API key từ Groq
- Truy cập: https://console.groq.com/keys
- Đăng nhập và tạo API key mới
- Copy key (dạng: `gsk_...`)

**Bước 2:** Thêm key vào GenVideoPro
- Mở GenVideoPro
- Vào tab **⚙️ Settings**
- Tìm phần **🔑 Groq API (Auto-prompt)**
- Paste API key vào (mỗi dòng một key nếu có nhiều)
- Click **💾 Save Settings**

![Groq API Settings](https://via.placeholder.com/800x200/FF8C2E/FFFFFF?text=Add+Groq+API+Keys+in+Settings+Tab)

---

## 📖 Cách sử dụng

### 1. Cấu hình Settings
- Mở GenVideoPro → Tab **🎨 Image Generator**
- Vào phần **Settings** (sidebar bên trái)
- Tìm **Script Parts (for Import Script)**
- Chọn số phần muốn chia (mặc định: 5, tối đa: 50)
  - Ví dụ: 8 = chia script thành 8 prompts
- Click **💾 Save Settings**

### 2. Chuẩn bị Script File
- Tạo file `.txt` chứa script tiếng Anh
- Lưu với encoding UTF-8
- Script nên dài 5-20 câu tùy số phần muốn chia

### 3. Click nút "📜 Import Script"
- Trên toolbar, click nút **📜 Import Script** (màu tím)
- Chọn file `.txt` chứa script

### 4. Tự động xử lý
- ✅ AI tự động phân tích script theo quy tắc
- ✅ Tự động tạo prompts (số lượng = Script Parts đã cài)
- ✅ Tự động import vào queue
- ✅ Tự động bắt đầu generate ảnh
- Thời gian xử lý: 10-60 giây tùy độ dài script

### 5. Theo dõi tiến độ
- Status bar hiển thị: "🤖 Analyzing script..."
- Sau đó: "✅ Imported X prompts. Generating..."
- Các prompt row sẽ hiện trạng thái: QUEUE → PROCESSING → DONE

---

## 🎨 Quy tắc prompt được áp dụng

AI sẽ tự động tạo prompt theo các quy tắc sau:

### ✅ Chuẩn Format
- **Style**: Ultra-realistic photo, 16:9
- **Ngôn ngữ**: Tiếng Anh
- **Consistency**: Mô tả ngoại hình nhân vật giống nhau qua các prompt (KHÔNG dùng "same outfit")

### 👥 Nhân vật
- **2 nhân vật chính**: 1 chính diện + 1 phản diện (nam & nữ HOẶC nữ & nữ)
  - **Chính diện**: Điềm tĩnh, nội tâm sâu sắc
  - **Phản diện**: Cảm xúc mạnh (la hét, chỉ tay, khiêu khích...)
- **2-5+ nhân vật nền**: Tăng cảm xúc (cười nhạo, khinh thường, theo dõi...)
- **Dân tộc**: Người Mỹ hoặc châu Âu
- **Màu tóc**: KHÔNG mô tả màu đen (blonde, brown, auburn, red,...)
- **Tương tác**: Nhân vật nhìn và tương tác với nhau, KHÔNG nhìn thẳng vào camera

### 🎬 Technical
- **Ánh sáng**: Tươi sáng, rõ ràng, màu sắc tương phản
- **Composition**: Natural daylight, contemporary setting
- **Focus**: Sharp focus on main characters

### 🚫 Từ cấm
Các từ sau KHÔNG được xuất hiện trong prompt:
- `revealing cleavage`
- `showing cleavage`
- `emerald green eyes`
- `same outfit`
- `same look`

### 📝 Format mô tả ngoại hình
- Mô tả ngoại hình **PHẢI** đặt trong `()` 
- Ví dụ: `A woman (fair skin, wearing elegant navy blue dress, blonde wavy hair)`

---

## 💡 Ví dụ

### Input Script File (`my_script.txt`):
```
Sarah discovers her husband cheating. She confronts him at a party. 
Everyone watches. He yells and blames her. She stays calm and walks away with dignity.
```

### Output (3 prompts):
```
1. Ultra-realistic photo, 16:9. A woman (fair skin, wearing elegant navy blue dress, 
blonde wavy hair) standing in a bright modern party room, looking directly at a man 
(tan skin, wearing grey suit, brown short hair) with a shocked expression. 3 guests 
in the background (varied appearances) whispering and pointing. Natural chandelier 
lighting, high contrast, contemporary decor.

2. Ultra-realistic photo, 16:9. A woman (fair skin, wearing elegant navy blue dress, 
blonde wavy hair) calmly listening while a man (tan skin, wearing grey suit, brown 
short hair) angrily pointing and shouting at her with raised fist. 4 party guests 
(varied appearances) in background watching with judgmental expressions. Bright 
indoor lighting, modern living room setting.

3. Ultra-realistic photo, 16:9. A woman (fair skin, wearing elegant navy blue dress, 
blonde wavy hair) walking away with head held high while a man (tan skin, wearing 
grey suit, brown short hair) continues yelling behind her. 5 onlookers (varied 
appearances) some clapping, some recording with phones. Natural daylight from 
large windows, contemporary apartment, sharp focus on woman's confident posture.
```

---

## 🛠 Troubleshooting

### ❌ Lỗi: "Groq API Key Missing"
**Nguyên nhân**: Chưa thêm Groq API key trong Settings

**Giải pháp**: 
1. Vào tab **⚙️ Settings**
2. Thêm Groq API key trong phần **🔑 Groq API**
3. Save và thử lại

---

### ❌ Lỗi: "Groq API Error: 401"
**Nguyên nhân**: API key không hợp lệ hoặc đã hết hạn

**Giải pháp**:
1. Kiểm tra key tại https://console.groq.com/keys
2. Tạo key mới nếu cần
3. Cập nhật trong Settings

---

### ❌ Lỗi: "No prompts generated"
**Nguyên nhân**: Script quá ngắn hoặc không đủ thông tin

**Giải pháp**:
1. Đảm bảo script dài ít nhất 2-3 câu
2. Script phải bằng tiếng Anh
3. Cung cấp đủ chi tiết về tình huống, nhân vật, cảm xúc

---

### ❌ AI tạo prompt không đúng format
**Nguyên nhân**: Model AI đôi khi không tuân thủ 100% quy tắc

**Giải pháy**:
1. Sau khi import, bạn có thể **chỉnh sửa prompt** trước khi generate
2. Sử dụng nút **✨ AI Fix** để tối ưu prompt
3. Hoặc nhấn **Regenerate** để tạo lại

---

## 📊 Tips & Best Practices

### ✅ Script tốt:
- **Dài 3-10 câu** cho mỗi phần
- **Rõ ràng về tình huống**: Ai làm gì, ở đâu, cảm xúc ra sao
- **Có conflict**: Nhân vật chính diện vs phản diện
- **Có background characters**: Người xem, người xung quanh phản ứng

### ✅ Số phần phù hợp:
- Script ngắn (5-10 câu): Chia 3-5 phần
- Script trung bình (10-20 câu): Chia 6-10 phần
- Script dài (20+ câu): Chia 10-15 phần

### ✅ Workflow hiệu quả:
1. **Chuẩn bị script TXT** → Lưu file
2. **Cài Script Parts** trong Settings → Save
3. **Import script** → Chọn file TXT → Tự động generate
4. **Đợi hoàn thành** → Tất cả ảnh được tạo tự động
5. **Download** → Xuất ảnh về máy
6. **Edit in video** → Ghép vào video với voice-over

---

## 🎥 Workflow hoàn chỉnh: Script → Video

```
1. Viết script (tiếng Anh)
   ↓
2. Import Script (Image Generator) → AI tạo prompts
   ↓
3. Generate Images (8-15 ảnh)
   ↓
4. Tạo Voice Over (Audio Generator tab)
   ↓
5. Ghép ảnh + voice → Video (Image to Video tab hoặc ngoài app)
   ↓
6. Upload lên YouTube
```

---

## 📞 Support

Nếu gặp vấn đề hoặc cần hỗ trợ:
- Check Settings đã có Groq API key chưa
- Kiểm tra internet connection
- Thử lại với script ngắn hơn để test
- Check console log nếu là developer

---

## 🚀 Updates

**Version 2.0** (Current)
- ✅ Import script từ file TXT
- ✅ Phân tích với Groq AI (llama-3.3-70b-versatile)
- ✅ Tự động tạo prompts theo quy tắc
- ✅ Tự động import vào queue
- ✅ Tự động generate ngay (không cần confirm)
- ✅ Cài Script Parts trong Settings

**Planned:**
- 🔜 Support nhiều style (hiện tại: Simple Woman)
- 🔜 Template presets cho các loại video khác
- 🔜 Export prompts ra file
- 🔜 History và reuse scripts

---

**Made with ❤️ for Content Creators**

