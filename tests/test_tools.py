"""Tests for the GitTools class."""

import json
import pytest
from unittest.mock import Mock, patch
from dataclasses import asdict
from collections import defaultdict, Counter

from mcp_mr_summarizer.tools import GitTools, GitAnalysisError, AnalysisResult
from mcp_mr_summarizer.models import CommitInfo, MergeRequestSummary


class TestGitTools:
    """Test cases for GitTools."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tools = GitTools("/test/repo")
        # Ensure analyzer is created and accessible
        _ = self.tools.analyzer

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
                files_changed=["src/feature.py"],
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

        # Mock the entire get_git_log method to avoid any git operations
        with patch.object(
            self.tools.analyzer, "get_git_log", return_value=mock_commits
        ):
            self.tools.analyzer.generate_summary = Mock(return_value=mock_summary)

            result = self.tools.generate_merge_request_summary(
                "main", "feature", "/test/repo", "markdown"
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
                files_changed=["src/feature.py"],
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

        # Mock the entire get_git_log method to avoid any git operations
        with patch.object(
            self.tools.analyzer, "get_git_log", return_value=mock_commits
        ):
            self.tools.analyzer.generate_summary = Mock(return_value=mock_summary)

            result = self.tools.generate_merge_request_summary(
                "main", "feature", "/test/repo", "json"
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
            mock_analyzer_instance.get_git_log = Mock(return_value=mock_commits)
            mock_analyzer_instance.generate_summary = Mock(return_value=mock_summary)
            mock_analyzer_class.return_value = mock_analyzer_instance

            # Mock the _with_repo_path_update method to avoid actual git operations
            with patch.object(self.tools, "_with_repo_path_update") as mock_update:
                mock_update.return_value = "# No Changes\n\nNo commits found."

                result = self.tools.generate_merge_request_summary(
                    "main", "feature", custom_path, "markdown"
                )

                # Verify that the update method was called
                mock_update.assert_called_once()
                assert result == "# No Changes\n\nNo commits found."

    def test_generate_merge_request_summary_exception_handling(self):
        """Test exception handling in generate_merge_request_summary."""
        # Mock the _generate_summary_internal method to directly test error handling
        with patch.object(self.tools, "_generate_summary_internal") as mock_internal:
            mock_internal.side_effect = Exception("Git error")

            with pytest.raises(
                GitAnalysisError,
                match="Error during generate_merge_request_summary: Git error",
            ):
                self.tools.generate_merge_request_summary(
                    "main", "feature", "/test/repo"
                )

    def test_analyze_git_commits_success(self):
        """Test successful git commits analysis."""
        # Mock commits
        mock_commits = [
            CommitInfo(
                hash="abc123def456",
                author="Test Author",
                date="2023-01-01",
                message="Fix bug in authentication",
                files_changed=["src/auth.py", "tests/test_auth.py"],
                insertions=20,
                deletions=5,
            ),
            CommitInfo(
                hash="def456ghi789",
                author="Test Author 2",
                date="2023-01-02",
                message="Add new user management feature",
                files_changed=["src/users.py", "src/models.py"],
                insertions=150,
                deletions=10,
            ),
        ]

        # Mock the entire get_git_log method to avoid any git operations
        with patch.object(
            self.tools.analyzer, "get_git_log", return_value=mock_commits
        ):
            self.tools.analyzer.categorize_commit = Mock(
                side_effect=[["bug_fix"], ["new_feature"]]
            )
            self.tools.analyzer._categorize_files = Mock(
                return_value={
                    "Source": ["src/auth.py", "src/users.py", "src/models.py"],
                    "Tests": ["tests/test_auth.py"],
                }
            )

            result = self.tools.analyze_git_commits("main", "feature", "/test/repo")

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
        # Mock the entire get_git_log method to avoid any git operations
        with patch.object(self.tools.analyzer, "get_git_log", return_value=[]):
            result = self.tools.analyze_git_commits("main", "feature", "/test/repo")
            assert result == "No commits found between the specified branches."

    def test_analyze_git_commits_with_custom_repo_path(self):
        """Test git commits analysis with custom repository path."""
        custom_path = "/custom/repo"
        mock_commits = []

        # Mock the analyzer creation
        with patch("mcp_mr_summarizer.tools.GitLogAnalyzer") as mock_analyzer_class:
            mock_analyzer_instance = Mock()
            mock_analyzer_instance.get_git_log = Mock(return_value=mock_commits)
            mock_analyzer_class.return_value = mock_analyzer_instance

            # Mock the _with_repo_path_update method to avoid actual git operations
            with patch.object(self.tools, "_with_repo_path_update") as mock_update:
                mock_update.return_value = (
                    "No commits found between the specified branches."
                )

                result = self.tools.analyze_git_commits(custom_path, "main", "feature")

                # Verify that the update method was called
                mock_update.assert_called_once()
                assert result == "No commits found between the specified branches."

    def test_analyze_git_commits_exception_handling(self):
        """Test exception handling in analyze_git_commits."""
        # Mock the _analyze_commits_internal method to directly test error handling
        with patch.object(self.tools, "_analyze_commits_internal") as mock_internal:
            mock_internal.side_effect = Exception("Git error")

            with pytest.raises(
                GitAnalysisError, match="Error during analyze_git_commits: Git error"
            ):
                self.tools.analyze_git_commits("/test/repo", "main", "feature")

    def test_analyze_git_commits_commit_processing_exception(self):
        """Test that individual commit processing exceptions don't stop analysis."""
        # Mock commits where one will cause an exception
        mock_commits = [
            CommitInfo(
                hash="abc123",
                author="Test Author",
                date="2023-01-01",
                message="Good commit",
                files_changed=["src/file1.py"],
                insertions=10,
                deletions=0,
            ),
            CommitInfo(
                hash="def456",
                author="Test Author 2",
                date="2023-01-02",
                message="Bad commit",
                files_changed=["src/file2.py"],
                insertions=5,
                deletions=0,
            ),
        ]

        # Mock the entire get_git_log method to avoid any git operations
        with patch.object(
            self.tools.analyzer, "get_git_log", return_value=mock_commits
        ):
            # Mock categorize_commit to raise an exception for the second commit
            self.tools.analyzer.categorize_commit = Mock(
                side_effect=[["feature"], Exception("Categorization error")]
            )

            result = self.tools.analyze_git_commits("main", "feature", "/test/repo")

        # Should still generate a report even with the error
        assert "# Git Commit Analysis" in result
        assert "Total Commits:** 2" in result

    def test_generate_analysis_report_empty_analysis(self):
        """Test report generation with empty analysis data."""
        analysis = AnalysisResult(
            total_commits=0,
            total_insertions=0,
            total_deletions=0,
            categories=defaultdict(list),
            significant_changes=[],
            files_affected=set(),
            stats=Counter(),
        )

        result = self.tools._generate_analysis_report_sync(analysis)

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
        analysis = AnalysisResult(
            total_commits=1,
            total_insertions=10,
            total_deletions=5,
            categories=defaultdict(list),
            significant_changes=[],
            files_affected={"src/file1.py", "src/file2.py"},
            stats=Counter(),
        )

        self.tools.analyzer._categorize_files = Mock(
            side_effect=Exception("Categorization error")
        )

        result = self.tools._generate_analysis_report_sync(analysis)

        assert "# Git Commit Analysis" in result
        assert "Error categorizing files:" in result
        assert "### All Files" in result
        assert "src/file1.py" in result
        assert "src/file2.py" in result

    def test_generate_analysis_report_many_files_truncation(self):
        """Test report generation with many files (truncation)."""
        # Create analysis with many files
        many_files = {f"file{i}.py" for i in range(25)}
        analysis = AnalysisResult(
            total_commits=1,
            total_insertions=10,
            total_deletions=5,
            categories=defaultdict(list),
            significant_changes=[],
            files_affected=many_files,
            stats=Counter(),
        )

        self.tools.analyzer._categorize_files = Mock(
            return_value={
                "Source": list(many_files),
            }
        )

        result = self.tools._generate_analysis_report_sync(analysis)

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

        # Mock the entire get_git_log method to avoid any git operations
        with patch.object(self.tools.analyzer, "get_git_log", return_value=[]):
            self.tools.analyzer.generate_summary = Mock(
                return_value=MergeRequestSummary(
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
            )

            # Call with same repo path
            self.tools.generate_merge_request_summary(
                "main", "feature", "/test/repo", "markdown"
            )

        # Analyzer should be the same instance
        assert self.tools.analyzer is original_analyzer
