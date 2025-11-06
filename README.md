# 🚀 WorkFlow Tool - AMZ Media

Modern workflow automation tool with ElevenLabs integration.

---

## 🎯 Quick Start

### Option 1: Run Directly (Recommended for testing)

```bash
# Setup (first time only)
setup.bat

# Run application
python GenVideoPro.py
```

### Option 2: Build Executable (For distribution)

```bash
# Build (includes setup + compile)
build-simple.bat

# Run built executable
dist\WorkFlowTool.exe
```

---

## 📋 Requirements

- **Python 3.8+** 
- **Internet connection** (for first-time setup)
- **Windows 10/11**

---

## 📦 What's Included

### Files
- `setup.bat` - Quick setup (install dependencies only)
- `build-simple.bat` - Full build (setup + compile to .exe)
- `GenVideoPro.py` - Main application
- `login_dialog.py` - Login interface
- `elevenlabs_key_manager.py` - Key management
- `requirements.txt` - Python dependencies

### Features
- 🎙️ ElevenLabs TTS integration
- 🔐 Server-based authentication
- 📊 Key management system
- 🤖 Browser automation (Playwright)
- 🎨 Modern gradient UI

---

## 🔧 Setup Details

### First Time Setup (~5-10 minutes)

**Automatic setup includes:**
1. Installing Python packages:
   - PySide6 (GUI framework)
   - Playwright (browser automation)
   - Requests, Cryptography, Pillow
   
2. Downloading Playwright Chromium (~100MB)

3. Verifying installation

**What you'll see:**
```
============================================
   Quick Setup - WorkFlow Tool
============================================

[1/2] Installing Python packages...
[OK] Python packages installed!

[2/2] Installing Playwright browsers...
This downloads ~100MB, may take a few minutes...
[OK] Setup complete!

============================================
[SUCCESS] Setup completed!
============================================

You can now run:
  python GenVideoPro.py
```

---

## 🐛 Troubleshooting

### Error: "Executable doesn't exist" (Playwright)

**Solution:**
```bash
# Run setup script
setup.bat

# Or manually:
pip install playwright
playwright install chromium
```

### Error: "Python is not installed"

**Solution:**
1. Download Python from: https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Restart terminal and try again

### Error: "Module not found"

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Build Failed

**Solution:**
```bash
# Clean and rebuild
rmdir /s /q dist
rmdir /s /q build
build-simple.bat
```

---

## 📁 File Structure

```
WorkFlow/
├── 📄 README.md              ← You are here
├── 📄 BUILD.md               ← Build documentation
├── 🔧 setup.bat              ← Quick setup script
├── 🔧 build-simple.bat       ← Build executable script
├── 📋 requirements.txt       ← Python dependencies
│
├── 🐍 GenVideoPro.py         ← Main application
├── 🐍 login_dialog.py        ← Login UI
├── 🐍 elevenlabs_key_manager.py  ← Key management
├── 🐍 tool_api_client.py     ← API client
│
├── 🖼️ logo.ico               ← App icon
├── 📁 image/                 ← Image assets
├── 📁 outputs/               ← Output files
│
└── 📁 admin-panel/           ← Admin web panel
    ├── Next.js app
    ├── API routes
    └── Database integration
```

---

## 🎯 Usage Workflow

### 1. First Run
```bash
setup.bat
```

### 2. Run Application
```bash
python GenVideoPro.py
```

### 3. Login
- Server: `https://amz.io.vn` (default)
- Enter your username and password
- Check "Remember me" for convenience

### 4. Load Keys
- Go to ElevenLabs tab
- Click "Load from Server"
- Keys will be loaded automatically

### 5. Start Working
- Use the tool features
- Keys rotate automatically on failure
- Status syncs with server

---

## 🔐 Server Configuration

Default server: `https://amz.io.vn`

To change server, edit `login_dialog.py`:
```python
DEFAULT_SERVER_URL = "https://amz.io.vn"  # Change this
```

---

## 🚀 Building for Distribution

```bash
# Build executable
build-simple.bat

# Output
dist/WorkFlowTool.exe  (~150MB)

# Distribute
# Copy the .exe file to target computers
# No Python installation needed on target!
```

---

## 💡 Tips

- **First build is slow** - Subsequent builds are faster
- **Antivirus warnings** - Normal for PyInstaller executables, add to whitelist
- **Large file size** - Includes Python runtime + all dependencies
- **Run as admin** - If you encounter permission errors
- **Keep updated** - Pull latest changes regularly

---

## 📞 Support

For issues or questions:
- Check `BUILD.md` for detailed build instructions
- Review error messages carefully
- Ensure Python and all dependencies are installed

---

## 🎨 UI Features

- **Modern gradient design** - Purple/blue gradient background
- **Responsive layout** - Adapts to content
- **Progress animations** - Visual feedback during operations
- **Status indicators** - Real-time status updates

---

Made with ❤️ by AMZ Media Team











