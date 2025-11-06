import os
import json
import time
import base64
import threading
from pathlib import Path
from typing import List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QCheckBox, QSpinBox, QProgressBar,
    QScrollArea, QFrame, QLineEdit, QFileDialog, QMessageBox, QComboBox,
    QDialog, QGridLayout, QGraphicsDropShadowEffect, QSizePolicy, QTabWidget,
    QGroupBox, QSlider, QToolButton, QMenu, QButtonGroup, QRadioButton
)
from PySide6.QtCore import Qt, Signal, QThread, QSize, QPropertyAnimation, QEasingCurve, QPoint, QRect, QTimer
from PySide6.QtGui import QPixmap, QPalette, QColor, QFont, QMouseEvent, QPainter, QPen, QCursor, QIcon

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
except Exception:
    print("❗ Install cryptography: pip install cryptography")

try:
    from google import genai
    from google.genai import types
    from google.genai.types import GenerateContentConfig, Modality
except Exception:
    print("❗ Install google-genai: pip install -U google-genai")
    raise

try:
    import requests
except Exception:
    print("❗ Install requests: pip install requests")
    requests = None

# ==================== CONSTANTS ====================
APP_TITLE = "AI Image Generator Pro"
APP_VERSION = "v4.0"
APP_DIR = Path(__file__).parent

SETTINGS_DIR = Path(r"C:\genImage\Settings")
SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
SETTINGS_PATH = SETTINGS_DIR / "premium_settings.json"

DEFAULT_OUTPUT_DIR = APP_DIR / "outputs"
DEFAULT_OUTPUT_DIR.mkdir(exist_ok=True)

# Models
IMAGEN4_STD = "imagen-4.0-generate-001"
IMAGEN4_FAST = "imagen-4.0-fast-generate-001"
IMAGEN4_ULTRA = "imagen-4.0-ultra-generate-001"
GEMINI_FLASH_IMAGE = "gemini-2.5-flash-image"
SUPPORTED_MODELS = [IMAGEN4_ULTRA, IMAGEN4_STD, GEMINI_FLASH_IMAGE]

AR_IMAGEN = ["1:1", "3:4", "4:3", "9:16", "16:9"]
AR_GEMINI = ["1:1", "3:4", "4:3", "9:16", "16:9", "2:3", "3:2", "4:5", "5:4", "21:9"]
IMAGEN_SIZES = ["1K", "2K"]
PERSON_GEN = ["dont_allow", "allow_adult", "allow_all"]

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

# ==================== MODERN THEME - ORANGE EDITION ====================
class Theme:
    # Background - Match Voice App
    BG_PRIMARY = "#f8f9fa"
    BG_SECONDARY = "#ffffff"
    BG_TERTIARY = "#fff7f0"  # Light orange tint
    
    # Text
    TEXT_PRIMARY = "#11224E"  # Navy blue like Voice app
    TEXT_SECONDARY = "#6b7280"
    TEXT_MUTED = "#9ca3af"
    TEXT_INVERSE = "#ffffff"
    
    # Brand Colors - ORANGE THEME
    PRIMARY = "#F87B1B"  # Main orange
    PRIMARY_HOVER = "#FF8C2E"
    PRIMARY_LIGHT = "#FFE8D6"
    PRIMARY_DARK = "#d97706"
    
    SECONDARY = "#11224E"  # Navy blue
    SECONDARY_HOVER = "#1A3366"
    SECONDARY_LIGHT = "#e2e8f0"
    
    SUCCESS = "#10b981"
    SUCCESS_HOVER = "#059669"
    SUCCESS_LIGHT = "#d1fae5"
    
    WARNING = "#f59e0b"
    WARNING_HOVER = "#d97706"
    WARNING_LIGHT = "#fef3c7"
    
    DANGER = "#ef4444"
    DANGER_HOVER = "#dc2626"
    DANGER_LIGHT = "#fee2e2"
    
    INFO = "#0ea5e9"
    INFO_HOVER = "#0284c7"
    INFO_LIGHT = "#dbeafe"
    
    PURPLE = "#8b5cf6"
    PURPLE_HOVER = "#7c3aed"
    PURPLE_LIGHT = "#ede9fe"
    
    # Borders
    BORDER = "#d1d9e6"  # Match Voice app
    BORDER_STRONG = "#94a3b8"
    
    # Shadows
    SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
    SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1)"
    SHADOW_XL = "0 20px 25px -5px rgba(0, 0, 0, 0.1)"

# ==================== UTILITIES ====================
def get_machine_guid() -> str:
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as k:
            v, _ = winreg.QueryValueEx(k, "MachineGuid")
        return str(v).strip()
    except Exception:
        return ""

class KeyRotator:
    def __init__(self, keys: List[str]):
        self.keys = [k.strip() for k in keys if k.strip()]
        if not self.keys:
            raise ValueError("No API keys loaded.")
        self.lock = threading.Lock()
        self.idx = 0
    
    def current(self) -> str:
        with self.lock:
            return self.keys[self.idx % len(self.keys)]
    
    def next(self) -> str:
        with self.lock:
            self.idx = (self.idx + 1) % len(self.keys)
            return self.keys[self.idx]
    
    def __len__(self): 
        return len(self.keys)

def is_rate_or_quota_error(msg: str) -> bool:
    msg = (msg or "").lower()
    return any(code in msg for code in ("429", "quota", "permission", "403", "rate", "resource_exhausted"))

def crop_to_16_9(pixmap: QPixmap, target_width: int, target_height: int) -> QPixmap:
    """
    Crop/scale pixmap to fill exact 16:9 aspect ratio without letterboxing.
    Uses center crop if source aspect doesn't match 16:9.
    """
    if pixmap.isNull():
        return pixmap
    
    src_w = pixmap.width()
    src_h = pixmap.height()
    src_ratio = src_w / src_h if src_h > 0 else 1
    target_ratio = 16 / 9
    
    # If source is wider than 16:9, crop width (keep height)
    if src_ratio > target_ratio:
        new_w = int(src_h * target_ratio)
        new_h = src_h
        x_offset = (src_w - new_w) // 2
        y_offset = 0
    # If source is taller than 16:9, crop height (keep width)
    else:
        new_w = src_w
        new_h = int(src_w / target_ratio)
        x_offset = 0
        y_offset = (src_h - new_h) // 2
    
    # Crop to 16:9
    cropped = pixmap.copy(x_offset, y_offset, new_w, new_h)
    
    # Scale to target size with smooth transformation
    return cropped.scaled(target_width, target_height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

# ==================== GROQ AI SCRIPT ANALYSIS ====================
def analyze_script_with_groq(script: str, num_parts: int, groq_api_key: str) -> List[str]:
    """
    Gửi script đến Groq API để phân tích và tạo prompts theo quy tắc.
    Returns: List các prompts đã được tạo ra.
    """
    if not requests:
        raise Exception("requests library not installed")
    
    if not groq_api_key or not groq_api_key.strip():
        raise Exception("Groq API key is empty")
    
    # System prompt với quy tắc chi tiết
    system_prompt = """Bạn là GPT chuyên xử lý các kịch bản dài bằng tiếng Anh để phục vụ sản xuất video cảm xúc dành cho khán giả YouTube tại Mỹ.

Quy trình tự động xử lý như sau:

1. Đọc hiểu kịch bản (Simple Woman - Nữ chính hiền lành, Nam phản diện tức giận)
2. Chia kịch bản thành {x} phần như yêu cầu
4. Prompt cần phải có sự đồng nhất chi tiết về trang phục, màu da và ngoại hình của các nhân vật trong toàn bộ các phân cảnh (nội dung được giữ nguyên từ prompt đầu tiên, KHÔNG DÙNG cụm "same outfit")
5. Các nhân vật trong phân cảnh phải nhìn, tương tác với nhau
6. Mô tả ngoại hình nhân vật (màu tóc, màu da, quần áo...) phải đặt trong dấu ngoặc đơn () theo đúng format chuẩn
7. Dưới mỗi phân cảnh, có:
   - Tóm tắt ngắn bằng tiếng Việt
   - Một prompt vẽ ảnh phù hợp, đồng nhất trang phục và đặc điểm nhân vật chính/phụ giữa các phân cảnh

NGUYÊN TẮC VIẾT PROMPT (ÁP DỤNG CHO MỌI PROMPT):
- Ngôn ngữ: tiếng Anh
- Style mặc định: ultra-realistic photo, 16:9
- Luôn có 2 nhân vật chính (nam & nữ) HOẶC (nữ & nữ): 1 chính diện và 1 phản diện
- Nhân vật chính: điềm tĩnh, nội tâm sâu sắc
- Phản diện: cảm xúc mạnh, khó kiểm soát (chửi, la hét, chỉ tay, khiêu khích...)
- Có 2-5+ nhân vật nền góp phần tăng cảm xúc (cười nhạo, khinh thường...)
- Ánh sáng tươi sáng, rõ ràng, màu sắc tương phản
- Nhân vật: người Mỹ hoặc châu Âu, màu tóc KHÔNG MÔ TÃ MÀU ĐEN
- Các nhân vật trong prompt phải tương tác với nhau và đặc biệt KHÔNG NHÌN THẲNG VÀO MÀNG HÌNH hay phá vỡ bức tường thứ 4
- Một bản dịch của prompt bằng tiếng Việt ở bên dưới mỗi prompt, KHÔNG ĐỂ TRONG CODE BOX
- Khi chia thành nhiều prompt (n hình), GPT KHÔNG BAO GIỜ được dùng từ "same outfit" hoặc "same look". Thay vào đó, phải giữ nguyên phần mô tả ngoại hình từ prompt đầu tiên (gồm màu da, quần áo, tóc...) và copy y hệt vào các prompt sau
- Mô tả về ngoại hình của nhân vật trong prompt phải được đặt trong ( ), nếu mô tả không phải ngoại hình sẽ phải nằm ngoài ( )
- Những từ KHÔNG ĐƯỢC xuất hiện trong prompt: revealing cleavage, showing cleavage, emerald green eyes

FORMAT OUTPUT:
Chỉ trả về các prompt tiếng Anh, mỗi prompt trên một dòng. KHÔNG CẦN tiêu đề "Phân cảnh X" hay bản dịch tiếng Việt. Chỉ cần prompt thuần tiếng Anh, mỗi prompt một dòng, ngăn cách bằng dấu xuống dòng đôi.

VÍ DỤ FORMAT OUTPUT:
Ultra-realistic photo, 16:9. A woman (fair skin, wearing elegant navy blue dress, blonde wavy hair) standing confidently in a bright modern living room, looking at a man (tan skin, wearing casual grey sweater, brown hair) who is angrily pointing at her with raised voice. 3 neighbors in the background (varied appearances) watching with judgmental expressions, some whispering. Natural daylight streaming through large windows, contemporary furniture, high contrast lighting.

Ultra-realistic photo, 16:9. A woman (fair skin, wearing elegant navy blue dress, blonde wavy hair) calmly walking away while a man (tan skin, wearing casual grey sweater, brown hair) continues shouting behind her with clenched fists. 4 onlookers (varied appearances) in background, some shaking heads, others recording with phones. Bright outdoor setting, modern apartment courtyard, sharp focus on main characters."""

    user_prompt = f"Hãy phân tích kịch bản sau và chia thành {num_parts} phần, tạo prompt cho mỗi phần theo đúng quy tắc trên:\n\n{script}"
    
    # Call Groq API
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",  # hoặc model khác của Groq
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"]["content"].strip()
        
        # DEBUG: Print raw response
        print(f"[GROQ AI RAW RESPONSE]:\n{content}\n{'='*80}")
        
        # Parse prompts - split by double newline OR single newline if no double
        if "\n\n" in content:
            prompts = [p.strip() for p in content.split("\n\n") if p.strip()]
        else:
            prompts = [p.strip() for p in content.split("\n") if p.strip()]
        
        print(f"[PARSED PROMPTS COUNT]: {len(prompts)}")
        
        # Filter out ONLY obvious headers/metadata
        final_prompts = []
        for i, p in enumerate(prompts):
            # Skip if it's a title line like "Phân cảnh 1:", "Scene 1:", "Part 1:"
            if any(p.startswith(x) for x in ["Phân cảnh", "Scene", "Part ", "Prompt ", "**"]):
                print(f"[SKIP HEADER {i}]: {p[:50]}...")
                continue
            
            # Skip if it's too short (likely not a full prompt)
            if len(p) < 30:
                print(f"[SKIP SHORT {i}]: {p}")
                continue
            
            # Accept if it looks like a valid prompt (less strict)
            # Just check if it's not Vietnamese translation or metadata
            if not any(keyword in p.lower() for keyword in ["tóm tắt:", "dịch:", "bản dịch:"]):
                print(f"[ACCEPT {i}]: {p[:80]}...")
                final_prompts.append(p)
            else:
                print(f"[SKIP TRANSLATION {i}]: {p[:50]}...")
        
        print(f"[FINAL PROMPTS COUNT]: {len(final_prompts)}")
        
        # Return final_prompts, but if empty, return all prompts as fallback
        if not final_prompts:
            print("[WARNING] No prompts passed filter, returning all parsed prompts")
            return prompts
        
        return final_prompts
    
    except Exception as e:
        raise Exception(f"Groq API Error: {str(e)}")

# ==================== SETTINGS MANAGER ====================
class SettingsManager:
    DEFAULTS = {
        "api_keys": "",
        "model": IMAGEN4_ULTRA,
        "aspect_ratio": "16:9",
        "image_size": "2K",
        "images": 4,
        "threads": 2,
        "max_retries": 2,
        "auto_retry": True,
        "person_generation": "allow_adult",
        "clear_output_before_run": False,
        "output_dir": str(DEFAULT_OUTPUT_DIR),
        "window": {"width": 1600, "height": 900},
        "preset": "balanced",
        "script_parts": 5
    }
    
    def __init__(self, path: Path):
        self.path = path
        self.data = self.DEFAULTS.copy()
        self.load()
    
    def load(self):
        try:
            if self.path.exists():
                self.data.update(json.loads(self.path.read_text(encoding="utf-8")))
        except Exception as e:
            print(f"⚠️ Cannot read settings: {e}")
    
    def save(self):
        try:
            self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"⚠️ Cannot save settings: {e}")
    
    def get(self, k, default=None): 
        return self.data.get(k, default)
    
    def set(self, k, v): 
        self.data[k] = v

