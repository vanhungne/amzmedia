import csv
from urllib.parse import urlparse, parse_qs
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox, QCheckBox,
    QSpinBox, QDoubleSpinBox, QTableWidget, QTableWidgetItem, QFileDialog,
    QMessageBox, QFrame, QScrollArea, QHeaderView, QMenu, QDialog,
    QDialogButtonBox, QTabWidget, QGroupBox, QSplitter, QRadioButton,
    QButtonGroup, QGridLayout, QProgressBar, QTreeWidget, QTreeWidgetItem,
    QAbstractItemView
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject, QThread, QEvent
from PySide6.QtGui import QFont, QColor, QTextCursor, QAction, QShortcut, QKeySequence, QClipboard
import json
import os
import requests
import time
import threading
import re
from datetime import datetime, timedelta, timezone
import queue
import subprocess
import platform
import hashlib
import base64
import shutil
import glob
import random
import pathlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import sys

# Optional Dependencies
try:
    import docx
except Exception:
    docx = None
APP_NAME = "Audio Generator V17"
APP_TAGLINE = "AMZ MEDIA <<Hưng>>"

# Cross-platform base directory
if os.name == 'nt':
    BASE_DIR = "C:/TotalTool"
else:
    BASE_DIR = os.path.expanduser("~/ElevenLabsAudio")

