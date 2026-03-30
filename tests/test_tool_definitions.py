"""Tests for tool definitions — verifies all tools are defined and use _dispatch."""

from __future__ import annotations

import json

import pytest


class TestToolDefinitions:
    """Verify tool definitions are properly wired."""

    def test_all_tools_list_populated(self):
        from runtime.strands.tool_definitions import ALL_TOOLS

        assert len(ALL_TOOLS) >= 20, f"Expected 20+ tools, got {len(ALL_TOOLS)}"

    def test_all_tools_are_callable(self):
        from runtime.strands.tool_definitions import ALL_TOOLS

        for tool_fn in ALL_TOOLS:
            assert callable(tool_fn), f"Tool {tool_fn} is not callable"

    def test_no_not_implemented_references(self):
        """Ensure _not_implemented has been fully replaced by _dispatch."""
        from pathlib import Path

        td_path = Path(__file__).parent.parent / "runtime" / "strands" / "tool_definitions.py"
        content = td_path.read_text(encoding="utf-8")
        assert "_not_implemented" not in content, "Found _not_implemented — all tools should use _dispatch"

    def test_dispatch_exists(self):
        from runtime.strands.tool_definitions import _dispatch

        assert callable(_dispatch)

    def test_list_skills_returns_json(self):
        from runtime.strands.tool_definitions import list_skills

        result = json.loads(list_skills())
        # list_skills returns skills + data as a dict
        assert "skills" in result
        assert len(result["skills"]) > 0

    def test_load_data_returns_json(self):
        from runtime.strands.tool_definitions import load_data

        result = json.loads(load_data(name="thresholds"))
        # Should return data or error
        assert isinstance(result, (dict, list))
