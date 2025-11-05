@echo off
echo ============================================
echo    WorkFlow Tool - Build Script
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH!
    pause
    exit /b 1
)

echo [1/5] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install Python dependencies!
    pause
    exit /b 1
)

echo [2/5] Installing PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo [ERROR] Failed to install PyInstaller!
    pause
    exit /b 1
)

echo [3/5] Building Admin Panel...
cd admin-panel
call npm install
if errorlevel 1 (
    echo [ERROR] Failed to install npm dependencies!
    cd ..
    pause
    exit /b 1
)

call npm run build
if errorlevel 1 (
    echo [ERROR] Failed to build admin panel!
    cd ..
    pause
    exit /b 1
)
cd ..

echo [4/5] Creating distribution folder...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
mkdir dist
mkdir dist\admin-panel

REM Create image folder if not exists
if not exist image mkdir image

echo [5/5] Building Python executable with PyInstaller...
pyinstaller --name="WorkFlowTool" ^
    --onefile ^
    --windowed ^
    --add-data "admin-panel\.next;admin-panel\.next" ^
    --add-data "admin-panel\public;admin-panel\public" ^
    --hidden-import=PIL ^
    --hidden-import=PIL.Image ^
    --hidden-import=requests ^
    --hidden-import=cryptography ^
    --hidden-import=PySide6.QtCore ^
    --hidden-import=PySide6.QtGui ^
    --hidden-import=PySide6.QtWidgets ^
    --hidden-import=PySide6.QtMultimedia ^
    --collect-all PySide6 ^
    GenVideoPro.py

if errorlevel 1 (
    echo [ERROR] Failed to build executable!
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Build completed!
echo.
echo Executable location: dist\WorkFlowTool.exe
echo.
echo Next steps:
echo 1. Copy dist\WorkFlowTool.exe to target machine
echo 2. Copy admin-panel folder to same location
echo 3. Run WorkFlowTool.exe
echo.
pause

