@echo off
echo ============================================
echo    WorkFlow Tool - Python Build Only
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    pause
    exit /b 1
)

echo [1/4] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install Python dependencies!
    pause
    exit /b 1
)

echo [2/4] Installing PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller!
        pause
        exit /b 1
    )
)

echo [3/4] Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist WorkFlowTool.spec del WorkFlowTool.spec

echo [4/4] Building Python executable...
pyinstaller --name="WorkFlowTool" ^
    --onefile ^
    --windowed ^
    --add-data "image;image" ^
    --hidden-import=PIL ^
    --hidden-import=PIL.Image ^
    --hidden-import=requests ^
    --hidden-import=cryptography ^
    --hidden-import=PySide6.QtCore ^
    --hidden-import=PySide6.QtGui ^
    --hidden-import=PySide6.QtWidgets ^
    --hidden-import=PySide6.QtMultimedia ^
    --hidden-import=PySide6.QtMultimediaWidgets ^
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
echo.
echo Executable location: dist\WorkFlowTool.exe
echo File size: 
dir dist\WorkFlowTool.exe | findstr WorkFlowTool.exe
echo.
echo Ready to use!
echo.
pause

