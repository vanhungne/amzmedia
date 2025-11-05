@echo off
echo ============================================
echo    WorkFlow Tool - Production Build
echo ============================================
echo.

set BUILD_VERSION=%date:~-4,4%%date:~-7,2%%date:~-10,2%
set BUILD_DIR=dist\WorkFlowTool-v%BUILD_VERSION%

echo Build Version: %BUILD_VERSION%
echo.

REM Clean previous builds
echo [0/6] Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist %BUILD_DIR% rmdir /s /q %BUILD_DIR%

REM Install Python dependencies
echo [1/6] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install Python dependencies!
    pause
    exit /b 1
)

REM Install PyInstaller
echo [2/6] Installing PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo [ERROR] Failed to install PyInstaller!
    pause
    exit /b 1
)

REM Build Admin Panel
echo [3/6] Building Admin Panel...
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

REM Create distribution structure
echo [4/6] Creating distribution structure...
mkdir dist
mkdir %BUILD_DIR%
mkdir %BUILD_DIR%\admin-panel
mkdir %BUILD_DIR%\image

REM Build executable
echo [5/6] Building executable...
pyinstaller --name="WorkFlowTool" ^
    --onefile ^
    --windowed ^
    --add-data "image;image" ^
    --add-data "admin-panel\.next;admin-panel\.next" ^
    --add-data "admin-panel\public;admin-panel\public" ^
    --hidden-import=PIL ^
    --hidden-import=requests ^
    --hidden-import=cryptography ^
    --collect-all PySide6 ^
    --clean ^
    GenVideoPro.py

if errorlevel 1 (
    echo [ERROR] Failed to build executable!
    pause
    exit /b 1
)

REM Copy files to distribution
echo [6/6] Packaging distribution...
copy dist\WorkFlowTool.exe %BUILD_DIR%\
xcopy /E /I /Y admin-panel\.next %BUILD_DIR%\admin-panel\.next
xcopy /E /I /Y admin-panel\public %BUILD_DIR%\admin-panel\public
xcopy /E /I /Y image %BUILD_DIR%\image

REM Create README
echo Creating README...
(
echo WorkFlow Tool v%BUILD_VERSION%
echo Build Date: %date% %time%
echo.
echo Installation:
echo 1. Extract all files to a folder
echo 2. Run WorkFlowTool.exe
echo.
echo Requirements:
echo - Windows 10 or later
echo - Internet connection for Admin Panel
echo.
echo For support, visit: https://github.com/vanhungne/amzmedia
) > %BUILD_DIR%\README.txt

echo.
echo ============================================
echo [SUCCESS] Production build completed!
echo ============================================
echo.
echo Distribution folder: %BUILD_DIR%
echo Executable: %BUILD_DIR%\WorkFlowTool.exe
echo.
echo Ready to distribute!
echo.
pause

