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
**VSCode/Cursor:**
```json
{
    "mcp.servers": {
        "merge-request-summarizer": {
            "command": "mcp-mr-summarizer-server",
            "args": []
        }
    }
}
```

**Claude Desktop:**
```json
{
    "mcpServers": {
        "merge-request-summarizer": {
            "command": "mcp-mr-summarizer-server",
            "args": []
        }
    }
}
```

## Command Line Usage

### Basic Usage
```bash
# Generate summary for current branch vs main
mcp-mr-summarizer

# Specify custom branches
mcp-mr-summarizer --base develop --current feature/new-feature

# Output to file
mcp-mr-summarizer --output mr_summary.md

# JSON format
mcp-mr-summarizer --format json --output summary.json
```

### Advanced Usage
```bash
# Include all commits (not just merge commits)
mcp-mr-summarizer --all-commits

# Custom commit range
mcp-mr-summarizer --since "2024-01-01" --until "2024-01-31"

# Verbose output
mcp-mr-summarizer --verbose

# Help
mcp-mr-summarizer --help
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
