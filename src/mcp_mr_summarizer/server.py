"""MCP Server for generating merge request summaries from git logs."""

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
    return resources.get_repo_status()


@mcp.resource("git://commits/{base_branch}..{current_branch}")
def get_commit_history(base_branch: str, current_branch: str) -> str:
    """Get commit history between two branches."""
    return resources.get_commit_history(base_branch, current_branch)


@mcp.resource("git://branches")
def get_branches() -> str:
    """Get list of all branches in the repository."""
    return resources.get_branches()


@mcp.resource("git://files/changed/{base_branch}..{current_branch}")
def get_changed_files(base_branch: str, current_branch: str) -> str:
    """Get list of files changed between two branches."""
    return resources.get_changed_files(base_branch, current_branch)


# Tools - Actions that perform computation or analysis
@mcp.tool()
def generate_merge_request_summary(
    base_branch: str = "develop",
    current_branch: str = "HEAD",
    repo_path: str = ".",
    format: str = "markdown",
) -> str:
    """Generate a comprehensive merge request summary from git logs"""
    return tools.generate_merge_request_summary(
        base_branch, current_branch, repo_path, format
    )


@mcp.tool()
def analyze_git_commits(
    base_branch: str = "develop", current_branch: str = "HEAD", repo_path: str = "."
) -> str:
    """Analyze git commits and categorize them by type"""
    return tools.analyze_git_commits(base_branch, current_branch, repo_path)


if __name__ == "__main__":
    mcp.run()
