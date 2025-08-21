"""Tests for the GitTools class."""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from dataclasses import asdict

from mcp_mr_summarizer.tools import GitTools
from mcp_mr_summarizer.models import CommitInfo, MergeRequestSummary


class TestGitTools:
    """Test cases for GitTools."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tools = GitTools("/test/repo")

    def test_init(self):
        """Test GitTools initialization."""
        tools = GitTools("/path/to/repo")
        assert tools.repo_path == "/path/to/repo"
        assert tools.analyzer is not None

    def test_generate_merge_request_summary_markdown(self):
        """Test merge request summary generation in markdown format."""
        # Mock commits and summary
        mock_commits = [
            CommitInfo(
                hash="abc123",
                author="Test Author",
                date="2023-01-01",
                message="Add new feature",
                files_changed={"src/feature.py"},
                insertions=50,
                deletions=10,
            )
        ]
        mock_summary = MergeRequestSummary(
            title="Feature Enhancement",
            description="Added new feature with comprehensive tests and documentation.",
            total_commits=1,
            total_files_changed=1,
            total_insertions=50,
            total_deletions=10,
            key_changes=["Added new feature"],
            breaking_changes=[],
            new_features=["New feature implementation"],
            bug_fixes=[],
            refactoring=[],
            files_affected=["src/feature.py"],
            estimated_review_time="15 minutes",
        )

        self.tools.analyzer.get_git_log = Mock(return_value=mock_commits)
        self.tools.analyzer.generate_summary = Mock(return_value=mock_summary)

        result = self.tools.generate_merge_request_summary(
            "main", "feature", ".", "markdown"
        )

        expected = "# Feature Enhancement\n\nAdded new feature with comprehensive tests and documentation."
        assert result == expected

    def test_generate_merge_request_summary_json(self):
        """Test merge request summary generation in JSON format."""
        # Mock commits and summary
        mock_commits = [
            CommitInfo(
                hash="abc123",
                author="Test Author",
                date="2023-01-01",
                message="Add new feature",
                files_changed={"src/feature.py"},
                insertions=50,
                deletions=10,
            )
        ]
        mock_summary = MergeRequestSummary(
            title="Feature Enhancement",
            description="Added new feature with comprehensive tests and documentation.",
            total_commits=1,
            total_files_changed=1,
            total_insertions=50,
            total_deletions=10,
            key_changes=["Added new feature"],
            breaking_changes=[],
            new_features=["New feature implementation"],
            bug_fixes=[],
            refactoring=[],
            files_affected=["src/feature.py"],
            estimated_review_time="15 minutes",
        )

        self.tools.analyzer.get_git_log = Mock(return_value=mock_commits)
        self.tools.analyzer.generate_summary = Mock(return_value=mock_summary)

        result = self.tools.generate_merge_request_summary(
            "main", "feature", ".", "json"
        )

        # Parse the JSON result to verify structure
        parsed_result = json.loads(result)
        expected_dict = asdict(mock_summary)
        assert parsed_result == expected_dict

    def test_generate_merge_request_summary_with_custom_repo_path(self):
        """Test merge request summary generation with custom repository path."""
        custom_path = "/custom/repo"
        mock_commits = []
        mock_summary = MergeRequestSummary(
            title="No Changes",
            description="No commits found.",
            total_commits=0,
            total_files_changed=0,
            total_insertions=0,
            total_deletions=0,
            key_changes=[],
            breaking_changes=[],
            new_features=[],
            bug_fixes=[],
            refactoring=[],
            files_affected=[],
            estimated_review_time="0 minutes",
        )

        # Mock the analyzer creation and methods
        with patch("mcp_mr_summarizer.tools.GitLogAnalyzer") as mock_analyzer_class:
            mock_analyzer_instance = Mock()
            mock_analyzer_instance.get_git_log.return_value = mock_commits
            mock_analyzer_instance.generate_summary.return_value = mock_summary
            mock_analyzer_class.return_value = mock_analyzer_instance

            result = self.tools.generate_merge_request_summary(
                "main", "feature", custom_path, "markdown"
            )

            # Verify that a new analyzer was created with the custom path
            mock_analyzer_class.assert_called_with(custom_path)
            assert self.tools.repo_path == custom_path

    def test_generate_merge_request_summary_exception_handling(self):
        """Test exception handling in generate_merge_request_summary."""
        self.tools.analyzer.get_git_log = Mock(side_effect=Exception("Git error"))

        result = self.tools.generate_merge_request_summary("main", "feature")
        assert result.startswith("Error generating merge request summary:")

    def test_analyze_git_commits_success(self):
        """Test successful git commits analysis."""
        # Mock commits
        mock_commits = [
            CommitInfo(
                hash="abc123def456",
                author="Test Author",
                date="2023-01-01",
                message="Fix bug in authentication",
                files_changed={"src/auth.py", "tests/test_auth.py"},
                insertions=20,
                deletions=5,
            ),
            CommitInfo(
                hash="def456ghi789",
                author="Test Author 2",
                date="2023-01-02",
                message="Add new user management feature",
                files_changed={"src/users.py", "src/models.py"},
                insertions=150,
                deletions=10,
            ),
        ]

        self.tools.analyzer.get_git_log = Mock(return_value=mock_commits)
        self.tools.analyzer.categorize_commit = Mock(
            side_effect=[["bug_fix"], ["new_feature"]]
        )
        self.tools.analyzer._categorize_files = Mock(
            return_value={
                "Source": ["src/auth.py", "src/users.py", "src/models.py"],
                "Tests": ["tests/test_auth.py"],
            }
        )

        result = self.tools.analyze_git_commits("main", "feature")

        # Verify the report structure
        assert "# Git Commit Analysis" in result
        assert "## Summary" in result
        assert "Total Commits:** 2" in result
        assert "Total Insertions:** 170" in result
        assert "Total Deletions:** 15" in result
        assert "Files Affected:** 4" in result
        assert "## Commit Categories" in result
        assert "### Bug Fix (1)" in result
        assert "### New Feature (1)" in result
        assert "## Significant Changes" in result
        assert "def456gh" in result  # Hash of significant change
        assert "## Files Affected" in result
        assert "### Source" in result
        assert "### Tests" in result

    def test_analyze_git_commits_no_commits(self):
        """Test git commits analysis when no commits are found."""
        self.tools.analyzer.get_git_log = Mock(return_value=[])

        result = self.tools.analyze_git_commits("main", "feature")
        assert result == "No commits found between the specified branches."

    def test_analyze_git_commits_with_custom_repo_path(self):
        """Test git commits analysis with custom repository path."""
        custom_path = "/custom/repo"
        mock_commits = []

        # Mock the analyzer creation
        with patch("mcp_mr_summarizer.tools.GitLogAnalyzer") as mock_analyzer_class:
            mock_analyzer_instance = Mock()
            mock_analyzer_instance.get_git_log.return_value = mock_commits
            mock_analyzer_class.return_value = mock_analyzer_instance

            result = self.tools.analyze_git_commits("main", "feature", custom_path)

            # Verify that a new analyzer was created with the custom path
            mock_analyzer_class.assert_called_with(custom_path)
            assert self.tools.repo_path == custom_path

    def test_analyze_git_commits_exception_handling(self):
        """Test exception handling in analyze_git_commits."""
        self.tools.analyzer.get_git_log = Mock(side_effect=Exception("Git error"))

        result = self.tools.analyze_git_commits("main", "feature")
        assert result.startswith("Error analyzing git commits:")

    def test_analyze_git_commits_commit_processing_exception(self):
        """Test that individual commit processing exceptions don't stop analysis."""
        # Mock commits where one will cause an exception
        mock_commits = [
            CommitInfo(
                hash="abc123",
                author="Test Author",
                date="2023-01-01",
                message="Good commit",
                files_changed={"src/file1.py"},
                insertions=10,
                deletions=0,
            ),
            CommitInfo(
                hash="def456",
                author="Test Author 2",
                date="2023-01-02",
                message="Problematic commit",
                files_changed={"src/file2.py"},
                insertions=20,
                deletions=5,
            ),
        ]

        self.tools.analyzer.get_git_log = Mock(return_value=mock_commits)
        # First call succeeds, second call raises exception
        self.tools.analyzer.categorize_commit = Mock(
            side_effect=[["bug_fix"], Exception("Categorization error")]
        )
        self.tools.analyzer._categorize_files = Mock(
            return_value={
                "Source": ["src/file1.py", "src/file2.py"],
            }
        )

        result = self.tools.analyze_git_commits("main", "feature")

        # Should still generate a report with the successful commit
        assert "# Git Commit Analysis" in result
        assert "Total Commits:** 2" in result
        assert (
            "### Bug Fix (1)" in result
        )  # Only one commit was successfully categorized

    def test_generate_analysis_report_empty_analysis(self):
        """Test report generation with empty analysis data."""
        analysis = {
            "total_commits": 0,
            "total_insertions": 0,
            "total_deletions": 0,
            "categories": {},
            "significant_changes": [],
            "files_affected": set(),
        }

        result = self.tools._generate_analysis_report(analysis)

        assert "# Git Commit Analysis" in result
        assert "Total Commits:** 0" in result
        assert "Total Insertions:** 0" in result
        assert "Total Deletions:** 0" in result
        assert "Files Affected:** 0" in result
        # Should not have categories, significant changes, or files sections
        assert "## Commit Categories" not in result
        assert "## Significant Changes" not in result
        assert "## Files Affected" not in result

    def test_generate_analysis_report_file_categorization_error(self):
        """Test report generation when file categorization fails."""
        analysis = {
            "total_commits": 1,
            "total_insertions": 10,
            "total_deletions": 5,
            "categories": {},
            "significant_changes": [],
            "files_affected": {"src/file1.py", "src/file2.py"},
        }

        self.tools.analyzer._categorize_files = Mock(
            side_effect=Exception("Categorization error")
        )

        result = self.tools._generate_analysis_report(analysis)

        assert "# Git Commit Analysis" in result
        assert "Error categorizing files:" in result
        assert "### All Files" in result
        assert "src/file1.py" in result
        assert "src/file2.py" in result

    def test_generate_analysis_report_many_files_truncation(self):
        """Test report generation with many files (truncation)."""
        # Create analysis with many files
        many_files = {f"file{i}.py" for i in range(25)}
        analysis = {
            "total_commits": 1,
            "total_insertions": 10,
            "total_deletions": 5,
            "categories": {},
            "significant_changes": [],
            "files_affected": many_files,
        }

        self.tools.analyzer._categorize_files = Mock(
            return_value={
                "Source": list(many_files),
            }
        )

        result = self.tools._generate_analysis_report(analysis)

        assert "# Git Commit Analysis" in result
        assert "### Source" in result
        # Should show first 10 files and indicate there are more
        assert "... and 15 more" in result

    def test_repo_path_parameter(self):
        """Test that repo_path parameter is properly used."""
        custom_path = "/custom/repo/path"
        tools = GitTools(custom_path)

        assert tools.repo_path == custom_path
        assert tools.analyzer.repo_path == custom_path

    def test_repo_path_update_same_path(self):
        """Test that analyzer is not recreated when repo_path is the same."""
        original_analyzer = self.tools.analyzer

        # Call with same repo path
        self.tools.analyzer.get_git_log = Mock(return_value=[])
        self.tools.generate_merge_request_summary(
            "main", "feature", "/test/repo", "markdown"
        )

        # Analyzer should be the same instance
        assert self.tools.analyzer is original_analyzer
