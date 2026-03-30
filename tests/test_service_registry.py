"""Tests for ServiceRegistry — verifies registration, dispatch, and configuration."""

from __future__ import annotations

import pytest


class TestServiceRegistry:
    """Test the ServiceRegistry singleton and dispatch."""

    def test_get_registry_returns_singleton(self):
        from runtime.strands.services import get_registry

        r1 = get_registry()
        r2 = get_registry()
        assert r1 is r2

    def test_default_handlers_registered(self):
        from runtime.strands.services import get_registry

        registry = get_registry()
        # Verify a sampling of expected handlers
        for tool in ("web_search", "web_fetch", "create_document", "manage_package",
                      "knowledge_search", "intake_workflow", "s3_document_ops"):
            assert tool in registry._handlers, f"Default handler missing: {tool}"

    def test_execute_unconfigured_returns_error(self):
        from runtime.strands.services import ServiceRegistry

        registry = ServiceRegistry()
        result = registry.execute("knowledge_search", {"query": "test"})
        # No handlers registered, so returns no_handler or aws_not_configured
        assert "error" in result

    def test_configure_sets_config(self):
        from runtime.strands.services import ServiceConfig, ServiceRegistry

        registry = ServiceRegistry()
        config = ServiceConfig(s3_bucket="test-bucket", dynamodb_table="test-table")
        registry.configure(config)
        assert registry.config.s3_bucket == "test-bucket"
        assert registry.config.is_configured is True

    def test_register_and_execute(self):
        from runtime.strands.services import ServiceConfig, ServiceRegistry

        registry = ServiceRegistry()

        def mock_handler(config, **params):
            return {"mock": True, "params": params}

        registry.register("test_tool", mock_handler)
        result = registry.execute("test_tool", {"foo": "bar"})
        assert result["mock"] is True
        assert result["params"]["foo"] == "bar"

    def test_override_replaces_handler(self):
        from runtime.strands.services import ServiceConfig, ServiceRegistry

        registry = ServiceRegistry()

        def original(config, **params):
            return {"version": 1}

        def override(config, **params):
            return {"version": 2}

        registry.register("tool", original)
        assert registry.execute("tool")["version"] == 1

        registry.override("tool", override)
        assert registry.execute("tool")["version"] == 2

    def test_handler_error_caught(self):
        from runtime.strands.services import ServiceRegistry

        registry = ServiceRegistry()

        def broken_handler(config, **params):
            raise ValueError("boom")

        registry.register("broken", broken_handler)
        result = registry.execute("broken")
        assert result["error"] == "handler_error"
        assert "boom" in result["message"]


class TestPluginLoader:
    """Test plugin_loader lazy registries."""

    def test_skill_agent_registry_populated(self):
        from runtime.strands.plugin_loader import SKILL_AGENT_REGISTRY

        assert len(SKILL_AGENT_REGISTRY) > 0

    def test_plugin_contents_populated(self):
        from runtime.strands.plugin_loader import PLUGIN_CONTENTS

        assert len(PLUGIN_CONTENTS) > 0

    def test_registry_has_skills_and_agents(self):
        from runtime.strands.plugin_loader import SKILL_AGENT_REGISTRY

        types = {v["type"] for v in SKILL_AGENT_REGISTRY.values()}
        assert "skill" in types
        assert "agent" in types

    def test_load_plugin_config(self):
        from runtime.strands.plugin_loader import load_plugin_config

        config = load_plugin_config()
        assert config["name"] == "eagle-acquisition"
        assert len(config["skills"]) == 25

    def test_get_supervisor_prompt(self):
        from runtime.strands.plugin_loader import get_supervisor_prompt

        prompt = get_supervisor_prompt()
        assert len(prompt) > 100
        assert "EAGLE" in prompt or "Supervisor" in prompt
