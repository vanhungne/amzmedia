@echo off
echo ============================================
echo    WorkFlow Tool - Build with Browsers
echo ============================================
echo.
echo This script will:
echo   1. Install Python dependencies
echo   2. Install Playwright browsers
echo   3. Build executable with browser bundle
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)
python --version
echo [OK] Python is installed!

REM Install dependencies
echo.
echo ============================================
echo [1/5] Installing Python dependencies...
echo ============================================
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)
echo [OK] All dependencies installed!

REM Install Playwright browsers
echo.
echo ============================================
echo [2/5] Installing Playwright browsers
echo ============================================
echo This may take a few minutes on first run...
echo.

REM Always install/update chromium to ensure it's available
echo Installing Chromium browser (required for automation)...
playwright install chromium
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install Playwright Chromium browser!
    pause
    exit /b 1
)

REM Verify installation
echo Verifying Playwright installation...
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); p.chromium.launch(headless=True); p.stop()" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [WARNING] Playwright verification failed!
    echo Build will continue, but runtime errors may occur.
    echo.
) else (
    echo [OK] Playwright browsers ready and verified!
)

REM Install PyInstaller if not exists
echo.
echo ============================================
echo [3/5] Checking PyInstaller...
echo ============================================
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found, installing...
    pip install pyinstaller
) else (
    echo [OK] PyInstaller is already installed!
)

REM Clean
echo.
echo ============================================
echo [4/5] Building executable...
echo ============================================
echo Cleaning previous builds...
REM Ensure no running instance is locking files
taskkill /IM WorkFlowTool.exe /F >nul 2>&1
REM Give Windows a moment to release handles
timeout /t 2 /nobreak >nul

if exist dist\WorkFlowTool rmdir /s /q dist\WorkFlowTool
if exist build rmdir /s /q build
REM If deletion failed due to attributes, force-clear attributes and retry once
if exist dist\WorkFlowTool (
    attrib -R -H -S /S /D dist\WorkFlowTool 2>nul
    rmdir /s /q dist\WorkFlowTool
)

REM Create image folder if not exists (empty folder is OK)
if not exist image mkdir image

echo.
echo Compiling with PyInstaller (ONEDIR mode)...
echo This may take several minutes, please wait...

REM Build in ONEDIR mode (not ONEFILE)
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
    echo.
    echo ============================================
    echo [ERROR] Build failed!
    echo ============================================
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ============================================
echo [5/5] Bundling Playwright browsers...
echo ============================================

REM Find ms-playwright root directory (parent of all browser folders)
for /f "tokens=*" %%i in ('python -c "import os; print(os.path.join(os.environ.get('LOCALAPPDATA', ''), 'ms-playwright'))"') do set MS_PLAYWRIGHT_ROOT=%%i

echo ms-playwright root: %MS_PLAYWRIGHT_ROOT%

REM Verify ms-playwright directory exists
if not exist "%MS_PLAYWRIGHT_ROOT%" (
    echo [ERROR] ms-playwright directory not found at: %MS_PLAYWRIGHT_ROOT%
    echo [INFO] Installing Chromium browser now...
    playwright install chromium
    if errorlevel 1 (
        echo [ERROR] Failed to install Playwright Chromium.
        pause
        exit /b 1
    )
)

REM Verify at least one chromium folder exists
dir /b "%MS_PLAYWRIGHT_ROOT%\chromium-*" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No chromium-* folder found in: %MS_PLAYWRIGHT_ROOT%
    echo [INFO] Installing Chromium browser now...
    playwright install chromium
    if errorlevel 1 (
        echo [ERROR] Failed to install Playwright Chromium.
        pause
        exit /b 1
    )
    REM Verify again
    dir /b "%MS_PLAYWRIGHT_ROOT%\chromium-*" >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Still no chromium-* folder after install. Build cannot proceed.
        pause
        exit /b 1
    )
)

echo [OK] Found Chromium browsers in: %MS_PLAYWRIGHT_ROOT%

REM Create _internal folder
mkdir "dist\WorkFlowTool\_internal" 2>nul

REM Copy entire ms-playwright folder to _internal/ms-playwright
echo Copying all browsers from ms-playwright...
xcopy "%MS_PLAYWRIGHT_ROOT%\*" "dist\WorkFlowTool\_internal\ms-playwright\" /E /I /Y /Q

if errorlevel 1 (
    echo [ERROR] Failed to copy browsers to _internal\ms-playwright
    echo Source: %MS_PLAYWRIGHT_ROOT%
    echo Dest: dist\WorkFlowTool\_internal\ms-playwright
    pause
    exit /b 1
)

REM Verify copy succeeded
dir /b "dist\WorkFlowTool\_internal\ms-playwright\chromium-*" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Copy completed but chromium-* folder not found in _internal\ms-playwright
    pause
    exit /b 1
)

echo [OK] Browsers bundled successfully in _internal\ms-playwright

echo.
echo ============================================
echo      [SUCCESS] Build completed!
echo ============================================
echo.
echo Executable location:
echo   ^> dist\WorkFlowTool\WorkFlowTool.exe
echo.
echo To distribute:
echo   - Copy entire "dist\WorkFlowTool" folder
echo   - Run WorkFlowTool.exe from that folder
echo.
echo Folder size:
for /f "usebackq" %%A in (`dir /s /a "dist\WorkFlowTool" ^| find "bytes"`) do set SIZE_INFO=%%A
echo   ^> Check dist\WorkFlowTool folder
echo.
pause












