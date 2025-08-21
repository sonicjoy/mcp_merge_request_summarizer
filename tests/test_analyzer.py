"""Tests for the GitLogAnalyzer class."""

import pytest
from unittest.mock import Mock, patch
from unittest.mock import AsyncMock

from mcp_mr_summarizer.analyzer import GitLogAnalyzer
from mcp_mr_summarizer.models import CommitInfo


class TestGitLogAnalyzer:
    """Test cases for GitLogAnalyzer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = GitLogAnalyzer()

    def test_init(self):
        """Test analyzer initialization."""
        analyzer = GitLogAnalyzer("/path/to/repo")
        assert analyzer.repo_path == "/path/to/repo"

    def test_categorize_commit_refactoring(self):
        """Test commit categorization for refactoring."""
        commit = CommitInfo(
            hash="abc123",
            author="Test Author",
            date="2023-01-01",
            message="Refactor user authentication module",
            files_changed=["auth.py"],
            insertions=50,
            deletions=30,
        )

        categories = self.analyzer.categorize_commit(commit)
        assert "refactoring" in categories

    def test_categorize_commit_bug_fix(self):
        """Test commit categorization for bug fixes."""
        commit = CommitInfo(
            hash="def456",
            author="Test Author",
            date="2023-01-01",
            message="Fix memory leak in data processor",
            files_changed=["processor.py"],
            insertions=10,
            deletions=5,
        )

        categories = self.analyzer.categorize_commit(commit)
        assert "bug_fix" in categories

    def test_categorize_commit_new_feature(self):
        """Test commit categorization for new features."""
        commit = CommitInfo(
            hash="ghi789",
            author="Test Author",
            date="2023-01-01",
            message="Add user profile management feature",
            files_changed=["profile.py"],
            insertions=100,
            deletions=0,
        )

        categories = self.analyzer.categorize_commit(commit)
        assert "new_feature" in categories

    def test_categorize_files(self):
        """Test file categorization."""
        files = {
            "UserService.py",
            "UserModel.py",
            "UserController.py",
            "test_user.py",
            "config.json",
            "README.md",
            "utils.py",
        }

        categories = self.analyzer._categorize_files(files)

        assert "UserService.py" in categories["Services"]
        assert "UserModel.py" in categories["Models"]
        assert "UserController.py" in categories["Controllers"]
        assert "test_user.py" in categories["Tests"]
        assert "config.json" in categories["Configuration"]
        assert "README.md" in categories["Documentation"]
        assert "utils.py" in categories["Other"]

    def test_estimate_review_time_short(self):
        """Test review time estimation for short reviews."""
        time = self.analyzer._estimate_review_time(2, 5, 50)
        assert time == "5 minutes"

    def test_estimate_review_time_long(self):
        """Test review time estimation for long reviews."""
        time = self.analyzer._estimate_review_time(10, 50, 3000)
        assert time == "1h 25m"

    def test_generate_title_single_commit(self):
        """Test title generation for single commit."""
        commits = [
            CommitInfo(
                hash="abc123",
                author="Test Author",
                date="2023-01-01",
                message="Add new user authentication",
                files_changed=["auth.py"],
                insertions=50,
                deletions=0,
            )
        ]

        title = self.analyzer._generate_title(commits, [], [], [])
        assert title == "feat: Add new user authentication"

    def test_generate_title_multiple_features(self):
        """Test title generation for multiple features."""
        commits = [
            CommitInfo(
                hash="abc123",
                author="Test Author",
                date="2023-01-01",
                message="Add user auth",
                files_changed=["auth.py"],
                insertions=50,
                deletions=0,
            ),
            CommitInfo(
                hash="def456",
                author="Test Author",
                date="2023-01-01",
                message="Add user profile",
                files_changed=["profile.py"],
                insertions=30,
                deletions=0,
            ),
        ]

        new_features = ["feature1", "feature2"]
        title = self.analyzer._generate_title(commits, new_features, [], [])
        assert title == "feat: 2 new features and improvements"

    @pytest.mark.asyncio
    async def test_generate_summary_no_commits(self):
        """Test summary generation with no commits."""
        summary = await self.analyzer.generate_summary([])

        assert summary.title == "No changes detected"
        assert summary.total_commits == 0
        assert summary.total_files_changed == 0
        assert summary.estimated_review_time == "0 minutes"

    @pytest.mark.asyncio
    async def test_generate_summary_with_commits(self):
        """Test summary generation with commits."""
        commits = [
            CommitInfo(
                hash="abc123",
                author="Test Author",
                date="2023-01-01",
                message="Add new feature",
                files_changed=["feature.py"],
                insertions=50,
                deletions=10,
            ),
            CommitInfo(
                hash="def456",
                author="Test Author",
                date="2023-01-01",
                message="Fix bug in processor",
                files_changed=["processor.py"],
                insertions=5,
                deletions=2,
            ),
        ]

        summary = await self.analyzer.generate_summary(commits)

        assert summary.total_commits == 2
        assert summary.total_files_changed == 2
        assert summary.total_insertions == 55
        assert summary.total_deletions == 12
        assert "Add new feature" in summary.new_features[0]
        assert "Fix bug in processor" in summary.bug_fixes[0]

    @pytest.mark.asyncio
    async def test_get_git_log_success(self):
        """Test successful git log retrieval."""
        # Mock the git command to return test data
        with patch("asyncio.create_subprocess_exec") as mock_subprocess:
            # Mock successful git command
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate.return_value = (
                b"abc1234567890123456789012345678901234567\nTest Author\n2023-01-01\nTest commit\n\nfile1.py | 10 +++++-----\n",
                b"",
            )
            mock_subprocess.return_value = mock_process

            commits = await self.analyzer.get_git_log("main", "feature")
            assert isinstance(commits, list)

    @pytest.mark.asyncio
    async def test_get_git_log_failure(self):
        """Test git log retrieval failure."""
        with patch("asyncio.create_subprocess_exec") as mock_subprocess:
            # Mock failed git command
            mock_process = AsyncMock()
            mock_process.returncode = 1
            mock_process.communicate.return_value = (b"", b"fatal: bad revision")
            mock_subprocess.return_value = mock_process

            with pytest.raises(Exception, match="Unexpected error getting git log"):
                await self.analyzer.get_git_log("main", "feature")
