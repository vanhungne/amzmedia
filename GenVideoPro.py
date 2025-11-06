#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os, re, time, json, base64, unicodedata, shutil, subprocess, gc
import hashlib, uuid
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from functools import partial
from PySide6.QtCore import Qt, QThreadPool, QRunnable, Signal, QObject, QSize, QTimer,QEvent, QRect   
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QFileDialog, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QStyle, QAbstractItemView, QButtonGroup,
    QRadioButton, QFrame, QSpinBox, QCheckBox, QLineEdit, QProgressBar,
    QTextEdit, QPlainTextEdit, QStackedLayout, QMenu,  QSizePolicy, QComboBox, QTableWidget, QScrollArea
)
from PySide6.QtGui import QAction, QKeySequence, QPixmap, QPainter, QPen, QColor, QLinearGradient
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from datetime import datetime, timezone
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout
# >>> NEW: deps cho AI prompt (Groq/OpenAI-compatible)
try:
    import requests
except Exception:
    requests = None  # fallback template nếu chưa cài requests

# >>> NEW: Import Image Generator Tab
try:
    from image_tab_full import ImageGeneratorTab
    IMAGE_TAB_AVAILABLE = True
except Exception:
    IMAGE_TAB_AVAILABLE = False

# >>> NEW: Import Auto Workflow Orchestrator
try:
    from auto_workflow import AutoWorkflowOrchestrator
    AUTO_WORKFLOW_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Auto workflow not available: {e}")
    AUTO_WORKFLOW_AVAILABLE = False

# >>> NEW: Import API Client for Admin Panel
try:
    from tool_api_client import WorkFlowAPIClient
    API_CLIENT_AVAILABLE = True
except Exception as e:
    print(f"⚠️ API Client not available: {e}")
    API_CLIENT_AVAILABLE = False

# >>> NEW: Import Login Dialog
try:
    from login_dialog import LoginDialog
    LOGIN_DIALOG_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Login Dialog not available: {e}")
    LOGIN_DIALOG_AVAILABLE = False

# ElevenLabs Audio Generation - Import toàn bộ GUI
try:
    from ElevenlabsV15 import ElevenLabsGUI
    ELEVENLABS_AVAILABLE = True
except Exception as e:
    print(f"ElevenLabs import error: {e}")
    ELEVENLABS_AVAILABLE = False

# cryptography (bắt buộc để verify)
try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
except Exception:
    hashes = serialization = padding = None

# ==== LICENSE PATHS ====
APP_LICENSE_DIR  = Path(r"C:\AppVeo\Settings")
APP_LICENSE_FILE = APP_LICENSE_DIR / "lience.txt"
PUBLIC_KEY_PEM = b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA8Sp6u0xiwQDdWlinmmbS
xvrjxmyYsIQf3IZjUg6BVrMTQTeY8dOlVmc+ro1d9/fOVt+TAklJv8WbQrjrU1pL
ACeWwPJoOXatzqDwZqXYzQmPnxOntOoeaDTh5IADUUK1q+rfeVNNByA6Hdg5+SQI
oU3LR/TT+GpSiKiYaCPBkGTd3Bax5lGs4eEsL+2wgbLvfOif9qEp0HbxYE9teB45
JyblSHCAaQD30YOzZm5hMkbOW8oGnGyZZe6KVT3AYo8xugORVu6YTfRrOty8FjDd
73pNTslBT25P725s/bPP305rp81+NIpXmuPzK4gZn8MVUt+A1KgwBGRhd/JHrDbj
DQIDAQAB
-----END PUBLIC KEY-----
"""
APP_DIR = Path(__file__).resolve().parent

# ==== NEW: WORKFLOW PROJECT MANAGEMENT ====
WORKFLOW_ROOT = Path(r"C:\WorkFlow")
WORKFLOW_SETTINGS = WORKFLOW_ROOT / "settings"
WORKFLOW_VIDEO = WORKFLOW_ROOT / "video"
WORKFLOW_VOICE = WORKFLOW_ROOT / "voice" 
WORKFLOW_IMAGE = WORKFLOW_ROOT / "image"
PROJECTS_FILE = WORKFLOW_SETTINGS / "projects.json"

# Ensure all directories exist
for dir_path in [WORKFLOW_ROOT, WORKFLOW_SETTINGS, WORKFLOW_VIDEO, WORKFLOW_VOICE, WORKFLOW_IMAGE]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ==== CLOUDINARY CONFIG (env or hardcode) ====
CLOUD_NAME   = os.getenv("CLOUDINARY_CLOUD_NAME", "dsihleioc")
UPLOAD_PRESET= os.getenv("CLOUDINARY_UPLOAD_PRESET", "")   # for unsigned
CLOUD_API_KEY= os.getenv("CLOUDINARY_API_KEY", "878254454332296")
CLOUD_SECRET = os.getenv("CLOUDINARY_API_SECRET", "3ozEXIzAYxTYK3J3rgwVXbX3aPU")
# Bảo đảm EXE tìm thấy ffmpeg và browsers của Playwright
os.environ["PATH"] = str(APP_DIR) + os.pathsep + os.environ.get("PATH", "")

# ============================== Playwright Browser Installer ===============================
def ensure_playwright_browsers_installed(show_dialog=False):
    """
    Kiểm tra và tự động cài đặt Playwright browsers nếu chưa có.
    Hàm này được gọi khi app khởi động để đảm bảo browsers luôn sẵn sàng.
    
    Args:
        show_dialog: Nếu True, hiển thị dialog box khi cài đặt (chỉ dùng khi GUI đã sẵn sàng)
    """
    try:
        # Thử import playwright
        from playwright.sync_api import sync_playwright
        
        # Thử khởi động chromium để kiểm tra
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                browser.close()
                print("[OK] Playwright browsers are ready!")
                return True
            except Exception as launch_error:
                print(f"[WARNING] Playwright browsers not found: {launch_error}")
                print("[INFO] Installing Playwright browsers...")
                
                # Hiển thị thông báo nếu có thể
                if show_dialog:
                    try:
                        from PySide6.QtWidgets import QMessageBox, QApplication
                        if QApplication.instance():
                            msg = QMessageBox()
                            msg.setIcon(QMessageBox.Information)
                            msg.setWindowTitle("First Time Setup")
                            msg.setText("Installing required browser components...\n\nThis will only happen once and may take a few minutes.\n\nPlease wait...")
                            msg.setStandardButtons(QMessageBox.NoButton)
                            msg.show()
                            QApplication.processEvents()
                    except:
                        pass
                
                # Cài đặt browsers
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "playwright", "install", "chromium"],
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minutes timeout
                    )
                    
                    if result.returncode == 0:
                        print("[OK] Playwright browsers installed successfully!")
                        
                        # Thông báo thành công
                        if show_dialog:
                            try:
                                from PySide6.QtWidgets import QMessageBox, QApplication
                                if QApplication.instance():
                                    QMessageBox.information(None, "Setup Complete", 
                                        "Browser components installed successfully!\n\nThe application is now ready to use.")
                            except:
                                pass
                        return True
                    else:
                        print(f"[ERROR] Failed to install browsers: {result.stderr}")
                        
                        # Thông báo lỗi
                        if show_dialog:
                            try:
                                from PySide6.QtWidgets import QMessageBox, QApplication
                                if QApplication.instance():
                                    QMessageBox.warning(None, "Setup Failed", 
                                        f"Failed to install browser components.\n\nPlease run:\nplaywright install\n\nError: {result.stderr}")
                            except:
                                pass
                        return False
                except subprocess.TimeoutExpired:
                    print("[ERROR] Browser installation timed out!")
                    return False
                except Exception as install_error:
                    print(f"[ERROR] Installation error: {install_error}")
                    return False
                    
    except ImportError:
        print("[WARNING] Playwright not installed!")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error checking Playwright: {e}")
        return False

# Khi chạy dạng đóng gói (PyInstaller), trỏ Playwright tới folder browsers đi kèm
try:
    # Thử nhiều vị trí có thể chứa browsers
    base = Path(getattr(sys, "_MEIPASS", APP_DIR))
    
    # Thứ tự ưu tiên tìm browsers:
    # 1. _internal/ms-playwright (PyInstaller bundle - trong folder dist)
    # 2. ms-playwright (PyInstaller bundle - trong temp _MEIPASS)
    # 3. _external/ms-playwright (manual copy - bên cạnh exe)
    
    possible_paths = [
        APP_DIR / "_internal" / "ms-playwright",   # Trong folder dist/_internal
        base / "ms-playwright",                     # Trong temp _MEIPASS
        APP_DIR / "_external" / "ms-playwright",   # Manual copy (fallback)
    ]
    
    for mp in possible_paths:
        if mp.exists():
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(mp)
            print(f"[OK] Found Playwright browsers at: {mp}")
            break
    else:
        print("[INFO] Playwright browsers not bundled, will download on first use")
        
except Exception as e:
    print(f"[WARNING] Error checking Playwright browsers: {e}")

# Kiểm tra Playwright browsers khi app khởi động (silent check, GUI dialog sẽ được gọi sau)
print("[INFO] Checking Playwright browsers...")
_playwright_ready = ensure_playwright_browsers_installed(show_dialog=False)
SETTINGS_FILE = APP_DIR / "vgp_settings.json"

# ============================== Cookie utils ===============================
def parse_netscape_cookie_file(path: str, domain_filter: Optional[str] = None) -> List[Dict]:
    cookies = []
    if not os.path.exists(path):
        return cookies
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 7:
                continue
            domain, include_sub, cpath, secure, expires, name, value = parts[:7]
            if domain_filter and (domain_filter not in domain):
                continue
            try:
                exp = int(expires)
            except:
                exp = 0
            cookie = {
                "name": name,
                "value": value,
                "domain": domain,
                "path": cpath or "/",
                "secure": (secure.upper() == "TRUE"),
            }
            if exp > 0:
                cookie["expires"] = float(exp)
            cookies.append(cookie)
    return cookies

# ============================== Helpers ===============================
# --- split helpers: mỗi block ngăn cách bởi 1 dòng trống trở lên ---
def _split_prompt_blocks(text: str) -> List[str]:
    if not text:
        return []
    # tách theo 1+ dòng trống, giữ nội dung trong block, gọn hoá xuống hàng nội bộ thành 1 space
    blocks = re.split(r"\r?\n\s*\r?\n", text.strip())
    out = []
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        # gọn hoá newline trong cùng block để AI đọc mạch lạc
        b = re.sub(r"[ \t]*\r?\n[ \t]*", " ", b)
        out.append(b)
    return out

def _normalize(s: str) -> str:
    return ''.join(ch for ch in unicodedata.normalize('NFKD', s) if not unicodedata.combining(ch)).lower()

def _b64url_decode(s: str) -> bytes:
    if isinstance(s, str): s = s.encode()
    return base64.urlsafe_b64decode(s + b'=' * (-len(s) % 4))

# ============================== PROJECT MANAGEMENT ===============================
@dataclass
class Project:
    """Project data class with channel automation settings"""
    id: str
    name: str
    description: str = ""
    created_at: str = ""
    video_output: str = ""
    voice_output: str = ""
    image_output: str = ""
    
    # NEW: Channel automation settings
    channel_name: str = ""
    script_template: str = ""  # System prompt for Groq AI
    num_prompts: int = 5  # Number of prompts to generate
    voice_id: str = ""  # Default ElevenLabs voice ID
    auto_workflow: bool = True  # Enable auto workflow
    auto_organize_folders: bool = False  # Auto create script folders (voice/image/video)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "video_output": self.video_output,
            "voice_output": self.voice_output,
            "image_output": self.image_output,
            # NEW fields
            "channel_name": self.channel_name,
            "script_template": self.script_template,
            "num_prompts": self.num_prompts,
            "voice_id": self.voice_id,
            "auto_workflow": self.auto_workflow,
            "auto_organize_folders": self.auto_organize_folders
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Project':
        return Project(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            created_at=data.get("created_at", ""),
            video_output=data.get("video_output", ""),
            voice_output=data.get("voice_output", ""),
            image_output=data.get("image_output", ""),
            # NEW fields
            channel_name=data.get("channel_name", ""),
            script_template=data.get("script_template", ""),
            num_prompts=data.get("num_prompts", 5),
            voice_id=data.get("voice_id", ""),
            auto_workflow=data.get("auto_workflow", True),
            auto_organize_folders=data.get("auto_organize_folders", False)
        )

class ProjectManager:
    """Manage projects with CRUD operations"""
    def __init__(self, projects_file: Path):
        self.projects_file = projects_file
        self.projects: List[Project] = []
        self.current_project: Optional[Project] = None
        self.load_projects()
    
    def load_projects(self):
        """Load projects from JSON file"""
        try:
            if self.projects_file.exists():
                data = json.loads(self.projects_file.read_text(encoding="utf-8"))
                self.projects = [Project.from_dict(p) for p in data.get("projects", [])]
                current_id = data.get("current_project_id")
                if current_id:
                    self.current_project = self.get_project_by_id(current_id)
        except Exception as e:
            print(f"Error loading projects: {e}")
            self.projects = []
    
    def save_projects(self):
        """Save projects to JSON file"""
        try:
            data = {
                "projects": [p.to_dict() for p in self.projects],
                "current_project_id": self.current_project.id if self.current_project else None
            }
            self.projects_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"Error saving projects: {e}")
    
    def create_project(self, name: str, description: str = "") -> Project:
        """Create new project with auto-generated folders"""
        project_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create output folders
        video_output = str(WORKFLOW_VIDEO / project_id)
        voice_output = str(WORKFLOW_VOICE / project_id)
        image_output = str(WORKFLOW_IMAGE / project_id)
        
        for folder in [video_output, voice_output, image_output]:
            Path(folder).mkdir(parents=True, exist_ok=True)
        
        project = Project(
            id=project_id,
            name=name,
            description=description,
            created_at=created_at,
            video_output=video_output,
            voice_output=voice_output,
            image_output=image_output
        )
        
        self.projects.append(project)
        self.save_projects()
        return project
    
    def update_project(self, project_id: str, name: str, description: str) -> bool:
        """Update existing project"""
        project = self.get_project_by_id(project_id)
        if project:
            project.name = name
            project.description = description
            self.save_projects()
            return True
        return False
    
    def delete_project(self, project_id: str) -> bool:
        """Delete project (keeps folders)"""
        project = self.get_project_by_id(project_id)
        if project:
            self.projects.remove(project)
            if self.current_project and self.current_project.id == project_id:
                self.current_project = None
            self.save_projects()
            return True
        return False
    
    def get_project_by_id(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        for p in self.projects:
            if p.id == project_id:
                return p
        return None
    
    def set_current_project(self, project_id: str):
        """Set current active project"""
        project = self.get_project_by_id(project_id)
        if project:
            self.current_project = project
            self.save_projects()
    
    def get_all_projects(self) -> List[Project]:
        """Get all projects"""
        return self.projects

class ProjectDialog(QDialog):
    """Dialog for creating/editing projects with channel automation settings"""
    def __init__(self, parent=None, name: str = "", description: str = "", voice_list: list = None):
        super().__init__(parent)
        self.setWindowTitle("Project" if not name else "Edit Project")
        self.setMinimumWidth(650)
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLabel {
                color: #11224E;
                font-weight: 600;
                font-size: 10pt;
            }
            QLineEdit, QTextEdit, QSpinBox, QComboBox {
                background-color: white;
                border: 2px solid #d1d9e6;
                border-radius: 6px;
                padding: 8px;
                font-size: 10pt;
            }
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {
                border-color: #F87B1B;
            }
            QCheckBox {
                color: #11224E;
                font-size: 10pt;
            }
        """)
        
        self.voice_list = voice_list or []
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("📁 " + ("New Project" if not name else "Edit Project"))
        title.setStyleSheet("""
            font-size: 16pt;
            font-weight: bold;
            color: #F87B1B;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # Form
        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)
        
        # Project name
        lbl_name = QLabel("Project Name *")
        form_layout.addWidget(lbl_name)
        
        self.txt_name = QLineEdit()
        self.txt_name.setText(name)
        self.txt_name.setPlaceholderText("Enter project name...")
        form_layout.addWidget(self.txt_name)
        
        # Description
        lbl_desc = QLabel("Description")
        form_layout.addWidget(lbl_desc)
        
        self.txt_desc = QTextEdit()
        self.txt_desc.setPlainText(description)
        self.txt_desc.setPlaceholderText("Enter project description (optional)...")
        self.txt_desc.setMaximumHeight(100)
        form_layout.addWidget(self.txt_desc)
        
        # Separator
        separator = QLabel("━" * 50)
        separator.setStyleSheet("color: #d1d9e6; margin: 5px 0;")
        form_layout.addWidget(separator)
        
        # Channel automation settings
        channel_header = QLabel("📺 Channel Automation Settings")
        channel_header.setStyleSheet("font-weight: bold; color: #F87B1B; font-size: 11pt; margin-top: 5px;")
        form_layout.addWidget(channel_header)
        
        # Num prompts - Hidden (auto random 12-24)
        # Tool will automatically generate random prompts between 12-24
        self.spin_num_prompts = QSpinBox()
        self.spin_num_prompts.setRange(12, 24)
        self.spin_num_prompts.setValue(12)  # Default, will be randomized
        self.spin_num_prompts.setVisible(False)  # Hidden from UI
        
        # Voice ID Dropdown
        lbl_voice = QLabel("🎙️ Default Voice ID")
        lbl_voice.setStyleSheet("font-size: 10pt; margin-top: 8px;")
        form_layout.addWidget(lbl_voice)
        
        self.combo_voice = QComboBox()
        self.combo_voice.addItem("None", "")
        for voice in self.voice_list:
            if isinstance(voice, dict):
                voice_name = voice.get('name', 'Unknown')
                voice_id = voice.get('id', '')
                self.combo_voice.addItem(f"{voice_name} ({voice_id})", voice_id)
        form_layout.addWidget(self.combo_voice)
        
        # Auto organize folders checkbox
        self.chk_auto_organize = QCheckBox("📁 Auto-create script folders (script_name/voice, /image, /video)")
        self.chk_auto_organize.setChecked(False)
        self.chk_auto_organize.setStyleSheet("""
            QCheckBox {
                spacing: 8px;
                font-size: 10pt;
                font-weight: 600;
                color: #11224E;
                margin-top: 10px;
                padding: 8px;
                background-color: #FFF7F0;
                border-radius: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #9CA3AF;
                background: #ffffff;
                border-radius: 4px;
            }
            QCheckBox::indicator:hover {
                border-color: #F87B1B;
                background: #FFF7F0;
            }
            QCheckBox::indicator:checked {
                background: #F87B1B;
                border-color: #FF8C2E;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEwIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDRMMy41IDYuNUw5IDEiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMS41IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
            }
        """)
        self.chk_auto_organize.setToolTip(
            "When enabled and importing a script, automatically create:\n"
            "• Folder with script name (same level as script)\n"
            "• Subfolders: voice/ image/ video/\n"
            "• All outputs will be saved to these folders"
        )
        form_layout.addWidget(self.chk_auto_organize)
        
        layout.addLayout(form_layout)
        
        # Info
        info = QLabel("💡 Folders will be created automatically:\n"
                     "  • Video: C:\\WorkFlow\\video\\[project_id]\n"
                     "  • Voice: C:\\WorkFlow\\voice\\[project_id]\n"
                     "  • Image: C:\\WorkFlow\\image\\[project_id]")
        info.setStyleSheet("""
            background-color: #E0F2FE;
            border: 1px solid #0284c7;
            border-radius: 6px;
            padding: 10px;
            font-size: 9pt;
            color: #0c4a6e;
            font-weight: normal;
        """)
        info.setWordWrap(True)
        layout.addWidget(info)
        
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
                font-size: 11pt;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #cbd5e1, stop:1 #94a3b8);
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        btn_save = QPushButton("Save" if name else "Create")
        btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF8C2E, stop:1 #F87B1B);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 25px;
                font-weight: bold;
                font-size: 11pt;
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
        
        # Focus on name field
        self.txt_name.setFocus()
    
    def get_values(self) -> Tuple[str, str]:
        """Get name and description - legacy method"""
        return self.txt_name.text().strip(), self.txt_desc.toPlainText().strip()
    
    def get_all_values(self) -> dict:
        """Get all project data including channel settings"""
        return {
            "name": self.txt_name.text().strip(),
            "description": self.txt_desc.toPlainText().strip(),
            "num_prompts": self.spin_num_prompts.value(),
            "voice_id": self.combo_voice.currentData(),
            "auto_organize_folders": self.chk_auto_organize.isChecked()
        }
    
    def accept(self):
        """Validate before accepting"""
        if not self.txt_name.text().strip():
            QMessageBox.warning(self, "Validation Error", "Project name is required!")
            return
        super().accept()

def _email_from_cookies(cookies: List[Dict]) -> Optional[str]:
    for c in cookies:
        if c["name"] in ["__Secure-next-auth.session-token", "next-auth.session-token"]:
            parts = c["value"].split(".")
            if len(parts) >= 2:
                try:
                    payload = json.loads(_b64url_decode(parts[1]).decode("utf-8", "ignore"))
                    em = payload.get("email") or (payload.get("user") or {}).get("email")
                    if em: return em
                except Exception:
                    pass
    for c in cookies:
        if c["name"].lower()=="email" and "@" in c["value"]:
            return c["value"]
    return None

def _extract_credits(text: str) -> Optional[str]:
    norm = _normalize(text)
    pats = [
        r"(?:tin dung(?:\s*ai)?|ai\s*credits?|credits?|tokens?|so du|remaining|left|balance)\D{0,8}(\d{1,6})",
        r"(\d{1,6})\s*(?:tin dung(?:\s*ai)?|ai\s*credits?|credits?|tokens?|so du)"
    ]
    for p in pats:
        m = re.search(p, norm)
        if m: return m.group(1)
    if any(k in norm for k in ["tin dung","ai credit","credit","token","so du","remaining","balance","left"]):
        nums = re.findall(r"\b\d{1,6}\b", norm)
        if nums: return str(max(map(int, nums)))
    return None

def _slugify(text: str, max_len: int = 32) -> str:
    s = unicodedata.normalize("NFKD", text)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^\w\s-]", "", s, flags=re.U)
    s = re.sub(r"\s+", "-", s.strip())
    s = re.sub(r"-{2,}", "-", s)
    return s[:max_len].lower() or "prompt"

def _read_json(path: Path, default):
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default

def _write_json(path: Path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# ============================== Flow checker ===============================
def check_cookie_file(cookie_file: str, timeout: int = 25) -> Dict:
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except Exception as e:
        return {"status": "Dead", "email": "-", "tokens": "-", "error": f"Playwright not installed: {e}"}

    HEADLESS = (os.getenv("PW_HEADLESS", "1") != "0")

    allcookies = parse_netscape_cookie_file(cookie_file)
    cookies_labs = parse_netscape_cookie_file(cookie_file, "labs.google")
    merged = cookies_labs if cookies_labs else allcookies
    if not merged:
        return {"status": "Dead", "email": "-", "tokens": "-", "error": "Không tìm thấy cookie hợp lệ."}

    email = _email_from_cookies(merged) or "-"
    tokens = "-"
    status, error = "Dead", None
    url = "https://labs.google/fx/vi/tools/flow"

    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=HEADLESS)
            context = browser.new_context()
            context.add_cookies(merged)
            page = context.new_page()

            page.goto(url, wait_until="domcontentloaded", timeout=timeout*1000)
            try: page.wait_for_load_state("networkidle", timeout=timeout*1000)
            except PWTimeout: pass

            final_url = page.url or ""
            status = "Live" if ("labs.google" in final_url and "accounts.google.com" not in final_url) else "Dead"
            if status != "Live":
                browser.close()
                return {"status": status, "email": email, "tokens": tokens, "error": "Not on labs.google"}

            def _panel_opened(pg) -> bool:
                return bool(pg.query_selector("text=/Đăng xuất|Sign out|Tín dụng AI|AI credits/i"))

            def _open_avatar_menu(pg) -> bool:
                sels = [
                    "button[aria-label*='Google Account' i]",
                    "a[aria-label*='Google Account' i]",
                    "button[aria-label*='Tài khoản Google' i]",
                    "a[aria-label*='Tài khoản Google' i]",
                    "img[alt*='Google Account' i]",
                    "img[alt*='Tài khoản Google' i]",
                    "button:has(img[alt*='Google Account' i])",
                    "button:has(img[alt*='Tài khoản Google' i])",
                    "[data-testid*='account' i]",
                ]
                for sel in sels:
                    el = pg.query_selector(sel)
                    if not el: continue
                    try:
                        el.click(timeout=1200)
                        pg.wait_for_timeout(300)
                        if _panel_opened(pg): return True
                    except Exception:
                        pass
                try:
                    cands = pg.locator("button, [role='button'], a").element_handles()
                    best, best_x = None, -1
                    for h in cands:
                        box = h.bounding_box()
                        if not box: continue
                        if box["y"] > 140 or box["width"] < 18 or box["height"] < 18:
                            continue
                        x_right = box["x"] + box["width"]
                        if x_right > best_x:
                            best_x, best = x_right, h
                    if best:
                        b = best.bounding_box()
                        pg.mouse.click(b["x"] + b["width"]/2, b["y"] + b["height"]/2)
                        pg.wait_for_timeout(300)
                        if _panel_opened(pg): return True
                except Exception:
                    pass
                try:
                    vp = pg.viewport_size or {"width": 1280, "height": 800}
                    for y in (40, 70, 100):
                        pg.mouse.click(vp["width"] - 22, y)
                        pg.wait_for_timeout(250)
                        if _panel_opened(pg): return True
                except Exception:
                    pass
                return False

            opened = _open_avatar_menu(page)
            if opened:
                inner = ""
                try: inner = page.inner_text("body")
                except Exception: inner = ""
                if (email == "-" or not email) and inner:
                    m = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9\.\-]+\.[a-zA-Z]{2,}", inner)
                    if m: email = m.group(0)
                tk = _extract_credits(inner)
                if tk: tokens = tk
            else:
                try:
                    t = page.inner_text("body")
                    if (email == "-" or not email):
                        m = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9\.\-]+\.[a-zA-Z]{2,}", t)
                        if m: email = m.group(0)
                    tk = _extract_credits(t);  tokens = tk or tokens
                except Exception:
                    pass

            browser.close()
    except Exception as e:
        error = str(e)

    return {"status": status, "email": email or "-", "tokens": tokens or "-", "error": error}

# ============================== Flow selectors ===============================
MODEL_REGEX = {
    "Veo 3.1 - Fast":    r"Veo\s*3\.1\s*-\s*Fast",
    "Veo 2 - Fast":      r"Veo\s*2\s*-\s*Fast",
    "Veo 3.1 - Quality": r"Veo\s*3\.1\s*-\s*Quality",
    "Veo 2 - Quality":   r"Veo\s*2\s*-\s*Quality",
}

def _wait_visible_text(page, pattern: str, to=12000) -> bool:
    try:
        page.wait_for_selector(f"text=/{pattern}/i", timeout=to)
        return True
    except Exception:
        return False

def _is_settings_popup_visible(page, to=8000) -> bool:
    try:
        page.wait_for_selector(
            "text=/Tỷ lệ khung hình|Aspect ratio|Câu trả lời đầu ra cho mỗi câu lệnh|Outputs per prompt|^(Mô hình|Model)$/i",
            timeout=to
        )
        return True
    except Exception:
        return False

def _new_project(page, timeout_ms: int):
    """Tạo project mới - Updated cho UI hiện tại"""
    try:
        page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
    except Exception:
        pass
    
    # Thử nhiều cách để tìm nút "New project"
    selectors = [
        "text=/Dự án mới/i", 
        "text=/\\+\\s*Dự án mới/i",
        "text=/New project/i", 
        "text=/\\+\\s*New project/i",
        "button:has-text('Dự án mới')", 
        "button:has-text('New project')",
        "button:has-text('+')",
        "[aria-label*='Dự án mới' i]",
        "[aria-label*='New project' i]"
    ]
    
    for sel in selectors:
        try:
            elements = page.locator(sel).all()
            for element in elements:
                if element.is_visible():
                    element.click(timeout=4000)
                    return True
        except Exception:
            continue
    
    # JavaScript fallback
    try:
        js_result = page.evaluate("""
            () => {
                const keywords = ['Dự án mới', 'New project', '+'];
                const elements = [...document.querySelectorAll('button, [role="button"], a')];
                
                for (const el of elements) {
                    const text = el.textContent || el.getAttribute('aria-label') || '';
                    for (const keyword of keywords) {
                        if (text.includes(keyword) && el.offsetParent) {
                            try {
                                el.click();
                                return {success: true, text: text.trim()};
                            } catch (e) {
                                continue;
                            }
                        }
                    }
                }
                return {success: false};
            }
        """)
        
        if js_result.get("success"):
            return True
            
    except Exception:
        pass
    
    return False

def _open_composer_settings(page) -> bool:
    """
    Mở popup 'Cài đặt' của composer - Unified version
    """
    # Strategy 1: bấm '3 gạch' trong vùng composer (UI mới)
    try:
        composer_input = None
        for sel in [
            "textarea[placeholder*='video' i]",
            "textarea",
            "[role='textbox']",
            "div[contenteditable='true']",
        ]:
            try:
                el = page.locator(sel).last
                if el.count() and el.is_visible():
                    composer_input = el
                    break
            except:
                pass

        if composer_input:
            container = composer_input.locator("xpath=ancestor::div[1]")
            candidates = []
            try:
                btns = container.locator("button, [role='button']").element_handles()
                candidates.extend(btns)
            except:
                pass

            vp = page.viewport_size or {"width": 1280, "height": 800}
            for h in candidates:
                try:
                    box = h.bounding_box()
                    if not box:
                        continue
                    if box["y"] > vp["height"] * 0.55 and 18 <= box["height"] <= 48 and 18 <= box["width"] <= 64:
                        h.click(timeout=1200)
                        page.wait_for_timeout(350)
                        if _is_settings_popup_visible(page, 3000):
                            return True
                except:
                    continue
    except:
        pass

    # Strategy 2: bấm gần chip 'Veo X - Fast/Quality'
    try:
        chip = page.locator("text=/Veo\\s*(?:[23]|3\\.1)\\s*-\\s*(?:Fast|Quality)/i").last
        if chip.count():
            chip.wait_for(state="visible", timeout=6000)
            box = chip.bounding_box()
            if box:
                x = box["x"] + box["width"] + 28
                y = box["y"] + box["height"]/2
                page.mouse.click(x, y)
                page.wait_for_timeout(500)
                if _is_settings_popup_visible(page, 3000):
                    return True
    except:
        pass

    # Strategy 3: nút có aria-label 'Cài đặt/Settings'
    for sel in ["button[aria-label*='Cài đặt' i]", "button[aria-label*='Settings' i]"]:
        try:
            btns = page.locator(sel)
            if btns.count():
                btns.last.click(timeout=2000)
                if _is_settings_popup_visible(page, 3000):
                    return True
        except:
            pass

    # Strategy 4: JavaScript approach
    try:
        js_result = page.evaluate("""
            () => {
                const settingsSelectors = [
                    'button[aria-label*="setting" i]',
                    'button[aria-label*="cài đặt" i]',
                    '*[data-testid*="settings" i]'
                ];
                
                for (const selector of settingsSelectors) {
                    const elements = document.querySelectorAll(selector);
                    for (const el of elements) {
                        if (el.offsetParent !== null) {
                            try {
                                el.click();
                                return {success: true, method: 'settings_button'};
                            } catch (e) {
                                continue;
                            }
                        }
                    }
                }
                
                const chips = [...document.querySelectorAll('*')].filter(el => 
                    el.textContent && el.textContent.match(/Veo\\s*[23]\\s*-\\s*(Fast|Quality)/i)
                );
                
                for (const chip of chips) {
                    if (chip.offsetParent) {
                        const rect = chip.getBoundingClientRect();
                        const clickX = rect.right + 20;
                        const clickY = rect.top + rect.height / 2;
                        
                        const clickEvent = new MouseEvent('click', {
                            view: window,
                            bubbles: true,
                            cancelable: true,
                            clientX: clickX,
                            clientY: clickY
                        });
                        
                        document.elementFromPoint(clickX, clickY)?.dispatchEvent(clickEvent);
                        return {success: true, method: 'chip_area_click'};
                    }
                }
                
                return {success: false};
            }
        """)
        
        if js_result.get("success"):
            page.wait_for_timeout(2000)
            if _is_settings_popup_visible(page, 3000):
                return True
    except Exception:
        pass

    return False

def _select_model_and_outputs(page, wanted_model: str, outputs: int):
    """
    Unified function for selecting model and outputs - works for both text and image modes
    """
    if not _is_settings_popup_visible(page, 1200):
        if not _open_composer_settings(page):
            return False

    try:
        dlg = page.get_by_role("dialog")
        dlg.wait_for(state="visible", timeout=4000)
    except Exception:
        dlg = page
    
    ok_any = False

    # ===== MODEL =====
    try:
        lbl = dlg.locator(r"text=/^(Mô hình|Model)$/i").first
        if lbl.count() and lbl.is_visible():
            row = lbl.locator("xpath=ancestor::*[self::div or self::section or self::form][1]")

            trigger = (row.get_by_role("combobox").first
                       or row.locator("[aria-haspopup='listbox']").first
                       or row.locator("[aria-haspopup]").first
                       or row.get_by_role("button").last)

            # Fallback: click vào giá trị hiện tại trong dòng
            if (not trigger) or (not trigger.count()) or (not trigger.is_visible()):
                trigger = row.locator(r"text=/Veo\s*[23]\s*-\s*(?:Fast|Quality)/i").first

            clicked = False
            if trigger and trigger.count() and trigger.is_visible():
                try:
                    trigger.click(timeout=1500)
                    clicked = True
                except Exception:
                    clicked = False
            
            if not clicked:
                try:
                    box = row.bounding_box()
                    if box:
                        page.mouse.click(box["x"] + box["width"] - 10, box["y"] + box["height"]/2)
                        clicked = True
                except Exception:
                    pass

            if clicked:
                page.wait_for_timeout(150)

                patt = re.compile(re.escape(wanted_model), re.I)
                opt = page.get_by_role("option", name=patt)
                if not opt.count():
                    for role in ("menuitemradio", "menuitem", "radio", "button"):
                        cand = page.get_by_role(role, name=patt)
                        if cand.count(): opt = cand; break
                if not opt.count():
                    opt = page.locator(f"//*[contains(normalize-space(.), '{wanted_model}')]").first

                if opt.count():
                    opt.first.click(timeout=1800)
                    page.wait_for_timeout(120)
                    ok_any = True
    except Exception:
        pass

    # ===== OUTPUTS =====
    try:
        out = max(1, min(4, int(outputs or 1)))
        lbl2 = dlg.locator(r"text=/^(Câu trả lời đầu ra cho mỗi câu lệnh|Outputs per prompt)$/i").first
        if lbl2.count() and lbl2.is_visible():
            row2 = lbl2.locator("xpath=ancestor::*[self::div or self::section or self::form][1]")

            trigger2 = (row2.get_by_role("combobox").first
                        or row2.locator("[aria-haspopup='listbox']").first
                        or row2.locator("[aria-haspopup]").first
                        or row2.get_by_role("button").last)
            
            # Fallback: click vào số hiện tại
            if (not trigger2) or (not trigger2.count()) or (not trigger2.is_visible()):
                trigger2 = row2.locator(r"text=/^\s*[1-4]\s*$/").first

            clicked2 = False
            if trigger2 and trigger2.count() and trigger2.is_visible():
                try:
                    trigger2.click(timeout=1500)
                    clicked2 = True
                except Exception:
                    clicked2 = False
            
            if not clicked2:
                try:
                    box2 = row2.bounding_box()
                    if box2:
                        page.mouse.click(box2["x"] + box2["width"] - 10, box2["y"] + box2["height"]/2)
                        clicked2 = True
                except Exception:
                    pass

            if clicked2:
                page.wait_for_timeout(120)

                patt2 = re.compile(f"^{out}$")
                opt2 = page.get_by_role("option", name=patt2)
                if not opt2.count():
                    for role in ("menuitemradio", "menuitem", "radio", "button"):
                        cand2 = page.get_by_role(role, name=str(out))
                        if cand2.count(): opt2 = cand2; break
                if not opt2.count():
                    opt2 = page.locator(f"//*[normalize-space(text())='{out}']").first

                if opt2.count():
                    opt2.first.click(timeout=1800)
                    ok_any = True
    except Exception:
        pass

    # Close popup
    try:
        page.keyboard.press("Escape")
        page.wait_for_timeout(120)
    except Exception:
        pass

    return ok_any

# ============================== File helpers ===============================
def _guess_ext_by_magic(path: Path) -> str:
    try:
        with open(path, "rb") as f:
            head = f.read(16)
        if b"ftyp" in head[4:12]:  # mp4/mov
            return ".mp4"
        if head.startswith(b"\x1A\x45\xDF\xA3"):  # EBML Matroska
            return ".webm"
        if head.startswith(b"RIFF") and b"WEBP" in head:
            return ".webp"
    except Exception:
        pass
    return ""

def _ffmpeg_convert_to_mp4(src: Path, dst: Path) -> bool:
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
    try:
        cmd = [ffmpeg, "-y", "-i", str(src), "-c:v", "libx264", "-c:a", "aac", str(dst)]
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return p.returncode == 0 and dst.exists() and dst.stat().st_size > 0
    except Exception:
        return False
def _simple_download_video(page, out_dir: Path, name_base: str, timeout: int = 60, progress_cb=None, phase_range=(60, 95)) -> str:
    """
    Tải video từ card kết quả mới nhất.
    1) Thử bấm các NÚT ICON download (không cần text) trong vùng card chứa <video>, rồi chờ expect_download.
    2) Fallback: nếu không có nút (hoặc không phát sinh download), lấy trực tiếp dữ liệu video/blob từ DOM
       (kể cả blob:) và ghi ra file, sau đó convert sang .mp4 nếu cần.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    video_path = ""
    last_emit = 0
    def _emit(p, label):
        nonlocal last_emit
        p = int(p)
        if progress_cb and (p != last_emit):
            last_emit = p
            progress_cb(p, label)

    def _latest_video_handle():
        try:
            vids = page.locator("video")
            if vids.count() == 0:
                return None
            return vids.last.element_handle()
        except Exception:
            return None

    def _hover_media_controls():
        # hover vài điểm để lộ cụm nút overlay
        try:
            vh = _latest_video_handle()
            if not vh:
                return
            box = vh.bounding_box()
            if not box:
                return
            positions = [
                (box["x"] + box["width"] - 10, box["y"] + 10),
                (box["x"] + box["width"] - 20, box["y"] + box["height"] - 20),
                (box["x"] + box["width"]/2,    box["y"] + box["height"]/2),
            ]
            for x, y in positions:
                page.mouse.move(x, y)
                page.wait_for_timeout(200)
        except Exception:
            pass

    def _click_any_plausible_download():
        """
        Quét các button/a trong card tổ tiên gần nhất của <video>:
        - aria-label/title/data-testid chứa download/save/export/lưu/xuất/tải
        - Material icons/text: file_download, download, save_alt, arrow_downward
        """
        try:
            vh = _latest_video_handle()
            if not vh:
                return False

            # Lấy container: ancestor div/section gần nhất
            container = None
            for i in range(1, 7):
                try:
                    c = page.locator(f"xpath=ancestor::*[self::div or self::section][{i}]").locator("xpath=.", has=page.locator("video")).last
                    # trên một số bản Playwright Python, cách trên khó xác định 'has', dùng JS để leo lên:
                except Exception:
                    c = None

            # Fallback JS để tìm container bọc video sâu nhất
            if not container:
                try:
                    container = page.evaluate_handle(
                        """(vid)=>{
                            let n = vid;
                            for (let depth=0; depth<6 && n && n.parentElement; depth++){
                                n = n.parentElement;
                                // nếu container có nhiều button/menu và có layout card-like thì dừng
                                const btns = n.querySelectorAll('button,[role="button"],a');
                                if (btns.length >= 2) return n;
                            }
                            return vid.parentElement || vid;
                        }""",
                        vh
                    )
                except Exception:
                    container = None

            # Nếu không xác định được container, quét toàn trang nhưng ưu tiên gần <video>
            scope = page if not container else page.locator(":scope").filter(has=page.locator("video")).first if False else page

            # Thu thập ứng cử viên ở quanh video (ưu tiên các nút hiện hữu)
            if container:
                btn_loc = page.locator("xpath=.", has=page.locator("video"))  # dummy giữ API, không dùng
                cand = page.query_selector_all("button, [role='button'], a") if not container else container.query_selector_all("button, [role='button'], a")
            else:
                cand = page.query_selector_all("button, [role='button'], a")

            if not cand:
                return False

            KEYWORDS = ["download", "file_download", "save", "save_alt", "export",
                        "tải", "lưu", "xuất", "xuất video"]

            def _score_button(h):
                try:
                    # Tổng hợp text/label/attr để nhận dạng
                    aria = (h.get_attribute("aria-label") or "") + " " + (h.get_attribute("aria-description") or "")
                    title = h.get_attribute("title") or ""
                    dataid = h.get_attribute("data-testid") or ""
                    inner = h.evaluate("el => (el.innerText||'') + ' ' + (el.textContent||'')")
                    blob = " ".join([aria, title, dataid, inner]).lower()
                    score = 0
                    for kw in KEYWORDS:
                        if kw in blob:
                            score += 1
                    # hơi ưu tiên các nút nhỏ ở cạnh phải/overlay
                    box = h.bounding_box()
                    if box and box["width"] <= 64 and box["height"] <= 64:
                        score += 0.5
                    return score, blob
                except Exception:
                    return 0, ""

            # Sắp xếp theo điểm heuristic
            ranked = sorted([( _score_button(h), h) for h in cand ], key=lambda x: x[0][0], reverse=True)

            for (sc, blob), h in ranked[:12]:
                if sc <= 0:
                    continue
                try:
                    # Thử click và chờ download event
                    with page.expect_download(timeout=8000) as dl_info:
                        h.click(timeout=2000)
                    dl = dl_info.value
                    raw_name = dl.suggested_filename or "video"
                    safe_name = re.sub(r"[^\w\-.]+", "_", raw_name).strip("._")
                    if not os.path.splitext(safe_name)[1]:
                        safe_name += ".bin"
                    tmp_path = (out_dir / safe_name).resolve()
                    dl.save_as(str(tmp_path))

                    # Chuẩn hoá đuôi và convert -> .mp4
                    final_path = tmp_path
                    guessed = _guess_ext_by_magic(tmp_path)
                    if guessed and os.path.splitext(tmp_path.name)[1].lower() != guessed:
                        try:
                            new_path = tmp_path.with_suffix(guessed)
                            tmp_path.rename(new_path)
                            final_path = new_path
                        except Exception:
                            final_path = tmp_path

                    desired = _slugify(name_base or "video", 48)
                    target = (out_dir / f"{desired}.mp4").resolve()
                    if final_path.suffix.lower() != ".mp4":
                        mp4_path = final_path.with_suffix(".mp4")
                        if _ffmpeg_convert_to_mp4(final_path, mp4_path):
                            try: final_path.unlink(missing_ok=True)
                            except Exception: pass
                            final_path = mp4_path
                    if final_path != target:
                        try:
                            if target.exists(): target.unlink()
                            final_path.rename(target)
                            final_path = target
                        except Exception:
                            pass

                    return str(final_path)
                except Exception:
                    # Không có download event, thử nút kế tiếp
                    continue

            return False
        except Exception:
            return False
        
    def _programmatic_grab_video():
        """
        Không cần nút. Lấy currentSrc/src của <video> (kể cả blob:) và đọc blob thành dataURL base64,
        sau đó ghi ra file.
        """
        try:
            data = page.evaluate("""
                async () => {
                    const vid = document.querySelector('video');
                    if (!vid) return { ok:false, reason:'no video' };
                    let src = vid.currentSrc || vid.src;
                    if (!src) {
                        const s = vid.querySelector('source[src]'); 
                        if (s) src = s.src;
                    }
                    if (!src) return { ok:false, reason:'no src' };

                    const resp = await fetch(src);
                    if (!resp.ok) return { ok:false, reason:'fetch failed '+resp.status };
                    const blob = await resp.blob();
                    const dataUrl = await new Promise((resolve, reject) => {
                        const r = new FileReader();
                        r.onload = () => resolve(r.result);
                        r.onerror = reject;
                        r.readAsDataURL(blob);
                    });
                    // dataUrl: "data:<mime>;base64,<...>"
                    return { ok:true, dataUrl };
                }
            """)
            if not data or not data.get("ok"):
                return ""

            data_url = data["dataUrl"]
            # tách mime và base64
            m = re.match(r"^data:([^;]+);base64,(.+)$", data_url)
            if not m:
                return ""
            mime, b64 = m.group(1), m.group(2)
            raw = base64.b64decode(b64)

            # Quyết định đuôi file từ mime (fallback -> .bin)
            ext = ".mp4"
            if "webm" in mime:
                ext = ".webm"
            elif "quicktime" in mime or "mov" in mime:
                ext = ".mov"
            elif "mp4" in mime:
                ext = ".mp4"

            desired = _slugify(name_base or "video", 48)
            tmp_path = (out_dir / f"{desired}{ext}").resolve()
            with open(tmp_path, "wb") as f:
                f.write(raw)

            final_path = tmp_path
            # Chuẩn hoá/convert sang mp4
            if final_path.suffix.lower() != ".mp4":
                mp4_path = final_path.with_suffix(".mp4")
                if _ffmpeg_convert_to_mp4(final_path, mp4_path):
                    try: final_path.unlink(missing_ok=True)
                    except Exception: pass
                    final_path = mp4_path

            return str(final_path) if final_path.exists() else ""
        except Exception:
            return ""
        
    # ====== Quy trình chính ======
    page.wait_for_timeout(1500)
    start_p, end_p = phase_range
    while time.time() - t0 < timeout:
        # tiến độ mượt theo thời gian
        elapsed = time.time() - t0
        frac = max(0.0, min(1.0, elapsed / max(1, timeout)))
        p_now = start_p + int((end_p - start_p) * frac)
        _emit(p_now, "Generating & waiting...")

        _hover_media_controls()

        path = _click_any_plausible_download()
        if isinstance(path, str) and path:
            _emit(98, "Saving file...")
            return path

        page.wait_for_timeout(500)

        if (time.time() - t0) > (timeout * 0.5):
            grabbed = _programmatic_grab_video()
            if grabbed:
                _emit(98, "Saving file...")
                return grabbed

    return ""

