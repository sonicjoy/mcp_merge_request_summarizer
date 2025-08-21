# Quick Start Guide

Get the MCP Merge Request Summarizer up and running in minutes!

## 🚀 One-Click Installation

### Windows Users
1. **Option A:** Double-click `install.bat` (Command Prompt)
2. **Option B:** Right-click `install.ps1` → "Run with PowerShell" (PowerShell)
3. Follow the prompts
4. Configure your editor (see below)

### Mac/Linux Users
1. Open terminal in this directory
2. Run: `chmod +x install.sh && ./install.sh`
3. Configure your editor (see below)

## ⚡ Editor Configuration

### VSCode Setup (30 seconds)
1. Open VSCode Settings (Ctrl + ,)
2. Search for "mcp"
3. Click "Edit in settings.json"
4. Copy this into your settings.json:
```json
{
    "mcp.servers": {
        "merge-request-summarizer": {
            "command": "python",
            "args": ["-m", "mcp_mr_summarizer.server"]
        }
    }
}
```
5. Restart VSCode

### Cursor Setup (30 seconds)
1. Open Cursor Settings (Ctrl + ,)
2. Search for "mcp"
3. Click "Edit in settings.json"
4. Copy this into your settings.json:
```json
{
    "mcp.servers": {
        "merge-request-summarizer": {
            "command": "python",
            "args": ["-m", "mcp_mr_summarizer.server"]
        }
    }
}
```
5. Restart Cursor

## ✅ Test Your Installation

1. Open a terminal in your git repository
2. Run: `python -m mcp_mr_summarizer.cli --help`
3. You should see the help output

## 🎯 First Use

1. In your editor, ask the AI: "Generate a merge request summary for my current branch"
2. The AI will use the MCP tool to analyze your git history
3. You'll get a comprehensive merge request summary!

## 🆘 Need Help?

- Check the `configs/README.md` for detailed configuration options
- See the main `README.md` for full documentation
- Run `python -m mcp_mr_summarizer.cli --help` for command-line options

## 🔧 Troubleshooting

**"Command not found" error?**
- Make sure you ran the installation script
- Try: `pip list | grep mcp-merge-request-summarizer`

**Editor not recognizing the MCP?**
- Restart your editor after configuration
- Check that the JSON syntax is correct
- Verify the command path in your settings

**Still having issues?**
- Check the full `README.md` for detailed troubleshooting
- Open an issue on GitHub with your error details
