#!/usr/bin/env python3
"""Simple test script to verify debugging output works."""

import sys
import os
import asyncio
import pytest

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from mcp_mr_summarizer.tools import GitTools


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
    print(f"Async Result: {result}")

    # Test with current directory (should work if it's a git repo)
    print("\n--- Testing async with current directory ---")
    result = await tools.generate_merge_request_summary(
        base_branch="master", current_branch="HEAD", repo_path="."
    )
    print(f"Async Result: {result}")


def test_sync_debug_output():
    """Test that sync debugging output works correctly."""
    print("Testing sync debugging output...")

    # Create tools instance
    tools = GitTools()

    # Test with a non-existent repo path to trigger error handling
    print("\n--- Testing sync with non-existent repo ---")
    result = tools.generate_merge_request_summary_sync(
        base_branch="master", current_branch="HEAD", repo_path="/non/existent/path"
    )
    print(f"Sync Result: {result}")

    # Test with current directory (should work if it's a git repo)
    print("\n--- Testing sync with current directory ---")
    result = tools.generate_merge_request_summary_sync(
        base_branch="master", current_branch="HEAD", repo_path="."
    )
    print(f"Sync Result: {result}")


async def main():
    """Run both sync and async tests."""
    print("=== Testing Async Version ===")
    await test_async_debug_output()

    print("\n" + "=" * 50 + "\n")

    print("=== Testing Sync Version ===")
    test_sync_debug_output()


if __name__ == "__main__":
    asyncio.run(main())
