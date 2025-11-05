@echo off
echo ============================================
echo    WorkFlow Tool - Simple Build (Python Only)
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    pause
    exit /b 1
)

REM Install dependencies
echo [1/4] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)

REM Install Playwright browsers
echo [2/4] Installing Playwright browsers...
playwright install chromium
if errorlevel 1 (
    echo [WARNING] Failed to install Playwright browsers. Will try to continue...
)

REM Install PyInstaller if not exists
echo [3/4] Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Clean
echo Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

REM Create image folder if not exists (empty folder is OK)
if not exist image mkdir image

REM Build executable
echo [4/4] Building executable...
pyinstaller --name="WorkFlowTool" ^
    --onefile ^
    --windowed ^
    --icon=logo.ico ^
    --hidden-import=requests ^
    --hidden-import=cryptography ^
    --hidden-import=PIL ^
    --hidden-import=PIL.Image ^
    --hidden-import=playwright ^
    --hidden-import=playwright.sync_api ^
    --collect-all PySide6 ^
    --collect-all playwright ^
    --clean ^
    GenVideoPro.py

if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo [SUCCESS] Build completed!
echo ============================================
echo Executable: dist\WorkFlowTool.exe
echo.
pause

