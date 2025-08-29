"""Tests for the CLI module."""

import json
from unittest.mock import Mock, patch
import pytest

from mcp_mr_summarizer.cli import main



class TestCLI:
    """Test cases for the CLI."""

    @patch("mcp_mr_summarizer.cli.GitTools")
    @patch(
        "sys.argv",
        ["mcp-mr-summarizer", "summary", "--base", "main", "--current", "feature"],
    )
    def test_main_markdown_output(self, mock_tools_class, capsys):
        """Test main function with markdown output."""
        # Mock the tools
        mock_tools = Mock()
        mock_tools_class.return_value = mock_tools

        # Mock the generate_merge_request_summary method
        mock_tools.generate_merge_request_summary = Mock(
            return_value="# Test Title\n\nTest Description"
        )

        main()

        captured = capsys.readouterr()
        assert "# Test Title" in captured.out
        assert "Test Description" in captured.out

    @patch("mcp_mr_summarizer.cli.GitTools")
    @patch("sys.argv", ["mcp-mr-summarizer", "summary", "--format", "json"])
    def test_main_json_output(self, mock_tools_class, capsys):
        """Test main function with JSON output."""
        # Mock the tools
        mock_tools = Mock()
        mock_tools_class.return_value = mock_tools

        # Mock the generate_merge_request_summary method with JSON output
        mock_tools.generate_merge_request_summary = Mock(
            return_value='{"title": "Test Title", "description": "Test Description"}'
        )

        main()

        captured = capsys.readouterr()
        # Should be valid JSON
        result = json.loads(captured.out)
        assert result["title"] == "Test Title"
        assert result["description"] == "Test Description"

    @patch("mcp_mr_summarizer.cli.GitTools")
    @patch("builtins.open", create=True)
    @patch("sys.argv", ["mcp-mr-summarizer", "summary", "--output", "test.md"])
    def test_main_file_output(self, mock_open, mock_tools_class, capsys):
        """Test main function with file output."""
        # Mock the tools
        mock_tools = Mock()
        mock_tools_class.return_value = mock_tools

        # Mock file operations
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Mock the generate_merge_request_summary method
        mock_tools.generate_merge_request_summary = Mock(
            return_value="# Test Title\n\nTest Description"
        )

        main()

        # Check that file was written
        mock_file.write.assert_called_once()
        captured = capsys.readouterr()
        assert "Output written to test.md" in captured.out

    @patch("mcp_mr_summarizer.cli.GitTools")
    @patch("sys.argv", ["mcp-mr-summarizer", "summary"])
    def test_main_error_handling(self, mock_tools_class, capsys):
        """Test main function error handling."""
        # Mock the tools to raise an exception
        mock_tools = Mock()
        mock_tools_class.return_value = mock_tools
        mock_tools.generate_merge_request_summary = Mock(
            side_effect=Exception("Test error")
        )

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error: Test error" in captured.err

    @patch("mcp_mr_summarizer.cli.GitTools")
    @patch(
        "sys.argv",
        ["mcp-mr-summarizer", "analyze", "--base", "main", "--current", "feature"],
    )
    def test_analyze_command(self, mock_tools_class, capsys):
        """Test analyze command."""
        # Mock the tools
        mock_tools = Mock()
        mock_tools_class.return_value = mock_tools

        # Mock the analyze_git_commits method
        mock_tools.analyze_git_commits = Mock(
            return_value="# Git Commit Analysis\n\n## Summary\n- **Total Commits:** 2"
        )

        main()

        captured = capsys.readouterr()
        assert "# Git Commit Analysis" in captured.out
        assert "Total Commits:** 2" in captured.out

    @patch("sys.argv", ["mcp-mr-summarizer"])
    def test_no_command_shows_help(self, capsys):
        """Test that no command shows help."""
        main()

        captured = capsys.readouterr()
        assert "usage:" in captured.out
        assert "Available commands" in captured.out
