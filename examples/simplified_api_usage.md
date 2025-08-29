# Simplified API Usage Example

## Overview
The MCP merge request summarizer now has a simplified API that removes the need to pass `repo_path` to every tool call. Instead, you set the working directory once and then use the tools.

## Setup

### 1. Set Working Directory
First, set the working directory to your repository:

```python
# Set the working directory to your repository
await set_working_directory("/path/to/your/repository")
```

### 2. Use Simplified Tools
Now you can use the tools without specifying the repository path:

```python
# Generate a merge request summary
summary = await generate_merge_request_summary(
    base_branch="main",
    current_branch="feature-branch",
    format="markdown"
)

# Analyze git commits
analysis = await analyze_git_commits(
    base_branch="main",
    current_branch="feature-branch"
)
```

## Complete Example

```python
# 1. Set up the working directory
await set_working_directory("/home/user/my-project")

# 2. Generate a merge request summary
summary = await generate_merge_request_summary(
    base_branch="main",
    current_branch="feature/user-authentication",
    format="markdown"
)

print("Merge Request Summary:")
print(summary)

# 3. Analyze commits for detailed insights
analysis = await analyze_git_commits(
    base_branch="main",
    current_branch="feature/user-authentication"
)

print("\nCommit Analysis:")
print(analysis)

# 4. Check current working directory
current_dir = await get_working_directory()
print(f"\nCurrent working directory: {current_dir}")
```

## Benefits

### Before (Complex)
```python
# Had to specify repo_path for every call
summary1 = await generate_merge_request_summary(
    base_branch="main",
    current_branch="feature1",
    repo_path="/path/to/repo",  # Required
    format="markdown"
)

summary2 = await generate_merge_request_summary(
    base_branch="main", 
    current_branch="feature2",
    repo_path="/path/to/repo",  # Required again
    format="markdown"
)

analysis = await analyze_git_commits(
    base_branch="main",
    current_branch="feature1", 
    repo_path="/path/to/repo"  # Required again
)
```

### After (Simplified)
```python
# Set once, use everywhere
await set_working_directory("/path/to/repo")

summary1 = await generate_merge_request_summary(
    base_branch="main",
    current_branch="feature1",
    format="markdown"
)

summary2 = await generate_merge_request_summary(
    base_branch="main",
    current_branch="feature2", 
    format="markdown"
)

analysis = await analyze_git_commits(
    base_branch="main",
    current_branch="feature1"
)
```

## Error Handling

The new API provides better error handling:

```python
try:
    await set_working_directory("/invalid/path")
    summary = await generate_merge_request_summary("main", "feature")
except Exception as e:
    print(f"Error: {e}")
    # Will show: "Error: No working directory set. Use set_working_directory() to configure the agent's working directory."
```

## Available Tools

### Core Tools
- `set_working_directory(path)` - Set the repository working directory
- `get_working_directory()` - Get the current working directory
- `generate_merge_request_summary(base_branch, current_branch, format)` - Generate MR summary
- `analyze_git_commits(base_branch, current_branch)` - Analyze commits

### Parameters
- `base_branch` - The base branch (default: "master")
- `current_branch` - The current branch (default: "HEAD") 
- `format` - Output format: "markdown" or "json" (default: "markdown")

## Migration from Old API

If you were using the old API with `repo_path`:

### Old Code
```python
summary = await generate_merge_request_summary(
    base_branch="main",
    current_branch="feature",
    repo_path="/path/to/repo",
    format="markdown"
)
```

### New Code
```python
await set_working_directory("/path/to/repo")
summary = await generate_merge_request_summary(
    base_branch="main",
    current_branch="feature",
    format="markdown"
)
```

The new API is cleaner, more consistent, and easier to use!
