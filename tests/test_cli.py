"""Tests for the CLI module."""

import json
from unittest.mock import Mock, patch
import pytest

from mcp_mr_summarizer.cli import main
from mcp_mr_summarizer.models import MergeRequestSummary


class TestCLI:
    """Test cases for the CLI."""

    @patch("mcp_mr_summarizer.cli.GitLogAnalyzer")
    @patch("sys.argv", ["mcp-mr-summarizer", "--base", "main", "--current", "feature"])
    def test_main_markdown_output(self, mock_analyzer_class, capsys):
        """Test main function with markdown output."""
        # Mock the analyzer
        mock_analyzer = Mock()
        mock_analyzer_class.return_value = mock_analyzer

        # Mock commits and summary
        mock_commits = [Mock()]
        mock_summary = MergeRequestSummary(
            title="Test Title",
            description="Test Description",
            total_commits=1,
            total_files_changed=1,
            total_insertions=10,
            total_deletions=5,
            key_changes=[],
            breaking_changes=[],
            new_features=[],
            bug_fixes=[],
            refactoring=[],
            files_affected=["test.py"],
            estimated_review_time="5 minutes",
        )

        mock_analyzer.get_git_log.return_value = mock_commits
        mock_analyzer.generate_summary.return_value = mock_summary

        main()

        captured = capsys.readouterr()
        assert "# Test Title" in captured.out
        assert "Test Description" in captured.out

    @patch("mcp_mr_summarizer.cli.GitLogAnalyzer")
    @patch("sys.argv", ["mcp-mr-summarizer", "--format", "json"])
    def test_main_json_output(self, mock_analyzer_class, capsys):
        """Test main function with JSON output."""
        # Mock the analyzer
        mock_analyzer = Mock()
        mock_analyzer_class.return_value = mock_analyzer

        # Mock commits and summary
        mock_commits = [Mock()]
        mock_summary = MergeRequestSummary(
            title="Test Title",
            description="Test Description",
            total_commits=1,
            total_files_changed=1,
            total_insertions=10,
            total_deletions=5,
            key_changes=[],
            breaking_changes=[],
            new_features=[],
            bug_fixes=[],
            refactoring=[],
            files_affected=["test.py"],
            estimated_review_time="5 minutes",
        )

        mock_analyzer.get_git_log.return_value = mock_commits
        mock_analyzer.generate_summary.return_value = mock_summary

        main()

        captured = capsys.readouterr()
        # Should be valid JSON
        result = json.loads(captured.out)
        assert result["title"] == "Test Title"
        assert result["description"] == "Test Description"

    @patch("mcp_mr_summarizer.cli.GitLogAnalyzer")
    @patch("builtins.open", create=True)
    @patch("sys.argv", ["mcp-mr-summarizer", "--output", "test.md"])
    def test_main_file_output(self, mock_open, mock_analyzer_class, capsys):
        """Test main function with file output."""
        # Mock the analyzer
        mock_analyzer = Mock()
        mock_analyzer_class.return_value = mock_analyzer

        # Mock file operations
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Mock commits and summary
        mock_commits = [Mock()]
        mock_summary = MergeRequestSummary(
            title="Test Title",
            description="Test Description",
            total_commits=1,
            total_files_changed=1,
            total_insertions=10,
            total_deletions=5,
            key_changes=[],
            breaking_changes=[],
            new_features=[],
            bug_fixes=[],
            refactoring=[],
            files_affected=["test.py"],
            estimated_review_time="5 minutes",
        )

        mock_analyzer.get_git_log.return_value = mock_commits
        mock_analyzer.generate_summary.return_value = mock_summary

        main()

        # Check that file was written
        mock_file.write.assert_called_once()
        captured = capsys.readouterr()
        assert "Summary written to test.md" in captured.out

    @patch("mcp_mr_summarizer.cli.GitLogAnalyzer")
    @patch("sys.argv", ["mcp-mr-summarizer"])
    def test_main_error_handling(self, mock_analyzer_class, capsys):
        """Test main function error handling."""
        # Mock the analyzer to raise an exception
        mock_analyzer = Mock()
        mock_analyzer_class.return_value = mock_analyzer
        mock_analyzer.get_git_log.side_effect = Exception("Test error")

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error: Test error" in captured.err
