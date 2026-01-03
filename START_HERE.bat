@echo off
echo ============================================
echo Document Indexing Gateway
echo Professional Document Processing System
echo ============================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed
    echo.
    echo Please install Python 3.7+ from python.org
    pause
    exit /b 1
)

echo Starting Document Indexing Gateway...
echo.

python aveva_gateway_gui_complete.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to start
    echo Check that aveva_gateway_gui_complete.py is present
)

pause