# ============================== Image2Video functions ===============================
def handle_crop_dialog(page) -> bool:
    """Xử lý dialog 'Cắt thành phần' sau khi upload ảnh"""
    
    try:
        # Wait for dialog to appear
        crop_indicators = [
            "text=/Cắt thành phần/i",
            "text=/Crop/i", 
            "text=/Cắt và lưu/i",
            "text=/Crop and save/i",
            "button:has-text('Cắt và lưu')",
            "button:has-text('Crop and save')"
        ]
        
        crop_found = False
        for indicator in crop_indicators:
            try:
                page.wait_for_selector(indicator, timeout=5000)
                crop_found = True
                break
            except:
                continue
        
        if not crop_found:
            return True
        
        # Click "Cắt và lưu" button
        save_selectors = [
            "text=/Cắt và lưu/i",
            "text=/Crop and save/i",
            "button:has-text('Cắt và lưu')",
            "button:has-text('Crop and save')",
            "[aria-label*='Cắt và lưu' i]",
            "[aria-label*='Crop and save' i]"
        ]
        
        for sel in save_selectors:
            try:
                btn = page.locator(sel).first
                if btn.count() and btn.is_visible():
                    btn.click(timeout=3000)
                    page.wait_for_timeout(2000)
                    return True
            except Exception:
                continue
        
        # Fallback: try clicking any prominent button
        try:
            buttons = page.locator("button").all()
            for btn in buttons:
                if btn.is_visible():
                    text = btn.inner_text().lower()
                    if any(word in text for word in ["cắt", "lưu", "crop", "save", "ok", "done"]):
                        btn.click(timeout=2000)
                        page.wait_for_timeout(2000)
                        return True
        except Exception:
            pass
        
        return False
        
    except Exception:
        return False

def upload_image_with_crop(page, image_path: str, upload_index: int, image_type: str) -> bool:
    """Upload ảnh với xử lý crop dialog"""
    
    try:
        # Find upload areas
        upload_candidates = []
        
        # Find + buttons or upload areas
        plus_buttons = page.locator("button:has-text('+'), [role='button']:has-text('+')").all()
        for btn in plus_buttons:
            if btn.is_visible():
                upload_candidates.append(("plus_button", btn))
        
        # Find upload text elements
        upload_text_elements = page.locator("text=/Tải lên|Upload|Thêm|Add/i").all()
        for elem in upload_text_elements:
            if elem.is_visible():
                upload_candidates.append(("text_element", elem))
        
        if upload_index >= len(upload_candidates):
            return False
        
        # Click upload area
        candidate_type, target_element = upload_candidates[upload_index]
        
        target_element.click(timeout=5000)
        page.wait_for_timeout(2000)
        
        # Find and click upload menu if present
        try:
            upload_menu_items = page.locator("text=/Tải lên|Upload/i").all()
            for item in upload_menu_items:
                if item.is_visible():
                    item.click(timeout=3000)
                    page.wait_for_timeout(1000)
                    break
        except:
            pass
        
        # Upload file
        page.wait_for_timeout(1000)
        file_inputs = page.locator("input[type='file']").all()
        
        upload_success = False
        for i, file_input in enumerate(file_inputs):
            try:
                file_input.set_input_files(image_path)
                page.wait_for_timeout(3000)
                upload_success = True
                break
            except Exception:
                continue
        
        if not upload_success:
            return False
        
        # Handle crop dialog
        page.wait_for_timeout(3000)
        crop_handled = handle_crop_dialog(page)
        
        return crop_handled
            
    except Exception:
        return False

def switch_to_image_mode(page):
    """Switch from text-to-video to image-to-video mode"""
    
    try:
        # Strategy 1: Find and click dropdown button
        dropdown_selectors = [
            "button[aria-haspopup='true']",
            "button[aria-haspopup='menu']", 
            "[role='button'][aria-haspopup]",
            "button:has(svg)",
            "div[role='combobox']",
            "button[role='combobox']"
        ]
        
        for sel in dropdown_selectors:
            try:
                elements = page.locator(sel).all()
                
                for i, element in enumerate(elements):
                    if element.is_visible():
                        try:
                            element.click(timeout=2000)
                            page.wait_for_timeout(1500)
                            
                            # Check if popup opened
                            if page.locator("text=/Tạo video từ các khung hình/i").count() > 0:
                                return True
                                
                        except Exception:
                            continue
                            
            except Exception:
                continue

        # Strategy 2: Click next to text "Từ văn bản sang video"
        try:
            text_elements = page.locator("text=/Từ văn bản sang video/i").all()
            for i, text_el in enumerate(text_elements):
                if text_el.is_visible():
                    box = text_el.bounding_box()
                    if box:
                        # Click to the right of text
                        click_x = box["x"] + box["width"] + 15
                        click_y = box["y"] + box["height"] / 2
                        
                        page.mouse.click(click_x, click_y)
                        page.wait_for_timeout(2000)
                        
                        if page.locator("text=/Tạo video từ các khung hình/i").count() > 0:
                            return True
        except Exception:
            pass

        # Strategy 3: JavaScript click
        try:
            js_result = page.evaluate("""
                () => {
                    const clickableElements = [
                        ...document.querySelectorAll('button[aria-haspopup]'),
                        ...document.querySelectorAll('[role="button"][aria-haspopup]'),
                        ...document.querySelectorAll('div[role="combobox"]')
                    ];
                    
                    for (const el of clickableElements) {
                        if (el.offsetParent !== null) {
                            try {
                                el.click();
                                return {success: true, element: el.tagName};
                            } catch (e) {
                                continue;
                            }
                        }
                    }
                    return {success: false};
                }
            """)
            
            if js_result.get("success"):
                page.wait_for_timeout(2000)
                if page.locator("text=/Tạo video từ các khung hình/i").count() > 0:
                    return True
        except Exception:
            pass

        return False
        
    except Exception:
        return False

def click_image_to_video_option(page):
    """Click on 'Tạo video từ các khung hình' option in popup"""
    
    try:
        page.wait_for_timeout(2000)
        
        # Find and click option
        option_selectors = [
            "text=/Tạo video từ các khung hình/i",
            "button:has-text('Tạo video từ các khung hình')",
            "[aria-label*='Tạo video từ các khung hình' i]",
            "div:has-text('Tạo video từ các khung hình')",
            "*:has-text('Tạo video từ các khung hình')"
        ]
        
        for sel in option_selectors:
            try:
                element = page.locator(sel).first
                if element.count() and element.is_visible():
                    element.click(timeout=5000)
                    page.wait_for_timeout(3000)
                    return True
            except Exception:
                continue
        
        # Fallback: JavaScript click
        try:
            js_result = page.evaluate("""
                () => {
                    const elements = [...document.querySelectorAll('*')].filter(el => 
                        el.textContent && el.textContent.includes('Tạo video từ các khung hình')
                    );
                    
                    for (const el of elements) {
                        if (el.offsetParent !== null) {
                            try {
                                el.click();
                                return {success: true};
                            } catch (e) {
                                continue;
                            }
                        }
                    }
                    return {success: false};
                }
            """)
            
            if js_result.get("success"):
                page.wait_for_timeout(3000)
                return True
        except Exception:
            pass
        
        return False
        
    except Exception:
        return False

def verify_image_mode(page):
    """Verify Image-to-Video mode"""
    
    try:
        # Check indicators
        indicators = [
            "text=/Tạo một video bằng văn bản và khung hình/i",
            "text=/Create a video using text and frames/i",
            "[aria-label*='Tải lên' i]",
            "[aria-label*='Upload' i]",
            "button:has-text('+')",
            "input[type='file']"
        ]
        
        for indicator in indicators:
            try:
                if page.locator(indicator).count() > 0:
                    return True
            except:
                continue
        
        # JavaScript check
        try:
            js_check = page.evaluate("""
                () => {
                    const bodyText = document.body.textContent || '';
                    const hasFileInputs = document.querySelectorAll('input[type="file"]').length > 0;
                    const hasUploadText = bodyText.includes('Tải lên') || bodyText.includes('Upload') || 
                                         bodyText.includes('khung hình') || bodyText.includes('frames');
                    
                    return {
                        hasFileInputs,
                        hasUploadText,
                        isImageMode: hasFileInputs || hasUploadText
                    };
                }
            """)
            
            if js_check.get("isImageMode"):
                return True
                
        except Exception:
            pass
        
        return False
        
    except Exception:
        return False

def send_prompt(page, prompt):
    """Send prompt"""
    
    prompt_selectors = [
        "textarea[placeholder*='Tạo một video bằng văn bản và khung hình' i]",
        "textarea[placeholder*='video' i]",
        "textarea",
        "[role='textbox']",
        "div[contenteditable='true']"
    ]
    
    for sel in prompt_selectors:
        try:
            el = page.locator(sel).last
            if el.count():
                el.click(timeout=2000)
                el.fill(prompt[:4000])
                page.wait_for_timeout(500)
                
                # Send prompt
                send_clicked = False
                send_selectors = [
                    "button[aria-label*='Gửi' i]",
                    "button[aria-label*='Send' i]",
                    "button:has(svg)",
                ]
                
                for send_sel in send_selectors:
                    try:
                        send_btn = page.locator(send_sel).last
                        if send_btn.count() and send_btn.is_visible():
                            send_btn.click(timeout=1000)
                            send_clicked = True
                            break
                    except:
                        pass
                
                if not send_clicked:
                    page.keyboard.press("Enter")
                
                return True
        except Exception:
            continue
    
    return False

def generate_video_from_image(
    cookie_file: str,
    start_image: str,
    prompt: str,
    wanted_model: str,
    outputs: int,
    out_dir: Path,
    timeout: int = 240,
    name_base: str = "",
    progress_cb=None
) -> Dict:
    """
    Image->Video: mở Flow, tạo project, chuyển chế độ hình ảnh, upload ảnh,
    chọn model, gửi prompt, tải video. Có hỗ trợ progress_cb(percent:int, label:str).
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    def _emit(p, label):
        if progress_cb:
            try:
                progress_cb(int(p), str(label))
            except Exception:
                pass

    if not os.path.exists(start_image):
        _emit(0, "Failed")
        return {"ok": False, "note": f"Start image not found: {start_image}", "video_path": ""}

    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except Exception as e:
        _emit(0, "Failed")
        return {"ok": False, "note": f"Playwright not installed: {e}", "video_path": ""}

    cookies = parse_netscape_cookie_file(cookie_file, "labs.google") or parse_netscape_cookie_file(cookie_file)
    if not cookies:
        _emit(0, "Failed")
        return {"ok": False, "note": "Không tìm thấy cookies hợp lệ", "video_path": ""}

    HEADLESS = (os.getenv("PW_HEADLESS", "1") != "0")
    url_home = "https://labs.google/fx/vi/tools/flow"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=HEADLESS)
            ctx = browser.new_context(accept_downloads=True)
            ctx.add_cookies(cookies)
            page = ctx.new_page()
            _emit(5, "Init")
            page.goto(url_home, timeout=(timeout + 5) * 1000)
            try:
                page.wait_for_load_state("networkidle", timeout=(timeout + 5) * 1000)
            except PWTimeout:
                pass

            _emit(20, "New project")
            if not _new_project(page, (timeout + 5) * 1000):
                browser.close()
                _emit(0, "Failed")
                return {"ok": False, "note": "Không tìm thấy nút tạo project mới", "video_path": ""}

            try:
                page.wait_for_url(re.compile(r"/project/"), timeout=(timeout + 10) * 1000)
            except PWTimeout:
                pass

            _emit(30, "Switch Image mode")
            page.wait_for_timeout(1500)
            popup_opened = switch_to_image_mode(page)
            if popup_opened:
                click_image_to_video_option(page)

            _emit(40, "Verify mode")
            page.wait_for_timeout(1500)
            verify_image_mode(page)  # không bắt buộc fail hard

            _emit(50, "Upload image")
            page.wait_for_timeout(3000)
            start_uploaded = upload_image_with_crop(page, start_image, 0, "start")
            page.wait_for_timeout(3000)
            if not start_uploaded:
                browser.close()
                _emit(0, "Failed")
                return {"ok": False, "note": "Start image upload failed", "video_path": ""}

            _emit(60, "Select model")
            page.wait_for_timeout(3000)
            _wait_visible_text(page, r"Veo\s*[23]\s*-\s*(?:Fast|Quality)", to=10000)
            _select_model_and_outputs(page, wanted_model, outputs)

            _emit(70, "Send prompt")
            sent = send_prompt(page, prompt)
            if not sent:
                browser.close()
                _emit(0, "Failed")
                return {"ok": False, "note": "Không thể gửi prompt", "video_path": ""}

            # Download (75% → 96%)
            video_path = _simple_download_video(
                page,
                out_dir,
                name_base,
                timeout=timeout,  # dùng toàn bộ timeout cho giai đoạn đợi generate/tải
                progress_cb=lambda p, l: _emit(p, l),
                phase_range=(75, 96),
            )
            browser.close()

            if video_path:
                _emit(100, "Saved")
                return {"ok": True, "note": "Success", "video_path": video_path}
            else:
                _emit(0, "Failed")
                return {"ok": False, "note": "Download failed", "video_path": ""}

    except Exception as e:
        _emit(0, "Failed")
        return {"ok": False, "note": str(e), "video_path": ""}
# ============================== Flow configurator ===============================
def configure_flow_project(cookie_file: str, model: str = "Veo 3 - Fast",
                           outputs: int = 1, timeout: int = 25,
                           debug: bool = True) -> dict:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

    url_home = "https://labs.google/fx/vi/tools/flow"
    cookies = parse_netscape_cookie_file(cookie_file, "labs.google") or parse_netscape_cookie_file(cookie_file)
    if not cookies:
        return {"ok": False, "final_url": "", "chosen_model": "", "note": "Không tìm thấy cookies hợp lệ"}

    wanted = model if model in MODEL_REGEX else "Veo 3.1 - Fast"
    HEADLESS = (os.getenv("PW_HEADLESS", "1") != "0")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        ctx = browser.new_context(); ctx.add_cookies(cookies)
        page = ctx.new_page()

        page.goto(url_home, wait_until="domcontentloaded", timeout=(timeout+5)*1000)
        try: page.wait_for_load_state("networkidle", timeout=(timeout+5)*1000)
        except PWTimeout: pass

        opened = _new_project(page, (timeout+15)*1000)
        if not opened:
            browser.close()
            return {"ok": False, "final_url": page.url, "chosen_model": "",
                    "note": "Không tìm thấy nút 'Dự án mới'."}

        try: page.wait_for_url(re.compile(r"/project/"), timeout=(timeout+15)*1000)
        except PWTimeout: pass

        _wait_visible_text(page, r"Veo\s*(?:[23]|3\.1)\s*-\s*(?:Fast|Quality)", to=20000)

        if not _open_composer_settings(page):
            browser.close()
            return {"ok": False, "final_url": page.url, "chosen_model": "",
                    "note": "Không mở được popup Cài đặt ở dưới."}

        _select_model_and_outputs(page, wanted, outputs)

        final_url = page.url
        chip_correct = False

        try:
            chip = page.locator("text=/Veo\\s*(?:[23]|3\\.1)\\s*-\\s*(Fast|Quality)/i").last
            chip_text = chip.inner_text(timeout=3000).strip()
            # So sánh linh hoạt hơn (bỏ qua khoảng trắng thừa)
            wanted_normalized = wanted.replace(" ", "").lower()
            chip_normalized = chip_text.replace(" ", "").lower()
            if wanted_normalized in chip_normalized:
                chip_correct = True
        except Exception:
            pass

        browser.close()

        if chip_correct:
            return {"ok": True, "final_url": final_url, "chosen_model": wanted,
                    "note": f"Successfully configured: {wanted}, Outputs: {int(max(1, min(4, outputs)))}"}
        else:
            return {"ok": False, "final_url": final_url, "chosen_model": "",
                    "note": "Model selection seemed to work but chip doesn't match"}

# ============================== Data model ===============================
@dataclass
class AccountRow:
    path: str
    status: str = "…"
    email: str = "…"
    tokens: str = "…"

@dataclass
@dataclass
class ImagePromptRow:
    prompt: str
    start_image: str
    status: str = "Pending"
    video: str = ""
# >>> NEW: Preset 12 style và các danh mục thông số
STYLE_PRESETS = [
    "Ultra-Realistic / Photorealism",
    "Cinematic / Hollywood Trailer",
    "Animation / Anime / Cartoon",
    "Stylized / Comic / Graphic Novel",
    "Surreal / Dreamlike / FX Heavy",
    "Loopable / Seamless Motion",
    "Hyper-Detailed Slow-Motion",
    "Documentary / Raw Handheld",
    "Game Engine / CGI Real-Time",
    "Minimalist / Aesthetic Focus",
    "High-Contrast Action (Bay/Snyder)",
    "Retro / VHS / Vintage",
]

RES_OPTIONS  = ["1080p", "4K UHD", "8K HDR"]
FPS_OPTIONS  = ["24fps", "30fps", "60fps", "120fps"]
LIGHTING_OPS = ["cinematic lighting", "golden hour", "volumetric light", "high contrast / chiaroscuro", "soft natural daylight"]
GRADING_OPS  = ["HDR10+", "Teal & Orange", "Monochrome", "Neon cyberpunk", "Pastel tones"]
LENS_OPS     = ["shallow depth of field", "anamorphic lens flare", "macro lens", "wide angle lens"]
FX_OPS       = ["fog/smoke/dust", "rain FX", "sparks/debris", "fire/explosion", "light bloom/glow"]
MOTION_OPS   = ["smooth motion", "speed ramping", "hyper slow motion", "time lapse"]
CAM_OPS      = ["close-up", "medium shot", "wide shot", "low angle", "over-the-shoulder", "drone view",
                "pan left/right", "tracking shot", "handheld shaky cam", "orbiting shot", "push-in zoom"]
COMP_OPS     = ["rule of thirds", "symmetrical framing", "Dutch angle", "center focus"]
AUDIO_OPS    = ["none", "epic orchestral", "suspenseful low rumble", "soft piano", "trap/electronic"]

def _join_specs(preset, res, fps, cams, lighting, grading, lens, fx, motion, comp, audio):
    """
    Hợp nhất các thông số thành chuỗi kỹ thuật gọn, để ép AI giữ nguyên.
    """
    parts = [
        "8s video", res, fps, preset,
        f"camera: {', '.join(cams)}" if cams else "",
        lighting, f"color grading: {grading}", f"lens/DoF: {lens}",
        f"FX: {fx}", f"motion: {motion}", f"composition: {comp}",
        (f"audio: {audio}" if audio and audio.lower()!="none" else "")
    ]
    return ", ".join([p for p in parts if p])

# ============================== Signals & Workers ===============================
class CheckSignal(QObject):
    finished = Signal(int, dict)

class CheckWorker(QRunnable):
    def __init__(self, row_index: int, cookie_path: str):
        super().__init__()
        self.row_index = row_index
        self.cookie_path = cookie_path
        self.signals = CheckSignal()
    def run(self):
        result = check_cookie_file(self.cookie_path)
        self.signals.finished.emit(self.row_index, result)

class ConfigSignal(QObject):
    finished = Signal(int, dict)

class ConfigureWorker(QRunnable):
    def __init__(self, row_index: int, cookie_path: str, model: str, outputs: int):
        super().__init__()
        self.row_index = row_index
        self.cookie_path = cookie_path
        self.model = model
        self.outputs = outputs
        self.signals = ConfigSignal()
    def run(self):
        try:
            result = configure_flow_project(self.cookie_path, self.model, self.outputs, debug=True)
        except Exception as e:
            result = {"ok": False, "note": str(e), "chosen_model": ""}
        self.signals.finished.emit(self.row_index, result)

class ImageVideoSignal(QObject):
    progress = Signal(int, str)
    done = Signal(int, dict)
    finished = Signal()

class ImageVideoWorker(QRunnable):
    def __init__(self, row: int, cookie_path: str, start_image: str,
                 prompt: str, model: str, outputs: int, out_dir: Path, name_base: str, 
                 timeout: int = 90, retries: int = 2):
        super().__init__()
        self.row = row
        self.cookie_path = cookie_path
        self.start_image = start_image
        self.prompt = prompt
        self.model = model
        self.outputs = outputs
        self.out_dir = out_dir
        self.name_base = name_base
        self.timeout = timeout
        self.retries = max(0, int(retries))
        self.signals = ImageVideoSignal()
    
    def run(self):
        try:
            attempts = max(1, self.retries + 1)
            last_result = {"ok": False, "note": "Unknown error", "video_path": ""}

            for attempt in range(1, attempts + 1):
                def _cb(pct, label):
                    self.signals.progress.emit(self.row, f"{pct}|Attempt {attempt}/{attempts} – {label}")
                self.signals.progress.emit(self.row, f"10|Attempt {attempt}/{attempts} – Starting...")

                result = generate_video_from_image(
                    self.cookie_path, self.start_image, self.prompt,
                    self.model, self.outputs, self.out_dir,
                    timeout=self.timeout, name_base=self.name_base, progress_cb=_cb
                )
                last_result = result
                if result.get("ok"):
                    self.signals.done.emit(self.row, result)
                    return

                if attempt < attempts:
                    self.signals.progress.emit(self.row, f"5|Attempt {attempt}/{attempts} failed – retrying...")
                    time.sleep(min(3 + attempt, 8))

            self.signals.done.emit(self.row, last_result)
        finally:
            self.signals.finished.emit()

class GeminiGenerateSignal(QObject):
    progress = Signal(str)  # status text
    finished = Signal(dict)  # result: {"ok": bool, "data": dict, "error": str}

class GeminiGenerateWorker(QRunnable):
    """Worker để call Gemini API không block UI thread"""
    def __init__(self, generator, is_first_batch: bool, topic: str, num_prompts: int,
                 video_style: str, dialogue_lang: str, subtitles: str):
        super().__init__()
        self.generator = generator
        self.is_first_batch = is_first_batch
        self.topic = topic
        self.num_prompts = num_prompts
        self.video_style = video_style
        self.dialogue_lang = dialogue_lang
        self.subtitles = subtitles
        self.signals = GeminiGenerateSignal()
    
    def run(self):
        try:
            self.signals.progress.emit("🧠 AI đang phân tích chủ đề...")
            
            if self.is_first_batch:
                result = self.generator.generate_first_batch(
                    topic=self.topic,
                    num_prompts=self.num_prompts,
                    video_style=self.video_style,
                    dialogue_lang=self.dialogue_lang,
                    subtitles=self.subtitles
                )
            else:
                self.signals.progress.emit("🧠 AI đang viết tiếp với nhân vật đã có...")
                result = self.generator.generate_next_batch(
                    topic=self.topic,
                    num_prompts=self.num_prompts,
                    video_style=self.video_style,
                    dialogue_lang=self.dialogue_lang,
                    subtitles=self.subtitles
                )
            
            self.signals.finished.emit({
                "ok": True,
                "data": result,
                "error": ""
            })
        except Exception as e:
            self.signals.finished.emit({
                "ok": False,
                "data": {},
                "error": str(e)
            })

# ============================== UI helpers ===============================
class PromptEdit(QTextEdit):
    submitted = Signal()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptRichText(False)
    def keyPressEvent(self, e):
        if (e.key() in (Qt.Key_Return, Qt.Key_Enter)) and (e.modifiers() & Qt.ControlModifier):
            self.submitted.emit(); e.accept(); return
        super().keyPressEvent(e)

class VideoCellWidget(QWidget):
    def __init__(self, video_path: str, parent=None, show_preview: bool = True):
        super().__init__(parent)
        self.video_path = video_path
        self.show_preview = show_preview

        if show_preview:
            # Version có preview (như cũ)
            self.player = QMediaPlayer(self)
            self.audio = QAudioOutput(self)
            self.player.setAudioOutput(self.audio)

            self.view = QVideoWidget(self)
            self.view.setFixedSize(240, 135)
            
            self.player.setVideoOutput(self.view)
            self.player.setSource(Path(video_path).as_uri())

            def _toggle(_e=None):
                st = self.player.playbackState()
                self.player.pause() if st == QMediaPlayer.PlayingState else self.player.play()
            self.view.mousePressEvent = _toggle

            lay = QVBoxLayout(self)
            lay.setContentsMargins(8, 8, 8, 8)
            lay.addWidget(self.view)
        else:
            # Version chỉ hiện label (rất nhẹ)
            label = QLabel("✓ Video Ready")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    background: #dcfce7;
                    border: 2px solid #86efac;
                    border-radius: 8px;
                    padding: 20px;
                    color: #166534;
                    font-weight: 700;
                    font-size: 13px;
                }
            """)
            label.setFixedSize(240, 135)
            
            lay = QVBoxLayout(self)
            lay.setContentsMargins(8, 8, 8, 8)
            lay.addWidget(label)

    def open_os(self):
        p = self.video_path
        if sys.platform.startswith("win"): os.startfile(p)
        else: os.system(f'xdg-open "{p}"')

    def sizeHint(self):
        return QSize(256, 151)
    
    def cleanup(self):
        """Cleanup resources khi widget bị remove"""
        if hasattr(self, 'player'):
            try:
                self.player.stop()
                self.player.setSource("")
                self.player.deleteLater()
            except:
                pass
        if hasattr(self, 'audio'):
            try:
                self.audio.deleteLater()
            except:
                pass

