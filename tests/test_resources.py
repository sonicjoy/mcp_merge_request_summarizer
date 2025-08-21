"""Tests for the GitResources class."""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from subprocess import CalledProcessError

from mcp_mr_summarizer.resources import GitResources
from mcp_mr_summarizer.models import CommitInfo


@pytest.mark.asyncio
class TestGitResources:
    """Test cases for GitResources."""

    def setup_method(self):
        """Set up test fixtures."""
        self.resources = GitResources("/test/repo")

    def test_init(self):
        """Test GitResources initialization."""
        resources = GitResources("/path/to/repo")
        assert resources.repo_path == "/path/to/repo"
        assert resources.analyzer is not None

    @pytest.mark.asyncio
    @patch("subprocess.run")
    async def test_get_repo_status_success(self, mock_run):
        """Test successful repository status retrieval."""
        # Mock successful git commands
        mock_run.side_effect = [
            Mock(returncode=0),  # git rev-parse --git-dir
            Mock(returncode=0, stdout="main\n"),  # git branch --show-current
            Mock(
                returncode=0, stdout="https://github.com/user/repo.git\n"
            ),  # git config remote.origin.url
            Mock(returncode=0, stdout="/test/repo\n"),  # git rev-parse --show-toplevel
            Mock(returncode=0, stdout=""),  # git status --porcelain (clean)
            Mock(returncode=0, stdout=""),  # git ls-files --others --exclude-standard
            Mock(returncode=0, stdout=""),  # git diff --cached --name-only
            Mock(returncode=0, stdout=""),  # git diff --name-only
        ]

        result = await self.resources.get_repo_status()
        status = json.loads(result)

        assert status["repository"] == "repo"
        assert status["current_branch"] == "main"
        assert status["remote_url"] == "https://github.com/user/repo.git"
        assert status["is_dirty"] is False
        assert status["untracked_files"] == 0
        assert status["staged_changes"] == 0
        assert status["unstaged_changes"] == 0

    @patch("subprocess.run")
    async def test_get_repo_status_no_git_repo(self, mock_run):
        """Test repository status when not in a git repository."""
        mock_run.side_effect = CalledProcessError(1, "git rev-parse --git-dir")

        result = await self.resources.get_repo_status()
        assert result == "No git repository found in current directory."

    @patch("subprocess.run")
    async def test_get_repo_status_no_remote(self, mock_run):
        """Test repository status when no remote is configured."""
        mock_run.side_effect = [
            Mock(returncode=0),  # git rev-parse --git-dir
            Mock(returncode=0, stdout="main\n"),  # git branch --show-current
            CalledProcessError(1, "git config remote.origin.url"),  # No remote
            Mock(returncode=0, stdout="/test/repo\n"),  # git rev-parse --show-toplevel
            Mock(returncode=0, stdout=""),  # git status --porcelain
            Mock(returncode=0, stdout=""),  # git ls-files --others --exclude-standard
            Mock(returncode=0, stdout=""),  # git diff --cached --name-only
            Mock(returncode=0, stdout=""),  # git diff --name-only
        ]

        result = await self.resources.get_repo_status()
        status = json.loads(result)

        assert status["remote_url"] == "No remote configured"

    @patch("subprocess.run")
    async def test_get_repo_status_dirty_working_directory(self, mock_run):
        """Test repository status with dirty working directory."""
        mock_run.side_effect = [
            Mock(returncode=0),  # git rev-parse --git-dir
            Mock(returncode=0, stdout="main\n"),  # git branch --show-current
            Mock(
                returncode=0, stdout="https://github.com/user/repo.git\n"
            ),  # git config remote.origin.url
            Mock(returncode=0, stdout="/test/repo\n"),  # git rev-parse --show-toplevel
            Mock(
                returncode=0, stdout="M  file1.py\nA  file2.py\n"
            ),  # git status --porcelain (dirty)
            Mock(
                returncode=0, stdout="untracked1.py\nuntracked2.py\n"
            ),  # git ls-files --others --exclude-standard
            Mock(
                returncode=0, stdout="staged1.py\nstaged2.py\n"
            ),  # git diff --cached --name-only
            Mock(
                returncode=0, stdout="unstaged1.py\nunstaged2.py\nunstaged3.py\n"
            ),  # git diff --name-only
        ]

        result = await self.resources.get_repo_status()
        status = json.loads(result)

        assert status["is_dirty"] is True
        assert status["untracked_files"] == 2
        assert status["staged_changes"] == 2
        assert status["unstaged_changes"] == 3

    async def test_get_commit_history_success(self):
        """Test successful commit history retrieval."""
        # Mock commits
        mock_commits = [
            CommitInfo(
                hash="abc123def456",
                author="Test Author",
                date="2023-01-01",
                message="Test commit 1",
                files_changed={"file1.py", "file2.py"},
                insertions=10,
                deletions=5,
            ),
            CommitInfo(
                hash="def456ghi789",
                author="Test Author 2",
                date="2023-01-02",
                message="Test commit 2",
                files_changed={"file3.py"},
                insertions=20,
                deletions=0,
            ),
        ]
        self.resources.analyzer.get_git_log = AsyncMock(return_value=mock_commits)

        result = await self.resources.get_commit_history("main", "feature")
        commits = json.loads(result)

        assert len(commits) == 2
        assert commits[0]["hash"] == "abc123de"
        assert commits[0]["message"] == "Test commit 1"
        assert commits[0]["author"] == "Test Author"
        assert commits[0]["insertions"] == 10
        assert commits[0]["deletions"] == 5
        assert set(commits[0]["files_changed"]) == {"file1.py", "file2.py"}

        assert commits[1]["hash"] == "def456gh"
        assert commits[1]["message"] == "Test commit 2"
        assert commits[1]["author"] == "Test Author 2"
        assert commits[1]["insertions"] == 20
        assert commits[1]["deletions"] == 0
        assert set(commits[1]["files_changed"]) == {"file3.py"}

    async def test_get_commit_history_no_commits(self):
        """Test commit history when no commits are found."""
        self.resources.analyzer.get_git_log = AsyncMock(return_value=[])

        result = await self.resources.get_commit_history("main", "feature")
        assert result == "No commits found between main and feature"

    @patch("subprocess.run")
    async def test_get_branches_success(self, mock_run):
        """Test successful branches retrieval."""
        mock_run.side_effect = [
            Mock(returncode=0),  # git rev-parse --git-dir
            Mock(returncode=0, stdout="main\n"),  # git branch --show-current
            Mock(returncode=0, stdout="main\nfeature\nbugfix\n"),  # git branch --format
            Mock(
                returncode=0, stdout="origin/main\norigin/feature\norigin/develop\n"
            ),  # git branch -r --format
        ]

        result = await self.resources.get_branches()
        branches = json.loads(result)

        assert branches["current_branch"] == "main"
        assert branches["local_branches"] == ["main", "feature", "bugfix"]
        assert branches["remote_branches"] == [
            "origin/main",
            "origin/feature",
            "origin/develop",
        ]

    @patch("subprocess.run")
    async def test_get_branches_no_git_repo(self, mock_run):
        """Test branches retrieval when not in a git repository."""
        mock_run.side_effect = CalledProcessError(1, "git rev-parse --git-dir")

        result = await self.resources.get_branches()
        assert result == "No git repository found in current directory."

    @patch("subprocess.run")
    async def test_get_branches_empty_branches(self, mock_run):
        """Test branches retrieval with empty branch lists."""
        mock_run.side_effect = [
            Mock(returncode=0),  # git rev-parse --git-dir
            Mock(returncode=0, stdout="main\n"),  # git branch --show-current
            Mock(returncode=0, stdout="\n\n"),  # git branch --format (empty)
            Mock(returncode=0, stdout="\n\n"),  # git branch -r --format (empty)
        ]

        result = await self.resources.get_branches()
        branches = json.loads(result)

        assert branches["current_branch"] == "main"
        assert branches["local_branches"] == []
        assert branches["remote_branches"] == []

    async def test_get_changed_files_success(self):
        """Test successful changed files retrieval."""
        # Mock commits with files
        mock_commits = [
            CommitInfo(
                hash="abc123",
                author="Test Author",
                date="2023-01-01",
                message="Test commit 1",
                files_changed={"src/file1.py", "tests/test1.py"},
                insertions=10,
                deletions=5,
            ),
            CommitInfo(
                hash="def456",
                author="Test Author 2",
                date="2023-01-02",
                message="Test commit 2",
                files_changed={"src/file2.py", "config.json"},
                insertions=20,
                deletions=0,
            ),
        ]
        self.resources.analyzer.get_git_log = AsyncMock(return_value=mock_commits)
        self.resources.analyzer._categorize_files = Mock(
            return_value={
                "Source": ["src/file1.py", "src/file2.py"],
                "Tests": ["tests/test1.py"],
                "Configuration": ["config.json"],
            }
        )

        result = await self.resources.get_changed_files("main", "feature")
        files = json.loads(result)

        assert "Source" in files
        assert "Tests" in files
        assert "Configuration" in files
        assert "src/file1.py" in files["Source"]
        assert "src/file2.py" in files["Source"]
        assert "tests/test1.py" in files["Tests"]
        assert "config.json" in files["Configuration"]

    async def test_get_changed_files_no_commits(self):
        """Test changed files when no commits are found."""
        self.resources.analyzer.get_git_log = AsyncMock(return_value=[])

        result = await self.resources.get_changed_files("main", "feature")
        assert result == "No commits found between main and feature"

    @patch("subprocess.run")
    async def test_get_repo_status_exception_handling(self, mock_run):
        """Test exception handling in get_repo_status."""
        mock_run.side_effect = Exception("Unexpected error")

        result = await self.resources.get_repo_status()
        assert result.startswith("Error getting repository status:")

    async def test_get_commit_history_exception_handling(self):
        """Test exception handling in get_commit_history."""
        self.resources.analyzer.get_git_log = AsyncMock(
            side_effect=Exception("Git log error")
        )

        result = await self.resources.get_commit_history("main", "feature")
        assert result.startswith("Error getting commit history:")

    @patch("subprocess.run")
    async def test_get_branches_exception_handling(self, mock_run):
        """Test exception handling in get_branches."""
        mock_run.side_effect = Exception("Git branch error")

        result = await self.resources.get_branches()
        assert result.startswith("Error getting branches:")

    async def test_get_changed_files_exception_handling(self):
        """Test exception handling in get_changed_files."""
        self.resources.analyzer.get_git_log = AsyncMock(
            side_effect=Exception("Git log error")
        )

        result = await self.resources.get_changed_files("main", "feature")
        assert result.startswith("Error getting changed files:")

    def test_repo_path_parameter(self):
        """Test that repo_path parameter is properly used."""
        custom_path = "/custom/repo/path"
        resources = GitResources(custom_path)

        assert resources.repo_path == custom_path
        assert resources.analyzer.repo_path == custom_path
