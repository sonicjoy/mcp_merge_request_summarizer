import pytest
from src.mcp_mr_summarizer.tools import GitTools


@pytest.mark.asyncio
async def test_async_debug_output():
    """Test that async debugging output works correctly."""
    print("Testing async debugging output...")

    # Create tools instance
    tools = GitTools()

    # Test with a non-existent repo path to trigger error handling
    print("\n--- Testing async with non-existent repo ---")
    result = await tools.generate_merge_request_summary(
        base_branch="master", current_branch="HEAD", repo_path="/non/existent/path"
    )
    print(f"Async result (non-existent repo): {result}")
    assert "Error" in result
    assert "Error processing git data" in result

    # Test with valid repo but non-existent branches
    print("\n--- Testing async with non-existent branches ---")
    # Create a new tools instance for the current directory
    tools_current = GitTools(".")
    result = await tools_current.generate_merge_request_summary(
        base_branch="non-existent-branch-1",
        current_branch="non-existent-branch-2",
    )
    print(f"Async result (non-existent branches): {result}")
    assert "Error" in result
    assert "Branch(es) not found" in result
