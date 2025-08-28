"""MCP Server for generating merge request summaries from git logs."""

import time
import sys
import asyncio
import logging
import os
from mcp.server.fastmcp import FastMCP

from .analyzer import GitLogAnalyzer
from .resources import GitResources
from .tools import GitTools
from .config import setup_logging

# Setup logging
setup_logging()

# Create logger for this module
logger = logging.getLogger(__name__)

# Get the directory of the current script to determine the repo root
# This makes the server more robust when run from different working directories
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(script_dir, "..", ".."))

# Create an MCP server
mcp = FastMCP("merge-request-summarizer")

# Initialize resources and tools (these don't require git validation on import)
resources = GitResources(repo_path=repo_root)
tools = GitTools(repo_path=repo_root)

# Initialize analyzer lazily to avoid validation errors on import
_analyzer = None


def get_analyzer():
    """Get or create the analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = GitLogAnalyzer(repo_path=repo_root)
    return _analyzer


# Resources - Data retrieval without side effects
@mcp.resource("git://repo/status")
async def get_repo_status() -> str:
    """Get current repository status and basic information."""
    logger.debug("Resource called: get_repo_status")
    return await resources.get_repo_status()


@mcp.resource("git://commits/{base_branch}..{current_branch}")
async def get_commit_history(base_branch: str, current_branch: str) -> str:
    """Get commit history between two branches."""
    logger.debug(
        f"Resource called: get_commit_history({base_branch}, {current_branch})"
    )
    return await resources.get_commit_history(base_branch, current_branch)


@mcp.resource("git://branches")
async def get_branches() -> str:
    """Get list of all branches in the repository."""
    logger.debug("Resource called: get_branches")
    return await resources.get_branches()


@mcp.resource("git://files/changed/{base_branch}..{current_branch}")
async def get_changed_files(base_branch: str, current_branch: str) -> str:
    """Get list of files changed between two branches."""
    logger.debug(f"Resource called: get_changed_files({base_branch}, {current_branch})")
    return await resources.get_changed_files(base_branch, current_branch)


# Tools - Actions that perform computation or analysis
@mcp.tool()
async def generate_merge_request_summary(
    base_branch: str = "master",
    current_branch: str = "HEAD",
    repo_path: str = ".",
    format: str = "markdown",
) -> str:
    """Generate a comprehensive merge request summary from git logs"""
    start_time = time.time()
    logger.debug("Async tool called: generate_merge_request_summary")
    logger.debug(
        f"Parameters: base_branch={base_branch}, current_branch={current_branch}, repo_path={repo_path}, format={format}"
    )

    try:
        result = await tools.generate_merge_request_summary(
            base_branch, current_branch, repo_path, format
        )
        total_time = time.time() - start_time
        logger.info(
            f"Async tool completed: generate_merge_request_summary in {total_time:.2f}s"
        )
        return result
    except Exception as e:
        logger.error(
            f"Async tool failed: generate_merge_request_summary - {e}", exc_info=True
        )
        return f"Error: {str(e)}"


@mcp.tool()
async def analyze_git_commits(
    base_branch: str = "master", current_branch: str = "HEAD", repo_path: str = "."
) -> str:
    """Analyze git commits and categorize them by type"""
    start_time = time.time()
    logger.debug("Async tool called: analyze_git_commits")
    logger.debug(
        f"Parameters: base_branch={base_branch}, current_branch={current_branch}, repo_path={repo_path}"
    )

    try:
        result = await tools.analyze_git_commits(base_branch, current_branch, repo_path)
        total_time = time.time() - start_time
        logger.info(f"Async tool completed: analyze_git_commits in {total_time:.2f}s")
        return result
    except Exception as e:
        logger.error(f"Async tool failed: analyze_git_commits - {e}", exc_info=True)
        return f"Error: {str(e)}"


if __name__ == "__main__":
    asyncio.run(mcp.run_stdio_async())