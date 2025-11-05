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
echo [1/3] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)

REM Install PyInstaller if not exists
echo [2/3] Checking PyInstaller...
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
echo [3/3] Building executable...
pyinstaller --name="WorkFlowTool" ^
    --onefile ^
    --windowed ^
    --hidden-import=requests ^
    --hidden-import=cryptography ^
    --hidden-import=PIL ^
    --hidden-import=PIL.Image ^
    --collect-all PySide6 ^
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

