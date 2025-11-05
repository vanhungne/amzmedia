# 🚀 Auto Workflow - Implementation Guide

## ✅ Completed So Far:

1. **auto_workflow.py** - Complete orchestrator module ✅
2. **Project class** - Updated with channel settings ✅  
3. **Plan** - Full architecture in AUTO_WORKFLOW_PLAN.md ✅

---

## 📝 Remaining Steps (Copy-Paste Ready):

### Step 1: Import orchestrator in GenVideoPro.py

**Add at top of file (line ~30):**
```python
# Import auto workflow orchestrator
try:
    from auto_workflow import AutoWorkflowOrchestrator
    AUTO_WORKFLOW_AVAILABLE = True
except Exception as e:
    print(f"Auto workflow not available: {e}")
    AUTO_WORKFLOW_AVAILABLE = False
```

---

### Step 2: Initialize orchestrator in MainWindow.__init__

**Add after line 3787 (`self.project_manager = ProjectManager(PROJECTS_FILE)`):**
```python
# Initialize Auto Workflow Orchestrator
if AUTO_WORKFLOW_AVAILABLE:
    self.orchestrator = AutoWorkflowOrchestrator(self)
else:
    self.orchestrator = None
```

---

### Step 3: Store image_generator_widget reference

**In `setup_image_generator_tab()` method, add after creating widget:**
```python
def setup_image_generator_tab(self):
    """Setup Image Generator tab - MODIFIED"""
    if IMAGE_TAB_AVAILABLE:
        try:
            from image_tab_full import ImageGeneratorTab
            self.image_generator_widget = ImageGeneratorTab(self)  # ← STORE REFERENCE
            
            layout = QVBoxLayout(self.tab_image_generator)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.image_generator_widget)
        except Exception as e:
            # ... existing error handling ...
```

---

### Step 4: Add "Import Script" button to Project tab

**In `setup_project_tab()`, add button BEFORE `btn_refresh`:**
```python
# Around line 4754, BEFORE btn_refresh
btn_import_script = QPushButton("📜 Import Script & Auto Generate")
btn_import_script.setStyleSheet("""
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #8b5cf6, stop:1 #7c3aed);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: bold;
        font-size: 11pt;
        min-height: 40px;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #a78bfa, stop:1 #8b5cf6);
    }
""")
btn_import_script.clicked.connect(self.on_import_script_auto)
btn_layout.addWidget(btn_import_script)
```

---

### Step 5: Add handler method for Import Script

**Add this method to MainWindow class:**
```python
def on_import_script_auto(self):
    """Handle Import Script button - Start auto workflow"""
    if not AUTO_WORKFLOW_AVAILABLE:
        QMessageBox.warning(
            self, 
            "Feature Not Available",
            "Auto workflow is not available. Check console for errors."
        )
        return
    
    # Check if project is selected
    if not self.project_manager.current_project:
        QMessageBox.warning(
            self,
            "No Project Selected",
            "Please select a project first!\n\n"
            "1. Create a new project\n"
            "2. Or select an existing project from the table\n"
            "3. Then click 'Import Script'"
        )
        return
    
    project = self.project_manager.current_project
    
    # Validate project settings
    if not project.num_prompts or project.num_prompts < 1:
        QMessageBox.warning(
            self,
            "Project Not Configured",
            "Please configure project settings first!\n\n"
            "Edit project and set:\n"
            "• Number of prompts\n"
            "• Voice ID (optional)\n"
            "• Script template (optional)"
        )
        return
    
    # File dialog to select script
    from PySide6.QtWidgets import QFileDialog
    script_path, _ = QFileDialog.getOpenFileName(
        self,
        "Select Script File for Auto Workflow",
        "",
        "Text files (*.txt);;All files (*.*)"
    )
    
    if not script_path:
        return
    
    # Confirm
    reply = QMessageBox.question(
        self,
        "Start Auto Workflow?",
        f"📁 Project: {project.name}\n"
        f"📜 Script: {os.path.basename(script_path)}\n"
        f"🎨 Images: {project.num_prompts} prompts\n\n"
        f"This will automatically:\n"
        f"1. Create folder structure\n"
        f"2. Parse script with Groq AI\n"
        f"3. Generate {project.num_prompts} images\n\n"
        f"Continue?",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.Yes
    )
    
    if reply == QMessageBox.Yes:
        # Start auto workflow
        self.orchestrator.start_workflow(project, script_path)
```

