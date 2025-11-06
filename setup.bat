@echo off
echo ============================================
echo    Quick Setup - WorkFlow Tool
echo ============================================
echo.
echo Installing dependencies only (no build)...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    pause
    exit /b 1
)

REM Install Python packages
echo [1/2] Installing Python packages...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install packages!
    pause
    exit /b 1
)
echo [OK] Python packages installed!

REM Install Playwright browsers
echo.
echo [2/2] Installing Playwright browsers...
echo This downloads ~100MB, may take a few minutes...
playwright install chromium
if errorlevel 1 (
    echo [ERROR] Failed to install Playwright browsers!
    pause
    exit /b 1
)

REM Verify
echo.
echo Verifying installation...
python -c "from playwright.sync_api import sync_playwright; import PySide6; import requests; print('✅ All packages working!')"
if errorlevel 1 (
    echo [WARNING] Verification failed!
) else (
    echo [OK] Setup complete!
)

echo.
echo ============================================
echo [SUCCESS] Setup completed!
echo ============================================
echo.
echo You can now run:
echo   python GenVideoPro.py
echo.
echo Or build executable:
echo   build-simple.bat
echo.
pause




