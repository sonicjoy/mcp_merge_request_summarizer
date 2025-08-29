"""Git repository resource methods for MCP server."""

import json
import os
import asyncio
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

    async def get_repo_status(self) -> str:
        """Get current repository status and basic information."""
        try:
            # Check if we're in a git repository
            try:
                result = await asyncio.create_subprocess_exec(
                    "git",
                    "--no-pager",
                    "-C",
                    self.repo_path,
                    "rev-parse",
                    "--git-dir",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await result.wait()
                if result.returncode != 0:
                    return "No git repository found in current directory."
            except Exception:
                return "No git repository found in current directory."

            # Get current branch
            result = await asyncio.create_subprocess_exec(
                "git",
                "--no-pager",
                "-C",
                self.repo_path,
                "branch",
                "--show-current",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()
            current_branch = stdout.decode().strip()

            # Get remote URL
            try:
                result = await asyncio.create_subprocess_exec(
                    "git",
                    "--no-pager",
                    "-C",
                    self.repo_path,
                    "config",
                    "--get",
                    "remote.origin.url",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await result.communicate()
                remote_url = stdout.decode().strip()
            except Exception:
                remote_url = "No remote configured"

            # Get repository name
            result = await asyncio.create_subprocess_exec(
                "git",
                "--no-pager",
                "-C",
                self.repo_path,
                "rev-parse",
                "--show-toplevel",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()
            repo_name = os.path.basename(stdout.decode().strip())

            # Check if working directory is dirty
            result = await asyncio.create_subprocess_exec(
                "git",
                "--no-pager",
                "-C",
                self.repo_path,
                "status",
                "--porcelain",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()
            is_dirty = bool(stdout.decode().strip())

            # Count untracked files
            result = await asyncio.create_subprocess_exec(
                "git",
                "--no-pager",
                "-C",
                self.repo_path,
                "ls-files",
                "--others",
                "--exclude-standard",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()
            untracked_files = (
                len(stdout.decode().strip().split("\n"))
                if stdout.decode().strip()
                else 0
            )

            # Count staged changes
            result = await asyncio.create_subprocess_exec(
                "git",
                "--no-pager",
                "-C",
                self.repo_path,
                "diff",
                "--cached",
                "--name-only",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()
            staged_changes = (
                len(stdout.decode().strip().split("\n"))
                if stdout.decode().strip()
                else 0
            )

            # Count unstaged changes
            result = await asyncio.create_subprocess_exec(
                "git",
                "--no-pager",
                "-C",
                self.repo_path,
                "diff",
                "--name-only",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()
            unstaged_changes = (
                len(stdout.decode().strip().split("\n"))
                if stdout.decode().strip()
                else 0
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

    async def get_commit_history(self, base_branch: str, current_branch: str) -> str:
        """Get commit history between two branches."""
        try:
            commits = await self.analyzer.get_git_log(base_branch, current_branch)

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

    async def get_branches(self) -> str:
        """Get list of all branches in the repository."""
        try:
            # Check if we're in a git repository
            try:
                result = await asyncio.create_subprocess_exec(
                    "git",
                    "--no-pager",
                    "-C",
                    self.repo_path,
                    "rev-parse",
                    "--git-dir",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await result.wait()
                if result.returncode != 0:
                    return "No git repository found in current directory."
            except Exception:
                return "No git repository found in current directory."

            # Get current branch
            result = await asyncio.create_subprocess_exec(
                "git",
                "--no-pager",
                "-C",
                self.repo_path,
                "branch",
                "--show-current",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()
            current_branch = stdout.decode().strip()

            # Get local branches
            result = await asyncio.create_subprocess_exec(
                "git",
                "--no-pager",
                "-C",
                self.repo_path,
                "branch",
                "--format=%(refname:short)",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()
            local_branches = [
                branch.strip()
                for branch in stdout.decode().strip().split("\n")
                if branch.strip()
            ]

            # Get remote branches
            result = await asyncio.create_subprocess_exec(
                "git",
                "--no-pager",
                "-C",
                self.repo_path,
                "branch",
                "-r",
                "--format=%(refname:short)",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()
            remote_branches = [
                branch.strip()
                for branch in stdout.decode().strip().split("\n")
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

    async def get_changed_files(self, base_branch: str, current_branch: str) -> str:
        """Get list of files changed between two branches."""
        try:
            commits = await self.analyzer.get_git_log(base_branch, current_branch)

            if not commits:
                return f"No commits found between {base_branch} and {current_branch}"

            all_files = set()
            for commit in commits:
                all_files.update(commit.files_changed)

            file_categories = self.analyzer._categorize_files(all_files)

            return json.dumps(file_categories, indent=2)
        except Exception as e:
            return f"Error getting changed files: {str(e)}"