class StatusProgress(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lab_pct = QLabel("0%")
        self.lab_pct.setAlignment(Qt.AlignCenter)
        self.lab_pct.setStyleSheet("font-weight:800; font-size:14px; color:#111827;")

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(14)
        # ← ĐƠN GIẢN HÓA STYLE (bỏ gradient):
        self.bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #d1d5db;
                background: #f9fafb;
                border-radius: 8px;
            }
            QProgressBar::chunk {
                border-radius: 8px;
                background: #3b82f6;  /* ← Màu đơn giản thay vì gradient */
            }
        """)

        self.lab_text = QLabel("waiting")
        self.lab_text.setAlignment(Qt.AlignCenter)
        self.lab_text.setStyleSheet("color:#6b7280; font-size:12px;")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(4)
        lay.addWidget(self.lab_pct)
        lay.addWidget(self.bar)
        lay.addWidget(self.lab_text)

        # NEW: spinner animation
        self._spin_frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
        self._spin_i = 0
        self._spin_timer = QTimer(self)
        self._spin_timer.setInterval(120)
        self._spin_timer.timeout.connect(self._tick_spinner)
        self._base_text = "waiting"
        self._running = False

    def _tick_spinner(self):
        self._spin_i = (self._spin_i + 1) % len(self._spin_frames)
        self._apply_text()

    def _apply_text(self):
        if self._running:
            self.lab_text.setText(f"{self._spin_frames[self._spin_i]}  {self._base_text}")
        else:
            self.lab_text.setText(self._base_text)

    def set_running(self, running: bool):
        self._running = bool(running)
        if self._running:
            if not self._spin_timer.isActive():
                self._spin_timer.start()
        else:
            if self._spin_timer.isActive():
                self._spin_timer.stop()
        self._apply_text()

    def set_progress(self, pct: int, text: str):
        pct = max(0, min(100, int(pct)))
        self.bar.setValue(pct)
        self.lab_pct.setText(f"{pct}%")
        self._base_text = text or ""

        # tô màu nhanh theo trạng thái (dùng objectName)
        t = (text or "").lower()
        if "failed" in t:
            self.lab_pct.setStyleSheet("font-weight:800; font-size:14px; color:#ef4444;")
        elif "saved" in t or pct == 100:
            self.lab_pct.setStyleSheet("font-weight:800; font-size:14px; color:#10b981;")
        else:
            self.lab_pct.setStyleSheet("font-weight:800; font-size:14px; color:#111827;")

        self.set_running(0 < pct < 100 and self._base_text.lower() not in ("queued", "failed", "saved"))

# ============================== License helpers ===============================
def get_current_license_info() -> dict:
    """
    Trả về:
      {
        "has_token": bool, "status": "Valid/Invalid/Missing",
        "device_id": str, "owner": str, "expiry": "YYYY-MM-DD",
        "days_left": int, "message": str
      }
    """
    info = {
        "has_token": False, "status": "Missing",
        "device_id": _get_device_id(), "owner": "-",
        "expiry": "-", "days_left": 0, "message": ""
    }
    pub_bytes = _load_public_key_bytes()
    if not pub_bytes:
        info["status"] = "Invalid"
        info["message"] = "Thiếu public key (PUBLIC_KEY_PEM rỗng)."
        return info

    token = ""
    if APP_LICENSE_FILE.exists():
        try:
            token = APP_LICENSE_FILE.read_text(encoding="utf-8").strip()
        except Exception as e:
            info["message"] = f"Không đọc được file token: {e}"

    if not token:
        info["status"] = "Missing"
        info["message"] = "Chưa có token."
        return info

    info["has_token"] = True

    try:
        did, owner, exp_dt, sig, msg = _parse_pipe_token(token)
        info["owner"] = owner
        info["expiry"] = exp_dt.date().isoformat()

        ok, msgv = verify_license_token(token, pub_bytes, info["device_id"])
        info["status"] = "Valid" if ok else "Invalid"
        info["message"] = msgv

        # days_left (0 nếu đã hết hạn)
        now = datetime.now(timezone.utc)
        info["days_left"] = max(0, (exp_dt - now).days)
        return info

    except Exception as e:
        info["status"] = "Invalid"
        info["message"] = f"Token lỗi: {e}"
        return info
def _get_device_id() -> str:
    """Windows MachineGuid (ưu tiên)."""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as k:
            v, _ = winreg.QueryValueEx(k, "MachineGuid")
        return str(v).strip()
    except Exception:
        # fallback nhẹ nếu không có registry
        import uuid, platform
        return f"{platform.node()}-{uuid.getnode()}"

def _load_public_key_bytes() -> bytes:
    if b"BEGIN PUBLIC KEY" in PUBLIC_KEY_PEM:
        return PUBLIC_KEY_PEM
    return b""

def _parse_pipe_token(token: str):
    """
    Định dạng: DID|OWNER|YYYY-MM-DD|BASE64_SIGNATURE
    """
    parts = (token or "").strip().split("|")
    if len(parts) != 4:
        raise ValueError("Token format invalid")
    did, owner, exp_s, sig_b64 = parts
    did = did.strip(); owner = owner.strip(); exp_s = exp_s.strip()
    if not did or not exp_s or not sig_b64:
        raise ValueError("Token missing fields")
    # kiểm tra ngày
    try:
        exp_dt = datetime.fromisoformat(exp_s).replace(tzinfo=timezone.utc)
    except Exception:
        raise ValueError("Expiry date invalid")
    # tách chữ ký
    try:
        sig = base64.b64decode(sig_b64.encode("ascii"), validate=True)
    except Exception:
        raise ValueError("Signature base64 invalid")
    msg = f"{did}|{owner}|{exp_s}".encode("utf-8")
    return did, owner, exp_dt, sig, msg

def verify_license_token(token: str, pubkey_pem: bytes, device_id: str) -> (bool, str):
    """
    Trả về (ok, message). Nếu ok=False, message là lý do.
    """
    if not hashes or not serialization or not padding:
        return False, "Missing 'cryptography' package"
    try:
        did, owner, exp_dt, sig, msg = _parse_pipe_token(token)
        if did.strip().lower() != (device_id or "").strip().lower():
            return False, "Wrong device ID"
        if exp_dt < datetime.now(timezone.utc):
            return False, "License expired"

        pub = serialization.load_pem_public_key(pubkey_pem)
        pub.verify(sig, msg, padding.PKCS1v15(), hashes.SHA256())
        return True, f"Owner: {owner} • Exp: {exp_dt.date().isoformat()}"
    except Exception as e:
        return False, f"Invalid license: {e}"

class LicenseDialog(QDialog):
    """Hộp thoại nhập/paste token và kích hoạt."""
    def __init__(self, parent=None, device_id: str = "", note: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Activate License")
        self.setMinimumWidth(720)
        lay = QVBoxLayout(self); lay.setContentsMargins(12,12,12,12); lay.setSpacing(8)

        # ==== Device ID + Copy ====
        self.device_id = device_id or ""
        row_did = QHBoxLayout()
        lab_did = QLabel("Device ID:")
        self.le_did = QLineEdit(self.device_id)
        self.le_did.setReadOnly(True)
        self.le_did.setCursorPosition(0)
        self.le_did.setStyleSheet(
            "QLineEdit{border:1px solid #d1d5db; border-radius:8px; padding:6px 8px; background:#f9fafb;}"
        )
        btn_copy_did = QPushButton("Copy")
        btn_copy_did.setToolTip("Copy Device ID vào clipboard")
        btn_copy_did.clicked.connect(self._copy_device_id)

        row_did.addWidget(lab_did)
        row_did.addWidget(self.le_did, 1)
        row_did.addWidget(btn_copy_did)
        lay.addLayout(row_did)

        hint = QLabel("Paste token (Liên hệ email: hungse17002@gmail.com")
        lay.addWidget(hint)

        self.ed = QPlainTextEdit(); self.ed.setPlaceholderText("Dán token tại đây…")
        self.ed.setMinimumHeight(130)
        lay.addWidget(self.ed)

        row = QHBoxLayout()
        btn_paste = QPushButton("Paste")
        btn_load  = QPushButton("Load từ file…")
        row.addWidget(btn_paste); row.addWidget(btn_load); row.addStretch(1)
        lay.addLayout(row)

        self.msg = QLabel(note or "")
        self.msg.setStyleSheet("color:#6b7280;")
        lay.addWidget(self.msg)

        bb = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        lay.addWidget(bb)

        btn_paste.clicked.connect(lambda: self.ed.setPlainText(QApplication.clipboard().text()))
        def _load_file():
            p, _ = QFileDialog.getOpenFileName(self, "Chọn token", "", "Text (*.txt);;All files (*)")
            if p:
                try:
                    self.ed.setPlainText(Path(p).read_text(encoding="utf-8").strip())
                except Exception as e:
                    QMessageBox.warning(self, "Load failed", str(e))
        btn_load.clicked.connect(_load_file)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)

    def _copy_device_id(self):
        if not self.device_id:
            QMessageBox.information(self, "Info", "Chưa có Device ID.")
            return
        QApplication.clipboard().setText(self.device_id)
        self.msg.setText("Device ID copied ✓")
        
    def token(self) -> str:
        return (self.ed.toPlainText() or "").strip()
# ============================== Main Window ===============================
class _RowOutlineOverlay(QWidget):
    """Overlay vẽ viền bo tròn cho toàn bộ hàng trên QTableWidget (không phủ nền)."""
    def __init__(self, table: QTableWidget):
        super().__init__(table.viewport())
        self.table = table
        self.rows: set[int] = set()
        self.hue = 0
        self.timer = QTimer(self)
        self.timer.setInterval(60)
        self.timer.timeout.connect(self._tick)

        # cho vẽ đè mà không chặn chuột
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(table.viewport().size())
        self.show()
        self.raise_()

        # theo dõi viewport để overlay bám đúng kích thước/scroll
        table.viewport().installEventFilter(self)
        self.table.verticalScrollBar().valueChanged.connect(lambda _=None: self.update())
        self.table.horizontalScrollBar().valueChanged.connect(lambda _=None: self.update())
        
    def eventFilter(self, obj, ev):
        if obj is self.table.viewport() and ev.type() == QEvent.Resize:
            self.resize(obj.size())
            self.raise_()
        return False

    def _tick(self):
        self.hue = (self.hue + 8) % 360
        self.update()

    def _h2rgb(self, h: float):
        x = 6*h; c = 255
        if   x < 1: r,g,b = c, int(c*x), 0
        elif x < 2: r,g,b = int(c*(2-x)), c, 0
        elif x < 3: r,g,b = 0, c, int(c*(x-2))
        elif x < 4: r,g,b = 0, int(c*(4-x)), c
        elif x < 5: r,g,b = int(c*(x-4)), 0, c
        else:        r,g,b = c, 0, int(c*(6-x))
        return r,g,b

    def set_row_active(self, row: int, active: bool):
        if active: self.rows.add(row)
        else: self.rows.discard(row)
        if self.rows and not self.timer.isActive(): self.timer.start()
        if not self.rows and self.timer.isActive(): self.timer.stop()
        self.update()

    def paintEvent(self, _ev):
        if not self.rows: return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        # 2 màu gradient cho nét viền
        h1 = (self.hue % 360)/360.0
        h2 = ((self.hue+60) % 360)/360.0
        r1,g1,b1 = self._h2rgb(h1)
        r2,g2,b2 = self._h2rgb(h2)

        # tìm cột hữu hình đầu/cuối để bao trọn hàng
        first_col = 0
        last_col  = self.table.columnCount()-1

        for row in list(self.rows):
            # lấy bound theo các cột đang hiển thị trong viewport
            left = None; right = None; top=None; bottom=None
            for c in range(self.table.columnCount()):
                if self.table.isColumnHidden(c): continue
                idx = self.table.model().index(row, c)
                rect = self.table.visualRect(idx)
                if not rect.isValid() or rect.width()==0 or rect.height()==0: continue
                if left is None or rect.left() < left: left = rect.left()
                if right is None or rect.right() > right: right = rect.right()
                if top is None or rect.top() < top: top = rect.top()
                if bottom is None or rect.bottom() > bottom: bottom = rect.bottom()

            if left is None:  # hàng đang ẩn/ngoài viewport
                continue

            # khung bo tròn bao cả hàng, chừa một chút đệm
            rect = QRect(int(left)-3, int(top)-3, int(right-left)+6, int(bottom-top)+6)

            grad = QLinearGradient(rect.left(), rect.top(), rect.right(), rect.top())
            grad.setColorAt(0.0, QColor(r1, g1, b1))
            grad.setColorAt(1.0, QColor(r2, g2, b2))
            pen = QPen(grad, 2.0)
            p.setPen(pen)
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(rect, 10, 10)
# >>> NEW: APIKeyPool quản lý nhiều key & xoay khi lỗi
class APIKeyPool:
    def __init__(self, keys: List[str] | None = None, rotate_on_fail: bool = True, base_url: str = "https://api.groq.com/openai/v1"):
        self.keys = [k.strip() for k in (keys or []) if k.strip()]
        self.rotate = bool(rotate_on_fail)
        self.i = 0
        self.base_url = base_url

    def has_keys(self) -> bool:
        return len(self.keys) > 0

    def current(self) -> Optional[str]:
        if not self.keys: return None
        return self.keys[self.i % len(self.keys)]

    def next(self):
        if self.keys:
            self.i = (self.i + 1) % len(self.keys)

    def headers(self, key: Optional[str] = None) -> Dict[str,str]:
        k = key or self.current()
        return {"Authorization": f"Bearer {k}", "Content-Type": "application/json"}

    def get(self, path: str) -> tuple[Optional[dict], dict, int, str]:
        if not requests: raise RuntimeError("Thiếu 'requests'. Hãy: pip install requests")
        url = self.base_url.rstrip("/") + path
        last_err = ""
        tried = 0
        total = max(1, len(self.keys))
        while tried < total:
            k = self.current()
            try:
                r = requests.get(url, headers=self.headers(k), timeout=15)
                if r.status_code == 200:
                    return r.json(), r.headers, r.status_code, k
                if r.status_code in (401, 403, 429, 500, 503) and self.rotate and total > 1:
                    last_err = f"{r.status_code}: {r.text[:180]}"
                    self.next(); tried += 1; continue
                return None, r.headers, r.status_code, k
            except Exception as e:
                last_err = str(e)
                if self.rotate and total > 1:
                    self.next(); tried += 1; continue
                raise
        raise RuntimeError(f"Tất cả API key đều lỗi: {last_err}")

    def post(self, path: str, json_body: dict) -> tuple[dict, dict, int, str]:
        if not requests: raise RuntimeError("Thiếu 'requests'. Hãy: pip install requests")
        url = self.base_url.rstrip("/") + path
        last_err = ""
        tried = 0; total = max(1, len(self.keys))
        while tried < total:
            k = self.current()
            try:
                r = requests.post(url, headers=self.headers(k), json=json_body, timeout=40)
                if r.status_code == 200:
                    return r.json(), r.headers, r.status_code, k
                # xoay key khi cần
                if r.status_code in (401, 403, 429, 500, 503) and self.rotate and total > 1:
                    last_err = f"{r.status_code}: {r.text[:180]}"
                    self.next(); tried += 1; continue
                raise RuntimeError(f"Groq API error {r.status_code}: {r.text[:300]}")
            except Exception as e:
                last_err = str(e)
                if self.rotate and total > 1:
                    self.next(); tried += 1; continue
                raise RuntimeError(last_err)
        raise RuntimeError(f"Tất cả API key đều lỗi: {last_err}")

# >>> NEW: Gemini API Pool
class GeminiKeyPool:
    def __init__(self, keys: List[str] | None = None, rotate_on_fail: bool = True):
        self.keys = [k.strip() for k in (keys or []) if k.strip()]
        self.rotate = bool(rotate_on_fail)
        self.i = 0
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    def has_keys(self) -> bool:
        return len(self.keys) > 0

    def current(self) -> Optional[str]:
        if not self.keys: return None
        return self.keys[self.i % len(self.keys)]

    def next(self):
        if self.keys:
            self.i = (self.i + 1) % len(self.keys)

    def generate_content(self, model: str, prompt: str) -> tuple[str, int, str]:
        if not requests:
            raise RuntimeError("Thiếu 'requests'. Hãy pip install requests")
        
        last_err = ""
        tried, total = 0, max(1, len(self.keys))
        
        while tried < total:
            key = self.current()
            url = f"{self.base_url}/{model}:generateContent?key={key}"
            
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 8192}
            }
            
            try:
                r = requests.post(url, json=payload, timeout=60)
                if r.status_code == 200:
                    data = r.json()
                    text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    return text, r.status_code, key
                
                if r.status_code in (400, 403, 429, 500, 503) and self.rotate and total > 1:
                    last_err = f"{r.status_code}: {r.text[:180]}"
                    self.next(); tried += 1; continue
                    
                raise RuntimeError(f"Gemini error {r.status_code}: {r.text[:300]}")
            except Exception as e:
                last_err = str(e)
                if self.rotate and total > 1:
                    self.next(); tried += 1; continue
                raise RuntimeError(last_err)
        
        raise RuntimeError(f"Tất cả Gemini key đều lỗi: {last_err}")

class GeminiScriptGenerator:
    """
    Sinh kịch bản cho Veo theo 2 pha:
      - First batch: tạo 'characterAnalysis' + 'script'
      - Next batch: chỉ tạo 'script' dựa trên characterAnalysis đã có + ngữ cảnh prompt cuối
    Sử dụng GeminiKeyPool.generate_content(model, prompt) -> (text, code, key)
    """

    def __init__(self, pool, model: str = "gemini-2.0-flash"):
        self.pool = pool
        self.model = model
        # Trạng thái tích lũy giữa các batch
        self._character_analysis: List[Dict[str, Any]] = []
        self._last_prompt_text: str = ""
        self._last_scene_number: int = 0  # ← THÊM: track số scene cuối cùng

    # ========== PUBLIC API ==========

    def generate_script(
        self,
        topic: str,
        num_prompts: int,
        video_style: str,
        dialogue_lang: str,
        subtitles: str
    ) -> Dict[str, Any]:
        """
        API cũ: luôn hành xử như batch đầu tiên.
        Trả về JSON có 2 key: 'characterAnalysis' (array) và 'script' (array[str]).
        """
        data = self.generate_first_batch(topic, num_prompts, video_style, dialogue_lang, subtitles)
        return data

    def generate_first_batch(
        self,
        topic: str,
        num_prompts: int,
        video_style: str,
        dialogue_lang: str,
        subtitles: str
    ) -> Dict[str, Any]:
        """
        Batch đầu tiên: yêu cầu model phân tích nhân vật + sinh script.
        Lưu 'characterAnalysis' dùng cho batch tiếp theo.
        """
        master_prompt = self._build_master_prompt(
            topic=topic,
            num_prompts=num_prompts,
            video_style=video_style,
            dialogue_lang=dialogue_lang,
            subtitles=subtitles,
            is_first_batch=True,
            existing_characters=None,
            last_prompt_text="",
            start_scene_number=1  # ← THÊM
        )
        text, code, key = self.pool.generate_content(self.model, master_prompt)
        data = self._extract_json(text)

        # Kiểm tra và lấy characterAnalysis + script
        script = data.get("script")
        if not isinstance(script, list) or not script:
            raise ValueError("Response không có 'script' array hợp lệ")

        char_anal = data.get("characterAnalysis", [])
        if not isinstance(char_anal, list):
            char_anal = []

        self._character_analysis = char_anal
        self._last_prompt_text = script[-1] if script else ""
        self._last_scene_number = len(script)  # ← THÊM: lưu số scene cuối

        return {"characterAnalysis": self._character_analysis, "script": script}

    def generate_next_batch(
        self,
        topic: str,
        num_prompts: int,
        video_style: str,
        dialogue_lang: str,
        subtitles: str
    ) -> Dict[str, Any]:
        """
        Batch tiếp theo: KHÔNG yêu cầu phân tích nhân vật nữa.
        Sử dụng lại self._character_analysis + self._last_prompt_text.
        Trả về JSON có 'characterAnalysis' = [] (rỗng) và 'script' (array[str]).
        """
        if not self._character_analysis:
            raise RuntimeError(
                "Chưa có characterAnalysis. Hãy gọi generate_first_batch() trước khi tiếp tục."
            )

        # ← THÊM: tính scene bắt đầu cho batch mới
        start_scene = self._last_scene_number + 1

        master_prompt = self._build_master_prompt(
            topic=topic,
            num_prompts=num_prompts,
            video_style=video_style,
            dialogue_lang=dialogue_lang,
            subtitles=subtitles,
            is_first_batch=False,
            existing_characters=self._character_analysis,
            last_prompt_text=self._last_prompt_text or "",
            start_scene_number=start_scene  # ← THÊM
        )
        text, code, key = self.pool.generate_content(self.model, master_prompt)
        data = self._extract_json(text)

        script = data.get("script")
        if not isinstance(script, list) or not script:
            raise ValueError("Response batch tiếp theo không có 'script' hợp lệ")

        # Tích lũy ngữ cảnh cho lần kế tiếp
        self._last_prompt_text = script[-1]
        self._last_scene_number += len(script)  # ← THÊM: cộng dồn

        # Theo spec: batch tiếp theo 'characterAnalysis' phải là []
        return {"characterAnalysis": [], "script": script}

    # ========== INTERNAL HELPERS ==========

    def _extract_json(self, raw_text: str) -> Dict[str, Any]:
        """
        Chuẩn hóa & parse JSON từ model - FIXED for newlines in strings
        """
        if not isinstance(raw_text, str):
            raise RuntimeError("Phản hồi model không phải string")

        # Remove markdown code blocks
        cleaned = raw_text.replace("```json", "").replace("```", "").strip()
        
        # NEW: Escape unescaped newlines inside JSON string values
        # This regex finds newlines that are inside quotes but not already escaped
        import re
        def escape_newlines_in_strings(match):
            """Replace actual newlines with \\n inside quoted strings"""
            content = match.group(0)
            # Replace unescaped newlines
            content = content.replace('\n', '\\n').replace('\r', '\\r')
            return content
        
        # Match quoted strings and escape newlines inside them
        # This pattern matches: "..." including escaped quotes
        cleaned = re.sub(
            r'"(?:[^"\\]|\\.)*"',
            escape_newlines_in_strings,
            cleaned,
            flags=re.DOTALL
        )
        
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            # Fallback: try to extract JSON object boundaries
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    data = json.loads(cleaned[start:end + 1])
                except Exception:
                    raise RuntimeError(f"Gemini trả JSON không hợp lệ: {e}\nRaw:\n{raw_text[:1000]}")
            else:
                raise RuntimeError(f"Gemini trả JSON không hợp lệ: {e}\nRaw:\n{raw_text[:1000]}")

        if not isinstance(data, dict):
            raise RuntimeError("JSON trả về không phải object (dict)")

        return data

    def _build_master_prompt(
        self,
        topic: str,
        num_prompts: int,
        video_style: str,
        dialogue_lang: str,
        subtitles: str,
        is_first_batch: bool,
        existing_characters: Optional[List[Dict[str, Any]]],
        last_prompt_text: str,
        start_scene_number: int  # ← THÊM parameter
    ) -> str:
        """
        Enhanced prompt với tính đồng nhất nhân vật và cảnh cao nhất
        """
        parts: List[str] = []
        parts.append(
            'You are an expert scriptwriter and prompt engineer for "Veo3" AI. '
            'Your PRIMARY objective is to maintain ABSOLUTE CONSISTENCY across all visual elements, characters, and scenes.'
        )

        if is_first_batch:
            parts.append("**PHASE 1: CHARACTER DEFINITION**")
            parts.append("First, create a comprehensive character analysis that will serve as the IMMUTABLE reference for all future prompts.")
            parts.append("**PHASE 2: INITIAL SCRIPT GENERATION**")
            parts.append("Then, generate the first batch of prompts using EXACT character descriptions.")
        else:
            parts.append("**CONTINUATION MODE: Maintaining Perfect Consistency**")
            parts.append("You MUST use the existing character analysis WITHOUT any modifications. Every character appearance must be IDENTICAL to previous scenes.")
            # ← THÊM: thông báo số scene bắt đầu
            parts.append(f"\n⚠️ **CRITICAL: Start scene numbering from Scene {start_scene_number}** (continue from previous batch)")

        parts.append("\n═══════════════════════════════════════════════════════")
        parts.append("📋 USER REQUIREMENTS:")
        parts.append("═══════════════════════════════════════════════════════")
        parts.append(f"• Topic/Story: {topic}")
        parts.append(f"• Prompts in THIS batch: {num_prompts}")
        parts.append(f"• Prompts in THIS batch: {num_prompts}")

        # THÊM ĐOẠN NÀY
        if num_prompts > 15:
            parts.append("""
        ⚠️⚠️⚠️ CRITICAL FOR LARGE BATCHES ⚠️⚠️⚠️
        You are generating many prompts. This increases JSON formatting errors.
        EXTRA CARE REQUIRED:
        - NO actual line breaks inside any JSON string value
        - Use \\n for line breaks, \\" for quotes
        - Double-check every character description contains NO unescaped newlines
        - If a description is long, still keep it on ONE line using \\n
        """)
        # ← THÊM: hiển thị range scene
        if is_first_batch:
            parts.append(f"• Scene numbers: 1 to {num_prompts}")
        else:
            parts.append(f"• Scene numbers: {start_scene_number} to {start_scene_number + num_prompts - 1}")
        parts.append(f"• Visual Style: {video_style}")
        parts.append(f"• Dialogue Language: {dialogue_lang}")
        parts.append(f"• Subtitles: {subtitles}")

        # ... (giữ nguyên phần còn lại của prompt, chỉ sửa phần scene numbering)
        
        parts.append("\n═══════════════════════════════════════════════════════")
        parts.append('📝 OUTPUT FORMAT: JSON with "characterAnalysis" and "script"')
        parts.append("═══════════════════════════════════════════════════════")

        if is_first_batch:
            parts.append("""
    **1. characterAnalysis** (First Batch Only):
    [... giữ nguyên phần character analysis ...]
    """)
        else:
            parts.append("1. characterAnalysis: MUST be an EMPTY array []")
            parts.append("\n" + "=" * 60)
            parts.append("🔒 LOCKED CHARACTER PROFILES (DO NOT MODIFY):")
            parts.append("=" * 60)
            parts.append(json.dumps(existing_characters or [], ensure_ascii=False, indent=2))
            parts.append("\n⚠️ CRITICAL: Copy these descriptions WORD-FOR-WORD in every prompt.")

            if last_prompt_text:
                parts.append("\n" + "=" * 60)
                parts.append("🎬 PREVIOUS SCENE CONTEXT:")
                parts.append("=" * 60)
                parts.append(f"{last_prompt_text}")

        # ← SỬA: phần scene numbering trong prompt format
        parts.append(f"""
    2. script: Generate {num_prompts} HIGHLY CONSISTENT prompts

    ═══════════════════════════════════════════════════════
    📐 PROMPT STRUCTURE (Pipe-delimited format):
    ═══════════════════════════════════════════════════════
    Scene [Number] – [Brief Title] | [Character 1: FULL VERBATIM Description] | ...
    
    ⚠️ **SCENE NUMBERING**: {'Start from Scene 1' if is_first_batch else f'Start from Scene {start_scene_number} and continue sequentially'}
    
    MANDATORY FOR EACH PART:

    Scene Number & Title: Keep it brief, descriptive
    Character Descriptions: COPY-PASTE from character analysis - include physical appearance, clothing, and visual identifier
    Style: Explicitly state "{video_style}" to maintain visual coherence
    Voices: Use exact voice descriptions from character analysis
    Camera: Be specific (e.g., "Medium close-up, eye-level, slow dolly-in")
    Setting: Include: location + time of day + lighting conditions + weather (if outdoor)
    Mood: Emotional atmosphere
    Audio: Background sounds, music style
    Dialog: MUST be in {dialogue_lang} - natural conversation
    Subtitles: MUST be {subtitles}

    ═══════════════════════════════════════════════════════
    ✅ QUALITY CHECKLIST (Verify each prompt):
    ═══════════════════════════════════════════════════════
    □ All character physical descriptions are IDENTICAL to character analysis
    □ Visual identifiers are present for each character
    □ Clothing matches previous prompts (unless story requires change)
    □ Scene flows logically from the previous one
    □ Time of day/lighting is consistent or logically progresses
    □ Location details match previous scene if in same place
    □ Camera style aligns with overall video style
    □ All sections of pipe-delimited format are complete
    ═══════════════════════════════════════════════════════
    ⚠️ CRITICAL WARNINGS:
    ═══════════════════════════════════════════════════════

    DO NOT simplify character descriptions - use FULL details every time
    DO NOT use pronouns like "the man" or "she" - always use full descriptions
    DO NOT vary descriptive language - consistency > stylistic variation
    DO NOT skip any section of the prompt format
    DO NOT add markdown, code blocks, or text outside the JSON object

    ═══════════════════════════════════════════════════════
    📤 OUTPUT: Pure JSON only (no markdown, no extra text)
    ═══════════════════════════════════════════════════════
    """
        )

        return "\n".join(parts)

# >>> NEW: PromptGenerator gọi Chat Completions (OpenAI-compatible)
class PromptGenerator:
    def __init__(self, pool: APIKeyPool, model: str = "llama-3.1-8b-instant"):
        self.pool = pool
        self.model = model

    def generate(self, topic: str, preset: str, spec_text: str, n: int = 3) -> List[str]:
        """
        Yêu cầu model trả về JSON: {"prompts": ["...", "..."]}.
        Mỗi prompt ~3-4 câu (ngắn gọn), kết thúc bằng ' — Technical: <spec_text>'.
        """
        topic = (topic or "").strip()
        if not topic:
            raise ValueError("Topic rỗng.")

        # Fallback không dùng API (khi chưa cài requests / chưa có key)
        if not self.pool or not self.pool.has_keys() or not requests:
            seeds = [
                "cinematic push-in on subject, crowd reactions, a beat of silence before impact",
                "slow reveal, eye contact, micro‑expression shift, background murmurs build tension",
                "dynamic parallax, quick cut to hands/eyes, breath frosting in air"
            ]
            outs = []
            for i in range(max(1, n)):
                s = seeds[i % len(seeds)]
                outs.append(f"{preset} — {topic}, {s}. — Technical: {spec_text}")
            return outs

        sys_prompt = (
            "You are a world-class prompt engineer specialized in short AI video generation. "
            "Task: generate prompts for exactly 8-second clips. "
            "Requirements:\n"
            "- Each prompt must be 5–7 sentences, concise yet vivid.\n"
            "- Write in cinematic style: include subject, environment, action, and mood.\n"
            "- Always use strong camera verbs (e.g., pan, zoom, tracking shot, close-up, wide shot...).\n"
            "- Add sensory details (lighting, atmosphere, sound, color) to enhance immersion.\n"
            "- Every prompt must be distinct: vary angle, mood, or scene to avoid repetition.\n"
            "- DO NOT invent or modify any technical specifications.\n"
            "- Always end the prompt with an em dash followed by the exact specs string: — Technical: <specs>\n\n"
            "Output format:\n"
            "{ \"prompts\": [\"...\"] }\n\n"
            "⚠️ STRICT RULES:\n"
            "- Return pure JSON only, no markdown, no code fences, no explanations.\n"
            "- JSON must be 100% valid and directly parseable."
        )


        user_prompt = (
            f"Topic: {topic}\n"
            f"Style preset: {preset}\n"
            f"Specs (use verbatim in the Technical section): {spec_text}\n"
            f"Return {max(1,n)} distinct prompts."
        )

        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": sys_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            "temperature": 0.7,
        }
        data, headers, _, _ = self.pool.post("/chat/completions", body)
        content = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
        try:
            obj = json.loads(content)
            arr = obj.get("prompts") or []
            arr = [str(x).strip() for x in arr if str(x).strip()]
            # chốt: đảm bảo Technical spec có trong từng dòng
            fixed = []
            for x in arr:
                if "Technical:" not in x:
                    fixed.append(f"{x.rstrip('.')}. — Technical: {spec_text}")
                else:
                    fixed.append(x)
            return fixed[:max(1, n)]
        except Exception:
            # nếu model không trả JSON sạch -> tách theo dòng
            lines = [l.strip("-• \n\r\t") for l in content.splitlines() if l.strip()]
            outs = []
            for l in lines:
                if not l: continue
                if "Technical:" not in l:
                    outs.append(f"{l.rstrip('.')}. — Technical: {spec_text}")
                else:
                    outs.append(l)
            return outs[:max(1, n)] if outs else [f"{preset} — {topic}. — Technical: {spec_text}"]
# >>> NEW: Popup Tạo Prompt
class PromptBuilderDialog(QDialog):
    def __init__(self, parent=None, key_pool: Optional[APIKeyPool]=None, llm_model: str="llama-3.1-8b-instant", default_mode: str="text"):
        super().__init__(parent)
        self.setWindowTitle("Tạo Prompt 8s")
        self.setMinimumWidth(720)
        self._prompts: List[str] = []
        self._pool = key_pool
        self._model = llm_model
        self._mode = default_mode  # "text" hoặc "image"

        lay = QVBoxLayout(self); lay.setContentsMargins(12,12,12,12); lay.setSpacing(8)

        form = QFormLayout()
        self.ed_topic = QLineEdit()
        self.cmb_style = QComboBox(); self.cmb_style.addItems(STYLE_PRESETS)
        self.cmb_res   = QComboBox(); self.cmb_res.addItems(RES_OPTIONS);  self.cmb_res.setCurrentIndex(1)  # 4K mặc định
        self.cmb_fps   = QComboBox(); self.cmb_fps.addItems(FPS_OPTIONS);  self.cmb_fps.setCurrentIndex(0)  # 24fps

        self.cmb_cam   = QComboBox(); self.cmb_cam.addItems(CAM_OPS); self.cmb_cam.setEditable(True)  # cho phép nhập nhiều, cách nhau dấu phẩy
        self.cmb_light = QComboBox(); self.cmb_light.addItems(LIGHTING_OPS)
        self.cmb_grade = QComboBox(); self.cmb_grade.addItems(GRADING_OPS)
        self.cmb_lens  = QComboBox(); self.cmb_lens.addItems(LENS_OPS)
        self.cmb_fx    = QComboBox(); self.cmb_fx.addItems(FX_OPS)
        self.cmb_motion= QComboBox(); self.cmb_motion.addItems(MOTION_OPS)
        self.cmb_comp  = QComboBox(); self.cmb_comp.addItems(COMP_OPS)
        self.cmb_audio = QComboBox(); self.cmb_audio.addItems(AUDIO_OPS)

        self.spin_n = QSpinBox(); self.spin_n.setRange(1, 20); self.spin_n.setValue(4)

        form.addRow("Topic:", self.ed_topic)
        form.addRow("Preset style:", self.cmb_style)
        form.addRow("Resolution:", self.cmb_res)
        form.addRow("Frame rate:", self.cmb_fps)
        form.addRow("Camera (có thể nhập nhiều, phẩy):", self.cmb_cam)
        form.addRow("Lighting:", self.cmb_light)
        form.addRow("Color grading:", self.cmb_grade)
        form.addRow("Lens / DoF:", self.cmb_lens)
        form.addRow("FX:", self.cmb_fx)
        form.addRow("Motion:", self.cmb_motion)
        form.addRow("Composition:", self.cmb_comp)
        form.addRow("Audio:", self.cmb_audio)
        form.addRow("Số lượng prompts:", self.spin_n)
        lay.addLayout(form)

        self.preview = QPlainTextEdit(); self.preview.setReadOnly(True)
        self.preview.setPlaceholderText("Preview các prompt sinh ra sẽ hiển thị tại đây…")
        lay.addWidget(self.preview, 1)

        row = QHBoxLayout()
        self.btn_gen = QPushButton("Generate"); self.btn_gen.setObjectName("btn-primary")
        self.btn_use = QPushButton("Use");      self.btn_use.setObjectName("btn-accent")
        self.btn_copy= QPushButton("Copy All"); self.btn_copy.setObjectName("btn-teal")
        self.btn_cancel = QPushButton("Cancel"); self.btn_cancel.setObjectName("btn-ghost")
        row.addWidget(self.btn_gen); row.addWidget(self.btn_use); row.addWidget(self.btn_copy); row.addStretch(1); row.addWidget(self.btn_cancel)
        lay.addLayout(row)

        self.btn_gen.clicked.connect(self.on_generate)
        self.btn_use.clicked.connect(self.on_use)
        self.btn_copy.clicked.connect(lambda: QApplication.clipboard().setText("\n\n".join(self._prompts)))
        self.btn_cancel.clicked.connect(self.reject)

    def _collect_spec(self) -> tuple[str, str]:
        preset = self.cmb_style.currentText()
        cams = [c.strip() for c in (self.cmb_cam.currentText() or "").split(",") if c.strip()]
        spec = _join_specs(
            preset=preset,
            res=self.cmb_res.currentText(),
            fps=self.cmb_fps.currentText(),
            cams=cams,
            lighting=self.cmb_light.currentText(),
            grading=self.cmb_grade.currentText(),
            lens=self.cmb_lens.currentText(),
            fx=self.cmb_fx.currentText(),
            motion=self.cmb_motion.currentText(),
            comp=self.cmb_comp.currentText(),
            audio=self.cmb_audio.currentText(),
        )
        return preset, spec

    def on_generate(self):
        topic = self.ed_topic.text().strip()
        if not topic:
            QMessageBox.information(self, "Info", "Vui lòng nhập Topic.")
            return
        preset, spec = self._collect_spec()
        n = int(self.spin_n.value())
        try:
            gen = PromptGenerator(self._pool, self._model)
            self._prompts = gen.generate(topic, preset, spec, n=n)
            self.preview.setPlainText("\n\n".join(f"- {p}" for p in self._prompts))
        except Exception as e:
            QMessageBox.warning(self, "Generate failed", str(e))

    def on_use(self):
        if not self._prompts:
            self.on_generate()
            if not self._prompts:
                return
        self.accept()

    def output_prompts(self) -> List[str]:
        return list(self._prompts)
class GeminiPromptDialog(QDialog):
    def __init__(self, parent=None, gemini_pool: Optional[GeminiKeyPool] = None):
        super().__init__(parent)
        self.setWindowTitle("Generate Prompt Pro (Gemini)")
        self.setMinimumWidth(900)
        self.resize(920, 720)
        self._pool = gemini_pool
        self._output_script: List[str] = []
        self._generator = None  # ← THÊM: Giữ generator instance để continue
        
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)
        
        header = QLabel("🎬 AI Script Generator - Gemini Pro")
        header.setStyleSheet("font-size:20px; font-weight:900;")
        root.addWidget(header)
        
        form = QFormLayout()
        
        self.ed_topic = QTextEdit()
        self.ed_topic.setPlaceholderText("Ví dụ: Thỏ Nhỏ Biết Xin Lỗi. Thông điệp: Dũng cảm nhận lỗi...")
        self.ed_topic.setMinimumHeight(100)
        form.addRow("Chủ đề / Tóm tắt:", self.ed_topic)
        
        self.spin_num = QSpinBox()
        self.spin_num.setRange(1, 50)
        self.spin_num.setValue(10)
        form.addRow("Số lượng prompt:", self.spin_num)
        
        self.cmb_style = QComboBox()
        styles = [
            ("Photorealistic", "Photorealistic (Chân thực)"),
            ("Cinematic", "Cinematic (Điện ảnh)"),
            ("Vlog", "Vlog (Nhật ký)"),
            ("Documentary", "Documentary (Tài liệu)"),
            ("History", "History (Lịch sử)"),
            ("Tutorial", "Tutorial (Hướng dẫn)"),
            ("3D Animation", "3D Animation (Hoạt hình 3D)"),
            ("2D Animation", "2D Animation (Hoạt hình 2D)"),
            ("Anime", "Anime (Hoạt hình Nhật Bản)"),
            ("Music Video", "Music Video (Video nhạc)"),
            ("Commercial", "Commercial (Quảng cáo)"),
            ("Time-lapse", "Time-lapse (Tua nhanh)"),
            ("Slow Motion", "Slow Motion (Chuyển động chậm)"),
            ("Drone Footage", "Drone Footage (Quay từ flycam)"),
            ("Vintage / Retro", "Vintage / Retro (Cổ điển)"),
            ("Sci-Fi", "Sci-Fi (Khoa học viễn tưởng)"),
            ("Fantasy", "Fantasy (Kỳ ảo)"),
            ("Horror", "Horror (Kinh dị)"),
            ("Action", "Action (Hành động)"),
            ("Minimalist", "Minimalist (Tối giản)"),
            ("Nature", "Nature (Thiên nhiên)"),
        ]
        for value, label_vi in styles:
            self.cmb_style.addItem(label_vi, value)
        idx_default = self.cmb_style.findData("3D Animation")
        self.cmb_style.setCurrentIndex(idx_default if idx_default >= 0 else 0)
        form.addRow("Phong cách video:", self.cmb_style)
        
        self.cmb_lang = QComboBox()
        self.cmb_lang.addItems(["English", "Vietnamese", "None"])
        form.addRow("Ngôn ngữ hội thoại:", self.cmb_lang)
        
        self.cmb_sub = QComboBox()
        self.cmb_sub.addItems(["Off", "On"])
        form.addRow("Phụ đề:", self.cmb_sub)
        
        root.addLayout(form)
        
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText("Preview script...")
        root.addWidget(self.preview, 1)
        
        btn_row = QHBoxLayout()
        self.btn_gen = QPushButton("✨ Generate Script")
        self.btn_gen.setObjectName("btn-primary")
        
        # ← THÊM: Nút Continue
        self.btn_continue = QPushButton("➕ Continue Script")
        self.btn_continue.setObjectName("btn-accent")
        self.btn_continue.setEnabled(False)
        self.btn_continue.setToolTip("Generate thêm prompts với cùng nhân vật đã phân tích")
        
        self.btn_use = QPushButton("Use")
        self.btn_use.setObjectName("btn-accent")
        self.btn_copy = QPushButton("Copy All")
        self.btn_copy.setObjectName("btn-teal")
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setObjectName("btn-ghost")
        
        for b in (self.btn_gen, self.btn_continue, self.btn_use, self.btn_copy, self.btn_cancel):
            b.setMinimumHeight(40)
        
        btn_row.addWidget(self.btn_gen)
        btn_row.addWidget(self.btn_continue)  # ← THÊM vào layout
        btn_row.addWidget(self.btn_use)
        btn_row.addWidget(self.btn_copy)
        btn_row.addStretch(1)
        btn_row.addWidget(self.btn_cancel)
        root.addLayout(btn_row)
        
        self.btn_gen.clicked.connect(self._on_generate)
        self.btn_continue.clicked.connect(self._on_continue)  # ← THÊM handler
        self.btn_use.clicked.connect(self._on_use)
        self.btn_copy.clicked.connect(lambda: QApplication.clipboard().setText("\n\n".join(self._output_script)))
        self.btn_cancel.clicked.connect(self.reject)
    def _on_generate(self):
            topic = self.ed_topic.toPlainText().strip()
            if not topic:
                QMessageBox.information(self, "Info", "Vui lòng nhập chủ đề.")
                return
            if not self._pool or not self._pool.has_keys():
                QMessageBox.warning(self, "Error", "Chưa có Gemini API key. Vào Settings.")
                return
            
            self.btn_gen.setEnabled(False)
            self.btn_gen.setText("🧠 AI đang viết...")
            self.btn_continue.setEnabled(False)
            
            try:
                # Tạo generator instance mới (reset state)
                self._generator = GeminiScriptGenerator(self._pool, model="gemini-2.0-flash")
                
                # Dùng API mới: generate_first_batch
                result = self._generator.generate_first_batch(
                    topic=topic, 
                    num_prompts=self.spin_num.value(),
                    video_style=self.cmb_style.currentData(),  # ← Dùng data (value) thay vì text
                    dialogue_lang=self.cmb_lang.currentText(),
                    subtitles=self.cmb_sub.currentText()
                )
                
                self._output_script = result.get("script", [])
                chars = result.get("characterAnalysis", [])
                
                preview = f"=== Characters ({len(chars)}) ===\n"
                for c in chars:
                    preview += f"\n{c.get('name', '?')}: {c.get('description', '')[:80]}...\n"
                preview += f"\n\n=== Script ({len(self._output_script)}) ===\n\n"
                preview += "\n\n".join(f"{i+1}. {p[:150]}..." for i, p in enumerate(self._output_script))
                
                self.preview.setPlainText(preview)
                
                # Bật nút Continue sau khi có first batch thành công
                self.btn_continue.setEnabled(True)
                
                QMessageBox.information(self, "Success", f"Đã tạo {len(self._output_script)} prompts!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Lỗi: {e}")
            finally:
                self.btn_gen.setEnabled(True)
                self.btn_gen.setText("✨ Generate Script")
    def _on_continue(self):
            """Generate thêm batch tiếp theo với cùng character analysis"""
            if not self._generator:
                QMessageBox.warning(self, "Error", "Chưa có batch đầu tiên. Hãy Generate trước.")
                return
            
            topic = self.ed_topic.toPlainText().strip()
            if not topic:
                QMessageBox.information(self, "Info", "Vui lòng nhập chủ đề.")
                return
            
            self.btn_continue.setEnabled(False)
            self.btn_continue.setText("🧠 AI đang viết thêm...")
            self.btn_gen.setEnabled(False)
            
            try:
                # Dùng API mới: generate_next_batch
                result = self._generator.generate_next_batch(
                    topic=topic,
                    num_prompts=self.spin_num.value(),
                    video_style=self.cmb_style.currentData(),
                    dialogue_lang=self.cmb_lang.currentText(),
                    subtitles=self.cmb_sub.currentText()
                )
                
                new_scripts = result.get("script", [])
                if not new_scripts:
                    QMessageBox.warning(self, "Error", "Không generate được prompts mới.")
                    return
                
                # Append vào existing scripts
                start_idx = len(self._output_script)
                self._output_script.extend(new_scripts)
                
                # Cập nhật preview (chỉ thêm phần mới)
                current_preview = self.preview.toPlainText()
                new_preview = current_preview + "\n\n=== Continued ===\n\n"
                new_preview += "\n\n".join(
                    f"{start_idx + i + 1}. {p[:150]}..." 
                    for i, p in enumerate(new_scripts)
                )
                self.preview.setPlainText(new_preview)
                
                QMessageBox.information(
                    self, "Success", 
                    f"Đã thêm {len(new_scripts)} prompts!\nTổng: {len(self._output_script)} prompts"
                )
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Lỗi: {e}")
            finally:
                self.btn_continue.setEnabled(True)
                self.btn_continue.setText("➕ Continue Script")
                self.btn_gen.setEnabled(True)    
    def _on_use(self):
            if not self._output_script:
                self._on_generate()
                if not self._output_script:
                    return
            self.accept()
    
    def output_prompts(self) -> List[str]:
        return list(self._output_script)
class ImageAnalyzeDialog(QDialog):
    def __init__(self, parent=None, models: list[str] | None=None, default_spec: str="8s video, 4K UHD, 24fps, cinematic lighting, shallow DoF"):
        super().__init__(parent)
        self.setWindowTitle("Phân tích ảnh → Tạo prompt 8s")
        self.setMinimumWidth(820)
        self._out_prompts: list[str] = []

        models = models or ["Claude", "Claude Pro"]

        root = QVBoxLayout(self)
        root.setContentsMargins(12,12,12,12)
        root.setSpacing(10)

        # ==== Hàng 1: Model + Topic hint + Số prompt ====
        row1 = QFormLayout()
        self.cmb_model = QComboBox(); self.cmb_model.addItems(models)
        self.le_topic  = QLineEdit(); self.le_topic.setPlaceholderText("Topic hint (optional)…")
        self.spin_n    = QSpinBox(); self.spin_n.setRange(1, 10); self.spin_n.setValue(1)
        row1.addRow("Model (Vision):", self.cmb_model)
        row1.addRow("Topic hint:",     self.le_topic)
        row1.addRow("Số prompt:",      self.spin_n)
        root.addLayout(row1)

        # ==== Hàng 2: SPEC builder (giống Text→Video) ====
        spec_card = QFrame(); spec_card.setObjectName("card")
        grid = QGridLayout(spec_card)
        grid.setContentsMargins(12,10,12,10)
        grid.setHorizontalSpacing(10); grid.setVerticalSpacing(8)

        # Combos
        self.cmb_res   = QComboBox(); self.cmb_res.addItems(RES_OPTIONS)
        self.cmb_fps   = QComboBox(); self.cmb_fps.addItems(FPS_OPTIONS)
        self.cmb_cam   = QComboBox(); self.cmb_cam.addItems(CAM_OPS); self.cmb_cam.setEditable(True)
        self.cmb_light = QComboBox(); self.cmb_light.addItems(LIGHTING_OPS)
        self.cmb_grade = QComboBox(); self.cmb_grade.addItems(GRADING_OPS)
        self.cmb_lens  = QComboBox(); self.cmb_lens.addItems(LENS_OPS)
        self.cmb_fx    = QComboBox(); self.cmb_fx.addItems(FX_OPS)
        self.cmb_motion= QComboBox(); self.cmb_motion.addItems(MOTION_OPS)
        self.cmb_comp  = QComboBox(); self.cmb_comp.addItems(COMP_OPS)
        self.cmb_audio = QComboBox(); self.cmb_audio.addItems(AUDIO_OPS)

        # Vị trí trên grid (2 cột chính)
        r = 0
        grid.addWidget(QLabel("Resolution:"), r, 0); grid.addWidget(self.cmb_res,   r, 1); r+=1
        grid.addWidget(QLabel("Frame rate:"), r, 0); grid.addWidget(self.cmb_fps,   r, 1); r+=1
        grid.addWidget(QLabel("Camera (phẩy):"), r,0); grid.addWidget(self.cmb_cam, r,1); r+=1
        grid.addWidget(QLabel("Lighting:"), r, 0); grid.addWidget(self.cmb_light,   r, 1); r+=1
        grid.addWidget(QLabel("Color grading:"), r,0); grid.addWidget(self.cmb_grade, r,1); r+=1
        grid.addWidget(QLabel("Lens / DoF:"), r, 0); grid.addWidget(self.cmb_lens,  r, 1); r+=1
        grid.addWidget(QLabel("FX:"), r, 0); grid.addWidget(self.cmb_fx,            r, 1); r+=1
        grid.addWidget(QLabel("Motion:"), r, 0); grid.addWidget(self.cmb_motion,    r, 1); r+=1
        grid.addWidget(QLabel("Composition:"), r,0); grid.addWidget(self.cmb_comp,  r, 1); r+=1
        grid.addWidget(QLabel("Audio:"), r, 0); grid.addWidget(self.cmb_audio,      r, 1)

        root.addWidget(spec_card)

        # ==== Preview spec (tự cập nhật) ====
        self.preview_spec = QPlainTextEdit()
        self.preview_spec.setReadOnly(True)
        self.preview_spec.setPlaceholderText("Spec xem trước…")
        root.addWidget(self.preview_spec)

        # ==== Preview prompts ====
        self.preview_prompts = QPlainTextEdit()
        self.preview_prompts.setReadOnly(True)
        self.preview_prompts.setPlaceholderText("Preview các prompt…")
        root.addWidget(self.preview_prompts, 1)

        # ==== Buttons ====
        row_btn = QHBoxLayout()
        self.btn_gen   = QPushButton("Generate")
        self.btn_use   = QPushButton("Use")
        self.btn_copy  = QPushButton("Copy All")
        self.btn_cancel= QPushButton("Cancel")
        for b in (self.btn_gen, self.btn_use, self.btn_copy, self.btn_cancel):
            b.setMinimumHeight(34)
        row_btn.addWidget(self.btn_gen); row_btn.addWidget(self.btn_use)
        row_btn.addWidget(self.btn_copy); row_btn.addStretch(1); row_btn.addWidget(self.btn_cancel)
        root.addLayout(row_btn)

        # seed mặc định theo default_spec truyền vào (nếu cần chỉ hiện, không phân tích)
        # ở đây ta chỉ đặt vài giá trị tiện dụng:
        try:
            # defaults: 4K / 24fps / cinematic lighting / shallow DoF
            self.cmb_res.setCurrentIndex(max(0, RES_OPTIONS.index("4K UHD")))
            self.cmb_fps.setCurrentIndex(max(0, FPS_OPTIONS.index("24fps")))
            self.cmb_light.setCurrentIndex(max(0, LIGHTING_OPS.index("cinematic lighting")))
            self.cmb_lens.setCurrentIndex(max(0, LENS_OPS.index("shallow depth of field")))
        except Exception:
            pass

        # wire up
        for w in (self.cmb_res, self.cmb_fps, self.cmb_cam, self.cmb_light, self.cmb_grade,
                  self.cmb_lens, self.cmb_fx, self.cmb_motion, self.cmb_comp, self.cmb_audio):
            try:
                w.currentTextChanged.connect(self._update_spec_preview)
            except Exception:
                # for editable cam field
                try: w.editTextChanged.connect(self._update_spec_preview)
                except Exception: pass

        self.btn_gen.clicked.connect(self._on_generate)
        self.btn_use.clicked.connect(self._on_use)
        self.btn_copy.clicked.connect(lambda: QApplication.clipboard().setText("\n\n".join(self._out_prompts)))
        self.btn_cancel.clicked.connect(self.reject)

        self._update_spec_preview()  # fill preview_spec ngay

    # tạo chuỗi spec từ các combobox (giống Text→Video)
    def _current_spec_text(self) -> str:
        cams = [c.strip() for c in (self.cmb_cam.currentText() or "").split(",") if c.strip()]
        return _join_specs(
            preset="Cinematic / Hollywood Trailer",
            res=self.cmb_res.currentText(),
            fps=self.cmb_fps.currentText(),
            cams=cams,
            lighting=self.cmb_light.currentText(),
            grading=self.cmb_grade.currentText(),
            lens=self.cmb_lens.currentText(),
            fx=self.cmb_fx.currentText(),
            motion=self.cmb_motion.currentText(),
            comp=self.cmb_comp.currentText(),
            audio=self.cmb_audio.currentText(),
        )

    def _update_spec_preview(self):
        self.preview_spec.setPlainText(self._current_spec_text())

    def _on_generate(self):
        # gọi parent để chạy Vision theo options hiện tại
        par = self.parent()
        if not hasattr(par, "analyze_image_to_prompt"):
            QMessageBox.warning(self, "Error", "Parent không hỗ trợ Vision.")
            return
        img = getattr(par, "_img_quick_path", "") or ""
        if not img or not os.path.exists(img):
            QMessageBox.information(self, "Info", "Chưa chọn ảnh trong composer.")
            return

        # set model + spec lên UI parent (để analyze_image_to_prompt lấy đúng)
        try:
            if hasattr(par, "cmb_vision_model"):
                par.cmb_vision_model.setCurrentText(self.cmb_model.currentText())
            # dùng _default_spec_img làm nguồn spec cho analyze_image_to_prompt
            spec = self._current_spec_text()
            setattr(par, "_default_spec_img", spec)
            if hasattr(par, "ed_default_spec_img"):
                par.ed_default_spec_img.setText(spec)
        except Exception:
            pass

        n = int(self.spin_n.value())
        prompts = []
        err = None
        for _ in range(n):
            try:
                prm = par.analyze_image_to_prompt(img, topic_hint=self.le_topic.text().strip())
                prompts.append(prm)
            except Exception as e:
                err = str(e); break
        if err:
            QMessageBox.warning(self, "Vision failed", err); return

        self._out_prompts = prompts
        self.preview_prompts.setPlainText("\n\n".join(f"- {p}" for p in prompts))

    def _on_use(self):
        # Nếu chưa có kết quả thì tự Generate trước
        if not self._out_prompts:
            self._on_generate()
            if not self._out_prompts:
                return

        par = self.parent()
        if not par or not hasattr(par, "image_prompts"):
            QMessageBox.warning(self, "Error", "Không tìm thấy parent để thêm vào hàng đợi.")
            return

        start = getattr(par, "_img_quick_path", "") or ""
        if not start or not os.path.exists(start):
            QMessageBox.information(self, "Info", "Chưa chọn ảnh trong composer.")
            return

        prompts = list(self._out_prompts)
        added = 0
        running = bool(getattr(par, "img_running_jobs", 0) > 0)

        if running:
            # Đang chạy → append xuống cuối & vẽ dòng mới ngay
            for p in prompts:
                ipr = ImagePromptRow(prompt=p, start_image=start)
                par.image_prompts.append(ipr)
                par._append_image_prompt_row(ipr)
                added += 1
        else:
            # Chưa chạy → insert lên đầu để prompt đầu nằm trên cùng
            for p in reversed(prompts):
                par.image_prompts.insert(0, ImagePromptRow(prompt=p, start_image=start))
                added += 1
            par._refresh_image_table()

        # cập nhật thống kê
        if hasattr(par, "_update_img_stats"):
            par._update_img_stats()

        # đánh dấu đã enqueue để caller khỏi điền lại vào ô nhập
        self._enqueued = True

        # đóng dialog
        self.accept()


    def output_prompts(self) -> list[str]:
        return list(self._out_prompts)
class DefaultSpecDialog(QDialog):
    def __init__(self, parent=None, current_spec: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Default Technical Spec")
        self.setMinimumWidth(600)
        lay = QVBoxLayout(self); lay.setContentsMargins(12,12,12,12); lay.setSpacing(8)

        form = QFormLayout()

        self.cmb_res   = QComboBox(); self.cmb_res.addItems(RES_OPTIONS);  self.cmb_res.setCurrentIndex(1)
        self.cmb_fps   = QComboBox(); self.cmb_fps.addItems(FPS_OPTIONS);  self.cmb_fps.setCurrentIndex(0)
        self.cmb_light = QComboBox(); self.cmb_light.addItems(LIGHTING_OPS)
        self.cmb_grade = QComboBox(); self.cmb_grade.addItems(GRADING_OPS)
        self.cmb_lens  = QComboBox(); self.cmb_lens.addItems(LENS_OPS)
        self.cmb_fx    = QComboBox(); self.cmb_fx.addItems(FX_OPS)
        self.cmb_motion= QComboBox(); self.cmb_motion.addItems(MOTION_OPS)
        self.cmb_comp  = QComboBox(); self.cmb_comp.addItems(COMP_OPS)
        self.cmb_audio = QComboBox(); self.cmb_audio.addItems(AUDIO_OPS)
        self.ed_cams   = QLineEdit(); self.ed_cams.setPlaceholderText("Ví dụ: close-up, tracking shot")

        form.addRow("Resolution:", self.cmb_res)
        form.addRow("Frame rate:", self.cmb_fps)
        form.addRow("Lighting:",   self.cmb_light)
        form.addRow("Color grading:", self.cmb_grade)
        form.addRow("Lens / DoF:", self.cmb_lens)
        form.addRow("FX:",         self.cmb_fx)
        form.addRow("Motion:",     self.cmb_motion)
        form.addRow("Composition:",self.cmb_comp)
        form.addRow("Audio:",      self.cmb_audio)
        form.addRow("Camera (phẩy):", self.ed_cams)
        lay.addLayout(form)

        self.preview = QPlainTextEdit(); self.preview.setReadOnly(True)
        lay.addWidget(self.preview, 1)

        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        lay.addWidget(bb)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)

        # seed nếu có spec hiện tại → chỉ hiển thị ở preview
        self._seed_spec = current_spec.strip()
        if self._seed_spec:
            self.preview.setPlainText(self._seed_spec)

        # cập nhật preview khi thay đổi
        for w in [self.cmb_res, self.cmb_fps, self.cmb_light, self.cmb_grade, self.cmb_lens,
                  self.cmb_fx, self.cmb_motion, self.cmb_comp, self.cmb_audio, self.ed_cams]:
            try:
                w.currentTextChanged.connect(self._update_preview)
            except Exception:
                w.textChanged.connect(self._update_preview)
        self._update_preview()

    def _update_preview(self):
        cams = [c.strip() for c in (self.ed_cams.text() or "").split(",") if c.strip()]
        spec = _join_specs(
            preset="Cinematic / Hollywood Trailer",
            res=self.cmb_res.currentText(),
            fps=self.cmb_fps.currentText(),
            cams=cams,
            lighting=self.cmb_light.currentText(),
            grading=self.cmb_grade.currentText(),
            lens=self.cmb_lens.currentText(),
            fx=self.cmb_fx.currentText(),
            motion=self.cmb_motion.currentText(),
            comp=self.cmb_comp.currentText(),
            audio=self.cmb_audio.currentText(),
        )
        self.preview.setPlainText(spec)

    def output_spec(self) -> str:
        return self.preview.toPlainText().strip()
class PromptGuideDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Prompt Guide")
        self.resize(960, 680)
        self.setMinimumSize(860, 600)

        # --- Detect dark theme from parent (MainWindow._theme_name) ---
        theme_name = getattr(parent, "_theme_name", "Indigo")
        dark = str(theme_name).strip().lower() in {"midnight", "carbon", "neon"}

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        # Header
        head = QHBoxLayout()
        icon = QLabel("🧭"); icon.setFixedSize(40, 40); icon.setAlignment(Qt.AlignCenter)
        title = QLabel("HƯỚNG DẪN THÔNG SỐ KỸ THUẬT PROMPT (AI Video)")
        title.setStyleSheet("font-size:20px; font-weight:900; margin-left:6px;")
        sub = QLabel("Giải thích ngắn gọn từng tham số để bạn chọn spec nhanh & đúng ý đồ hình ảnh.")
        sub.setObjectName("sub")
        head_text = QVBoxLayout(); head_text.addWidget(title); head_text.addWidget(sub)
        head.addWidget(icon); head.addLayout(head_text); head.addStretch(1)
        root.addLayout(head)

        # Card
        card = QFrame(); card.setObjectName("card")
        card_lay = QVBoxLayout(card); card_lay.setContentsMargins(16,16,16,16); card_lay.setSpacing(10)

        # Scrollable content
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        cont = QWidget(); cont_lay = QVBoxLayout(cont); cont_lay.setContentsMargins(0,0,0,0)

        body = QLabel(); body.setTextFormat(Qt.RichText); body.setWordWrap(True)
        body.setObjectName("body")
        body.setText("""