SETTINGS_DIR = os.path.join(BASE_DIR, "Settings")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
API_FILE = os.path.join(BASE_DIR, "API.txt")
VOICES_FILE = os.path.join(SETTINGS_DIR, "voices.json")
API_SETTINGS_FILE = os.path.join(SETTINGS_DIR, "api_settings.json")
VOICE_SETTINGS_FILE = os.path.join(SETTINGS_DIR, "voice_settings.json")
PROXY_LINKS_FILE = os.path.join(SETTINGS_DIR, "proxy_links.json")
EMBEDDED_PUBLIC_KEY = b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA8Sp6u0xiwQDdWlinmmbS
xvrjxmyYsIQf3IZjUg6BVrMTQTeY8dOlVmc+ro1d9/fOVt+TAklJv8WbQrjrU1pL
ACeWwPJoOXatzqDwZqXYzQmPnxOntOoeaDTh5IADUUK1q+rfeVNNByA6Hdg5+SQI
oU3LR/TT+GpSiKiYaCPBkGTd3Bax5lGs4eEsL+2wgbLvfOif9qEp0HbxYE9teB45
JyblSHCAaQD30YOzZm5hMkbOW8oGnGyZZe6KVT3AYo8xugORVu6YTfRrOty8FjDd
73pNTslBT25P725s/bPP305rp81+NIpXmuPzK4gZn8MVUt+A1KgwBGRhd/JHrDbj
DQIDAQAB
-----END PUBLIC KEY-----"""
LICENSE_FILE = pathlib.Path(r"C:\TotalTool\Settings\license_token.txt")
# Model IDs - OFFICIAL MODELS ONLY
MODEL_IDS = {
    "eleven_v3": "V3 (Alpha)",
    "eleven_flash_v2_5": "Flash 2.5",
    "eleven_flash_v2": "Flash 2",
    "eleven_turbo_v2_5": "Turbo 2.5",
    "eleven_turbo_v2": "Turbo 2",
    "eleven_multilingual_v2": "Multilingual v2"
}

V3_MODEL_ID = "eleven_v3"
V3_CHAR_LIMIT = 3000

# Chunk Status Constants
STATUS_QUEUE   = "Queue"
STATUS_PENDING = "Pending"
STATUS_SUCCESS = "Success"
STATUS_FAIL    = "Fail"

# Proxy URL Template - GIỐNG HỆT TKINTER
PROXY_URL_TEMPLATE = "https://proxyxoay.shop/api/get.php?key={KEY}&nhamang=random&tinhthanh=0"


# ================================================================================
# INITIALIZATION FUNCTIONS - TẠO FILE TỰ ĐỘNG
# ================================================================================

def ensure_directories_and_files():
    """Tạo tất cả folders và files cần thiết nếu chưa tồn tại"""
    try:
        # Tạo folders
        for directory in [BASE_DIR, SETTINGS_DIR, TEMP_DIR, OUTPUT_DIR]:
            os.makedirs(directory, exist_ok=True)
        
        # Tạo API.txt nếu chưa có
        if not os.path.exists(API_FILE):
            with open(API_FILE, 'w', encoding='utf-8') as f:
                f.write("# Paste your ElevenLabs API keys here, one per line\n")
                f.write("# Example: sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n")
            print(f"✅ Created empty API.txt at {API_FILE}")
        
        # Tạo voices.json nếu chưa có
        if not os.path.exists(VOICES_FILE):
            default_voices = [
                {"id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel"},
                {"id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi"},
                {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella"}
            ]
            with open(VOICES_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_voices, f, indent=2, ensure_ascii=False)
            print(f"✅ Created default voices.json at {VOICES_FILE}")
        
        # Tạo api_settings.json nếu chưa có
        if not os.path.exists(API_SETTINGS_FILE):
            default_settings = {
                'chunk_size': 800,
                'concurrency': 4,
                'gen_delay_ms': 0,
                'max_retries': 3,
                'timeout_s': 30,
                'credit_threshold': 1000,
                'multithread': True,
                'open_after_merge': True,
                'keep_chunks_after_merge': False,
                'proxy_mode': 'no_proxy'
            }
            with open(API_SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_settings, f, indent=2)
            print(f"✅ Created default api_settings.json at {API_SETTINGS_FILE}")
        
        # Tạo voice_settings.json nếu chưa có
        if not os.path.exists(VOICE_SETTINGS_FILE):
            default_voice_settings = {
                'model': 'Flash 2.5',
                'voice': 'Rachel (21m00Tcm4TlvDq8ikWAM)',
                'speed': 1.0,
                'stability': 0.5,
                'similarity': 0.8,
                'style': 0.0,
                'speaker_boost': False,
                'language_code': 'vi'
            }
            with open(VOICE_SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_voice_settings, f, indent=2)
            print(f"✅ Created default voice_settings.json at {VOICE_SETTINGS_FILE}")
        
        # Tạo proxy_links.json nếu chưa có
        if not os.path.exists(PROXY_LINKS_FILE):
            default_proxy = {
                'proxy_links': []
            }
            with open(PROXY_LINKS_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_proxy, f, indent=2)
            print(f"✅ Created empty proxy_links.json at {PROXY_LINKS_FILE}")
        
        print("✅ All directories and files initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing directories/files: {e}")
        return False


# ================================================================================
# UTILITY FUNCTIONS
# ================================================================================

def status_human_text(s: str) -> str:
    return {
        STATUS_QUEUE:   "🟦 Queue",
        STATUS_PENDING: "🟨 Pending",
        STATUS_SUCCESS: "✅ Success",
        STATUS_FAIL:    "❌ Fail",
    }.get(s, s or STATUS_QUEUE)


# ================================================================================
# INFRASTRUCTURE CLASSES  
# ================================================================================
try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


def get_machine_guid() -> str:
    """Đọc MachineGuid từ Registry."""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as k:
            v, _ = winreg.QueryValueEx(k, "MachineGuid")
        return str(v).strip()
    except Exception:
        return ""


def load_public_key():
    """Tải public key từ EMBEDDED_PUBLIC_KEY."""
    if not CRYPTO_AVAILABLE:
        return None
    try:
        return serialization.load_pem_public_key(EMBEDDED_PUBLIC_KEY)
    except Exception:
        return None


def verify_license_token(token: str, device_id: str) -> dict:
    """
    Xác thực token license.
    Returns: dict với các key:
        - valid: bool
        - reason: str
        - owner: str
        - exp_date: str
        - days_left: int
    """
    if not CRYPTO_AVAILABLE:
        return {"valid": False, "reason": "Cryptography library not installed"}
    
    if not token or not device_id:
        return {"valid": False, "reason": "Token or Device ID is empty"}
    
    try:
        # Parse token: DID|OWNER|YYYY-MM-DD|BASE64_SIGNATURE
        parts = token.split("|")
        if len(parts) != 4:
            return {"valid": False, "reason": "Invalid token format"}
        
        token_did, owner, exp_date_str, sig_b64 = parts
        
        # Check device ID match
        if token_did != device_id:
            return {"valid": False, "reason": f"Device ID mismatch\nExpected: {token_did}\nActual: {device_id}"}
        
        # Verify signature
        public_key = load_public_key()
        if not public_key:
            return {"valid": False, "reason": "Failed to load public key"}
        
        message = f"{token_did}|{owner}|{exp_date_str}".encode("utf-8")
        signature = base64.b64decode(sig_b64)
        
        try:
            public_key.verify(signature, message, padding.PKCS1v15(), hashes.SHA256())
        except Exception:
            return {"valid": False, "reason": "Invalid signature - Token has been tampered"}
        
        # Check expiration
        try:
            exp_date = datetime.strptime(exp_date_str, "%Y-%m-%d").date()
            today = datetime.now(timezone.utc).date()
            days_left = (exp_date - today).days
            
            if days_left < 0:
                return {
                    "valid": False, 
                    "reason": f"License expired on {exp_date_str}",
                    "owner": owner,
                    "exp_date": exp_date_str,
                    "days_left": days_left
                }
            
            return {
                "valid": True,
                "reason": "Valid",
                "owner": owner,
                "exp_date": exp_date_str,
                "days_left": days_left
            }
            
        except ValueError:
            return {"valid": False, "reason": "Invalid expiration date format"}
            
    except Exception as e:
        return {"valid": False, "reason": f"Verification error: {str(e)}"}


def check_license() -> tuple:
    """
    Kiểm tra license từ file.
    Returns: (valid: bool, info: dict)
    """
    if not CRYPTO_AVAILABLE:
        return False, {"reason": "⚠️ Cryptography library not installed\n\nPlease install: pip install cryptography"}
    
    # Check license file exists
    if not LICENSE_FILE.exists():
        return False, {"reason": f"❌ License file not found\n\nExpected location:\n{LICENSE_FILE}\n\nPlease contact your administrator."}
    
    # Read license token
    try:
        token = LICENSE_FILE.read_text(encoding="utf-8").strip()
    except Exception as e:
        return False, {"reason": f"❌ Failed to read license file\n\nError: {str(e)}"}
    
    # Get machine ID
    device_id = get_machine_guid()
    if not device_id:
        return False, {"reason": "❌ Failed to read Machine GUID from Registry"}
    
    # Verify token
    result = verify_license_token(token, device_id)
    
    if not result["valid"]:
        return False, result
    
    return True, result


# ================================================================================
# LICENSE DIALOG
# ================================================================================

class LicenseDialog(QDialog):
    """Dialog hiển thị khi license không hợp lệ - CHO PHÉP NHẬP LICENSE MỚI"""
    def __init__(self, info: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("❌ License Verification Failed")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        
        self.license_valid = False
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Error icon and title
        title_label = QLabel("🔒 LICENSE VERIFICATION FAILED")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #ef4444;
            padding: 15px;
            background-color: #fee;
            border-radius: 8px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Error message
        reason = info.get("reason", "Unknown error")
        self.msg_label = QLabel(reason)
        self.msg_label.setStyleSheet("""
            font-size: 13px;
            padding: 15px;
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 5px;
            color: #333;
        """)
        self.msg_label.setWordWrap(True)
        layout.addWidget(self.msg_label)
        
        # Machine info
        device_id = get_machine_guid()
        machine_frame = QFrame()
        machine_frame.setStyleSheet("""
            QFrame {
                background-color: #fafafa;
                border: 1px dashed #ccc;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        machine_layout = QVBoxLayout(machine_frame)
        
        machine_label = QLabel("Machine ID:")
        machine_label.setStyleSheet("font-size: 11px; color: #666; font-weight: bold;")
        machine_layout.addWidget(machine_label)
        
        machine_id_text = QLineEdit(device_id or 'Unable to read')
        machine_id_text.setReadOnly(True)
        machine_id_text.setStyleSheet("""
            QLineEdit {
                font-family: 'Consolas', monospace;
                font-size: 11px;
                background-color: #fff;
                border: 1px solid #ddd;
                padding: 5px;
            }
        """)
        machine_layout.addWidget(machine_id_text)
        
        # Copy button
        copy_btn = QPushButton("📋 Copy Machine ID")
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                font-size: 11px;
                padding: 5px 10px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        copy_btn.clicked.connect(lambda: self._copy_to_clipboard(device_id))
        machine_layout.addWidget(copy_btn)
        
        layout.addWidget(machine_frame)
        
        # License input section
        license_frame = QFrame()
        license_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f9ff;
                border: 2px solid #3b82f6;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        license_layout = QVBoxLayout(license_frame)
        
        license_title = QLabel("💡 Enter License Key to Activate:")
        license_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #1e40af;")
        license_layout.addWidget(license_title)
        
        self.license_input = QTextEdit()
        self.license_input.setPlaceholderText("Paste your license token here...")
        self.license_input.setMaximumHeight(80)
        self.license_input.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', monospace;
                font-size: 11px;
                background-color: white;
                border: 1px solid #94a3b8;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        license_layout.addWidget(self.license_input)
        
        # Activate button
        activate_btn = QPushButton("✅ Activate License")
        activate_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        activate_btn.clicked.connect(self._activate_license)
        license_layout.addWidget(activate_btn)
        
        layout.addWidget(license_frame)
        
        # Instructions
        instruction = QLabel(
            "⚠️ Please contact your administrator or software provider\n"
            "to obtain a valid license key for this machine."
        )
        instruction.setStyleSheet("font-size: 11px; color: #555; padding: 10px;")
        instruction.setAlignment(Qt.AlignCenter)
        layout.addWidget(instruction)
        
        # Spacer
        layout.addStretch()
        
        # Bottom buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        # Exit button
        exit_btn = QPushButton("❌ Exit Application")
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 8px 25px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        exit_btn.clicked.connect(self._exit_app)
        btn_layout.addWidget(exit_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def _copy_to_clipboard(self, text):
        """Copy machine ID to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        QMessageBox.information(self, "Copied", "Machine ID copied to clipboard!")
    
    def _activate_license(self):
        """Kích hoạt license"""
        license_token = self.license_input.toPlainText().strip()
        
        if not license_token:
            QMessageBox.warning(self, "Error", "Please enter a license key!")
            return
        
        # Get machine ID
        device_id = get_machine_guid()
        if not device_id:
            QMessageBox.critical(self, "Error", "Failed to read Machine GUID from Registry")
            return
        
        # Verify license
        result = verify_license_token(license_token, device_id)
        
        if result["valid"]:
            # Save license to file
            try:
                LICENSE_FILE.parent.mkdir(parents=True, exist_ok=True)
                LICENSE_FILE.write_text(license_token, encoding="utf-8")
                
                success_msg = (
                    f"✅ License Activated Successfully!\n\n"
                    f"Owner: {result.get('owner', 'N/A')}\n"
                    f"Expires: {result.get('exp_date', 'N/A')}\n"
                    f"Days Left: {result.get('days_left', 'N/A')}"
                )
                
                QMessageBox.information(self, "Success", success_msg)
                
                self.license_valid = True
                self.accept()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save license:\n{str(e)}")
        else:
            # Show error
            error_msg = f"❌ License Activation Failed\n\n{result.get('reason', 'Unknown error')}"
            self.msg_label.setText(error_msg)
            self.msg_label.setStyleSheet("""
                font-size: 13px;
                padding: 15px;
                background-color: #fee;
                border: 1px solid #ef4444;
                border-radius: 5px;
                color: #dc2626;
            """)
            QMessageBox.critical(self, "Activation Failed", result.get('reason', 'Unknown error'))
    
    def _exit_app(self):
        """Exit application"""
        QApplication.quit()
        sys.exit(1)
    
    def closeEvent(self, event):
        """Prevent closing without activating or exiting"""
        event.ignore()
        reply = QMessageBox.question(
            self, 
            'Confirm Exit',
            'Exit application without activating license?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._exit_app()


class APIKeyManager:
    """Thread-safe API key manager - GIỐNG HỆT TKINTER"""
    def __init__(self, api_file, base_dir, logger):
        self._lock = threading.Lock()
        self.api_file = api_file
        self.base_dir = base_dir
        self._keys = []
        self._idx = 0
        self._logger = logger

    def load_from_file(self):
        with self._lock:
            if os.path.exists(self.api_file):
                with open(self.api_file, 'r', encoding='utf-8') as f:
                    lines = [l.strip() for l in f.readlines()]
                self._keys = [k for k in lines if k.startswith('sk_') and len(k) >= 40]
                self._idx = 0
            else:
                self._keys = []
                self._idx = 0
        self._logger(f"🔑 Loaded {len(self._keys)} API keys")
        return len(self._keys) > 0

    def count(self):
        with self._lock:
            return len(self._keys)

    def get_next(self):
        with self._lock:
            if not self._keys:
                return None
            key = self._keys[self._idx]
            self._idx = (self._idx + 1) % len(self._keys)
            return key

    def current_snapshot(self):
        with self._lock:
            return list(self._keys)

    def remove_and_backup(self, api_key, backup_filename, reason):
        with self._lock:
            if api_key in self._keys:
                self._keys.remove(api_key)
                with open(self.api_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(self._keys))
                path = os.path.join(self.base_dir, backup_filename)
                existed = set()
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        existed = {l.strip() for l in f.readlines() if l.strip()}
                if api_key not in existed:
                    with open(path, 'a', encoding='utf-8') as f:
                        f.write(api_key + "\n")
                self._idx = 0 if self._idx >= len(self._keys) else self._idx
                self._logger(f"🗑️ Quarantined API ...{api_key[-4:]} → {backup_filename} ({reason})")


class ProxyProvider:
    """Manages proxy - GIỐNG HỆT TKINTER"""
    def __init__(self, get_links_callable, logger):
        self._lock = threading.Lock()
        self._current = None
        self._need_refresh = False
        self._get_links = get_links_callable
        self._logger = logger

    def mark_need_refresh(self):
        with self._lock:
            self._need_refresh = True

    def _fetch_new_proxy(self):
        links = self._get_links()
        if not links:
            return None
        link = random.choice(links)
        try:
            r = requests.get(link, timeout=10)
            if r.status_code == 200:
                data = r.json()
                st = data.get('status')
                
                if st == 100:
                    # Parse proxy format: IP:Port:User:Password
                    proxy_http = data.get('proxyhttp', '')
                    parts = proxy_http.split(':')
                    if len(parts) != 4:
                        self._logger(f"Invalid proxy format: {proxy_http}")
                        return None
                    
                    ip, port, user, pwd = parts
                    try:
                        port_num = int(port)
                        if port_num <= 0 or port_num > 65535:
                            self._logger(f"Invalid port: {port}")
                            return None
                    except ValueError:
                        self._logger(f"Port is not numeric: {port}")
                        return None
                    
                    # Build proxy URL for requests library
                    url = f"http://{user}:{pwd}@{ip}:{port}"
                    self._logger(f"Got proxy: {ip}:{port}")
                    return {'http': url, 'https': url}
                
                elif st == 101:
                    # Service busy - wait and retry
                    msg = data.get('message', '')
                    self._logger(f"Proxy service busy: {msg}")
                    m = re.search(r'(\d+)s', msg)
                    if m:
                        wait = int(m.group(1))
                        if 0 < wait <= 300:
                            self._logger(f"Waiting {wait}s for new proxy...")
                            time.sleep(wait)
                            return self._fetch_new_proxy()
                    return None
                else:
                    self._logger(f"Proxy service error (status {st}): {data.get('message','Unknown')}")
                    return None
        except Exception as e:
            self._logger(f"Proxy error: {str(e)}")
            return None

    def get_proxy(self):
        """Get current proxy or fetch new one if needed"""
        with self._lock:
            if self._current is None or self._need_refresh:
                self._current = self._fetch_new_proxy()
                self._need_refresh = False
            return self._current


# ================================================================================
# MAIN GUI CLASS
# ================================================================================

class ElevenLabsGUI(QMainWindow):
    def __init__(self, api_client=None, project_manager=None):
        super().__init__()
        
        # API Client for server integration (optional)
        self.api_client = api_client
        # Project Manager for voice output folder
        self.project_manager = project_manager
        
        # Initialize directories và files - TẠO TỰ ĐỘNG
        ensure_directories_and_files()
        
        # Initialize core data structures
        self.chunks = []
        self.chunks_by_num = {}
        self.voices_cache = []  # List format giống Tkinter
        self.proxy_keys = []  # Store proxy KEYS only
        self.generation_active = False
        self.worker_threads = []
        
        # Project folders - GIỐNG TKINTER
        self.selected_file = None
        self.project_text_path = None
        self.project_root = None
        self.project_name = None
        self.project_dir = None
        self.project_chunks_txt_dir = None
        self.project_chunks_audio_dir = None
        
        # Stats
        self.total_credits = 0
        self.proxy_total = 0
        self.proxy_ok = 0
        self.proxy_fail = 0
        
        # Initialize managers
        self.log_queue = queue.Queue()
        self.api_manager = APIKeyManager(API_FILE, BASE_DIR, self.log)
        self.proxy_provider = ProxyProvider(self._get_proxy_links, self.log)
        
        # Build UI TRƯỚC
        self.init_ui()
        
        # Setup hotkeys
        self.setup_hotkeys()
        
        # Load settings SAU khi UI đã được tạo
        self.log("Loading all settings...")
        self.api_manager.load_from_file()
        self.load_voices()
        self.load_voice_settings()
        self.load_proxy_links()
        self._load_settings()
        self.log("All settings loaded successfully")
        
        # Start log processing
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.process_logs)
        self.log_timer.start(100)

    def init_ui(self):
        self.setWindowTitle(f"{APP_NAME}")
        self.setGeometry(100, 50, 1600, 1000)
        
        # Apply theme
        self.apply_theme()
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Left side (70%)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.create_text_import_section(left_layout)
        self.create_chunks_section(left_layout)
        self.create_progress_section(left_layout)
        
        main_layout.addWidget(left_widget, 7)
        
        # Right side (30%)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.create_settings_section(right_layout)
        self.create_log_section(right_layout)
        
        main_layout.addWidget(right_widget, 3)

    def apply_theme(self):
        """Navy & Vibrant Orange theme - MODERN & PROFESSIONAL"""
        stylesheet = """
        QMainWindow, QWidget {
            background-color: #f8f9fa;
            color: #11224E;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 10pt;
        }
        QGroupBox {
            background-color: white;
            border: 2px solid #d1d9e6;
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 14px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 8px;
            color: #F87B1B;
            font-size: 11pt;
        }
        /* GRADIENT SHADOW EFFECT FOR SETTINGS GROUP */
        QGroupBox#settingsGroup {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 white, stop:0.02 #fff7f0, stop:0.98 #fff7f0, stop:1 white);
            border: 3px solid #F87B1B;
            border-radius: 10px;
            margin-top: 12px;
            padding-top: 14px;
        }
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #FF8C2E, stop:1 #F87B1B);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 10pt;
            min-height: 32px;
            text-shadow: 0px 1px 2px rgba(0, 0, 0, 0.3);
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #FFA04D, stop:1 #FF8C2E);
            border: 2px solid #FFB366;
            transform: translateY(-1px);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #E66A08, stop:1 #D35F00);
            transform: translateY(1px);
        }
        QPushButton:disabled {
            background-color: #8b99a8;
            color: #d1d5db;
            text-shadow: none;
        }
        QPushButton#secondaryButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1A3366, stop:1 #11224E);
            color: white;
            text-shadow: 0px 1px 2px rgba(0, 0, 0, 0.4);
        }
        QPushButton#secondaryButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #234580, stop:1 #1A3366);
            border: 2px solid #3d5a99;
        }
        QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
            background-color: white;
            border: 2px solid #d1d9e6;
            border-radius: 5px;
            padding: 6px;
            color: #11224E;
        }
        QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
            border: 2px solid #F87B1B;
            background-color: #fffcf9;
        }
        QComboBox {
            background-color: #11224E;
            color: white;
            border: 2px solid #11224E;
            border-radius: 5px;
            padding: 6px;
            min-height: 28px;
        }
        QComboBox:hover {
            border: 2px solid #F87B1B;
            background-color: #1A3366;
        }
        QComboBox::drop-down {
            border: none;
        }
        QComboBox QAbstractItemView {
            background-color: white;
            color: #11224E;
            selection-background-color: #F87B1B;
            selection-color: white;
            border: 1px solid #d1d9e6;
        }
        QTableWidget, QTreeWidget {
            background-color: white;
            border: 2px solid #d1d9e6;
            gridline-color: #e8eef5;
            color: #11224E;
        }
        QTableWidget::item:selected, QTreeWidget::item:selected {
            background-color: #FFE8D6;
            color: #11224E;
        }
        QTableWidget::item:hover {
            background-color: #FFF4E8;
        }
        QHeaderView::section {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #f1f5f9, stop:1 #e2e8f0);
            color: #11224E;
            padding: 8px;
            border: none;
            border-right: 1px solid #cbd5e1;
            border-bottom: 2px solid #94a3b8;
            font-weight: bold;
            font-size: 10pt;
        }
        QCheckBox, QRadioButton {
            color: #11224E;
            spacing: 5px;
        }
        QCheckBox::indicator, QRadioButton::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #94a3b8;
            border-radius: 4px;
            background-color: white;
        }
        QCheckBox::indicator:hover, QRadioButton::indicator:hover {
            border: 2px solid #F87B1B;
        }
        QCheckBox::indicator:checked {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #FF8C2E, stop:1 #F87B1B);
            border: 2px solid #F87B1B;
        }
        QRadioButton::indicator {
            border-radius: 9px;
        }
        QRadioButton::indicator:checked {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #FF8C2E, stop:1 #F87B1B);
            border: 3px solid white;
            outline: 2px solid #F87B1B;
        }
        QTabBar::tab {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #f1f5f9, stop:1 #e2e8f0);
            color: #334155;
            padding: 12px 20px;
            border: 2px solid #cbd5e1;
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            margin-right: 4px;
        }
        QTabBar::tab:selected {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 white, stop:1 #fffcf9);
            border-bottom: 4px solid #F87B1B;
            color: #F87B1B;
            font-weight: bold;
        }
        QTabBar::tab:hover:!selected {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #fff7f0, stop:1 #FFE8D6);
            color: #F87B1B;
        }
        QTabWidget::pane {
            border: 2px solid #cbd5e1;
            background-color: white;
            border-radius: 6px;
        }
        QProgressBar {
            border: 2px solid #d1d9e6;
            border-radius: 6px;
            text-align: center;
            background-color: white;
            color: #11224E;
            font-weight: bold;
            font-size: 11pt;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #F87B1B, stop:0.5 #FF8C2E, stop:1 #FFA04D);
            border-radius: 4px;
        }
        QMenu {
            background-color: white;
            border: 2px solid #cbd5e1;
            border-radius: 5px;
        }
        QMenu::item {
            padding: 8px 30px;
            color: #11224E;
        }
        QMenu::item:selected {
            background-color: #FFE8D6;
            color: #F87B1B;
        }
        QLabel {
            color: #11224E;
        }
        """
        self.setStyleSheet(stylesheet)
    def create_text_import_section(self, parent_layout):
        """Text Import section"""
        group = QGroupBox("📝 Text Import")
        layout = QVBoxLayout()
        
        row1 = QHBoxLayout()
        
        btn_choose = QPushButton("📁 Choose File")
        btn_choose.clicked.connect(self.choose_file_to_import)
        row1.addWidget(btn_choose)
        
        self.text_format_combo = QComboBox()
        self.text_format_combo.addItems(["SSML", "Plain Text"])
        row1.addWidget(self.text_format_combo)
        
        row1.addWidget(QLabel("Size:"))
        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setRange(100, 5000)
        self.chunk_size_spin.setValue(800)
        self.chunk_size_spin.setMaximumWidth(80)
        row1.addWidget(self.chunk_size_spin)
        
        btn_create = QPushButton("▶️ Create")
        btn_create.clicked.connect(self.create_chunks)
        row1.addWidget(btn_create)
        
        btn_load = QPushButton("📂 Load")
        btn_load.setObjectName("secondaryButton")
        btn_load.clicked.connect(self.load_project)
        row1.addWidget(btn_load)
        
        btn_clear = QPushButton("🗑️")
        btn_clear.setMaximumWidth(40)
        btn_clear.clicked.connect(self.clear_text_input)
        row1.addWidget(btn_clear)
        
        layout.addLayout(row1)
        group.setLayout(layout)
        parent_layout.addWidget(group)

    def create_chunks_section(self, parent_layout):
        """Chunks section with improved layout"""
        group = QGroupBox("📋 Chunks")
        layout = QVBoxLayout()
        
        # Table - Remove "No" column, make Content wider
        self.chunks_table = QTableWidget()
        self.chunks_table.setColumnCount(3)  # Only: Chars, Status, Content
        self.chunks_table.setHorizontalHeaderLabels(["Chars", "Status", "Content"])
        self.chunks_table.horizontalHeader().setStretchLastSection(True)
        self.chunks_table.setColumnWidth(0, 60)   # Chars
        self.chunks_table.setColumnWidth(1, 100)  # Status
        # Content takes remaining space (stretch)
        self.chunks_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.chunks_table.setSelectionMode(QTableWidget.ExtendedSelection)
        
        # Enable row numbers in vertical header
        self.chunks_table.verticalHeader().setVisible(True)  # Show row numbers
        self.chunks_table.verticalHeader().setDefaultSectionSize(25)  # Row height
        
        # Context menu
        self.chunks_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.chunks_table.customContextMenuRequested.connect(self.show_chunks_context_menu)
        
        layout.addWidget(self.chunks_table)
        group.setLayout(layout)
        parent_layout.addWidget(group)

    def create_progress_section(self, parent_layout):
        """Progress and Actions"""
        group = QGroupBox("⚡ Progress")
        layout = QVBoxLayout()
        
        # Stats row - Total chunks/chars
        stats_layout = QHBoxLayout()
        self.chunks_stats_label = QLabel("Total: 0 chunks | 0 chars")
        self.chunks_stats_label.setStyleSheet("color: #d64500; font-size: 10pt; padding: 5px; font-weight: bold;")
        stats_layout.addWidget(self.chunks_stats_label)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # Progress bar
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("0/0 (0%)")
        self.progress_label.setStyleSheet("color: #2c3e50; font-weight: bold; font-size: 11pt;")
        progress_layout.addWidget(self.progress_label)
        
        layout.addLayout(progress_layout)
        group.setLayout(layout)
        parent_layout.addWidget(group)
        
        # Actions
        actions_group = QGroupBox("🎬 Actions")
        actions_layout = QVBoxLayout()
        
        row1 = QHBoxLayout()
        
        # Single Generate button - click to generate ALL immediately
        self.btn_generate = QPushButton("▶️ Generate")
        self.btn_generate.setMinimumHeight(40)
        self.btn_generate.clicked.connect(self.start_generation_all)  # Direct action
        row1.addWidget(self.btn_generate)
        
        self.btn_stop = QPushButton("⏹️ Stop")
        self.btn_stop.setObjectName("secondaryButton")
        self.btn_stop.setMinimumHeight(40)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_generation)
        row1.addWidget(self.btn_stop)
        
        actions_layout.addLayout(row1)
        
        row2 = QHBoxLayout()
        self.btn_merge = QPushButton("🔗 Merge")
        self.btn_merge.setMinimumHeight(35)
        self.btn_merge.clicked.connect(self.merge_audio_files)
        row2.addWidget(self.btn_merge)
        
        self.btn_output = QPushButton("📂 Output")
        self.btn_output.setObjectName("secondaryButton")
        self.btn_output.setMinimumHeight(35)
        self.btn_output.clicked.connect(self.open_output_folder)
        row2.addWidget(self.btn_output)
        
        actions_layout.addLayout(row2)
        
        actions_group.setLayout(actions_layout)
        parent_layout.addWidget(actions_group)

    def create_settings_section(self, parent_layout):
        """Settings with tabs"""
        group = QGroupBox("⚙️ Settings")
        group.setObjectName("settingsGroup")  # For gradient border
        layout = QVBoxLayout()
        
        self.settings_tabs = QTabWidget()
        
        # New order: Voice -> API -> Generation -> Tools (removed Library)
        self.create_voice_tab()
        self.create_api_tab()
        self.create_generation_tab()
        self.create_tools_tab()
        
        layout.addWidget(self.settings_tabs)
        group.setLayout(layout)
        parent_layout.addWidget(group)

    def create_api_tab(self):
        """API tab - GIỐNG HỆT TKINTER"""
        api_tab = QWidget()
        api_tab.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
            }
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # API Keys
        api_group = QGroupBox("API Keys")
        api_layout = QVBoxLayout()
        
        btn_row = QHBoxLayout()
        btn_load_server = QPushButton("☁️ Load from Server")
        btn_load_server.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3b82f6, stop:1 #2563eb);
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
                    stop:0 #60a5fa, stop:1 #3b82f6);
            }
        """)
        btn_load_server.clicked.connect(self.load_keys_from_server)
        btn_row.addWidget(btn_load_server)
        
        btn_check = QPushButton("💰 Check Credits")
        btn_check.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #10b981, stop:1 #059669);
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
                    stop:0 #34d399, stop:1 #10b981);
            }
        """)
        btn_check.clicked.connect(self.check_credits)
        btn_row.addWidget(btn_check)
        
        self.api_status_label = QLabel("Ready")
        self.api_status_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        btn_row.addWidget(self.api_status_label)
        btn_row.addStretch()
        api_layout.addLayout(btn_row)
        
        credit_row = QHBoxLayout()
        credit_row.addWidget(QLabel("Min Credit:"))
        self.min_credit_spin = QSpinBox()
        self.min_credit_spin.setRange(0, 100000)
        self.min_credit_spin.setValue(1000)
        self.min_credit_spin.setMaximumWidth(100)
        credit_row.addWidget(self.min_credit_spin)
        credit_row.addStretch()
        api_layout.addLayout(credit_row)
        
        total_row = QHBoxLayout()
        total_row.addWidget(QLabel("💎 Total:"))
        self.total_credits_label = QLabel("0 credits")
        self.total_credits_label.setStyleSheet("color: #d64500; font-weight: bold; font-size: 11pt;")
        total_row.addWidget(self.total_credits_label)
        total_row.addStretch()
        api_layout.addLayout(total_row)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # Proxy - GIỐNG HỆT TKINTER
        proxy_group = QGroupBox("Proxy")
        proxy_layout = QVBoxLayout()
        
        radio_layout = QHBoxLayout()
        self.proxy_none_radio = QRadioButton("No Proxy")
        self.proxy_none_radio.setChecked(True)
        radio_layout.addWidget(self.proxy_none_radio)
        
        self.proxy_rotation_radio = QRadioButton("Rotation")
        radio_layout.addWidget(self.proxy_rotation_radio)
        
        self.proxy_stats_label = QLabel("Links: 0    OK: 0    Fail: 0")
        self.proxy_stats_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        radio_layout.addWidget(self.proxy_stats_label)
        radio_layout.addStretch()
        proxy_layout.addLayout(radio_layout)
        
        # Proxy buttons
        proxy_btn_row = QHBoxLayout()
        btn_load_proxy = QPushButton("☁️ Load from Server")
        btn_load_proxy.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3b82f6, stop:1 #2563eb);
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
                    stop:0 #60a5fa, stop:1 #3b82f6);
            }
        """)
        btn_load_proxy.clicked.connect(self.load_proxy_from_server)
        proxy_btn_row.addWidget(btn_load_proxy)
        
        btn_validate = QPushButton("✓ Validate")
        btn_validate.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1A3366, stop:1 #11224E);
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
                    stop:0 #2A4376, stop:1 #1A3366);
            }
        """)
        btn_validate.clicked.connect(self.validate_proxy_links)
        proxy_btn_row.addWidget(btn_validate)
        
        proxy_layout.addLayout(proxy_btn_row)
        
        proxy_group.setLayout(proxy_layout)
        layout.addWidget(proxy_group)
        
        layout.addStretch()
        api_tab.setLayout(layout)
        self.settings_tabs.addTab(api_tab, "🔑 API")

    def create_voice_tab(self):
        """Voice tab - COMPACT & CLEAN DESIGN"""
        voice_tab = QWidget()
        voice_tab.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
            }
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        
        # Model Section
        model_group = QGroupBox("Model")
        model_layout = QVBoxLayout()
        model_layout.setSpacing(8)
        model_layout.setContentsMargins(10, 12, 10, 10)
        
        model_row = QHBoxLayout()
        model_label = QLabel("Model:")
        model_label.setStyleSheet("font-weight: 600; color: #1f2937; font-size: 9pt;")
        model_label.setFixedWidth(70)
        model_row.addWidget(model_label)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "V3 (Alpha)",
            "Flash 2.5",
            "Flash 2",
            "Turbo 2.5",
            "Turbo 2",
            "Multilingual v2"
        ])
        self.model_combo.setCurrentText("Flash 2.5")
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        self.model_combo.setFixedHeight(32)
        self.model_combo.setMaximumWidth(250)
        self.model_combo.setStyleSheet("""
            QComboBox {
                padding: 6px 10px;
                font-size: 9pt;
                border: 2px solid #cbd5e1;
                border-radius: 5px;
                background: white;
                color: #1f2937;
            }
            QComboBox:hover {
                border-color: #F87B1B;
            }
            QComboBox:focus {
                border-color: #F87B1B;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #1f2937;
                selection-background-color: #F87B1B;
                selection-color: white;
            }
        """)
        model_row.addWidget(self.model_combo)
        model_row.addStretch()
        
        model_layout.addLayout(model_row)
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Voice Section
        voice_group = QGroupBox("Voice")
        voice_layout = QVBoxLayout()
        voice_layout.setSpacing(8)
        voice_layout.setContentsMargins(10, 12, 10, 10)
        
        voice_row = QHBoxLayout()
        voice_label = QLabel("Voice:")
        voice_label.setStyleSheet("font-weight: 600; color: #1f2937; font-size: 9pt;")
        voice_label.setFixedWidth(70)
        voice_row.addWidget(voice_label)
        
        self.voice_combo = QComboBox()
        self.voice_combo.setFixedHeight(32)
        self.voice_combo.setMaximumWidth(250)
        self.voice_combo.setStyleSheet("""
            QComboBox {
                padding: 6px 10px;
                font-size: 9pt;
                border: 2px solid #cbd5e1;
                border-radius: 5px;
                background: white;
                color: #1f2937;
            }
            QComboBox:hover {
                border-color: #F87B1B;
            }
            QComboBox:focus {
                border-color: #F87B1B;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #1f2937;
                selection-background-color: #F87B1B;
                selection-color: white;
            }
        """)
        voice_row.addWidget(self.voice_combo)
        voice_row.addStretch()
        voice_layout.addLayout(voice_row)
        
        # Voice buttons - compact row
        voice_btn_row = QHBoxLayout()
        voice_btn_row.setSpacing(6)
        
        btn_add_voice = QPushButton("➕ Add")
        btn_add_voice.setFixedSize(70, 28)
        btn_add_voice.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF8C2E, stop:1 #F87B1B);
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: 600;
                font-size: 9pt;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFA04D, stop:1 #FF8C2E);
            }
        """)
        btn_add_voice.clicked.connect(self.add_voice)
        voice_btn_row.addWidget(btn_add_voice)
        
        btn_remove_voice = QPushButton("➖ Remove")
        btn_remove_voice.setObjectName("secondaryButton")
        btn_remove_voice.setFixedSize(80, 28)
        btn_remove_voice.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1A3366, stop:1 #11224E);
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: 600;
                font-size: 9pt;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2A4376, stop:1 #1A3366);
            }
        """)
        btn_remove_voice.clicked.connect(self.remove_voice)
        voice_btn_row.addWidget(btn_remove_voice)
        
        btn_preview = QPushButton("🔊 Preview")
        btn_preview.setFixedSize(80, 28)
        btn_preview.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF8C2E, stop:1 #F87B1B);
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: 600;
                font-size: 9pt;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFA04D, stop:1 #FF8C2E);
            }
        """)
        btn_preview.clicked.connect(self.preview_voice)
        voice_btn_row.addWidget(btn_preview)
        
        voice_btn_row.addStretch()
        
        voice_layout.addLayout(voice_btn_row)
        voice_group.setLayout(voice_layout)
        layout.addWidget(voice_group)
        
        # Voice Parameters Section - COMPACT
        params_group = QGroupBox("Voice Parameters")
        params_layout = QVBoxLayout()
        params_layout.setSpacing(8)
        params_layout.setContentsMargins(10, 12, 10, 10)
        
        # V3 Tips label - compact
        self.v3_tips_label = QLabel("💡 V3 Alpha: Select stability mode below")
        self.v3_tips_label.setStyleSheet("""
            color: #ff6f00; 
            font-size: 8pt; 
            font-weight: bold; 
            background-color: #fff5f2; 
            padding: 6px 8px; 
            border-radius: 4px; 
            border: 1px solid #ff8c42;
        """)
        self.v3_tips_label.setWordWrap(True)
        self.v3_tips_label.setVisible(False)  # Hidden by default
        params_layout.addWidget(self.v3_tips_label)
        
        # Create grid for parameters - compact
        params_grid = QGridLayout()
        params_grid.setHorizontalSpacing(10)
        params_grid.setVerticalSpacing(8)
        
        # Speed row
        row = 0
        self.speed_label = QLabel("Speed:")
        self.speed_label.setStyleSheet("font-weight: 600; color: #1f2937; font-size: 9pt;")
        self.speed_label.setFixedWidth(70)
        params_grid.addWidget(self.speed_label, row, 0)
        
        self.speed_spin = QDoubleSpinBox()
        self.speed_spin.setRange(0.0, 2.0)
        self.speed_spin.setSingleStep(0.1)
        self.speed_spin.setValue(1.0)
        self.speed_spin.setFixedHeight(28)
        self.speed_spin.setMaximumWidth(100)
        self.speed_spin.setStyleSheet("""
            QDoubleSpinBox {
                padding: 4px 8px;
                font-size: 9pt;
                border: 2px solid #cbd5e1;
                border-radius: 4px;
                background: white;
                color: #1f2937;
            }
            QDoubleSpinBox:hover {
                border-color: #F87B1B;
            }
        """)
        params_grid.addWidget(self.speed_spin, row, 1)
        
        # Similarity row
        row += 1
        self.similarity_label = QLabel("Similarity:")
        self.similarity_label.setStyleSheet("font-weight: 600; color: #1f2937; font-size: 9pt;")
        self.similarity_label.setFixedWidth(70)
        params_grid.addWidget(self.similarity_label, row, 0)
        
        self.similarity_spin = QDoubleSpinBox()
        self.similarity_spin.setRange(0.0, 1.0)
        self.similarity_spin.setSingleStep(0.05)
        self.similarity_spin.setValue(0.8)
        self.similarity_spin.setFixedHeight(28)
        self.similarity_spin.setMaximumWidth(100)
        self.similarity_spin.setStyleSheet("""
            QDoubleSpinBox {
                padding: 4px 8px;
                font-size: 9pt;
                border: 2px solid #cbd5e1;
                border-radius: 4px;
                background: white;
                color: #1f2937;
            }
            QDoubleSpinBox:hover {
                border-color: #F87B1B;
            }
        """)
        params_grid.addWidget(self.similarity_spin, row, 1)
        
        # Stability row - COLUMN 2
        self.stability_label = QLabel("Stability:")
        self.stability_label.setStyleSheet("font-weight: 600; color: #1f2937; font-size: 9pt;")
        self.stability_label.setFixedWidth(70)
        params_grid.addWidget(self.stability_label, 0, 2)
        
        self.stability_combo = QComboBox()
        self.stability_combo.addItem("Creative", 0.0)
        self.stability_combo.addItem("Natural", 0.5)
        self.stability_combo.addItem("Robust", 1.0)
        self.stability_combo.setCurrentIndex(1)
        self.stability_combo.setFixedHeight(28)
        self.stability_combo.setMaximumWidth(120)
        self.stability_combo.setStyleSheet("""
            QComboBox {
                padding: 4px 8px;
                font-size: 9pt;
                border: 2px solid #cbd5e1;
                border-radius: 4px;
                background: white;
                color: #1f2937;
            }
            QComboBox:hover {
                border-color: #F87B1B;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #1f2937;
                selection-background-color: #F87B1B;
                selection-color: white;
            }
        """)
        params_grid.addWidget(self.stability_combo, 0, 3)
        
        # Style row - COLUMN 2
        self.style_label = QLabel("Style:")
        self.style_label.setStyleSheet("font-weight: 600; color: #1f2937; font-size: 9pt;")
        self.style_label.setFixedWidth(70)
        params_grid.addWidget(self.style_label, 1, 2)
        
        self.style_spin = QDoubleSpinBox()
        self.style_spin.setRange(0.0, 1.0)
        self.style_spin.setSingleStep(0.05)
        self.style_spin.setValue(0.0)
        self.style_spin.setFixedHeight(28)
        self.style_spin.setMaximumWidth(100)
        self.style_spin.setStyleSheet("""
            QDoubleSpinBox {
                padding: 4px 8px;
                font-size: 9pt;
                border: 2px solid #cbd5e1;
                border-radius: 4px;
                background: white;
                color: #1f2937;
            }
            QDoubleSpinBox:hover {
                border-color: #F87B1B;
            }
        """)
        params_grid.addWidget(self.style_spin, 1, 3)
        
        params_layout.addLayout(params_grid)
        
        # Bottom row: Language + Speaker Boost
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(10)
        
        self.language_label = QLabel("Language:")
        self.language_label.setStyleSheet("font-weight: 600; color: #1f2937; font-size: 9pt;")
        self.language_label.setFixedWidth(70)
        bottom_row.addWidget(self.language_label)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["vi", "en", "es", "fr", "de", "zh", "ja", "ko"])
        self.language_combo.setFixedHeight(28)
        self.language_combo.setMaximumWidth(100)
        self.language_combo.setStyleSheet("""
            QComboBox {
                padding: 4px 8px;
                font-size: 9pt;
                border: 2px solid #cbd5e1;
                border-radius: 4px;
                background: white;
                color: #1f2937;
            }
            QComboBox:hover {
                border-color: #F87B1B;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #1f2937;
                selection-background-color: #F87B1B;
                selection-color: white;
            }
        """)
        bottom_row.addWidget(self.language_combo)
        
        # Speaker boost checkbox
        self.speaker_boost_check = QCheckBox("🔊 Speaker Boost")
        self.speaker_boost_check.setStyleSheet("""
            QCheckBox {
                font-weight: 600;
                color: #1f2937;
                font-size: 9pt;
                padding: 4px;
                margin-left: 20px;
            }
        """)
        bottom_row.addWidget(self.speaker_boost_check)
        bottom_row.addStretch()
        
        params_layout.addLayout(bottom_row)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        layout.addStretch()
        voice_tab.setLayout(layout)
        self.settings_tabs.addTab(voice_tab, "🎤 Voice")

    def create_generation_tab(self):
        """Generation tab"""
        gen_tab = QWidget()
        gen_tab.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
            }
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        gen_group = QGroupBox("Generation")
        gen_layout = QGridLayout()
        
        gen_layout.addWidget(QLabel("Delay (ms):"), 0, 0)
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 10000)
        self.delay_spin.setValue(0)
        gen_layout.addWidget(self.delay_spin, 0, 1)
        
        gen_layout.addWidget(QLabel("Max retries:"), 1, 0)
        self.max_retries_spin = QSpinBox()
        self.max_retries_spin.setRange(1, 10)
        self.max_retries_spin.setValue(3)
        gen_layout.addWidget(self.max_retries_spin, 1, 1)
        
        gen_layout.addWidget(QLabel("Concurrency:"), 2, 0)
        self.concurrency_spin = QSpinBox()
        self.concurrency_spin.setRange(1, 20)
        self.concurrency_spin.setValue(4)
        gen_layout.addWidget(self.concurrency_spin, 2, 1)
        
        gen_layout.addWidget(QLabel("Timeout (s):"), 3, 0)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 300)
        self.timeout_spin.setValue(30)
        gen_layout.addWidget(self.timeout_spin, 3, 1)
        
        self.enable_multithread_check = QCheckBox("Enable multithread")
        self.enable_multithread_check.setChecked(True)
        gen_layout.addWidget(self.enable_multithread_check, 4, 0, 1, 2)
        
        gen_group.setLayout(gen_layout)
        layout.addWidget(gen_group)
        
        merge_group = QGroupBox("Merge")
        merge_layout = QVBoxLayout()
        
        self.open_after_merge_check = QCheckBox("Open after merge")
        self.open_after_merge_check.setChecked(True)
        merge_layout.addWidget(self.open_after_merge_check)
        
        self.auto_merge_check = QCheckBox("Auto-merge when complete")
        self.auto_merge_check.setChecked(True)  # Enable by default
        merge_layout.addWidget(self.auto_merge_check)
        
        self.keep_chunks_check = QCheckBox("Keep chunk files")
        merge_layout.addWidget(self.keep_chunks_check)
        
        merge_group.setLayout(merge_layout)
        layout.addWidget(merge_group)
        
        layout.addStretch()
        gen_tab.setLayout(layout)
        self.settings_tabs.addTab(gen_tab, "⚙️ Generation")

    def create_tools_tab(self):
        """Tools tab"""
        tools_tab = QWidget()
        tools_tab.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
            }
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        btn_open_output = QPushButton("📂 Open Output Folder")
        btn_open_output.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f59e0b, stop:1 #d97706);
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
                    stop:0 #fbbf24, stop:1 #f59e0b);
            }
        """)
        btn_open_output.clicked.connect(self.open_output_folder)
        layout.addWidget(btn_open_output)
        
        btn_open_settings = QPushButton("📂 Open Settings Folder")
        btn_open_settings.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #06b6d4, stop:1 #0891b2);
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
                    stop:0 #22d3ee, stop:1 #06b6d4);
            }
        """)
        btn_open_settings.clicked.connect(self.open_settings_folder)
        layout.addWidget(btn_open_settings)
        
        btn_save_settings = QPushButton("💾 Save Settings")
        btn_save_settings.setStyleSheet("""
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
        btn_save_settings.clicked.connect(self.save_all_settings)
        layout.addWidget(btn_save_settings)
        
        layout.addStretch()
        tools_tab.setLayout(layout)
        self.settings_tabs.addTab(tools_tab, "🔧 Tools")

    def create_log_section(self, parent_layout):
        """Log section"""
        group = QGroupBox("📝 Log")
        layout = QVBoxLayout()
        
        btn_row = QHBoxLayout()
        btn_save = QPushButton("💾 Save")
        btn_save.setObjectName("secondaryButton")
        btn_save.clicked.connect(self.save_logs)
        btn_row.addWidget(btn_save)
        
        btn_clear = QPushButton("🗑️ Clear")
        btn_clear.clicked.connect(self.clear_logs)
        btn_row.addWidget(btn_clear)
        
        self.wrap_log_check = QCheckBox("Wrap")
        self.wrap_log_check.setChecked(True)
        self.wrap_log_check.stateChanged.connect(self.toggle_log_wrap)
        btn_row.addWidget(self.wrap_log_check)
        btn_row.addStretch()
        
        layout.addLayout(btn_row)
        
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont("Consolas", 9))
        self.log_area.setLineWrapMode(QTextEdit.WidgetWidth)
        layout.addWidget(self.log_area)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)

    def setup_hotkeys(self):
        """Setup keyboard shortcuts"""
        # F5: Start generation
        self.shortcut_f5 = QShortcut(QKeySequence(Qt.Key_F5), self)
        self.shortcut_f5.activated.connect(self.start_generation_all)
        
        # Ctrl+S: Save settings
        self.shortcut_save = QShortcut(QKeySequence.Save, self)
        self.shortcut_save.activated.connect(self.save_all_settings)

    # ================================================================================
    # CONTEXT MENU
    # ================================================================================
    
    def show_chunks_context_menu(self, position):
        """Show context menu for chunks table"""
        menu = QMenu()
        
        edit_action = menu.addAction("✏️ Edit Content")
        edit_action.triggered.connect(self.edit_selected_chunk)
        
        queue_action = menu.addAction("🟦 Mark as Queue")
        queue_action.triggered.connect(self.mark_selected_queue)
        
        menu.addSeparator()
        
        open_audio_action = menu.addAction("🔊 Open Audio")
        open_audio_action.triggered.connect(self.open_selected_audio)
        
        open_text_action = menu.addAction("📄 Open Text File")
        open_text_action.triggered.connect(self.open_selected_text)
        
        menu.addSeparator()
        
        regen_action = menu.addAction("🔁 Regenerate Selected")
        regen_action.triggered.connect(self.start_generation_selected)
        
        menu.exec(self.chunks_table.viewport().mapToGlobal(position))

    def edit_selected_chunk(self):
        """Edit selected chunk content"""
        selected = self.chunks_table.selectedItems()
        if not selected:
            return
        
        row = self.chunks_table.currentRow()
        if row < 0 or row >= len(self.chunks):
            return
        
        chunk = self.chunks[row]
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit Chunk {chunk['number']}")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        text_edit = QTextEdit()
        text_edit.setPlainText(chunk['content'])
        layout.addWidget(text_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.Accepted:
            new_content = text_edit.toPlainText()
            chunk['content'] = new_content
            chunk['chars'] = len(new_content)
            
            # Save to file
            if chunk.get('file'):
                with open(chunk['file'], 'w', encoding='utf-8') as f:
                    f.write(new_content)
            
            self.update_chunks_display()
            self.log(f"✏️ Edited chunk {chunk['number']}")

    def mark_selected_queue(self):
        """Mark selected chunks as Queue"""
        nums = self.get_selected_chunk_numbers()
        if not nums:
            return
        
        for n in nums:
            c = self.chunks_by_num.get(n)
            if c:
                c['status'] = STATUS_QUEUE
        
        self.update_chunks_display()
        self.log(f"🟦 Marked {len(nums)} chunk(s) as Queue")

    def open_selected_audio(self):
        """Open audio file for selected chunk"""
        nums = self.get_selected_chunk_numbers()
        if not nums:
            return
        
        for n in nums:
            c = self.chunks_by_num.get(n)
            if c and c.get('audio_file') and os.path.exists(c['audio_file']):
                self.open_file(c['audio_file'])

    def open_selected_text(self):
        """Open text file for selected chunk"""
        nums = self.get_selected_chunk_numbers()
        if not nums:
            return
        
        for n in nums:
            c = self.chunks_by_num.get(n)
            if c and c.get('file') and os.path.exists(c['file']):
                self.open_file(c['file'])

    def get_selected_chunk_numbers(self):
        """Get list of selected chunk numbers"""
        rows = set()
        for item in self.chunks_table.selectedItems():
            rows.add(item.row())
        
        nums = []
        for row in rows:
            if 0 <= row < len(self.chunks):
                nums.append(self.chunks[row]['number'])
        
        return nums

    # ================================================================================
    # API MANAGEMENT - GIỐNG HỆT TKINTER
    # ================================================================================
    
    def import_api_keys(self):
        """Open API.txt file for editing - GIỐNG HỆT TKINTER"""
        try:
            if os.name == 'nt':
                os.startfile(API_FILE)
            else:
                subprocess.call(['open', API_FILE])
            self.log("Opened API.txt file. Please paste your API keys there.")
        except Exception as e:
            self.log(f"Error opening API file: {str(e)}")

    def check_credits(self):
        """Check credits - GIỐNG HỆT TKINTER"""
        if not self.api_manager.load_from_file():
            self.log("No API keys found")
            return
        
        total = self.api_manager.count()
        if total == 0:
            self.log("No valid API keys found")
            return
        
        self.log("💰 Checking credits...")
        threading.Thread(target=self._check_credits_thread, daemon=True).start()

    def _check_credits_thread(self):
        """Check credits thread - GIỐNG HỆT TKINTER"""
        try:
            threshold = self.min_credit_spin.value()
            total_remaining_credits = 0
            valid_keys = []
            snapshot = self.api_manager.current_snapshot()
            
            for api_key in snapshot:
                try:
                    headers = {'xi-api-key': api_key}
                    r = requests.get('https://api.elevenlabs.io/v1/user/subscription',
                                   headers=headers, timeout=10)
                    if r.status_code == 200:
                        d = r.json()
                        used = d.get('character_count', 0)
                        limit = d.get('character_limit', 0)
                        remaining = max(0, limit - used)
                        total_remaining_credits += remaining
                        if remaining >= threshold:
                            valid_keys.append(api_key)
                            self.log(f"✅ API ...{api_key[-4:]}: {remaining:,} credits")
                        else:
                            self.log(f"⚠️ API ...{api_key[-4:]}: {remaining:,} credits (Below threshold)")
                    else:
                        self.log(f"❌ API ...{api_key[-4:]}: Error {r.status_code}")
                except Exception as e:
                    self.log(f"❌ API ...{api_key[-4:]}: {str(e)}")
            
            # Save only valid keys
            with open(API_FILE, 'w', encoding='utf-8') as f:
                f.write('\n'.join(valid_keys))
            self.api_manager.load_from_file()
            
            self.total_credits_label.setText(f"{total_remaining_credits:,} credits")
            self.log(f"💎 Total: {total_remaining_credits:,} credits")
            self.log(f"✅ Valid keys: {len(valid_keys)}")
            
        except Exception as e:
            self.log(f"💥 Error: {str(e)}")

    # ================================================================================
    # PROXY MANAGEMENT - GIỐNG HỆT TKINTER
    # ================================================================================
    
    def _get_proxy_links(self):
        """Convert proxy KEYS to full URLs - GIỐNG HỆT TKINTER"""
        try:
            urls = []
            for key in self.proxy_keys:
                if key.startswith('http://') or key.startswith('https://'):
                    urls.append(key)
                else:
                    full_url = PROXY_URL_TEMPLATE.replace("{KEY}", key)
                    urls.append(full_url)
            return urls
        except Exception:
            return []

    def add_proxy_key(self):
        """Add proxy KEY (not URL) - GIỐNG HỆT TKINTER"""
        key = self.proxy_key_input.text().strip()
        if key:
            self.proxy_keys.append(key)
            self.save_proxy_links()
            self.proxy_key_input.clear()
            self.update_proxy_stats()
            self.log(f"✅ Added proxy key")

    def save_proxy_links(self):
        """Save proxy links - GIỐNG HỆT TKINTER"""
        try:
            links = self._get_proxy_links()
            with open(PROXY_LINKS_FILE, 'w', encoding='utf-8') as f:
                json.dump({'proxy_links': links}, f, indent=2)
            self.update_proxy_stats()
            self.log(f"Saved {len(links)} proxy links")
        except Exception as e:
            self.log(f"Error saving proxy links: {str(e)}")

    def load_proxy_links(self):
        """Load proxy links - GIỐNG HỆT TKINTER"""
        try:
            if os.path.exists(PROXY_LINKS_FILE):
                with open(PROXY_LINKS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    links = data.get('proxy_links', [])
                # Extract keys from URLs
                self.proxy_keys = []
                for link in links:
                    if 'key=' in link:
                        # Extract key from URL
                        key = link.split('key=')[1].split('&')[0]
                        self.proxy_keys.append(key)
                    else:
                        self.proxy_keys.append(link)
                self.update_proxy_stats()
                self.log(f"Loaded {len(self.proxy_keys)} proxy links")
            else:
                self.log("Proxy links file not found")
        except Exception as e:
            self.log(f"Error loading proxy links: {str(e)}")

    def edit_proxy_links(self):
        """Edit proxy links - GIỐNG HỆT TKINTER"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Proxy Links")
        dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Proxy Keys (one per line):"))
        
        text_edit = QTextEdit()
        text_edit.setPlainText('\n'.join(self.proxy_keys))
        layout.addWidget(text_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.Accepted:
            self.proxy_keys = [line.strip() for line in text_edit.toPlainText().split('\n') if line.strip()]
            self.save_proxy_links()
            self.log(f"💾 Saved {len(self.proxy_keys)} proxy keys")

    def validate_proxy_links(self):
        """Validate proxy links - GIỐNG TKINTER"""
        self.log("🔍 Starting proxy validation...")
        threading.Thread(target=self._validate_proxy_links_thread, daemon=True).start()

    def _validate_proxy_links_thread(self):
        """Validate proxy thread - GIỐNG TKINTER"""
        try:
            links = self._get_proxy_links()
            total = len(links)
            ok = 0
            fail = 0
            
            if total == 0:
                self.log("⚠️ No proxy links to validate")
                return
            
            self.log(f"🔎 Validating {total} proxy link(s)...")
            
            # Update initial UI
            QTimer.singleShot(0, lambda: self.update_proxy_validation_ui(0, total, 0, 0))
            
            for i, link in enumerate(links, 1):
                good = False
                try:
                    r = requests.get(link, timeout=8)
                    if r.status_code == 200:
                        try:
                            data = r.json()
                        except Exception:
                            data = {}
                        
                        st = int(data.get("status", 0))
                        # 100 = OK, 101 = Busy (still usable), 102 = Invalid key
                        if st in (100, 101):
                            good = True
                            self.log(f"✅ Proxy {i}/{total}: OK (status {st})")
                        else:
                            good = False
                            self.log(f"❌ Proxy {i}/{total}: Failed (status {st})")
                    else:
                        good = False
                        self.log(f"❌ Proxy {i}/{total}: HTTP {r.status_code}")
                except Exception as e:
                    good = False
                    self.log(f"❌ Proxy {i}/{total}: {str(e)}")
                
                if good:
                    ok += 1
                else:
                    fail += 1
                
                # Update progress
                QTimer.singleShot(0, lambda d=i, t=total, o=ok, f=fail: self.update_proxy_validation_ui(d, t, o, f))
            
            # Save final stats
            self.proxy_ok = ok
            self.proxy_fail = fail
            
            # Update final UI
            QTimer.singleShot(0, self.update_proxy_stats)
            
            self.log(f"✅ Validation done • Total: {total} • Usable: {ok} • Failed: {fail}")
            
        except Exception as e:
            self.log(f"💥 Validation error: {str(e)}")

    def update_proxy_validation_ui(self, done, total, ok, fail):
        """Update validation progress UI"""
        try:
            self.proxy_stats_label.setText(f"Links: {total}    OK: {ok}    Fail: {fail}")
        except Exception:
            pass

    def update_proxy_stats(self):
        """Update proxy stats"""
        self.proxy_total = len(self.proxy_keys)
        self.proxy_stats_label.setText(f"Links: {self.proxy_total}    OK: {self.proxy_ok}    Fail: {self.proxy_fail}")

    # ================================================================================
    # VOICE MANAGEMENT - GIỐNG HỆT TKINTER
    # ================================================================================
    
    def load_voices(self):
        """Load voices - GIỐNG HỆT TKINTER"""
        try:
            if os.path.exists(VOICES_FILE):
                with open(VOICES_FILE, 'r', encoding='utf-8') as f:
                    self.voices_cache = json.load(f)  # List format
                self.log(f"Loaded {len(self.voices_cache)} voices from file")
                # Update combo box ngay sau khi load - FIX
                self.update_voice_list()
            else:
                self.voices_cache = []
                self.log("voices.json file not found")
        except Exception as e:
            self.voices_cache = []
            self.log(f"Error loading voices: {str(e)}")

    def save_voices(self):
        """Save voices"""
        try:
            with open(VOICES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.voices_cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log(f"Error saving voices: {str(e)}")

    def update_voice_list(self):
        """Update voice combo - GIỐNG HỆT TKINTER"""
        self.voice_combo.clear()
        if isinstance(self.voices_cache, list):
            for v in self.voices_cache:
                if isinstance(v, dict):
                    name = v.get('name', 'Unknown')
                    vid = v.get('id', '')
                    self.voice_combo.addItem(f"{name} ({vid})", vid)

    def add_voice(self):
        """Add voice manually - GIỐNG HỆT TKINTER"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Voice")
        dialog.setMinimumSize(400, 200)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Voice ID:"))
        id_input = QLineEdit()
        layout.addWidget(id_input)
        
        layout.addWidget(QLabel("Voice Name:"))
        name_input = QLineEdit()
        layout.addWidget(name_input)
        
        layout.addWidget(QLabel("Example: ID = 21m00Tcm4TlvDq8ikWAM, Name = Rachel"))
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.Accepted:
            vid = id_input.text().strip()
            vname = name_input.text().strip()
            if vid and vname:
                new_voice = {'id': vid, 'name': vname}
                self.voices_cache.append(new_voice)
                self.save_voices()
                self.update_voice_list()
                self.log(f"✅ Added voice: {vname}")

    def remove_voice(self):
        """Remove voice - GIỐNG HỆT TKINTER"""
        current_vid = self.voice_combo.currentData()
        if current_vid:
            self.voices_cache = [v for v in self.voices_cache if v.get('id') != current_vid]
            self.save_voices()
            self.update_voice_list()
            self.log(f"🗑️ Removed voice")

    def preview_voice(self):
        """Preview voice"""
        if not self.api_manager.count():
            QMessageBox.warning(self, "No API", "Please add API keys first")
            return
        
        voice_id = self.voice_combo.currentData()
        if not voice_id:
            QMessageBox.warning(self, "No Voice", "Please select a voice")
            return
        
        self.log("🎙 Generating preview...")
        threading.Thread(target=self._preview_voice_thread, args=(voice_id,), daemon=True).start()

    def _preview_voice_thread(self, voice_id):
        """Preview voice thread"""
        try:
            api_key = self.api_manager.get_next()
            if not api_key:
                self.log("No API keys available")
                return
            
            # Get proxy if enabled
            proxies = None
            if self.proxy_rotation_radio.isChecked():
                proxies = self.proxy_provider.get_proxy()
            
            # Create session
            session = self._get_session(proxies)
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
            
            payload = {
                "text": "This is a short preview of the selected voice.",
                "model_id": self._get_model_id(),
                "voice_settings": {
                    "stability": self.stability_combo.currentData(),  # Get value
                    "similarity_boost": self.similarity_spin.value(),
                    "style": self.style_spin.value(),
                    "use_speaker_boost": self.speaker_boost_check.isChecked()
                }
            }
            
            timeout = self.timeout_spin.value()
            r = session.post(url, json=payload, headers=headers, timeout=timeout)
            
            if r.status_code == 200:
                out = os.path.join(OUTPUT_DIR, f"preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3")
                with open(out, "wb") as f:
                    f.write(r.content)
                self.log(f"✅ Preview saved: {os.path.basename(out)}")
                QTimer.singleShot(0, lambda: self.open_file(out))
            else:
                self.log(f"❌ Preview error: HTTP {r.status_code}")
        except Exception as e:
            self.log(f"💥 Preview error: {str(e)}")

    def on_model_changed(self, model_name):
        """Handle model change - show/hide settings based on model"""
        is_v3 = model_name == "V3 (Alpha)"
        
        # Show/hide V3 tips
        self.v3_tips_label.setVisible(is_v3)
        
        if is_v3:
            # V3: Chỉ show Stability, ẩn hết còn lại
            self.speed_label.setVisible(False)
            self.speed_spin.setVisible(False)
            
            self.stability_label.setVisible(True)
            self.stability_combo.setVisible(True)
            
            self.similarity_label.setVisible(False)
            self.similarity_spin.setVisible(False)
            
            self.style_label.setVisible(False)
            self.style_spin.setVisible(False)
            
            self.language_label.setVisible(False)
            self.language_combo.setVisible(False)
            
            self.speaker_boost_check.setVisible(False)
            
            # Log stability mode
            current_stability = self.stability_combo.currentData()
            if current_stability == 0.0:
                self.log("⚠️ V3 Creative (0.0): Most emotional, prone to hallucinations")
            elif current_stability == 0.5:
                self.log("✅ V3 Natural (0.5): Balanced (RECOMMENDED)")
            else:
                self.log("🔒 V3 Robust (1.0): Highly stable, consistent")
        else:
            # Other models: Show tất cả settings
            self.speed_label.setVisible(True)
            self.speed_spin.setVisible(True)
            
            self.stability_label.setVisible(True)
            self.stability_combo.setVisible(True)
            
            self.similarity_label.setVisible(True)
            self.similarity_spin.setVisible(True)
            
            self.style_label.setVisible(True)
            self.style_spin.setVisible(True)
            
            self.language_label.setVisible(True)
            self.language_combo.setVisible(True)
            
            self.speaker_boost_check.setVisible(True)

    def load_voice_settings(self):
        """Load voice settings - UPDATED for 6 official models"""
        try:
            if os.path.exists(VOICE_SETTINGS_FILE):
                with open(VOICE_SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    vs = json.load(f)
                model = vs.get('model', 'Flash 2.5')
                
                # Accept both old and new model names
                valid_models = ["V3 (Alpha)", "Flash 2.5", "Flash 2", "Turbo 2.5", "Turbo 2", "Multilingual v2"]
                if model in valid_models:
                    self.model_combo.setCurrentText(model)
                elif model in ["Multilingual v1", "English v1"]:
                    # Migrate old models to Multilingual v2
                    self.model_combo.setCurrentText("Multilingual v2")
                    self.log(f"⚠️ Migrated {model} → Multilingual v2")
                
                # Restore saved voice - FIX
                saved_voice = vs.get('voice', '')
                if saved_voice:
                    # Tìm voice trong combo
                    idx = self.voice_combo.findText(saved_voice)
                    if idx >= 0:
                        self.voice_combo.setCurrentIndex(idx)
                        self.log(f"Restored voice: {saved_voice}")
                
                self.speed_spin.setValue(vs.get('speed', 1.0))
                
                # Set stability combo based on value
                stability_val = vs.get('stability', 0.5)
                if stability_val <= 0.0:
                    self.stability_combo.setCurrentIndex(0)  # Creative
                elif stability_val <= 0.5:
                    self.stability_combo.setCurrentIndex(1)  # Natural
                else:
                    self.stability_combo.setCurrentIndex(2)  # Robust
                
                self.similarity_spin.setValue(vs.get('similarity', 0.8))
                self.style_spin.setValue(vs.get('style', 0.0))
                self.speaker_boost_check.setChecked(vs.get('speaker_boost', False))
                lang = vs.get('language_code', 'vi')
                idx = self.language_combo.findText(lang)
                if idx >= 0:
                    self.language_combo.setCurrentIndex(idx)
                self.log("Voice settings loaded successfully")
            else:
                self.log("Voice settings file not found")
        except Exception as e:
            self.log(f"Error loading voice settings: {str(e)}")

    # ================================================================================
    # FILE OPERATIONS
    # ================================================================================
    
    def choose_file_to_import(self):
        """Choose file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choose File", "", 
            "Text Files (*.txt);;Word Documents (*.docx);;CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            self.import_file(file_path)

    def import_file(self, file_path):
        """Import file và tự động chia chunk luôn - GIỐNG TKINTER"""
        try:
            # Lưu thông tin project - GIỐNG TKINTER
            self.selected_file = file_path
            self.project_text_path = file_path
            self.project_root = os.path.dirname(file_path)
            self.project_name = os.path.splitext(os.path.basename(file_path))[0]
            self.project_dir = os.path.join(self.project_root, f"{self.project_name}_tts")
            self.project_chunks_txt_dir = os.path.join(self.project_dir, "chunks_txt")
            self.project_chunks_audio_dir = os.path.join(self.project_dir, "chunks_audio")
            
            # Tạo folder structure
            try:
                os.makedirs(self.project_chunks_txt_dir, exist_ok=True)
                os.makedirs(self.project_chunks_audio_dir, exist_ok=True)
                self.log(f"📁 Created project folder: {self.project_dir}")
            except Exception as e:
                self.log(f"Error creating project folders: {e}")
            
            # Import content
            text = ""
            if file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                self.log(f"📄 Imported: {os.path.basename(file_path)}")
            elif file_path.endswith('.docx') and docx:
                doc = docx.Document(file_path)
                text = '\n\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
                self.log(f"📄 Imported DOCX: {os.path.basename(file_path)}")
            elif file_path.endswith('.csv'):
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                text = '\n'.join([', '.join(row) for row in rows])
                self.log(f"📊 Imported CSV: {os.path.basename(file_path)}")
            
            if text:
                # Tự động chia chunk luôn - GIỐNG TKINTER
                self.imported_text = text
                self.create_chunks_from_text(text)
                self.log("✂️ Auto-split done (after import)")
                
        except Exception as e:
            self.log(f"❌ Error: {e}")

    def create_chunks_from_text(self, text):
        """Tạo chunks từ text - gọi tự động khi import - GIỐNG TKINTER"""
        if not text.strip():
            return
        
        chunk_size = self.chunk_size_spin.value()
        text_chunks = self.split_text_into_chunks(text, chunk_size)
        
        if not text_chunks:
            return
        
        # Xóa file tạm cũ
        for p in glob.glob(os.path.join(TEMP_DIR, "chunk_*.txt")):
            try:
                os.remove(p)
            except:
                pass
        
        # Nơi lưu txt chunk: ưu tiên thư mục project - GIỐNG TKINTER
        base_txt_dir = self.project_chunks_txt_dir if self.project_chunks_txt_dir else TEMP_DIR
        os.makedirs(base_txt_dir, exist_ok=True)
        
        self.chunks = []
        for i, chunk_text in enumerate(text_chunks, 1):
            chunk_file = os.path.join(base_txt_dir, f"chunk_{i:03d}.txt")
            with open(chunk_file, 'w', encoding='utf-8') as f:
                f.write(chunk_text)
            
            chunk = {
                'number': i,
                'content': chunk_text,
                'file': chunk_file,
                'status': STATUS_QUEUE,
                'audio_file': None,
                'chars': len(chunk_text)
            }
            self.chunks.append(chunk)
        
        self._index_chunks()
        self.update_chunks_display()
        self.log(f"✅ Created {len(text_chunks)} chunks in {base_txt_dir}")

    def clear_text_input(self):
        """Clear text"""
        self.imported_text = ""
        self.chunks = []
        self.chunks_by_num = {}
        self.update_chunks_display()
        self.log("🗑️ Cleared")

    def create_chunks(self):
        """Create chunks - dùng khi muốn re-chunk với size mới"""
        if not hasattr(self, 'imported_text') or not self.imported_text:
            QMessageBox.warning(self, "Error", "No text to create chunks from. Please import a file first.")
            return
        
        # Re-chunk với size mới
        self.create_chunks_from_text(self.imported_text)

    def split_text_into_chunks(self, text, max_size):
        """Split text"""
        if not text.strip():
            return []
        
        chunks = []
        sentences = re.split(r'([.!?]+[\s\n]+)', text)
        sentences = [sentences[i] + (sentences[i+1] if i+1 < len(sentences) else '') 
                    for i in range(0, len(sentences), 2)]
        
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_size:
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return [c for c in chunks if c]

    def load_project(self):
        """Load project"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Project", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.chunks = data.get('chunks', [])
                self._index_chunks()
                self.update_chunks_display()
                self.log(f"📂 Loaded: {os.path.basename(file_path)}")
            except Exception as e:
                self.log(f"❌ Error: {e}")

    # ================================================================================
    # GENERATION - WITH ALL MODES
    # ================================================================================
    
    def start_generation_all(self):
        """Start generation for all non-success chunks"""
        target = [c for c in self.chunks if c['status'] != STATUS_SUCCESS]
        self._start_generation(target)

    def start_generation_failed(self):
        """Start generation for failed chunks only"""
        target = [c for c in self.chunks if c['status'] == STATUS_FAIL]
        if not target:
            self.log("No failed chunks to generate")
            return
        self._start_generation(target)

    def start_generation_selected(self):
        """Start generation for selected chunks"""
        nums = self.get_selected_chunk_numbers()
        if not nums:
            self.log("No selected chunks")
            return
        
        tgtset = set(nums)
        target = [c for c in self.chunks if c['number'] in tgtset and c['status'] != STATUS_SUCCESS]
        if not target:
            self.log("Nothing to generate from selected")
            return
        
        self._start_generation(target)

    def _start_generation(self, target_chunks, auto_mode=False):
        """Start generation
        
        Args:
            target_chunks: List of chunks to generate
            auto_mode: If True, skip confirmation dialogs (for auto workflow)
        """
        if not target_chunks:
            if not auto_mode:
                QMessageBox.warning(self, "Error", "No chunks to generate")
            return
        
        if self.api_manager.count() == 0:
            if not auto_mode:
                QMessageBox.warning(self, "Error", "No API keys")
            return
        
        voice_id = self.voice_combo.currentData()
        if not voice_id:
            if not auto_mode:
                QMessageBox.warning(self, "Error", "Select a voice")
            return
        
        # V3 Alpha Warning (skip in auto mode)
        model_name = self.model_combo.currentText()
        if model_name == "V3 (Alpha)" and not auto_mode:
            num_gen = self.v3_generations_spin.value()
            stability = self.stability_combo.currentData()
            
            # Determine mode name
            mode_text = self.stability_combo.currentText()
            
            if stability == 0.0:
                desc = "Most emotional, prone to hallucinations"
            elif stability == 0.5:
                desc = "Balanced and neutral (RECOMMENDED)"
            else:  # 1.0
                desc = "Highly stable, consistent like v2"
            
            msg = f"🎭 V3 Alpha Mode:\n\n"
            msg += f"• Stability: {mode_text}\n"
            msg += f"  → {desc}\n\n"
            msg += f"• Generating {num_gen} version(s) per chunk\n"
            msg += f"• Only STABILITY setting works\n"
            msg += f"• Review and select best results\n"
            msg += f"• Not for real-time applications\n\n"
            msg += f"Continue?"
            
            reply = QMessageBox.question(
                self, "V3 Alpha Mode", msg,
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Set chunks to Queue
        for chunk in target_chunks:
            chunk['status'] = STATUS_QUEUE
        self.update_chunks_display()
        
        self.generation_active = True
        self.btn_generate.setEnabled(False)
        self.btn_stop.setEnabled(True)
        
        # Check và log proxy mode - GIỐNG TKINTER
        if self.proxy_rotation_radio.isChecked():
            self.log("🔄 Proxy rotation enabled")
            self.proxy_provider.mark_need_refresh()
        else:
            self.log("🔗 Using direct connection (no proxy)")
        
        self.log(f"🚀 Starting generation for {len(target_chunks)} chunks...")
        
        # Start auto-refresh timer for UI updates
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_chunks_display)
        self.refresh_timer.timeout.connect(self.update_progress)
        self.refresh_timer.timeout.connect(self.check_generation_complete)  # Check if done
        self.refresh_timer.start(500)  # Update every 500ms
        
        self.worker_threads = []
        num_workers = self.concurrency_spin.value()
        
        for i in range(num_workers):
            thread = threading.Thread(target=self.generation_worker, args=(i+1,), daemon=True)
            thread.start()
            self.worker_threads.append(thread)

    def stop_generation(self):
        """Stop generation"""
        self.generation_active = False
        self.btn_generate.setEnabled(True)
        self.btn_stop.setEnabled(False)
        
        # Stop refresh timer
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
        
        # Final update
        self.update_chunks_display()
        self.update_progress()
        
        self.log("⏹️ Stopped")

    def generation_worker(self, worker_id):
        """Worker thread - GIỐNG TKINTER"""
        # Get model ID
        model_name = self.model_combo.currentText()
        model_id = {v: k for k, v in MODEL_IDS.items()}.get(model_name, "eleven_turbo_v2_5")
        
        while self.generation_active:
            chunk = None
            for c in self.chunks:
                if c['status'] == STATUS_QUEUE:
                    c['status'] = STATUS_PENDING
                    chunk = c
                    break
            
            if not chunk:
                break
            
            QTimer.singleShot(0, self.update_chunks_display)
            
            # Retry logic - TỐI ƯU HÓA
            max_retries = self.max_retries_spin.value()
            retry_count = 0
            success = False
            
            while retry_count < max_retries and not success:
                if retry_count > 0:
                    self.log(f"🔄 Retry {retry_count}/{max_retries} for chunk {chunk['number']}")
                    time.sleep(1)  # Wait 1s between retries
                
                try:
                    api_key = self.api_manager.get_next()
                    if not api_key:
                        chunk['status'] = STATUS_FAIL
                        continue
                    
                    voice_id = self.voice_combo.currentData()
                    
                    # Debug: Log voice info
                    if chunk['number'] == 1:
                        voice_name = self.voice_combo.currentText()
                        self.log(f"🎙️ Voice: {voice_name} ({voice_id})")
                    
                    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
                    headers = {
                        "xi-api-key": api_key,
                        "Content-Type": "application/json"
                    }
                    
                    # V3 check - MUST BE BEFORE PAYLOAD!
                    is_v3 = model_id == "eleven_v3"  # FIXED: eleven_v3 not eleven_v3_alpha
                    
                    # V3 CRITICAL: Only stability is supported!
                    if is_v3:
                        payload = {
                            "text": chunk['content'],
                            "model_id": model_id,
                            "voice_settings": {
                                "stability": self.stability_combo.currentData()
                                # V3 does NOT support: similarity_boost, style, use_speaker_boost
                            }
                        }
                    else:
                        # Other models: full settings
                        payload = {
                            "text": chunk['content'],
                            "model_id": model_id,
                            "voice_settings": {
                                "stability": self.stability_combo.currentData(),
                                "similarity_boost": self.similarity_spin.value(),
                                "style": self.style_spin.value(),
                                "use_speaker_boost": self.speaker_boost_check.isChecked()
                            }
                        }
                    
                    timeout = self.timeout_spin.value()
                    
                    # Get proxy if rotation mode - GIỐNG TKINTER
                    proxies = None
                    if self.proxy_rotation_radio.isChecked():
                        proxies = self.proxy_provider.get_proxy()
                        if proxies:
                            self.log(f"🌐 Using proxy for chunk {chunk['number']}")
                    
                    # Create session with proxy - GIỐNG TKINTER
                    session = self._get_session(proxies)
                    
                    self.log(f"⚡ Chunk {chunk['number']} • API ...{api_key[-4:]} • send")
                    
                    # Debug: Log payload for first chunk
                    if chunk['number'] == 1:
                        self.log(f"🔍 DEBUG Payload: model={model_id}, stability={self.stability_combo.currentData()}, is_v3={is_v3}")
                        if not is_v3:
                            self.log(f"🔍 DEBUG: similarity={self.similarity_spin.value()}, style={self.style_spin.value()}, boost={self.speaker_boost_check.isChecked()}")
                    
                    # V3 Multiple Generations Support
                    num_generations = self.v3_generations_spin.value() if is_v3 else 1
                    
                    if is_v3 and num_generations > 1:
                        self.log(f"🎭 V3: Generating {num_generations} versions for chunk {chunk['number']}")
                    
                    # Generate multiple versions for V3
                    best_audio = None
                    outdir = self._get_audio_output_dir()
                    os.makedirs(outdir, exist_ok=True)
                    
                    for gen_num in range(num_generations):
                        resp = session.post(url, json=payload, headers=headers, timeout=timeout)
                        
                        if gen_num == 0:
                            self.log(f"📊 Chunk {chunk['number']} • HTTP {resp.status_code}")
                            
                            # Log detailed error for non-200 responses
                            if resp.status_code != 200:
                                try:
                                    error_data = resp.json()
                                    error_msg = error_data.get('detail', {}).get('message', str(error_data))
                                    self.log(f"⚠️ API Error: {error_msg}")
                                except:
                                    self.log(f"⚠️ Response: {resp.text[:200]}")
                        
                        if resp.status_code == 200:
                            if num_generations > 1:
                                # Save multiple versions
                                audio_file = os.path.join(outdir, f"chunk_{chunk['number']:03d}_v{gen_num+1}.mp3")
                                with open(audio_file, 'wb') as f:
                                    f.write(resp.content)
                                
                                if gen_num == 0:
                                    best_audio = audio_file
                                
                                if is_v3:
                                    self.log(f"  ✅ Version {gen_num+1}/{num_generations}")
                            else:
                                # Single generation
                                audio_file = os.path.join(outdir, f"chunk_{chunk['number']:03d}.mp3")
                                with open(audio_file, 'wb') as f:
                                    f.write(resp.content)
                                best_audio = audio_file
                        else:
                            if gen_num == 0:
                                chunk['status'] = STATUS_FAIL
                                self.log(f"❌ Chunk {chunk['number']}: {resp.status_code}")
                                break
                    
                    if resp.status_code == 200 and best_audio:
                        chunk['audio_file'] = best_audio
                        chunk['status'] = STATUS_SUCCESS
                        success = True  # Mark success to exit retry loop
                        
                        if is_v3 and num_generations > 1:
                            self.log(f"✅ Chunk {chunk['number']} • Generated {num_generations} versions")
                        else:
                            self.log(f"✅ Chunk {chunk['number']}")
                        
                        # Update UI immediately after success
                        QTimer.singleShot(0, self.update_chunks_display)
                        QTimer.singleShot(0, self.update_progress)
                    else:
                        # Failed this attempt, will retry if retries left
                        chunk['status'] = STATUS_FAIL
                        retry_count += 1
                        
                        if retry_count < max_retries:
                            # Will retry
                            chunk['status'] = STATUS_PENDING  # Reset to pending for retry
                        else:
                            # No more retries
                            self.log(f"❌ Chunk {chunk['number']}: {resp.status_code} (after {max_retries} attempts)")
                            # Update UI immediately after final fail
                            QTimer.singleShot(0, self.update_chunks_display)
                            QTimer.singleShot(0, self.update_progress)
                        
                        # Handle proxy errors - GIỐNG TKINTER
                        if self.proxy_rotation_radio.isChecked():
                            self.proxy_provider.mark_need_refresh()
                        
                except requests.exceptions.ProxyError as e:
                    chunk['status'] = STATUS_FAIL
                    retry_count += 1
                    self.log(f"🌐 Proxy error chunk {chunk['number']}: {e}")
                    if retry_count >= max_retries:
                        QTimer.singleShot(0, self.update_chunks_display)
                        QTimer.singleShot(0, self.update_progress)
                    if self.proxy_rotation_radio.isChecked():
                        self.proxy_provider.mark_need_refresh()
                except requests.exceptions.Timeout:
                    chunk['status'] = STATUS_FAIL
                    retry_count += 1
                    self.log(f"⏰ Timeout chunk {chunk['number']}")
                    if retry_count >= max_retries:
                        QTimer.singleShot(0, self.update_chunks_display)
                        QTimer.singleShot(0, self.update_progress)
                except Exception as e:
                    chunk['status'] = STATUS_FAIL
                    retry_count += 1
                    self.log(f"❌ Chunk {chunk['number']}: {e}")
                    if retry_count >= max_retries:
                        QTimer.singleShot(0, self.update_chunks_display)
                        QTimer.singleShot(0, self.update_progress)
            
            # Final update at end of chunk processing
            QTimer.singleShot(0, self.update_chunks_display)
            QTimer.singleShot(0, self.update_progress)
            
            delay = self.delay_spin.value() / 1000.0
            if delay > 0:
                time.sleep(delay)
        
        # Worker finished - check if all done
        QTimer.singleShot(100, self.check_generation_complete)

    def check_generation_complete(self):
        """Check if generation is complete and auto-stop"""
        if not self.generation_active:
            return
        
        # Check if any chunks still in queue OR pending
        has_queue = any(c['status'] == STATUS_QUEUE for c in self.chunks)
        has_pending = any(c['status'] == STATUS_PENDING for c in self.chunks)
        
        # Count statuses for debugging
        queue_count = sum(1 for c in self.chunks if c['status'] == STATUS_QUEUE)
        pending_count = sum(1 for c in self.chunks if c['status'] == STATUS_PENDING)
        
        if not has_queue and not has_pending:
            # All workers done, stop generation
            if self.generation_active:  # Double-check to avoid race condition
                self.log(f"🎯 All chunks processed (Queue: {queue_count}, Pending: {pending_count})")
                self.stop_generation()
                self.log("✅ Generation complete!")
                
                # Show completion stats
                success = sum(1 for c in self.chunks if c['status'] == STATUS_SUCCESS)
                failed = sum(1 for c in self.chunks if c['status'] == STATUS_FAIL)
                self.log(f"📊 Success: {success} | Failed: {failed}")
                
                # Auto-merge if enabled and has successful chunks
                if self.auto_merge_check.isChecked() and success > 0:
                    self.log("🔗 Auto-merging...")
                    QTimer.singleShot(500, self.merge_audio_files)  # Delay 500ms to ensure UI updates


    def _get_session(self, proxies):
        """Create requests session with proxy - GIỐNG TKINTER"""
        try:
            concurrency = self.concurrency_spin.value()
            pool_size = max(32, concurrency * 4)
        except Exception:
            pool_size = 64
        
        sess = requests.Session()
        adapter = HTTPAdapter(
            pool_connections=pool_size, 
            pool_maxsize=pool_size,
            max_retries=Retry(total=0, connect=2, read=2, backoff_factor=0)
        )
        sess.mount('https://', adapter)
        sess.mount('http://', adapter)
        sess.headers.update({'Connection': 'keep-alive'})
        
        # Set proxy - GIỐNG TKINTER
        sess.proxies = proxies or {}
        
        return sess

    def _get_model_id(self):
        """Get model ID from combo"""
        model_name = self.model_combo.currentText()
        return {v: k for k, v in MODEL_IDS.items()}.get(model_name, "eleven_turbo_v2_5")

    def _get_audio_output_dir(self):
        """Get audio output directory - GIỐNG TKINTER"""
        # Ưu tiên project folder nếu có
        if self.project_chunks_audio_dir:
            return self.project_chunks_audio_dir
        return OUTPUT_DIR

    def _index_chunks(self):
        """Index chunks"""
        self.chunks_by_num = {c['number']: c for c in self.chunks}

    def update_chunks_display(self):
        """Update table and stats"""
        self.chunks_table.setRowCount(len(self.chunks))
        
        # Calculate stats
        total_chunks = len(self.chunks)
        total_chars = sum(chunk.get('chars', len(chunk.get('content', ''))) for chunk in self.chunks)
        
        # Update stats label
        self.chunks_stats_label.setText(f"Total: {total_chunks} chunks | {total_chars:,} chars")
        
        for i, chunk in enumerate(self.chunks):
            # Column 0: Chars
            chars = chunk.get('chars', len(chunk.get('content', '')))
            self.chunks_table.setItem(i, 0, QTableWidgetItem(str(chars)))
            
            # Column 1: Status
            status_text = status_human_text(chunk['status'])
            status_item = QTableWidgetItem(status_text)
            
            if chunk['status'] == STATUS_SUCCESS:
                status_item.setForeground(QColor("#10b981"))  # Green
            elif chunk['status'] == STATUS_FAIL:
                status_item.setForeground(QColor("#ef4444"))  # Red
            elif chunk['status'] == STATUS_PENDING:
                status_item.setForeground(QColor("#f59e0b"))  # Yellow
            elif chunk['status'] == STATUS_QUEUE:
                status_item.setForeground(QColor("#3b82f6"))  # Blue
            
            self.chunks_table.setItem(i, 1, status_item)
            
            # Column 2: Content (longer preview - 100 chars)
            preview = chunk['content'][:150] + "..." if len(chunk['content']) > 100 else chunk['content']
            self.chunks_table.setItem(i, 2, QTableWidgetItem(preview))

    def update_progress(self):
        """Update progress"""
        if not self.chunks:
            self.progress_bar.setValue(0)
            self.progress_label.setText("0/0 (0%)")
            return
        
        total = len(self.chunks)
        completed = sum(1 for c in self.chunks if c['status'] == STATUS_SUCCESS)
        percentage = int((completed / total) * 100) if total > 0 else 0
        
        self.progress_bar.setValue(percentage)
        self.progress_label.setText(f"{completed}/{total} ({percentage}%)")

    def merge_audio_files(self):
        """
        Merge audio files - ĐẢM BẢO 100% ĐÚNG THỨ TỰ
        - Validation toàn diện trước khi merge
        - Kiểm tra tính liên tục của chunk numbers
        - Merge theo thứ tự tuyệt đối
        - Lưu file cùng cấp với file txt gốc
        - LOG CHI TIẾT THỨ TỰ MERGE
        """
        try:
            # ============================================================
            # STEP 1: KIỂM TRA CƠ BẢN
            # ============================================================
            if not self.chunks:
                QMessageBox.warning(self, "Error", "No chunks available!")
                return
            
            total_chunks = len(self.chunks)
            
            # Phân loại chunks
            success_chunks = [c for c in self.chunks if c['status'] == STATUS_SUCCESS]
            failed_chunks = [c for c in self.chunks if c['status'] == STATUS_FAIL]
            pending_chunks = [c for c in self.chunks if c['status'] in [STATUS_QUEUE, STATUS_PENDING]]
            
            success_count = len(success_chunks)
            failed_count = len(failed_chunks)
            pending_count = len(pending_chunks)
            
            self.log("=" * 60)
            self.log("🔍 MERGE VALIDATION CHECK")
            self.log(f"   Total Chunks: {total_chunks}")
            self.log(f"   ✅ Success: {success_count}")
            self.log(f"   ❌ Failed: {failed_count}")
            self.log(f"   🟨 Pending: {pending_count}")
            self.log("=" * 60)
            
            # CRITICAL: Phải 100% success
            if success_count != total_chunks:
                error_msg = "❌ CANNOT MERGE - NOT 100% SUCCESSFUL!\n\n"
                error_msg += f"Total: {total_chunks}\n"
                error_msg += f"✅ Success: {success_count}\n"
                error_msg += f"❌ Failed: {failed_count}\n"
                error_msg += f"🟨 Pending: {pending_count}\n\n"
                
                if failed_count > 0:
                    error_msg += "Failed chunks: "
                    error_msg += ", ".join([f"#{c['number']}" for c in failed_chunks[:10]])
                    if failed_count > 10:
                        error_msg += f" ... and {failed_count - 10} more"
                    error_msg += "\n\n"
                
                if pending_count > 0:
                    error_msg += "Pending chunks: "
                    error_msg += ", ".join([f"#{c['number']}" for c in pending_chunks[:10]])
                    if pending_count > 10:
                        error_msg += f" ... and {pending_count - 10} more"
                    error_msg += "\n\n"
                
                error_msg += "⚠️ Please generate all chunks successfully before merging!"
                
                self.log("❌ Merge aborted - Not 100% success")
                QMessageBox.critical(self, "Merge Failed", error_msg)
                return
            
            self.log("✅ Validation passed - All chunks successful!")
            
            # ============================================================
            # STEP 2: SẮP XẾP VÀ KIỂM TRA CHUNKS
            # ============================================================
            self.log("🔍 Validating chunk sequence...")
            
            # Sắp xếp chunks theo số thứ tự
            sorted_chunks = sorted(self.chunks, key=lambda x: x['number'])
            
            # LOG THỨ TỰ SAU KHI SORT
            chunk_sequence = [c['number'] for c in sorted_chunks]
            sequence_str = "-".join(map(str, chunk_sequence))
            self.log(f"📊 Chunk order after sorting: {sequence_str}")
            
            # Kiểm tra tính liên tục: phải là 1, 2, 3, ..., n
            expected_sequence = list(range(1, total_chunks + 1))
            actual_sequence = [c['number'] for c in sorted_chunks]
            
            if actual_sequence != expected_sequence:
                error_msg = "❌ CHUNK SEQUENCE ERROR!\n\n"
                error_msg += "Chunks must be numbered 1, 2, 3, ... sequentially.\n\n"
                error_msg += f"Expected: {expected_sequence}\n"
                error_msg += f"Actual:   {actual_sequence}\n\n"
                
                # Tìm chunks bị thiếu
                missing = set(expected_sequence) - set(actual_sequence)
                if missing:
                    error_msg += f"Missing: {sorted(missing)}\n"
                
                # Tìm chunks bị duplicate
                duplicates = [x for x in actual_sequence if actual_sequence.count(x) > 1]
                if duplicates:
                    error_msg += f"Duplicates: {set(duplicates)}\n"
                
                self.log("❌ Merge aborted - Invalid sequence")
                QMessageBox.critical(self, "Merge Failed", error_msg)
                return
            
            self.log(f"✅ Chunk sequence validated: 1 → {total_chunks}")
            
            # ============================================================
            # STEP 3: KIỂM TRA AUDIO FILES
            # ============================================================
            self.log("🔍 Validating audio files...")
            
            audio_files_ordered = []
            errors = []
            
            for chunk in sorted_chunks:
                chunk_num = chunk['number']
                audio_path = chunk.get('audio_file')
                
                # Check 1: Audio path exists
                if not audio_path:
                    errors.append(f"Chunk #{chunk_num}: No audio file path")
                    continue
                
                # Check 2: File exists on disk
                if not os.path.exists(audio_path):
                    errors.append(f"Chunk #{chunk_num}: File not found\n  Path: {audio_path}")
                    continue
                
                # Check 3: File is not empty
                file_size = os.path.getsize(audio_path)
                if file_size == 0:
                    errors.append(f"Chunk #{chunk_num}: Empty file (0 bytes)\n  Path: {audio_path}")
                    continue
                
                # Check 4: File is readable
                try:
                    with open(audio_path, 'rb') as f:
                        f.read(1)  # Try reading 1 byte
                except Exception as e:
                    errors.append(f"Chunk #{chunk_num}: Cannot read file\n  Error: {e}")
                    continue
                
                # All checks passed
                audio_files_ordered.append({
                    'number': chunk_num,
                    'path': audio_path,
                    'size': file_size,
                    'name': os.path.basename(audio_path)
                })
                
                self.log(f"   ✓ Chunk #{chunk_num:03d}: {os.path.basename(audio_path)} ({file_size:,} bytes)")
            
            # Check for errors
            if errors:
                error_msg = "❌ AUDIO FILE VALIDATION FAILED!\n\n"
                error_msg += "\n".join(errors)
                error_msg += "\n\n⚠️ All chunks must have valid audio files!"
                
                self.log("❌ Merge aborted - Audio file errors")
                QMessageBox.critical(self, "Merge Failed", error_msg)
                return
            
            # Verify count
            if len(audio_files_ordered) != total_chunks:
                error_msg = f"❌ FILE COUNT MISMATCH!\n\n"
                error_msg += f"Expected: {total_chunks} files\n"
                error_msg += f"Found: {len(audio_files_ordered)} valid files\n"
                
                self.log("❌ Merge aborted - File count mismatch")
                QMessageBox.critical(self, "Merge Failed", error_msg)
                return
            
            self.log(f"✅ All {len(audio_files_ordered)} audio files validated")
            
            # ============================================================
            # STEP 4: XÁC ĐỊNH OUTPUT PATH (3 PRIORITY LEVELS)
            # ============================================================
            self.log("📁 Determining output path...")
            
            output_dir = None
            output_name = None
            
            # PRIORITY 1: Auto workflow voice output folder (HIGHEST)
            if self.project_chunks_audio_dir:
                output_dir = self.project_chunks_audio_dir
                # Get script name from script_path if available
                if hasattr(self, 'project_text_path') and self.project_text_path:
                    output_name = os.path.splitext(os.path.basename(self.project_text_path))[0]
                elif hasattr(self, 'script_path') and self.script_path:
                    output_name = os.path.splitext(os.path.basename(self.script_path))[0]
                else:
                    # Use script name from script input if available
                    script_text = self.script_input.toPlainText().strip()
                    if script_text:
                        # Try to extract name from first line or use default
                        first_line = script_text.split('\n')[0][:50].strip()
                        output_name = re.sub(r'[^\w\s-]', '', first_line).strip().replace(' ', '_')
                        if not output_name:
                            output_name = "script"
                if not output_name:
                    output_name = "merged_audio"
                
                merged_file = os.path.join(output_dir, f"{output_name}.mp3")
                self.log(f"   ✅ Using auto workflow voice folder: {output_dir}")
                self.log(f"   📄 Output file: {merged_file}")
            
            # PRIORITY 2: Same folder as TXT file (legacy)
            elif self.project_text_path and os.path.exists(self.project_text_path):
                output_dir = os.path.dirname(self.project_text_path)
                output_name = os.path.splitext(os.path.basename(self.project_text_path))[0]
                merged_file = os.path.join(output_dir, f"{output_name}.mp3")
                
                self.log(f"   📁 Using TXT file folder: {output_dir}")
                self.log(f"   📄 Output file: {merged_file}")
            
            # PRIORITY 3: Fallback to default output folder
            else:
                output_dir = OUTPUT_DIR
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_name = f"merged_{timestamp}"
                merged_file = os.path.join(OUTPUT_DIR, f"{output_name}.mp3")
                self.log(f"   ⚠️ No project/TXT path - using fallback: {OUTPUT_DIR}")
                self.log(f"   📄 Output file: {merged_file}")
            
            # Ensure output directory exists
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                self.log(f"   ✅ Created output directory: {output_dir}")
            
            # ============================================================
            # STEP 5: MERGE FILES THEO THỨ TỰ TUYỆT ĐỐI
            # ============================================================
            self.log("=" * 60)
            self.log("🔗 STARTING MERGE PROCESS")
            self.log("=" * 60)
            
            # LOG THỨ TỰ MERGE NGAY TRƯỚC KHI BẮT ĐẦU
            merge_order = [f['number'] for f in audio_files_ordered]
            merge_order_str = "-".join(map(str, merge_order))
            self.log(f"📋 MERGE ORDER: {merge_order_str}")
            self.log(f"📋 Total files to merge: {len(audio_files_ordered)}")
            
            # Xóa file cũ nếu tồn tại
            if os.path.exists(merged_file):
                try:
                    os.remove(merged_file)
                    self.log(f"   🗑️ Removed existing file: {os.path.basename(merged_file)}")
                except Exception as e:
                    error_msg = f"Cannot remove existing file:\n{merged_file}\n\nError: {e}"
                    QMessageBox.critical(self, "Merge Failed", error_msg)
                    return
            
            # Merge process
            total_bytes_written = 0
            chunks_merged = 0
            merge_log_parts = []  # Để build string "1-2-3-4-5-..."
            
            try:
                with open(merged_file, 'wb') as outfile:
                    for i, audio_info in enumerate(audio_files_ordered, 1):
                        chunk_num = audio_info['number']
                        audio_path = audio_info['path']
                        
                        # Add to merge log
                        merge_log_parts.append(str(chunk_num))
                        
                        # Log progress mỗi chunk
                        progress_pct = int((i / total_chunks) * 100)
                        current_merge_str = "-".join(merge_log_parts)
                        self.log(f"   [{progress_pct:3d}%] Merging #{chunk_num:03d} → Current order: {current_merge_str}")
                        
                        # Read and write
                        try:
                            with open(audio_path, 'rb') as infile:
                                audio_data = infile.read()
                                
                                # Verify data
                                if len(audio_data) == 0:
                                    raise Exception(f"File became empty during read: {audio_path}")
                                
                                # Write to output
                                bytes_written = outfile.write(audio_data)
                                total_bytes_written += bytes_written
                                chunks_merged += 1
                                
                                # Verify write
                                if bytes_written != len(audio_data):
                                    raise Exception(f"Write incomplete: expected {len(audio_data)}, wrote {bytes_written}")
                        
                        except Exception as e:
                            error_msg = f"Failed to merge chunk #{chunk_num}:\n{audio_path}\n\nError: {e}"
                            self.log(f"❌ Merge failed at chunk #{chunk_num}: {e}")
                            QMessageBox.critical(self, "Merge Failed", error_msg)
                            
                            # Cleanup incomplete file
                            try:
                                outfile.close()
                                os.remove(merged_file)
                            except:
                                pass
                            return
            
            except Exception as e:
                error_msg = f"Merge process failed:\n\n{e}"
                self.log(f"❌ Merge failed: {e}")
                QMessageBox.critical(self, "Merge Failed", error_msg)
                return
            
            # LOG FINAL MERGE ORDER
            final_merge_str = "-".join(merge_log_parts)
            self.log("=" * 60)
            self.log(f"✅ MERGE SEQUENCE COMPLETED: {final_merge_str}")
            self.log("=" * 60)
            
            # ============================================================
            # STEP 6: VERIFY OUTPUT FILE
            # ============================================================
            self.log("🔍 Verifying merged file...")
            
            if not os.path.exists(merged_file):
                error_msg = "Output file was not created!"
                self.log("❌ Merge failed - No output file")
                QMessageBox.critical(self, "Merge Failed", error_msg)
                return
            
            merged_size = os.path.getsize(merged_file)
            
            if merged_size == 0:
                error_msg = "Output file is empty (0 bytes)!"
                self.log("❌ Merge failed - Empty output")
                QMessageBox.critical(self, "Merge Failed", error_msg)
                return
            
            if chunks_merged != total_chunks:
                error_msg = f"Merge incomplete!\n\n"
                error_msg += f"Expected: {total_chunks} chunks\n"
                error_msg += f"Merged: {chunks_merged} chunks"
                self.log(f"❌ Merge incomplete: {chunks_merged}/{total_chunks}")
                QMessageBox.critical(self, "Merge Failed", error_msg)
                return
            
            # Calculate expected vs actual size
            total_input_size = sum(f['size'] for f in audio_files_ordered)
            size_diff = abs(merged_size - total_input_size)
            size_diff_pct = (size_diff / total_input_size * 100) if total_input_size > 0 else 0
            
            self.log(f"   Input total: {total_input_size:,} bytes")
            self.log(f"   Output size: {merged_size:,} bytes")
            self.log(f"   Difference: {size_diff:,} bytes ({size_diff_pct:.2f}%)")
            
            # Warning if size difference is too large
            if size_diff_pct > 5:
                self.log(f"   ⚠️ Size difference exceeds 5% - verify output quality!")
            
            # ============================================================
            # STEP 7: SUCCESS REPORT
            # ============================================================
            self.log("=" * 60)
            self.log("✅ MERGE COMPLETED SUCCESSFULLY!")
            self.log(f"   Merged Order: {final_merge_str}")
            self.log(f"   Total Chunks: {total_chunks}")
            self.log(f"   Output Size: {merged_size:,} bytes ({merged_size / 1024 / 1024:.2f} MB)")
            self.log(f"   Output File: {os.path.basename(merged_file)}")
            self.log(f"   Full Path: {merged_file}")
            self.log("=" * 60)
            
            # ============================================================
            # STEP 8: CLEANUP (optional)
            # ============================================================
            if not self.keep_chunks_check.isChecked():
                self.log("🗑️ Cleaning up chunk files...")
                deleted_count = 0
                failed_deletions = []
                
                for audio_info in audio_files_ordered:
                    try:
                        os.remove(audio_info['path'])
                        deleted_count += 1
                    except Exception as e:
                        failed_deletions.append(f"{audio_info['name']}: {e}")
                
                self.log(f"   Deleted: {deleted_count}/{len(audio_files_ordered)} files")
                
                if failed_deletions:
                    self.log("   ⚠️ Some files could not be deleted:")
                    for fail in failed_deletions[:5]:  # Show first 5
                        self.log(f"      - {fail}")
                    if len(failed_deletions) > 5:
                        self.log(f"      ... and {len(failed_deletions) - 5} more")
            
            # ============================================================
            # STEP 9: OPEN FILE (optional)
            # ============================================================
            if self.open_after_merge_check.isChecked():
                self.log("📂 Opening merged file...")
                self.open_file(merged_file)
            
            # ============================================================
            # STEP 10: SUCCESS MESSAGE
            # ============================================================
            success_msg = "✅ MERGE SUCCESSFUL!\n\n"
            success_msg += f"📁 File: {os.path.basename(merged_file)}\n\n"
            success_msg += f"📊 Details:\n"
            success_msg += f"   • Chunks merged: {total_chunks}\n"
            success_msg += f"   • Merge order: {final_merge_str}\n"
            success_msg += f"   • Total size: {merged_size:,} bytes ({merged_size / 1024 / 1024:.2f} MB)\n"
            success_msg += f"   • Sequence: 1 → {total_chunks} (validated)\n\n"
            success_msg += f"📂 Location:\n{merged_file}"
            
            QMessageBox.information(self, "Merge Complete", success_msg)
            
        except Exception as e:
            error_msg = f"❌ UNEXPECTED ERROR!\n\n{str(e)}\n\n"
            error_msg += "Please check the log for details."
            self.log(f"❌ Merge error: {e}")
            import traceback
            self.log(traceback.format_exc())
            QMessageBox.critical(self, "Merge Error", error_msg)
        
    def _load_settings(self):
        """Load settings"""
        if os.path.exists(API_SETTINGS_FILE):
            try:
                with open(API_SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    s = json.load(f)
                    self.chunk_size_spin.setValue(s.get('chunk_size', 800))
                    self.concurrency_spin.setValue(s.get('concurrency', 4))
                    self.delay_spin.setValue(s.get('gen_delay_ms', 0))
                    self.max_retries_spin.setValue(s.get('max_retries', 3))
                    self.timeout_spin.setValue(s.get('timeout_s', 30))
                    self.min_credit_spin.setValue(s.get('credit_threshold', 1000))
                    
                    # Load proxy mode - GIỐNG TKINTER
                    proxy_mode = s.get('proxy_mode', 'no_proxy')
                    if proxy_mode == 'rotation':
                        self.proxy_rotation_radio.setChecked(True)
                    else:
                        self.proxy_none_radio.setChecked(True)
                    
                self.log("API settings loaded")
            except Exception as e:
                self.log(f"Error loading settings: {e}")
        else:
            self.log("API settings file not found")

    def save_all_settings(self):
        """Save settings"""
        try:
            settings = {
                'chunk_size': self.chunk_size_spin.value(),
                'concurrency': self.concurrency_spin.value(),
                'gen_delay_ms': self.delay_spin.value(),
                'max_retries': self.max_retries_spin.value(),
                'timeout_s': self.timeout_spin.value(),
                'credit_threshold': self.min_credit_spin.value(),
                'multithread': self.enable_multithread_check.isChecked(),
                'open_after_merge': self.open_after_merge_check.isChecked(),
                'keep_chunks_after_merge': self.keep_chunks_check.isChecked(),
                'proxy_mode': 'rotation' if self.proxy_rotation_radio.isChecked() else 'no_proxy'
            }
            
            with open(API_SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            
            voice_settings = {
                'model': self.model_combo.currentText(),
                'voice': self.voice_combo.currentText(),
                'speed': self.speed_spin.value(),
                'stability': self.stability_combo.currentData(),
                'similarity': self.similarity_spin.value(),
                'style': self.style_spin.value(),
                'speaker_boost': self.speaker_boost_check.isChecked(),
                'language_code': self.language_combo.currentText()
            }
            
            with open(VOICE_SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(voice_settings, f, indent=2)
            
            self.save_proxy_links()
            
            self.log("💾 All settings saved")
            QMessageBox.information(self, "Success", "Settings saved")
        except Exception as e:
            self.log(f"❌ Error: {e}")

    # ================================================================================
    # FILE SYSTEM
    # ================================================================================
    
    def open_output_folder(self):
        """Open output folder"""
        if self.project_chunks_audio_dir:
            self.open_folder(self.project_chunks_audio_dir)
        else:
            self.open_folder(OUTPUT_DIR)

    def open_settings_folder(self):
        """Open settings folder"""
        self.open_folder(SETTINGS_DIR)

    def open_folder(self, folder_path):
        """Open folder"""
        try:
            os.makedirs(folder_path, exist_ok=True)
            if os.name == 'nt':
                os.startfile(folder_path)
            elif platform.system() == 'Darwin':
                subprocess.call(['open', folder_path])
            else:
                subprocess.call(['xdg-open', folder_path])
            self.log(f"📂 Opened: {folder_path}")
        except Exception as e:
            self.log(f"❌ Error: {e}")

    def open_file(self, file_path):
        """Open file"""
        try:
            if os.name == 'nt':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':
                subprocess.call(['open', file_path])
            else:
                subprocess.call(['xdg-open', file_path])
        except Exception as e:
            self.log(f"❌ Error: {e}")

    # ================================================================================
    # LOGGING
    # ================================================================================
    
    def log(self, msg: str):
        """Log message"""
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.log_queue.put_nowait(f"[{timestamp}] {msg}")
        except Exception:
            pass
        try:
            print(msg)
        except Exception:
            pass

    def process_logs(self):
        """Process logs"""
        try:
            while True:
                try:
                    line = self.log_queue.get_nowait()
                except queue.Empty:
                    break
                self.log_area.append(line)
        except Exception:
            pass

    def save_logs(self):
        """Save logs"""
        try:
            text = self.log_area.toPlainText()
            if not text.strip():
                return
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = os.path.join(OUTPUT_DIR, f"logs_{timestamp}.txt")
            
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            self.log(f"💾 Saved: {os.path.basename(log_file)}")
            
        except Exception as e:
            self.log(f"❌ Error: {e}")

    def clear_logs(self):
        """Clear logs"""
        self.log_area.clear()
        self.log("🧹 Cleared")

    def toggle_log_wrap(self):
        """Toggle wrap"""
        if self.wrap_log_check.isChecked():
            self.log_area.setLineWrapMode(QTextEdit.WidgetWidth)
        else:
            self.log_area.setLineWrapMode(QTextEdit.NoWrap)
    
    def load_proxy_from_server(self):
        """Load proxy keys from Admin Panel server"""
        if not self.api_client or not self.api_client.is_authenticated():
            return  # Silently skip if not connected
        
        try:
            proxy_data = self.api_client.get_proxy_keys()
            
            if not proxy_data:
                self.log("⚠️ No proxy keys assigned")
                return
            
            # Load proxy keys into memory (as list of strings)
            self.proxy_keys = [p['proxy_key'] for p in proxy_data if p.get('proxy_key')]
            
            # Store mapping key -> id for reporting
            self.proxy_keys_with_ids = {
                p['proxy_key']: p['id'] 
                for p in proxy_data 
                if p.get('proxy_key') and p.get('id')
            }
            
            # Update proxy provider with new api_client and keys mapping
            if self.proxy_provider:
                self.proxy_provider._api_client = self.api_client
                self.proxy_provider._proxy_keys_with_ids = getattr(self, 'proxy_keys_with_ids', {})
            
            if self.proxy_keys:
                self.log(f"✅ Loaded {len(self.proxy_keys)} proxy keys from server")
                # Update stats label if exists
                if hasattr(self, 'proxy_stats_label'):
                    self.proxy_stats_label.setText(f"Links: {len(self.proxy_keys)}    OK: 0    Fail: 0")
            else:
                self.log("⚠️ No valid proxy keys")
                
        except Exception as e:
            self.log(f"⚠️ Failed to load proxy keys: {e}")
    
    def load_keys_from_server(self):
        """Load ElevenLabs API keys from Admin Panel server"""
        if not self.api_client or not self.api_client.is_authenticated():
            self.log("❌ Not connected to server. Please login first!")
            # Skip popup during silent startup
            if not os.environ.get("WF_SILENT_STARTUP"):
                QMessageBox.warning(
                    self,
                    "Not Connected",
                    "Please login to Admin Panel first!\n\n"
                    "Go to Projects tab → 🔐 Connect to Admin Panel"
                )
            return
        
        self.log("☁️ Loading ElevenLabs keys from server...")
        
        try:
            keys_data = self.api_client.get_elevenlabs_keys()
            
            if not keys_data:
                self.log("⚠️ No keys found on server or failed to load")
                # Skip popup during silent startup
                if not os.environ.get("WF_SILENT_STARTUP"):
                    QMessageBox.information(
                        self,
                        "No Keys Found",
                        "No ElevenLabs API keys assigned to your account.\n\n"
                        "Please ask admin to assign keys to you."
                    )
                return
            
            # Extract API keys from server data
            api_keys = [item.get('api_key', '').strip() for item in keys_data if item.get('api_key')]
            
            if not api_keys:
                self.log("⚠️ No valid API keys extracted from server data")
                return
            
            # Load keys directly into api_manager (in memory, not file)
            with self.api_manager._lock:
                self.api_manager._keys = api_keys
                self.api_manager._idx = 0
            
            key_count = len(api_keys)
            self.log(f"✅ Loaded {key_count} keys from server (in memory only)")
            
            # Skip popup during silent startup
            if not os.environ.get("WF_SILENT_STARTUP"):
                QMessageBox.information(
                    self,
                    "Success",
                    f"✅ Loaded {key_count} ElevenLabs API keys from server!\n\n"
                    f"Keys are ready to use.\n"
                    f"🔒 Keys are stored securely (not visible to users)"
                )
            
        except Exception as e:
            self.log(f"❌ Error loading keys from server: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load keys from server:\n\n{str(e)}"
            )


def main():
    app = QApplication(sys.argv)
    
    # ============================================================
    # INIT FILES FIRST - TẠO FILE TỰ ĐỘNG TRƯỚC KHI CHECK LICENSE
    # ============================================================
    print("Initializing directories and files...")
    ensure_directories_and_files()
    
    # ============================================================
    # CHECK LICENSE SAU KHI INIT
    # ============================================================
    valid, info = check_license()
    
    if not valid:
        # Hiển thị dialog để nhập license
        dialog = LicenseDialog(info)
        result = dialog.exec()
        
        # Nếu user không activate thành công
        if result != QDialog.Accepted or not dialog.license_valid:
            sys.exit(1)
        
        # Kiểm tra lại license sau khi activate
        valid, info = check_license()
        if not valid:
            QMessageBox.critical(None, "Error", "License verification failed after activation!")
            sys.exit(1)
    
    # License hợp lệ - mở app bình thường
    window = ElevenLabsGUI()
    
    # Hiển thị thông tin license trong log
    if info.get("valid"):
        window.log("=" * 60)
        window.log("✅ LICENSE VERIFIED")
        window.log(f"   Owner: {info.get('owner', 'N/A')}")
        window.log(f"   Expires: {info.get('exp_date', 'N/A')}")
        window.log(f"   Days Left: {info.get('days_left', 'N/A')}")
        window.log("=" * 60)
    
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
