@echo off
echo ============================================
echo    WorkFlow Tool - Folder Build
echo ============================================
echo.
echo This will build a FOLDER (not single exe)
echo with Playwright browsers included.
echo.
pause

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    pause
    exit /b 1
)

REM Install dependencies
echo.
echo [1/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)

REM Install Playwright browsers
echo.
echo [2/4] Installing Playwright browsers...
playwright install chromium
if errorlevel 1 (
    echo [ERROR] Failed to install Playwright!
    pause
    exit /b 1
)

REM Clean previous build
echo.
echo [3/4] Building executable (FOLDER mode)...
if exist dist\WorkFlowTool rmdir /s /q dist\WorkFlowTool
if exist build rmdir /s /q build

REM Build with PyInstaller (ONEDIR)
pyinstaller --name="WorkFlowTool" ^
    --onedir ^
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

REM Copy browsers
echo.
echo [4/4] Copying Playwright browsers...
python copy_browsers.py

echo.
echo ============================================
echo      BUILD COMPLETE!
echo ============================================
echo.
echo Executable: dist\WorkFlowTool\WorkFlowTool.exe
echo.
echo To distribute:
echo   1. Copy ENTIRE "dist\WorkFlowTool" folder
echo   2. Run WorkFlowTool.exe from that folder
echo.
pause




