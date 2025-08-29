"""MCP Server for generating merge request summaries from git logs."""

import time
import asyncio
import logging
from mcp.server.fastmcp import FastMCP

from .analyzer import GitLogAnalyzer
from .tools import GitTools, GitAnalysisError, GitTimeoutError, GitRepositoryError
from .config import setup_logging

# Setup logging
setup_logging()

# Create logger for this module
logger = logging.getLogger(__name__)

# Create an MCP server
mcp = FastMCP("merge-request-summarizer")

# Initialize tools with default repo path
tools = GitTools()

# Global variable to store the agent's working directory
_agent_working_dir = None

# Initialize analyzer lazily to avoid validation errors on import
_analyzer = None


def get_analyzer():
    """Get or create the analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = GitLogAnalyzer()
    return _analyzer


def get_agent_working_dir():
    """Get the agent's working directory."""
    global _agent_working_dir
    return _agent_working_dir


# Tools - Actions that perform computation or analysis
@mcp.tool()
async def set_working_directory(working_directory: str) -> str:
    """Set the working directory context for the MCP server.

    This allows the client agent to communicate its working directory
    so that when repo_path='.' is used, it refers to the agent's directory
    rather than the MCP server's directory.
    """
    global _agent_working_dir
    import os

    # Validate the directory exists
    if not os.path.exists(working_directory):
        return f"Error: Directory does not exist: {working_directory}"

    if not os.path.isdir(working_directory):
        return f"Error: Path is not a directory: {working_directory}"

    # Convert to absolute path
    abs_path = os.path.abspath(working_directory)
    _agent_working_dir = abs_path

    logger.info(f"Agent working directory set to: {abs_path}")
    return f"Working directory set to: {abs_path}"


@mcp.tool()
async def get_working_directory() -> str:
    """Get the current working directory context."""
    global _agent_working_dir

    if _agent_working_dir is None:
        return "No agent working directory set. Use set_working_directory() to configure the agent's working directory."

    return f"Agent working directory: {_agent_working_dir}"


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
        # If repo_path is ".", use the agent's working directory if set
        agent_dir = get_agent_working_dir()
        if repo_path == "." and agent_dir is not None:
            repo_path = agent_dir
            logger.debug(
                f"Using agent working directory for repo_path='.': {repo_path}"
            )

        result = await tools.generate_merge_request_summary(
            base_branch, current_branch, repo_path, format
        )
        total_time = time.time() - start_time
        logger.info(
            f"Async tool completed: generate_merge_request_summary in {total_time:.2f}s"
        )
        return result
    except GitTimeoutError as e:
        logger.error(f"Git timeout error in generate_merge_request_summary: {e}")
        return f"Error: Git operation timed out. Please check if the repository is accessible and the branches exist."
    except GitRepositoryError as e:
        logger.error(f"Git repository error in generate_merge_request_summary: {e}")
        return f"Error: Repository issue - {str(e)}"
    except GitAnalysisError as e:
        logger.error(f"Git analysis error in generate_merge_request_summary: {e}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(
            f"Unexpected error in generate_merge_request_summary - {e}", exc_info=True
        )
        return f"Error: Unexpected error occurred - {str(e)}"


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
        # If repo_path is ".", use the agent's working directory if set
        agent_dir = get_agent_working_dir()
        if repo_path == "." and agent_dir is not None:
            repo_path = agent_dir
            logger.debug(
                f"Using agent working directory for repo_path='.': {repo_path}"
            )

        result = await tools.analyze_git_commits(base_branch, current_branch, repo_path)
        total_time = time.time() - start_time
        logger.info(f"Async tool completed: analyze_git_commits in {total_time:.2f}s")
        return result
    except GitTimeoutError as e:
        logger.error(f"Git timeout error in analyze_git_commits: {e}")
        return f"Error: Git operation timed out. Please check if the repository is accessible and the branches exist."
    except GitRepositoryError as e:
        logger.error(f"Git repository error in analyze_git_commits: {e}")
        return f"Error: Repository issue - {str(e)}"
    except GitAnalysisError as e:
        logger.error(f"Git analysis error in analyze_git_commits: {e}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in analyze_git_commits - {e}", exc_info=True)
        return f"Error: Unexpected error occurred - {str(e)}"


if __name__ == "__main__":
    asyncio.run(mcp.run_stdio_async())
