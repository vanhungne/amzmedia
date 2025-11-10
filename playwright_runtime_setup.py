"""
Playwright Runtime Setup for Packaged App
Thêm đoạn code này vào đầu file GenVideoPro_v2.py của bạn (sau imports)
"""

import sys
import os
from pathlib import Path

# ========== Detect if running as packaged app (PyInstaller) ==========
if getattr(sys, 'frozen', False):
    # Running as packaged executable
    APP_DIR = Path(sys.executable).parent
    
    # Try to find bundled ms-playwright browsers
    # Priority order:
    # 1. _internal/ms-playwright (primary bundle location)
    # 2. ms-playwright (in temp _MEIPASS folder)
    # 3. _external/ms-playwright (manual copy fallback)
    
    base = Path(getattr(sys, "_MEIPASS", APP_DIR))
    
    possible_paths = [
        APP_DIR / "_internal" / "ms-playwright",   # Primary bundle location
        base / "ms-playwright",                     # Temp _MEIPASS location
        APP_DIR / "_external" / "ms-playwright",   # Manual fallback
    ]
    
    for mp in possible_paths:
        if mp.exists():
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(mp)
            print(f"[OK] Found Playwright browsers at: {mp}")
            break
    else:
        print("[WARNING] Playwright browsers not found in bundle")
        print("          App may attempt to download browsers on first run")
else:
    # Running in development mode
    print("[INFO] Running in development mode (not packaged)")

# ========== Verify Playwright setup ==========
def verify_playwright_setup():
    """
    Call this function early in your app startup to verify Playwright is ready
    Optional: set show_dialog=True to show GUI message if browsers missing
    """
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            try:
                # Quick test launch
                browser = p.chromium.launch(headless=True)
                browser.close()
                print("[OK] Playwright browsers are ready!")
                return True
            except Exception as e:
                print(f"[ERROR] Playwright browser launch failed: {e}")
                return False
                
    except ImportError:
        print("[ERROR] Playwright not installed!")
        return False
    except Exception as e:
        print(f"[ERROR] Playwright setup error: {e}")
        return False

# ========== Usage Example ==========
if __name__ == "__main__":
    print("Testing Playwright setup...")
    if verify_playwright_setup():
        print("✅ All good! Playwright is ready to use.")
    else:
        print("❌ Playwright setup failed. Check errors above.")









