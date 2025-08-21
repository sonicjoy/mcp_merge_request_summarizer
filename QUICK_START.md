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

### Claude Desktop Setup (30 seconds)
1. Open Claude Desktop
2. Go to Settings → MCP Servers
3. Add new server with this configuration:
```json
{
    "mcpServers": {
        "merge-request-summarizer": {
            "command": "python",
            "args": ["-m", "mcp_mr_summarizer.server"]
        }
    }
}
```
4. Restart Claude Desktop

## ✅ Test Your Installation

1. Open a terminal in your git repository
2. Run: `python -m mcp_mr_summarizer.cli --help`
3. You should see the help output

## 🎯 First Use

### Tools (Actions)
1. In your editor, ask the AI: "Generate a merge request summary for my current branch"
2. The AI will use the MCP tool to analyze your git history
3. You'll get a comprehensive merge request summary!

### Resources (Data)
You can also access git data directly:
- "Show me the repository status"
- "List all branches in this repository"
- "Show me the commit history between develop and main"
- "What files have changed between these branches?"

## 📋 Available Tools and Resources

### Tools
- **`generate_merge_request_summary`** - Generate comprehensive merge request summaries
- **`analyze_git_commits`** - Analyze git commits and categorize them by type

### Resources
- **`git://repo/status`** - Current repository status and information
- **`git://commits/{base}..{current}`** - Commit history between branches
- **`git://branches`** - List of all repository branches
- **`git://files/changed/{base}..{current}`** - Files changed between branches

## 🆘 Need Help?

- Check the `configs/README.md` for detailed configuration options
- See the main `README.md` for full documentation
- Run `python -m mcp_mr_summarizer.cli --help` for command-line options

## 🔧 Troubleshooting

**"Command not found" error?**
- Make sure you ran the installation script
- Try: `pip list | grep mcp-merge-request-summarizer`
- Use: `python -m mcp_mr_summarizer.server` instead

**Editor not recognizing the MCP?**
- Restart your editor after configuration
- Check that the JSON syntax is correct
- Verify the command path in your settings

**Python version issues?**
- This tool requires Python 3.10 or higher
- Check your version: `python --version`

**Still having issues?**
- Check the full `README.md` for detailed troubleshooting
- Open an issue on GitHub with your error details