---

### Step 6: Update ProjectDialog to support channel settings

**Replace entire ProjectDialog class with this enhanced version:**

```python
class ProjectDialog(QDialog):
    """Dialog for creating/editing projects with channel automation settings"""
    def __init__(self, parent=None, project: Optional[Project] = None):
        super().__init__(parent)
        self.project = project  # For editing
        self.setWindowTitle("New Project" if not project else "Edit Project")
        self.setMinimumWidth(700)
        self.setMinimumHeight(750)
        
        # ... (stylesheet - keep existing) ...
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("📁 " + ("New Project" if not project else "Edit Project"))
        title.setStyleSheet("""
            font-size: 16pt;
            font-weight: bold;
            color: #F87B1B;
            margin-bottom: 8px;
        """)
        layout.addWidget(title)
        
        # Scroll area for form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(12)
        
        # === BASIC INFO ===
        basic_label = QLabel("📝 Basic Information")
        basic_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #F87B1B;")
        form_layout.addWidget(basic_label)
        
        # Project name
        form_layout.addWidget(QLabel("Project Name *"))
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Enter project name...")
        if project:
            self.txt_name.setText(project.name)
        form_layout.addWidget(self.txt_name)
        
        # Description
        form_layout.addWidget(QLabel("Description"))
        self.txt_desc = QTextEdit()
        self.txt_desc.setMaximumHeight(80)
        self.txt_desc.setPlaceholderText("Optional description...")
        if project:
            self.txt_desc.setPlainText(project.description)
        form_layout.addWidget(self.txt_desc)
        
        # Separator
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setStyleSheet("background-color: #d1d9e6;")
        form_layout.addWidget(line1)
        
        # === CHANNEL SETTINGS ===
        channel_label = QLabel("📺 Channel Automation Settings")
        channel_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #F87B1B;")
        form_layout.addWidget(channel_label)
        
        # Channel name
        form_layout.addWidget(QLabel("Channel Name"))
        self.txt_channel_name = QLineEdit()
        self.txt_channel_name.setPlaceholderText("e.g., My Cooking Channel")
        if project:
            self.txt_channel_name.setText(project.channel_name)
        form_layout.addWidget(self.txt_channel_name)
        
        # Number of prompts
        form_layout.addWidget(QLabel("Number of Prompts to Generate"))
        self.spin_num_prompts = QSpinBox()
        self.spin_num_prompts.setRange(1, 50)
        self.spin_num_prompts.setValue(project.num_prompts if project else 5)
        form_layout.addWidget(self.spin_num_prompts)
        
        # Voice ID
        form_layout.addWidget(QLabel("Voice ID (ElevenLabs)"))
        self.txt_voice_id = QLineEdit()
        self.txt_voice_id.setPlaceholderText("Optional: e.g., adam, rachel, etc.")
        if project:
            self.txt_voice_id.setText(project.voice_id)
        form_layout.addWidget(self.txt_voice_id)
        
        # Script template
        form_layout.addWidget(QLabel("Custom Script Template (Groq System Prompt)"))
        info_template = QLabel("💡 Leave empty to use default template. Use {x} for number of parts.")
        info_template.setStyleSheet("color: #6b7280; font-size: 9pt;")
        form_layout.addWidget(info_template)
        
        self.txt_script_template = QTextEdit()
        self.txt_script_template.setMaximumHeight(150)
        self.txt_script_template.setPlaceholderText(
            "Optional: Custom system prompt for Groq AI...\n"
            "Example: You are analyzing cooking scripts. Create {x} image prompts..."
        )
        if project:
            self.txt_script_template.setPlainText(project.script_template)
        form_layout.addWidget(self.txt_script_template)
        
        # Auto workflow checkbox
        self.chk_auto_workflow = QCheckBox("✅ Enable Auto Workflow")
        self.chk_auto_workflow.setChecked(project.auto_workflow if project else True)
        self.chk_auto_workflow.setStyleSheet("font-weight: 600;")
        form_layout.addWidget(self.chk_auto_workflow)
        
        form_layout.addStretch()
        scroll.setWidget(form_widget)
        layout.addWidget(scroll)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #94a3b8, stop:1 #64748b);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 25px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #cbd5e1, stop:1 #94a3b8);
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        btn_save = QPushButton("Save" if project else "Create")
        btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF8C2E, stop:1 #F87B1B);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 25px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFA04D, stop:1 #FF8C2E);
            }
        """)
        btn_save.clicked.connect(self.accept)
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
        
        self.txt_name.setFocus()
    
    def get_project_data(self) -> dict:
        """Get all project data including channel settings"""
        return {
            "name": self.txt_name.text().strip(),
            "description": self.txt_desc.toPlainText().strip(),
            "channel_name": self.txt_channel_name.text().strip(),
            "num_prompts": self.spin_num_prompts.value(),
            "voice_id": self.txt_voice_id.text().strip(),
            "script_template": self.txt_script_template.toPlainText().strip(),
            "auto_workflow": self.chk_auto_workflow.isChecked()
        }
    
    def accept(self):
        """Validate before accepting"""
        if not self.txt_name.text().strip():
            QMessageBox.warning(self, "Validation Error", "Project name is required!")
            return
        super().accept()
```

