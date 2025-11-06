# 📝 Hướng Dẫn Tùy Biến System Prompt cho Từng Project

## ✅ Đã Sửa 2 Vấn Đề Chính

### 🐛 **Vấn đề 1: Số lượng prompts không khớp**

**TRƯỚC:**
- User chọn 22 prompts
- AI trả về 34 prompts
- System lấy cả 34 prompts → SAI!

**SAU:**
```python
# ✅ Giới hạn số lượng theo yêu cầu
if len(final_prompts) > num_parts:
    print(f"[LIMIT] AI trả về {len(final_prompts)} prompts, giới hạn về {num_parts}")
    final_prompts = final_prompts[:num_parts]
```

**Kết quả:** 
- Chọn 22 prompts → Nhận ĐÚNG 22 prompts ✅

---

### 🐛 **Vấn đề 2: System prompt hardcoded, không linh hoạt**

**TRƯỚC:**
```python
# ❌ Hardcoded - không thể thay đổi cho project khác
system_prompt = """Bạn là GPT chuyên xử lý kịch bản Simple Woman..."""
```

**SAU:**
```python
# ✅ Lấy từ Project settings
def analyze_script_with_groq(..., custom_system_prompt: str = ""):
    # Use custom prompt from Project, or default
    system_prompt = custom_system_prompt if custom_system_prompt else default_system_prompt
```

---

## 🎯 Cách Sử Dụng - Tùy Biến System Prompt Cho Từng Project

### **Bước 1: Tạo/Chỉnh Sửa Project**

1. Mở **GenVideoPro** → Tab **Projects**
2. Click **"➕ New Project"** hoặc **"✏️ Edit Project"** 
3. Trong dialog, tìm field **"Script Template (System Prompt)"**

![Project Dialog]

---

### **Bước 2: Nhập System Prompt Tùy Biến**

**Ví dụ cho project "Simple Woman Story":**

```
Bạn là GPT chuyên xử lý các kịch bản dài bằng tiếng Anh để phục vụ sản xuất video cảm xúc dành cho khán giả YouTube tại Mỹ.

Quy trình tự động xử lý như sau:

1. Đọc hiểu kịch bản (Simple Woman - Nữ chính hiền lành, Nam phản diện tức giận)
2. Chia kịch bản thành {x} phần như yêu cầu
3. Prompt cần phải có sự đồng nhất chi tiết về trang phục, màu da và ngoại hình

NGUYÊN TẮC VIẾT PROMPT:
- Ngôn ngữ: tiếng Anh
- Style mặc định: ultra-realistic photo, 16:9
- Luôn có 2 nhân vật chính (nam & nữ): 1 chính diện và 1 phản diện
- Nhân vật: người Mỹ hoặc châu Âu, màu tóc KHÔNG MÔ TẢ MÀU ĐEN

FORMAT OUTPUT:
Chỉ trả về các prompt tiếng Anh, mỗi prompt trên một dòng, ngăn cách bằng dấu xuống dòng đôi.
```

**Ví dụ cho project "Adventure Story":**

```
You are an expert GPT for creating cinematic adventure scene prompts for YouTube videos.

RULES:
1. Split script into {x} equal parts as requested
2. Each prompt must describe an exciting adventure scene
3. Style: cinematic photo, 16:9, action-packed
4. Characters: diverse adventurers with consistent appearance
5. Settings: exotic locations, dramatic lighting

OUTPUT FORMAT:
Return ONLY English prompts, one per line, separated by double newline.
```

---

### **Bước 3: Lưu Project**

Click **"Save"** → System prompt được lưu vào Project.

---

### **Bước 4: Sử dụng Trong Image Generator**

1. **Chọn Project hiện tại:**
   - Vào tab **Projects** → Click vào project bạn muốn
   - Project sẽ được đánh dấu là "Current"

2. **Generate Prompts:**
   - Vào tab **Image Generator**
   - Click **"📜 Import Script"**
   - Paste script → Click **"🤖 Analyze & Generate"**

3. **Kết quả:**
   - ✅ AI sẽ dùng **custom system prompt** từ project
   - ✅ Tạo **ĐÚNG SỐ LƯỢNG** prompts như bạn chọn
   - ✅ Prompts phù hợp với style của project

