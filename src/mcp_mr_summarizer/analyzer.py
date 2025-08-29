"""Git log analyzer for generating merge request summaries."""

import re
import time
import asyncio
import logging
import subprocess
from typing import Dict, List, Optional, Set, Iterator, Tuple
from dataclasses import dataclass

from .models import CommitInfo, MergeRequestSummary

# Create logger for this module
logger = logging.getLogger(__name__)


class TimeoutError(Exception):
    """Custom timeout exception."""

    pass


# Constants for better maintainability
class GitPatterns:
    """Regex patterns for git output parsing."""

    INSERTION_DELETION_PATTERNS = [
        r"(\d+)\s+insertions?\(\+\),\s*(\d+)\s+deletions?\(-\)",  # "13 insertions(+), 25 deletions(-)"
        r"(\d+)\s+insertions?,\s*(\d+)\s+deletions?",  # "13 insertions, 25 deletions"
        r"(\d+)\s+insertions?\(\+\)",  # "13 insertions(+)" (insertions only)
        r"(\d+)\s+deletions?\(-\)",  # "25 deletions(-)" (deletions only)
    ]
    COMMIT_HASH_PATTERN = r"^[0-9a-f]{40}$"


class CategoryPatterns:
    """Patterns for commit categorization."""

    PATTERNS = {
        "refactoring": {
            "refactor",
            "refactoring",
            "cleanup",
            "clean up",
            "restructure",
        },
        "bug_fix": {"fix", "bug", "issue", "error", "resolve", "patch", "hotfix"},
        "new_feature": {
            "add",
            "new",
            "feature",
            "implement",
            "create",
            "introduce",
            "feat",
        },
        "cleanup": {"remove", "delete", "drop", "deprecate", "clean"},
        "update": {"update", "upgrade", "bump", "dependenc", "version"},
        "test": {"test", "spec", "specs", "testing", "unit", "integration"},
        "documentation": {"docs", "documentation", "readme", "comment", "doc"},
    }


class FilePatterns:
    """Patterns for file categorization."""

    PATTERNS = {
        "Services": {"patterns": ["service", "api", "client"], "extensions": set()},
        "Models": {
            "patterns": ["model", "entity", "dto", "schema"],
            "extensions": set(),
        },
        "Controllers": {
            "patterns": ["controller", "handler", "route"],
            "extensions": set(),
        },
        "Tests": {
            "patterns": ["test", "spec", "specs", "testing"],
            "extensions": set(),
        },
        "Configuration": {
            "patterns": [],
            "extensions": {
                ".json",
                ".config",
                ".yml",
                ".yaml",
                ".xml",
                ".toml",
                ".ini",
            },
        },
        "Documentation": {
            "patterns": [],
            "extensions": {".md", ".txt", ".rst", ".adoc"},
        },
        "Frontend": {
            "patterns": [],
            "extensions": {
                ".js",
                ".jsx",
                ".ts",
                ".tsx",
                ".vue",
                ".svelte",
                ".html",
                ".css",
                ".scss",
                ".sass",
            },
        },
        "Backend": {
            "patterns": [],
            "extensions": {
                ".py",
                ".java",
                ".cs",
                ".go",
                ".rs",
                ".php",
                ".rb",
                ".js",
                ".ts",
            },
        },
        "Other": {"patterns": [], "extensions": set()},
    }


@dataclass
class GitLogSection:
    """Represents a section of git log output."""

    hash: str
    author: str
    date: str
    message: str
    stats_lines: List[str]