<h3>Resolution (Độ phân giải)</h3>
<ul>
  <li><b>1080p</b> – Full HD, nhẹ & nhanh để xem thử.</li>
  <li><b>4K UHD</b> – Chi tiết cao, dùng cho xuất chuẩn.</li>
  <li><b>8K HDR</b> – Rất nặng, chỉ khi cần cực sắc nét.</li>
</ul>

<h3>FPS (Frame rate – số khung hình/giây)</h3>
<ul>
  <li><b>24fps</b> – Cảm giác điện ảnh, chuyển động mượt vừa.</li>
  <li><b>30fps</b> – Tự nhiên, phù hợp nội dung thường nhật.</li>
  <li><b>60fps</b> – Rất mượt, tốt cho hành động/động tác nhanh.</li>
  <li><b>120fps</b> – Dành cho <i>slow-motion</i> siêu mượt.</li>
</ul>

<h3>Camera (Góc máy & chuyển động máy)</h3>
<ul>
  <li><b>close-up</b> – Cận gương mặt/vật thể (nhấn cảm xúc/chi tiết).</li>
  <li><b>medium / wide shot</b> – Trung cảnh / toàn cảnh.</li>
  <li><b>low angle</b> – Góc thấp, tạo cảm giác uy lực/đe nẹt.</li>
  <li><b>drone view</b> – Góc bay cao, quét toàn cảnh.</li>
  <li><b>tracking shot</b> – Máy quay bám theo nhân vật.</li>
  <li><b>orbiting / push-in / pan</b> – Quay vòng / tiến sát / lia máy.</li>
