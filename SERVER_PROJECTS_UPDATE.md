# 📡 Server Projects - Updates

## Thay Đổi Mới

### 1. ✅ Sửa Lỗi `save()` Method

**Vấn đề:**
```python
AttributeError: 'ProjectManager' object has no attribute 'save'
```

**Nguyên nhân:**
- Method đúng là `save_projects()` không phải `save()`

**Đã sửa:**
- Bỏ hoàn toàn việc lưu local
- Projects luôn load fresh từ server

### 2. ✅ Projects Hoàn Toàn Từ Server

**Trước:**
```python
# Load from server + merge with local + save to local file
for server_project in projects:
    # Check if exists locally
    # Update or add
    # ...
self.project_manager.save()  # Save to local file
```

**Sau:**
```python
# Always load fresh from server, no local storage
self.project_manager.projects.clear()
for server_project in projects:
    # Add to memory only
    self.project_manager.projects.append(local_project)
# No save() - always fetch from server
```

**Lợi ích:**
- ✅ Luôn có data mới nhất từ server
- ✅ Không conflict giữa local và server
- ✅ Multi-user friendly
- ✅ Đơn giản hơn

### 3. ✅ UI Đơn Giản - Chỉ Hiện Tên Project

**Trước:**
```
┌──────────┬──────────────┬─────────────┬─────────┬──────────────┬──────────────┐
│ Select   │ Project Name │ Description │ Created │ Video Output │ Voice Output │
├──────────┼──────────────┼─────────────┼─────────┼──────────────┼──────────────┤
│ ✓ Select │ My Project   │ Template... │ 2025... │ C:\...       │ C:\...       │
└──────────┴──────────────┴─────────────┴─────────┴──────────────┴──────────────┘
```

**Sau:**
```
┌──────────┬────────────────────────────────────┐
│ Select   │ Project Name                       │
├──────────┼────────────────────────────────────┤
│ ✓ Select │ My Project                         │
│ ✓ Select │ Another Project                    │
│ ✓ Select │ Test Channel                       │
└──────────┴────────────────────────────────────┘
```

**Thay đổi:**
- ❌ Bỏ: Description, Created, Video Output, Voice Output
- ✅ Giữ: Select button + Project Name
- ✅ Font lớn hơn, bold cho tên project
- ✅ Giao diện clean, dễ nhìn

**Code:**
```python
# Table setup
self.table_projects.setColumnCount(2)  # Only 2 columns
self.table_projects.setHorizontalHeaderLabels([
    "Select", "Project Name"
])
self.table_projects.setColumnWidth(0, 120)  # Select button width

# Display
name_item = QTableWidgetItem(project.name)
font = name_item.font()
font.setPointSize(11)
font.setBold(True)
name_item.setFont(font)
```

### 4. ✅ Phân Quyền Admin/User (Đã Có)

**Admin thấy:**
- ➕ New Project
- ✏️ Edit Project
- 🗑️ Delete Project
- 📜 Import Script
- 🔄 Refresh

**User thấy:**
- 📜 Import Script
- 🔄 Refresh

*(Nút New/Edit/Delete bị ẩn)*

---

## Workflow Flow

### Load Projects từ Server

```
User clicks "☁️ Load Projects from Server"
    ↓
Check authentication
    ↓
Fetch projects from API: GET /api/tool/projects
    ↓
Clear local projects list
    ↓
Add all server projects to memory
    ↓
Refresh UI (show in table)
    ↓
No local save - always fresh from server
```

### Select & Use Project

```
User clicks "✓ Select" on a project
    ↓
Set as current project
    ↓
User clicks "📜 Import Script"
    ↓
Choose script.txt file
    ↓
Create folders at script location:
    [script_location]/
        ├─ script.txt
        ├─ voice/
        ├─ image/
        └─ video/
    ↓
Auto workflow starts...
```

---

## API Integration

### Endpoint: `/api/tool/projects`

**Request:**
```http
GET /api/tool/projects
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "projects": [
    {
      "project_id": "uuid-here",
      "channel_name": "My Channel",
      "script_template": "System prompt...",
      "num_prompts": 15,
      "voice_id": "voice_id_here",
      "auto_workflow": true
    }
  ]
}
```

### Data Mapping

**Server → Local:**
```python
Project(
    id=server['project_id'],
    name=server['channel_name'],
    description=server['script_template'],
    video_output="",  # Set when importing script
    voice_output="",  # Set when importing script
    image_output="",  # Set when importing script
    channel_name=server['channel_name'],
    script_template=server['script_template'],
    num_prompts=server['num_prompts'],  # Ignored, random 12-20
    voice_id=server['voice_id'],
    auto_workflow=server['auto_workflow']
)
```

---

## UI Screenshots

### Before (6 columns):
```
[Select] [Name] [Description] [Created] [Video] [Voice]
  Too much information, cluttered
```

### After (2 columns):
```
[Select] [Project Name                    ]
  Clean, simple, easy to read
```

---

## Benefits

### 1. Always Fresh Data
- ✅ No stale local data
- ✅ Changes from admin panel immediately visible
- ✅ Multi-user safe

### 2. Simpler UI
- ✅ Less clutter
- ✅ Focus on what matters (project name)
- ✅ Easier to select

### 3. No Sync Issues
- ✅ No local vs server conflicts
- ✅ No need to "sync"
- ✅ Single source of truth (server)

### 4. Better UX
- ✅ Larger, bolder text
- ✅ More space for project names
- ✅ Cleaner look

---

## Testing

### Test Load Projects:
1. Login to tool
2. Click "☁️ Load Projects from Server"
3. ✅ Projects appear in table
4. ✅ Only 2 columns shown
5. ✅ No error about `save()`

### Test Select Project:
1. Click "✓ Select" on a project
2. ✅ Current project updates
3. Click "📜 Import Script"
4. ✅ Workflow starts

### Test Admin vs User:
1. **Admin login:**
   - ✅ See New/Edit/Delete buttons
2. **User login:**
   - ✅ Only see Import Script and Refresh
   - ❌ New/Edit/Delete hidden

---

## Files Changed

1. ✅ `GenVideoPro.py`:
   - Fixed `on_load_projects_from_server()` - removed `save()`
   - Changed to always load from server
   - Simplified table to 2 columns
   - Updated `refresh_project_list()` for simple view

---

## Notes

- ⚠️ Projects NOT saved locally anymore
- ✅ Always fetch fresh from server
- ✅ UI simplified to 2 columns
- ✅ Admin/User permissions working
- ✅ Random 12-20 prompts (ignore server setting)

---

## Migration

**Old behavior:**
- Projects saved to `C:\WorkFlow\settings\projects.json`
- Merged with server data

**New behavior:**
- No local file
- Always load from server
- Memory only (cleared on restart)

**Impact:**
- ✅ Old local projects ignored
- ✅ Must load from server each time
- ✅ No migration needed

---

**Updated:** 2025-11-01
**Version:** 2.3
**Status:** ✅ COMPLETE