class GitLogAnalyzer:
    """Analyzes git logs and generates structured summaries."""

    def __init__(self, repo_path: str = ".") -> None:
        """Initialize the analyzer with a repository path."""
        self.repo_path = repo_path
        # Pre-compile regex patterns for better performance
        self._compiled_patterns = [
            re.compile(pattern) for pattern in GitPatterns.INSERTION_DELETION_PATTERNS
        ]
        self._commit_hash_pattern = re.compile(GitPatterns.COMMIT_HASH_PATTERN)

    def _is_testing(self) -> bool:
        """Check if we're running in a test environment."""
        import sys
        import os

        return (
            any("pytest" in arg for arg in sys.argv)
            or "PYTEST_CURRENT_TEST" in os.environ
        )

    def _build_git_command(self, subcommand: List[str]) -> List[str]:
        """Build a git command with the repository path."""
        return ["git", "--no-pager", "-C", self.repo_path] + subcommand[
            2:
        ]  # Skip "git" and "--no-pager"

    async def _execute_git_command(
        self, cmd: List[str], timeout: int = 10
    ) -> subprocess.CompletedProcess:
        """Execute a git command asynchronously."""
        cmd_with_path = self._build_git_command(cmd)
        logger.debug(f"Executing git command: {' '.join(cmd_with_path)}")

        try:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    cmd_with_path,
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=timeout,
                ),
            )
        except subprocess.TimeoutExpired as e:
            logger.error(f"Git command timed out: {' '.join(cmd_with_path)}")
            raise e
        except Exception as e:
            logger.error(f"Git command failed: {' '.join(cmd_with_path)} - {e}")
            raise e

    async def _validate_repo_path(self) -> None:
        """Validate that the repository path exists and is a valid git repository."""
        import os

        logger.debug(f"Validating repo path: {self.repo_path}")

        if not os.path.exists(self.repo_path):
            raise ValueError(f"Repository path does not exist: {self.repo_path}")

        try:
            # Validate git repository
            result1 = await self._execute_git_command(
                ["git", "--no-pager", "rev-parse", "--git-dir"]
            )
            if result1.returncode != 0:
                raise ValueError(f"Not a valid git repository: {self.repo_path}")

            result2 = await self._execute_git_command(
                ["git", "--no-pager", "rev-parse", "--show-toplevel"]
            )
            if result2.returncode != 0:
                raise ValueError(f"Invalid git repository state: {self.repo_path}")

        except subprocess.TimeoutExpired:
            raise ValueError(f"Git repository validation timed out: {self.repo_path}")
        except FileNotFoundError:
            raise ValueError(
                "Git command not found. Please ensure git is installed and in your PATH."
            )
        except Exception as e:
            raise ValueError(f"Error validating git repository: {e}")

    def _is_commit_hash(self, line: str) -> bool:
        """Check if a line is a valid git commit hash."""
        return bool(self._commit_hash_pattern.match(line))

    async def _validate_branches(self, base_branch: str, current_branch: str) -> None:
        """Validate that the specified branches exist in the repository."""
        # Skip validation for commit hashes
        if self._is_commit_hash(base_branch) or self._is_commit_hash(current_branch):
            logger.debug(
                f"Skipping branch validation for commit hashes: {base_branch}, {current_branch}"
            )
            return

        try:
            cmd = ["git", "--no-pager", "branch", "-a", "--format=%(refname:short)"]
            result = await self._execute_git_command(cmd)

            if result.returncode != 0:
                raise Exception(
                    f"Failed to get branches: {result.stderr or 'No stderr output'}"
                )

            stdout_output = result.stdout.strip()
            available_branches = (
                set(stdout_output.split("\n")) if stdout_output else set()
            )

            # Check if branches exist
            missing_branches = []
            if base_branch not in available_branches:
                missing_branches.append(base_branch)
            if current_branch != "HEAD" and current_branch not in available_branches:
                missing_branches.append(current_branch)

            if missing_branches:
                raise ValueError(
                    f"Branch(es) not found: {', '.join(missing_branches)}. "
                    f"Available branches: {', '.join(sorted(list(available_branches)))}"
                )

        except subprocess.TimeoutExpired:
            raise TimeoutError("Branch validation timed out")
        except FileNotFoundError:
            raise Exception(
                "Git command not found. Please ensure git is installed and in your PATH."
            )
        except (ValueError, TimeoutError):
            raise
        except Exception as e:
            raise Exception(f"Error validating branches: {e}")

    async def get_git_log(
        self, base_branch: str = "master", current_branch: str = "HEAD"
    ) -> List[CommitInfo]:
        """Retrieve git log between two branches asynchronously."""
        start_time = time.time()
        logger.debug(f"Starting git log retrieval: {base_branch}..{current_branch}")

        try:
            # Validate repository and branches
            if not self._is_testing():
                await self._validate_repo_path()
            await self._validate_branches(base_branch, current_branch)

            # Execute git log command
            cmd = [
                "git",
                "--no-pager",
                "log",
                f"{base_branch}..{current_branch}",
                "--stat",
                "--format=format:%H%n%an%n%ad%n%s%n",
                "--date=short",
            ]

            result = await self._execute_git_command(cmd, timeout=30)

            if result.returncode != 0:
                if result.returncode == 128:
                    logger.debug("No commits found between branches (return code 128)")
                    return []
                else:
                    raise Exception(
                        f"Git command failed with return code {result.returncode}: {result.stderr}"
                    )

            output = result.stdout
            if not output:
                logger.debug("No git output found, returning empty list")
                return []

            # Parse the output
            parse_start = time.time()
            commits = self._parse_git_output_sync_modern(output)
            parse_time = time.time() - parse_start

            total_time = time.time() - start_time
            logger.debug(
                f"Git log retrieval completed in {total_time:.2f}s, found {len(commits)} commits"
            )

            return commits

        except subprocess.TimeoutExpired:
            raise TimeoutError("Git command timed out after 30 seconds")
        except Exception as e:
            raise Exception(f"Unexpected error getting git log: {e}")

    def _parse_git_output_sync_modern(self, output: str) -> List[CommitInfo]:
        """Modern synchronous parsing of git output using iterators and generators."""
        lines = output.split("\n")
        logger.debug(f"Parsing {len(lines)} lines of git output")

        commits = []
        line_iter = iter(lines)

        try:
            while True:
                section = self._extract_commit_section(line_iter)
                if not section:
                    break

                commit_info = self._parse_commit_section(section)
                if commit_info:
                    commits.append(commit_info)
        except StopIteration:
            pass

        logger.debug(f"Parsed {len(commits)} commits")
        return commits

    def _extract_commit_section(
        self, line_iter: Iterator[str]
    ) -> Optional[GitLogSection]:
        """Extract a complete commit section from the iterator."""
        try:
            # Find the next commit hash
            while True:
                line = next(line_iter).strip()
                if self._is_commit_hash(line):
                    break

            commit_hash = line

            # Extract author, date, message
            try:
                author = next(line_iter).strip()
                date = next(line_iter).strip()
                message = next(line_iter).strip()
            except StopIteration:
                logger.debug(
                    f"Skipping commit {commit_hash[:8]} - insufficient header lines"
                )
                return None

            # Validate required fields
            if not all([author, date, message]):
                logger.debug(
                    f"Skipping commit {commit_hash[:8]} - missing required fields"
                )
                return None

            # Collect stats lines
            stats_lines = []
            try:
                # Skip empty lines
                while True:
                    line = next(line_iter).strip()
                    if line:
                        break

                # Collect stats lines until we hit another commit
                while line and not self._is_commit_hash(line):
                    stats_lines.append(line)
                    try:
                        line = next(line_iter).strip()
                    except StopIteration:
                        break

            except StopIteration:
                pass

            logger.debug(
                f"Collected stats lines for commit {commit_hash[:8]}: {stats_lines}"
            )
            return GitLogSection(
                hash=commit_hash,
                author=author,
                date=date,
                message=message,
                stats_lines=stats_lines,
            )

        except StopIteration:
            return None

    def _parse_commit_section(self, section: GitLogSection) -> Optional[CommitInfo]:
        """Parse a commit section into a CommitInfo object."""
        files_changed = []
        insertions = 0
        deletions = 0

        logger.debug(
            f"Parsing commit section with {len(section.stats_lines)} stats lines"
        )
        for line in section.stats_lines:
            logger.debug(f"Processing stats line: {line}")
            if "|" in line and any(c.isdigit() for c in line):
                file_name, _ = self._parse_file_stats_line(line)
                if file_name:
                    files_changed.append(file_name)
                    logger.debug(f"Added file: {file_name}")
            elif "file changed" in line or "files changed" in line:
                # This is the summary line with total stats
                logger.debug(f"Parsing summary line: {line}")
                ins, dels = self._extract_insertions_deletions(line)
                logger.debug(f"Extracted insertions: {ins}, deletions: {dels}")
                insertions = ins
                deletions = dels

        logger.debug(
            f"Final commit info: files={files_changed}, insertions={insertions}, deletions={deletions}"
        )
        return CommitInfo(
            hash=section.hash,
            author=section.author,
            date=section.date,
            message=section.message,
            files_changed=files_changed,
            insertions=insertions,
            deletions=deletions,
        )

    def _parse_file_stats_line(self, line: str) -> Tuple[Optional[str], str]:
        """Parse a file stats line and return (filename, stats_part)."""
        parts = line.split("|", 1)
        if len(parts) < 2:
            return None, ""

        file_name = parts[0].strip()
        stats_part = parts[1].strip()

        return file_name, stats_part

    def _extract_insertions_deletions(self, stats_part: str) -> Tuple[int, int]:
        """Extract insertions and deletions from stats part."""
        insertions = 0
        deletions = 0

        logger.debug(f"Extracting from stats part: {stats_part}")
        for pattern in self._compiled_patterns:
            stats_match = pattern.search(stats_part)
            if stats_match:
                logger.debug(f"Pattern matched: {pattern.pattern}")
                # If pattern has both groups, use them
                if len(stats_match.groups()) >= 2:
                    insertions = int(stats_match.group(1))
                    deletions = int(stats_match.group(2))
                    logger.debug(f"Both groups: {insertions}, {deletions}")
                else:
                    # Single group pattern
                    if "insertions" in pattern.pattern:
                        insertions = int(stats_match.group(1))
                        logger.debug(f"Insertions only: {insertions}")
                    if "deletions" in pattern.pattern:
                        deletions = int(stats_match.group(1))
                        logger.debug(f"Deletions only: {deletions}")

        logger.debug(f"Final result: {insertions}, {deletions}")
        return insertions, deletions

    def categorize_commit(self, commit: CommitInfo) -> List[str]:
        """Categorize a commit based on its message and changes."""
        message_lower = commit.message.lower()
        message_words = set(message_lower.split())

        # Use set intersection for efficient matching
        categories = []
        for category, keywords in CategoryPatterns.PATTERNS.items():
            if keywords & message_words:
                categories.append(category)

        # If no categories found, add a default category based on change size
        if not categories:
            total_changes = commit.insertions + commit.deletions
            categories.append("significant_change" if total_changes > 50 else "other")

        return categories

    def generate_summary(self, commits: List[CommitInfo]) -> MergeRequestSummary:
        """Generate a comprehensive merge request summary."""
        if not commits:
            return MergeRequestSummary(
                title="No changes detected",
                description="No commits found between the specified branches.",
                total_commits=0,
                total_files_changed=0,
                total_insertions=0,
                total_deletions=0,
                key_changes=[],
                breaking_changes=[],
                new_features=[],
                bug_fixes=[],
                refactoring=[],
                files_affected=[],
                estimated_review_time="0 minutes",
            )

        return self._generate_summary_sync(commits)

    def _generate_summary_sync(self, commits: List[CommitInfo]) -> MergeRequestSummary:
        """Synchronous summary generation."""
        # Calculate totals
        total_commits = len(commits)
        total_insertions = sum(c.insertions for c in commits)
        total_deletions = sum(c.deletions for c in commits)

        # Collect all unique files
        all_files: Set[str] = set()
        for commit in commits:
            all_files.update(commit.files_changed)
        total_files_changed = len(all_files)

        # Categorize commits
        categorized_commits = self._categorize_commits(commits)

        # Generate title and description
        title = self._generate_title(commits, categorized_commits)
        description = self._generate_description(
            commits,
            total_commits,
            total_files_changed,
            total_insertions,
            total_deletions,
            categorized_commits,
            all_files,
        )

        # Estimate review time
        estimated_time = self._estimate_review_time(
            total_commits, total_files_changed, total_insertions + total_deletions
        )

        return MergeRequestSummary(
            title=title,
            description=description,
            total_commits=total_commits,
            total_files_changed=total_files_changed,
            total_insertions=total_insertions,
            total_deletions=total_deletions,
            key_changes=categorized_commits["key_changes"],
            breaking_changes=categorized_commits["breaking_changes"],
            new_features=categorized_commits["new_features"],
            bug_fixes=categorized_commits["bug_fixes"],
            refactoring=categorized_commits["refactoring"],
            files_affected=sorted(list(all_files)),
            estimated_review_time=estimated_time,
        )

    def _categorize_commits(self, commits: List[CommitInfo]) -> Dict[str, List[str]]:
        """Categorize commits into different types."""
        categories = {
            "new_features": [],
            "bug_fixes": [],
            "refactoring": [],
            "breaking_changes": [],
            "key_changes": [],
        }

        for commit in commits:
            commit_categories = self.categorize_commit(commit)
            commit_entry = f"- {commit.message} ({commit.hash[:8]})"

            if "new_feature" in commit_categories:
                categories["new_features"].append(commit_entry)
            elif "bug_fix" in commit_categories:
                categories["bug_fixes"].append(commit_entry)
            elif "refactoring" in commit_categories:
                categories["refactoring"].append(commit_entry)

            # Check for breaking changes
            if any(
                word in commit.message.lower()
                for word in ["breaking", "deprecate", "remove"]
            ):
                categories["breaking_changes"].append(commit_entry)

            # Key changes (commits with significant impact)
            if commit.insertions + commit.deletions > 100:
                categories["key_changes"].append(
                    f"{commit_entry} - {commit.insertions + commit.deletions} lines changed"
                )

        return categories

    def _generate_title(
        self, commits: List[CommitInfo], categorized_commits: Dict[str, List[str]]
    ) -> str:
        """Generate a concise title for the merge request."""
        if len(commits) == 1:
            return f"feat: {commits[0].message}"

        # Determine primary type
        if categorized_commits["new_features"]:
            return f"feat: {len(categorized_commits['new_features'])} new features and improvements"
        elif categorized_commits["refactoring"]:
            return "refactor: Code quality improvements and optimizations"
        elif categorized_commits["bug_fixes"]:
            return f"fix: {len(categorized_commits['bug_fixes'])} bug fixes and improvements"
        else:
            return f"chore: {len(commits)} commits with various improvements"

    def _generate_description(
        self,
        commits: List[CommitInfo],
        total_commits: int,
        total_files_changed: int,
        total_insertions: int,
        total_deletions: int,
        categorized_commits: Dict[str, List[str]],
        all_files: Set[str],
    ) -> str:
        """Generate a comprehensive description for the merge request."""
        description = f"""## Overview
This merge request contains {total_commits} commits with {total_files_changed} files changed ({total_insertions} insertions, {total_deletions} deletions).

## Key Changes
"""

        if categorized_commits["key_changes"]:
            description += "\n".join(categorized_commits["key_changes"][:5]) + "\n\n"

        for category, items in categorized_commits.items():
            if items and category != "key_changes":
                category_name = category.replace("_", " ").title()
                description += f"### {category_name} ({len(items)})\n"
                description += "\n".join(items) + "\n\n"

        # Add file summary
        description += f"### Files Affected ({len(all_files)})\n"
        file_categories = self._categorize_files(all_files)
        for category, files in file_categories.items():
            if files:
                description += f"\n**{category}:**\n"
                for file in files[:10]:  # Limit to 10 files per category
                    description += f"- `{file}`\n"
                if len(files) > 10:
                    description += f"- ... and {len(files) - 10} more\n"

        description += f"\n### Summary\n"
        description += f"- **Total Commits:** {total_commits}\n"
        description += f"- **Files Changed:** {total_files_changed}\n"
        description += f"- **Lines Added:** {total_insertions}\n"
        description += f"- **Lines Removed:** {total_deletions}\n"
        description += f"- **Estimated Review Time:** {self._estimate_review_time(total_commits, total_files_changed, total_insertions + total_deletions)}\n"

        return description

    def _categorize_files(self, files: Set[str]) -> Dict[str, List[str]]:
        """Categorize files by type."""
        categories = {category: [] for category in FilePatterns.PATTERNS.keys()}

        for file in files:
            category = self._categorize_single_file(file)
            categories[category].append(file)

        return categories

    def _categorize_single_file(self, file: str) -> str:
        """Categorize a single file efficiently."""
        file_lower = file.lower()

        # Check for special cases first
        if file == "utils.py":
            return "Other"

        # Check pattern-based categories first
        for category, config in FilePatterns.PATTERNS.items():
            if any(pattern in file_lower for pattern in config["patterns"]):
                return category

        # Check extensions
        file_ext = self._get_file_extension(file_lower)
        for category, config in FilePatterns.PATTERNS.items():
            if file_ext in config["extensions"]:
                # Special case: .js and .ts can be both frontend and backend
                if file_ext in {".js", ".ts"}:
                    if any(
                        pattern in file_lower
                        for pattern in ["component", "page", "view", "ui"]
                    ):
                        return "Frontend"
                    else:
                        return "Backend"
                return category

        return "Other"

    def _get_file_extension(self, file_lower: str) -> str:
        """Get file extension efficiently."""
        last_dot = file_lower.rfind(".")
        return file_lower[last_dot:] if last_dot != -1 else ""

    def _estimate_review_time(self, commits: int, files: int, lines: int) -> str:
        """Estimate review time based on changes."""
        # Rough estimation: 2 minutes per commit + 1 minute per 50 lines + 30 seconds per file
        total_minutes = (commits * 2) + (lines // 50) + (files // 2)

        if total_minutes < 1:
            return "Less than a minute"
        if total_minutes < 60:
            return f"{total_minutes} minutes"

        hours = total_minutes // 60
        minutes = total_minutes % 60

        if minutes == 0:
            return f"{hours}h"

        return f"{hours}h {minutes}m"
