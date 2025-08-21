"""Git repository resource methods for MCP server."""

import json
import os
import subprocess
from typing import Dict, Any

from .analyzer import GitLogAnalyzer


class GitResources:
    """Git repository resource methods."""

    def __init__(self, repo_path: str = "."):
        """Initialize GitResources with repository path."""
        self.repo_path = repo_path
        self._analyzer = None

    @property
    def analyzer(self):
        """Get or create the analyzer instance."""
        if self._analyzer is None:
            self._analyzer = GitLogAnalyzer(self.repo_path)
        return self._analyzer

    def get_repo_status(self) -> str:
        """Get current repository status and basic information."""
        try:
            # Check if we're in a git repository
            try:
                subprocess.run(
                    ["git", "rev-parse", "--git-dir"],
                    capture_output=True,
                    check=True,
                    cwd=self.repo_path,
                )
            except subprocess.CalledProcessError:
                return "No git repository found in current directory."

            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_path,
            )
            current_branch = result.stdout.strip()

            # Get remote URL
            try:
                result = subprocess.run(
                    ["git", "config", "--get", "remote.origin.url"],
                    capture_output=True,
                    text=True,
                    check=True,
                    cwd=self.repo_path,
                )
                remote_url = result.stdout.strip()
            except subprocess.CalledProcessError:
                remote_url = "No remote configured"

            # Get repository name
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_path,
            )
            repo_name = os.path.basename(result.stdout.strip())

            # Check if working directory is dirty
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_path,
            )
            is_dirty = bool(result.stdout.strip())

            # Count untracked files
            result = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_path,
            )
            untracked_files = (
                len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            )

            # Count staged changes
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_path,
            )
            staged_changes = (
                len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            )

            # Count unstaged changes
            result = subprocess.run(
                ["git", "diff", "--name-only"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_path,
            )
            unstaged_changes = (
                len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            )

            status = {
                "repository": repo_name,
                "current_branch": current_branch,
                "remote_url": remote_url,
                "is_dirty": is_dirty,
                "untracked_files": untracked_files,
                "staged_changes": staged_changes,
                "unstaged_changes": unstaged_changes,
            }

            return json.dumps(status, indent=2)
        except Exception as e:
            return f"Error getting repository status: {str(e)}"

    def get_commit_history(self, base_branch: str, current_branch: str) -> str:
        """Get commit history between two branches."""
        try:
            commits = self.analyzer.get_git_log(base_branch, current_branch)

            if not commits:
                return f"No commits found between {base_branch} and {current_branch}"

            commit_list = []
            for commit in commits:
                commit_list.append(
                    {
                        "hash": commit.hash[:8],
                        "message": commit.message,
                        "author": commit.author,
                        "date": commit.date,  # Already a string
                        "insertions": commit.insertions,
                        "deletions": commit.deletions,
                        "files_changed": list(commit.files_changed),
                    }
                )

            return json.dumps(commit_list, indent=2)
        except Exception as e:
            return f"Error getting commit history: {str(e)}"

    def get_branches(self) -> str:
        """Get list of all branches in the repository."""
        try:
            # Check if we're in a git repository
            try:
                subprocess.run(
                    ["git", "rev-parse", "--git-dir"],
                    capture_output=True,
                    check=True,
                    cwd=self.repo_path,
                )
            except subprocess.CalledProcessError:
                return "No git repository found in current directory."

            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_path,
            )
            current_branch = result.stdout.strip()

            # Get local branches
            result = subprocess.run(
                ["git", "branch", "--format=%(refname:short)"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_path,
            )
            local_branches = [
                branch.strip()
                for branch in result.stdout.strip().split("\n")
                if branch.strip()
            ]

            # Get remote branches
            result = subprocess.run(
                ["git", "branch", "-r", "--format=%(refname:short)"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_path,
            )
            remote_branches = [
                branch.strip()
                for branch in result.stdout.strip().split("\n")
                if branch.strip()
            ]

            branches = {
                "local_branches": local_branches,
                "remote_branches": remote_branches,
                "current_branch": current_branch,
            }

            return json.dumps(branches, indent=2)
        except Exception as e:
            return f"Error getting branches: {str(e)}"

    def get_changed_files(self, base_branch: str, current_branch: str) -> str:
        """Get list of files changed between two branches."""
        try:
            commits = self.analyzer.get_git_log(base_branch, current_branch)

            if not commits:
                return f"No commits found between {base_branch} and {current_branch}"

            all_files = set()
            for commit in commits:
                all_files.update(commit.files_changed)

            file_categories = self.analyzer._categorize_files(all_files)

            return json.dumps(file_categories, indent=2)
        except Exception as e:
            return f"Error getting changed files: {str(e)}"