</ul>

<h3>Lighting (Ánh sáng)</h3>
<ul>
  <li><b>cinematic lighting</b> – Ánh sáng kiểu phim, kiểm soát rõ vùng sáng/tối.</li>
  <li><b>golden hour</b> – Vàng ấm lúc bình minh/hoàng hôn.</li>
  <li><b>volumetric light</b> – Tia sáng có khói/bụi.</li>
  <li><b>soft daylight</b> – Tự nhiên, dịu, ít tương phản.</li>
  <li><b>high contrast / chiaroscuro</b> – Tương phản mạnh, kịch tính.</li>
</ul>

<h3>Color grading (Màu)</h3>
<ul>
  <li><b>HDR10+</b> – Rực rỡ, biên độ sáng cao.</li>
  <li><b>Teal & Orange</b> – Phong cách Hollywood hiện đại.</li>
  <li><b>Monochrome</b> – Trắng đen nghệ thuật.</li>
  <li><b>Neon cyberpunk</b> – Màu neon, tương lai, nổi bật.</li>
  <li><b>Pastel tones</b> – Màu nhạt, dịu mắt.</li>
</ul>

<h3>Lens / DoF (Ống kính / độ sâu trường ảnh)</h3>
<ul>
  <li><b>shallow depth of field</b> – Nền mờ, chủ thể nổi bật.</li>
  <li><b>wide angle lens</b> – Góc rộng, mở không gian.</li>
  <li><b>macro lens</b> – Siêu cận, chi tiết nhỏ.</li>
  <li><b>anamorphic lens flare</b> – Flare điện ảnh, sang trọng.</li>
</ul>

<h3>FX (Hiệu ứng)</h3>
<ul>
  <li><b>fog/smoke/dust</b> – Sương/khói/bụi tăng chiều sâu.</li>
  <li><b>rain FX</b> – Hiệu ứng mưa kịch tính.</li>
  <li><b>sparks/debris</b> – Tia lửa/mảnh vỡ cho cảnh action.</li>
  <li><b>fire/explosion</b> – Cháy nổ mạnh mẽ.</li>
  <li><b>light bloom/glow</b> – Viền sáng rực rỡ.</li>
</ul>

<h3>Motion (Chuyển động nội dung)</h3>
<ul>
  <li><b>smooth motion</b> – Mượt mà, ổn định.</li>
  <li><b>speed ramping</b> – Đổi tốc độ (nhanh/chậm) có chủ đích.</li>
  <li><b>hyper slow motion</b> – Siêu chậm để nhấn chi tiết.</li>
  <li><b>time lapse</b> – Tua nhanh thời gian.</li>
</ul>

<h3>Composition (Bố cục khung hình)</h3>
<ul>
  <li><b>rule of thirds</b> – Quy tắc 1/3 kinh điển.</li>
  <li><b>symmetrical framing</b> – Đối xứng cân bằng.</li>
  <li><b>Dutch angle</b> – Góc nghiêng tạo cảm giác bất ổn.</li>
  <li><b>center focus</b> – Chủ thể ở tâm khung hình.</li>
</ul>

<h3>Audio (Âm thanh nền)</h3>
<ul>
  <li><b>none</b> – Không nhạc (chỉ hình).</li>
  <li><b>epic orchestral</b> – Hùng tráng/điện ảnh.</li>
  <li><b>suspenseful low rumble</b> – Căng thẳng, trầm.</li>
  <li><b>soft piano</b> – Ấm áp, nhẹ.</li>
  <li><b>trap/electronic</b> – Hiện đại, giàu năng lượng.</li>
</ul>

