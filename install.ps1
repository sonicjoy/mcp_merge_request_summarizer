# MCP Merge Request Summarizer Installation Script for PowerShell

Write-Host "Installing MCP Merge Request Summarizer..." -ForegroundColor Green
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.10 or higher from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if pip is available
try {
    $pipVersion = pip --version 2>&1
    Write-Host "Found pip: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: pip is not available" -ForegroundColor Red
    Write-Host "Please ensure pip is installed with Python" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Installing package in development mode..." -ForegroundColor Yellow
pip install -e .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to install package" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Installation completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Configure your MCP client (VSCode/Cursor) using the config files in the 'configs' folder" -ForegroundColor White
Write-Host "2. Restart your editor" -ForegroundColor White
Write-Host "3. Test the installation by running: python -m mcp_mr_summarizer.cli --help" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to continue"
