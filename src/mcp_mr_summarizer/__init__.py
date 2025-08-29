"""MCP Merge Request Summarizer.

A tool for generating comprehensive merge request summaries from git logs.
"""

__version__ = "1.0.0"
__author__ = "Joe Luo"
__email__ = "joe.luo@hotmail.com"

from .analyzer import GitLogAnalyzer
from .models import CommitInfo, MergeRequestSummary
from .tools import GitTools

__all__ = [
    "GitLogAnalyzer",
    "CommitInfo",
    "MergeRequestSummary",
    "GitTools",
]