<p class="hint">Mẹo: Chọn 2–3 yếu tố quan trọng (Camera + Lighting + Grading) rồi thêm 1 điểm nhấn (Lens/FX) để prompt gọn mà vẫn “ra chất”.</p>
        """)
        cont_lay.addWidget(body); cont_lay.addStretch(1)
        scroll.setWidget(cont)
        card_lay.addWidget(scroll)

        # Buttons
        btns = QHBoxLayout()
        btn_copy = QPushButton("Copy nội dung"); btn_close = QPushButton("Đóng")
        btn_copy.clicked.connect(lambda: QApplication.clipboard().setText(body.text()))
        btn_close.clicked.connect(self.accept)
        btns.addStretch(1); btns.addWidget(btn_copy); btns.addWidget(btn_close)
        card_lay.addLayout(btns)

        root.addWidget(card)

        # Apply theme-aware styles
        self._apply_style(dark)

    def _apply_style(self, dark: bool):
        if dark:
            # Dark palette
            self.setStyleSheet("""
                QDialog { background: #0b1020; }
                QLabel#body, QLabel, QLabel#sub { color: #EAF2FF; }
                QLabel#body h3 { color:#FFFFFF; }
                QFrame#card {
                    border-radius: 12px;
                    border: 1px solid #25314a;
                    background: #101a2b;
                }
                QScrollArea { background: #101a2b; border: none; }
                QPushButton {
                    padding: 8px 12px; border-radius: 8px;
                    border:1px solid #25314a; background:#0f1626;
                    color:#EAF2FF; font-weight:600;
                }
                QPushButton:hover { background:#182238; }
                .hint { color:#9aa3b2; font-size:12px; }
                QLabel#body ul { margin-left: 18px; }
            """)
        else:
            # Light palette
            self.setStyleSheet("""
                QDialog { background: #F8FAFC; }
                QLabel#body, QLabel, QLabel#sub { color: #0f172a; }
                QLabel#body h3 { color:#111827; }
                QFrame#card {
                    border-radius: 12px;
                    border: 1px solid #E5E7EB;
                    background: #FFFFFF;
                }
                QScrollArea { background: #FFFFFF; border: none; }
                QPushButton {
                    padding: 8px 12px; border-radius: 8px;
                    border:1px solid #E5E7EB; background:#FFFFFF;
                    color:#111827; font-weight:600;
                }
                QPushButton:hover { background:#F3F4F6; }
                .hint { color:#6b7280; font-size:12px; }
                QLabel#body ul { margin-left: 18px; }
            """)

    def _apply_light_style(self):
        # dùng màu sáng trung tính; app của bạn có theme, nên dialog vẫn sạch sẽ
        self.setStyleSheet("""
            QDialog { background: #F8FAFC; }
            QLabel { color: #0f172a; }
            QPushButton {
                padding: 8px 12px; border-radius: 8px;
                border:1px solid #E5E7EB; background:#FFFFFF; color:#111827; font-weight:600;
            }
            QPushButton:hover { background:#F3F4F6; }
        """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Generator Pro v2")
        self.setFixedSize(1360, 900)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        self.thread_pool = QThreadPool.globalInstance()
        self._theme_name = "Indigo"

        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        act_quit = QAction("Quit", self); act_quit.triggered.connect(self.close); file_menu.addAction(act_quit)
        help_menu = menubar.addMenu("Help")
        act_about = QAction("About", self); act_about.triggered.connect(self.show_about); help_menu.addAction(act_about)
        

        act_guide = QAction("Prompt Guide", self)
        act_guide.triggered.connect(self.show_prompt_guide)
        help_menu.addAction(act_guide)
                # Kiểm tra license trước khi dựng UI nặng
        # Initialize Project Manager
        self.project_manager = ProjectManager(PROJECTS_FILE)
        
        # Initialize API Client for Admin Panel (will be set after login)
        self.api_client = None
        self.current_user = None  # Store user info after login
        self.user_role = None  # 'admin' or 'user'
        
        # Initialize Auto Workflow Orchestrator
        if AUTO_WORKFLOW_AVAILABLE:
            self.orchestrator = AutoWorkflowOrchestrator(self)
        else:
            self.orchestrator = None
        
        self.tabs = QTabWidget(); self.tabs.setTabPosition(QTabWidget.North)
        self.tab_project = QWidget()  # NEW: Project Management tab
        self.tab_image2video = QWidget()
        self.tab_accounts, self.tab_settings = QWidget(), QWidget()
        self.tab_elevenlabs = QWidget()  # NEW: ElevenLabs Audio tab
        self.tab_image_generator = QWidget()  # NEW: Image Generator tab

        # Tab order: Project -> Audio -> Image -> Video -> Accounts -> Settings
        self.tabs.addTab(self.tab_project, "📁 Projects")
        if ELEVENLABS_AVAILABLE:
            self.tabs.addTab(self.tab_elevenlabs, "🎵 Audio Generator")
        if IMAGE_TAB_AVAILABLE:
            self.tabs.addTab(self.tab_image_generator, "🎨 Image Generator")
        self.tabs.addTab(self.tab_image2video, "🎬 Image to Video")
        self.tabs.addTab(self.tab_accounts, "👤 Accounts")
        self.tabs.addTab(self.tab_settings, "⚙️ Settings")
        self.setCentralWidget(self.tabs)
        
        # Setup workflow status bar at bottom
        self.setup_workflow_status_bar()

        self.accounts: List[AccountRow] = []
        self.image_prompts: List[ImagePromptRow] = []
        self.img_stop_flag = {"stop": False}
        self.img_running_jobs = 0
        self.img_active_rows = set()   # rows đang chạy (Image->Video)
        self.setup_project_tab()  # NEW: Setup Project Management tab
        self.setup_image2video_tab()
        if IMAGE_TAB_AVAILABLE:
            self.setup_image_generator_tab()
        if ELEVENLABS_AVAILABLE:
            self.setup_elevenlabs_tab()
        self.setup_accounts_tab()
        self.setup_settings_tab()
        self.apply_styles()
        self.load_settings()
        
        # Initialize UI permissions (will be updated after login)
        self.update_ui_permissions()
        
        # ← THÊM: Timer để cleanup định kỳ
        self.cleanup_timer = QTimer(self)
        self.cleanup_timer.setInterval(300000)  # 5 phút
        self.cleanup_timer.timeout.connect(self._periodic_cleanup)
        self.cleanup_timer.start()
        
    @staticmethod
    def _sha1hex(b: bytes) -> str:
        h = hashlib.sha1(); h.update(b); return h.hexdigest()

    @staticmethod
    def _file_sha(path: str) -> str:
        h = hashlib.sha1()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1<<20), b""): h.update(chunk)
        return h.hexdigest()
    # cache: { sha1 : secure_url }
    _CDN_CACHE: Dict[str, str] = {}
    def show_prompt_guide(self):
        dlg = PromptGuideDialog(self)
        dlg.exec()
    def _periodic_cleanup(self):
        """Cleanup memory mỗi 5 phút"""
        # Cleanup video widgets không còn visible
        for row in range(self.tbl_img.rowCount()):
            for col in range(self.tbl_img.columnCount()):
                widget = self.tbl_img.cellWidget(row, col)
                if isinstance(widget, VideoCellWidget):
                    if not widget.isVisible() and hasattr(widget, 'player'):
                        widget.cleanup()        
        # Force garbage collection
        import gc
        gc.collect()
        
        # Clear completed threads
        self.thread_pool.clear()
    def _periodic_cleanup_image_prompts(self):
        """Cleanup memory và resources định kỳ"""
        try:
            # Clean completed rows nếu > 100 items
            if len(self.image_prompts) > 100:
                completed = [i for i, p in enumerate(self.image_prompts) 
                           if p.status.lower() in ("done", "failed")]
                if len(completed) > 50:
                    keep_recent = sorted(completed)[-50:]
                    for i in reversed([c for c in completed if c not in keep_recent]):
                        if i < len(self.image_prompts):
                            del self.image_prompts[i]
            
            # Force garbage collection
            import gc
            gc.collect()
            
            # Clear thread pool queue
            if self.thread_pool.activeThreadCount() == 0:
                self.thread_pool.clear()
                
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    def _get_img_prompt_text(self) -> str:
        # hỗ trợ cả QLineEdit (cũ) lẫn QTextEdit (mới)
        if hasattr(self, "img_prompt_edit"):
            try:
                return self.img_prompt_edit.toPlainText()
            except AttributeError:
                return self.img_prompt_edit.text()
        return ""

    def _set_img_prompt_text(self, text: str):
        if hasattr(self, "img_prompt_edit"):
            try:
                self.img_prompt_edit.setPlainText(text)
            except AttributeError:
                self.img_prompt_edit.setText(text)
    def test_checkboxes(self):
        """Test all checkboxes"""
        print("Testing checkboxes...")
        
        # Test video preview
        print(f"Video preview: {self.chk_no_preview.isChecked()}")
        self.chk_no_preview.setChecked(not self.chk_no_preview.isChecked())
        print(f"After toggle: {self.chk_no_preview.isChecked()}")
        
        # Test rotate
        print(f"Rotate: {self.chk_rotate_keys.isChecked()}")
        self.chk_rotate_keys.setChecked(not self.chk_rotate_keys.isChecked())
        print(f"After toggle: {self.chk_rotate_keys.isChecked()}")
    def upload_image_cloudinary(self, image_path: str, folder: str="vgp", public_id: str|None=None) -> str:
        """
        Upload ảnh lên Cloudinary bằng API key/secret (signed upload).
        Trả về secure_url (https).
        """
        if not requests:
            raise RuntimeError("Thiếu 'requests'. Hãy pip install requests")
        if not os.path.exists(image_path):
            raise FileNotFoundError(image_path)
        if not (CLOUD_NAME and CLOUD_API_KEY and CLOUD_SECRET):
            raise RuntimeError("Chưa cấu hình Cloudinary env (cloud name, api key, secret)")

        url = f"https://api.cloudinary.com/v1_1/{CLOUD_NAME}/image/upload"
        ts  = str(int(time.time()))

        # tạo chuỗi signature
        params = {"timestamp": ts}
        if folder:    params["folder"] = folder
        if public_id: params["public_id"] = public_id
        sig_base = "&".join(f"{k}={v}" for k,v in sorted(params.items())) + CLOUD_SECRET
        signature = self._sha1hex(sig_base.encode("utf-8"))

        data = {
            "api_key": CLOUD_API_KEY,
            "timestamp": ts,
            "signature": signature,
        }
        data.update({k:v for k,v in params.items() if k not in ["timestamp"]})

        with open(image_path, "rb") as f:
            files = {"file": f}
            r = requests.post(url, data=data, files=files, timeout=60)

        if r.status_code != 200:
            raise RuntimeError(f"Cloudinary error {r.status_code}: {r.text[:200]}")

        out = r.json()
        return out.get("secure_url") or out.get("url")
    # >>> VISION: đọc ảnh thành data URL (base64)
    def _image_to_data_url(self, path: str) -> str:
        import mimetypes, base64, os
        if not (path and os.path.exists(path)):
            raise FileNotFoundError("Image not found.")
        mime, _ = mimetypes.guess_type(path)
        if not mime:
            mime = "image/jpeg"
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        return f"data:{mime};base64,{b64}"
     
    def open_default_spec_popup(self):
        cur = getattr(self, "_default_spec_img", "").strip() or \
              "8s video, 4K UHD, 24fps, cinematic lighting, shallow DoF"
        dlg = DefaultSpecDialog(self, current_spec=cur)
        if dlg.exec() != QDialog.Accepted:
            return
        spec = dlg.output_spec() or cur
        self._default_spec_img = spec
        if hasattr(self, "lab_spec_preview"):
            # rút gọn hiển thị nếu quá dài
            self.lab_spec_preview.setText(spec if len(spec) <= 140 else spec[:140] + "…")
        self.save_settings()

    def analyze_image_to_prompt(self, image_path: str, topic_hint: str = "") -> str:
        """
        Upload ảnh lên Cloudinary để lấy HTTPS URL rồi gọi Groq /chat/completions
        với block multimodal chuẩn: [{"type":"text",...}, {"type":"image_url",...}].
        Trả về 1 prompt (3–5 câu) và luôn kết thúc bằng '— Technical: <specs>'.

        Yêu cầu:
          - Đã cấu hình Cloudinary (CLOUD_NAME + UPLOAD_PRESET) và `requests`.
          - Đã có pool key Groq qua self.get_key_pool().
          - UI có self.cmb_vision_model và self.ed_default_spec_img (như trong code của bạn).
        """
        # ===== Validate deps & inputs =====
        if not image_path or not os.path.exists(image_path):
            raise RuntimeError("Chưa chọn ảnh hợp lệ.")
        pool = self.get_key_pool()
        if not pool or not pool.has_keys():
            raise RuntimeError("Chưa có API key . Vào Settings > Prompt AI để thêm key.")
        if requests is None:
            raise RuntimeError("Thiếu 'requests'. Hãy cài: pip install requests")

        # ===== Lấy model & specs từ UI =====
        ui_choice = self.cmb_vision_model.currentText()
        if ui_choice == "Claude":
            model = "meta-llama/llama-4-scout-17b-16e-instruct"
        elif ui_choice == "Claude Pro":
            model = "meta-llama/llama-4-maverick-17b-128e-instruct"
        else:
            model = "meta-llama/llama-4-scout-17b-16e-instruct"  # default
        specs = getattr(self, "_default_spec_img",
                "8s video, 4K UHD, 24fps, cinematic lighting, shallow DoF")


        # ===== Upload Cloudinary để lấy https URL =====
        # Hàm upload_image_cloudinary đã được thêm ở phần helpers trước đó
        img_url = self.upload_image_cloudinary(image_path, folder="vgp")


        # ===== Compose chat payload (multimodal) =====
        system_msg = (
            "You are a senior prompt engineer specialized in cinematic short video generation. "
            "Analyze the provided image and produce ONE video prompt for an 8-second clip. "
            "Requirements:\n"
            "- The prompt must be 5–7 sentences, concise yet vivid.\n"
            "- Describe ONLY what is actually visible in the image: subjects, actions/movements, camera angles, atmosphere, lighting, emotions.\n"
            "- Always include strong camera verbs (e.g., pan, zoom, tracking shot, dolly, close-up, wide shot…).\n"
            "- Add sensory details: lighting quality, colors, smoke, wind, ambient sound if perceivable.\n"
            "- ABSOLUTELY do not invent or hallucinate unseen details.\n"
            "- Always end the prompt with an em dash followed by the EXACT provided technical specs string: — Technical: <specs>\n\n"
            "⚠️ Return a single plain-text prompt only. No markdown, no explanations, no extra symbols."
        )
        user_txt = f"Specs: {specs}\nTopic hint (optional): {topic_hint}".strip()

        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": [
                    {"type": "text", "text": user_txt},
                    {"type": "image_url", "image_url": {"url": img_url}}
                ]}
            ],
            "temperature": 0.6,
            "max_tokens": 300
        }

        # ===== Call Groq (try strict schema; if server expects image_url as string, retry once) =====
        try:
            data, headers, code, used = pool.post("/chat/completions", body)
        except Exception as e1:
            # Retry nhẹ với biến thể 'image_url' là string (một số gateway chấp nhận kiểu này)
            try:
                body["messages"][1]["content"][1] = {"type": "image_url", "image_url": img_url}
                data, headers, code, used = pool.post("/chat/completions", body)
            except Exception as e2:
                raise RuntimeError(f"Groq Vision failed: {e2}") from e2

        # ===== Parse & normalize output =====
        content = (data.get("choices") or [{}])[0].get("message", {}).get("content", "") or ""
        content = content.strip()
        if not content:
            raise RuntimeError("Vision model không trả nội dung.")

        # Lấy dòng đầu tiên gọn gàng nếu model trả nhiều dòng
        first = next((ln.strip(" -•\t") for ln in content.splitlines() if ln.strip()), content)

        # Đảm bảo luôn có '— Technical: <specs>'
        if "Technical:" not in first:
            first = f"{first.rstrip('.')}. — Technical: {specs}"

        return first

    # >>> VISION: handler cho nút “Phân tích ảnh → Gợi ý prompt”
    def get_key_pool(self) -> APIKeyPool:
        """Lấy Groq API key pool từ settings"""
        raw = getattr(self, '_groq_keys_raw', '')
        keys = []
        for ln in (raw or '').splitlines():
            s = (ln or '').strip()
            if s:
                keys.append(s)
        
        rotate = getattr(self, '_groq_rotate', True)
        
        if not hasattr(self, '_api_pool'):
            self._api_pool = APIKeyPool(keys, rotate_on_fail=rotate)
        else:
            self._api_pool.keys = keys
            self._api_pool.rotate = rotate
        return self._api_pool

    def _on_analyze_current_image(self):
        img = getattr(self, "_img_quick_path", "") or ""
        if not (img and os.path.exists(img)):
            QMessageBox.information(self, "Info", "Chưa chọn ảnh. Click ô thumbnail để chọn ảnh trước.")
            return
        try:
            if hasattr(self, "btn_img_analyze"):
                self.btn_img_analyze.setEnabled(False)
                self.btn_img_analyze.setText("Đang phân tích…")
            prompt = self.analyze_image_to_prompt(img, topic_hint="")
            if hasattr(self, "img_prompt_edit"):
                self.img_prompt_edit.setText(prompt)
            if hasattr(self, "lab_keys_status"):
                self.lab_keys_status.setText("Vision OK – prompt đã được đề xuất")
        except Exception as e:
            QMessageBox.warning(self, "Vision failed", str(e))
        finally:
            if hasattr(self, "btn_img_analyze"):
                self.btn_img_analyze.setEnabled(True)
                self.btn_img_analyze.setText("Phân tích ảnh → Gợi ý prompt")
    # >>> NEW: mở popup setting cho Vision rồi chạy
    def open_image_analyze_dialog(self):
        models = ["Claude", "Claude Pro"]
        default_spec = self.ed_default_spec_img.text() if hasattr(self, "ed_default_spec_img") else "8s video, 4K UHD, 24fps, cinematic lighting, shallow DoF"
        dlg = ImageAnalyzeDialog(self, models=models, default_spec=default_spec)
        if dlg.exec() != QDialog.Accepted:
            return

        # Nếu dialog đã tự enqueue rồi thì thôi, không đụng composer nữa
        if getattr(dlg, "_enqueued", False):
            return

        # (Giữ logic cũ như fallback: điền prompt đầu vào ô nhập)
        prompts = dlg.output_prompts()
        if not prompts:
            return
        self._set_img_prompt_text(prompts[0])

        if hasattr(self, "lab_keys_status"):
            self.lab_keys_status.setText("Vision OK – prompt đã được đề xuất qua popup")

    # ---- Row glow helpers (gradient for the whole row) ----
    # >>> NEW: Prompt-AI section (đẹp, dễ click, không bị đè)
    # >>> NEW: chuẩn hoá suffix và ghép/tháo "gsk_"
    def load_settings(self):
        s = _read_json(SETTINGS_FILE, {
            "model": "Veo 3.1 - Fast",
            "outputs": 1,
            "concurrency": 2,
            "out_dir": str(APP_DIR / "outputs"),
            "theme": "Indigo",
            "img_timeout": 180,
            "retries": 2,
            "cookie_folder": ""
        })
        # apply
        for b in self.model_group.buttons():
            if b.text() == s.get("model", "Veo 3 - Fast"):
                b.setChecked(True); break
        self.spin_outputs.setValue(int(s.get("outputs", 1)))
        self.spin_conc.setValue(int(s.get("concurrency", 2)))
        self.edit_outdir.setText(s.get("out_dir", str(APP_DIR / "outputs")))
        self._theme_name = s.get("theme","Indigo")
        if hasattr(self, "cmb_theme"):
            idx = self.cmb_theme.findText(self._theme_name)
            if idx >= 0: self.cmb_theme.setCurrentIndex(idx)
        if hasattr(self, "spin_img_timeout"):
            self.spin_img_timeout.setValue(int(s.get("img_timeout", 180)))
        if hasattr(self, "spin_retry"):                      # <-- ADD
            self.spin_retry.setValue(int(s.get("retries", 2)))# <-- ADD
        if hasattr(self, "chk_no_preview"):
            self.chk_no_preview.setChecked(bool(s.get("no_video_preview", False)))
        
        # Load Groq API keys
        groq_keys = s.get("groq_keys", [])
        if hasattr(self, "ed_groq_keys"):
            self.ed_groq_keys.setPlainText("\n".join(groq_keys))
        self._groq_keys_raw = "\n".join(groq_keys)
        self._groq_rotate = s.get("groq_rotate", True)
        
        # >>> VISION (Image→Video only)
        if hasattr(self, "cmb_vision_model"):
            self.cmb_vision_model.setCurrentText(s.get("vision_model", "llama-3.2-90b-vision-preview"))
        self._default_spec_img = s.get("default_spec", "8s video, 4K UHD, 24fps, cinematic lighting, shallow DoF")
        if hasattr(self, "lab_spec_preview"):
            self.lab_spec_preview.setText(self._default_spec_img if len(self._default_spec_img) <= 140 else self._default_spec_img[:140] + "…")
        if hasattr(self, "cmb_acc_strategy"):
            strategy = s.get("acc_strategy", "Round Robin (Chia đều)")
            self.cmb_acc_strategy.setCurrentText(strategy)

        if hasattr(self, "chk_multi_acc"):
            self.chk_multi_acc.setChecked(bool(s.get("multi_acc_enabled", True)))
        
        self._last_cookie_folder = s.get("cookie_folder", "")
        if self._last_cookie_folder and os.path.isdir(self._last_cookie_folder):
            # Tự động load cookies từ folder đã lưu
            QTimer.singleShot(500, lambda: self._load_cookie_folder(self._last_cookie_folder, silent=True))

        # Load ElevenLabs settings
        if ELEVENLABS_AVAILABLE and hasattr(self, "eleven_api_file"):
            el_settings = s.get("elevenlabs", {})
            self.eleven_api_file.setText(el_settings.get("api_file", "C:/TotalTool/API.txt"))
            self.eleven_output_dir.setText(el_settings.get("output_dir", "C:/TotalTool/output"))
            self.eleven_voice_id.setText(el_settings.get("voice_id", ""))
            self.eleven_stability.setValue(int(el_settings.get("stability", 50)))
            self.eleven_similarity.setValue(int(el_settings.get("similarity", 75)))
            
    def _theme_palette(self, name: str) -> dict:
        name = (name or "").strip().lower()

        if name == "aurora":  # xanh lá/teal
            return {
                "bg":"#F7FCFB","surface":"#FFFFFF","surface2":"#F1FAF7","text":"#0b1b17","muted":"#5b6b66",
                "border":"#DDEBE6","border_soft":"#E8F3F0",
                "accent":"#10B981","accent2":"#14B8A6","accent_text":"#ffffff",
                "grad1":"#34d399","grad2":"#06b6d4",
                "success":"#10B981","warning":"#f59e0b","danger":"#ef4444",
                "sel_bg":"#d1fae5","hover":"#ecfdf5","scroll":"#CDE7DF"
            }
        if name == "sunset":  # cam/hồng
            return {
                "bg":"#FFF8F5","surface":"#FFFFFF","surface2":"#FFF2ED","text":"#24140e","muted":"#6b4b3f",
                "border":"#F5E2DA","border_soft":"#FAECE6",
                "accent":"#F97316","accent2":"#FB7185","accent_text":"#ffffff",
                "grad1":"#fb923c","grad2":"#f472b6",
                "success":"#10B981","warning":"#f59e0b","danger":"#ef4444",
                "sel_bg":"#FFE7DA","hover":"#FFF1EA","scroll":"#F3D9CF"
            }
        if name == "midnight":  # dark mode
            return {
                "bg":"#0b1020","surface":"#121a2b","surface2":"#0f1626","text":"#e6eaf3","muted":"#9aa3b2",
                "border":"#25314a","border_soft":"#1b2438",
                "accent":"#8B5CF6","accent2":"#22D3EE","accent_text":"#10131c",
                "grad1":"#8b5cf6","grad2":"#22d3ee",
                "success":"#34d399","warning":"#f59e0b","danger":"#f87171",
                "sel_bg":"#1d2a45","hover":"#182238","scroll":"#2a3856"
            }
        if name == "ocean":  # xanh biển
            return {
                "bg":"#F5FAFF","surface":"#FFFFFF","surface2":"#EEF5FF","text":"#0f172a","muted":"#6b7280",
                "border":"#D9E6FF","border_soft":"#EAF3FF",
                "accent":"#3B82F6","accent2":"#06B6D4","accent_text":"#ffffff",
                "grad1":"#60a5fa","grad2":"#22d3ee",
                "success":"#10B981","warning":"#f59e0b","danger":"#ef4444",
                "sel_bg":"#DBEAFE","hover":"#EFF6FF","scroll":"#D4E6FF"
            }

        # ===== New vivid themes =====
        if name == "neon":  # dark + tím/hồng/teal kiểu cyber
            return {
                "bg":"#0a0a1a","surface":"#101028","surface2":"#0e0e24","text":"#EAF2FF","muted":"#9aa3b2",
                "border":"#2a2a52","border_soft":"#19193b",
                "accent":"#F472B6","accent2":"#22D3EE","accent_text":"#0c0e18",
                "grad1":"#f472b6","grad2":"#22d3ee",
                "success":"#34d399","warning":"#f59e0b","danger":"#fb7185",
                "sel_bg":"#1b1b3a","hover":"#171735","scroll":"#2b2b4f"
            }

        if name == "ember":  # nóng – đỏ/cam đậm
            return {
                "bg":"#FFF7F3","surface":"#FFFFFF","surface2":"#FFEDE6","text":"#1e120d","muted":"#7a5546",
                "border":"#F6D7CC","border_soft":"#FBE3DA",
                "accent":"#EF4444","accent2":"#F97316","accent_text":"#ffffff",
                "grad1":"#f97316","grad2":"#ef4444",
                "success":"#10B981","warning":"#f59e0b","danger":"#dc2626",
                "sel_bg":"#FFE4D5","hover":"#FFF1EA","scroll":"#F8D8CC"
            }

        if name == "plum":  # tím mận + hồng, tươi
            return {
                "bg":"#FFF6FF","surface":"#FFFFFF","surface2":"#FCEBFF","text":"#24122A","muted":"#6E5A77",
                "border":"#F0D6FA","border_soft":"#F7E6FF",
                "accent":"#A855F7","accent2":"#EC4899","accent_text":"#ffffff",
                "grad1":"#a855f7","grad2":"#ec4899",
                "success":"#10B981","warning":"#f59e0b","danger":"#ef4444",
                "sel_bg":"#F4E8FF","hover":"#FDF3FF","scroll":"#EDD6FF"
            }

        if name == "forest":  # xanh lục đậm – tươi
            return {
                "bg":"#F4FBF6","surface":"#FFFFFF","surface2":"#EAF7EF","text":"#0b1f15","muted":"#4b6759",
                "border":"#D4EDE0","border_soft":"#E4F4EA",
                "accent":"#059669","accent2":"#22C55E","accent_text":"#ffffff",
                "grad1":"#10b981","grad2":"#22c55e",
                "success":"#10B981","warning":"#f59e0b","danger":"#ef4444",
                "sel_bg":"#DDF7EA","hover":"#EDFCF3","scroll":"#CFECE0"
            }

        if name == "carbon":  # dark xanh than + cyan
            return {
                "bg":"#0a0f14","surface":"#101820","surface2":"#0d141b","text":"#E6EEF8","muted":"#8fa3b8",
                "border":"#1e2a36","border_soft":"#16202b",
                "accent":"#06B6D4","accent2":"#0EA5E9","accent_text":"#081016",
                "grad1":"#06b6d4","grad2":"#0ea5e9",
                "success":"#34d399","warning":"#f59e0b","danger":"#f87171",
                "sel_bg":"#152231","hover":"#111b25","scroll":"#213040"
            }

        # default Indigo
        return {
            "bg":"#F7F7FF","surface":"#FFFFFF","surface2":"#F2F3FF","text":"#0f172a","muted":"#6b7280",
            "border":"#DBE2EA","border_soft":"#E8ECF5",
            "accent":"#6366F1","accent2":"#8B5CF6","accent_text":"#ffffff",
            "grad1":"#a5b4fc","grad2":"#6366f1",
            "success":"#10B981","warning":"#f59e0b","danger":"#ef4444",
            "sel_bg":"#E0E7FF","hover":"#EEF2FF","scroll":"#D9E4FF"
        }


    def set_theme(self, name: str):
        self._theme_name = name
        self.apply_styles()
        self.save_settings()

    def _show_text_popup(self, title: str, text: str, editable: bool = False) -> Optional[str]:
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton
        dlg = QDialog(self); dlg.setWindowTitle(title); dlg.resize(860, 560)

        root = QVBoxLayout(dlg); root.setContentsMargins(12, 12, 12, 12); root.setSpacing(8)
        lbl = QLabel(title); lbl.setStyleSheet("font-size:16px; font-weight:800;"); root.addWidget(lbl)

        te = QTextEdit(); te.setAcceptRichText(False)
        te.setReadOnly(not editable)
        te.setPlainText(text or "")

        # dùng màu theo apply_styles (dark = nền tối, chữ trắng)
        te.setStyleSheet("QTextEdit{ border:1px solid #1e2a36; border-radius:10px; padding:8px; }")
        root.addWidget(te, 1)

        row = QHBoxLayout(); row.addStretch(1)
        btn_copy  = QPushButton("Copy");            btn_copy.setObjectName("btn-teal")
        btn_close = QPushButton("Close");           btn_close.setObjectName("btn-ghost")
        row.addWidget(btn_copy); 
        if editable:
            btn_save  = QPushButton("Save");        btn_save.setObjectName("btn-primary")
            row.addWidget(btn_save)
        row.addWidget(btn_close); 
        root.addLayout(row)

        def _copy(): QApplication.clipboard().setText(te.toPlainText())
        btn_copy.clicked.connect(_copy)
        if editable:
            btn_save.clicked.connect(dlg.accept)
        btn_close.clicked.connect(dlg.reject)

        ok = dlg.exec()  # ← ĐỔI exec_() THÀNH exec()
        if editable and ok:
            return te.toPlainText()
        return None
    def refresh_license_view(self):
        info = get_current_license_info()

        self.lic_dev.setText(info.get("device_id","-"))
        self.lic_owner.setText(info.get("owner","-"))
        self.lic_exp.setText(info.get("expiry","-"))

        days = info.get("days_left", 0)
        self.lic_days.setText(str(days))

        status = info.get("status","-")
        self.lic_stat.setText(f"{status} — {info.get('message','')}")
        # màu trạng thái
        if status == "Valid":
            if days <= 0:
                self.lic_stat.setStyleSheet("color:#ef4444; font-weight:800;")   # hết hạn
            elif days <= 7:
                self.lic_stat.setStyleSheet("color:#f59e0b; font-weight:800;")   # sắp hết
            else:
                self.lic_stat.setStyleSheet("color:#10b981; font-weight:800;")   # ok
        elif status == "Missing":
            self.lic_stat.setStyleSheet("color:#6b7280; font-weight:800;")
        else:
            self.lic_stat.setStyleSheet("color:#ef4444; font-weight:800;")

    def _lic_copy_did(self):
        QApplication.clipboard().setText(_get_device_id())
        QMessageBox.information(self, "Copied", "Device ID đã được copy.")

    def _lic_paste_and_save(self):
        txt = QApplication.clipboard().text().strip()
        if not txt:
            QMessageBox.information(self, "Info", "Clipboard không có token.")
            return
        try:
            APP_LICENSE_DIR.mkdir(parents=True, exist_ok=True)
            APP_LICENSE_FILE.write_text(txt, encoding="utf-8")
            QMessageBox.information(self, "Saved", "Đã lưu token từ clipboard.")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không lưu được token: {e}")
        self.refresh_license_view()

    def _lic_load_file(self):
        p, _ = QFileDialog.getOpenFileName(self, "Chọn token", "", "Text (*.txt);;All files (*)")
        if not p: return
        try:
            data = Path(p).read_text(encoding="utf-8").strip()
            APP_LICENSE_DIR.mkdir(parents=True, exist_ok=True)
            APP_LICENSE_FILE.write_text(data, encoding="utf-8")
            QMessageBox.information(self, "Saved", "Đã lưu token.")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không lưu được token: {e}")
        self.refresh_license_view()

    def _lic_open_folder(self):
        try:
            APP_LICENSE_DIR.mkdir(parents=True, exist_ok=True)
            if sys.platform.startswith("win"):
                os.startfile(str(APP_LICENSE_DIR))
            else:
                os.system(f'xdg-open "{APP_LICENSE_DIR}"')
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))

    # -------- Settings persistence --------
    def _set_img_video_cell(self, row_idx: int, video_path: str):
        """Image-to-Video table"""
        show_preview = not getattr(self, "chk_no_preview", None) or not self.chk_no_preview.isChecked()
        
        vw = VideoCellWidget(video_path, self, show_preview=show_preview)
        self.tbl_img.setCellWidget(row_idx, 5, vw)
        
        h = 150 if show_preview else 60
        self.tbl_img.verticalHeader().resizeSection(row_idx, h)

        # Open button
        btn_open = QPushButton("Open")
        btn_open.clicked.connect(lambda _, p=video_path: self._open_file_safe(p))
        w_open = QWidget()
        lo = QHBoxLayout(w_open)
        lo.setContentsMargins(6, 2, 6, 2)
        lo.addWidget(btn_open, 0, Qt.AlignCenter)
        self.tbl_img.setCellWidget(row_idx, 6, w_open)

    def current_img_timeout(self) -> int:
        try:
            return int(self.spin_img_timeout.value())
        except Exception:
            return 140

    def save_settings(self):
        s = {
            "model": self.current_model(),
            "outputs": self.current_outputs(),
            "concurrency": self.current_concurrency(),
            "out_dir": self.edit_outdir.text() or str(APP_DIR / "outputs"),
            "theme": self._theme_name,
            "img_timeout": int(self.spin_img_timeout.value()),
            "retries": int(self.spin_retry.value()),
            "cookie_folder": getattr(self, "_last_cookie_folder", ""),
            "no_video_preview": bool(self.chk_no_preview.isChecked()) if hasattr(self, "chk_no_preview") else False,
            "acc_strategy": self.cmb_acc_strategy.currentText() if hasattr(self, "cmb_acc_strategy") else "Round Robin (Chia đều)",
            "multi_acc_enabled": bool(self.chk_multi_acc.isChecked()) if hasattr(self, "chk_multi_acc") else True,
        }
        
        # >>> VISION (Image→Video only)
        s.update({
            "vision_model": self.cmb_vision_model.currentText() if hasattr(self, "cmb_vision_model") else "llama-3.2-90b-vision-preview",
            "default_spec": getattr(self, "_default_spec_img", "8s video, 4K UHD, 24fps, cinematic lighting, shallow DoF"),
            "img_auto_analyze": bool(self.chk_img_auto_analyze.isChecked()) if hasattr(self, "chk_img_auto_analyze") else False,
        })
        
        # Save Groq API keys
        groq_keys = []
        if hasattr(self, "ed_groq_keys"):
            groq_keys = [ln.strip() for ln in self.ed_groq_keys.toPlainText().splitlines() if ln.strip()]
            self._groq_keys_raw = "\n".join(groq_keys)
        s["groq_keys"] = groq_keys
        s["groq_rotate"] = True

        # Save ElevenLabs settings
        if ELEVENLABS_AVAILABLE and hasattr(self, "eleven_api_file"):
            s["elevenlabs"] = {
                "api_file": self.eleven_api_file.text(),
                "output_dir": self.eleven_output_dir.text(),
                "voice_id": self.eleven_voice_id.text(),
                "stability": self.eleven_stability.value(),
                "similarity": self.eleven_similarity.value(),
            }

        _write_json(SETTINGS_FILE, s)

    def current_retries(self) -> int:
        try:
            return int(self.spin_retry.value())
        except Exception:
            return 2

    # -------- Utilities --------
    def _open_file_safe(self, path: str):
        try:
            if not path or not os.path.exists(path):
                choice = QMessageBox.question(
                    self, "File not found",
                    "Không tìm thấy file đầu ra.\nBạn có muốn chọn lại đường dẫn mới không?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if choice == QMessageBox.Yes:
                    new_path, _ = QFileDialog.getOpenFileName(self, "Select video", "", "Videos (*.mp4 *.webm *.mov);;All files (*)")
                    if new_path:
                        return new_path
                return ""
            
            if sys.platform.startswith("win"):
                os.startfile(path)
            else:
                os.system(f'xdg-open "{path}"')
            return path
        except Exception as e:
            QMessageBox.warning(self, "Open failed", f"Không mở được file:\n{e}")
    def _cleanup_row_widgets(self, table: QTableWidget, row: int):
        """Cleanup với error handling tốt hơn"""
        for col in range(table.columnCount()):
            widget = table.cellWidget(row, col)
            if not widget:
                continue
            
            # 1. Cleanup VideoCellWidget
            if isinstance(widget, VideoCellWidget):
                try:
                    widget.cleanup()
                except Exception:
                    pass
            
            # 2. Disconnect checkbox signals
            try:
                if hasattr(widget, '_cb'):
                    widget._cb.blockSignals(True)
                    widget._cb.deleteLater()
            except Exception:
                pass
            
            # 3. Disconnect buttons - CHECK RECEIVERS FIRST
            try:
                for btn in widget.findChildren(QPushButton):
                    try:
                        btn.blockSignals(True)  # Safer than disconnect
                        if btn.receivers(btn.clicked) > 0:
                            btn.clicked.disconnect()
                    except (RuntimeError, TypeError):
                        pass
                    finally:
                        btn.deleteLater()
            except Exception:
                pass
            
            # 4. Cleanup StatusProgress
            try:
                if hasattr(widget, '_sp'):
                    sp = widget._sp
                    if hasattr(sp, '_spin_timer') and sp._spin_timer.isActive():
                        sp._spin_timer.stop()
                        sp._spin_timer.deleteLater()
                    sp.deleteLater()
            except Exception:
                pass
            
            # 5. Remove widget
            try:
                widget.setParent(None)
                widget.deleteLater()
            except Exception:
                pass
    def _append_image_prompt_row(self, ipr: ImagePromptRow):
        r = self.tbl_img.rowCount()
        self.tbl_img.insertRow(r)

        # Select
        w = QWidget(); box = QCheckBox(); box.setChecked(True)
        lay = QHBoxLayout(w); lay.setContentsMargins(8, 0, 8, 0)
        lay.addWidget(box); lay.addStretch(1)
        w._cb = box
        self.tbl_img.setCellWidget(r, 0, w)

        # STT
        it_idx = QTableWidgetItem(str(len(self.image_prompts)))
        it_idx.setTextAlignment(Qt.AlignCenter)
        self.tbl_img.setItem(r, 1, it_idx)

        # Prompt
        self.tbl_img.setItem(r, 2, QTableWidgetItem(ipr.prompt))

        # Image preview (col 3)
        self._set_img_preview_cell(r, 3, ipr.start_image)

        # Status (col 4)
        sp = self._ensure_img_progress_cell(r)
        sp.set_progress(0, "Queued")

        # Video/Open rỗng
        self.tbl_img.setItem(r, 5, QTableWidgetItem(""))
        self.tbl_img.setItem(r, 6, QTableWidgetItem(""))
        
        # Regen (col 7)
        btn_regen = QPushButton()
        btn_regen.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        btn_regen.setToolTip("Regenerate this row")
        btn_regen.setFixedWidth(32)
        btn_regen.setIconSize(QSize(18, 18))
        btn_regen.clicked.connect(lambda _, row=r: self._img_regenerate_row(row))

        cell_regen = QWidget()
        lr = QHBoxLayout(cell_regen)
        lr.setContentsMargins(6, 2, 6, 2)
        lr.addWidget(btn_regen, 0, Qt.AlignCenter)
        self.tbl_img.setCellWidget(r, 7, cell_regen)

        # Delete (dời sang col 8)
        btn_del = QPushButton()
        btn_del.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        btn_del.setToolTip("Delete this row"); btn_del.setFixedWidth(32)
        btn_del.clicked.connect(lambda _, row=r: self._delete_img_row(row))
        cell = QWidget(); l = QHBoxLayout(cell); l.setContentsMargins(6,2,6,2)
        l.addWidget(btn_del, 0, Qt.AlignCenter)
        self.tbl_img.setCellWidget(r, 8, cell)


    def _change_page_size(self, size_text):
        try:
            new_size = int(size_text)
            if new_size > 0:
                self._items_per_page = new_size
                self._current_page = 0  # Reset về trang đầu
                self._refresh_image_table()
        except ValueError:
            pass
    
    def _reset_job_to_queue(self, row: int, is_image: bool = False):
        """Reset một job đang chạy về trạng thái Queued"""
        if is_image:
            if 0 <= row < len(self.image_prompts):
                ipr = self.image_prompts[row]
                if ipr.status.lower() not in ("done", "failed"):
                    ipr.status = "Pending"
                    ipr.video = ""
                    sp = self._ensure_img_progress_cell(row)
                    sp.set_progress(0, "Queued")
                    sp.set_running(False)
    
    def _get_available_accounts(self) -> List[AccountRow]:
        """Lấy danh sách accounts LIVE có thể dùng"""
        return [a for a in self.accounts if a.status.lower() == "live"]

    def _pick_quick_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select image", "", "Images (*.png *.jpg *.jpeg *.webp *.bmp);;All files (*)"
        )
        if path:
            self._update_quick_image_preview(path)
        if getattr(self, "chk_img_auto_analyze", None) and self.chk_img_auto_analyze.isChecked():
            try:
                self._on_analyze_current_image()
            except Exception as e:
                QMessageBox.warning(self, "Vision", str(e))

    def _make_thumb(self, image_path: str, width: int, height: int) -> QPixmap:
        """Create thumbnail from image with specified dimensions"""
        try:
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                return QPixmap()
            return pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        except Exception:
            return QPixmap()

    def _update_quick_image_preview(self, path: str | None):
        self._img_quick_path = path or ""
        if path and os.path.exists(path):
            pm = self._make_thumb(path, 150, 95)
            if pm:
                self.img_quick_preview.setPixmap(pm)
                self.img_quick_preview.setText("")  # không hiện text khi đã có thumbnail
                return
        # fallback khi chưa có ảnh
        self.img_quick_preview.setPixmap(QPixmap())
        self.img_quick_preview.setText("Click to choose")

    # ======================== WORKFLOW STATUS BAR ========================
    def setup_workflow_status_bar(self):
        """Setup workflow status bar at bottom of window"""
        # Create status bar
        self.status_bar = self.statusBar()
        
        # Workflow status label
        self.workflow_status_label = QLabel("Ready")
        self.workflow_status_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10b981, stop:1 #059669);
                color: white;
                padding: 6px 15px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10pt;
            }
        """)
        
        # Progress bar for workflow
        self.workflow_progress = QProgressBar()
        self.workflow_progress.setRange(0, 100)
        self.workflow_progress.setValue(0)
        self.workflow_progress.setTextVisible(True)
        self.workflow_progress.setFixedWidth(200)
        self.workflow_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #d1d9e6;
                border-radius: 5px;
                text-align: center;
                background: white;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F87B1B, stop:1 #FF8C2E);
                border-radius: 3px;
            }
        """)
        self.workflow_progress.hide()  # Hidden by default
        
        # Add to status bar
        self.status_bar.addPermanentWidget(self.workflow_status_label)
        self.status_bar.addPermanentWidget(self.workflow_progress)
        
        # Connect orchestrator signals if available
        if self.orchestrator:
            self.orchestrator.step_changed.connect(self.on_workflow_step_changed)
            self.orchestrator.progress_changed.connect(self.on_workflow_progress_changed)
            self.orchestrator.workflow_complete.connect(self.on_workflow_complete)
            self.orchestrator.workflow_error.connect(self.on_workflow_error)
    
    def on_workflow_step_changed(self, step_text: str):
        """Update workflow status label"""
        self.workflow_status_label.setText(step_text)
        self.workflow_progress.show()
        
        # Change color based on step
        if "❌" in step_text or "error" in step_text.lower():
            bg_color = "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ef4444, stop:1 #dc2626);"
        elif "✅" in step_text:
            bg_color = "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #059669);"
        elif "🤖" in step_text or "🎵" in step_text or "🎨" in step_text:
            bg_color = "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b5cf6, stop:1 #7c3aed);"
        else:
            bg_color = "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #2563eb);"
        
        self.workflow_status_label.setStyleSheet(f"""
            QLabel {{
                {bg_color}
                color: white;
                padding: 6px 15px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10pt;
            }}
        """)
    
    def on_workflow_progress_changed(self, current: int, total: int):
        """Update workflow progress bar"""
        if total > 0:
            progress = int((current / total) * 100)
            self.workflow_progress.setValue(progress)
            self.workflow_progress.setFormat(f"{current}/{total}")
    
    def on_workflow_complete(self):
        """Handle workflow completion"""
        self.workflow_status_label.setText("✅ Workflow Complete!")
        self.workflow_status_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10b981, stop:1 #059669);
                color: white;
                padding: 6px 15px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10pt;
            }
        """)
        self.workflow_progress.setValue(100)
        
        # Hide progress bar after 3 seconds
        QTimer.singleShot(3000, lambda: self.workflow_progress.hide())
        QTimer.singleShot(3000, lambda: self.workflow_status_label.setText("Ready"))
    
    def on_workflow_error(self, error_msg: str):
        """Handle workflow error"""
        self.workflow_status_label.setText(f"❌ Error: {error_msg[:50]}...")
        self.workflow_status_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ef4444, stop:1 #dc2626);
                color: white;
                padding: 6px 15px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10pt;
            }
        """)
        self.workflow_progress.hide()
        
        # Show error dialog
        QMessageBox.critical(self, "Workflow Error", f"Auto workflow failed:\n\n{error_msg}")
    
    # ======================== PROJECT MANAGEMENT TAB ========================
    def setup_project_tab(self):
        """Setup Project Management tab"""
        layout = QVBoxLayout(self.tab_project)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("📁 Project Management")
        title.setStyleSheet("""
            font-size: 18pt;
            font-weight: bold;
            color: #F87B1B;
        """)
        header.addWidget(title)
        header.addStretch()
        
        # User info display
        self.lbl_user_info = QLabel("👤 Not logged in")
        self.lbl_user_info.setStyleSheet("""
            font-size: 10pt;
            color: #dc2626;
            font-weight: 600;
            padding: 6px 12px;
            background-color: #fee2e2;
            border-radius: 5px;
            margin-right: 10px;
        """)
        header.addWidget(self.lbl_user_info)
        
        # Logout button
        self.btn_logout = QPushButton("🚪 Logout")
        self.btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        self.btn_logout.clicked.connect(self.on_logout)
        self.btn_logout.setVisible(False)  # Hidden until logged in
        header.addWidget(self.btn_logout)
        
        # Current Project Display
        self.lbl_current_project = QLabel("No project selected")
        self.lbl_current_project.setStyleSheet("""
            font-size: 12pt;
            color: #11224E;
            font-weight: 600;
            padding: 8px 15px;
            background-color: #FFE8D6;
            border-radius: 6px;
        """)
        header.addWidget(self.lbl_current_project)
        layout.addLayout(header)
        
        # Admin Panel Integration
        if API_CLIENT_AVAILABLE:
            admin_layout = QHBoxLayout()
            
            # Login status
            self.lbl_admin_status = QLabel("❌ Not connected to admin panel")
            self.lbl_admin_status.setStyleSheet("""
                font-size: 10pt;
                color: #dc2626;
                padding: 5px 10px;
                background-color: #fee2e2;
                border-radius: 4px;
            """)
            admin_layout.addWidget(self.lbl_admin_status)
            
            # Login button
            btn_admin_login = QPushButton("🔐 Connect to Admin Panel")
            btn_admin_login.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #6366f1, stop:1 #4f46e5);
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 10pt;
                    min-height: 35px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #818cf8, stop:1 #6366f1);
                }
            """)
            btn_admin_login.clicked.connect(self.on_admin_login)
            admin_layout.addWidget(btn_admin_login)
            
            # Load from server button
            btn_load_server = QPushButton("☁️ Load Projects from Server")
            btn_load_server.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #06b6d4, stop:1 #0891b2);
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 10pt;
                    min-height: 35px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #22d3ee, stop:1 #06b6d4);
                }
            """)
            btn_load_server.clicked.connect(self.on_load_projects_from_server)
            admin_layout.addWidget(btn_load_server)
            
            admin_layout.addStretch()
            layout.addLayout(admin_layout)
        
        # Action buttons (store references for permission control)
        btn_layout = QHBoxLayout()
        
        self.btn_new_project = QPushButton("➕ New Project")
        self.btn_new_project.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF8C2E, stop:1 #F87B1B);
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
                    stop:0 #FFA04D, stop:1 #FF8C2E);
            }
        """)
        self.btn_new_project.clicked.connect(self.on_new_project)
        btn_layout.addWidget(self.btn_new_project)
        
        self.btn_edit_project = QPushButton("✏️ Edit Project")
        self.btn_edit_project.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0ea5e9, stop:1 #0284c7);
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
                    stop:0 #38bdf8, stop:1 #0ea5e9);
            }
        """)
        self.btn_edit_project.clicked.connect(self.on_edit_project)
        btn_layout.addWidget(self.btn_edit_project)
        
        self.btn_delete_project = QPushButton("🗑️ Delete Project")
        self.btn_delete_project.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ef4444, stop:1 #dc2626);
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
                    stop:0 #f87171, stop:1 #ef4444);
            }
        """)
        self.btn_delete_project.clicked.connect(self.on_delete_project)
        btn_layout.addWidget(self.btn_delete_project)
        
        # NEW: Import Script & Auto Generate button
        btn_import_script = QPushButton("📜 Import Script")
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
        
        btn_refresh = QPushButton("🔄 Refresh")
        btn_refresh.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #10b981, stop:1 #059669);
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
                    stop:0 #34d399, stop:1 #10b981);
            }
        """)
        btn_refresh.clicked.connect(self.refresh_project_list)
        btn_layout.addWidget(btn_refresh)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Projects table - Simple view with 2 columns only
        self.table_projects = QTableWidget()
        self.table_projects.setColumnCount(2)
        self.table_projects.setHorizontalHeaderLabels([
            "Select", "Project Name"
        ])
        self.table_projects.horizontalHeader().setStretchLastSection(True)
        self.table_projects.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_projects.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_projects.setAlternatingRowColors(True)
        self.table_projects.verticalHeader().setVisible(False)
        
        # Set column widths - Simple 2-column layout
        self.table_projects.setColumnWidth(0, 120)  # Select button
        # Column 1 (Project Name) will stretch to fill remaining space
        self.table_projects.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #d1d9e6;
                border-radius: 8px;
                gridline-color: #e8eef5;
            }
            QTableWidget::item:selected {
                background-color: #FFE8D6;
                color: #11224E;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f1f5f9, stop:1 #e2e8f0);
                color: #11224E;
                padding: 10px;
                border: none;
                border-right: 1px solid #cbd5e1;
                border-bottom: 2px solid #94a3b8;
                font-weight: bold;
                font-size: 10pt;
            }
        """)
        layout.addWidget(self.table_projects)
        
        # Double click to select project
        self.table_projects.cellDoubleClicked.connect(self.on_select_project)
        
        # Load initial data
        self.refresh_project_list()

    def refresh_project_list(self):
        """Refresh project list in table - Simple view with project name only"""
        self.table_projects.setRowCount(0)
        projects = self.project_manager.get_all_projects()
        
        for project in projects:
            row = self.table_projects.rowCount()
            self.table_projects.insertRow(row)
            
            # Select button
            btn_select = QPushButton("✓ Select")
            btn_select.setStyleSheet("""
                QPushButton {
                    background: #10b981;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 11pt;
                }
                QPushButton:hover {
                    background: #059669;
                }
            """)
            btn_select.clicked.connect(lambda checked, pid=project.id: self.select_project(pid))
            self.table_projects.setCellWidget(row, 0, btn_select)
            
            # Project name only (simple view)
            name_item = QTableWidgetItem(project.name)
            name_item.setFont(QApplication.font())
            font = name_item.font()
            font.setPointSize(11)
            font.setBold(True)
            name_item.setFont(font)
            self.table_projects.setItem(row, 1, name_item)
        
        # Update current project display
        if self.project_manager.current_project:
            self.lbl_current_project.setText(f"Current: {self.project_manager.current_project.name}")
        else:
            self.lbl_current_project.setText("No project selected")
    
    def on_new_project(self):
        """Create new project on server"""
        if not API_CLIENT_AVAILABLE or not self.api_client:
            QMessageBox.warning(self, "API Not Available",
                              "Server connection is required to create projects.")
            return
        
        if not self.api_client.is_authenticated():
            QMessageBox.warning(self, "Not Authenticated",
                              "Please login first!")
            return
        
        voice_list = self._load_elevenlabs_voices()
        dialog = ProjectDialog(self, voice_list=voice_list)
        if dialog.exec():
            data = dialog.get_all_values()
            
            # Random num_prompts from 12 to 24
            import random
            num_prompts = random.randint(12, 24)
            
            # Create project on server via API
            project_data = {
                "channel_name": data["name"],
                "script_template": data["description"],
                "num_prompts": num_prompts,  # Random 12-24
                "voice_id": data.get("voice_id", ""),
                "auto_workflow": True,
                "auto_organize_folders": data.get("auto_organize_folders", False)
            }
            
            created_project = self.api_client.create_project(project_data)
            
            if created_project:
                # Reload projects from server
                self.on_load_projects_from_server()
                QMessageBox.information(self, "Success", 
                    f"✅ Project '{data['name']}' created on server!")
            else:
                QMessageBox.warning(self, "Failed",
                    "Failed to create project on server. Check console for details.")
    
    def on_edit_project(self):
        """Edit selected project on server"""
        if not API_CLIENT_AVAILABLE or not self.api_client:
            QMessageBox.warning(self, "API Not Available",
                              "Server connection is required to edit projects.")
            return
        
        if not self.api_client.is_authenticated():
            QMessageBox.warning(self, "Not Authenticated",
                              "Please login first!")
            return
        
        row = self.table_projects.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Please select a project to edit")
            return
        
        project_name = self.table_projects.item(row, 1).text()
        project = None
        for p in self.project_manager.get_all_projects():
            if p.name == project_name:
                project = p
                break
        
        if not project:
            return
        
        voice_list = self._load_elevenlabs_voices()
        dialog = ProjectDialog(self, project.name, project.description, voice_list=voice_list)
        # Pre-fill voice_id if exists
        if hasattr(project, 'voice_id') and project.voice_id:
            idx = dialog.combo_voice.findData(project.voice_id)
            if idx >= 0:
                dialog.combo_voice.setCurrentIndex(idx)
        
        # Pre-fill auto_organize_folders if exists
        if hasattr(project, 'auto_organize_folders'):
            dialog.chk_auto_organize.setChecked(project.auto_organize_folders)
        
        if dialog.exec():
            data = dialog.get_all_values()
            
            # Random num_prompts from 12 to 24 (even for edit)
            import random
            num_prompts = random.randint(12, 24)
            
            # Update project on server via API
            project_data = {
                "channel_name": data["name"],
                "script_template": data["description"],
                "num_prompts": num_prompts,  # Random 12-24
                "voice_id": data.get("voice_id", ""),
                "auto_workflow": True,
                "auto_organize_folders": data.get("auto_organize_folders", False)
            }
            
            success = self.api_client.update_project(project.id, project_data)
            
            if success:
                # Reload projects from server
                self.on_load_projects_from_server()
                QMessageBox.information(self, "Success",
                    f"✅ Project '{data['name']}' updated on server!")
            else:
                QMessageBox.warning(self, "Failed",
                    "Failed to update project on server. Check console for details.")
    
    def _load_elevenlabs_voices(self) -> list:
        """Load voice list from ElevenLabs voices.json"""
        try:
            voices_file = Path(r"C:\TotalTool\Settings\voices.json")
            if voices_file.exists():
                with open(voices_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[VOICE LOAD ERROR] {e}")
        return []
    
    def on_delete_project(self):
        """Delete selected project from server"""
        if not API_CLIENT_AVAILABLE or not self.api_client:
            QMessageBox.warning(self, "API Not Available",
                              "Server connection is required to delete projects.")
            return
        
        if not self.api_client.is_authenticated():
            QMessageBox.warning(self, "Not Authenticated",
                              "Please login first!")
            return
        
        row = self.table_projects.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Please select a project to delete")
            return
        
        project_name = self.table_projects.item(row, 1).text()
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"⚠️ Are you sure you want to delete project '{project_name}'?\n\n"
            "This will delete the project from the server permanently!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            project = None
            for p in self.project_manager.get_all_projects():
                if p.name == project_name:
                    project = p
                    break
            
            if project:
                # Delete from server via API
                success = self.api_client.delete_project(project.id)
                
                if success:
                    # Reload projects from server
                    self.on_load_projects_from_server()
                    QMessageBox.information(self, "Success",
                        f"✅ Project '{project_name}' deleted from server!")
                else:
                    QMessageBox.warning(self, "Failed",
                        "Failed to delete project from server. Check console for details.")
    
    def on_admin_login(self):
        """Handle admin panel login - DEPRECATED, use login dialog instead"""
        QMessageBox.information(
            self, "Login Required",
            "Please restart the application to login.\n\n"
            "Login is now required at startup for security."
        )
    
    def update_ui_permissions(self):
        """Update UI based on user role (admin or user)"""
        if not self.current_user or not self.user_role:
            # Not logged in - hide everything
            self.lbl_user_info.setText("👤 Not logged in")
            self.lbl_user_info.setStyleSheet("""
                font-size: 10pt;
                color: #dc2626;
                font-weight: 600;
                padding: 6px 12px;
                background-color: #fee2e2;
                border-radius: 5px;
            """)
            self.btn_logout.setVisible(False)
            
            # Hide admin buttons
            if hasattr(self, 'btn_new_project'):
                self.btn_new_project.setVisible(False)
            if hasattr(self, 'btn_edit_project'):
                self.btn_edit_project.setVisible(False)
            if hasattr(self, 'btn_delete_project'):
                self.btn_delete_project.setVisible(False)
            return
        
        # Update user info label
        username = self.current_user.get('username', 'Unknown')
        role_display = "👑 Admin" if self.user_role == 'admin' else "👤 User"
        self.lbl_user_info.setText(f"{role_display}: {username}")
        
        if self.user_role == 'admin':
            self.lbl_user_info.setStyleSheet("""
                font-size: 10pt;
                color: #7c3aed;
                font-weight: 600;
                padding: 6px 12px;
                background-color: #ede9fe;
                border-radius: 5px;
            """)
        else:
            self.lbl_user_info.setStyleSheet("""
                font-size: 10pt;
                color: #059669;
                font-weight: 600;
                padding: 6px 12px;
                background-color: #d1fae5;
                border-radius: 5px;
            """)
        
        self.btn_logout.setVisible(True)
        
        # Show/hide buttons based on role
        is_admin = (self.user_role == 'admin')
        
        if hasattr(self, 'btn_new_project'):
            self.btn_new_project.setVisible(is_admin)
        if hasattr(self, 'btn_edit_project'):
            self.btn_edit_project.setVisible(is_admin)
        if hasattr(self, 'btn_delete_project'):
            self.btn_delete_project.setVisible(is_admin)
        
        print(f"✅ UI permissions updated for {username} ({self.user_role})")
    
    def on_logout(self):
        """Handle logout"""
        reply = QMessageBox.question(
            self, "Logout",
            "Bạn có chắc muốn đăng xuất?\n\nỨng dụng sẽ đóng sau khi đăng xuất.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Clear user data
            self.api_client = None
            self.current_user = None
            self.user_role = None
            
            # Clear saved credentials
            try:
                creds_file = Path(__file__).parent / ".workflow_creds"
                if creds_file.exists():
                    creds_file.unlink()
            except:
                pass
            
            # Close application
            self.close()
    
    def on_load_projects_from_server(self):
        """Load projects from admin panel server"""
        if not API_CLIENT_AVAILABLE or not self.api_client:
            QMessageBox.warning(self, "API Client Not Available",
                              "Admin panel integration is not available.")
            return
        
        if not self.api_client.is_authenticated():
            QMessageBox.warning(
                self, "Not Authenticated",
                "Please connect to admin panel first!\n\n"
                "Click '🔐 Connect to Admin Panel' button."
            )
            return
        
        # Fetch projects from server
        projects = self.api_client.get_projects()
        
        if not projects:
            QMessageBox.information(
                self, "No Projects",
                "No projects found on admin panel or failed to load."
            )
            return
        
        # Load projects from server (no local storage, always fresh from server)
        self.project_manager.projects.clear()
        
        for server_project in projects:
            # Convert server project to local Project
            # Note: video_output, voice_output, image_output will be set when importing script
            local_project = Project(
                id=server_project['project_id'],  # Use server UUID
                name=server_project['channel_name'],
                description=server_project['script_template'] or "",
                video_output="",  # Will be set when importing script
                voice_output="",  # Will be set when importing script
                image_output="",  # Will be set when importing script
                channel_name=server_project['channel_name'],
                script_template=server_project['script_template'],
                num_prompts=server_project['num_prompts'],  # This will be ignored, random 12-20 instead
                voice_id=server_project['voice_id'],
                auto_workflow=server_project['auto_workflow']
            )
            self.project_manager.projects.append(local_project)
        
        # Refresh UI (no local save - always load from server)
        self.refresh_project_list()
        
        QMessageBox.information(
            self, "Success",
            f"✅ Loaded {len(projects)} projects from server"
        )
    
    def on_import_script_auto(self):
        """Handle Import Script button - Start auto workflow"""
        if not AUTO_WORKFLOW_AVAILABLE:
            QMessageBox.warning(
                self,
                "Feature Not Available",
                "Auto workflow module is not available.\n\n"
                "Please check:\n"
                "• auto_workflow.py exists in the same folder\n"
                "• Check console for import errors"
            )
            return
        
        # Check if project is selected
        if not self.project_manager.current_project:
            QMessageBox.warning(
                self,
                "No Project Selected",
                "Please select a project first!\n\n"
                "Steps:\n"
                "1. Create a new project (➕ button)\n"
                "2. Or select existing project from table\n"
                "3. Then click 'Import Script'"
            )
            return
        
        project = self.project_manager.current_project
        
        # File dialog to select script
        script_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Script File for Auto Workflow",
            "",
            "Text files (*.txt);;All files (*.*)"
        )
        
        if not script_path:
            return
        
        # Random num_prompts from 12 to 24 (on import)
        import random
        num_prompts = random.randint(12, 24)
        print(f"[IMPORT SCRIPT] Random num_prompts: {num_prompts} (range: 12-24)")
        
        # Override project num_prompts with random value
        project.num_prompts = num_prompts
        
        # Confirm
        reply = QMessageBox.question(
            self,
            "🚀 Start Auto Workflow?",
            f"📁 Project: {project.name}\n"
            f"📜 Script: {os.path.basename(script_path)}\n"
            f"🎨 Images: {num_prompts} prompts (random 12-24)\n\n"
            f"This will automatically:\n"
            f"1. Create folder: C:\\WorkFlow\\{project.name}\\\n"
            f"2. Parse script with Groq AI\n"
            f"3. Generate {num_prompts} image prompts\n"
            f"4. Switch to Image tab\n"
            f"5. Start generating images\n\n"
            f"Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Start auto workflow
                self.orchestrator.start_workflow(project, script_path)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Workflow Error",
                    f"Failed to start auto workflow:\n\n{e}"
                )
    
    def on_select_project(self, row, col):
        """Select project on double click"""
        project_name = self.table_projects.item(row, 1).text()
        for p in self.project_manager.get_all_projects():
            if p.name == project_name:
                self.select_project(p.id)
                break
    
    def select_project(self, project_id: str):
        """Set current active project and apply project settings"""
        self.project_manager.set_current_project(project_id)
        project = self.project_manager.current_project
        
        # Apply project voice settings to ElevenLabs widget
        if ELEVENLABS_AVAILABLE and hasattr(self, 'elevenlabs_widget') and self.elevenlabs_widget:
            if hasattr(project, 'voice_id') and project.voice_id:
                # Find and select voice in combo box
                voice_combo = self.elevenlabs_widget.voice_combo
                idx = voice_combo.findData(project.voice_id)
                if idx >= 0:
                    voice_combo.setCurrentIndex(idx)
                    self.elevenlabs_widget.log(f"🎙️ Applied project voice: {voice_combo.currentText()}")
                else:
                    self.elevenlabs_widget.log(f"⚠️ Project voice ID not found: {project.voice_id}")
        
        self.refresh_project_list()
        QMessageBox.information(
            self, "Project Selected",
            f"Project '{project.name}' is now active!\n\n"
            f"✅ Voice settings applied\n"
            "All apps will now use this project's output folders."
        )

    def setup_image2video_tab(self):
        # Set consistent background color
        self.tab_image2video.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
            }
        """)
        wrapper = QVBoxLayout(self.tab_image2video)
        wrapper.setSpacing(8)

        # ----- Enhanced composer: Single row with better proportions -----
        composer = QFrame()
        composer.setObjectName("card")
        composer.setMaximumHeight(120)  # more compact
        main_layout = QHBoxLayout(composer)
        main_layout.setContentsMargins(12, 10, 12, 10)
        main_layout.setSpacing(16)

        # ==== IMAGE SECTION (Left) ====
        image_section = QVBoxLayout()
        image_section.setSpacing(6)
        
        self.img_quick_preview = QLabel("Click to choose")
        self.img_quick_preview.setAlignment(Qt.AlignCenter)
        self.img_quick_preview.setFixedSize(120, 75)
        self.img_quick_preview.setCursor(Qt.PointingHandCursor)
        self.img_quick_preview.setScaledContents(True)
        self.img_quick_preview.setStyleSheet(
            "background:#f3f4f6; border:2px dashed #9ca3af; border-radius:8px; color:#6b7280; font-size:11px; font-weight:500;"
        )
        self.img_quick_preview.mousePressEvent = lambda _e: self._pick_quick_image()
        image_section.addWidget(self.img_quick_preview)
        
        # Tạo prompt button right under image
        self.btn_img_analyze = QPushButton("🔍 Tạo prompt")
        self.btn_img_analyze.setObjectName("btn-primary")
        self.btn_img_analyze.setMinimumHeight(28)
        self.btn_img_analyze.setMaximumHeight(28)
        self.btn_img_analyze.clicked.connect(self.open_image_analyze_dialog)
        self.btn_img_analyze.setStyleSheet("font-size: 11px; padding: 4px 8px;")
        image_section.addWidget(self.btn_img_analyze)
        
        main_layout.addLayout(image_section)

        # ==== PROMPT SECTION (Center - Main area) ====
        prompt_section = QVBoxLayout()
        prompt_section.setSpacing(6)
        
        self.img_prompt_edit = QTextEdit()
        self.img_prompt_edit.setAcceptRichText(False)
        self.img_prompt_edit.setPlaceholderText(
            "Nhập 1 hoặc nhiều PROMPT cho cùng 1 ảnh…\n"
            "- Mỗi PROMPT cách nhau 1 dòng trống (blank line)\n"
            "Ví dụ:\n"
            "slow push-in, handheld, crowd gasps…\n"
            "\n"  # <— dòng trống ngăn prompt 1 và 2
            "low-angle reveal, dusk ambience, subtle wind on hair…"
        )
        self.img_prompt_edit.setObjectName("pill-input")
        self.img_prompt_edit.setFixedHeight(75)
        self.img_prompt_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        prompt_section.addWidget(self.img_prompt_edit)
        main_layout.addLayout(prompt_section, 1)  # expand to fill

        # ==== RIGHT SECTION: Add + Vision Controls ====
        right_section = QVBoxLayout()
        right_section.setSpacing(8)
        
        # Add button (top) - Orange Gradient
        self.btn_img_add = QPushButton("➕ Add To Queue")
        self.btn_img_add.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF8C2E, stop:1 #F87B1B);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 10pt;
                min-height: 36px;
                text-shadow: 0px 1px 2px rgba(0, 0, 0, 0.3);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFA04D, stop:1 #FF8C2E);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #E66A08, stop:1 #D35F00);
            }
        """)
        self.btn_img_add.setMinimumSize(80, 36)
        self.btn_img_add.clicked.connect(self.add_one_image_prompt)
        right_section.addWidget(self.btn_img_add, 0, Qt.AlignCenter)

        # Vision controls (bottom, horizontal compact)
        vision_controls = QFrame()
        vision_controls.setStyleSheet("""
            QFrame {
                background: rgba(45, 55, 72, 0.2);
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                padding: 4px;
            }
        """)
        vc_layout = QHBoxLayout(vision_controls)
        vc_layout.setContentsMargins(6, 4, 6, 4)
        vc_layout.setSpacing(6)

        # Auto checkbox (smaller)
        self.chk_img_auto_analyze = QCheckBox("Auto")
        self.chk_img_auto_analyze.setChecked(False)
        self.chk_img_auto_analyze.setCursor(Qt.PointingHandCursor)
        self.chk_img_auto_analyze.setMinimumHeight(24)
        self.chk_img_auto_analyze.setStyleSheet("""
            QCheckBox {
                spacing: 6px;
                font-size: 11px;
                font-weight: 600;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #9CA3AF;
                background: #ffffff;
                border-radius: 3px;
            }
            QCheckBox::indicator:hover {
                border-color: #F87B1B;
                background: #FFF7F0;
            }
            QCheckBox::indicator:checked {
                background: #F87B1B;
                border-color: #FF8C2E;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEwIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDRMMy41IDYuNUw5IDEiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMS41IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
            }
        """)
        self.chk_img_auto_analyze.stateChanged.connect(self.save_settings)
        vc_layout.addWidget(self.chk_img_auto_analyze)

        # Model dropdown (more compact)
        model_label = QLabel("Model:")
        model_label.setStyleSheet("color:#6b7280; font-size:10px;")
        vc_layout.addWidget(model_label)
        
        self.cmb_vision_model = QComboBox()
        self.cmb_vision_model.addItems(["Claude", "Claude Pro"])
        self.cmb_vision_model.setMinimumWidth(70)
        self.cmb_vision_model.setMaximumWidth(80)
        self.cmb_vision_model.setStyleSheet("font-size: 10px;")
        self.cmb_vision_model.currentTextChanged.connect(self.save_settings)
        vc_layout.addWidget(self.cmb_vision_model)

        # Settings gear (smaller)
        self.btn_edit_spec = QPushButton("⚙")
        self.btn_edit_spec.setFixedSize(22, 22)
        self.btn_edit_spec.setToolTip("Edit auto prompt settings")
        self.btn_edit_spec.clicked.connect(self.open_default_spec_popup)
        self.btn_edit_spec.setStyleSheet("""
            QPushButton {
                border-radius: 11px;
                font-size: 11px;
                background: #f3f4f6;
                border: 1px solid #d1d5db;
                color: #6b7280;
            }
            QPushButton:hover {
                background: #e5e7eb;
                color: #374151;
            }
        """)
        vc_layout.addWidget(self.btn_edit_spec)

        right_section.addWidget(vision_controls)
        main_layout.addLayout(right_section)
        
        wrapper.addWidget(composer)

        # ----- Tools row: Select All | Clear | (stretch) | Import | Generate | Stop -----
        tools = QHBoxLayout()
        tools.setSpacing(8)

        self.btn_img_sel_all = QPushButton("✓ Select All")
        self.btn_img_sel_all.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0d1836, stop:1 #090e1e);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 10pt;
                min-height: 32px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #11224E, stop:1 #0d1836);
            }
        """)
        self.btn_img_sel_all.clicked.connect(self._img_select_all)
        self.btn_img_sel_all.setMaximumWidth(120)
        
        self.btn_img_sel_none = QPushButton("✗ Clear")
        self.btn_img_sel_none.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0d1836, stop:1 #090e1e);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 10pt;
                min-height: 32px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #11224E, stop:1 #0d1836);
            }
        """)
        self.btn_img_sel_none.clicked.connect(self._img_clear_all)
        self.btn_img_sel_none.setMaximumWidth(100)

        tools.addWidget(self.btn_img_sel_all)
        tools.addWidget(self.btn_img_sel_none)
        tools.addStretch(1)

        # Delete buttons group - Red Gradient
        delete_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ef4444, stop:1 #dc2626);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 10pt;
                min-height: 32px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f87171, stop:1 #ef4444);
            }
        """
        
        self.btn_img_del_all = QPushButton("🗑️ Delete All")
        self.btn_img_del_all.setStyleSheet(delete_style)
        self.btn_img_del_all.clicked.connect(self._img_delete_all)
        
        self.btn_img_del_done = QPushButton("✓ Delete Success")
        self.btn_img_del_done.setStyleSheet(delete_style)
        self.btn_img_del_done.clicked.connect(self._img_delete_success)
        
        self.btn_img_del_sel = QPushButton("✗ Delete Selected")
        self.btn_img_del_sel.setStyleSheet(delete_style)
        self.btn_img_del_sel.clicked.connect(self._img_delete_selected)

        tools.addWidget(self.btn_img_del_all)
        tools.addWidget(self.btn_img_del_done)
        tools.addWidget(self.btn_img_del_sel)

        # Stats label
        self.lab_img_stats = QLabel("✓ 0  •  ✗ 0")
        self.lab_img_stats.setStyleSheet("color:#6b7280; font-weight:700; margin: 0 8px;")
        tools.addWidget(self.lab_img_stats)

        # Main action buttons with gradient style
        self.btn_img_import = QPushButton("📄 Import List")
        self.btn_img_import.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0d1836, stop:1 #090e1e);
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
                    stop:0 #11224E, stop:1 #0d1836);
            }
        """)
        self.btn_img_import.clicked.connect(self.import_image_list)
        
        self.btn_img_generate = QPushButton("▶️ Generate Videos")
        self.btn_img_generate.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF8C2E, stop:1 #F87B1B);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 25px;
                font-weight: bold;
                font-size: 11pt;
                min-height: 40px;
                text-shadow: 0px 1px 2px rgba(0, 0, 0, 0.3);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFA04D, stop:1 #FF8C2E);
            }
        """)
        self.btn_img_generate.clicked.connect(self.start_image_generate_queue)
        
        self.btn_img_stop = QPushButton("⏹ Stop")
        self.btn_img_stop.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0d1836, stop:1 #090e1e);
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
                    stop:0 #11224E, stop:1 #0d1836);
            }
            QPushButton:disabled {
                background: #8b99a8;
                color: #d1d5db;
            }
        """)
        self.btn_img_stop.clicked.connect(self.on_img_stop_clicked)
        self.btn_img_stop.setEnabled(False)

        tools.addWidget(self.btn_img_import)
        tools.addWidget(self.btn_img_generate)
        tools.addWidget(self.btn_img_stop)

        wrapper.addLayout(tools)

        # ----- Table -----
        self.tbl_img = QTableWidget(0, 9, self.tab_image2video)
        self.tbl_img.setHorizontalHeaderLabels(
            ["Select", "STT", "Prompt", "Image", "Status", "Video", "Open", "Regen", "Delete"]
        )
        header = self.tbl_img.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Fixed)
        vheader = self.tbl_img.verticalHeader()
        vheader.setSectionResizeMode(QHeaderView.Fixed)
        vheader.setDefaultSectionSize(160)
        vheader.setVisible(False)

        self.tbl_img.setColumnWidth(0, 60)
        self.tbl_img.setColumnWidth(1, 40)
        self.tbl_img.setColumnWidth(2, 450)
        self.tbl_img.setColumnWidth(3, 180)
        self.tbl_img.setColumnWidth(4, 145)
        self.tbl_img.setColumnWidth(5, 256)
        self.tbl_img.setColumnWidth(6, 80)
        self.tbl_img.setColumnWidth(7, 60)   # Regen
        self.tbl_img.setColumnWidth(8, 60)   # Delete

        self.tbl_img.setAlternatingRowColors(False)
        self.tbl_img.setShowGrid(False)
        self.tbl_img.setFrameStyle(QFrame.NoFrame)
        self.tbl_img.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_img.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_img.cellClicked.connect(self._on_img_tbl_clicked)
        self.tbl_img.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)
        self.tbl_img.setHorizontalScrollMode(QAbstractItemView.ScrollPerItem)
        self.tbl_img.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tbl_img.customContextMenuRequested.connect(self._on_img_tbl_context)
        wrapper.addWidget(self.tbl_img)

        # Initialize state
        self._img_quick_path = ""
        self._update_quick_image_preview(None)
        self._update_img_stats()
    # ===== GIỮ NGUYÊN CÁC METHODS NÀY (không thay đổi) =====
    def browse_image(self, image_type: str):
        path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select {image_type} image",
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp);;All files (*)"
        )
        if path:
            if image_type == "start":
                self.img_start_edit.setText(path)
            else:
                self.img_end_edit.setText(path)

    def _update_img_stats(self):
        ok = sum(1 for p in self.image_prompts if getattr(p, "status", "").lower()=="done")
        fail = sum(1 for p in self.image_prompts if getattr(p, "status", "").lower()=="failed")
        if hasattr(self, "lab_img_stats"):
            self.lab_img_stats.setText(f"✓ {ok}  •  ✗ {fail}")

    def _img_delete_all(self):
        if self.img_running_jobs > 0:
            QMessageBox.warning(self, "Busy", "Đang chạy jobs. Hãy dừng/chờ xong rồi xoá.")
            return
        if QMessageBox.question(self, "Delete All", "Xoá toàn bộ hàng?") == QMessageBox.Yes:
            self.image_prompts.clear()
            self._refresh_image_table()
            self._update_img_stats()

    def _img_delete_success(self):
        if QMessageBox.question(self, "Delete Success", "Xoá các hàng Done?") != QMessageBox.Yes:
            return
        self.image_prompts = [p for p in self.image_prompts if p.status.lower()!="done"]
        self._refresh_image_table()
        self._update_img_stats()

    def _img_delete_selected(self):
        rows = []
        for r in range(self.tbl_img.rowCount()):
            w = self.tbl_img.cellWidget(r, 0)
            if getattr(w, "_cb", None) and w._cb.isChecked():
                rows.append(r)
        if not rows:
            QMessageBox.information(self, "Info", "Chưa chọn hàng nào.")
            return
        if QMessageBox.question(self, "Delete Selected", f"Xoá {len(rows)} hàng đã chọn?") != QMessageBox.Yes:
            return
        for r in sorted(rows, reverse=True):
            if 0 <= r < len(self.image_prompts):
                del self.image_prompts[r]
        self._refresh_image_table()
        self._update_img_stats()

    def add_one_image_prompt(self):
        start = (getattr(self, "_img_quick_path", "") or "").strip()
        raw_text = (self._get_img_prompt_text() or "").strip()

        if not start or not os.path.exists(start):
            QMessageBox.warning(self, "Error", "Vui lòng chọn ảnh (click ô thumbnail).")
            return
        if not raw_text:
            QMessageBox.warning(self, "Error", "Vui lòng nhập prompt.")
            return

        # >>> NEW: tách nhiều prompt theo block (dòng trống = ngăn prompt)
        blocks = _split_prompt_blocks(raw_text)
        if not blocks:
            QMessageBox.warning(self, "Error", "Không tìm thấy prompt hợp lệ.")
            return

        added = 0
        if self.img_running_jobs > 0:
            # đang chạy → append xuống cuối để không phá hàng đang chạy
            for prompt in blocks:
                ipr = ImagePromptRow(prompt=prompt, start_image=start)
                self.image_prompts.append(ipr)
                self._append_image_prompt_row(ipr)
                added += 1
        else:
            # chưa chạy → insert theo thứ tự để prompt đầu nằm trên cùng
            for prompt in reversed(blocks):
                self.image_prompts.insert(0, ImagePromptRow(prompt=prompt, start_image=start))
                added += 1
            self._refresh_image_table()

        # dọn composer
        self.img_prompt_edit.clear()
        # Giữ lại thumbnail ảnh (vì có thể muốn add thêm batch mới). Nếu muốn reset ảnh thì gọi:
        # self._update_quick_image_preview(None)

        self._update_img_stats()
        if added > 1:
            QMessageBox.information(self, "Added", f"Đã thêm {added} prompts cho 1 ảnh.")


    def import_image_list(self):
        """Import CSV/TXT: prompt,start_image"""
        path, _ = QFileDialog.getOpenFileName(
            self, 
            "Import Image List", 
            "", 
            "CSV/Text files (*.csv *.txt);;All files (*)"
        )
        if not path:
            return
        
        count = 0
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 2:
                    prompt, start = parts[0], parts[1]
                    if os.path.exists(start):
                        self.image_prompts.insert(0, ImagePromptRow(
                            prompt=prompt,
                            start_image=start
                        ))
                        count += 1
        
        self._refresh_image_table()
        QMessageBox.information(self, "Imported", f"Đã nạp {count} items")
        self._update_img_stats()
        
    def _on_img_tbl_clicked(self, row: int, col: int):
        # Cột 2 là "Prompt"
        if col == 2 and 0 <= row < len(self.image_prompts):
            full = self.image_prompts[row].prompt
            # Mặc định: mở popup xem & sửa
            new_text = self._show_text_popup("Image2Video Prompt", full, editable=True)
            if new_text is not None and new_text.strip() != full.strip():
                # cập nhật model + UI
                self.image_prompts[row].prompt = new_text.strip()
                it = self.tbl_img.item(row, 2)
                if it: it.setText(self.image_prompts[row].prompt)

    def _on_img_tbl_context(self, pos):
        idx = self.tbl_img.indexAt(pos)
        if not idx.isValid(): return
        row, col = idx.row(), idx.column()
        if col != 2 or not (0 <= row < len(self.image_prompts)): 
            return

        from PySide6.QtWidgets import QMenu
        menu = QMenu(self)
        act_view  = menu.addAction("View Full Prompt…")
        act_edit  = menu.addAction("Edit Prompt…")
        act_copy  = menu.addAction("Copy Prompt")
        chosen = menu.exec(self.tbl_img.viewport().mapToGlobal(pos))  # ← ĐỔI exec_() THÀNH exec()
        if chosen is None: return

        cur = self.image_prompts[row].prompt
        if chosen == act_view:
            self._show_text_popup("Image2Video Prompt", cur, editable=False)
        elif chosen == act_edit:
            new_text = self._show_text_popup("Edit Image2Video Prompt", cur, editable=True)
            if new_text is not None and new_text.strip() != cur.strip():
                self.image_prompts[row].prompt = new_text.strip()
                it = self.tbl_img.item(row, 2)
                if it: it.setText(self.image_prompts[row].prompt)
        elif chosen == act_copy:
            QApplication.clipboard().setText(cur or "")

    def _refresh_image_table(self):
        """
        Refresh Image-to-Video table với cleanup đầy đủ
        """
        # ========================================
        # BƯỚC 1: CLEANUP TẤT CẢ WIDGETS CŨ
        # ========================================
        for row in range(self.tbl_img.rowCount()):
            self._cleanup_row_widgets(self.tbl_img, row)
        
        # ========================================
        # BƯỚC 2: CLEAR TABLE
        # ========================================
        self.tbl_img.setUpdatesEnabled(False)  # Tắt update để nhanh hơn
        self.tbl_img.setSortingEnabled(False)
        self.tbl_img.clearContents()
        self.tbl_img.setRowCount(0)
        
        # ========================================
        # BƯỚC 3: RENDER LẠI ROWS
        # ========================================
        try:
            for i, ipr in enumerate(self.image_prompts, start=1):
                r = self.tbl_img.rowCount()
                self.tbl_img.insertRow(r)
                
                # Select checkbox
                w = QWidget()
                box = QCheckBox()
                box.setChecked(True)
                lay = QHBoxLayout(w)
                lay.setContentsMargins(8, 0, 8, 0)
                lay.addWidget(box)
                lay.addStretch(1)
                self.tbl_img.setCellWidget(r, 0, w)
                w._cb = box
                
                # STT
                it_idx = QTableWidgetItem(str(i))
                it_idx.setTextAlignment(Qt.AlignCenter)
                self.tbl_img.setItem(r, 1, it_idx)
                
                # Prompt
                self.tbl_img.setItem(r, 2, QTableWidgetItem(ipr.prompt))
                
                # Start Image preview (col 3)
                self._set_img_preview_cell(r, 3, ipr.start_image)

                
                # Status (progress widget) at col 4
                self._ensure_img_progress_cell(r)
                
                # Video + Open
                if ipr.video and os.path.exists(ipr.video):
                    self._set_img_video_cell(r, ipr.video)
                else:
                    self.tbl_img.setItem(r, 5, QTableWidgetItem(""))
                    self.tbl_img.setItem(r, 6, QTableWidgetItem(""))
                    
                # Regen (col 7)
                btn_regen = QPushButton()
                btn_regen.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
                btn_regen.setToolTip("Regenerate this row")
                btn_regen.setFixedWidth(32)
                btn_regen.setIconSize(QSize(18, 18))
                btn_regen.clicked.connect(lambda _, row=r: self._img_regenerate_row(row))

                cell_regen = QWidget()
                lr = QHBoxLayout(cell_regen)
                lr.setContentsMargins(6, 2, 6, 2)
                lr.addWidget(btn_regen, 0, Qt.AlignCenter)
                self.tbl_img.setCellWidget(r, 7, cell_regen)

                # Delete (col 8)
                btn_del = QPushButton()
                btn_del.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
                btn_del.setToolTip("Delete this row")
                btn_del.setFixedWidth(32)
                btn_del.clicked.connect(lambda _, row=r: self._delete_img_row(row))
                
                cell = QWidget()
                l = QHBoxLayout(cell)
                l.setContentsMargins(6, 2, 6, 2)
                l.addWidget(btn_del, 0, Qt.AlignCenter)
                self.tbl_img.setCellWidget(r, 8, cell)
        
        finally:
            # ========================================
            # BƯỚC 4: BẬT LẠI UPDATE
            # ========================================
            self.tbl_img.setUpdatesEnabled(True)
            self.tbl_img.setSortingEnabled(True)
            
        # Update stats
        self._update_img_stats()
    def _ensure_img_progress_cell(self, row_idx: int):
        w = self.tbl_img.cellWidget(row_idx, 4)
        if isinstance(w, QWidget) and hasattr(w, "_sp"):
            return w._sp
        
        sp = StatusProgress(self)
        wrapper = QWidget()
        lay = QVBoxLayout(wrapper)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addStretch(1)
        lay.addWidget(sp)
        lay.addStretch(1)
        
        wrapper._sp = sp
        self.tbl_img.setCellWidget(row_idx, 4, wrapper)
        return sp


    def _set_img_preview_cell(self, row_idx: int, col_idx: int, path: str):
        """Hiển thị thumbnail ảnh thật"""
        wrap = QWidget()
        lay = QVBoxLayout(wrap)
        lay.setContentsMargins(6, 4, 6, 4)
        
        # Hiển thị thumbnail ảnh thật
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(160, 80)
        
        if path and os.path.exists(path):
            pm = QPixmap(path)
            if not pm.isNull():
                scaled = pm.scaled(160, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(scaled)
                icon_label.setStyleSheet("""
                    QLabel {
                        background: #f9fafb;
                        border: 1px solid #e5e7eb;
                        border-radius: 6px;
                    }
                """)
            else:
                icon_label.setText("🖼️")
                icon_label.setStyleSheet("""
                    QLabel {
                        background: #f0f9ff;
                        border: 2px solid #bae6fd;
                        border-radius: 8px;
                        font-size: 40px;
                    }
                """)
        else:
            icon_label.setText("🖼️")
            icon_label.setStyleSheet("""
                QLabel {
                    background: #f0f9ff;
                    border: 2px solid #bae6fd;
                    border-radius: 8px;
                    font-size: 40px;
                }
            """)
        
        cap = QLabel(os.path.basename(path) if path else "—")
        cap.setAlignment(Qt.AlignCenter)
        cap.setStyleSheet("color:#6b7280; font-size:11px;")
        
        lay.addWidget(icon_label)
        lay.addWidget(cap)
        
        self.tbl_img.setCellWidget(row_idx, col_idx, wrap)
        self.tbl_img.verticalHeader().resizeSection(row_idx, 110)

    def _img_select_all(self):
        for r in range(self.tbl_img.rowCount()):
            w = self.tbl_img.cellWidget(r, 0)
            if getattr(w, "_cb", None):
                w._cb.setChecked(True)

    def _img_clear_all(self):
        for r in range(self.tbl_img.rowCount()):
            w = self.tbl_img.cellWidget(r, 0)
            if getattr(w, "_cb", None):
                w._cb.setChecked(False)

    def _delete_img_row(self, row: int):
        if not (0 <= row < len(self.image_prompts)):
            return
        if QMessageBox.question(self, "Delete", "Xoá hàng đã chọn?") == QMessageBox.Yes:
            del self.image_prompts[row]
            self._refresh_image_table()
            self._update_img_stats()

    def on_img_stop_clicked(self):
        """Stop tất cả Image-to-Video jobs đang chạy"""
        if self.img_running_jobs <= 0:
            return
        
        # Set stop flag
        self.img_stop_flag["stop"] = True
        
        # Disable nút Stop ngay
        self.btn_img_stop.setEnabled(False)
        self.btn_img_stop.setText("Stopping...")
        
        # Reset tất cả jobs đang chạy về queue
        for row in list(self.img_active_rows):
            if 0 <= row < len(self.image_prompts):
                ipr = self.image_prompts[row]
                # Chỉ reset nếu chưa Done/Failed
                if ipr.status.lower() not in ("done", "failed"):
                    self._reset_job_to_queue(row, is_image=True)
                    self._stop_row_glow(row, is_image=True)
        
        # Clear active rows
        self.img_active_rows.clear()
        
        # Reset UI
        self.img_running_jobs = 0
        self.btn_img_generate.setEnabled(True)
        self.btn_img_stop.setEnabled(False)
        self.btn_img_stop.setText("Stop")
        
        # Update stats
        self._update_img_stats()
        
        QMessageBox.information(
            self, 
            "Stopped", 
            "Đã dừng tất cả Image-to-Video jobs.\n\n"
            "• Jobs thành công: giữ nguyên\n"
            "• Jobs đang chạy: đã đưa về Queue"
        )


    def start_image_generate_queue(self):
        if not self.image_prompts:
            QMessageBox.information(self, "Info", "Chưa có item nào.")
            return
        
        live = [a for a in self.accounts if a.status.lower()=="live"]
        if not live:
            QMessageBox.warning(self, "No account", "Không có tài khoản LIVE.")
            return
        
        cookie_path = live[0].path
        
        # Get selected rows
        rows = []
        for r in range(self.tbl_img.rowCount()):
            w = self.tbl_img.cellWidget(r, 0)
            if getattr(w, "_cb", None) and w._cb.isChecked():
                rows.append(r)
        
        if not rows:
            QMessageBox.information(self, "Info", "Hãy tick các hàng cần chạy.")
            return
        
        out_dir = Path(self.edit_outdir.text() or str(APP_DIR / "outputs"))
        self.img_stop_flag = {"stop": False}
        self.btn_img_generate.setEnabled(False)
        self.btn_img_stop.setEnabled(True)
        
        model = self.current_model()
        outputs = self.current_outputs()
        conc = self.current_concurrency()
        self.thread_pool.setMaxThreadCount(conc)

        self.img_running_jobs = 0
        default_timeout = self.current_img_timeout()
        for idx, r in enumerate(rows):
            ipr = self.image_prompts[r]
            
            # FIX: Use enumerate index for consistent numbering
            name_base = f"{idx+1:03d}_{_slugify(ipr.prompt, 28)}"
            
            # Set initial progress
            sp = self._ensure_img_progress_cell(r)
            sp.set_progress(0, "Queued")
            
            worker = ImageVideoWorker(
                r, cookie_path, ipr.start_image,
                ipr.prompt, model, outputs, out_dir, name_base,
                timeout=self.current_img_timeout(),
                retries=self.current_retries()
            )

            worker.signals.progress.connect(self._on_img_progress)
            worker.signals.done.connect(self._on_img_done)
            worker.signals.finished.connect(self._on_img_finished)
            
            self.img_running_jobs += 1
            self.thread_pool.start(worker)

    def _start_row_glow(self, row: int, is_image: bool = False):
        """Start row glow effect - placeholder (disabled)"""
        return  # Tắt hiệu ứng viền hàng

    def _stop_row_glow(self, row: int, is_image: bool = False):
        """Stop row glow effect - placeholder (disabled)"""
        return  # Tắt hiệu ứng viền hàng

    def _on_img_progress(self, row: int, payload: str):
        try:
            pct_s, label = payload.split("|", 1)
            pct = int(float(pct_s))
        except:
            pct, label = 0, payload

        if 0 < pct < 100:
            self._start_row_glow(row, is_image=True)   # <— bật glow cho bảng img

        sp = self._ensure_img_progress_cell(row)
        sp.set_progress(pct, label)

    def _on_img_done(self, row: int, result: Dict):
        """Image-to-Video job done callback"""
        ok = result.get("ok", False)
        path = result.get("video_path", "")
        
        self._stop_row_glow(row, is_image=True)
        
        # Check stop flag - nếu bị stop thì không update Done/Failed
        if self.img_stop_flag.get("stop"):
            # Job bị stop giữa chừng - đã reset về queue ở on_img_stop_clicked
            return
        
        # Xử lý bình thường khi KHÔNG bị stop
        if 0 <= row < len(self.image_prompts):
            self.image_prompts[row].status = "Done" if ok else "Failed"
            self.image_prompts[row].video = path if ok else ""
        
        if ok and path and os.path.exists(path):
            self._set_img_video_cell(row, path)
            sp = self._ensure_img_progress_cell(row)
            sp.set_progress(100, "Saved")
        else:
            sp = self._ensure_img_progress_cell(row)
            sp.set_progress(0, "Failed")
            if result.get("note"):
                QMessageBox.warning(self, f"Row {row+1}", result["note"][:800])
        
        self._update_img_stats()
    def _on_img_finished(self):
        """Image-to-Video job finished callback"""
        self.img_running_jobs -= 1
        
        # Nếu bị stop, không làm gì thêm
        if self.img_stop_flag.get("stop"):
            return
        
        if self.img_running_jobs <= 0:
            self.btn_img_generate.setEnabled(True)
            self.btn_img_stop.setEnabled(False)
            QMessageBox.information(self, "Done", "All image to video jobs finished.")
        
    def _make_field_cell(self, label_text: str, widget: QWidget, label_w: int = 160) -> QFrame:
        cell = QFrame(); cell.setObjectName("fieldCell")
        h = QHBoxLayout(cell); h.setContentsMargins(10,8,10,8); h.setSpacing(12)

        lab = QLabel(label_text); lab.setFixedWidth(label_w)
        lab.setObjectName("fieldLabel")
        h.addWidget(lab)
        h.addWidget(widget)
        h.addStretch(1)
        return cell

    def setup_image_generator_tab(self):
        """Setup Image Generator tab"""
        layout = QVBoxLayout(self.tab_image_generator)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Add Image Generator Tab
        if IMAGE_TAB_AVAILABLE:
            # Pass api_client, project_manager, and main_window for full integration
            self.image_gen_widget = ImageGeneratorTab(
                self.tab_image_generator, 
                api_client=self.api_client,
                project_manager=self.project_manager,
                main_window=self  # Pass MainWindow reference for "to Video" feature
            )
            layout.addWidget(self.image_gen_widget)
        else:
            # Fallback message
            msg = QLabel("Image Generator tab not available.\nPlease ensure image_tab_full.py is present.")
            msg.setAlignment(Qt.AlignCenter)
            msg.setStyleSheet("font-size: 16px; color: #ef4444; padding: 50px;")
            layout.addWidget(msg)

    def setup_settings_tab(self):
        root = QVBoxLayout(self.tab_settings)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(14)

        # --- Header ---
        title = QLabel("⚙️  Cài Đặt Hệ Thống")
        title.setStyleSheet("font-size:24px; font-weight:900;")
        subtitle = QLabel("Contact for email: hungse17002@gmail.com || Telegram: @hung251102 ")
        subtitle.setStyleSheet("color:#6b7280; font-size:13px; margin-bottom:8px;")
        root.addWidget(title)
        root.addWidget(subtitle)

        # --- Two-column layout ---
        two_col = QHBoxLayout()
        two_col.setSpacing(16)
        root.addLayout(two_col, 1)

        # ===== Left Card =====
        left_card = QFrame()
        left_card.setObjectName("card")
        left = QVBoxLayout(left_card)
        left.setContentsMargins(16, 16, 16, 16)
        left.setSpacing(12)

        sec_title = QLabel("⚡ Model & Hiệu năng")
        sec_title.setStyleSheet("font-weight:800; font-size:15px;")
        left.addWidget(sec_title)

        # Theme selector
        row_theme = QHBoxLayout()
        row_theme.setObjectName("settingRow")
        lab_theme = QLabel("Giao diện")
        lab_theme.setFixedWidth(160)
        self.cmb_theme = QComboBox()
        self.cmb_theme.addItems([
            "Indigo", "Aurora", "Sunset", "Ocean", "Midnight",
            "Neon", "Ember", "Plum", "Forest", "Carbon"
        ])
        self.cmb_theme.setFixedWidth(200)
        self.cmb_theme.currentTextChanged.connect(self.set_theme)
        row_theme.addWidget(lab_theme)
        row_theme.addWidget(self.cmb_theme)
        row_theme.addStretch(1)
        left.addLayout(row_theme)

        # Model options
        lab_model = QLabel("Model video")
        lab_model.setStyleSheet("font-weight:600; margin-top:6px;")
        left.addWidget(lab_model)

        self.model_group = QButtonGroup(self)
        for text, price, color, chk in [
            ("Veo 2 - Fast", "10 credit", "#10B981", False),
            ("Veo 3.1 - Fast", "20 credit", "#3B82F6", True),
            ("Veo 3.1 - Quality", "100 credit", "#8B5CF6", False),
            ("Veo 2 - Quality", "100 credit", "#F59E0B", False),
        ]:
            row = QFrame()
            row.setObjectName("settingRow")
            hl = QHBoxLayout(row)
            hl.setContentsMargins(8, 6, 8, 6)
            rb = QRadioButton(text)
            rb.setChecked(chk)
            self.model_group.addButton(rb)
            chip = QLabel(price)
            chip.setAlignment(Qt.AlignCenter)
            chip.setStyleSheet(
                f"background:{color}; color:white; border-radius:10px; padding:4px 10px;"
            )
            hl.addWidget(rb, 1)
            hl.addWidget(chip, 0)
            left.addWidget(row)

        # --- Grid 2×2: Concurrency / Outputs / Text timeout / Image timeout ---
        grid_wrap = QFrame()
        grid_wrap.setObjectName("fieldGrid")
        grid = QGridLayout(grid_wrap)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)

        # Spinboxes
        self.spin_conc = QSpinBox()
        self.spin_conc.setRange(1, 50)
        self.spin_conc.setValue(2)

        self.spin_outputs = QSpinBox()
        self.spin_outputs.setRange(1, 1)
        self.spin_outputs.setValue(1)
        self.spin_outputs.setVisible(False)

        self.spin_img_timeout = QSpinBox()
        self.spin_img_timeout.setRange(30, 900)
        self.spin_img_timeout.setValue(140)
        
        self.spin_retry = QSpinBox()
        self.spin_retry.setRange(0, 10)
        self.spin_retry.setValue(2)
        self.spin_retry.setFixedWidth(110)
        self.spin_retry.valueChanged.connect(self.save_settings)
        
        self.chk_no_preview = QCheckBox("Tắt video preview")
        self.chk_no_preview.setChecked(True)
        self.chk_no_preview.setToolTip("Chỉ hiện label thay vì video player. Click Open để xem video.")
        self.chk_no_preview.setCursor(Qt.PointingHandCursor)
        self.chk_no_preview.setMinimumHeight(32)
        self.chk_no_preview.setStyleSheet("""
            QCheckBox {
                spacing: 8px;
                font-weight: 600;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #9CA3AF;
                background: #ffffff;
                border-radius: 4px;
            }
            QCheckBox::indicator:hover {
                border-color: #6366F1;
                background: #EEF2FF;
            }
            QCheckBox::indicator:checked {
                background: #6366F1;
                border-color: #4F46E5;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTAiIHZpZXdCb3g9IjAgMCAxMiAxMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEgNUw0LjUgOC41TDExIDEuNSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
            }
        """)
        self.chk_no_preview.stateChanged.connect(self.save_settings)

        # Add to grid
        grid.addWidget(self._make_field_cell("Số job chạy song song", self.spin_conc), 0, 0)
        grid.addWidget(self._make_field_cell("Image→Video timeout (s)", self.spin_img_timeout), 0, 1)
        grid.addWidget(self._make_field_cell("Retries on fail", self.spin_retry), 1, 0)
        grid.addWidget(self.chk_no_preview, 1, 1)
        grid.setRowStretch(2, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        left.addWidget(grid_wrap)

        left.addStretch(1)
        two_col.addWidget(left_card, 1)

        # ===== Right Card =====
        right_card = QFrame()
        right_card.setObjectName("card")
        right = QVBoxLayout(right_card)
        right.setContentsMargins(16, 16, 16, 16)
        right.setSpacing(12)

        sec_title2 = QLabel("📁 Thư mục & Lưu trữ")
        sec_title2.setStyleSheet("font-weight:800; font-size:15px;")
        right.addWidget(sec_title2)

        row_outdir = QHBoxLayout()
        row_outdir.setObjectName("settingRow")
        lab_outdir = QLabel("Thư mục xuất video")
        lab_outdir.setFixedWidth(160)
        self.edit_outdir = QLineEdit(str(APP_DIR / "outputs"))
        self.edit_outdir.setReadOnly(True)
        self.edit_outdir.setMinimumWidth(280)
        btn_outdir = QPushButton("Browse…")
        btn_outdir.setObjectName("btn-teal")

        def _pick_outdir():
            folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục xuất video")
            if folder:
                self.edit_outdir.setText(folder)
                self.save_settings()
        
        btn_outdir.clicked.connect(_pick_outdir)
        row_outdir.addWidget(lab_outdir)
        row_outdir.addWidget(self.edit_outdir, 1)
        row_outdir.addWidget(btn_outdir)
        right.addLayout(row_outdir)

        note = QLabel("💡 Gợi ý: giữ timeout 120–240s tuỳ tải server.")
        note.setStyleSheet("color:#6b7280; font-size:12px; margin-top:6px;")
        right.addWidget(note)
        
        # Groq API for Auto-prompt
        groq_card = QFrame()
        groq_card.setObjectName("card")
        groq_lay = QVBoxLayout(groq_card)
        groq_lay.setContentsMargins(14, 12, 14, 12)
        groq_lay.setSpacing(8)
        
        groq_title = QLabel("🔑 Groq API (Auto-prompt)")
        groq_title.setStyleSheet("font-weight:800; font-size:15px;")
        groq_lay.addWidget(groq_title)
        
        self.ed_groq_keys = QPlainTextEdit()
        self.ed_groq_keys.setPlaceholderText("Nhập Groq API key (mỗi dòng một key)")
        self.ed_groq_keys.setMinimumHeight(80)
        groq_lay.addWidget(self.ed_groq_keys)
        
        groq_note = QLabel("💡 Để tự động tạo prompt từ ảnh. Không bắt buộc.")
        groq_note.setStyleSheet("color:#6b7280; font-size:11px;")
        groq_lay.addWidget(groq_note)
        
        groq_btn = QPushButton("Save")
        groq_btn.setObjectName("btn-teal")
        groq_btn.clicked.connect(self.save_settings)
        groq_lay.addWidget(groq_btn)
        
        right.addWidget(groq_card)
        
        right.addStretch(1)
        two_col.addWidget(right_card, 1)

        # Save khi đổi model
        for b in self.model_group.buttons():
            b.toggled.connect(self.save_settings)
    
    def _model_row(self, text: str, credit_text: str, color_hex: str, checked: bool=False) -> QWidget:
        row = QFrame(); row.setObjectName("modelRow")
        hl = QHBoxLayout(row); hl.setContentsMargins(12,10,12,10)
        rb = QRadioButton(text); rb.setChecked(checked)
        self.model_group.addButton(rb)
        hl.addWidget(rb, 1)
        credit = QLabel(credit_text)
        credit.setAlignment(Qt.AlignCenter)
        credit.setStyleSheet(f"background:{color_hex}; color:white; border-radius:6px; padding:6px 10px;")
        credit.setMinimumWidth(90)
        hl.addWidget(credit, 0)
        return row

    def current_model(self) -> str:
        for b in self.model_group.buttons():
            if b.isChecked(): return b.text()
        return "Veo 3.1 - Fast"

    def current_outputs(self) -> int:
        return int(self.spin_outputs.value())

    def current_concurrency(self) -> int:
        return int(self.spin_conc.value())

    # -------- ElevenLabs Audio Tab --------
    def setup_elevenlabs_tab(self):
        """Setup ElevenLabs Audio Generation tab - NHÚNG TOÀN BỘ GUI GỐC"""
        layout = QVBoxLayout(self.tab_elevenlabs)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if ELEVENLABS_AVAILABLE:
            # Tạo instance của ElevenLabsGUI nhưng dùng như Widget
            # Bỏ window decorations
            # Pass api_client và project_manager để load keys + voice folder
            self.elevenlabs_widget = ElevenLabsGUI(
                api_client=self.api_client,
                project_manager=self.project_manager
            )
            self.elevenlabs_widget.setWindowFlags(Qt.Widget)  # Set as widget, not window
            
            # Nhúng vào layout
            layout.addWidget(self.elevenlabs_widget)
        else:
            msg = QLabel("❌ ElevenLabs module not available\n\nPlease ensure ElevenlabsV15.py is present.")
            msg.setAlignment(Qt.AlignCenter)
            msg.setStyleSheet("font-size: 14px; color: #ef4444; padding: 50px;")
            layout.addWidget(msg)

    # -------- Accounts Tab --------
    def setup_accounts_tab(self):
        wrapper = QVBoxLayout(self.tab_accounts)
        head = QHBoxLayout()
        title = QLabel("Account Management"); title.setStyleSheet("font-size:20px; font-weight:900;")
        head.addWidget(title)
        
        # ← THÊM LABEL HIỂN THỊ FOLDER HIỆN TẠI
        self.lab_cookie_folder = QLabel("Folder: (chưa chọn)")
        self.lab_cookie_folder.setStyleSheet("color:#6b7280; font-size:12px; margin-left:12px;")
        head.addWidget(self.lab_cookie_folder)
        head.addStretch(1)

        self.btn_select = QPushButton("Select Cookie Folder")
        self.btn_select.clicked.connect(self.choose_folder)
        self.btn_select.setCursor(Qt.PointingHandCursor)
        self.btn_select.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        
        # ← THÊM NÚT RELOAD
        self.btn_reload = QPushButton("Reload Folder")
        self.btn_reload.clicked.connect(self._reload_cookie_folder)
        self.btn_reload.setCursor(Qt.PointingHandCursor)
        self.btn_reload.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.btn_reload.setToolTip("Reload cookies từ folder đã lưu (không cần chọn lại)")
        
        self.btn_check = QPushButton("Check Again")
        self.btn_check.clicked.connect(self.check_all)
        self.btn_check.setCursor(Qt.PointingHandCursor)
        self.btn_check.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        
        head.addWidget(self.btn_select)
        head.addWidget(self.btn_reload)
        head.addWidget(self.btn_check)
        wrapper.addLayout(head)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Status", "Email", "Credits", "Cookie File", "Configure", "Delete"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        wrapper.addWidget(self.table)

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục chứa cookies.txt")
        if not folder:
            return
        
        self._load_cookie_folder(folder, silent=False)
        self.check_all()  # Auto-check sau khi load
    def _load_cookie_folder(self, folder: str, silent: bool = False):
        """Load cookies from folder path."""
        if not folder or not os.path.isdir(folder):
            if not silent:
                QMessageBox.warning(self, "Error", f"Folder không tồn tại:\n{folder}")
            return
        
        files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(".txt")]
        files.sort()
        
        if not files:
            if not silent:
                QMessageBox.information(self, "No files", "Không tìm thấy file *.txt trong thư mục.")
            return
        
        self.accounts = [AccountRow(path=f) for f in files]
        self._last_cookie_folder = folder
        self.save_settings()
        
        # ← THÊM: Cập nhật label hiển thị folder
        if hasattr(self, "lab_cookie_folder"):
            short_path = folder if len(folder) < 60 else "..." + folder[-57:]
            self.lab_cookie_folder.setText(f"Folder: {short_path}")
            self.lab_cookie_folder.setToolTip(folder)  # Full path ở tooltip
        
        self.refresh_table()
        
        if not silent:
            QMessageBox.information(self, "Loaded", f"Đã load {len(files)} cookies từ:\n{folder}")
    def _reload_cookie_folder(self):
        """Reload cookies từ folder đã lưu"""
        folder = getattr(self, "_last_cookie_folder", "")
        if not folder:
            QMessageBox.information(self, "Info", 
                "Chưa có folder nào được lưu.\nHãy dùng 'Select Cookie Folder' để chọn lần đầu.")
            return
        
        self._load_cookie_folder(folder, silent=False)
        self.check_all()  # Auto-check sau khi reload
    def refresh_table(self):
        self.table.setRowCount(0)
        for idx, acc in enumerate(self.accounts):
            self.table.insertRow(idx)
            it_status = QTableWidgetItem(str(acc.status)); it_status.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(idx, 0, it_status)
            it_email = QTableWidgetItem(str(acc.email)); self.table.setItem(idx, 1, it_email)
            it_token = QTableWidgetItem(str(acc.tokens)); it_token.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(idx, 2, it_token)
            it_path = QTableWidgetItem(acc.path); self.table.setItem(idx, 3, it_path)

            btn_cfg = QPushButton("Configure"); btn_cfg.setCursor(Qt.PointingHandCursor)
            btn_cfg.setToolTip("Mở dự án mới, mở popup Cài đặt (dưới), chọn model & outputs (từ Settings).")
            btn_cfg.clicked.connect(lambda _, r=idx: self.configure_row(r))
            self.table.setCellWidget(idx, 4, btn_cfg)

            btn_del = QPushButton(); btn_del.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.clicked.connect(lambda _, r=idx: self.delete_row(r))
            self.table.setCellWidget(idx, 5, btn_del)

    def delete_row(self, row: int):
        if 0 <= row < len(self.accounts):
            del self.accounts[row]; self.refresh_table()

    def check_all(self):
        if not self.accounts:
            QMessageBox.information(self, "Info", "Chưa có tài khoản nào. Hãy chọn thư mục cookie trước.")
            return
        self.btn_select.setEnabled(False); self.btn_check.setEnabled(False)
        for row_idx, acc in enumerate(self.accounts):
            self.table.item(row_idx, 0).setText("Checking…")
            self.table.item(row_idx, 1).setText("…")
            self.table.item(row_idx, 2).setText("…")
            worker = CheckWorker(row_idx, acc.path)
            worker.signals.finished.connect(self.on_checked)
            self.thread_pool.start(worker)

    def on_checked(self, row_idx: int, result: Dict):
        if 0 <= row_idx < len(self.accounts):
            acc = self.accounts[row_idx]
            acc.status = result.get("status", "-")
            acc.email = result.get("email", "-") or "-"
            acc.tokens = str(result.get("tokens", "-"))
            if row_idx < self.table.rowCount():
                self.table.item(row_idx, 0).setText(acc.status)
                self.table.item(row_idx, 1).setText(acc.email)
                self.table.item(row_idx, 2).setText(acc.tokens)
        if self.thread_pool.activeThreadCount() <= 1:
            self.btn_select.setEnabled(True); self.btn_check.setEnabled(True)

    def configure_row(self, row: int):
        if not (0 <= row < len(self.accounts)): return
        acc = self.accounts[row]
        model = self.current_model()
        outputs = self.current_outputs()
        self.table.item(row, 0).setText(f"Configuring…")
        worker = ConfigureWorker(row, acc.path, model, outputs)
        worker.signals.finished.connect(self.on_configured)
        self.thread_pool.start(worker)

    def on_configured(self, row_idx: int, result: Dict):
        ok = result.get("ok", False)
        chosen = result.get("chosen_model", "")
        if row_idx < self.table.rowCount():
            self.table.item(row_idx, 0).setText(f"Configured: {chosen}" if ok else f"Failed")
        if ok:
            QMessageBox.information(self, "Configure done",
                f"Model: {chosen}\nURL: {result.get('final_url','')}")
        else:
            QMessageBox.warning(self, "Configure failed", result.get('note','Configuration failed'))

    def show_about(self):
        QMessageBox.information(self, "About",
            "Video Generator Pro - Optimized\n\n"
            
            "- Image to Video generation\n"
            "- Batch processing with progress tracking\n"
            "- Account management\n"
            "- Generation history\n"
            "- Multi-threaded processing\n"
        )
    # -------- License --------
    # >>> NEW: mở popup tạo prompt, đổ kết quả vào UI
    def open_prompt_builder(self, mode: str = "text"):
        pool = self.get_key_pool()
        llm = self.cmb_llm_model.currentText() if hasattr(self, "cmb_llm_model") else "llama-3.1-8b-instant"
        dlg = PromptBuilderDialog(self, key_pool=pool, llm_model=llm, default_mode=mode)
        if dlg.exec() != QDialog.Accepted:
            return
        prompts = dlg.output_prompts()
        if not prompts:
            return

        if mode == "text":
            # thêm tất cả vào queue
            if self.running_jobs > 0:
                for p in prompts:
                    pr = PromptRow(prompt=p)
                    self.prompts.append(pr)
                    self._append_prompt_row(pr)
            else:
                for p in reversed(prompts):  # đảo để prompt đầu nằm trên cùng
                    self.prompts.insert(0, PromptRow(prompt=p))
                self._refresh_prompt_table()
            self._update_img_stats()
            # điền prompt đầu vào ô nhập để dễ sửa tay nếu muốn
            if prompts:
                self.edit_prompt.setPlainText(prompts[0])
        else:
            # image mode: điền prompt đầu vào ô input; người dùng bấm Add to Queue
            self.img_prompt_edit.setText(prompts[0])

    def apply_styles(self):
        p = self._theme_palette(self._theme_name)

        # ---- PURE DARK when Midnight/Carbon ----
        is_pure_dark = self._theme_name.strip().lower() in {"midnight", "carbon"}
        if is_pure_dark:
            # một bảng màu tối thống nhất
            BG      = "#0a0f14" if self._theme_name.strip().lower()=="carbon" else "#0b1020"
            SUR     = "#101820" if self._theme_name.strip().lower()=="carbon" else "#121a2b"
            SUR2    = SUR
            BORDER  = "#1e2a36"
            HOVER   = "#151f2a"
            TEXT    = "#ffffff"
            SEL     = "#1e293b"
            SCROLL  = "#223042"
            PLACEH  = "#a7b1be"

            # prompt input (Text→Video)
            prompt_bg   = SUR
            prompt_text = TEXT
        else:
            # theme sáng như cũ
            BG, SUR, SUR2 = p['bg'], p['surface'], p['surface2']
            BORDER, HOVER = p['border'], p['hover']
            TEXT, SEL     = p['text'], p['sel_bg']
            SCROLL        = p.get('scroll', p['border'])
            PLACEH        = "#9ca3af"
            prompt_bg     = "#ffffff"
            prompt_text   = p['text']

        # --------- CSS tổng ---------
        css = f"""
        /* Prompt (Text→Video) */
        QTextEdit#promptEdit {{
            border: 1px solid {BORDER};
            border-radius: 10px;
            padding: 6px 8px;
            background: {prompt_bg};
            color: {prompt_text};
            selection-background-color: {SEL};
            selection-color: {TEXT};
        }}
        QTextEdit#promptEdit:focus {{ border: 1px solid {BORDER}; }}

        /* ===== App Base ===== */
        QMainWindow, QDialog, QWidget {{
            background: {BG};
            color: {TEXT};
            font-size: 14px;
        }}
        QMenuBar, QStatusBar {{ background: {SUR2}; color:{TEXT}; }}

        /* ===== Tabs ===== */
        QTabWidget::pane {{
            background: {SUR};
            border: 1px solid {BORDER};
            top: -1px; border-radius: 12px;
        }}
        QTabBar::tab {{
            padding: 10px 16px; margin: 2px;
            font-weight: 800;
            color: {TEXT};
            background: {SUR};
            border: 1px solid {BORDER};
            border-bottom: none;
            border-top-left-radius: 12px; border-top-right-radius: 12px;
        }}
        QTabBar::tab:hover    {{ background: {HOVER}; }}
        QTabBar::tab:selected {{
            background: {HOVER};
            color: {TEXT};
            border: 1px solid {BORDER};
        }}

        /* ===== Cards / Cells ===== */
        QFrame#card, QFrame#fieldCell, QFrame#fieldGrid, QFrame#settingRow, QFrame#modelRow {{
            background: {SUR};
            border: 1px solid {BORDER};
            border-radius: 10px;
        }}
        QLabel#fieldLabel {{ font-weight: 600; color: {TEXT}; }}

        /* ===== Tables ===== */
        QTableWidget {{
            background: {BG};
            color: {TEXT};
            border: 1px solid {BORDER};
            border-radius: 10px;
            gridline-color: {BORDER};
            selection-background-color: {SEL};
            selection-color: {TEXT};
        }}
        QTableWidget::item:hover {{ background: {HOVER}; }}
        QHeaderView::section {{
            background: {SUR2};
            color: {TEXT};
            padding: 8px; border: none; border-right: 1px solid {BORDER};
            font-weight: 700;
        }}

        /* ===== Buttons (tất cả nền tối, chữ trắng) ===== */
        QPushButton,
        QPushButton#btn-primary,
        QPushButton#btn-accent,
        QPushButton#btn-teal,
        QPushButton#btn-danger {{
            padding: 9px 14px; border-radius: 10px;
            border: 1px solid {BORDER};
            background: {SUR};
            color: {TEXT};
            font-weight: 700;
        }}
        QPushButton:hover {{ background: {HOVER}; border-color: {BORDER}; }}
        QPushButton:pressed {{ transform: translateY(1px); }}

        /* ===== Inputs ===== */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            border: 1px solid {BORDER}; border-radius: 10px; padding: 8px;
            background: {SUR}; color: {TEXT};
            selection-background-color: {SEL}; selection-color: {TEXT};
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{ border: 1px solid {BORDER}; }}
        QLineEdit#pill-input {{ border-radius: 999px; padding: 10px 14px; background: {SUR}; color: {TEXT}; }}

        /* ===== ProgressBar ===== */
        QProgressBar {{
            border: 1px solid {BORDER}; background: {SUR};
            padding: 2px; border-radius: 8px; height: 14px;
            text-align: center; color: {TEXT};
        }}
        QProgressBar::chunk {{ border-radius: 8px; background: {HOVER}; }}

        /* ===== ToolTip & Menus ===== */
        QToolTip, QMenu {{
            background: {SUR}; color: {TEXT}; border: 1px solid {BORDER};
            padding: 6px; border-radius: 8px;
        }}

        /* ===== Scrollbar ===== */
        QScrollBar:vertical {{
            background: {SUR2}; width: 12px; margin: 2px; border-radius: 6px;
        }}
        QScrollBar::handle:vertical {{
            background: {SCROLL}; border-radius: 6px; min-height: 24px;
        }}
        QScrollBar::handle:vertical:hover {{ background: {BORDER}; }}
        QScrollBar:horizontal {{
            background: {SUR2}; height: 12px; margin: 2px; border-radius: 6px;
        }}
        QScrollBar::handle:horizontal {{
            background: {SCROLL}; border-radius: 6px; min-width: 24px;
        }}
        """

        # Áp CSS
        self.setStyleSheet(css)

        # ---- Palette cho placeholder/text của các ô nhập ----
        from PySide6.QtGui import QPalette, QColor
        def _apply_palette(widget):
            if not widget: return
            pal = widget.palette()
            pal.setColor(QPalette.Text, QColor(TEXT if is_pure_dark else p['text']))
            pal.setColor(QPalette.PlaceholderText, QColor(PLACEH))
            widget.setPalette(pal)

        _apply_palette(getattr(self, "edit_prompt", None))
        _apply_palette(getattr(self, "img_prompt_edit", None))
        _apply_palette(getattr(self, "search", None))
        _apply_palette(getattr(self, "hist_search", None))
        _apply_palette(getattr(self, "edit_outdir", None))

