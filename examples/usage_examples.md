# Usage Examples

This document provides various examples of how to use the MCP Merge Request Summarizer tool.

## Command Line Usage

### Basic Usage

```bash
# Generate summary for current branch against develop
mcp-mr-summarizer

# Specify different branches
mcp-mr-summarizer --base main --current feature/user-authentication

# Use a different repository path
mcp-mr-summarizer --repo /path/to/your/repo
```

### Output Options

```bash
# Output to a file
mcp-mr-summarizer --output mr_summary.md

# Generate JSON output
mcp-mr-summarizer --format json --output summary.json

# JSON output to stdout
mcp-mr-summarizer --format json
```

### Real-world Examples

```bash
# Feature branch summary
mcp-mr-summarizer --base develop --current feature/payment-integration

# Hotfix summary
mcp-mr-summarizer --base main --current hotfix/security-patch

# Release branch summary
mcp-mr-summarizer --base develop --current release/v2.1.0
```

## MCP Server Configuration

### Claude Desktop Configuration

Add to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "merge-request-summarizer": {
      "command": "python",
      "args": ["/path/to/mcp-merge-request-summarizer/src/mcp_mr_summarizer/server.py"],
      "env": {
        "PYTHONPATH": "/path/to/mcp-merge-request-summarizer/src"
      }
    }
  }
}
```

### Cursor Configuration

Add to your Cursor settings:

```json
{
  "mcp.servers": {
    "merge-request-summarizer": {
      "command": "mcp-mr-summarizer-server"
    }
  }
}
```

## Example Outputs

### Markdown Output

```markdown
# feat: 3 new features and improvements

## Overview
This merge request contains 5 commits with 12 files changed (234 insertions, 89 deletions).

## Key Changes
- Add user authentication system (a1b2c3d) - 156 lines changed
- Implement payment processing (e4f5g6h) - 98 lines changed

### 🚀 New Features (3)
- Add user authentication system (a1b2c3d)
- Implement payment processing (e4f5g6h)
- Add user profile management (i7j8k9l)

### 🔧 Refactoring (1)
- Refactor database connection handling (m0n1o2p)

### 🐛 Bug Fixes (1)
- Fix memory leak in data processor (q3r4s5t)

### 📁 Files Affected (12)

**Services:**
- `src/services/AuthService.py`
- `src/services/PaymentService.py`
- `src/services/UserService.py`

**Models:**
- `src/models/User.py`
- `src/models/Payment.py`

**Controllers:**
- `src/controllers/AuthController.py`
- `src/controllers/PaymentController.py`

**Tests:**
- `tests/test_auth.py`
- `tests/test_payment.py`

**Configuration:**
- `config/database.json`
- `config/payment.yaml`

**Other:**
- `utils/helpers.py`

### 📊 Summary
- **Total Commits:** 5
- **Files Changed:** 12
- **Lines Added:** 234
- **Lines Removed:** 89
- **Estimated Review Time:** 25 minutes
```

### JSON Output

```json
{
  "title": "feat: 3 new features and improvements",
  "description": "## Overview\nThis merge request contains 5 commits with 12 files changed (234 insertions, 89 deletions).\n\n## Key Changes\n...",
  "total_commits": 5,
  "total_files_changed": 12,
  "total_insertions": 234,
  "total_deletions": 89,
  "key_changes": [
    "- Add user authentication system (a1b2c3d) - 156 lines changed",
    "- Implement payment processing (e4f5g6h) - 98 lines changed"
  ],
  "breaking_changes": [],
  "new_features": [
    "- Add user authentication system (a1b2c3d)",
    "- Implement payment processing (e4f5g6h)",
    "- Add user profile management (i7j8k9l)"
  ],
  "bug_fixes": [
    "- Fix memory leak in data processor (q3r4s5t)"
  ],
  "refactoring": [
    "- Refactor database connection handling (m0n1o2p)"
  ],
  "files_affected": [
    "config/database.json",
    "config/payment.yaml",
    "src/controllers/AuthController.py",
    "src/controllers/PaymentController.py",
    "src/models/Payment.py",
    "src/models/User.py",
    "src/services/AuthService.py",
    "src/services/PaymentService.py",
    "src/services/UserService.py",
    "tests/test_auth.py",
    "tests/test_payment.py",
    "utils/helpers.py"
  ],
  "estimated_review_time": "25 minutes"
}
```

## Integration Examples

### GitHub Actions

```yaml
name: Generate MR Summary
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  generate-summary:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install MR Summarizer
        run: pip install mcp-merge-request-summarizer
      
      - name: Generate Summary
        run: |
          mcp-mr-summarizer --base ${{ github.base_ref }} --current ${{ github.head_ref }} --output summary.md
      
      - name: Comment PR
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const summary = fs.readFileSync('summary.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: summary
            });
