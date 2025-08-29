import pytest
from src.mcp_mr_summarizer.tools import GitTools, GitAnalysisError


@pytest.mark.asyncio
async def test_async_debug_output():
    """Test that async debugging output works correctly."""
    print("Testing async debugging output...")

    # Create tools instance
    tools = GitTools()

    # Test with a non-existent repo path to trigger error handling
    print("\n--- Testing async with non-existent repo ---")
    try:
        result = await tools.generate_merge_request_summary(
            "/non/existent/path", base_branch="master", current_branch="HEAD"
        )
        print(f"Async result (non-existent repo): {result}")
        assert False, "Expected exception to be raised"
    except GitAnalysisError as e:
        print(f"Async exception (non-existent repo): {e}")
        assert "Error" in str(e)
        assert "Error during generate_merge_request_summary" in str(e)

    # Test with valid repo but non-existent branches
    print("\n--- Testing async with non-existent branches ---")
    # Create a new tools instance for the current directory
    tools_current = GitTools(".")
    try:
        result = await tools_current.generate_merge_request_summary(
            ".",
            base_branch="non-existent-branch-1",
            current_branch="non-existent-branch-2",
        )
        print(f"Async result (non-existent branches): {result}")
        assert False, "Expected exception to be raised"
    except GitAnalysisError as e:
        print(f"Async exception (non-existent branches): {e}")
        assert "Error" in str(e)
        assert "Error during generate_merge_request_summary" in str(e)