# License system removed

# ==================== AI GENERATION ====================
def generate_with_imagen4(client: genai.Client, model_id: str, prompt: str, aspect_ratio: str,
                          image_size: Optional[str], person_generation: str, n_images: int):
    kwargs = dict(
        number_of_images=int(n_images),
        aspect_ratio=aspect_ratio,
        person_generation=person_generation
    )
    if model_id in (IMAGEN4_STD, IMAGEN4_ULTRA) and image_size:
        kwargs["image_size"] = image_size
    cfg = types.GenerateImagesConfig(**kwargs)
    return client.models.generate_images(model=model_id, prompt=prompt, config=cfg)

def extract_inline_image_bytes_from_gemini(resp) -> List[bytes]:
    outs = []
    if not resp or not getattr(resp, "candidates", None): return outs
    for cand in resp.candidates:
        content = getattr(cand, "content", None)
        if not content: continue
        for part in getattr(content, "parts", []):
            inline = getattr(part, "inline_data", None)
            if inline and getattr(inline, "data", None):
                data = inline.data
                if isinstance(data, bytes):
                    outs.append(data)
                elif isinstance(data, str):
                    try: outs.append(base64.b64decode(data))
                    except Exception: pass
    return outs

def generate_with_gemini_image(client: genai.Client, prompt: str,
                               aspect_ratio: str, n_images: int) -> List[bytes]:
    images: List[bytes] = []
    for _ in range(n_images):
        try:
            cfg = GenerateContentConfig(
                response_modalities=[Modality.IMAGE],
                image_config=types.ImageConfig(aspect_ratio=aspect_ratio)
            )
            resp = client.models.generate_content(model=GEMINI_FLASH_IMAGE, contents=[prompt], config=cfg)
        except Exception:
            resp = client.models.generate_content(
                model=GEMINI_FLASH_IMAGE,
                contents=[f"{prompt}\nAspect ratio: {aspect_ratio}"],
                config=GenerateContentConfig(response_modalities=[Modality.IMAGE])
            )
        images.extend(extract_inline_image_bytes_from_gemini(resp))
    return images

def ai_fix_prompt(client: genai.Client, raw_prompt: str) -> str:
    system_hint = (
        "You are an expert prompt editor for image generation. "
        "Rewrite the user's prompt to be clear, specific, visually rich, and safe. "
        "Keep it concise (1-3 sentences). Reply with the improved prompt only."
    )
    resp = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[{"role": "user", "parts": [{"text": system_hint}, {"text": raw_prompt}]}],
        config=GenerateContentConfig(response_modalities=[Modality.TEXT])
    )
    text = getattr(resp, "text", None) or ""
    return text.strip() or raw_prompt

def describe_image_for_video(client: genai.Client, image_path: str) -> str:
    """Use Gemini Vision to describe image and create video prompt"""
    try:
        # Read image
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        system_hint = (
            "You are an expert at creating video generation prompts. "
            "Describe this image in detail for video generation. "
            "Focus on: main subject, setting, mood, lighting, camera angle. "
            "Write a cinematic prompt (1-2 sentences) that describes what motion/animation should happen. "
            "Reply with the video prompt only, no extra text."
        )
        
        resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                {
                    "role": "user", 
                    "parts": [
                        {"text": system_hint},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }
            ],
            config=GenerateContentConfig(response_modalities=[Modality.TEXT])
        )
        
        text = getattr(resp, "text", None) or ""
        return text.strip()
    except Exception as e:
        print(f"Error describing image: {e}")
        return "A cinematic scene"

def escalate_model_quality_fallback(model_id: str) -> str:
    if model_id == IMAGEN4_ULTRA:
        return IMAGEN4_STD
    return model_id

# ==================== MODERN COMPONENTS ====================

class ModernButton(QPushButton):
    """Modern styled button with gradient - Match Voice App Style"""
    def __init__(self, text: str, color: str = Theme.PRIMARY, parent=None):
        super().__init__(text, parent)
        self.base_color = color
        self.hover_color = self._darken_color(color)
        self._setup_style()
        self.setCursor(Qt.PointingHandCursor)
    
    def _darken_color(self, color: str) -> str:
        mapping = {
            Theme.PRIMARY: Theme.PRIMARY_HOVER,
            Theme.SUCCESS: Theme.SUCCESS_HOVER,
            Theme.DANGER: Theme.DANGER_HOVER,
            Theme.WARNING: Theme.WARNING_HOVER,
            Theme.INFO: Theme.INFO_HOVER,
            Theme.SECONDARY: Theme.SECONDARY_HOVER,
            Theme.PURPLE: Theme.PURPLE_HOVER,
        }
        return mapping.get(color, color)
    
    def _get_gradient_style(self):
        """Return gradient style based on color"""
        gradients = {
            Theme.PRIMARY: f"""
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF8C2E, stop:1 #F87B1B);
            """,
            Theme.SUCCESS: f"""
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #10b981, stop:1 #059669);
            """,
            Theme.DANGER: f"""
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ef4444, stop:1 #dc2626);
            """,
            Theme.WARNING: f"""
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f59e0b, stop:1 #d97706);
            """,
            Theme.INFO: f"""
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0ea5e9, stop:1 #0284c7);
            """,
            Theme.SECONDARY: f"""
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0d1836, stop:1 #090e1e);
            """,
            Theme.PURPLE: f"""
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8b5cf6, stop:1 #7c3aed);
            """,
        }
        return gradients.get(self.base_color, f"background-color: {self.base_color};")
    
    def _get_hover_gradient_style(self):
        """Return hover gradient style based on color"""
        gradients = {
            Theme.PRIMARY: f"""
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFA04D, stop:1 #FF8C2E);
            """,
            Theme.SUCCESS: f"""
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34d399, stop:1 #10b981);
            """,
            Theme.DANGER: f"""
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f87171, stop:1 #ef4444);
            """,
            Theme.WARNING: f"""
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fbbf24, stop:1 #f59e0b);
            """,
            Theme.INFO: f"""
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #38bdf8, stop:1 #0ea5e9);
            """,
            Theme.SECONDARY: f"""
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #11224E, stop:1 #0d1836);
            """,
            Theme.PURPLE: f"""
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #a78bfa, stop:1 #8b5cf6);
            """,
        }
        return gradients.get(self.base_color, f"background-color: {self.hover_color};")
    
    def _setup_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                {self._get_gradient_style()}
                color: {Theme.TEXT_INVERSE};
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 600;
                font-size: 9pt;
                min-height: 30px;
                text-shadow: 0px 1px 2px rgba(0, 0, 0, 0.2);
            }}
            QPushButton:hover {{
                {self._get_hover_gradient_style()}
            }}
            QPushButton:pressed {{
                {self._get_gradient_style()}
                padding: 7px 13px 5px 11px;
            }}
            QPushButton:disabled {{
                background: #8b99a8;
                color: #d1d5db;
                text-shadow: none;
            }}
        """)

class ModernCard(QFrame):
    """Modern card with shadow effect"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            ModernCard {{
                background-color: {Theme.BG_SECONDARY};
                border: 1px solid {Theme.BORDER};
                border-radius: 12px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)

