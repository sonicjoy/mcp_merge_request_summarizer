# Working Directory Guide for MCP Merge Request Summarizer

## Overview

The MCP Merge Request Summarizer now supports a working directory context feature that allows client agents to communicate their working directory to the MCP server. This solves the issue where `repo_path="."` would refer to the MCP server's directory instead of the agent's directory.

## Problem Solved

Previously, when an agent called the MCP server with `repo_path="."`, it would use the MCP server's working directory, not the agent's working directory. This caused issues because:

1. The MCP server runs in its own directory
2. The agent works in a different directory (e.g., a git repository)
3. When the agent calls with `repo_path="."`, it expects to use its own directory

## Solution

The MCP server now provides two new tools to manage working directory context:

### 1. `set_working_directory(working_directory: str)`

Sets the agent's working directory context for the MCP server.

**Parameters:**
- `working_directory`: The absolute or relative path to the agent's working directory

**Returns:**
- Success message with the absolute path
- Error message if the directory doesn't exist or is not a directory

**Example:**
```python
# Agent sets its working directory
result = await set_working_directory("/path/to/my/git/repo")
# Returns: "Working directory set to: /path/to/my/git/repo"
```

### 2. `get_working_directory()`

Gets the current working directory context.

**Returns:**
- The agent's working directory if set
- MCP server directory if no agent directory is set

**Example:**
```python
# Agent checks the working directory
result = await get_working_directory()
# Returns: "Agent working directory: /path/to/my/git/repo"
```

## Usage Pattern

### Step 1: Set Working Directory
The agent should call `set_working_directory()` at the beginning of its session:

```python
# Agent sets its working directory
await set_working_directory("/path/to/my/git/repo")
```

### Step 2: Use repo_path="."
Now when the agent calls other tools with `repo_path="."`, it will use the agent's working directory:

```python
# This will use the agent's working directory, not the MCP server's
result = await generate_merge_request_summary(
    base_branch="main",
    current_branch="feature-branch",
    repo_path=".",  # Now refers to agent's directory
    format="markdown"
)
```

## Implementation Details

### How It Works

1. **Global Context**: The MCP server maintains a global variable `_agent_working_dir` to store the agent's working directory.

2. **Automatic Resolution**: When `repo_path="."` is used, the server automatically replaces it with the agent's working directory if set.

3. **Validation**: The `set_working_directory()` tool validates that the directory exists and is actually a directory.

4. **Absolute Paths**: All working directories are converted to absolute paths for consistency.

### Code Flow

```
Agent calls set_working_directory("/path/to/repo")
    ↓
MCP server stores "/path/to/repo" in _agent_working_dir
    ↓
Agent calls generate_merge_request_summary(repo_path=".")
    ↓
MCP server replaces "." with "/path/to/repo"
    ↓
Tools use "/path/to/repo" for git operations
```

## Benefits

1. **Correct Context**: `repo_path="."` now correctly refers to the agent's working directory
2. **Flexibility**: Agents can work in any directory and communicate it to the MCP server
3. **Backward Compatibility**: Existing code using explicit paths continues to work
4. **Validation**: Invalid directories are caught early with clear error messages

## Error Handling

The `set_working_directory()` tool provides clear error messages for:

- **Non-existent directories**: "Error: Directory does not exist: /path/to/nonexistent"
- **Non-directory paths**: "Error: Path is not a directory: /path/to/file.txt"

## Example Workflow

```python
# 1. Agent starts and sets its working directory
await set_working_directory("/home/user/my-project")

# 2. Agent can now use "." to refer to its working directory
summary = await generate_merge_request_summary(
    base_branch="main",
    current_branch="feature",
    repo_path=".",  # Uses /home/user/my-project
    format="markdown"
)

# 3. Agent can also use explicit paths
summary = await generate_merge_request_summary(
    base_branch="main", 
    current_branch="feature",
    repo_path="/home/user/my-project",  # Explicit path
    format="markdown"
)
```

## Migration Guide

### For Existing Users

If you're already using explicit paths, no changes are needed:

```python
# This continues to work as before
result = await generate_merge_request_summary(
    base_branch="main",
    current_branch="feature", 
    repo_path="/explicit/path/to/repo",
    format="markdown"
)
```

### For New Users

Add a call to `set_working_directory()` at the beginning of your session:

```python
# Set your working directory
await set_working_directory("/path/to/your/repo")

# Now you can use "." for convenience
result = await generate_merge_request_summary(
    base_branch="main",
    current_branch="feature",
    repo_path=".",  # Uses your working directory
    format="markdown"
)
```

## Troubleshooting

### Issue: "Directory does not exist"
**Cause**: The path provided to `set_working_directory()` doesn't exist.
**Solution**: Verify the path exists and is correct.

### Issue: "Path is not a directory"  
**Cause**: The path exists but is a file, not a directory.
**Solution**: Provide the path to the directory containing your git repository.

### Issue: Git operations still fail
**Cause**: The directory exists but is not a git repository.
**Solution**: Ensure the directory contains a `.git` folder or is a valid git repository.
