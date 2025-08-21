"""Git analysis tools for MCP server."""

import json
import time
import sys
import asyncio
from dataclasses import asdict
from typing import Dict, Any
import subprocess

from .analyzer import GitLogAnalyzer


class GitTools:
    """Git analysis tools for generating summaries and analyzing commits."""

    def __init__(self, repo_path: str = "."):
        """Initialize GitTools with repository path."""
        self.repo_path = repo_path
        self._analyzer = None
        print(
            f"[DEBUG] GitTools initialized with repo_path: {repo_path}", file=sys.stderr
        )

    @property
    def analyzer(self):
        """Get or create the analyzer instance."""
        if self._analyzer is None:
            print(f"[DEBUG] Creating new GitLogAnalyzer instance", file=sys.stderr)
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
        print(f"[DEBUG] Starting async generate_merge_request_summary", file=sys.stderr)
        print(
            f"[DEBUG] Parameters: base_branch={base_branch}, current_branch={current_branch}, repo_path={repo_path}, format={format}",
            file=sys.stderr,
        )

        try:
            # Update analyzer repo path if specified
            if repo_path != "." and repo_path != self.repo_path:
                print(
                    f"[DEBUG] Updating analyzer repo_path from {self.repo_path} to {repo_path}",
                    file=sys.stderr,
                )
                self._analyzer = GitLogAnalyzer(repo_path)
                self.repo_path = repo_path

            # Get commits and generate summary with timeout protection
            try:
                print(f"[DEBUG] Calling async analyzer.get_git_log...", file=sys.stderr)
                commits = await self.analyzer.get_git_log(base_branch, current_branch)
                git_time = time.time() - start_time
                print(
                    f"[DEBUG] async get_git_log completed in {git_time:.2f}s, found {len(commits)} commits",
                    file=sys.stderr,
                )

                if not commits:
                    print("[DEBUG] No commits found, returning early", file=sys.stderr)
                    return (
                        f"No commits found between {base_branch} and {current_branch}."
                    )

                print(
                    f"[DEBUG] Calling async analyzer.generate_summary...",
                    file=sys.stderr,
                )
                summary_start = time.time()
                summary = await self.analyzer.generate_summary(commits)
                summary_time = time.time() - summary_start
                print(
                    f"[DEBUG] async generate_summary completed in {summary_time:.2f}s",
                    file=sys.stderr,
                )

                if format == "json":
                    print("[DEBUG] Returning JSON format", file=sys.stderr)
                    return json.dumps(asdict(summary), indent=2)
                else:
                    print("[DEBUG] Returning markdown format", file=sys.stderr)
                    return f"# {summary.title}\n\n{summary.description}"

            except asyncio.TimeoutError:
                print("[ERROR] Async git operation timed out", file=sys.stderr)
                return f"Error: Git operation timed out. Please check if the repository is accessible and the branches exist."
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Git command failed: {e}", file=sys.stderr)
                return f"Error: Git command failed: {e.stderr.decode() if e.stderr else str(e)}"
            except Exception as e:
                print(f"[ERROR] Error processing git data: {e}", file=sys.stderr)
                return f"Error processing git data: {str(e)}"

        except Exception as e:
            print(
                f"[ERROR] Error generating merge request summary: {e}", file=sys.stderr
            )
            return f"Error generating merge request summary: {str(e)}"
        finally:
            total_time = time.time() - start_time
            print(
                f"[DEBUG] async generate_merge_request_summary completed in {total_time:.2f}s",
                file=sys.stderr,
            )

    async def analyze_git_commits(
        self,
        base_branch: str = "master",
        current_branch: str = "HEAD",
        repo_path: str = ".",
    ) -> str:
        """Analyze git commits and categorize them by type asynchronously."""
        start_time = time.time()
        print(f"[DEBUG] Starting async analyze_git_commits", file=sys.stderr)
        print(
            f"[DEBUG] Parameters: base_branch={base_branch}, current_branch={current_branch}, repo_path={repo_path}",
            file=sys.stderr,
        )

        try:
            # Update analyzer repo path if specified
            if repo_path != "." and repo_path != self.repo_path:
                print(
                    f"[DEBUG] Updating analyzer repo_path from {self.repo_path} to {repo_path}",
                    file=sys.stderr,
                )
                self._analyzer = GitLogAnalyzer(repo_path)
                self.repo_path = repo_path

            # Get commits with timeout protection
            try:
                print(f"[DEBUG] Calling async analyzer.get_git_log...", file=sys.stderr)
                commits = await self.analyzer.get_git_log(base_branch, current_branch)
                git_time = time.time() - start_time
                print(
                    f"[DEBUG] async get_git_log completed in {git_time:.2f}s, found {len(commits)} commits",
                    file=sys.stderr,
                )

                if not commits:
                    print("[DEBUG] No commits found, returning early", file=sys.stderr)
                    return "No commits found between the specified branches."

                # Analyze commits asynchronously
                print(f"[DEBUG] Starting async commit analysis...", file=sys.stderr)
                analysis_start = time.time()
                analysis = await self._analyze_commits_async(commits)
                analysis_time = time.time() - analysis_start
                print(
                    f"[DEBUG] Async commit analysis completed in {analysis_time:.2f}s",
                    file=sys.stderr,
                )

                print(f"[DEBUG] Generating async analysis report...", file=sys.stderr)
                report_start = time.time()
                report = await self._generate_analysis_report_async(analysis)
                report_time = time.time() - report_start
                print(
                    f"[DEBUG] Async report generation completed in {report_time:.2f}s",
                    file=sys.stderr,
                )

                return report

            except asyncio.TimeoutError:
                print("[ERROR] Async git operation timed out", file=sys.stderr)
                return f"Error: Git operation timed out. Please check if the repository is accessible and the branches exist."
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Git command failed: {e}", file=sys.stderr)
                return f"Error: Git command failed: {e.stderr.decode() if e.stderr else str(e)}"
            except Exception as e:
                print(f"[ERROR] Error processing git data: {e}", file=sys.stderr)
                return f"Error processing git data: {str(e)}"

        except Exception as e:
            print(f"[ERROR] Error analyzing git commits: {e}", file=sys.stderr)
            return f"Error analyzing git commits: {str(e)}"
        finally:
            total_time = time.time() - start_time
            print(
                f"[DEBUG] async analyze_git_commits completed in {total_time:.2f}s",
                file=sys.stderr,
            )

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
                print(
                    f"[DEBUG] Analyzing commit {i+1}/{len(commits)}: {commit.hash[:8]}",
                    file=sys.stderr,
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
                print(
                    f"[WARNING] Error analyzing commit {commit.hash[:8]}: {e}",
                    file=sys.stderr,
                )
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
                report += f"Error categorizing files: {str(e)}\n\n"
                # Fallback: just list all files
                report += "### All Files\n"
                for file in sorted(analysis["files_affected"])[:20]:
                    report += f"- `{file}`\n"
                if len(analysis["files_affected"]) > 20:
                    report += f"- ... and {len(analysis['files_affected']) - 20} more\n"
                report += "\n"

        return report

    # Keep the old synchronous methods for backward compatibility
    def generate_merge_request_summary_sync(
        self,
        base_branch: str = "develop",
        current_branch: str = "HEAD",
        repo_path: str = ".",
        format: str = "markdown",
    ) -> str:
        """Synchronous version for backward compatibility."""
        # Run the async version in a new event loop
        return asyncio.run(
            self.generate_merge_request_summary(
                base_branch, current_branch, repo_path, format
            )
        )

    def analyze_git_commits_sync(
        self,
        base_branch: str = "develop",
        current_branch: str = "HEAD",
        repo_path: str = ".",
    ) -> str:
        """Synchronous version for backward compatibility."""
        # Run the async version in a new event loop
        return asyncio.run(
            self.analyze_git_commits(base_branch, current_branch, repo_path)
        )