class ImagePreviewCard(QFrame):
    """Image card with selection and delete"""
    delete_clicked = Signal(int)
    preview_clicked = Signal(int)
    
    def __init__(self, pixmap: QPixmap, index: int, parent=None):
        super().__init__(parent)
        self.index = index
        self.pixmap = pixmap
        
        self.setFixedSize(280, 200)
        self.setStyleSheet(f"""
            ImagePreviewCard {{
                background-color: {Theme.BG_SECONDARY};
                border: 2px solid {Theme.BORDER};
                border-radius: 10px;
            }}
            ImagePreviewCard:hover {{
                border-color: {Theme.PRIMARY};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Image with click - crop to 16:9 to fill without letterboxing
        self.image_label = QLabel()
        cropped_pixmap = crop_to_16_9(pixmap, 264, 148)  # 264/148 ≈ 16/9
        self.image_label.setPixmap(cropped_pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setCursor(Qt.PointingHandCursor)
        self.image_label.mousePressEvent = lambda e: self.preview_clicked.emit(self.index)
        layout.addWidget(self.image_label)
        
        # Bottom controls
        controls = QWidget()
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(6)
        
        self.check_box = QCheckBox()
        self.check_box.setChecked(True)
        self.check_box.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {Theme.BORDER_STRONG};
                background-color: {Theme.BG_SECONDARY};
            }}
            QCheckBox::indicator:checked {{
                background-color: {Theme.SUCCESS};
                border-color: {Theme.SUCCESS};
            }}
        """)
        self.check_box.stateChanged.connect(self._on_check_changed)
        controls_layout.addWidget(self.check_box)
        
        controls_layout.addStretch()
        
        delete_btn = QPushButton("🗑")
        delete_btn.setFixedSize(32, 32)
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.DANGER};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 9pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Theme.DANGER_HOVER};
            }}
        """)
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.index))
        controls_layout.addWidget(delete_btn)
        
        layout.addWidget(controls)
    
    def _on_check_changed(self, state):
        if state == Qt.Checked:
            self.setStyleSheet(f"""
                ImagePreviewCard {{
                    background-color: {Theme.BG_SECONDARY};
                    border: 2px solid {Theme.SUCCESS};
                    border-radius: 10px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                ImagePreviewCard {{
                    background-color: {Theme.BG_SECONDARY};
                    border: 2px solid {Theme.BORDER};
                    border-radius: 10px;
                }}
                ImagePreviewCard:hover {{
                    border-color: {Theme.PRIMARY};
                }}
            """)
    
    def is_selected(self):
        return self.check_box.isChecked()
    
    def set_selected(self, selected: bool):
        self.check_box.setChecked(selected)

class StatusBadge(QLabel):
    """Colored status badge"""
    def __init__(self, text: str, color: str, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                border-radius: 6px;
                padding: 3px 8px;
                font-weight: 600;
                font-size: 8pt;
            }}
        """)
        self.setAlignment(Qt.AlignCenter)

# ==================== IMAGE LIGHTBOX ====================
class ImageLightbox(QDialog):
    """Fullscreen image preview"""
    def __init__(self, pixmap: QPixmap, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Preview")
        self.setModal(True)
        self.setStyleSheet(f"background-color: rgba(0, 0, 0, 0.9);")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Close button
        close_btn = QPushButton("✕ Close")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.DANGER};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 4px 8px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {Theme.DANGER_HOVER};
            }}
        """)
        close_btn.clicked.connect(self.accept)
        close_btn.setCursor(Qt.PointingHandCursor)
        
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_btn)
        layout.addLayout(close_layout)
        
        # Image
        image_label = QLabel()
        screen_size = QApplication.primaryScreen().size()
        scaled_pixmap = pixmap.scaled(
            screen_size.width() - 100,
            screen_size.height() - 150,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)
        
        self.showMaximized()

# ==================== SCRIPT IMPORT DIALOG ====================
class ScriptImportDialog(QDialog):
    """Dialog to import script and analyze with Groq AI"""
    def __init__(self, parent=None, groq_keys: List[str] = None):
        super().__init__(parent)
        self.setWindowTitle("📄 Import Script & Auto Generate")
        self.setModal(True)
        self.resize(900, 700)
        
        self.groq_keys = groq_keys or []
        self.result_prompts = []
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Title
        title = QLabel("📄 Import Script & Auto Generate Prompts")
        title.setStyleSheet(f"""
            QLabel {{
                color: {Theme.PRIMARY};
                font-size: 18pt;
                font-weight: bold;
                margin-bottom: 8px;
            }}
        """)
        layout.addWidget(title)
        
        # Description
        desc = QLabel(
            "Paste your script below. The AI will analyze it and create prompts following the rules:\n"
            "• Split into N parts\n"
            "• Ultra-realistic, 16:9 format\n"
            "• Consistent character descriptions (no 'same outfit')\n"
            "• Characters interact with each other\n"
            "• American/European characters, no black hair\n"
            "• No 'emerald green eyes', 'revealing cleavage'"
        )
        desc.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT_SECONDARY};
                font-size: 10pt;
                margin-bottom: 12px;
                line-height: 1.5;
            }}
        """)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Number of parts
        parts_layout = QHBoxLayout()
        parts_label = QLabel("Number of parts to split:")
        parts_label.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-weight: 600; font-size: 10pt;")
        parts_layout.addWidget(parts_label)
        
        self.parts_spin = QSpinBox()
        self.parts_spin.setRange(1, 50)
        self.parts_spin.setValue(5)
        self.parts_spin.setFixedWidth(80)
        self.parts_spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {Theme.BG_SECONDARY};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER};
                border-radius: 6px;
                padding: 8px;
                font-size: 11pt;
                font-weight: 600;
            }}
        """)
        parts_layout.addWidget(self.parts_spin)
        parts_layout.addStretch()
        layout.addLayout(parts_layout)
        
        # Script input
        script_label = QLabel("📝 Script (English):")
        script_label.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-weight: 600; font-size: 10pt;")
        layout.addWidget(script_label)
        
        self.script_edit = QTextEdit()
        self.script_edit.setPlaceholderText("Paste your English script here...")
        self.script_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Theme.BG_SECONDARY};
                color: {Theme.TEXT_PRIMARY};
                border: 2px solid {Theme.BORDER};
                border-radius: 8px;
                padding: 12px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 10pt;
                line-height: 1.5;
            }}
            QTextEdit:focus {{
                border-color: {Theme.PRIMARY};
            }}
        """)
        layout.addWidget(self.script_edit, 1)
        
        # Status
        self.status_label = QLabel("Ready to analyze")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT_SECONDARY};
                font-size: 9pt;
                padding: 8px;
                background-color: {Theme.BG_TERTIARY};
                border-radius: 6px;
            }}
        """)
        layout.addWidget(self.status_label)
        
        # Progress
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Indeterminate
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {Theme.BORDER};
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Theme.PRIMARY}, stop:1 {Theme.SUCCESS});
                border-radius: 3px;
            }}
        """)
        self.progress.hide()
        layout.addWidget(self.progress)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        cancel_btn = ModernButton("Cancel", Theme.DANGER, self)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        btn_layout.addStretch()
        
        self.analyze_btn = ModernButton("🤖 Analyze & Generate", Theme.SUCCESS, self)
        self.analyze_btn.clicked.connect(self.on_analyze)
        btn_layout.addWidget(self.analyze_btn)
        
        layout.addLayout(btn_layout)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.BG_PRIMARY};
            }}
        """)
    
    def on_analyze(self):
        script = self.script_edit.toPlainText().strip()
        if not script:
            QMessageBox.warning(self, "Warning", "Please paste a script first!")
            return
        
        if not self.groq_keys:
            QMessageBox.critical(
                self, 
                "Groq API Key Missing",
                "No Groq API keys found!\n\n"
                "Please add Groq API keys in GenVideoPro Settings tab.\n"
                "Get your key at: https://console.groq.com/keys"
            )
            return
        
        num_parts = self.parts_spin.value()
        
        # Disable button and show progress
        self.analyze_btn.setEnabled(False)
        self.progress.show()
        self.status_label.setText(f"🤖 Analyzing script with Groq AI (splitting into {num_parts} parts)...")
        
        # Run in thread to not block UI
        def worker():
            try:
                # Use first Groq key
                groq_key = self.groq_keys[0]
                prompts = analyze_script_with_groq(script, num_parts, groq_key)
                
                # Success
                QTimer.singleShot(0, lambda: self.on_success(prompts))
            except Exception as e:
                error_msg = str(e)
                QTimer.singleShot(0, lambda: self.on_error(error_msg))
        
        threading.Thread(target=worker, daemon=True).start()
    
    def on_success(self, prompts: List[str]):
        self.progress.hide()
        self.analyze_btn.setEnabled(True)
        
        if not prompts:
            self.status_label.setText("❌ No prompts generated. Please check your script.")
            QMessageBox.warning(self, "No Results", "AI didn't generate any prompts. Try a different script.")
            return
        
        self.result_prompts = prompts
        self.status_label.setText(f"✅ Success! Generated {len(prompts)} prompts. Closing to import...")
        
        QMessageBox.information(
            self,
            "Success!",
            f"Successfully generated {len(prompts)} prompts!\n\n"
            f"They will be added to the queue automatically."
        )
        self.accept()
    
    def on_error(self, error_msg: str):
        self.progress.hide()
        self.analyze_btn.setEnabled(True)
        self.status_label.setText(f"❌ Error: {error_msg}")
        
        QMessageBox.critical(
            self,
            "Analysis Failed",
            f"Failed to analyze script:\n\n{error_msg}\n\n"
            f"Please check:\n"
            f"• Groq API key is valid\n"
            f"• You have internet connection\n"
            f"• Script is in English"
        )
    
    def get_prompts(self) -> List[str]:
        return self.result_prompts

# ==================== PROMPT ROW ====================
class PromptRow(QWidget):
    """Single prompt with horizontal split: left prompt, right preview"""
    def __init__(self, parent, index: int, controller):
        super().__init__(parent)
        self.controller = controller
        self.index = index
        self.saved_paths = []
        self.image_cards = []
        
        self.setStyleSheet("background-color: transparent;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 4, 0, 4)
        
        # Card container
        self.card = ModernCard()
        card_layout = QHBoxLayout(self.card)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(8)
        
        # === LEFT SIDE: Prompt Editor ===
        left_widget = QWidget()
        left_widget.setFixedWidth(400)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(4)
        
        # Header row
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(4)
        
        # Checkbox
        self.sel_cb = QCheckBox()
        self.sel_cb.setChecked(True)
        self.sel_cb.setFixedSize(16, 16)
        self.sel_cb.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 2px solid {Theme.BORDER_STRONG};
                background-color: {Theme.BG_SECONDARY};
            }}
            QCheckBox::indicator:checked {{
                background-color: {Theme.PRIMARY};
                border-color: {Theme.PRIMARY};
            }}
        """)
        header_layout.addWidget(self.sel_cb)
        
        # Index badge
        self.index_label = QLabel(f"#{index}")
        self.index_label.setFixedHeight(20)
        self.index_label.setStyleSheet(f"""
            QLabel {{
                background-color: {Theme.SECONDARY};
                color: white;
                border-radius: 3px;
                padding: 2px 8px;
                font-weight: 700;
                font-size: 9pt;
            }}
        """)
        header_layout.addWidget(self.index_label)
        
        # Status badge - default QUEUE
        self.status_badge = QLabel("QUEUE")
        self.status_badge.setFixedHeight(20)
        self.status_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {Theme.WARNING};
                color: white;
                border-radius: 3px;
                padding: 2px 8px;
                font-weight: 600;
                font-size: 8pt;
            }}
        """)
        header_layout.addWidget(self.status_badge)
        
        header_layout.addStretch()
        left_layout.addWidget(header)
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {Theme.BORDER};
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Theme.PRIMARY}, stop:1 {Theme.SUCCESS});
                border-radius: 2px;
            }}
        """)
        self.progress_bar.hide()
        left_layout.addWidget(self.progress_bar)
        
        # Prompt editor - taller for better editing - Voice App Style
        self.txt = QTextEdit()
        self.txt.setPlaceholderText("Enter prompt...")
        self.txt.setStyleSheet(f"""
            QTextEdit {{
                background-color: #fffcf9;
                color: {Theme.TEXT_PRIMARY};
                border: 2px solid #cbd5e1;
                border-radius: 5px;
                padding: 6px;
                font-size: 9pt;
                line-height: 1.4;
            }}
            QTextEdit:focus {{
                border-color: {Theme.PRIMARY};
                background-color: white;
            }}
        """)
        self.txt.setFixedHeight(130)
        left_layout.addWidget(self.txt, 1)
        
        # Action buttons row - smaller
        buttons_row = QWidget()
        buttons_layout = QHBoxLayout(buttons_row)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(3)
        
        self.open_btn = ModernButton("📁 Open", Theme.SECONDARY)
        self.open_btn.setFixedHeight(26)
        self.open_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0d1836, stop:1 #090e1e);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 10px;
                font-weight: 600;
                font-size: 8pt;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #11224E, stop:1 #0d1836);
            }}
        """)
        self.open_btn.clicked.connect(self.open_folder)
        buttons_layout.addWidget(self.open_btn)
        
        self.regen_btn = ModernButton("🔄 Regen", Theme.SUCCESS)
        self.regen_btn.setFixedHeight(26)
        self.regen_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #10b981, stop:1 #059669);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 10px;
                font-weight: 600;
                font-size: 8pt;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34d399, stop:1 #10b981);
            }}
        """)
        self.regen_btn.clicked.connect(self.regenerate)
        buttons_layout.addWidget(self.regen_btn)
        
        # AI Fix button
        self.ai_fix_btn = ModernButton("✨ AI Fix", Theme.PRIMARY)
        self.ai_fix_btn.setFixedHeight(26)
        self.ai_fix_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF8C2E, stop:1 #F87B1B);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 10px;
                font-weight: 600;
                font-size: 8pt;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFA04D, stop:1 #FF8C2E);
            }}
        """)
        self.ai_fix_btn.clicked.connect(self.ai_fix_prompt)
        buttons_layout.addWidget(self.ai_fix_btn)
        
        self.delete_btn = ModernButton("🗑 Delete", Theme.DANGER)
        self.delete_btn.setFixedHeight(26)
        self.delete_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ef4444, stop:1 #dc2626);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 10px;
                font-weight: 600;
                font-size: 8pt;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f87171, stop:1 #ef4444);
            }}
        """)
        self.delete_btn.clicked.connect(self.delete_self)
        buttons_layout.addWidget(self.delete_btn)
        
        left_layout.addWidget(buttons_row)
        
        card_layout.addWidget(left_widget)
        
        # === RIGHT SIDE: Large Image Preview ===
        right_widget = QFrame()
        right_widget.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.BG_TERTIARY};
                border: 1px solid {Theme.BORDER};
                border-radius: 6px;
            }}
        """)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Main large preview
        self.main_preview = QLabel()
        self.main_preview.setAlignment(Qt.AlignCenter)
        self.main_preview.setMinimumSize(380, 180)
        self.main_preview.setMaximumHeight(220)
        self.main_preview.setStyleSheet(f"""
            QLabel {{
                background-color: {Theme.BG_TERTIARY};
                border-radius: 6px;
                padding: 4px;
            }}
        """)
        self.main_preview.setCursor(Qt.PointingHandCursor)
        
        # Placeholder
        self.placeholder = QLabel("No images")
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setStyleSheet(f"""
            color: {Theme.TEXT_MUTED};
            font-size: 9pt;
            padding: 60px 15px;
        """)
        
        # Stack main preview
        preview_stack = QVBoxLayout()
        preview_stack.setContentsMargins(0, 0, 0, 0)
        preview_stack.addWidget(self.placeholder)
        preview_stack.addWidget(self.main_preview)
        self.main_preview.hide()
        
        right_layout.addLayout(preview_stack, 1)
        
        # Thumbnail strip at bottom - very compact
        thumb_container = QWidget()
        thumb_container.setFixedHeight(60)
        thumb_container.setStyleSheet(f"""
            QWidget {{
                background-color: {Theme.BG_SECONDARY};
                border-top: 1px solid {Theme.BORDER};
            }}
        """)
        
        thumb_layout = QHBoxLayout(thumb_container)
        thumb_layout.setContentsMargins(6, 4, 6, 4)
        thumb_layout.setSpacing(4)
        
        self.thumb_scroll = QScrollArea()
        self.thumb_scroll.setWidgetResizable(True)
        self.thumb_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.thumb_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.thumb_scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollBar:horizontal {{
                background-color: transparent;
                height: 3px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {Theme.BORDER_STRONG};
                border-radius: 2px;
            }}
        """)
        
        self.thumb_widget = QWidget()
        self.thumb_layout = QHBoxLayout(self.thumb_widget)
        self.thumb_layout.setContentsMargins(0, 0, 0, 0)
        self.thumb_layout.setSpacing(4)
        self.thumb_layout.setAlignment(Qt.AlignLeft)
        
        self.thumb_scroll.setWidget(self.thumb_widget)
        thumb_layout.addWidget(self.thumb_scroll)
        
        right_layout.addWidget(thumb_container)
        
        card_layout.addWidget(right_widget, 1)
        
        main_layout.addWidget(self.card)
        
        # Track thumbnails
        self.thumbnails = []
        self.current_preview_index = 0
    
    def get_prompt(self) -> str:
        return self.txt.toPlainText().strip()
    
    def set_index(self, idx: int):
        self.index = idx
        self.index_label.setText(f"#{idx}")
    
    def set_busy(self, busy: bool):
        self.sel_cb.setEnabled(not busy)
        self.txt.setReadOnly(busy)
        self.delete_btn.setEnabled(not busy)
        self.regen_btn.setEnabled(not busy)
        
        if busy:
            self.progress_bar.show()
            self.progress_bar.setValue(0)
        else:
            self.progress_bar.hide()
    
    def set_status(self, status: str):
        mapping = {
            "queue": ("QUEUE", Theme.WARNING),
            "generating": ("GENERATING", Theme.PRIMARY),
            "done": ("DONE", Theme.SUCCESS),
            "failed": ("FAILED", Theme.DANGER),
        }
        text, color = mapping.get(status, ("UNKNOWN", Theme.TEXT_MUTED))
        self.status_badge.setText(text)
        self.status_badge.setFixedHeight(20)
        self.status_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                border-radius: 3px;
                padding: 2px 8px;
                font-weight: 600;
                font-size: 9px;
            }}
        """)
    
    def update_progress(self, value: int):
        self.progress_bar.setValue(value)
    
    def update_preview(self, image_paths: List[Path]):
        self.saved_paths = image_paths
        self.thumbnails.clear()
        
        # Clear thumbnails
        for i in reversed(range(self.thumb_layout.count())):
            widget = self.thumb_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        if not image_paths:
            self.placeholder.show()
            self.main_preview.hide()
            self.open_btn.setEnabled(False)
            return
        
        self.placeholder.hide()
        self.main_preview.show()
        self.open_btn.setEnabled(True)
        
        # Create thumbnails - very compact
        for idx, p in enumerate(image_paths):
            try:
                pixmap = QPixmap(str(p))
                
                # Thumbnail button - very small
                thumb_btn = QPushButton()
                thumb_btn.setFixedSize(70, 48)
                thumb_btn.setCursor(Qt.PointingHandCursor)
                thumb_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Theme.BG_TERTIARY};
                        border: 2px solid {Theme.BORDER};
                        border-radius: 4px;
                        padding: 2px;
                    }}
                    QPushButton:hover {{
                        border-color: {Theme.PRIMARY};
                    }}
                """)
                
                # Set thumbnail image - crop to 16:9
                cropped_thumb = crop_to_16_9(pixmap, 66, 37)  # 66/37 ≈ 16/9
                thumb_btn.setIcon(QIcon(cropped_thumb))
                thumb_btn.setIconSize(QSize(66, 37))
                thumb_btn.clicked.connect(lambda checked, i=idx: self.show_preview(i))
                
                # Delete overlay button - very small
                delete_overlay = QPushButton("×", thumb_btn)
                delete_overlay.setFixedSize(16, 16)
                delete_overlay.move(52, 2)
                delete_overlay.setCursor(Qt.PointingHandCursor)
                delete_overlay.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Theme.DANGER};
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-weight: bold;
                        font-size: 9pt;
                        padding: 0px;
                    }}
                    QPushButton:hover {{
                        background-color: {Theme.DANGER_HOVER};
                    }}
                """)
                delete_overlay.clicked.connect(lambda checked, i=idx: self._delete_image(i))
                
                self.thumb_layout.addWidget(thumb_btn)
                self.thumbnails.append((thumb_btn, pixmap))
            except Exception as e:
                print("Preview error:", e)
        
        # Show first image
        if self.thumbnails:
            self.show_preview(0)
    
    def show_preview(self, index: int):
        """Show selected image in main preview"""
        if 0 <= index < len(self.thumbnails):
            self.current_preview_index = index
            _, pixmap = self.thumbnails[index]
            
            # Crop to 16:9 to fill preview without letterboxing
            preview_w = self.main_preview.width() - 8
            preview_h = self.main_preview.height() - 8
            
            # Force 16:9 aspect for preview area
            target_h = int(preview_w / (16/9))
            if target_h > preview_h:
                target_h = preview_h
                target_w = int(preview_h * (16/9))
            else:
                target_w = preview_w
            
            cropped = crop_to_16_9(pixmap, target_w, target_h)
            self.main_preview.setPixmap(cropped)
            
            # Update thumbnail borders
            for i, (btn, _) in enumerate(self.thumbnails):
                if i == index:
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {Theme.BG_TERTIARY};
                            border: 2px solid {Theme.SUCCESS};
                            border-radius: 4px;
                            padding: 2px;
                        }}
                    """)
                else:
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {Theme.BG_TERTIARY};
                            border: 2px solid {Theme.BORDER};
                            border-radius: 4px;
                            padding: 2px;
                        }}
                        QPushButton:hover {{
                            border-color: {Theme.PRIMARY};
                        }}
                    """)
            
            # Connect click to lightbox
            self.main_preview.mousePressEvent = lambda e: self._preview_fullscreen()
    
    def _preview_fullscreen(self):
        """Open fullscreen preview"""
        if 0 <= self.current_preview_index < len(self.saved_paths):
            try:
                pixmap = QPixmap(str(self.saved_paths[self.current_preview_index]))
                lightbox = ImageLightbox(pixmap, self)
                lightbox.exec()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Cannot preview: {e}")
    
    def _delete_image(self, index):
        """Delete specific image"""
        if 0 <= index < len(self.saved_paths):
            try:
                self.saved_paths[index].unlink()
                
                # Remove from lists
                self.saved_paths.pop(index)
                
                # Refresh preview
                self.update_preview(self.saved_paths)
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Cannot delete image: {e}")
    
    def get_selected_images(self) -> List[Path]:
        return self.saved_paths
    
    def select_all_images(self):
        pass  # Not needed in this design
    
    def deselect_all_images(self):
        pass  # Not needed in this design
    
    def delete_selected_images(self):
        pass  # Not needed in this design
    
    def open_folder(self):
        if self.saved_paths:
            try:
                os.startfile(self.saved_paths[0].parent)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Cannot open folder: {e}")
    
    def regenerate(self):
        self.controller.regenerate_row(self)
    
    def ai_fix_prompt(self):
        """AI Fix cho prompt của row này"""
        self.controller.ai_fix_single_row(self)
    
    def delete_self(self):
        self.controller.remove_row(self)

# ==================== GENERATION WORKER ====================
class GenerationWorker(QThread):
    progress_signal = Signal(int)
    row_done_signal = Signal(object, list, str)
    all_done_signal = Signal()
    
    def __init__(self, targets, controller):
        super().__init__()
        self.targets = targets
        self.controller = controller
        self.cancel_flag = False
    
    def run(self):
        concurrency = self.controller.get_concurrency()
        done = 0
        
        with ThreadPoolExecutor(max_workers=concurrency) as ex:
            futures = {ex.submit(self.task_fn, r): r for r in self.targets}
            for fut in as_completed(futures):
                if self.cancel_flag:
                    break
                row = futures[fut]
                try:
                    r, paths, err = fut.result()
                    self.row_done_signal.emit(r, paths, err)
                except Exception as e2:
                    self.row_done_signal.emit(row, [], str(e2))
                
                done += 1
                self.progress_signal.emit(done)
        
        self.all_done_signal.emit()
    
    def task_fn(self, row):
        self.controller._delete_images_for_row(row.index)
        
        tries = 0
        last_err = None
        saved_paths = []
        
        model_id_local = self.controller.get_base_model_id()
        user_prompt_raw = row.get_prompt()
        
        max_retries = self.controller.get_max_retries()
        auto_retry = self.controller.get_auto_retry()
        
        while tries < max_retries and not self.cancel_flag:
            api_key = self.controller.rotator.current()
            client = genai.Client(api_key=api_key)
            
            final_prompt = user_prompt_raw
            
            try:
                if model_id_local.startswith("imagen-4.0"):
                    effective_size = self.controller.get_image_size() if model_id_local in (IMAGEN4_STD, IMAGEN4_ULTRA) else None
                    
                    resp = generate_with_imagen4(
                        client,
                        model_id_local,
                        final_prompt,
                        self.controller.get_aspect_ratio(),
                        effective_size,
                        self.controller.get_person_gen(),
                        self.controller.get_n_images()
                    )
                    bytes_list = [gi.image.image_bytes for gi in resp.generated_images]
                    saved_paths = self.controller.save_bytes_list(row.index, bytes_list)
                else:
                    bytes_list = generate_with_gemini_image(
                        client,
                        final_prompt,
                        self.controller.get_aspect_ratio(),
                        self.controller.get_n_images()
                    )
                    saved_paths = self.controller.save_bytes_list(row.index, bytes_list)
                
                return (row, saved_paths, None)
            
            except Exception as e:
                last_err = str(e)
                
                if not auto_retry:
                    break
                
                if is_rate_or_quota_error(last_err):
                    self.controller.rotator.next()
                    
                    low = last_err.lower()
                    if ("quota" in low or "permission" in low or "exhaust" in low or "403" in low):
                        model_id_local = escalate_model_quality_fallback(model_id_local)
                    
                    time.sleep(0.3)
                    tries += 1
                    continue
                
                break
        
        return (row, saved_paths, last_err)
    
    def cancel(self):
        self.cancel_flag = True

# ==================== MAIN APPLICATION ====================
class ImageGeneratorTab(QWidget):
    """Image Generator Widget - để nhúng vào GenVideoPro tab"""
    # Signals for thread-safe communication
    script_analysis_success = Signal(list)  # List[str] of prompts
    script_analysis_error = Signal(str)     # Error message
    
    def __init__(self, parent=None, api_client=None):
        super().__init__(parent)
        
        self.api_client = api_client
        self.settings = SettingsManager(SETTINGS_PATH)
        
        # Theme - Match Voice App Style
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Theme.BG_PRIMARY};
            }}
            QLabel {{
                color: {Theme.TEXT_PRIMARY};
            }}
            QTextEdit, QLineEdit {{
                background-color: white;
                color: {Theme.TEXT_PRIMARY};
                border: 2px solid #cbd5e1;
                border-radius: 5px;
                padding: 6px 10px;
                font-size: 9pt;
            }}
            QTextEdit:focus, QLineEdit:focus {{
                border-color: {Theme.PRIMARY};
            }}
            QComboBox {{
                background-color: white;
                color: {Theme.TEXT_PRIMARY};
                border: 2px solid #cbd5e1;
                border-radius: 5px;
                padding: 6px 10px;
                font-size: 9pt;
                min-height: 26px;
            }}
            QComboBox:hover {{
                border-color: {Theme.PRIMARY};
            }}
            QComboBox:focus {{
                border-color: {Theme.PRIMARY};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: white;
                color: {Theme.TEXT_PRIMARY};
                selection-background-color: {Theme.PRIMARY};
                selection-color: white;
                border: 2px solid #cbd5e1;
            }}
            QSpinBox {{
                background-color: white;
                color: {Theme.TEXT_PRIMARY};
                border: 2px solid #cbd5e1;
                border-radius: 5px;
                padding: 6px 10px;
                min-height: 26px;
                font-size: 9pt;
            }}
            QSpinBox:hover {{
                border-color: {Theme.PRIMARY};
            }}
            QSpinBox:focus {{
                border-color: {Theme.PRIMARY};
            }}
            QCheckBox {{
                color: {Theme.TEXT_PRIMARY};
                spacing: 8px;
                font-size: 9pt;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #94a3b8;
                background-color: white;
            }}
            QCheckBox::indicator:hover {{
                border-color: {Theme.PRIMARY};
            }}
            QCheckBox::indicator:checked {{
                background-color: {Theme.PRIMARY};
                border-color: {Theme.PRIMARY};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cGF0aCBkPSJNMTAgM0w0LjUgOC41TDIgNiIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
            }}
            QCheckBox::indicator:checked:hover {{
                background-color: {Theme.PRIMARY_HOVER};
            }}
            QGroupBox {{
                background-color: white;
                border: 2px solid {Theme.BORDER};
                border-radius: 8px;
                margin-top: 12px;
                font-weight: 600;
                font-size: 10pt;
                padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                top: 4px;
                color: {Theme.TEXT_PRIMARY};
            }}
        """)
        
        self.rows = []
        
        # Initialize with empty keys - will be loaded from server
        DEFAULT_KEY = "AIzaSyBZI6MARCTjityVTpe5-_SWyONlm-Cdm-w"  # Fallback only
        self.rotator = KeyRotator([DEFAULT_KEY])
        
        self.output_dir = Path(self.settings.get("output_dir", str(DEFAULT_OUTPUT_DIR)))
        self.output_dir.mkdir(exist_ok=True)
        
        self.worker = None
        
        # Connect signals for thread-safe script analysis
        self.script_analysis_success.connect(self._on_script_analysis_success)
        self.script_analysis_error.connect(self._on_script_analysis_error)
        
        self._build_ui()
        self._load_settings_to_ui()
    
    def _build_ui(self):
        # QWidget không có setCentralWidget, dùng layout trực tiếp
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # === BODY ===
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        
        # === SIDEBAR ===
        sidebar = QWidget()
        sidebar.setFixedWidth(380)
        sidebar.setStyleSheet(f"""
            background-color: {Theme.BG_SECONDARY};
            border-right: 1px solid {Theme.BORDER};
        """)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 12, 12, 12)
        sidebar_layout.setSpacing(8)
        
        # Output folder
        output_section = self._create_section("📁 Output Folder")
        sidebar_layout.addWidget(output_section)
        
        output_layout = QHBoxLayout()
        self.output_edit = QLineEdit(str(self.output_dir))
        self.output_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: #fffcf9;
                padding: 6px 10px;
                font-size: 9pt;
            }}
        """)
        output_layout.addWidget(self.output_edit)
        
        browse_btn = ModernButton("...", Theme.PRIMARY)
        browse_btn.setFixedWidth(40)
        browse_btn.setFixedHeight(24)
        browse_btn.clicked.connect(self.on_browse_output)
        output_layout.addWidget(browse_btn)
        
        sidebar_layout.addLayout(output_layout)
        
        # Settings tabs - Match Voice App Style
        settings_tabs = QTabWidget()
        settings_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {Theme.BORDER};
                border-radius: 0px;
                background-color: white;
                padding: 0px;
            }}
            QTabBar::tab {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f1f5f9, stop:1 #e2e8f0);
                color: #1f2937;
                padding: 8px 16px;
                border: 1px solid {Theme.BORDER};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
                font-size: 9pt;
                font-weight: 600;
            }}
            QTabBar::tab:selected {{
                background: white;
                color: {Theme.PRIMARY};
                font-weight: 700;
            }}
            QTabBar::tab:hover:!selected {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
            }}
        """)
        
        # Basic tab
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        basic_layout.setSpacing(12)
        
        basic_layout.addWidget(self._create_label("Model"))
        self.model_cb = QComboBox()
        self.model_cb.addItems(SUPPORTED_MODELS)
        self.model_cb.currentTextChanged.connect(self.on_model_change)
        self.model_cb.setMinimumWidth(360)
        basic_layout.addWidget(self.model_cb)
        
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setVerticalSpacing(8)
        
        grid.addWidget(self._create_label("Aspect Ratio"), 0, 0)
        self.ar_cb = QComboBox()
        self.ar_cb.addItems(AR_IMAGEN)
        self.ar_cb.setMinimumWidth(180)
        grid.addWidget(self.ar_cb, 1, 0)
        
        grid.addWidget(self._create_label("Size"), 0, 1)
        self.size_cb = QComboBox()
        self.size_cb.addItems(IMAGEN_SIZES)
        self.size_cb.setMinimumWidth(180)
        grid.addWidget(self.size_cb, 1, 1)
        
        grid.addWidget(self._create_label("Images per Prompt"), 2, 0)
        self.count_cb = QComboBox()
        self.count_cb.addItems(["1", "2", "3", "4", "5", "6", "8"])
        self.count_cb.setMinimumWidth(180)
        grid.addWidget(self.count_cb, 3, 0)
        
        grid.addWidget(self._create_label("Threads"), 2, 1)
        self.cc_cb = QComboBox()
        self.cc_cb.addItems(["1", "2", "3", "4", "5"])
        self.cc_cb.setMinimumWidth(180)
        grid.addWidget(self.cc_cb, 3, 1)
        
        basic_layout.addLayout(grid)
        basic_layout.addStretch()
        
        settings_tabs.addTab(basic_tab, "Basic")
        
        # Advanced tab
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        advanced_layout.setSpacing(12)
        
        advanced_layout.addWidget(self._create_label("Max Retries"))
        self.retry_spin = QSpinBox()
        self.retry_spin.setRange(0, 10)
        self.retry_spin.setMinimumWidth(360)
        advanced_layout.addWidget(self.retry_spin)
        
        advanced_layout.addWidget(self._create_label("Person Generation"))
        self.person_cb = QComboBox()
        self.person_cb.addItems(PERSON_GEN)
        self.person_cb.setMinimumWidth(360)
        advanced_layout.addWidget(self.person_cb)
        
        advanced_layout.addWidget(self._create_label("Script Parts (for Import Script)"))
        self.script_parts_spin = QSpinBox()
        self.script_parts_spin.setRange(1, 50)
        self.script_parts_spin.setValue(5)
        self.script_parts_spin.setMinimumWidth(360)
        advanced_layout.addWidget(self.script_parts_spin)
        
        self.auto_retry_cb = QCheckBox("🔄 Auto retry on errors")
        self.auto_retry_cb.setToolTip("Automatically retry with next API key when rate limit or quota errors occur\n(Default: ON ✓)")
        self.auto_retry_cb.setStyleSheet(f"""
            QCheckBox {{
                font-weight: 600;
                padding: 4px 0px;
            }}
        """)
        advanced_layout.addWidget(self.auto_retry_cb)
        
        self.clear_before_cb = QCheckBox("🧹 Clear output before run")
        self.clear_before_cb.setToolTip("Delete all existing images in output folder before generating new ones\n(Default: OFF)")
        self.clear_before_cb.setStyleSheet(f"""
            QCheckBox {{
                font-weight: 600;
                padding: 4px 0px;
            }}
        """)
        advanced_layout.addWidget(self.clear_before_cb)
        
        self.auto_describe_cb = QCheckBox("🤖 Auto describe when sending to Video")
        self.auto_describe_cb.setToolTip("Use AI Vision to automatically generate video prompts from images\nwhen sending to Image2Video tab\n(Default: ON ✓)")
        self.auto_describe_cb.setStyleSheet(f"""
            QCheckBox {{
                font-weight: 600;
                padding: 4px 0px;
            }}
        """)
        advanced_layout.addWidget(self.auto_describe_cb)
        
        advanced_layout.addStretch()
        
        settings_tabs.addTab(advanced_tab, "Advanced")
        
        sidebar_layout.addWidget(settings_tabs)
        
        # Save button
        save_btn = ModernButton("💾 Save Settings", Theme.SUCCESS)
        save_btn.clicked.connect(self.save_settings)
        sidebar_layout.addWidget(save_btn)
        
        # Quick add
        sidebar_layout.addWidget(self._create_section("✨ Quick Add"))
        
        self.quick_prompt_edit = QLineEdit()
        self.quick_prompt_edit.setPlaceholderText("Type prompt and press Enter...")
        self.quick_prompt_edit.returnPressed.connect(self._on_quick_add)
        self.quick_prompt_edit.setStyleSheet(f"""
            QLineEdit {{
                padding: 6px 10px;
                font-size: 9pt;
            }}
        """)
        sidebar_layout.addWidget(self.quick_prompt_edit)
        
        add_btn = ModernButton("➕ Add Prompt", Theme.SUCCESS)
        add_btn.clicked.connect(self._on_quick_add)
        sidebar_layout.addWidget(add_btn)
        
        sidebar_layout.addStretch()
        
        body_layout.addWidget(sidebar)
        
        # === MAIN CONTENT ===
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Toolbar
        toolbar = QWidget()
        toolbar.setFixedHeight(70)
        toolbar.setStyleSheet(f"""
            background-color: {Theme.BG_SECONDARY};
            border-bottom: 1px solid {Theme.BORDER};
        """)
        
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(24, 0, 24, 0)
        toolbar_layout.setSpacing(8)
        
        import_btn = ModernButton("📄 Import TXT", Theme.SECONDARY)
        import_btn.setMaximumWidth(130)
        import_btn.clicked.connect(self.on_import_txt)
        toolbar_layout.addWidget(import_btn)
        
        script_import_btn = ModernButton("📜 Import Script", Theme.PRIMARY)
        script_import_btn.setMaximumWidth(140)
        script_import_btn.clicked.connect(self.on_import_script)
        toolbar_layout.addWidget(script_import_btn)
        
        toolbar_layout.addSpacing(12)
        
        run_sel_btn = ModernButton("▶️ Run Selected", Theme.SUCCESS)
        run_sel_btn.setMaximumWidth(130)
        run_sel_btn.clicked.connect(self.on_run_selected)
        toolbar_layout.addWidget(run_sel_btn)
        
        run_all_btn = ModernButton("▶️ Run All", Theme.SUCCESS)
        run_all_btn.setMaximumWidth(110)
        run_all_btn.clicked.connect(self.on_run_all)
        toolbar_layout.addWidget(run_all_btn)
        
        retry_btn = ModernButton("🔁 Retry Failed", Theme.WARNING)
        retry_btn.setMaximumWidth(130)
        retry_btn.clicked.connect(self.on_retry_failed)
        toolbar_layout.addWidget(retry_btn)
        
        toolbar_layout.addSpacing(12)
        
        send_to_video_btn = ModernButton("🎬 to Video", Theme.PRIMARY)
        send_to_video_btn.setMaximumWidth(110)
        send_to_video_btn.clicked.connect(self.on_send_to_image2video)
        toolbar_layout.addWidget(send_to_video_btn)
        
        self.cancel_btn = ModernButton("⏹ Cancel", Theme.DANGER)
        self.cancel_btn.setMaximumWidth(100)
        self.cancel_btn.clicked.connect(self.on_cancel_batch)
        self.cancel_btn.setEnabled(False)
        toolbar_layout.addWidget(self.cancel_btn)
        
        toolbar_layout.addSpacing(12)
        
        delete_btn = ModernButton("🗑 Delete All", Theme.DANGER)
        delete_btn.setMaximumWidth(120)
        delete_btn.clicked.connect(self.on_delete_all_rows)
        toolbar_layout.addWidget(delete_btn)
        
        toolbar_layout.addStretch()
        
        # Button to load Gemini keys from server
        load_keys_btn = ModernButton("🔑 Load Keys", Theme.PRIMARY)
        load_keys_btn.setMaximumWidth(120)
        load_keys_btn.setToolTip("Load Gemini API keys from Admin Panel server")
        load_keys_btn.clicked.connect(self.load_gemini_keys_from_server)
        toolbar_layout.addWidget(load_keys_btn)
        
        right_layout.addWidget(toolbar)
        
        # Rows scroll
        rows_scroll = QScrollArea()
        rows_scroll.setWidgetResizable(True)
        rows_scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {Theme.BG_PRIMARY};
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: transparent;
                width: 12px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {Theme.BORDER_STRONG};
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {Theme.TEXT_MUTED};
            }}
        """)
        
        self.rows_widget = QWidget()
        self.rows_layout = QVBoxLayout(self.rows_widget)
        self.rows_layout.setContentsMargins(16, 16, 16, 16)
        self.rows_layout.setSpacing(6)
        self.rows_layout.addStretch()
        
        rows_scroll.setWidget(self.rows_widget)
        right_layout.addWidget(rows_scroll)
        
        # Status bar
        status_bar = QWidget()
        status_bar.setFixedHeight(60)
        status_bar.setStyleSheet(f"""
            background-color: {Theme.BG_SECONDARY};
            border-top: 1px solid {Theme.BORDER};
        """)
        
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(24, 0, 24, 0)
        
        self.status_label = QLabel("🎨 Ready to generate")
        self.status_label.setStyleSheet(f"""
            color: {Theme.TEXT_PRIMARY};
            font-size: 9pt;
            font-weight: 600;
        """)
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.progress = QProgressBar()
        self.progress.setFixedWidth(300)
        self.progress.setFixedHeight(8)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {Theme.BORDER};
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Theme.PRIMARY},
                    stop:1 {Theme.SUCCESS}
                );
                border-radius: 4px;
            }}
        """)
        status_layout.addWidget(self.progress)
        
        right_layout.addWidget(status_bar)
        
        body_layout.addWidget(right_widget, 1)
        main_layout.addWidget(body)
    
    def _create_section(self, title: str) -> QLabel:
        """Create section header - Match Voice App Style"""
        label = QLabel(title)
        label.setStyleSheet(f"""
            color: {Theme.TEXT_PRIMARY};
            font-weight: 700;
            font-size: 10pt;
            margin-top: 12px;
            margin-bottom: 6px;
        """)
        return label
    
    def _create_label(self, text: str) -> QLabel:
        """Create label for form fields - Match Voice App Style"""
        label = QLabel(text)
        label.setStyleSheet(f"""
            color: {Theme.TEXT_PRIMARY};
            font-weight: 600;
            font-size: 9pt;
        """)
        return label
    
    def _load_settings_to_ui(self):
        s = self.settings
        self.output_edit.setText(s.get("output_dir", str(DEFAULT_OUTPUT_DIR)))
        self.model_cb.setCurrentText(s.get("model", IMAGEN4_ULTRA))
        self.on_model_change()
        self.ar_cb.setCurrentText(s.get("aspect_ratio", "16:9"))
        self.size_cb.setCurrentText(s.get("image_size", "2K"))
        self.count_cb.setCurrentText(str(s.get("images", 4)))
        self.cc_cb.setCurrentText(str(s.get("threads", 2)))
        self.retry_spin.setValue(int(s.get("max_retries", 2)))
        self.script_parts_spin.setValue(int(s.get("script_parts", 5)))
        self.auto_retry_cb.setChecked(bool(s.get("auto_retry", True)))
        self.clear_before_cb.setChecked(bool(s.get("clear_output_before_run", False)))
        self.auto_describe_cb.setChecked(bool(s.get("auto_describe_for_video", True)))
        self.person_cb.setCurrentText(s.get("person_generation", "allow_adult"))
    
    def save_settings(self):
        self.settings.set("output_dir", self.output_edit.text().strip())
        self.settings.set("model", self.model_cb.currentText())
        self.settings.set("aspect_ratio", self.ar_cb.currentText())
        self.settings.set("image_size", self.size_cb.currentText())
        self.settings.set("images", int(self.count_cb.currentText()))
        self.settings.set("threads", int(self.cc_cb.currentText()))
        self.settings.set("max_retries", int(self.retry_spin.value()))
        self.settings.set("script_parts", int(self.script_parts_spin.value()))
        self.settings.set("auto_retry", bool(self.auto_retry_cb.isChecked()))
        self.settings.set("clear_output_before_run", bool(self.clear_before_cb.isChecked()))
        self.settings.set("auto_describe_for_video", bool(self.auto_describe_cb.isChecked()))
        self.settings.set("person_generation", self.person_cb.currentText())
        
        try:
            w = self.width()
            h = self.height()
            self.settings.set("window", {"width": w, "height": h})
        except Exception:
            pass
        
        self.settings.save()
        self.set_status("💾 Settings saved successfully")
    
    def on_model_change(self):
        m = self.model_cb.currentText()
        if m == GEMINI_FLASH_IMAGE:
            self.ar_cb.clear()
            self.ar_cb.addItems(AR_GEMINI)
        else:
            self.ar_cb.clear()
            self.ar_cb.addItems(AR_IMAGEN)
        
        enable_size = (m in (IMAGEN4_STD, IMAGEN4_ULTRA))
        self.size_cb.setEnabled(enable_size)
    
    def on_browse_output(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", str(self.output_dir))
        if folder:
            self.output_dir = Path(folder)
            self.output_dir.mkdir(exist_ok=True)
            self.output_edit.setText(str(self.output_dir))
            self.set_status(f"📁 Output folder updated")
    
    def _on_quick_add(self):
        text = self.quick_prompt_edit.text().strip()
        if not text:
            return
        self.add_row(text)
        self.quick_prompt_edit.clear()
        self.set_status(f"➕ Added 1 prompt")
    
    def add_row(self, prompt: str = ""):
        idx = len(self.rows) + 1
        row = PromptRow(self.rows_widget, idx, self)
        row.txt.setPlainText(prompt)
        self.rows.append(row)
        self.rows_layout.insertWidget(self.rows_layout.count() - 1, row)
    
    def remove_row(self, row: PromptRow):
        if row in self.rows:
            self.rows.remove(row)
            row.deleteLater()
            for i, r in enumerate(self.rows, start=1):
                r.set_index(i)
    
    def regenerate_row(self, row: PromptRow):
        self.generate_rows([row])
    
    def ai_fix_single_row(self, row: PromptRow):
        """AI Fix cho một row cụ thể"""
        row.set_busy(True)
        row.set_status("fixing")
        
        def worker():
            raw = row.get_prompt()
            fixed = None
            err = None
            tries = 0
            max_retries = max(1, self.retry_spin.value())
            
            while tries < max_retries:
                api_key = self.rotator.current()
                client = genai.Client(api_key=api_key)
                try:
                    fixed = ai_fix_prompt(client, raw)
                    break
                except Exception as e:
                    err = e
                    if self.auto_retry_cb.isChecked() and is_rate_or_quota_error(str(e)):
                        self.rotator.next()
                        tries += 1
                        time.sleep(0.25)
                    else:
                        break
            
            if fixed:
                row.txt.setPlainText(fixed)
                row.set_status("done")
            else:
                row.set_status(f"error: {err}")
            
            row.set_busy(False)
        
        threading.Thread(target=worker, daemon=True).start()
    
    def on_import_txt(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Prompts", "", "Text files (*.txt)")
        if not file_path:
            return
        
        lines = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as fp:
            for line in fp:
                s = line.strip()
                if s:
                    lines.append(s)
        
        if not lines:
            QMessageBox.information(self, "Info", "File is empty.")
            return
        
        for s in lines:
            self.add_row(s)
        self.set_status(f"✅ Imported {len(lines)} prompts")
    
    def _load_groq_keys_from_genvideo_settings(self) -> List[str]:
        """Load Groq API keys from GenVideoPro settings file"""
        try:
            genvideo_settings_path = Path(__file__).parent / "vgp_settings.json"
            if genvideo_settings_path.exists():
                with open(genvideo_settings_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    keys = data.get("groq_keys", [])
                    return [k.strip() for k in keys if k.strip()]
        except Exception as e:
            print(f"Error loading Groq keys: {e}")
        return []
    
    def on_import_script(self):
        """Import script from TXT file and auto-generate prompts with Groq AI"""
        # Load Groq keys from GenVideoPro settings
        groq_keys = self._load_groq_keys_from_genvideo_settings()
        
        if not groq_keys:
            QMessageBox.critical(
                self, 
                "Groq API Key Missing",
                "No Groq API keys found!\n\n"
                "Please add Groq API keys in GenVideoPro Settings tab.\n"
                "Get your key at: https://console.groq.com/keys"
            )
            return
        
        # Open file dialog to select script TXT file
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Import Script File", 
            "", 
            "Text files (*.txt)"
        )
        
        if not file_path:
            return
        
        # Read script from file
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                script = f.read().strip()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read file:\n{e}")
            return
        
        if not script:
            QMessageBox.warning(self, "Empty File", "The script file is empty!")
            return
        
        # Get number of parts from settings
        num_parts = int(self.script_parts_spin.value())
        
        # Show processing message
        self.set_status(f"🤖 Analyzing script with Groq AI (splitting into {num_parts} parts)...")
        
        # Process in thread to not block UI
        def worker():
            try:
                print(f"[WORKER] Starting analysis with {num_parts} parts")
                print(f"[WORKER] Script length: {len(script)} chars")
                print(f"[WORKER] Script preview: {script[:200]}...")
                
                groq_key = groq_keys[0]
                print(f"[WORKER] Using Groq key: {groq_key[:20]}...")
                
                prompts = analyze_script_with_groq(script, num_parts, groq_key)
                
                print(f"[WORKER] Got {len(prompts)} prompts from AI")
                
                # Success - emit signal to update UI safely from main thread
                self.script_analysis_success.emit(prompts)
            except Exception as e:
                error_msg = str(e)
                print(f"[WORKER ERROR] {error_msg}")
                import traceback
                traceback.print_exc()
                # Emit error signal to update UI safely from main thread
                self.script_analysis_error.emit(error_msg)
        
        threading.Thread(target=worker, daemon=True).start()
    
    def _on_script_analysis_success(self, prompts: List[str]):
        """Handle successful script analysis"""
        print(f"[SUCCESS HANDLER] Received {len(prompts)} prompts")
        
        if not prompts:
            self.set_status("❌ No prompts generated from script")
            QMessageBox.warning(self, "No Results", "AI didn't generate any prompts. Check console for debug info.")
            return
        
        # DEBUG: Print first prompt preview
        if prompts:
            print(f"[FIRST PROMPT PREVIEW]: {prompts[0][:100]}...")
        
        # Show message box with prompts summary
        prompt_summary = "\n".join([f"{i+1}. {p[:50]}..." for i, p in enumerate(prompts[:5])])
        if len(prompts) > 5:
            prompt_summary += f"\n... và {len(prompts)-5} prompts khác"
        
        QMessageBox.information(
            self,
            "✅ Prompts Generated",
            f"Generated {len(prompts)} prompts:\n\n{prompt_summary}\n\n"
            f"Adding to queue now..."
        )
        
        # Add all prompts to queue
        for i, prompt in enumerate(prompts):
            print(f"[ADDING ROW {i+1}]: {prompt[:60]}...")
            self.add_row(prompt)
        
        # Force UI update and scroll to show new rows
        QApplication.processEvents()
        self.rows_scroll.ensureVisible(0, self.rows_scroll.widget().height())
        
        self.set_status(f"✅ Imported {len(prompts)} prompts from script. Generating...")
        print(f"[STATUS] Starting generation for {len(prompts)} prompts")
        
        # Auto-generate all imported prompts (no dialog)
        new_rows = self.rows[-len(prompts):]
        print(f"[GENERATING] {len(new_rows)} rows")
        self.generate_rows(new_rows)
    
    def _on_script_analysis_error(self, error_msg: str):
        """Handle script analysis error"""
        self.set_status(f"❌ Script analysis failed: {error_msg}")
        
        QMessageBox.critical(
            self,
            "Analysis Failed",
            f"Failed to analyze script:\n\n{error_msg}\n\n"
            f"Please check:\n"
            f"• Groq API key is valid\n"
            f"• You have internet connection\n"
            f"• Script is in English"
        )
    
    def on_ai_fix_selected(self):
        targets = [r for r in self.rows if r.sel_cb.isChecked()]
        if not targets:
            QMessageBox.information(self, "Info", "Select at least 1 row.")
            return
        
        for r in targets:
            r.set_busy(True)
            r.set_status("generating")
        
        def worker():
            for r in targets:
                raw = r.get_prompt()
                fixed = None
                err = None
                tries = 0
                max_retries = max(1, self.retry_spin.value())
                
                while tries < max_retries:
                    api_key = self.rotator.current()
                    client = genai.Client(api_key=api_key)
                    try:
                        fixed = ai_fix_prompt(client, raw)
                        break
                    except Exception as e:
                        err = e
                        if self.auto_retry_cb.isChecked() and is_rate_or_quota_error(str(e)):
                            self.rotator.next()
                            tries += 1
                            time.sleep(0.25)
                        else:
                            break
                
                if fixed:
                    r.txt.setPlainText(fixed)
                    r.set_status("done")
                else:
                    r.set_status("failed")
                r.set_busy(False)
        
        threading.Thread(target=worker, daemon=True).start()
    
    def on_run_selected(self):
        targets = [r for r in self.rows if r.sel_cb.isChecked()]
        if not targets:
            QMessageBox.information(self, "Info", "Select at least 1 row.")
            return
        self.generate_rows(targets)
    
    def on_run_all(self):
        if not self.rows:
            QMessageBox.information(self, "Info", "No prompts yet.")
            return
        self.generate_rows(self.rows)
    
    def on_retry_failed(self):
        failed_rows = [r for r in self.rows if "FAILED" in r.status_badge.text()]
        if not failed_rows:
            QMessageBox.information(self, "Info", "No failed rows.")
            return
        self.generate_rows(failed_rows)
    
    def on_send_to_image2video(self):
        """Chuyển tất cả ảnh đã generate thành công sang Image to Video tab"""
        # Collect all successfully generated images
        successful_images = []
        
        for row in self.rows:
            # Check if row has completed (has saved images)
            if hasattr(row, 'saved_paths') and row.saved_paths:
                prompt = row.get_prompt()
                # Get the first image as start image
                first_image = str(row.saved_paths[0])
                successful_images.append({
                    'prompt': prompt,
                    'image': first_image
                })
        
        if not successful_images:
            QMessageBox.information(
                self, 
                "No Images", 
                "No successfully generated images to send.\n\n"
                "Please generate some images first."
            )
            return
        
        # Auto describe images if enabled
        if self.auto_describe_cb.isChecked():
            self.set_status("🤖 Auto describing images for video...")
            
            def describe_worker():
                for i, img_data in enumerate(successful_images):
                    try:
                        api_key = self.rotator.current()
                        client = genai.Client(api_key=api_key)
                        video_prompt = describe_image_for_video(client, img_data['image'])
                        if video_prompt and video_prompt != "A cinematic scene":
                            img_data['prompt'] = video_prompt
                        self.set_status(f"🤖 Described {i+1}/{len(successful_images)} images...")
                    except Exception as e:
                        print(f"Error describing image {i+1}: {e}")
                        # Keep original prompt if error
                
                # Continue with sending to video after describing
                QTimer.singleShot(0, lambda: self._finish_send_to_video(successful_images))
            
            threading.Thread(target=describe_worker, daemon=True).start()
            return
        
        # If not auto-describing, send directly
        self._finish_send_to_video(successful_images)
    
    def _finish_send_to_video(self, successful_images):
        
        # Get parent (GenVideoPro MainWindow)
        parent = self.parent()
        while parent and not hasattr(parent, 'image_prompts'):
            parent = parent.parent()
        
        if not parent:
            QMessageBox.warning(
                self,
                "Error",
                "Cannot find GenVideoPro main window.\n\n"
                "This feature only works when Image Generator is embedded in GenVideoPro."
            )
            return
        
        # Add to Image to Video tab
        try:
            # Import dynamically to avoid circular imports
            import sys
            if 'GenVideoPro' in sys.modules:
                from GenVideoPro import ImagePromptRow
            else:
                # Create ImagePromptRow inline if not available
                from dataclasses import dataclass
                @dataclass
                class ImagePromptRow:
                    prompt: str
                    start_image: str
                    status: str = "Pending"
                    video: str = ""
            
            # Add all images to image_prompts list
            for img_data in successful_images:
                ipr = ImagePromptRow(
                    prompt=img_data['prompt'], 
                    start_image=img_data['image']
                )
                parent.image_prompts.append(ipr)
            
            # Refresh the Image to Video table
            if hasattr(parent, '_refresh_image_table'):
                parent._refresh_image_table()
            
            # Switch to Image to Video tab
            if hasattr(parent, 'tabs'):
                # Find Image to Video tab index
                for i in range(parent.tabs.count()):
                    if "Image to Video" in parent.tabs.tabText(i):
                        parent.tabs.setCurrentIndex(i)
                        break
            
            self.set_status(f"✅ Sent {len(successful_images)} images to Video")
            
            QMessageBox.information(
                self,
                "Success",
                f"✅ Sent {len(successful_images)} images to Image to Video tab!\n\n"
                f"Switched to Image to Video tab."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to send images to Image to Video:\n\n{str(e)}"
            )
    
    def on_cancel_batch(self):
        if self.worker:
            self.worker.cancel()
        self.set_status("⚠️ Canceling...")
    
    def on_delete_all_rows(self):
        if not self.rows:
            return
        reply = QMessageBox.question(self, "Confirm", "Delete all rows?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            for r in list(self.rows):
                r.deleteLater()
            self.rows.clear()
            self.set_status("🗑 Deleted all rows")
    
    def _clear_output_folder(self):
        cnt = 0
        for p in self.output_dir.glob("*.png"):
            try:
                p.unlink()
                cnt += 1
            except Exception:
                pass
        return cnt
    
    def _delete_images_for_row(self, row_index: int):
        prefix = f"{row_index:02d}_"
        for p in self.output_dir.glob("*.png"):
            if p.name.startswith(prefix):
                try:
                    p.unlink()
                except Exception:
                    pass
    
    def generate_rows(self, targets: List[PromptRow]):
        if self.clear_before_cb.isChecked():
            removed = self._clear_output_folder()
            if removed:
                self.set_status(f"🧹 Cleared {removed} images")
        
        total = len(targets)
        self.progress.setMaximum(total)
        self.progress.setValue(0)
        self.cancel_btn.setEnabled(True)
        
        for r in targets:
            r.set_busy(True)
            r.set_status("generating")
        
        self.set_status(f"⚡ Generating {total} prompts...")
        
        self.worker = GenerationWorker(targets, self)
        self.worker.progress_signal.connect(self.on_progress_update)
        self.worker.row_done_signal.connect(self.on_row_done)
        self.worker.all_done_signal.connect(self.on_all_done)
        self.worker.start()
    
    def on_progress_update(self, value):
        self.progress.setValue(value)
        total = self.progress.maximum()
        self.set_status(f"⚡ Generating... {value}/{total}")
    
    def on_row_done(self, row, paths, error):
        if paths:
            row.update_preview(paths)
            row.set_status("done")
        else:
            row.set_status("failed")
            if error:
                print("Error:", error)
        row.set_busy(False)
    
    def on_all_done(self):
        self.cancel_btn.setEnabled(False)
        completed = self.progress.value()
        self.set_status(f"✅ Complete! Generated {completed} prompts")
        self.worker = None
    
    def set_status(self, text: str):
        self.status_label.setText(text)
    
    def closeEvent(self, event):
        self.save_settings()
        event.accept()
    
    # Helper methods for worker
    def get_concurrency(self):
        return max(1, int(self.cc_cb.currentText()))
    
    def get_base_model_id(self):
        base_model_id = self.model_cb.currentText()
        if base_model_id == IMAGEN4_FAST:
            base_model_id = IMAGEN4_ULTRA
        if base_model_id not in (IMAGEN4_ULTRA, IMAGEN4_STD, GEMINI_FLASH_IMAGE):
            base_model_id = IMAGEN4_ULTRA
        return base_model_id
    
    def get_aspect_ratio(self):
        ar = self.ar_cb.currentText()
        if ar not in ("16:9", "9:16", "3:4", "4:3", "1:1"):
            ar = "16:9"
        return ar
    
    def get_image_size(self):
        return "2K"
    
    def get_n_images(self):
        return int(self.count_cb.currentText())
    
    def get_max_retries(self):
        return max(1, int(self.retry_spin.value()))
    
    def get_auto_retry(self):
        return bool(self.auto_retry_cb.isChecked())
    
    def get_person_gen(self):
        return self.person_cb.currentText()
    
    def save_bytes_list(self, row_idx: int, bytes_list: List[bytes]) -> List[Path]:
        saved = []
        local_idx = 0
        for b in bytes_list:
            local_idx += 1
            fname = f"{row_idx:02d}_{local_idx:02d}.png"
            out = self.output_dir / fname
            with open(out, "wb") as f:
                f.write(b)
            saved.append(out)
        return saved
    
    def load_gemini_keys_from_server(self):
        """Load Gemini API keys from Admin Panel server"""
        if not self.api_client or not self.api_client.is_authenticated():
            self.set_status("❌ Not connected to server. Using fallback key.")
            print("❌ Not authenticated. Cannot load Gemini keys from server.")
            return
        
        self.set_status("☁️ Loading Gemini keys from server...")
        print("☁️ Loading Gemini API keys from server...")
        
        try:
            keys_data = self.api_client.get_gemini_keys()
            
            if not keys_data:
                self.set_status("⚠️ No Gemini keys found on server")
                print("⚠️ No Gemini keys found on server or failed to load")
                return
            
            # Extract and clean API keys from the data
            # keys_data is a list of dict like: [{'id': 1, 'api_key': 'AIza...', 'name': '...', 'status': 'active'}]
            api_keys = []
            for item in keys_data:
                raw_key = item.get('api_key', '')
                # Clean key: trim, remove newlines, tabs, and any whitespace
                clean_key = raw_key.strip().replace('\r', '').replace('\n', '').replace('\t', '').replace(' ', '')
                
                if clean_key:
                    api_keys.append(clean_key)
                    # Debug logging - show first/last 8 chars only
                    print(f"🔑 Loaded key {item.get('id')}: {clean_key[:8]}...{clean_key[-8:]} (length: {len(clean_key)})")
            
            if not api_keys:
                self.set_status("⚠️ No valid Gemini keys found")
                print("⚠️ No valid API keys extracted from server data")
                return
            
            # Update the key rotator with server keys
            self.rotator = KeyRotator(api_keys)
            
            key_count = len(api_keys)
            self.set_status(f"✅ Loaded {key_count} Gemini keys from server")
            print(f"✅ Loaded {key_count} Gemini API keys from server successfully")
            print(f"📝 Keys are ready for use. First key starts with: {api_keys[0][:12]}...")
            
            # Show message to user
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Success",
                f"✅ Loaded {key_count} Gemini API keys from server!\n\n"
                f"Keys are ready for image generation.\n"
                f"🔒 Keys are stored securely in memory."
            )
            
        except Exception as e:
            self.set_status(f"❌ Failed to load Gemini keys: {str(e)}")
            print(f"❌ Error loading Gemini keys from server: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main function - chỉ dùng khi chạy standalone"""
    app = QApplication([])
    
    # Modern font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Create as main window when standalone
    window = QMainWindow()
    window.setWindowTitle(f"{APP_TITLE} {APP_VERSION}")
    window.resize(1600, 900)
    
    # Add widget
    tab = ImageGeneratorTab()
    window.setCentralWidget(tab)
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
