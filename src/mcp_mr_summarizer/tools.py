"""Git analysis tools for MCP server."""

import json
from dataclasses import asdict
from typing import Dict, Any

from .analyzer import GitLogAnalyzer


class GitTools:
    """Git analysis tools for generating summaries and analyzing commits."""

    def __init__(self, repo_path: str = "."):
        """Initialize GitTools with repository path."""
        self.repo_path = repo_path
        self._analyzer = None

    @property
    def analyzer(self):
        """Get or create the analyzer instance."""
        if self._analyzer is None:
            self._analyzer = GitLogAnalyzer(self.repo_path)
        return self._analyzer

    def generate_merge_request_summary(
        self,
        base_branch: str = "develop",
        current_branch: str = "HEAD",
        repo_path: str = ".",
        format: str = "markdown",
    ) -> str:
        """Generate a comprehensive merge request summary from git logs."""
        try:
            # Update analyzer repo path if specified
            if repo_path != "." and repo_path != self.repo_path:
                self._analyzer = GitLogAnalyzer(repo_path)
                self.repo_path = repo_path

            # Get commits and generate summary
            commits = self.analyzer.get_git_log(base_branch, current_branch)
            summary = self.analyzer.generate_summary(commits)

            if format == "json":
                return json.dumps(asdict(summary), indent=2)
            else:
                return f"# {summary.title}\n\n{summary.description}"
        except Exception as e:
            return f"Error generating merge request summary: {str(e)}"

    def analyze_git_commits(
        self,
        base_branch: str = "develop",
        current_branch: str = "HEAD",
        repo_path: str = ".",
    ) -> str:
        """Analyze git commits and categorize them by type."""
        try:
            # Update analyzer repo path if specified
            if repo_path != "." and repo_path != self.repo_path:
                self._analyzer = GitLogAnalyzer(repo_path)
                self.repo_path = repo_path

            # Get commits
            commits = self.analyzer.get_git_log(base_branch, current_branch)

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
                try:
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
                    # Continue processing other commits even if one fails
                    continue

            return self._generate_analysis_report(analysis)

        except Exception as e:
            return f"Error analyzing git commits: {str(e)}"

    def _generate_analysis_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a formatted analysis report from analysis data."""
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
