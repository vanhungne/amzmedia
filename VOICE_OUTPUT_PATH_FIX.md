# 🎵 Voice Output Path Fix - Lưu Đúng Folder Project

## ✅ Đã Sửa

### 🐛 **Vấn đề:**

File audio merged được lưu SAI CHỖ:
- ❌ Lưu vào: `C:/TotalTool/output/merged_timestamp.mp3`
- ❌ Tên file: `merged_20251106_150316.mp3` (timestamp)

**Mong muốn:**
- ✅ Lưu vào: `D:\Black woman\voice\script_name.mp3` (project voice folder)
- ✅ Tên file: Theo tên script được import (ví dụ: `black_woman_story.mp3`)

---

## 🔧 **Đã sửa:**

### **1. Thêm `project_manager` vào ElevenLabsGUI**

```python
# ElevenlabsV15.py - Line 790
class ElevenLabsGUI(QMainWindow):
    def __init__(self, api_client=None, project_manager=None):  # ← Thêm project_manager
        super().__init__()
        
        self.api_client = api_client
        self.project_manager = project_manager  # ← Access to project settings
```

### **2. Logic mới cho output path (3 priority levels)**

```python
# ElevenlabsV15.py - merge_audio_files() - Line 3537+

# Priority 1: Project Voice Folder ✅ (HIGHEST)
if self.project_manager and self.project_manager.current_project:
    project = self.project_manager.current_project
    if project.voice_output:
        output_dir = project.voice_output  # D:\Black woman\voice
        output_name = script_name  # black_woman_story
        # → D:\Black woman\voice\black_woman_story.mp3

# Priority 2: TXT File Location (legacy)
elif self.project_text_path:
    output_dir = os.path.dirname(self.project_text_path)
    output_name = script_name
    # → Same folder as TXT file

# Priority 3: Fallback (last resort)
else:
    output_dir = C:/TotalTool/output
    output_name = f"merged_{timestamp}"
    # → C:/TotalTool/output/merged_timestamp.mp3
```

### **3. Pass `project_manager` từ GenVideoPro**

```python
# GenVideoPro.py - Line 6947
self.elevenlabs_widget = ElevenLabsGUI(
    api_client=self.api_client,
    project_manager=self.project_manager  # ← Pass project manager
)
```

---

## 🎯 **Cách Hoạt Động:**

### **Kịch bản 1: Có project được chọn (Recommended)**

```
[User] → Chọn project "Black woman"
         ↓
[Project] → voice_output = "D:\Black woman\voice"
            ↓
[ElevenLabs] → Import script "black_woman_story.txt"
               ↓
[Generate] → Create chunks → Merge
             ↓
[Output] → D:\Black woman\voice\black_woman_story.mp3 ✅
```

**Logs sẽ hiển thị:**
```
📁 Determining output path...
   ✅ Using project voice folder: D:\Black woman\voice
   📄 Script name: black_woman_story
   🎵 Output file: D:\Black woman\voice\black_woman_story.mp3
```

---

### **Kịch bản 2: Không có project (legacy mode)**

```
[User] → Import script from "D:\Scripts\story.txt"
         ↓
[ElevenLabs] → Generate chunks → Merge
               ↓
[Output] → D:\Scripts\story.mp3 ✅
```

**Logs:**
```
📁 Determining output path...
   📁 Using TXT folder: D:\Scripts
   📄 Script name: story
   🎵 Output file: D:\Scripts\story.mp3
```

---

### **Kịch bản 3: Fallback (không có thông tin gì)**

```
[User] → Paste text directly (no file)
         ↓
[ElevenLabs] → Generate chunks → Merge
               ↓
[Output] → C:/TotalTool/output/merged_20251106_150316.mp3
```

**Logs:**
```
📁 Determining output path...
   ⚠️ No project/script path - using fallback
   📁 Fallback folder: C:/TotalTool/output
   🎵 Output file: C:/TotalTool/output/merged_20251106_150316.mp3
```

---

## 📋 **Ví Dụ Thực Tế:**

### **Trước khi sửa:**

```bash
# User import script "black_woman_story.txt"
# Auto workflow tạo folders:
D:\Black woman\
├─ voice\       ← EMPTY! File không được lưu vào đây
├─ image\
└─ video\

# File được lưu SAI CHỖ:
C:\TotalTool\output\merged_20251106_150316.mp3  ❌
```

### **Sau khi sửa:**

```bash
# User chọn project "Black woman"
# User import script "black_woman_story.txt"
# Generate → Merge

# File được lưu ĐÚNG CHỖ:
D:\Black woman\
├─ voice\
│  └─ black_woman_story.mp3  ✅ ← Lưu vào đây!
├─ image\
└─ video\
```

**Tên file:** `black_woman_story.mp3` (theo tên script) ✅

---

## ✅ **Files Đã Sửa:**

1. **`ElevenlabsV15.py`:**
   - Line 790: Thêm `project_manager` parameter
   - Line 800: Store `self.project_manager`
   - Line 3537-3577: Logic mới cho output path (3 priorities)

2. **`GenVideoPro.py`:**
   - Line 6947: Pass `project_manager` vào `ElevenLabsGUI`

---

## 🧪 **Test Scenarios:**

### **Test 1: Với Project**
```
1. Chọn project "Black woman"
2. Import script "story.txt"
3. Generate audio
4. Kiểm tra: D:\Black woman\voice\story.mp3 ✅
```

### **Test 2: Không có Project**
```
1. Import script từ "D:\Scripts\test.txt"
2. Generate audio
3. Kiểm tra: D:\Scripts\test.mp3 ✅
```

### **Test 3: Paste Text**
```
1. Paste text trực tiếp (no file)
2. Generate audio
3. Kiểm tra: C:/TotalTool/output/merged_timestamp.mp3 ✅
```

---

## 📊 **Ưu tiên lưu file:**

| Priority | Điều kiện | Output Path | Tên File |
|----------|-----------|-------------|----------|
| **1 (Cao nhất)** | Có project được chọn | `{project.voice_output}` | `{script_name}.mp3` |
| **2 (Trung bình)** | Có import TXT file | `{txt_folder}` | `{script_name}.mp3` |
| **3 (Fallback)** | Không có gì | `C:/TotalTool/output` | `merged_{timestamp}.mp3` |

---

## 🎯 **Kết Quả:**

**TRƯỚC:**
```
❌ File: C:/TotalTool/output/merged_20251106_150316.mp3
❌ Tên: merged_timestamp (không rõ ràng)
❌ Vị trí: Sai folder
```

**SAU:**
```
✅ File: D:\Black woman\voice\black_woman_story.mp3
✅ Tên: Theo script name (rõ ràng)
✅ Vị trí: Đúng project voice folder
```

---

## 🔗 **Related:**

- Auto Workflow tự động tạo folders:
  - `{project_root}\voice\`
  - `{project_root}\image\`
  - `{project_root}\video\`
  
- File audio sẽ tự động lưu vào folder `voice` của project

---

**Perfect! Bây giờ file được lưu đúng chỗ và đúng tên!** ✅🎵



