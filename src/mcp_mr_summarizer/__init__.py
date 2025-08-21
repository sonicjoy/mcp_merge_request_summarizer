"""MCP Merge Request Summarizer.

A tool for generating comprehensive merge request summaries from git logs.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .analyzer import GitLogAnalyzer
from .models import CommitInfo, MergeRequestSummary

__all__ = ["GitLogAnalyzer", "CommitInfo", "MergeRequestSummary"]
