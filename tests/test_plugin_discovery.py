"""Tests for plugin discovery — verifies plugin.json, skill/agent scanning, and frontmatter parsing."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

PLUGIN_DIR = Path(__file__).resolve().parent.parent
PLUGIN_JSON = PLUGIN_DIR / "plugin.json"


@pytest.fixture
def plugin_config():
    return json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))


class TestPluginJSON:
    """Validate plugin.json structure and references."""

    def test_plugin_json_exists(self):
        assert PLUGIN_JSON.is_file(), "plugin.json must exist at repo root"

    def test_required_fields(self, plugin_config):
        for field in ("name", "version", "agents", "skills", "data"):
            assert field in plugin_config, f"plugin.json missing required field: {field}"

    def test_agent_count(self, plugin_config):
        agents = plugin_config["agents"]
        assert len(agents) == 5, f"Expected 5 specialist agents, got {len(agents)}"

    def test_skill_count(self, plugin_config):
        skills = plugin_config["skills"]
        assert len(skills) == 25, f"Expected 25 skills, got {len(skills)}"

    def test_all_agents_have_directories(self, plugin_config):
        for agent in plugin_config["agents"]:
            agent_dir = PLUGIN_DIR / "agents" / agent
            assert agent_dir.is_dir(), f"Agent directory missing: {agent_dir}"

    def test_all_agents_have_agent_md(self, plugin_config):
        for agent in plugin_config["agents"]:
            agent_md = PLUGIN_DIR / "agents" / agent / "agent.md"
            assert agent_md.is_file(), f"agent.md missing: {agent_md}"

    def test_supervisor_exists(self, plugin_config):
        assert plugin_config.get("agent") == "supervisor"
        assert (PLUGIN_DIR / "agents" / "supervisor" / "agent.md").is_file()

    def test_all_skills_have_directories(self, plugin_config):
        for skill in plugin_config["skills"]:
            skill_dir = PLUGIN_DIR / "skills" / skill
            assert skill_dir.is_dir(), f"Skill directory missing: {skill_dir}"

    def test_all_skills_have_skill_md(self, plugin_config):
        for skill in plugin_config["skills"]:
            skill_md = PLUGIN_DIR / "skills" / skill / "SKILL.md"
            assert skill_md.is_file(), f"SKILL.md missing: {skill_md}"

    def test_data_files_exist(self, plugin_config):
        for name, entry in plugin_config.get("data", {}).items():
            data_file = PLUGIN_DIR / entry["file"]
            assert data_file.is_file(), f"Data file missing: {data_file} (key: {name})"

    def test_no_old_policy_agents(self, plugin_config):
        """Ensure consolidated policy agents are removed."""
        old_agents = ["policy-supervisor", "policy-librarian", "policy-analyst"]
        for old in old_agents:
            assert old not in plugin_config["agents"], f"Old agent still in plugin.json: {old}"
            assert not (PLUGIN_DIR / "agents" / old).exists(), f"Old agent dir still exists: {old}"


class TestFrontmatter:
    """Validate YAML frontmatter in skill and agent files."""

    def _parse_frontmatter(self, path: Path) -> dict:
        import re
        import yaml

        text = path.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
        assert match, f"No YAML frontmatter in {path}"
        try:
            return yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            # Some legacy skills use comma-separated values in YAML lists;
            # fall back to basic key extraction
            meta = {}
            for line in match.group(1).splitlines():
                if ":" in line and not line.startswith(" ") and not line.startswith("-"):
                    key, _, val = line.partition(":")
                    meta[key.strip()] = val.strip()
            return meta

    def test_all_skills_have_valid_frontmatter(self, plugin_config):
        for skill in plugin_config["skills"]:
            skill_md = PLUGIN_DIR / "skills" / skill / "SKILL.md"
            meta = self._parse_frontmatter(skill_md)
            assert "name" in meta, f"Skill {skill} missing 'name' in frontmatter"
            assert "description" in meta, f"Skill {skill} missing 'description'"

    def test_all_agents_have_valid_frontmatter(self, plugin_config):
        for agent in plugin_config["agents"]:
            agent_md = PLUGIN_DIR / "agents" / agent / "agent.md"
            meta = self._parse_frontmatter(agent_md)
            assert "name" in meta, f"Agent {agent} missing 'name' in frontmatter"
            assert "description" in meta, f"Agent {agent} missing 'description'"
