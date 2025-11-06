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
if exist dist\WorkFlowTool rmdir /s /q dist\WorkFlowTool
if exist build rmdir /s /q build

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
echo [5/5] Copying Playwright browsers...
echo ============================================

REM Find Playwright browsers location
for /f "tokens=*" %%i in ('python -c "import os; from playwright.sync_api import sync_playwright; p = sync_playwright().start(); print(os.path.dirname(p.chromium.executable_path)); p.stop()"') do set BROWSER_PATH=%%i

echo Browser location: %BROWSER_PATH%

REM Copy browsers to dist folder
if exist "%BROWSER_PATH%" (
    echo Copying browsers to dist folder...
    
    REM Get parent directory (ms-playwright folder)
    for %%i in ("%BROWSER_PATH%") do set PLAYWRIGHT_DIR=%%~dpi
    
    REM Remove trailing backslash and go up one level
    set PLAYWRIGHT_DIR=%PLAYWRIGHT_DIR:~0,-1%
    for %%i in ("%PLAYWRIGHT_DIR%") do set PLAYWRIGHT_DIR=%%~dpi
    set PLAYWRIGHT_DIR=%PLAYWRIGHT_DIR:~0,-1%
    
    echo Copying from: %PLAYWRIGHT_DIR%
    
    REM Copy entire ms-playwright folder to _external
    if exist "%PLAYWRIGHT_DIR%" (
        mkdir "dist\WorkFlowTool\_external" 2>nul
        xcopy "%PLAYWRIGHT_DIR%" "dist\WorkFlowTool\_external\ms-playwright\" /E /I /Y /Q
        
        if errorlevel 1 (
            echo [WARNING] Failed to copy browsers automatically
            echo You may need to copy browsers manually later
        ) else (
            echo [OK] Browsers copied successfully!
        )
    ) else (
        echo [WARNING] Playwright directory not found at: %PLAYWRIGHT_DIR%
    )
) else (
    echo [WARNING] Browser executable not found!
    echo The application may need to download browsers on first run
)

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



