"""MCP Server for generating merge request summaries from git logs."""

import time
import sys
import asyncio
from mcp.server.fastmcp import FastMCP

from .analyzer import GitLogAnalyzer
from .resources import GitResources
from .tools import GitTools

# Create an MCP server
mcp = FastMCP("merge-request-summarizer")

# Initialize resources and tools (these don't require git validation on import)
resources = GitResources()
tools = GitTools()

# Initialize analyzer lazily to avoid validation errors on import
_analyzer = None


def get_analyzer():
    """Get or create the analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = GitLogAnalyzer()
    return _analyzer


# Resources - Data retrieval without side effects
@mcp.resource("git://repo/status")
def get_repo_status() -> str:
    """Get current repository status and basic information."""
    print("[DEBUG] Resource called: get_repo_status", file=sys.stderr)
    return resources.get_repo_status()


@mcp.resource("git://commits/{base_branch}..{current_branch}")
def get_commit_history(base_branch: str, current_branch: str) -> str:
    """Get commit history between two branches."""
    print(
        f"[DEBUG] Resource called: get_commit_history({base_branch}, {current_branch})",
        file=sys.stderr,
    )
    return resources.get_commit_history(base_branch, current_branch)


@mcp.resource("git://branches")
def get_branches() -> str:
    """Get list of all branches in the repository."""
    print("[DEBUG] Resource called: get_branches", file=sys.stderr)
    return resources.get_branches()


@mcp.resource("git://files/changed/{base_branch}..{current_branch}")
def get_changed_files(base_branch: str, current_branch: str) -> str:
    """Get list of files changed between two branches."""
    print(
        f"[DEBUG] Resource called: get_changed_files({base_branch}, {current_branch})",
        file=sys.stderr,
    )
    return resources.get_changed_files(base_branch, current_branch)


# Tools - Actions that perform computation or analysis
@mcp.tool()
async def generate_merge_request_summary(
    base_branch: str = "develop",
    current_branch: str = "HEAD",
    repo_path: str = ".",
    format: str = "markdown",
) -> str:
    """Generate a comprehensive merge request summary from git logs"""
    start_time = time.time()
    print(f"[DEBUG] Async tool called: generate_merge_request_summary", file=sys.stderr)
    print(
        f"[DEBUG] Parameters: base_branch={base_branch}, current_branch={current_branch}, repo_path={repo_path}, format={format}",
        file=sys.stderr,
    )

    try:
        result = await tools.generate_merge_request_summary(
            base_branch, current_branch, repo_path, format
        )
        total_time = time.time() - start_time
        print(
            f"[DEBUG] Async tool completed: generate_merge_request_summary in {total_time:.2f}s",
            file=sys.stderr,
        )
        return result
    except Exception as e:
        print(
            f"[ERROR] Async tool failed: generate_merge_request_summary - {e}",
            file=sys.stderr,
        )
        return f"Error: {str(e)}"


@mcp.tool()
async def analyze_git_commits(
    base_branch: str = "develop", current_branch: str = "HEAD", repo_path: str = "."
) -> str:
    """Analyze git commits and categorize them by type"""
    start_time = time.time()
    print(f"[DEBUG] Async tool called: analyze_git_commits", file=sys.stderr)
    print(
        f"[DEBUG] Parameters: base_branch={base_branch}, current_branch={current_branch}, repo_path={repo_path}",
        file=sys.stderr,
    )

    try:
        result = await tools.analyze_git_commits(base_branch, current_branch, repo_path)
        total_time = time.time() - start_time
        print(
            f"[DEBUG] Async tool completed: analyze_git_commits in {total_time:.2f}s",
            file=sys.stderr,
        )
        return result
    except Exception as e:
        print(f"[ERROR] Async tool failed: analyze_git_commits - {e}", file=sys.stderr)
        return f"Error: {str(e)}"


if __name__ == "__main__":
    mcp.run()
