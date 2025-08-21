"""Tests for the CLI module."""

import json
from unittest.mock import Mock, patch, AsyncMock
import pytest

from mcp_mr_summarizer.cli import main


@pytest.mark.asyncio
class TestCLI:
    """Test cases for the CLI."""

    @patch("mcp_mr_summarizer.cli.GitTools")
    @patch(
        "sys.argv",
        ["mcp-mr-summarizer", "summary", "--base", "main", "--current", "feature"],
    )
    async def test_main_markdown_output(self, mock_tools_class, capsys):
        """Test main function with markdown output."""
        # Mock the tools
        mock_tools = Mock()
        mock_tools_class.return_value = mock_tools

        # Mock the generate_merge_request_summary method
        mock_tools.generate_merge_request_summary = AsyncMock(
            return_value="# Test Title\n\nTest Description"
        )

        await main()

        captured = capsys.readouterr()
        assert "# Test Title" in captured.out
        assert "Test Description" in captured.out

    @patch("mcp_mr_summarizer.cli.GitTools")
    @patch("sys.argv", ["mcp-mr-summarizer", "summary", "--format", "json"])
    async def test_main_json_output(self, mock_tools_class, capsys):
        """Test main function with JSON output."""
        # Mock the tools
        mock_tools = Mock()
        mock_tools_class.return_value = mock_tools

        # Mock the generate_merge_request_summary method with JSON output
        mock_tools.generate_merge_request_summary = AsyncMock(
            return_value='{"title": "Test Title", "description": "Test Description"}'
        )

        await main()

        captured = capsys.readouterr()
        # Should be valid JSON
        result = json.loads(captured.out)
        assert result["title"] == "Test Title"
        assert result["description"] == "Test Description"

    @patch("mcp_mr_summarizer.cli.GitTools")
    @patch("builtins.open", create=True)
    @patch("sys.argv", ["mcp-mr-summarizer", "summary", "--output", "test.md"])
    async def test_main_file_output(self, mock_open, mock_tools_class, capsys):
        """Test main function with file output."""
        # Mock the tools
        mock_tools = Mock()
        mock_tools_class.return_value = mock_tools

        # Mock file operations
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Mock the generate_merge_request_summary method
        mock_tools.generate_merge_request_summary = AsyncMock(
            return_value="# Test Title\n\nTest Description"
        )

        await main()

        # Check that file was written
        mock_file.write.assert_called_once()
        captured = capsys.readouterr()
        assert "Output written to test.md" in captured.out

    @patch("mcp_mr_summarizer.cli.GitTools")
    @patch("sys.argv", ["mcp-mr-summarizer", "summary"])
    async def test_main_error_handling(self, mock_tools_class, capsys):
        """Test main function error handling."""
        # Mock the tools to raise an exception
        mock_tools = Mock()
        mock_tools_class.return_value = mock_tools
        mock_tools.generate_merge_request_summary = AsyncMock(
            side_effect=Exception("Test error")
        )

        with pytest.raises(SystemExit) as exc_info:
            await main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error: Test error" in captured.err

    @patch("mcp_mr_summarizer.cli.GitTools")
    @patch(
        "sys.argv",
        ["mcp-mr-summarizer", "analyze", "--base", "main", "--current", "feature"],
    )
    async def test_analyze_command(self, mock_tools_class, capsys):
        """Test analyze command."""
        # Mock the tools
        mock_tools = Mock()
        mock_tools_class.return_value = mock_tools

        # Mock the analyze_git_commits method
        mock_tools.analyze_git_commits = AsyncMock(
            return_value="# Git Commit Analysis\n\n## Summary\n- **Total Commits:** 2"
        )

        await main()

        captured = capsys.readouterr()
        assert "# Git Commit Analysis" in captured.out
        assert "Total Commits:** 2" in captured.out

    @patch("mcp_mr_summarizer.cli.GitResources")
    @patch("sys.argv", ["mcp-mr-summarizer", "status"])
    async def test_status_command(self, mock_resources_class, capsys):
        """Test status command."""
        # Mock the resources
        mock_resources = Mock()
        mock_resources_class.return_value = mock_resources

        # Mock the get_repo_status method
        mock_resources.get_repo_status = AsyncMock(
            return_value='{"repository": "test-repo", "current_branch": "main"}'
        )

        await main()

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["repository"] == "test-repo"
        assert result["current_branch"] == "main"

    @patch("mcp_mr_summarizer.cli.GitResources")
    @patch("sys.argv", ["mcp-mr-summarizer", "branches"])
    async def test_branches_command(self, mock_resources_class, capsys):
        """Test branches command."""
        # Mock the resources
        mock_resources = Mock()
        mock_resources_class.return_value = mock_resources

        # Mock the get_branches method
        mock_resources.get_branches = AsyncMock(
            return_value='{"local_branches": ["main", "feature"], "current_branch": "main"}'
        )

        await main()

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["local_branches"] == ["main", "feature"]
        assert result["current_branch"] == "main"

    @patch("mcp_mr_summarizer.cli.GitResources")
    @patch(
        "sys.argv",
        ["mcp-mr-summarizer", "commits", "--base", "main", "--current", "feature"],
    )
    async def test_commits_command(self, mock_resources_class, capsys):
        """Test commits command."""
        # Mock the resources
        mock_resources = Mock()
        mock_resources_class.return_value = mock_resources

        # Mock the get_commit_history method
        mock_resources.get_commit_history = AsyncMock(
            return_value='[{"hash": "abc123", "message": "Test commit"}]'
        )

        await main()

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert len(result) == 1
        assert result[0]["hash"] == "abc123"
        assert result[0]["message"] == "Test commit"

    @patch("mcp_mr_summarizer.cli.GitResources")
    @patch(
        "sys.argv",
        ["mcp-mr-summarizer", "files", "--base", "main", "--current", "feature"],
    )
    async def test_files_command(self, mock_resources_class, capsys):
        """Test files command."""
        # Mock the resources
        mock_resources = Mock()
        mock_resources_class.return_value = mock_resources

        # Mock the get_changed_files method
        mock_resources.get_changed_files = AsyncMock(
            return_value='{"Source": ["src/file1.py"], "Tests": ["tests/test1.py"]}'
        )

        await main()

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert "Source" in result
        assert "Tests" in result
        assert result["Source"] == ["src/file1.py"]
        assert result["Tests"] == ["tests/test1.py"]

    @patch("sys.argv", ["mcp-mr-summarizer"])
    async def test_no_command_shows_help(self, capsys):
        """Test that no command shows help."""
        await main()

        captured = capsys.readouterr()
        assert "usage:" in captured.out
        assert "Available commands" in captured.out
