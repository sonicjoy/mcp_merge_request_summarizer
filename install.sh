#!/bin/bash

echo "Installing MCP Merge Request Summarizer..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not available"
    echo "Please ensure pip is installed with Python"
    exit 1
fi

echo "Installing package in development mode..."
pip3 install -e .

if [ $? -ne 0 ]; then
    echo "Error: Failed to install package"
    exit 1
fi

echo
echo "Installation completed successfully!"
echo
echo "Next steps:"
echo "1. Configure your MCP client (VSCode/Cursor) using the config files in the 'configs' folder"
echo "2. Restart your editor"
echo "3. Test the installation by running: python -m mcp_mr_summarizer.cli --help"
echo
