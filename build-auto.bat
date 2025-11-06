@echo off
echo ============================================
echo    WorkFlow Tool - Auto Build
echo    (Browsers bundled in _internal)
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
echo [1/3] Installing dependencies...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)

REM Install Playwright browsers (required for build)
echo [2/3] Installing Playwright browsers...
playwright install chromium
if errorlevel 1 (
    echo [ERROR] Failed to install Playwright!
    pause
    exit /b 1
)

REM Clean previous build
echo [3/3] Building executable...
if exist dist\WorkFlowTool rmdir /s /q dist\WorkFlowTool
if exist build rmdir /s /q build

REM Build using spec file (will auto-bundle browsers into _internal)
pyinstaller WorkFlowTool.spec --clean

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo      BUILD COMPLETE!
echo ============================================
echo.
echo Executable: dist\WorkFlowTool\WorkFlowTool.exe
echo.
echo Browsers are bundled in: dist\WorkFlowTool\_internal\ms-playwright\
echo.
echo To distribute:
echo   Copy ENTIRE "dist\WorkFlowTool" folder
echo.

REM Check if browsers were bundled
if exist "dist\WorkFlowTool\_internal\ms-playwright" (
    echo [OK] Browsers bundled successfully!
) else (
    echo [WARNING] Browsers not found in _internal!
    echo The app will download browsers on first run.
)

echo.
pause










