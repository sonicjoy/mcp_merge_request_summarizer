"""Git analysis tools for MCP server."""

import json
import time
import asyncio
import logging
from dataclasses import asdict
from typing import Dict, Any

from .analyzer import GitLogAnalyzer

# Create logger for this module
logger = logging.getLogger(__name__)


class GitTools:
    """Git analysis tools for generating summaries and analyzing commits."""

    def __init__(self, repo_path: str = "."):
        """Initialize GitTools with repository path."""
        self.repo_path = repo_path
        self._analyzer = None
        logger.debug(f"GitTools initialized with repo_path: {repo_path}")

    @property
    def analyzer(self):
        """Get or create the analyzer instance."""
        if self._analyzer is None:
            logger.debug("Creating new GitLogAnalyzer instance")
            self._analyzer = GitLogAnalyzer(self.repo_path)
        return self._analyzer

    async def generate_merge_request_summary(
        self,
        base_branch: str = "master",
        current_branch: str = "HEAD",
        repo_path: str = ".",
        format: str = "markdown",
    ) -> str:
        """Generate a comprehensive merge request summary from git logs asynchronously."""
        start_time = time.time()
        logger.debug("Starting async generate_merge_request_summary")
        logger.debug(
            f"Parameters: base_branch={base_branch}, current_branch={current_branch}, repo_path={repo_path}, format={format}"
        )

        try:
            # Update analyzer repo path if specified
            if repo_path != self.repo_path:
                logger.debug(
                    f"Updating analyzer repo_path from {self.repo_path} to {repo_path}"
                )
                self._analyzer = GitLogAnalyzer(repo_path)
                self.repo_path = repo_path

            # Get commits and generate summary with timeout protection
            try:
                logger.debug("Calling async analyzer.get_git_log...")
                commits = await self.analyzer.get_git_log(base_branch, current_branch)
                git_time = time.time() - start_time
                logger.debug(
                    f"async get_git_log completed in {git_time:.2f}s, found {len(commits)} commits"
                )

                if not commits:
                    logger.debug("No commits found, returning early")
                    return (
                        f"No commits found between {base_branch} and {current_branch}."
                    )

                logger.debug("Calling analyzer.generate_summary...")
                summary_start = time.time()
                summary = self.analyzer.generate_summary(commits)
                summary_time = time.time() - summary_start
                logger.debug(f"generate_summary completed in {summary_time:.2f}s")

                if format == "json":
                    logger.debug("Returning JSON format")
                    return json.dumps(asdict(summary), indent=2)
                else:
                    logger.debug("Returning markdown format")
                    return f"# {summary.title}\n\n{summary.description}"

            except asyncio.TimeoutError:
                logger.error("Async git operation timed out")
                return f"Error: Git operation timed out. Please check if the repository is accessible and the branches exist."
            except Exception as e:
                logger.error(f"Error processing git data: {e}")
                return f"Error processing git data: {str(e)}"

        except Exception as e:
            logger.error(f"Error generating merge request summary: {e}")
            return f"Error generating merge request summary: {str(e)}"
        finally:
            total_time = time.time() - start_time
            logger.debug(
                f"async generate_merge_request_summary completed in {total_time:.2f}s"
            )

    async def analyze_git_commits(
        self,
        base_branch: str = "master",
        current_branch: str = "HEAD",
        repo_path: str = ".",
    ) -> str:
        """Analyze git commits and categorize them by type asynchronously."""
        start_time = time.time()
        logger.debug("Starting async analyze_git_commits")
        logger.debug(
            f"Parameters: base_branch={base_branch}, current_branch={current_branch}, repo_path={repo_path}"
        )

        try:
            # Update analyzer repo path if specified
            if repo_path != self.repo_path:
                logger.debug(
                    f"Updating analyzer repo_path from {self.repo_path} to {repo_path}"
                )
                self._analyzer = GitLogAnalyzer(repo_path)
                self.repo_path = repo_path

            # Get commits with timeout protection
            try:
                logger.debug("Calling async analyzer.get_git_log...")
                commits = await self.analyzer.get_git_log(base_branch, current_branch)
                git_time = time.time() - start_time
                logger.debug(
                    f"async get_git_log completed in {git_time:.2f}s, found {len(commits)} commits"
                )

                if not commits:
                    logger.debug("No commits found, returning early")
                    return "No commits found between the specified branches."

                # Analyze commits asynchronously
                logger.debug("Starting async commit analysis...")
                analysis_start = time.time()
                analysis = await self._analyze_commits_async(commits)
                analysis_time = time.time() - analysis_start
                logger.debug(f"Async commit analysis completed in {analysis_time:.2f}s")

                logger.debug("Generating async analysis report...")
                report_start = time.time()
                report = await self._generate_analysis_report_async(analysis)
                report_time = time.time() - report_start
                logger.debug(f"Async report generation completed in {report_time:.2f}s")

                return report

            except asyncio.TimeoutError:
                logger.error("Async git operation timed out")
                return f"Error: Git operation timed out. Please check if the repository is accessible and the branches exist."
            except Exception as e:
                logger.error(f"Error processing git data: {e}")
                return f"Error processing git data: {str(e)}"

        except Exception as e:
            logger.error(f"Error analyzing git commits: {e}")
            return f"Error analyzing git commits: {str(e)}"
        finally:
            total_time = time.time() - start_time
            logger.debug(f"async analyze_git_commits completed in {total_time:.2f}s")

    async def _analyze_commits_async(self, commits) -> Dict[str, Any]:
        """Analyze commits asynchronously."""
        # Run analysis in thread pool to avoid blocking
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._analyze_commits_sync, commits)

    def _analyze_commits_sync(self, commits) -> Dict[str, Any]:
        """Synchronous commit analysis (runs in thread pool)."""
        analysis = {
            "total_commits": len(commits),
            "total_insertions": sum(c.insertions for c in commits),
            "total_deletions": sum(c.deletions for c in commits),
            "categories": {},
            "significant_changes": [],
            "files_affected": set(),
        }

        for i, commit in enumerate(commits):
            try:
                logger.debug(
                    f"Analyzing commit {i+1}/{len(commits)}: {commit.hash[:8]}"
                )
                categories = self.analyzer.categorize_commit(commit)
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
            except Exception as e:
                logger.warning(f"Error analyzing commit {commit.hash[:8]}: {e}")
                # Continue processing other commits even if one fails
                continue

        return analysis

    async def _generate_analysis_report_async(self, analysis: Dict[str, Any]) -> str:
        """Generate analysis report asynchronously."""
        # Run report generation in thread pool to avoid blocking
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, self._generate_analysis_report_sync, analysis
        )

    def _generate_analysis_report_sync(self, analysis: Dict[str, Any]) -> str:
        """Synchronous report generation (runs in thread pool)."""
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
            try:
                file_categories = self.analyzer._categorize_files(
                    analysis["files_affected"]
                )
                for category, files in file_categories.items():
                    if files:
                        report += f"### {category}\n"
                        for file in sorted(files)[:10]:
                            report += f"- `{file}`\n"
                        if len(files) > 10:
                            report += f"- ... and {len(files) - 10} more\n"
                        report += "\n"
            except Exception as e:
                logger.error(f"Error categorizing files: {e}")
                report += f"Error categorizing files: {str(e)}\n\n"
                # Fallback: just list all files
                report += "### All Files\n"
                for file in sorted(analysis["files_affected"])[:20]:
                    report += f"- `{file}`\n"
                if len(analysis["files_affected"]) > 20:
                    report += f"- ... and {len(analysis['files_affected']) - 20} more\n"
                report += "\n"

        return report
