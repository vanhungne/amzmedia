@echo off
echo ============================================
echo    Building Admin Panel Only
echo ============================================
echo.

cd admin-panel

echo [1/2] Installing dependencies...
call npm install
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies!
    cd ..
    pause
    exit /b 1
)

echo [2/2] Building production...
call npm run build
if errorlevel 1 (
    echo [ERROR] Failed to build!
    cd ..
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Admin Panel built successfully!
echo.
echo Build output: admin-panel\.next
echo To run: cd admin-panel && npm run start
echo.
cd ..
pause

