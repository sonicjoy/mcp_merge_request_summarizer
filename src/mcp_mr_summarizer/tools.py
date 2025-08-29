"""Git analysis tools for MCP server."""

import json
import time
import asyncio
import logging
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, Callable, Awaitable
from collections import defaultdict, Counter
from contextlib import asynccontextmanager

from .analyzer import GitLogAnalyzer

# Create logger for this module
logger = logging.getLogger(__name__)


# Custom exceptions for better error handling
class GitAnalysisError(Exception):
    """Base exception for git analysis errors."""

    pass


class GitTimeoutError(GitAnalysisError):
    """Raised when git operations timeout."""

    pass


class GitRepositoryError(GitAnalysisError):
    """Raised when repository is invalid or inaccessible."""

    pass


@dataclass
class AnalysisConfig:
    """Configuration for git analysis."""

    significant_change_threshold: int = 100
    max_files_displayed: int = 10
    timeout_seconds: int = 30
    default_format: str = "markdown"
    batch_size: int = 100


@dataclass
class AnalysisResult:
    """Structured analysis result."""

    total_commits: int
    total_insertions: int
    total_deletions: int
    categories: Dict[str, list]
    significant_changes: list
    files_affected: set
    stats: Counter


class GitTools:
    """Git analysis tools for generating summaries and analyzing commits."""

    def __init__(
        self, repo_path: str = ".", analyzer_factory: Optional[Callable] = None
    ):
        """Initialize GitTools with repository path and optional analyzer factory."""
        self.repo_path = repo_path
        self._analyzer_factory = analyzer_factory or GitLogAnalyzer
        self._analyzer = None
        self.config = AnalysisConfig()
        logger.debug(f"GitTools initialized with repo_path: {repo_path}")

    @property
    def analyzer(self):
        """Get or create the analyzer instance."""
        if self._analyzer is None:
            logger.debug("Creating new GitLogAnalyzer instance")
            self._analyzer = self._analyzer_factory(self.repo_path)
        return self._analyzer

    async def _with_repo_path_update(
        self, repo_path: str, operation: Callable[[], Awaitable[Any]]
    ) -> Any:
        """Execute operation with repo path update if needed."""
        if repo_path != self.repo_path:
            logger.debug(
                f"Updating analyzer repo_path from {self.repo_path} to {repo_path}"
            )
            self._analyzer = self._analyzer_factory(repo_path)
            self.repo_path = repo_path
        return await operation()

    async def _with_error_handling(
        self, operation: Callable[[], Awaitable[Any]], operation_name: str
    ) -> Any:
        """Execute operation with standardized error handling."""
        start_time = time.time()
        logger.debug(f"Starting {operation_name}")

        try:
            result = await operation()
            total_time = time.time() - start_time
            logger.debug(f"{operation_name} completed in {total_time:.2f}s")
            return result
        except asyncio.TimeoutError:
            logger.error(f"{operation_name} timed out")
            raise GitTimeoutError(f"Git operation timed out during {operation_name}")
        except Exception as e:
            logger.error(f"Error in {operation_name}: {e}")
            raise GitAnalysisError(f"Error during {operation_name}: {str(e)}")

    @asynccontextmanager
    async def git_analysis_session(self, repo_path: str):
        """Context manager for git analysis sessions."""
        try:
            analyzer = self._get_analyzer(repo_path)
            yield analyzer
        finally:
            await self._cleanup_resources()

    def _get_analyzer(self, repo_path: str):
        """Get analyzer for specific repo path."""
        if repo_path != self.repo_path:
            return self._analyzer_factory(repo_path)
        return self.analyzer

    async def _cleanup_resources(self):
        """Clean up resources after analysis."""
        # Currently no cleanup needed, but provides hook for future resource management
        pass

    async def generate_merge_request_summary(
        self,
        base_branch: str = "master",
        current_branch: str = "HEAD",
        repo_path: str = ".",
        format: str = "markdown",
    ) -> str:
        """Generate a comprehensive merge request summary from git logs asynchronously."""

        async def _generate_summary():
            return await self._with_repo_path_update(
                repo_path,
                lambda: self._generate_summary_internal(
                    base_branch, current_branch, format
                ),
            )

        return await self._with_error_handling(
            _generate_summary, "generate_merge_request_summary"
        )

    async def _generate_summary_internal(
        self, base_branch: str, current_branch: str, format: str
    ) -> str:
        """Internal implementation of summary generation."""
        commits = await self.analyzer.get_git_log(base_branch, current_branch)

        if not commits:
            return f"No commits found between {base_branch} and {current_branch}."

        summary = self.analyzer.generate_summary(commits)

        if format == "json":
            return json.dumps(asdict(summary), indent=2)
        else:
            return f"# {summary.title}\n\n{summary.description}"

    async def analyze_git_commits(
        self,
        base_branch: str = "master",
        current_branch: str = "HEAD",
        repo_path: str = ".",
    ) -> str:
        """Analyze git commits and categorize them by type asynchronously."""

        async def _analyze_commits():
            return await self._with_repo_path_update(
                repo_path,
                lambda: self._analyze_commits_internal(base_branch, current_branch),
            )

        return await self._with_error_handling(_analyze_commits, "analyze_git_commits")

    async def _analyze_commits_internal(
        self, base_branch: str, current_branch: str
    ) -> str:
        """Internal implementation of commit analysis."""
        commits = await self.analyzer.get_git_log(base_branch, current_branch)

        if not commits:
            return "No commits found between the specified branches."

        analysis = await self._analyze_commits_async(commits)
        return await self._generate_analysis_report_async(analysis)

    async def _analyze_commits_async(self, commits) -> AnalysisResult:
        """Analyze commits asynchronously with improved performance."""
        if len(commits) <= self.config.batch_size:
            return self._analyze_commits_sync(commits)

        # Process in batches for large commit sets
        results = []
        for i in range(0, len(commits), self.config.batch_size):
            batch = commits[i : i + self.config.batch_size]
            result = self._analyze_commits_sync(batch)
            results.append(result)

        return self._merge_batch_results(results)

    def _analyze_commits_sync(self, commits) -> AnalysisResult:
        """Synchronous commit analysis with improved data structures."""
        analysis = AnalysisResult(
            total_commits=len(commits),
            total_insertions=0,
            total_deletions=0,
            categories=defaultdict(list),
            significant_changes=[],
            files_affected=set(),
            stats=Counter(),
        )

        for i, commit in enumerate(commits):
            try:
                logger.debug(
                    f"Analyzing commit {i+1}/{len(commits)}: {commit.hash[:8]}"
                )

                # Update totals
                analysis.total_insertions += commit.insertions
                analysis.total_deletions += commit.deletions

                # Categorize commit
                categories = self.analyzer.categorize_commit(commit)
                for category in categories:
                    analysis.categories[category].append(
                        {
                            "hash": commit.hash[:8],
                            "message": commit.message,
                            "insertions": commit.insertions,
                            "deletions": commit.deletions,
                        }
                    )

                # Track files affected
                analysis.files_affected.update(commit.files_changed)

                # Track significant changes
                total_lines = commit.insertions + commit.deletions
                if total_lines > self.config.significant_change_threshold:
                    analysis.significant_changes.append(
                        {
                            "hash": commit.hash[:8],
                            "message": commit.message,
                            "total_lines": total_lines,
                        }
                    )

                # Update stats
                analysis.stats["total_lines"] += total_lines
                analysis.stats["files_changed"] += len(commit.files_changed)

            except Exception as e:
                logger.warning(f"Error analyzing commit {commit.hash[:8]}: {e}")
                continue

        return analysis

    def _merge_batch_results(self, results: list[AnalysisResult]) -> AnalysisResult:
        """Merge multiple batch analysis results into a single result."""
        if not results:
            return AnalysisResult(0, 0, 0, defaultdict(list), [], set(), Counter())

        merged = results[0]
        for result in results[1:]:
            merged.total_commits += result.total_commits
            merged.total_insertions += result.total_insertions
            merged.total_deletions += result.total_deletions
            merged.significant_changes.extend(result.significant_changes)
            merged.files_affected.update(result.files_affected)
            merged.stats.update(result.stats)

            for category, commits in result.categories.items():
                merged.categories[category].extend(commits)

        return merged

    async def _generate_analysis_report_async(self, analysis: AnalysisResult) -> str:
        """Generate analysis report asynchronously."""
        # This is CPU-bound, so we can run it directly without executor
        return self._generate_analysis_report_sync(analysis)

    def _generate_analysis_report_sync(self, analysis: AnalysisResult) -> str:
        """Synchronous report generation with improved formatting."""
        report_parts = [
            "# Git Commit Analysis\n\n",
            "## Summary\n",
            f"- **Total Commits:** {analysis.total_commits}\n",
            f"- **Total Insertions:** {analysis.total_insertions}\n",
            f"- **Total Deletions:** {analysis.total_deletions}\n",
            f"- **Files Affected:** {len(analysis.files_affected)}\n\n",
        ]

        # Add categories section
        if analysis.categories:
            report_parts.append("## Commit Categories\n\n")
            for category, commits_list in analysis.categories.items():
                report_parts.append(
                    f"### {category.replace('_', ' ').title()} ({len(commits_list)})\n"
                )
                for commit_info in commits_list:
                    report_parts.append(
                        f"- `{commit_info['hash']}` {commit_info['message']} "
                        f"(+{commit_info['insertions']}/-{commit_info['deletions']})\n"
                    )
                report_parts.append("\n")

        # Add significant changes section
        if analysis.significant_changes:
            report_parts.append("## Significant Changes\n\n")
            for change in analysis.significant_changes:
                report_parts.append(
                    f"- `{change['hash']}` {change['message']} ({change['total_lines']} lines)\n"
                )
            report_parts.append("\n")

        # Add files affected section
        if analysis.files_affected:
            report_parts.extend(self._generate_files_section(analysis.files_affected))

        return "".join(report_parts)

    def _generate_files_section(self, files_affected: set) -> list[str]:
        """Generate the files affected section with error handling."""
        section_parts = ["## Files Affected\n\n"]

        try:
            file_categories = self.analyzer._categorize_files(files_affected)
            for category, files in file_categories.items():
                if files:
                    section_parts.append(f"### {category}\n")
                    sorted_files = sorted(files)
                    for file in sorted_files[: self.config.max_files_displayed]:
                        section_parts.append(f"- `{file}`\n")
                    if len(files) > self.config.max_files_displayed:
                        section_parts.append(
                            f"- ... and {len(files) - self.config.max_files_displayed} more\n"
                        )
                    section_parts.append("\n")
        except Exception as e:
            logger.error(f"Error categorizing files: {e}")
            section_parts.append(f"Error categorizing files: {str(e)}\n\n")
            # Fallback: just list all files
            section_parts.append("### All Files\n")
            sorted_files = sorted(files_affected)
            for file in sorted_files[: self.config.max_files_displayed * 2]:
                section_parts.append(f"- `{file}`\n")
            if len(files_affected) > self.config.max_files_displayed * 2:
                section_parts.append(
                    f"- ... and {len(files_affected) - self.config.max_files_displayed * 2} more\n"
                )
            section_parts.append("\n")

        return section_parts
