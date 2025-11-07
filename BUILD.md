# 🚀 WorkFlow Tool - Build Guide

## Quick Start

### Build Executable (One Command!)

```bash
build-simple.bat
```

That's it! The script will automatically:
1. ✅ Install all Python dependencies
2. ✅ Install Playwright browsers
3. ✅ Check PyInstaller
4. ✅ Build executable file

### Output

After successful build, you'll find:
- **Executable**: `dist/WorkFlowTool.exe`
- Ready to run or distribute!

---

## Requirements

- **Python 3.8+** installed on your system
- Internet connection (for first-time setup)

---

## First Run Notes

### Installation Time
- **First run**: May take 5-10 minutes (downloading Playwright browsers ~100-200MB)
- **Subsequent runs**: Much faster (only compiling)

### What Gets Downloaded
1. Python packages from `requirements.txt`:
   - PySide6 (GUI framework)
   - Playwright (browser automation)
   - Requests, Cryptography, Pillow, etc.

2. Playwright Chromium browser (~100MB)

---

## Build Process

```
============================================
   WorkFlow Tool - Build Script
============================================

This script will:
  1. Install Python dependencies
  2. Install Playwright browsers
  3. Build executable file

[1/4] Installing Python dependencies...
[OK] All dependencies installed!

[2/4] Installing Playwright browsers
[OK] Playwright browsers ready!

[3/4] Checking PyInstaller...
[OK] PyInstaller is already installed!

[4/4] Building executable...
Compiling with PyInstaller...

============================================
     [SUCCESS] Build completed!
============================================

Executable location:
  > dist\WorkFlowTool.exe

File size:
  > ~150MB (approximately)

You can now run the executable or distribute it!
```

---

## Troubleshooting

### Error: Python not found
```bash
# Install Python from:
https://www.python.org/downloads/
```

### Error: Playwright browsers failed
```bash
# Run manually:
playwright install chromium
```

### Clean Build
If you encounter issues, delete these folders and rebuild:
```bash
rmdir /s /q dist
rmdir /s /q build
build-simple.bat
```

---

## Manual Run (Without Building)

```bash
# Install dependencies first
pip install -r requirements.txt
playwright install chromium

# Run directly
python GenVideoPro.py
```

---

## File Structure

```
WorkFlow/
├── build-simple.bat          ← Run this to build!
├── requirements.txt          ← Python dependencies
├── GenVideoPro.py           ← Main application
├── login_dialog.py          ← Login UI
├── elevenlabs_key_manager.py ← Key management
├── logo.ico                 ← App icon
├── dist/
│   └── WorkFlowTool.exe     ← Built executable (after build)
└── build/                   ← Temp build files
```

---

## 💡 Tips

- **First build takes longer** - Be patient!
- **Keep `requirements.txt` updated** - Ensures all dependencies are installed
- **Run as administrator** if you encounter permission errors
- **Antivirus may flag** the exe initially - Add to whitelist if needed

---

Made with ❤️ by AMZ Team



















