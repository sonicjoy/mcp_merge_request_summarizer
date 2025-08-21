"""Command-line interface for the MCP merge request summarizer."""

import argparse
import json
import sys

from .tools import GitTools
from .resources import GitResources


def main() -> None:
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description="MCP Merge Request Summarizer - Git analysis tools and resources",
        prog="mcp-mr-summarizer",
    )

    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Summary command
    summary_parser = subparsers.add_parser(
        "summary", help="Generate merge request summary"
    )
    summary_parser.add_argument(
        "--base", default="develop", help="Base branch (default: develop)"
    )
    summary_parser.add_argument(
        "--current", default="HEAD", help="Current branch (default: HEAD)"
    )
    summary_parser.add_argument(
        "--repo", default=".", help="Repository path (default: current directory)"
    )
    summary_parser.add_argument("--output", help="Output file for result")
    summary_parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="markdown",
        help="Output format (default: markdown)",
    )

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze git commits")
    analyze_parser.add_argument(
        "--base", default="develop", help="Base branch (default: develop)"
    )
    analyze_parser.add_argument(
        "--current", default="HEAD", help="Current branch (default: HEAD)"
    )
    analyze_parser.add_argument(
        "--repo", default=".", help="Repository path (default: current directory)"
    )
    analyze_parser.add_argument("--output", help="Output file for result")

    # Status command
    status_parser = subparsers.add_parser("status", help="Get repository status")
    status_parser.add_argument(
        "--repo", default=".", help="Repository path (default: current directory)"
    )
    status_parser.add_argument("--output", help="Output file for result")

    # Branches command
    branches_parser = subparsers.add_parser("branches", help="List all branches")
    branches_parser.add_argument(
        "--repo", default=".", help="Repository path (default: current directory)"
    )
    branches_parser.add_argument("--output", help="Output file for result")

    # Commits command
    commits_parser = subparsers.add_parser("commits", help="Get commit history")
    commits_parser.add_argument(
        "--base", default="develop", help="Base branch (default: develop)"
    )
    commits_parser.add_argument(
        "--current", default="HEAD", help="Current branch (default: HEAD)"
    )
    commits_parser.add_argument(
        "--repo", default=".", help="Repository path (default: current directory)"
    )
    commits_parser.add_argument("--output", help="Output file for result")

    # Files command
    files_parser = subparsers.add_parser("files", help="Get changed files")
    files_parser.add_argument(
        "--base", default="develop", help="Base branch (default: develop)"
    )
    files_parser.add_argument(
        "--current", default="HEAD", help="Current branch (default: HEAD)"
    )
    files_parser.add_argument(
        "--repo", default=".", help="Repository path (default: current directory)"
    )
    files_parser.add_argument("--output", help="Output file for result")

    # Global arguments
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    args = parser.parse_args()

    # If no command is specified, show help
    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "summary":
            tools = GitTools(args.repo)
            output = tools.generate_merge_request_summary(
                args.base, args.current, args.repo, args.format
            )
        elif args.command == "analyze":
            tools = GitTools(args.repo)
            output = tools.analyze_git_commits(args.base, args.current, args.repo)
        elif args.command == "status":
            resources = GitResources(args.repo)
            output = resources.get_repo_status()
        elif args.command == "branches":
            resources = GitResources(args.repo)
            output = resources.get_branches()
        elif args.command == "commits":
            resources = GitResources(args.repo)
            output = resources.get_commit_history(args.base, args.current)
        elif args.command == "files":
            resources = GitResources(args.repo)
            output = resources.get_changed_files(args.base, args.current)
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            sys.exit(1)

        if hasattr(args, "output") and args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Output written to {args.output}")
        else:
            print(output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
