# 🌐 Server CRUD Operations - Complete

## Tổng Quan

Tất cả operations Create/Update/Delete projects giờ tác động lên **server** thông qua API, không còn lưu local nữa.

---

## API Methods (tool_api_client.py)

### 1. ✅ Create Project
```python
def create_project(self, project_data: Dict) -> Optional[Dict]:
    """
    POST /api/tool/projects
    
    Args:
        project_data: {
            "channel_name": str,
            "script_template": str,
            "num_prompts": int,
            "voice_id": str,
            "auto_workflow": bool
        }
    
    Returns:
        Created project dict or None
    """
```

### 2. ✅ Update Project
```python
def update_project(self, project_id: str, project_data: Dict) -> bool:
    """
    PUT /api/tool/projects/{project_id}
    
    Args:
        project_id: Project UUID
        project_data: Fields to update
    
    Returns:
        True if successful
    """
```

### 3. ✅ Delete Project
```python
def delete_project(self, project_id: str) -> bool:
    """
    DELETE /api/tool/projects/{project_id}
    
    Args:
        project_id: Project UUID
    
    Returns:
        True if successful
    """
```

---

## Tool Operations (GenVideoPro.py)

### 1. ✅ Create Project (on_new_project)

**Flow:**
```
User clicks "➕ New Project"
    ↓
Check authentication
    ↓
Show ProjectDialog
    ↓
User fills: Name, Description, Num Prompts, Voice ID
    ↓
Call API: create_project(project_data)
    ↓
If success:
    - Reload projects from server
    - Show success message
```

**Code:**
```python
def on_new_project(self):
    # Check auth
    if not self.api_client.is_authenticated():
        return
    
    # Show dialog
    dialog = ProjectDialog(self, voice_list=voice_list)
    if dialog.exec():
        data = dialog.get_all_values()
        
        # Create on server
        project_data = {
            "channel_name": data["name"],
            "script_template": data["description"],
            "num_prompts": data["num_prompts"],
            "voice_id": data.get("voice_id", ""),
            "auto_workflow": True
        }
        
        created_project = self.api_client.create_project(project_data)
        
        if created_project:
            self.on_load_projects_from_server()  # Reload
            QMessageBox.information(...)
```

### 2. ✅ Update Project (on_edit_project)

**Flow:**
```
User selects project in table
    ↓
User clicks "✏️ Edit Project"
    ↓
Check authentication
    ↓
Show ProjectDialog with pre-filled data
    ↓
User edits fields
    ↓
Call API: update_project(project_id, project_data)
    ↓
If success:
    - Reload projects from server
    - Show success message
```

**Code:**
```python
def on_edit_project(self):
    # Check auth
    if not self.api_client.is_authenticated():
        return
    
    # Get selected project
    project = ...
    
    # Show dialog with pre-filled data
    dialog = ProjectDialog(self, project.name, project.description, ...)
    if dialog.exec():
        data = dialog.get_all_values()
        
        # Update on server
        project_data = {...}
        success = self.api_client.update_project(project.id, project_data)
        
        if success:
            self.on_load_projects_from_server()  # Reload
            QMessageBox.information(...)
```

### 3. ✅ Delete Project (on_delete_project)

**Flow:**
```
User selects project in table
    ↓
User clicks "🗑️ Delete Project"
    ↓
Check authentication
    ↓
Show confirmation dialog
    ↓
User confirms
    ↓
Call API: delete_project(project_id)
    ↓
If success:
    - Reload projects from server
    - Show success message
```

**Code:**
```python
def on_delete_project(self):
    # Check auth
    if not self.api_client.is_authenticated():
        return
    
    # Get selected project
    project = ...
    
    # Confirm
    reply = QMessageBox.question(
        self, "Confirm Delete",
        f"⚠️ Are you sure you want to delete '{project_name}'?\n\n"
        "This will delete the project from the server permanently!",
        ...
    )
    
    if reply == QMessageBox.Yes:
        # Delete from server
        success = self.api_client.delete_project(project.id)
        
        if success:
            self.on_load_projects_from_server()  # Reload
            QMessageBox.information(...)
```

---

## API Endpoints Required