---

### Step 7: Update on_new_project() and on_edit_project()

**Replace existing methods:**
```python
def on_new_project(self):
    """Create new project with channel settings"""
    dialog = ProjectDialog(self)
    if dialog.exec() == QDialog.Accepted:
        data = dialog.get_project_data()
        
        project = Project(
            id=str(uuid.uuid4()),
            name=data["name"],
            description=data["description"],
            created_at=datetime.now(timezone.utc).isoformat(),
            channel_name=data["channel_name"],
            num_prompts=data["num_prompts"],
            voice_id=data["voice_id"],
            script_template=data["script_template"],
            auto_workflow=data["auto_workflow"]
        )
        
        self.project_manager.create_project(project)
        self.refresh_project_list()
        QMessageBox.information(self, "Success", f"Project '{project.name}' created successfully!")

def on_edit_project(self):
    """Edit existing project"""
    if not self.project_manager.current_project:
        QMessageBox.warning(self, "No Selection", "Please select a project to edit!")
        return
    
    project = self.project_manager.current_project
    dialog = ProjectDialog(self, project)
    
    if dialog.exec() == QDialog.Accepted:
        data = dialog.get_project_data()
        
        # Update project
        project.name = data["name"]
        project.description = data["description"]
        project.channel_name = data["channel_name"]
        project.num_prompts = data["num_prompts"]
        project.voice_id = data["voice_id"]
        project.script_template = data["script_template"]
        project.auto_workflow = data["auto_workflow"]
        
        self.project_manager.update_project(project)
        self.refresh_project_list()
        QMessageBox.information(self, "Success", f"Project '{project.name}' updated!")
```

---

## 🎯 Testing Steps:

1. **Restart app**
2. **Go to Project tab**
3. **Create new project:**
   - Name: "Test Channel"
   - Channel Name: "My Test Channel"
   - Num Prompts: 5
   - Leave others empty for now
4. **Click "Import Script"**
5. **Select example_script.txt**
6. **Watch automation:**
   - Progress dialog shows
   - Folder created: `C:\WorkFlow\Test Channel\`
   - Images start generating

---

## 📁 Expected Result:

```
C:\WorkFlow\
└─ Test Channel\
    ├─ script.txt (copied)
    ├─ voice\ (empty for now)
    ├─ image\
    │   ├─ 01_001.png
    │   ├─ 01_002.png
    │   └─ ... (5 prompts × 4 images each)
    └─ video\ (empty)
```

---

## 🐛 Troubleshooting:

### Error: "Auto workflow not available"
→ Check console for import errors
→ Make sure `auto_workflow.py` is in same folder

### Error: "No Groq API keys"
→ Go to Settings tab
→ Add Groq keys
→ Save settings

### Images don't generate
→ Check Image Generator tab manually
→ Prompts should be in queue
→ Click "Run All" if needed

---

## 🚀 Next Features (Future):

- Voice integration (auto generate voice first)
- Progress tracking with estimated time
- Resume on failure
- Batch processing multiple scripts
- Export final video

---

**Implementation Time: ~30 minutes** (copy-paste all snippets)
**File Changes: GenVideoPro.py** (7 locations)
**New Files: auto_workflow.py** ✅ Already created

Ready to implement! 🎬




