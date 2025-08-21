"""MCP Server for generating merge request summaries from git logs."""

import json
import os
from dataclasses import asdict
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP

from .analyzer import GitLogAnalyzer

# Create an MCP server
mcp = FastMCP("merge-request-summarizer")

# Initialize analyzer
analyzer = GitLogAnalyzer()


# Resources - Data retrieval without side effects
@mcp.resource("git://repo/status")
def get_repo_status() -> str:
    """Get current repository status and basic information."""
    try:
        repo = analyzer.repo
        if not repo:
            return "No git repository found in current directory."

        current_branch = repo.active_branch.name
        remote_url = repo.remotes.origin.url if repo.remotes else "No remote configured"

        status = {
            "repository": os.path.basename(repo.working_dir),
            "current_branch": current_branch,
            "remote_url": remote_url,
            "is_dirty": repo.is_dirty(),
            "untracked_files": len(repo.untracked_files),
            "staged_changes": len(repo.index.diff("HEAD")),
            "unstaged_changes": len(repo.index.diff(None)),
        }

        return json.dumps(status, indent=2)
    except Exception as e:
        return f"Error getting repository status: {str(e)}"


@mcp.resource("git://commits/{base_branch}..{current_branch}")
def get_commit_history(base_branch: str, current_branch: str) -> str:
    """Get commit history between two branches."""
    try:
        commits = analyzer.get_git_log(base_branch, current_branch)

        if not commits:
            return f"No commits found between {base_branch} and {current_branch}"

        commit_list = []
        for commit in commits:
            commit_list.append(
                {
                    "hash": commit.hash[:8],
                    "message": commit.message,
                    "author": commit.author,
                    "date": commit.date.isoformat(),
                    "insertions": commit.insertions,
                    "deletions": commit.deletions,
                    "files_changed": list(commit.files_changed),
                }
            )

        return json.dumps(commit_list, indent=2)
    except Exception as e:
        return f"Error getting commit history: {str(e)}"


@mcp.resource("git://branches")
def get_branches() -> str:
    """Get list of all branches in the repository."""
    try:
        repo = analyzer.repo
        if not repo:
            return "No git repository found in current directory."

        branches = {
            "local_branches": [branch.name for branch in repo.branches],
            "remote_branches": [branch.name for branch in repo.remote().refs],
            "current_branch": repo.active_branch.name,
        }

        return json.dumps(branches, indent=2)
    except Exception as e:
        return f"Error getting branches: {str(e)}"


@mcp.resource("git://files/changed/{base_branch}..{current_branch}")
def get_changed_files(base_branch: str, current_branch: str) -> str:
    """Get list of files changed between two branches."""
    try:
        commits = analyzer.get_git_log(base_branch, current_branch)

        if not commits:
            return f"No commits found between {base_branch} and {current_branch}"

        all_files = set()
        for commit in commits:
            all_files.update(commit.files_changed)

        file_categories = analyzer._categorize_files(all_files)

        return json.dumps(file_categories, indent=2)
    except Exception as e:
        return f"Error getting changed files: {str(e)}"


# Tools - Actions that perform computation or analysis
@mcp.tool()
def generate_merge_request_summary(
    base_branch: str = "develop",
    current_branch: str = "HEAD",
    repo_path: str = ".",
    format: str = "markdown",
) -> str:
    """Generate a comprehensive merge request summary from git logs"""
    global analyzer

    # Update analyzer repo path if specified
    if repo_path != ".":
        analyzer = GitLogAnalyzer(repo_path)

    # Get commits and generate summary
    commits = analyzer.get_git_log(base_branch, current_branch)
    summary = analyzer.generate_summary(commits)

    if format == "json":
        return json.dumps(asdict(summary), indent=2)
    else:
        return f"# {summary.title}\n\n{summary.description}"


@mcp.tool()
def analyze_git_commits(
    base_branch: str = "develop", current_branch: str = "HEAD", repo_path: str = "."
) -> str:
    """Analyze git commits and categorize them by type"""
    global analyzer

    # Update analyzer repo path if specified
    if repo_path != ".":
        analyzer = GitLogAnalyzer(repo_path)

    # Get commits
    commits = analyzer.get_git_log(base_branch, current_branch)

    if not commits:
        return "No commits found between the specified branches."

    # Analyze commits
    analysis = {
        "total_commits": len(commits),
        "total_insertions": sum(c.insertions for c in commits),
        "total_deletions": sum(c.deletions for c in commits),
        "categories": {},
        "significant_changes": [],
        "files_affected": set(),
    }

    for commit in commits:
        categories = analyzer.categorize_commit(commit)
        for category in categories:
            if category not in analysis["categories"]:
                analysis["categories"][category] = []
            analysis["categories"][category].append(
                {
                    "hash": commit.hash[:8],
                    "message": commit.message,
                    "insertions": commit.insertions,
                    "deletions": commit.deletions,
                }
            )

        analysis["files_affected"].update(commit.files_changed)

        # Significant changes (more than 100 lines)
        if commit.insertions + commit.deletions > 100:
            analysis["significant_changes"].append(
                {
                    "hash": commit.hash[:8],
                    "message": commit.message,
                    "total_lines": commit.insertions + commit.deletions,
                }
            )

    # Generate report
    report = "# Git Commit Analysis\n\n"
    report += "## Summary\n"
    report += f"- **Total Commits:** {analysis['total_commits']}\n"
    report += f"- **Total Insertions:** {analysis['total_insertions']}\n"
    report += f"- **Total Deletions:** {analysis['total_deletions']}\n"
    report += f"- **Files Affected:** {len(analysis['files_affected'])}\n\n"

    if analysis["categories"]:
        report += "## Commit Categories\n\n"
        for category, commits_list in analysis["categories"].items():
            report += (
                f"### {category.replace('_', ' ').title()} ({len(commits_list)})\n"
            )
            for commit_info in commits_list:
                report += f"- `{commit_info['hash']}` {commit_info['message']} (+{commit_info['insertions']}/-{commit_info['deletions']})\n"
            report += "\n"

    if analysis["significant_changes"]:
        report += "## Significant Changes\n\n"
        for change in analysis["significant_changes"]:
            report += f"- `{change['hash']}` {change['message']} ({change['total_lines']} lines)\n"
        report += "\n"

    if analysis["files_affected"]:
        report += "## Files Affected\n\n"
        file_categories = analyzer._categorize_files(analysis["files_affected"])
        for category, files in file_categories.items():
            if files:
                report += f"### {category}\n"
                for file in sorted(files)[:10]:
                    report += f"- `{file}`\n"
                if len(files) > 10:
                    report += f"- ... and {len(files) - 10} more\n"
                report += "\n"

    return report


if __name__ == "__main__":
    mcp.run()
