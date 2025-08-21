"""Git log analyzer for generating merge request summaries."""

import re
import subprocess
from typing import Dict, List, Optional, Set

from .models import CommitInfo, MergeRequestSummary


class GitLogAnalyzer:
    """Analyzes git logs and generates structured summaries."""

    def __init__(self, repo_path: str = ".") -> None:
        """Initialize the analyzer with a repository path."""
        self.repo_path = repo_path

    def get_git_log(
        self, base_branch: str = "develop", current_branch: str = "HEAD"
    ) -> List[CommitInfo]:
        """Retrieve git log between two branches."""
        try:
            # Get commit hashes first
            cmd_hashes = [
                "git",
                "-C",
                self.repo_path,
                "log",
                f"{base_branch}..{current_branch}",
                "--format=format:%H",
            ]

            result = subprocess.run(
                cmd_hashes, capture_output=True, text=True, check=True
            )
            commit_hashes = result.stdout.strip().split("\n")

            commits = []
            for commit_hash in commit_hashes:
                if commit_hash.strip():
                    # Get detailed info for each commit
                    cmd_details = [
                        "git",
                        "-C",
                        self.repo_path,
                        "show",
                        "--stat",
                        "--format=format:%H|%an|%ad|%s",
                        "--date=short",
                        commit_hash,
                    ]

                    result = subprocess.run(
                        cmd_details, capture_output=True, text=True, check=True
                    )
                    commit_info = self._parse_commit_details(result.stdout, commit_hash)
                    if commit_info:
                        commits.append(commit_info)

            return commits

        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get git log: {e}")

    def _parse_commit_details(
        self, output: str, commit_hash: str
    ) -> Optional[CommitInfo]:
        """Parse detailed commit information from git show output."""
        lines = output.strip().split("\n")

        # Find the commit info line
        commit_info_line = None
        for line in lines:
            if "|" in line and commit_hash in line:
                commit_info_line = line
                break

        if not commit_info_line:
            return None

        # Parse commit info
        parts = commit_info_line.split("|")
        if len(parts) >= 4:
            author = parts[1]
            date = parts[2]
            message = parts[3]

            # Parse stats
            files_changed = []
            insertions = 0
            deletions = 0

            for line in lines:
                if "|" in line and ("insertions" in line or "deletions" in line):
                    # Parse file changes
                    file_part = line.split("|")[0].strip()
                    if file_part and not file_part.startswith("..."):
                        files_changed.append(file_part)

                    # Parse insertions/deletions
                    stats_part = line.split("|")[1].strip()
                    if "insertions" in stats_part and "deletions" in stats_part:
                        match = re.search(
                            r"(\d+)\s+insertions?,\s*(\d+)\s+deletions?", stats_part
                        )
                        if match:
                            insertions = int(match.group(1))
                            deletions = int(match.group(2))

            return CommitInfo(
                hash=commit_hash,
                author=author,
                date=date,
                message=message,
                files_changed=files_changed,
                insertions=insertions,
                deletions=deletions,
            )

        return None

    def categorize_commit(self, commit: CommitInfo) -> List[str]:
        """Categorize a commit based on its message and changes."""
        categories = []
        message_lower = commit.message.lower()

        # Check for common patterns
        if any(word in message_lower for word in ["refactor", "refactoring"]):
            categories.append("refactoring")

        if any(word in message_lower for word in ["fix", "bug", "issue", "error"]):
            categories.append("bug_fix")

        if any(
            word in message_lower for word in ["add", "new", "feature", "implement"]
        ):
            categories.append("new_feature")

        if any(word in message_lower for word in ["remove", "delete", "cleanup"]):
            categories.append("cleanup")

        if any(word in message_lower for word in ["update", "upgrade", "bump"]):
            categories.append("update")

        if any(word in message_lower for word in ["test", "spec"]):
            categories.append("test")

        if any(word in message_lower for word in ["docs", "documentation", "readme"]):
            categories.append("documentation")

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
        new_features = []
        bug_fixes = []
        refactoring = []
        breaking_changes = []
        key_changes = []

        for commit in commits:
            categories = self.categorize_commit(commit)

            if "new_feature" in categories:
                new_features.append(f"- {commit.message} ({commit.hash[:8]})")
            elif "bug_fix" in categories:
                bug_fixes.append(f"- {commit.message} ({commit.hash[:8]})")
            elif "refactoring" in categories:
                refactoring.append(f"- {commit.message} ({commit.hash[:8]})")

            # Check for breaking changes
            if any(
                word in commit.message.lower()
                for word in ["breaking", "deprecate", "remove"]
            ):
                breaking_changes.append(f"- {commit.message} ({commit.hash[:8]})")

            # Key changes (commits with significant impact)
            if commit.insertions + commit.deletions > 100:
                key_changes.append(
                    f"- {commit.message} ({commit.hash[:8]}) - "
                    f"{commit.insertions + commit.deletions} lines changed"
                )

        # Generate title
        title = self._generate_title(commits, new_features, refactoring, bug_fixes)

        # Generate description
        description = self._generate_description(
            commits,
            total_commits,
            total_files_changed,
            total_insertions,
            total_deletions,
            new_features,
            bug_fixes,
            refactoring,
            breaking_changes,
            key_changes,
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
            key_changes=key_changes,
            breaking_changes=breaking_changes,
            new_features=new_features,
            bug_fixes=bug_fixes,
            refactoring=refactoring,
            files_affected=sorted(list(all_files)),
            estimated_review_time=estimated_time,
        )

    def _generate_title(
        self,
        commits: List[CommitInfo],
        new_features: List[str],
        refactoring: List[str],
        bug_fixes: List[str],
    ) -> str:
        """Generate a concise title for the merge request."""
        if len(commits) == 1:
            return f"feat: {commits[0].message}"

        # Determine primary type
        if new_features:
            return f"feat: {len(new_features)} new features and improvements"
        elif refactoring:
            return "refactor: Code quality improvements and optimizations"
        elif bug_fixes:
            return f"fix: {len(bug_fixes)} bug fixes and improvements"
        else:
            return f"chore: {len(commits)} commits with various improvements"

    def _generate_description(
        self,
        commits: List[CommitInfo],
        total_commits: int,
        total_files_changed: int,
        total_insertions: int,
        total_deletions: int,
        new_features: List[str],
        bug_fixes: List[str],
        refactoring: List[str],
        breaking_changes: List[str],
        key_changes: List[str],
        all_files: Set[str],
    ) -> str:
        """Generate a comprehensive description for the merge request."""
        description = f"""## Overview
This merge request contains {total_commits} commits with {total_files_changed} files changed ({total_insertions} insertions, {total_deletions} deletions).

## Key Changes
"""

        if key_changes:
            description += "\n".join(key_changes[:5]) + "\n\n"

        if new_features:
            description += f"### 🚀 New Features ({len(new_features)})\n"
            description += "\n".join(new_features) + "\n\n"

        if refactoring:
            description += f"### 🔧 Refactoring ({len(refactoring)})\n"
            description += "\n".join(refactoring) + "\n\n"

        if bug_fixes:
            description += f"### 🐛 Bug Fixes ({len(bug_fixes)})\n"
            description += "\n".join(bug_fixes) + "\n\n"

        if breaking_changes:
            description += f"### ⚠️ Breaking Changes ({len(breaking_changes)})\n"
            description += "\n".join(breaking_changes) + "\n\n"

        # Add file summary
        description += f"### 📁 Files Affected ({len(all_files)})\n"
        file_categories = self._categorize_files(all_files)
        for category, files in file_categories.items():
            if files:
                description += f"\n**{category}:**\n"
                for file in files[:10]:  # Limit to 10 files per category
                    description += f"- `{file}`\n"
                if len(files) > 10:
                    description += f"- ... and {len(files) - 10} more\n"

        description += f"\n### 📊 Summary\n"
        description += f"- **Total Commits:** {total_commits}\n"
        description += f"- **Files Changed:** {total_files_changed}\n"
        description += f"- **Lines Added:** {total_insertions}\n"
        description += f"- **Lines Removed:** {total_deletions}\n"
        description += f"- **Estimated Review Time:** {self._estimate_review_time(total_commits, total_files_changed, total_insertions + total_deletions)}\n"

        return description

    def _categorize_files(self, files: Set[str]) -> Dict[str, List[str]]:
        """Categorize files by type."""
        categories = {
            "Services": [],
            "Models": [],
            "Controllers": [],
            "Tests": [],
            "Configuration": [],
            "Documentation": [],
            "Other": [],
        }

        for file in files:
            if "Service" in file or "service" in file:
                categories["Services"].append(file)
            elif "Model" in file or "model" in file or "Entity" in file:
                categories["Models"].append(file)
            elif "Controller" in file or "controller" in file:
                categories["Controllers"].append(file)
            elif "Test" in file or "test" in file or "Spec" in file:
                categories["Tests"].append(file)
            elif any(
                ext in file for ext in [".json", ".config", ".yml", ".yaml", ".xml"]
            ):
                categories["Configuration"].append(file)
            elif any(ext in file for ext in [".md", ".txt", ".rst"]):
                categories["Documentation"].append(file)
            else:
                categories["Other"].append(file)

        return categories

    def _estimate_review_time(self, commits: int, files: int, lines: int) -> str:
        """Estimate review time based on changes."""
        # Rough estimation: 2 minutes per commit + 1 minute per 50 lines + 30 seconds per file
        total_minutes = (commits * 2) + (lines // 50) + (files // 2)

        if total_minutes < 60:
            return f"{total_minutes} minutes"
        else:
            hours = total_minutes // 60
            minutes = total_minutes % 60
            return f"{hours}h {minutes}m"
