"""Data models for the MCP merge request summarizer."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CommitInfo:
    """Represents a single commit with its metadata."""

    hash: str
    author: str
    date: str
    message: str
    files_changed: List[str]
    insertions: int
    deletions: int
    branch: Optional[str] = None


@dataclass
class MergeRequestSummary:
    """Represents a complete merge request summary."""

    title: str
    description: str
    total_commits: int
    total_files_changed: int
    total_insertions: int
    total_deletions: int
    key_changes: List[str]
    breaking_changes: List[str]
    new_features: List[str]
    bug_fixes: List[str]
    refactoring: List[str]
    files_affected: List[str]
    estimated_review_time: str
