@echo off
setlocal enabledelayedexpansion

rem --- luôn chạy tại thư mục script ---
cd /d "%~dp0"

rem --- tạo venv nếu chưa có (không tạo lại nếu đã tồn tại) ---
if not exist ".venv" (
  py -3.13 -m venv .venv
)

rem --- dùng python trong venv, không phụ thuộc activate ---
set PYVENV="%CD%\.venv\Scripts\python.exe"

rem --- xác thực python đúng venv ---
%PYVENV% -c "import sys;print('Python:',sys.version);print('Exec:',sys.executable)" || goto :fail

rem --- cập nhật công cụ build ---
echo [1/6] Updating pip, wheel, setuptools...
%PYVENV% -m pip install -U pip wheel setuptools || goto :fail

rem --- cài deps (nếu bạn có requirements.txt thì thêm vào) ---
if exist requirements.txt (
  echo [2/6] Installing requirements.txt...
  %PYVENV% -m pip install -r requirements.txt || goto :fail
)

rem --- cài các gói cần cho build ---
echo [3/6] Installing build dependencies...
%PYVENV% -m pip install requests PyInstaller PySide6 playwright cryptography || goto :fail

rem --- cài browser cho playwright ---
echo [4/6] Installing Playwright Chromium browser...
%PYVENV% -m playwright install chromium || goto :fail

rem --- Detect ms-playwright root directory ---
echo [5/6] Detecting ms-playwright browsers location...
for /f "tokens=*" %%i in ('%PYVENV% -c "from pathlib import Path; from playwright.sync_api import sync_playwright; p=sync_playwright().start(); exe=Path(p.chromium.executable_path); p.stop(); root=exe; 
while root and root.name.lower()!='ms-playwright' and root.parent!=root: root=root.parent; 
print(str(root) if root.name.lower()=='ms-playwright' else '')"') do set PLAYWRIGHT_MS_ROOT=%%i

if not defined PLAYWRIGHT_MS_ROOT (
    echo [WARNING] Could not detect ms-playwright via Python. Trying LOCALAPPDATA fallback...
    set PLAYWRIGHT_MS_ROOT=%LOCALAPPDATA%\ms-playwright
)

echo Detected ms-playwright root: %PLAYWRIGHT_MS_ROOT%

if not exist "%PLAYWRIGHT_MS_ROOT%" (
    echo [ERROR] ms-playwright not found. Cannot bundle browsers.
    goto :fail
)

rem --- Export environment variable for spec file ---
set PLAYWRIGHT_MS_ROOT=%PLAYWRIGHT_MS_ROOT%

rem --- (tuỳ chọn) dọn build/dist cũ ---
echo [6/6] Building with PyInstaller...
if exist build rmdir /s /q build
if exist dist  rmdir /s /q dist

rem --- build bằng PyInstaller (qua -m) ---
%PYVENV% -m PyInstaller --clean --noconfirm veogen.spec || goto :fail

echo.
echo ============================================
echo      [SUCCESS] Build completed!
echo ============================================
echo.
echo Executable location:
echo   ^> dist\VeoProGen\VeoProGen.exe
echo.
echo To distribute:
echo   - Copy entire "dist\VeoProGen" folder
echo   - Run VeoProGen.exe from that folder
echo.

goto :end

:fail
echo.
echo [ERROR] Build failed. Xem log ở trên (bước lỗi gần nhất).
pause
exit /b 1

:end
pause




