"""MCP Server for generating merge request summaries from git logs."""

import json
import sys
from dataclasses import asdict
from typing import Any, Dict

from .analyzer import GitLogAnalyzer


class MergeRequestSummarizerMCPServer:
    """MCP Server for merge request summarization."""

    def __init__(self) -> None:
        """Initialize the MCP server."""
        self.analyzer = GitLogAnalyzer()

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests."""
        method = request.get("method")
        params = request.get("params", {})

        if method == "tools/list":
            return self.list_tools()
        elif method == "tools/call":
            return self.call_tool(params)
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }

    def list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        return {
            "jsonrpc": "2.0",
            "result": {
                "tools": [
                    {
                        "name": "generate_merge_request_summary",
                        "description": "Generate a comprehensive merge request summary from git logs",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "base_branch": {
                                    "type": "string",
                                    "description": "Base branch to compare against (default: develop)",
                                    "default": "develop",
                                },
                                "current_branch": {
                                    "type": "string",
                                    "description": "Current branch to analyze (default: HEAD)",
                                    "default": "HEAD",
                                },
                                "repo_path": {
                                    "type": "string",
                                    "description": "Repository path (default: current directory)",
                                    "default": ".",
                                },
                                "format": {
                                    "type": "string",
                                    "enum": ["markdown", "json"],
                                    "description": "Output format for the summary",
                                    "default": "markdown",
                                },
                            },
                            "required": [],
                        },
                    },
                    {
                        "name": "analyze_git_commits",
                        "description": "Analyze git commits and categorize them by type",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "base_branch": {
                                    "type": "string",
                                    "description": "Base branch to compare against",
                                    "default": "develop",
                                },
                                "current_branch": {
                                    "type": "string",
                                    "description": "Current branch to analyze",
                                    "default": "HEAD",
                                },
                                "repo_path": {
                                    "type": "string",
                                    "description": "Repository path",
                                    "default": ".",
                                },
                            },
                            "required": [],
                        },
                    },
                ]
            },
        }

    def call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool."""
        name = params.get("name")
        arguments = params.get("arguments", {})

        try:
            if name == "generate_merge_request_summary":
                result = self.generate_merge_request_summary(arguments)
            elif name == "analyze_git_commits":
                result = self.analyze_git_commits(arguments)
            else:
                return {
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": f"Tool not found: {name}"},
                }

            return {
                "jsonrpc": "2.0",
                "result": {"content": [{"type": "text", "text": result}]},
            }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
            }

    def generate_merge_request_summary(self, args: Dict[str, Any]) -> str:
        """Generate a merge request summary."""
        base_branch = args.get("base_branch", "develop")
        current_branch = args.get("current_branch", "HEAD")
        repo_path = args.get("repo_path", ".")
        output_format = args.get("format", "markdown")

        # Update analyzer repo path if specified
        if repo_path != ".":
            self.analyzer = GitLogAnalyzer(repo_path)

        # Get commits and generate summary
        commits = self.analyzer.get_git_log(base_branch, current_branch)
        summary = self.analyzer.generate_summary(commits)

        if output_format == "json":
            return json.dumps(asdict(summary), indent=2)
        else:
            return f"# {summary.title}\n\n{summary.description}"

    def analyze_git_commits(self, args: Dict[str, Any]) -> str:
        """Analyze git commits and provide detailed breakdown."""
        base_branch = args.get("base_branch", "develop")
        current_branch = args.get("current_branch", "HEAD")
        repo_path = args.get("repo_path", ".")

        # Update analyzer repo path if specified
        if repo_path != ".":
            self.analyzer = GitLogAnalyzer(repo_path)

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

        return report


def main() -> None:
    """Main function for MCP server."""
    server = MergeRequestSummarizerMCPServer()

    # Read from stdin, write to stdout
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = server.handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
        except json.JSONDecodeError:
            print(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32700, "message": "Parse error"},
                    }
                )
            )
            sys.stdout.flush()
        except Exception as e:
            print(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}",
                        },
                    }
                )
            )
            sys.stdout.flush()


if __name__ == "__main__":
    main()
