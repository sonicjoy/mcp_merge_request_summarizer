# Installation Guide

This guide provides multiple ways to install and configure the MCP Merge Request Summarizer for different editors and operating systems.

## 🚀 Quick Installation (Recommended)

### Step 1: Install the Package

**Windows:**
```bash
# Option A: Using batch file
install.bat

# Option B: Using PowerShell
.\install.ps1

# Option C: Manual installation
pip install -e .
```

**Mac/Linux:**
```bash
# Option A: Using shell script
chmod +x install.sh && ./install.sh

# Option B: Manual installation
pip install -e .
```

### Step 2: Configure Your Editor

#### VSCode Configuration
1. Open VSCode Settings (Ctrl + ,)
2. Search for "mcp"
3. Click "Edit in settings.json"
4. Add this configuration:
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

#### Cursor Configuration
1. Open Cursor Settings (Ctrl + ,)
2. Search for "mcp"
3. Click "Edit in settings.json"
4. Add this configuration:
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

#### Claude Desktop Configuration
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

### Step 3: Test Installation

```bash
# Test the CLI
python -m mcp_mr_summarizer.cli --help

# Test the server
python -m mcp_mr_summarizer.server
```

## 📁 Ready-to-Use Configuration Files

Copy the appropriate configuration from the `configs/` folder:

- `configs/vscode_settings.json` - For VSCode
- `configs/cursor_settings.json` - For Cursor
- `configs/claude_desktop_config.json` - For Claude Desktop

## 🔧 Alternative Installation Methods

### Using pip (when published to PyPI)
```bash
pip install mcp-merge-request-summarizer
```

### Development Installation
```bash
git clone https://github.com/yourusername/mcp-merge-request-summarizer.git
cd mcp-merge-request-summarizer
pip install -e .
```

### Using requirements.txt
```bash
pip install -r requirements.txt
```

## 🐛 Troubleshooting

### Common Issues

**1. "Command not found" error**
- Make sure you've run the installation script
- Verify the package is installed: `pip list | grep mcp-merge-request-summarizer`
- Use the module approach: `python -m mcp_mr_summarizer.server`

**2. Python path issues**
If Python is not in your PATH, use the full path:
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

**3. Permission issues (Unix)**
```bash
chmod +x install.sh
./install.sh
```

**4. Editor not recognizing MCP**
- Restart your editor after configuration
- Check JSON syntax in settings
- Verify the command path is correct

**5. Virtual environment issues**
Make sure you're using the correct Python environment:
```bash
# Activate your virtual environment
source venv/bin/activate  # Unix
venv\Scripts\activate     # Windows

# Then install
pip install -e .
```

## 📋 System Requirements

- Python 3.8 or higher
- Git (for git operations)
- pip (for package installation)

## 🎯 First Use

1. Open your configured editor
2. Navigate to a git repository
3. Ask the AI: "Generate a merge request summary for my current branch"
4. The AI will use the MCP tool to analyze your git history and create a comprehensive summary

## 📚 Additional Resources

- `QUICK_START.md` - Quick setup guide
- `configs/README.md` - Detailed configuration options
- `examples/usage_examples.md` - Usage examples
- Main `README.md` - Full documentation

## 🆘 Getting Help

- Check the troubleshooting section above
- Review the configuration files in the `configs/` folder
- Open an issue on GitHub with your error details
- Check the main README for comprehensive documentation
