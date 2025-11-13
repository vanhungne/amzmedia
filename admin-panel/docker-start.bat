@echo off
echo ====================================
echo Starting Admin Panel with Docker
echo ====================================
echo.

echo Building and starting containers...
docker-compose up -d --build

echo.
echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo.
echo ====================================
echo Admin Panel is starting!
echo ====================================
echo.
echo Access at: http://localhost:3000
echo Default login:
echo   Username: admin
echo   Password: admin123
echo.
echo To view logs: docker-compose logs -f
echo To stop: docker-compose down
echo.

pause

