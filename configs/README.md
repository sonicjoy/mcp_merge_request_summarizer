# MCP Configuration Files

This folder contains ready-to-use configuration files for different MCP clients.

## Quick Setup Guide

### For VSCode Users

1. Open VSCode Settings (Ctrl/Cmd + ,)
2. Search for "mcp"
3. Click "Edit in settings.json"
4. Copy the contents of `vscode_settings.json` into your settings.json
5. Restart VSCode

### For Cursor Users

1. Open **Cursor Settings** from the main menu bar
2. Go to **Tools & Integrations**
3. Click **New MCP Server**
4. Add this configuration in the json file:
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
6. Restart Cursor

**Note:** Cursor uses a GUI interface, so the `cursor_settings.json` file is mainly for reference. Use the GUI steps above instead.

### For Claude Desktop Users

1. Open Claude Desktop
2. Go to Settings → MCP Servers
3. Add a new server configuration
4. Copy the contents of `claude_desktop_config.json` into the configuration
5. Restart Claude Desktop

## Manual Configuration

If you prefer to configure manually, here are the key settings:

### VSCode
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

### Cursor
```mcp.json
{
    "mcpServers": {
        "merge-request-summarizer": {
            "command": "python",
            "args": ["-m", "mcp_mr_summarizer.server"]
        }
    }
}
```

### Claude Desktop
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

## Important Notes

### Works from Any Directory
Once installed, the MCP server works from any directory. You don't need to be in the project directory to use it.

### Installation Required
Make sure you've run the installation script first:
- **Windows:** `install.bat` or `install.ps1`
- **Mac/Linux:** `./install.sh`

## Troubleshooting

### Command Not Found
If you get a "command not found" error:
1. Make sure you've run the installation script (`install.bat` on Windows or `install.sh` on Unix)
2. Verify the package is installed: `pip list | grep mcp-merge-request-summarizer`
3. Try using the module approach: `python -m mcp_mr_summarizer.server`

### MCP Not Found in Editor
If your editor doesn't recognize the MCP:
1. **Restart your editor** after adding the configuration
2. **Check JSON syntax** - make sure it's valid JSON
3. **Verify the command path** - the configuration should use `python -m mcp_mr_summarizer.server`
4. **Test the command manually** - run `python -m mcp_mr_summarizer.cli --help` to verify installation

### Permission Issues
On Unix systems, you might need to make the installation script executable:
```bash
chmod +x install.sh
```

### Python Path Issues
If Python is not in your PATH, you can use the full path to Python in the configuration:
```json
{
    "mcp.servers": {
        "merge-request-summarizer": {
            "command": "/usr/bin/python3",
            "args": ["-m", "mcp_mr_summarizer.server"]
        }
    }
}
```

### Testing the Installation
To verify everything is working:
1. Run: `python -m mcp_mr_summarizer.cli --help`
2. Run: `python -m mcp_mr_summarizer.cli status` (in a git repository)
3. Check that your editor shows the MCP tools and resources
