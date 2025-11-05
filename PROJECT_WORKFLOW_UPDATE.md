# 📋 Project Workflow - Updates

## Thay Đổi Mới

### 1. ✅ Sửa Lỗi Load Projects từ Server

**Vấn đề:**
```python
TypeError: Project.__init__() got an unexpected keyword argument 'video_output_folder'
```

**Nguyên nhân:**
- Field `video_output_folder` không tồn tại trong Project class
- Đúng phải là: `video_output`, `voice_output`, `image_output`

**Đã sửa:**
```python
local_project = Project(
    id=server_project['project_id'],
    name=server_project['channel_name'],
    description=server_project['script_template'] or "",
    video_output="",  # Will be set when importing script
    voice_output="",  # Will be set when importing script
    image_output="",  # Will be set when importing script
    channel_name=server_project['channel_name'],
    script_template=server_project['script_template'],
    num_prompts=server_project['num_prompts'],
    voice_id=server_project['voice_id'],
    auto_workflow=server_project['auto_workflow']
)
```

### 2. ✅ Thay Đổi Logic Folder Output

**Trước:**
```
C:\WorkFlow\
  ├─ video\[channel_name]\
  ├─ voice\[channel_name]\
  └─ image\[channel_name]\
```

**Sau:**
```
[Script Location]\
  ├─ script.txt
  ├─ voice\
  ├─ image\
  └─ video\
```

**Lợi ích:**
- ✅ Tất cả files liên quan ở cùng 1 nơi
- ✅ Dễ quản lý và backup
- ✅ Không cần tạo folder trước

**Code:**
```python
def create_folder_structure(self) -> Path:
    # Base directory = script location
    base_dir = Path(self.script_path).parent
    
    # Subdirectories
    voice_dir = base_dir / "voice"
    image_dir = base_dir / "image"
    video_dir = base_dir / "video"
    
    voice_dir.mkdir(exist_ok=True)
    image_dir.mkdir(exist_ok=True)
    video_dir.mkdir(exist_ok=True)
    
    # Update project paths
    self.project.voice_output = str(voice_dir)
    self.project.image_output = str(image_dir)
    self.project.video_output = str(video_dir)
```

### 3. ✅ Random Number of Prompts

**Trước:**
- Sử dụng `num_prompts` từ admin panel (cố định)
- Range: 12-24

**Sau:**
- Random mỗi lần chạy
- Range: **12-20** (giảm từ 12-24)

**Code:**
```python
# Random num_prompts from 12 to 20 (changed from 12-24)
import random
num_prompts = random.randint(12, 20)
print(f"[AUTO WORKFLOW] Random num_prompts: {num_prompts} (range: 12-20)")
```

**Lợi ích:**
- ✅ Đa dạng hơn mỗi lần chạy
- ✅ Không phụ thuộc vào admin setting
- ✅ Range hợp lý hơn (12-20 thay vì 12-24)

---

## Workflow Flow

### 1. Load Project từ Server
```
User clicks "Load Projects from Server"
    ↓
Fetch projects from Admin Panel API
    ↓
Convert to local Project objects
    ↓
Save to local projects.json
    ↓
Display in project list
```

### 2. Import Script & Auto Workflow
```
User selects project
    ↓
User clicks "Import Script"
    ↓
Select script.txt file
    ↓
Create folder structure at script location:
    [script_location]/
        ├─ script.txt
        ├─ voice/
        ├─ image/
        └─ video/
    ↓
Parse script with Groq AI (random 12-20 prompts)
    ↓
Generate voice (if voice_id set)
    ↓
Generate images
    ↓
Done!
```

---

## Example

### Ví dụ: Import Script

**Script location:**
```
D:\Projects\MyVideo\script.txt
```

**Folders created:**
```
D:\Projects\MyVideo\
  ├─ script.txt          (imported file)
  ├─ voice\              (voice files here)
  ├─ image\              (image files here)
  └─ video\              (video files here)
```

**Prompts generated:**
- Random: 15 prompts (between 12-20)
- Not fixed from admin panel

---

## Testing

### Test Load Projects:
1. Đăng nhập tool
2. Click "Load Projects from Server"
3. Kiểm tra projects hiển thị
4. ✅ Không có lỗi `video_output_folder`

### Test Import Script:
1. Select project
2. Click "Import Script"
3. Choose script.txt
4. Kiểm tra folders được tạo cùng cấp script
5. Kiểm tra số prompts random 12-20

---

## Files Changed

1. ✅ `GenVideoPro.py` - Fixed `on_load_projects_from_server()`
2. ✅ `auto_workflow.py` - Changed random range to 12-20

---

## Notes

- ⚠️ `num_prompts` từ admin panel giờ bị ignore
- ✅ Mỗi lần import script sẽ random 12-20 prompts
- ✅ Folders luôn tạo cùng cấp với script
- ✅ Không cần setup folders trước

---

**Updated:** 2025-11-01
**Version:** 2.2
**Status:** ✅ FIXED

