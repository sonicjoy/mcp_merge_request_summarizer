# MCP Merge Request Summarizer

An MCP (Model Context Protocol) tool that automatically generates comprehensive merge request summaries from git logs. This tool analyzes commit history, categorizes changes, and produces structured summaries suitable for merge request descriptions.

## 🚀 Features

- **Automatic Commit Analysis**: Analyzes git logs between branches to understand changes
- **Smart Categorization**: Categorizes commits by type (features, bug fixes, refactoring, etc.)
- **Comprehensive Summaries**: Generates detailed merge request descriptions with:
  - Overview and statistics
  - Key changes and significant commits
  - Categorized changes (features, bug fixes, refactoring)
  - Breaking changes detection
  - File categorization and impact analysis
  - Estimated review time
- **Multiple Output Formats**: Supports both Markdown and JSON output
- **Flexible Integration**: Works standalone or as MCP server
- **Cross-Platform**: Compatible with Windows, macOS, and Linux

## 📦 Installation

### 🚀 Quick Start (Recommended)
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/mcp-merge-request-summarizer.git
   cd mcp-merge-request-summarizer
   ```

2. **Run the installation script:**
   - **Windows:** Double-click `install.bat` or run `install.bat` in PowerShell
   - **Mac/Linux:** Run `chmod +x install.sh && ./install.sh`

3. **Configure your editor:**
   - See `QUICK_START.md` for 30-second setup instructions
   - Or check `configs/README.md` for detailed configuration options

### Manual Installation
```bash
git clone https://github.com/yourusername/mcp-merge-request-summarizer.git
cd mcp-merge-request-summarizer
pip install -e .
```

### From PyPI
```bash
pip install mcp-merge-request-summarizer
```

**Note**: This package is not yet published to PyPI. For now, use the installation scripts or manual installation.

## 🔧 Usage

### As a Standalone Tool

```bash
# Basic usage (compares current branch against develop)
python -m mcp_mr_summarizer.cli

# Specify different branches
python -m mcp_mr_summarizer.cli --base main --current feature/new-feature

# Output to file
python -m mcp_mr_summarizer.cli --output mr_summary.md

# JSON output
python -m mcp_mr_summarizer.cli --format json --output summary.json

# Help
python -m mcp_mr_summarizer.cli --help
```

### As an MCP Server

1. **Configure your MCP client** (e.g., Claude Desktop, Cursor, VSCode):
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

2. **Use the tools and resources** through your MCP client interface:

### Tools (Actions)
- `generate_merge_request_summary`: Creates full MR summaries
- `analyze_git_commits`: Provides detailed commit analysis

### Resources (Data)
- `git://repo/status`: Current repository status and information
- `git://commits/{base_branch}..{current_branch}`: Commit history between branches
- `git://branches`: List of all repository branches
- `git://files/changed/{base_branch}..{current_branch}`: Files changed between branches

## 📊 Example Output

```markdown
# feat: 4 new features and improvements

## Overview
This merge request contains 9 commits with 35 files changed (1543 insertions, 1485 deletions).

## Key Changes
- Refactor mappers in MLB, NBA, NHL, and NFL to use object initializer syntax (bdf5d9c) - 3028 lines changed
- Refactor season stats services to use base class and improve dependency injection (30de323) - 1976 lines changed

### 🚀 New Features (4)
- Add soccer metrics extraction methods and register soccer season stats service (176930f)
- Update services to use constructor injection for dependencies (29f1c46)
- Update CbStatsDaemon and CbStatsFeedPublicApi to use async host run methods (22c1202)
- Refactor PoolSeasonStatsController and related services (3a28ab4)

### 🔧 Refactoring (3)
- Refactor mappers in MLB, NBA, NHL, and NFL to use object initializer syntax (bdf5d9c)
- Refactor season stats services to use base class and improve dependency injection (30de323)
- Refactor logging in season stats services to use consistent casing (fd7b8b9)

### 📊 Summary
- **Total Commits:** 9
- **Files Changed:** 35
- **Lines Added:** 1543
- **Lines Removed:** 1485
- **Estimated Review Time:** 1h 15m
```

## 🛠️ Configuration

### Quick Configuration (Recommended)

**For VSCode/Cursor:**
1. Open Settings (Ctrl/Cmd + ,)
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

**For Claude Desktop:**
1. Go to Settings → MCP Servers
2. Add new server with this configuration:
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

### Ready-to-Use Config Files

Copy the appropriate configuration from the `configs/` folder:
- `configs/vscode_settings.json` - For VSCode
- `configs/cursor_settings.json` - For Cursor  
- `configs/claude_desktop_config.json` - For Claude Desktop

See `configs/README.md` for detailed setup instructions.

## 🎯 Customization

### Adding Custom Commit Categories

Extend the categorization by modifying the `categorize_commit` method:

```python
def categorize_commit(self, commit: CommitInfo) -> List[str]:
    categories = []
    message_lower = commit.message.lower()
    
    # Add your custom patterns
    if any(word in message_lower for word in ['security', 'vulnerability']):
        categories.append('security')
    
    # ... existing patterns ...
    
    return categories
```

### Customizing File Categories

Add custom file type categories:

```python
def _categorize_files(self, files: set) -> Dict[str, List[str]]:
    categories = {
        'Services': [],
        'Models': [],
        'Controllers': [],
        'Tests': [],
        'Configuration': [],
        'Documentation': [],
        'CustomCategory': [],  # Add your custom category
        'Other': []
    }
    
    for file in files:
        if 'CustomPattern' in file:  # Add your custom pattern
            categories['CustomCategory'].append(file)
        # ... existing patterns ...
    
    return categories
```

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=mcp_mr_summarizer --cov-report=html
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Run the test suite
6. Commit your changes (`git commit -m 'Add some amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the Model Context Protocol (MCP) ecosystem
- Inspired by the need for better merge request documentation
- Thanks to all contributors and users

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/mcp-merge-request-summarizer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/mcp-merge-request-summarizer/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/mcp-merge-request-summarizer/wiki)

---

**Made with ❤️ for developers who want better merge request summaries**
