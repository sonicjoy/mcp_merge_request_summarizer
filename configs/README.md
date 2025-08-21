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

1. Open Cursor Settings (Ctrl/Cmd + ,)
2. Search for "mcp"
3. Click "Edit in settings.json"
4. Copy the contents of `cursor_settings.json` into your settings.json
5. Restart Cursor

### For Claude Desktop Users

1. Open Claude Desktop
2. Go to Settings → MCP Servers
3. Add a new server configuration
4. Copy the contents of `claude_desktop_config.json` into the configuration
5. Restart Claude Desktop

## Manual Configuration

If you prefer to configure manually, here are the key settings:

### VSCode/Cursor
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

## Troubleshooting

### Command Not Found
If you get a "command not found" error:
1. Make sure you've run the installation script (`install.bat` on Windows or `install.sh` on Unix)
2. Verify the package is installed: `pip list | grep mcp-merge-request-summarizer`
3. Try using the module approach: `python -m mcp_mr_summarizer.server`

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
