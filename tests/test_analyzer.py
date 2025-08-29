"""Tests for the GitLogAnalyzer class."""

import pytest
from unittest.mock import patch, MagicMock

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

    @pytest.mark.parametrize(
        "stats_line, expected_insertions, expected_deletions",
        [
            ("2 files changed, 10 insertions(+), 5 deletions(-)", 10, 5),
            ("1 file changed, 1 insertion(+)", 1, 0),
            ("1 file changed, 1 deletion(-)", 0, 1),
            ("5 files changed, 100 insertions(+), 200 deletions(-)", 100, 200),
            ("1 file changed, 0 insertions(+), 0 deletions(-)", 0, 0),
            ("1 file changed, 1 insertion, 1 deletion", 1, 1),
        ],
    )
    def test_extract_insertions_deletions(
        self,
        stats_line,
        expected_insertions,
        expected_deletions,
    ):
        """Test extraction of insertion and deletion counts from stats line."""
        insertions, deletions = self.analyzer._extract_insertions_deletions(stats_line)
        assert insertions == expected_insertions
        assert deletions == expected_deletions

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
        assert time == "7 minutes"

    def test_estimate_review_time_long(self):
        """Test review time estimation for long reviews."""
        time = self.analyzer._estimate_review_time(10, 50, 3000)
        assert time == "1h 45m"

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

        categorized_commits = {"new_features": [], "bug_fixes": [], "refactoring": []}
        title = self.analyzer._generate_title(commits, categorized_commits)
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

        categorized_commits = {
            "new_features": ["feature1", "feature2"],
            "bug_fixes": [],
            "refactoring": [],
        }
        title = self.analyzer._generate_title(commits, categorized_commits)
        assert title == "feat: 2 new features and improvements"

    def test_generate_summary_no_commits(self):
        """Test summary generation with no commits."""
        summary = self.analyzer.generate_summary([])

        assert summary.title == "No changes detected"
        assert summary.total_commits == 0
        assert summary.total_files_changed == 0
        assert summary.estimated_review_time == "0 minutes"

    def test_generate_summary_with_commits(self):
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

        summary = self.analyzer.generate_summary(commits)

        assert summary.total_commits == 2
        assert summary.total_files_changed == 2
        assert summary.total_insertions == 55
        assert summary.total_deletions == 12
        assert "Add new feature" in summary.new_features[0]
        assert "Fix bug in processor" in summary.bug_fixes[0]

    def test_get_git_log_success(self):
        """Test successful git log retrieval."""
        mock_log_result = MagicMock()
        mock_log_result.returncode = 0
        mock_log_result.stdout = (
            "abc1234567890123456789012345678901234567\n"
            "Test Author\n"
            "2023-01-01\n"
            "Test commit\n\n"
            "src/main.py | 10 +++++-----\n"
            " 1 file changed, 5 insertions(+), 5 deletions(-)\n"
        )
        mock_log_result.stderr = ""

        # Mock the git command execution to avoid actual git operations
        with patch.object(self.analyzer, "_execute_git_command") as mock_execute:
            # First call is for branch validation, second call is for git log
            mock_execute.side_effect = [
                MagicMock(
                    returncode=0, stdout="main\nfeature\n", stderr=""
                ),  # Branch validation
                mock_log_result,  # Git log
            ]
            commits = self.analyzer.get_git_log("main", "feature")

        assert isinstance(commits, list)
        assert len(commits) == 1
        assert commits[0].hash == "abc1234567890123456789012345678901234567"
        assert commits[0].insertions == 5
        assert commits[0].deletions == 5
        assert "src/main.py" in commits[0].files_changed

    def test_get_git_log_failure(self):
        """Test git log retrieval failure."""
        mock_log_result = MagicMock()
        mock_log_result.returncode = 1
        mock_log_result.stdout = ""
        mock_log_result.stderr = "fatal: bad revision"

        # Mock the git command execution to avoid actual git operations
        with patch.object(self.analyzer, "_execute_git_command") as mock_execute:
            # First call is for branch validation, second call is for git log
            mock_execute.side_effect = [
                MagicMock(
                    returncode=0, stdout="main\nfeature\n", stderr=""
                ),  # Branch validation
                mock_log_result,  # Git log
            ]
            with pytest.raises(Exception, match="Git command failed"):
                self.analyzer.get_git_log("main", "feature")