---

## 📊 Flow Hoạt Động

```
[User] → Chọn Project "Simple Woman"
         ↓
[Project] → script_template = "Bạn là GPT chuyên Simple Woman..."
            ↓
[ImageGenerator] → Import script
                   ↓
[Groq AI] ← system_prompt = script_template từ Project
            + user_prompt = "Chia thành 22 phần..."
            ↓
[AI Response] → 34 prompts (có thể nhiều hơn)
                ↓
[Filter & Limit] → Giới hạn về 22 prompts ✅
                    ↓
[Result] → User nhận ĐÚNG 22 prompts ✅
```

---

## 🎨 Ví Dụ Các Project Khác Nhau

### **Project 1: Simple Woman (Drama)**

**Script Template:**
```
Focus: Emotional drama, female protagonist, male antagonist
Style: Ultra-realistic, bright lighting, 16:9
Characters: American/European, no black hair
Tone: Dramatic, emotional
```

### **Project 2: Hero Journey (Adventure)**

**Script Template:**
```
Focus: Epic adventure, hero's journey
Style: Cinematic, dramatic lighting, 16:9
Characters: Diverse heroes, fantasy elements
Tone: Inspirational, action-packed
```

### **Project 3: Tech Startup (Modern)**

**Script Template:**
```
Focus: Modern business, innovation stories
Style: Professional photography, clean aesthetics, 16:9
Characters: Young entrepreneurs, diverse teams
Tone: Inspirational, professional
```

**→ Mỗi project có style khác nhau, prompts khác nhau!**

---

## ✅ Checklist Sử Dụng

- [ ] Tạo/Edit project
- [ ] Nhập custom **Script Template** (System Prompt)
- [ ] **Lưu project**
- [ ] **Chọn project** làm "Current"
- [ ] Vào **Image Generator** tab
- [ ] Import script → AI sẽ dùng custom prompt
- [ ] Nhận **đúng số lượng** prompts ✅

---

## 🔧 Chi Tiết Kỹ Thuật (Cho Dev)

### **Files Đã Sửa:**

1. **`image_tab_full.py`:**
   - ✅ Function `analyze_script_with_groq()`: Thêm parameter `custom_system_prompt`
   - ✅ Giới hạn số lượng prompts theo `num_parts`
   - ✅ Class `ScriptImportDialog`: Nhận `custom_system_prompt`
   - ✅ Class `ImageGeneratorTab`: Nhận `project_manager`, lấy `script_template`

2. **`GenVideoPro.py`:**
   - ✅ Pass `project_manager` vào `ImageGeneratorTab`
   - ✅ Project class đã có field `script_template` (line 299)

### **Flow Code:**

```python
# GenVideoPro.py
self.image_gen_widget = ImageGeneratorTab(
    api_client=self.api_client,
    project_manager=self.project_manager  # ← Pass project manager
)

# image_tab_full.py - ImageGeneratorTab
def on_import_script(self):
    # Get custom prompt from project
    custom_prompt = ""
    if self.project_manager and self.project_manager.current_project:
        custom_prompt = self.project_manager.current_project.script_template
    
    # Use custom prompt
    prompts = analyze_script_with_groq(
        script, 
        num_parts, 
        groq_key,
        custom_prompt  # ← Truyền custom prompt
    )

# analyze_script_with_groq function
def analyze_script_with_groq(..., custom_system_prompt: str = ""):
    # Use custom or default
    system_prompt = custom_system_prompt if custom_system_prompt else default_system_prompt
    
    # Limit to num_parts
    if len(prompts) > num_parts:
        prompts = prompts[:num_parts]  # ✅ Giới hạn
```

---

## 🚀 Kết Quả

**TRƯỚC:**
- ❌ 22 prompts → Nhận 34 prompts (sai)
- ❌ Không thể tùy biến prompt cho từng project
- ❌ Phải sửa code mỗi lần đổi style

**SAU:**
- ✅ 22 prompts → Nhận ĐÚNG 22 prompts
- ✅ Mỗi project có custom system prompt riêng
- ✅ Tùy biến qua UI, không cần sửa code
- ✅ Linh hoạt cho nhiều loại content

---

**Happy Prompting!** 🎨✨



