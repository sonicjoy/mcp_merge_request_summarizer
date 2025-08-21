@echo off
echo Installing MCP Merge Request Summarizer...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo Installing package in development mode...
pip install -e .

if errorlevel 1 (
    echo Error: Failed to install package
    pause
    exit /b 1
)

echo.
echo Installation completed successfully!
echo.
echo Next steps:
echo 1. Configure your MCP client (VSCode/Cursor) using the config files in the 'configs' folder
echo 2. Restart your editor
echo 3. Test the installation by running: python -m mcp_mr_summarizer.cli --help
echo.
pause