# ============================== Entry ===============================
def main():
    app = QApplication(sys.argv)
    
    # Show login dialog first
    if LOGIN_DIALOG_AVAILABLE and API_CLIENT_AVAILABLE:
        login_dialog = LoginDialog()
        
        # Store api_client reference
        api_client_ref = [None]  # Use list to allow modification in nested function
        
        def on_login_success(api_client):
            api_client_ref[0] = api_client
        
        login_dialog.login_successful.connect(on_login_success)
        
        result = login_dialog.exec()
        
        if result != QDialog.Accepted or not api_client_ref[0]:
            # User cancelled login or login failed
            QMessageBox.warning(
                None, "Login Required",
                "Bạn phải đăng nhập để sử dụng WorkFlow Tool."
            )
            return 0
        
        # Login successful, create main window
        win = MainWindow()
        
        # Set authenticated user data
        win.api_client = api_client_ref[0]
        win.current_user = api_client_ref[0].user_info
        win.user_role = api_client_ref[0].user_info.get('role', 'user')
        
        # Update API client reference in ElevenLabs widget if available
        if hasattr(win, 'elevenlabs_widget') and win.elevenlabs_widget:
            win.elevenlabs_widget.api_client = win.api_client
            # Auto-load ElevenLabs keys from server
            QTimer.singleShot(1000, win.elevenlabs_widget.load_keys_from_server)
            # Auto-load Proxy keys from server
            QTimer.singleShot(1500, win.elevenlabs_widget.load_proxy_from_server)
        
        # Update API client reference in Image Generator widget if available
        if hasattr(win, 'image_gen_widget') and win.image_gen_widget:
            win.image_gen_widget.api_client = win.api_client
            # Auto-load Gemini keys from server
            QTimer.singleShot(2000, win.image_gen_widget.load_gemini_keys_from_server)
        
        # Update UI permissions
        win.update_ui_permissions()
        
        # Update admin status label if exists
        if hasattr(win, 'lbl_admin_status'):
            username = win.current_user.get('username', 'Unknown')
            win.lbl_admin_status.setText(f"✅ Connected as: {username}")
            win.lbl_admin_status.setStyleSheet("""
                font-size: 10pt;
                color: #059669;
                padding: 5px 10px;
                background-color: #d1fae5;
                border-radius: 4px;
            """)
        
    else:
        # Login dialog not available, use old method
        win = MainWindow()
        print("⚠️ Login dialog not available - running without authentication")
    
    if not getattr(win, "license_ok", True):
        return 0
    
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