```

### GitLab CI

```yaml
generate_mr_summary:
  stage: review
  image: python:3.9
  before_script:
    - pip install mcp-merge-request-summarizer
  script:
    - mcp-mr-summarizer --base $CI_MERGE_REQUEST_TARGET_BRANCH_NAME --current $CI_COMMIT_REF_NAME --output summary.md
    - cat summary.md
  artifacts:
    reports:
      junit: summary.md
  only:
    - merge_requests
```

### Pre-commit Hook

```bash
#!/bin/sh
# .git/hooks/pre-push

# Generate summary for the current branch
mcp-mr-summarizer --base develop --current HEAD --output .git/mr_summary.md

echo "Merge request summary generated in .git/mr_summary.md"
echo "You can copy this content to your merge request description."
```

## Customization Examples

### Custom Commit Categories

Create a custom analyzer with additional categories:

```python
from mcp_mr_summarizer import GitLogAnalyzer, CommitInfo

class CustomGitLogAnalyzer(GitLogAnalyzer):
    def categorize_commit(self, commit: CommitInfo) -> List[str]:
        categories = super().categorize_commit(commit)
        message_lower = commit.message.lower()
        
        # Add custom categories
        if any(word in message_lower for word in ['security', 'vulnerability', 'auth']):
            categories.append('security')
        
        if any(word in message_lower for word in ['performance', 'optimize', 'speed']):
            categories.append('performance')
        
        if any(word in message_lower for word in ['ui', 'ux', 'design', 'style']):
            categories.append('ui_ux')
        
        return categories

# Usage
analyzer = CustomGitLogAnalyzer()
commits = analyzer.get_git_log('main', 'feature-branch')
summary = analyzer.generate_summary(commits)
```

### Custom File Categories

```python
def custom_categorize_files(self, files: set) -> Dict[str, List[str]]:
    categories = {
        'Frontend': [],
        'Backend': [],
        'Database': [],
        'Infrastructure': [],
        'Tests': [],
        'Documentation': [],
        'Other': []
    }
    
    for file in files:
        if any(pattern in file for pattern in ['frontend/', 'ui/', 'components/', '.vue', '.jsx', '.tsx']):
            categories['Frontend'].append(file)
        elif any(pattern in file for pattern in ['backend/', 'api/', 'server/', 'services/']):
            categories['Backend'].append(file)
        elif any(pattern in file for pattern in ['migrations/', 'schema/', '.sql', 'database/']):
            categories['Database'].append(file)
        elif any(pattern in file for pattern in ['docker', 'k8s/', 'terraform/', '.yml', '.yaml']):
            categories['Infrastructure'].append(file)
        elif any(pattern in file for pattern in ['test', 'spec', '__tests__']):
            categories['Tests'].append(file)
        elif any(pattern in file for pattern in ['.md', '.rst', '.txt', 'docs/']):
            categories['Documentation'].append(file)
        else:
            categories['Other'].append(file)
    
    return categories

# Monkey patch the method
GitLogAnalyzer._categorize_files = custom_categorize_files
```

## Troubleshooting

### Common Issues

1. **Git command not found**
   ```bash
   # Ensure git is installed and in PATH
   which git
   git --version
   ```

2. **No commits found**
   ```bash
   # Check branch names
   git branch -a
   
   # Verify commits exist between branches
   git log develop..HEAD --oneline
   ```

3. **Permission denied**
   ```bash
   # Make script executable
   chmod +x /path/to/mcp-mr-summarizer
   ```

4. **Module not found**
   ```bash
   # Install in development mode
   pip install -e .
   
   # Or add to PYTHONPATH
   export PYTHONPATH=/path/to/mcp-merge-request-summarizer/src:$PYTHONPATH
   ```
