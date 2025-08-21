# Usage Examples

## Quick Setup Examples

### 1. One-Click Installation
```bash
# Windows
install.bat

# Mac/Linux
chmod +x install.sh && ./install.sh
```

### 2. Editor Configuration
**VSCode:**
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

**Cursor:**
1. Open Cursor Settings (Ctrl + ,)
2. Go to **Tools & Integrations**
3. Click **New MCP Server**
4. Add:
   - **Name:** `merge-request-summarizer`
   - **Command:** `python`
   - **Arguments:** `["-m", "mcp_mr_summarizer.server"]`
5. Click **Save**

**Cursor (alternative JSON format):**
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

**Claude Desktop:**
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

## Command Line Usage

### Basic Usage
```bash
# Generate summary for current branch vs develop
python -m mcp_mr_summarizer.cli

# Specify custom branches
python -m mcp_mr_summarizer.cli --base develop --current feature/new-feature

# Output to file
python -m mcp_mr_summarizer.cli --output mr_summary.md

# JSON format
python -m mcp_mr_summarizer.cli --format json --output summary.json
```

### Advanced Usage
```bash
# Include all commits (not just merge commits)
python -m mcp_mr_summarizer.cli --all-commits

# Custom commit range
python -m mcp_mr_summarizer.cli --since "2024-01-01" --until "2024-01-31"

# Verbose output
python -m mcp_mr_summarizer.cli --verbose

# Help
python -m mcp_mr_summarizer.cli --help
```

## AI Integration Examples

### In VSCode/Cursor
```
User: "Generate a merge request summary for my current branch"

AI: I'll analyze your git history and create a comprehensive merge request summary.

[AI uses the MCP tool to generate the summary]
```

### In Claude Desktop
```
User: "Can you analyze the commits in my feature branch and create a merge request description?"

AI: I'll use the merge request summarizer to analyze your commits and create a detailed description.

[AI uses the MCP tool to analyze and summarize]
```

## Example Output

### Markdown Output
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

### JSON Output
```json
{
  "summary": "feat: 4 new features and improvements",
  "overview": "This merge request contains 9 commits with 35 files changed (1543 insertions, 1485 deletions).",
  "key_changes": [
    {
      "commit": "bdf5d9c",
      "message": "Refactor mappers in MLB, NBA, NHL, and NFL to use object initializer syntax",
      "lines_changed": 3028
    }
  ],
  "categories": {
    "features": 4,
    "refactoring": 3,
    "bug_fixes": 2
  },
  "statistics": {
    "total_commits": 9,
    "files_changed": 35,
    "lines_added": 1543,
    "lines_removed": 1485,
    "estimated_review_time": "1h 15m"
  }
}
```

## Troubleshooting Examples

### Common Issues and Solutions

**1. "Command not found" error**
```bash
# Check if package is installed
pip list | grep mcp-merge-request-summarizer

# Reinstall if needed
pip install -e .

# Use module approach instead
python -m mcp_mr_summarizer.cli --help
```

**2. Python path issues**
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

**5. Python version issues**
```bash
# Check Python version (requires 3.10+)
python --version

# Upgrade if necessary
# On Ubuntu/Debian:
sudo apt update && sudo apt install python3.10

# On macOS with Homebrew:
brew install python@3.10
```

## Development Examples

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=mcp_mr_summarizer --cov-report=html

# Run specific test file
python -m pytest tests/test_analyzer.py -v
```

### Code Quality Checks
```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/
mypy src/

# Run all checks
make check
```

### Building and Publishing
```bash
# Build package
python -m build

# Upload to PyPI
python -m twine upload dist/*

# Or use Makefile
make build
make upload
```
