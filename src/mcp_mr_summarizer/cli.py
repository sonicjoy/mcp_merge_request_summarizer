"""Command-line interface for the MCP merge request summarizer."""

import argparse
import json
import sys
from dataclasses import asdict

from .analyzer import GitLogAnalyzer


def main() -> None:
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Generate merge request summaries from git logs",
        prog="mcp-mr-summarizer",
    )
    parser.add_argument(
        "--base", default="develop", help="Base branch (default: develop)"
    )
    parser.add_argument(
        "--current", default="HEAD", help="Current branch (default: HEAD)"
    )
    parser.add_argument(
        "--repo", default=".", help="Repository path (default: current directory)"
    )
    parser.add_argument("--output", help="Output file for result")
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    args = parser.parse_args()

    try:
        analyzer = GitLogAnalyzer(args.repo)
        commits = analyzer.get_git_log(args.base, args.current)
        summary = analyzer.generate_summary(commits)

        if args.format == "json":
            result = asdict(summary)
            output = json.dumps(result, indent=2)
        else:
            output = f"# {summary.title}\n\n{summary.description}"

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Summary written to {args.output}")
        else:
            print(output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