### Admin Panel API Routes

#### 1. POST /api/tool/projects
**Create new project**

Request:
```json
{
  "channel_name": "My Channel",
  "script_template": "System prompt...",
  "num_prompts": 15,
  "voice_id": "voice_id_here",
  "auto_workflow": true
}
```

Response:
```json
{
  "success": true,
  "project": {
    "project_id": "uuid-here",
    "channel_name": "My Channel",
    ...
  }
}
```

#### 2. PUT /api/tool/projects/{project_id}
**Update existing project**

Request:
```json
{
  "channel_name": "Updated Name",
  "script_template": "Updated prompt...",
  "num_prompts": 20,
  "voice_id": "new_voice_id",
  "auto_workflow": true
}
```

Response:
```json
{
  "success": true
}
```

#### 3. DELETE /api/tool/projects/{project_id}
**Delete project**

Response:
```json
{
  "success": true
}
```

---

## Benefits

### 1. Single Source of Truth
- ✅ Server is the only source
- ✅ No local vs server conflicts
- ✅ Always up-to-date

### 2. Multi-User Safe
- ✅ Changes visible to all users
- ✅ No sync issues
- ✅ Real-time updates

### 3. Admin Control
- ✅ All changes tracked on server
- ✅ Can audit who created/modified what
- ✅ Centralized management

### 4. Simpler Code
- ✅ No local file management
- ✅ No sync logic needed
- ✅ Just API calls

---

## User Experience

### Admin User:
1. **Create:**
   - Click "➕ New Project"
   - Fill form
   - ✅ Created on server
   - List refreshes automatically

2. **Edit:**
   - Select project
   - Click "✏️ Edit Project"
   - Modify fields
   - ✅ Updated on server
   - List refreshes automatically

3. **Delete:**
   - Select project
   - Click "🗑️ Delete Project"
   - Confirm
   - ✅ Deleted from server
   - List refreshes automatically

### Regular User:
- ❌ Cannot see Create/Edit/Delete buttons
- ✅ Can only view and select projects
- ✅ Can import scripts and use projects

---

## Error Handling

### Not Authenticated:
```
⚠️ Please login first!
```

### API Error:
```
❌ Failed to create/update/delete project.
Check console for details.
```

### Network Error:
```
❌ API Error: Connection timeout
```

---

## Testing

### Test Create:
1. Login as admin
2. Click "➕ New Project"
3. Fill: Name, Description, Num Prompts, Voice
4. Submit
5. ✅ Check project appears in list
6. ✅ Check project exists in admin panel web UI

### Test Update:
1. Select existing project
2. Click "✏️ Edit Project"
3. Change name/description
4. Submit
5. ✅ Check changes reflected in list
6. ✅ Check changes in admin panel web UI

### Test Delete:
1. Select project
2. Click "🗑️ Delete Project"
3. Confirm
4. ✅ Check project removed from list
5. ✅ Check project deleted in admin panel web UI

### Test Permissions:
1. Login as regular user
2. ✅ New/Edit/Delete buttons hidden
3. ✅ Can only view and select

---

## Files Changed

1. ✅ `tool_api_client.py`:
   - Added `create_project()`
   - Added `update_project()`
   - Added `delete_project()`

2. ✅ `GenVideoPro.py`:
   - Updated `on_new_project()` - call API
   - Updated `on_edit_project()` - call API
   - Updated `on_delete_project()` - call API
   - All reload from server after changes

---

## Migration Notes

**Old Behavior:**
- Projects saved to local `projects.json`
- Changes only local

**New Behavior:**
- All operations via API
- Changes on server
- No local storage

**Impact:**
- ✅ Old local projects ignored
- ✅ Must use server
- ✅ Must be authenticated

---

## Next Steps (Optional)

### Future Enhancements:
- [ ] Optimistic UI updates (update UI before API response)
- [ ] Undo/Redo support
- [ ] Batch operations
- [ ] Project templates
- [ ] Import/Export projects
- [ ] Project sharing between users

---

**Updated:** 2025-11-01
**Version:** 2.4
**Status:** ✅ COMPLETE

**All CRUD operations now work with server!** 🎉

