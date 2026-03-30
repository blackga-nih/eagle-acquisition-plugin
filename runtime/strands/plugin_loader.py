"""Plugin loader — helpers for plugin.json, data files, and skill/agent discovery.

Provides:
  - load_plugin_config() — reads plugin.json
  - load_data_file() — reads data/*.json by logical name
  - SKILL_AGENT_REGISTRY — lazy dict of all skills + agents with descriptions
  - PLUGIN_CONTENTS — lazy dict of name → {content, type} for all skills/agents
  - PLUGIN_DIR — resolved path to the plugin root
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

# ── Paths ────────────────────────────────────────────────────────────

PLUGIN_DIR = Path(__file__).resolve().parent.parent.parent  # eagle-acquisition-plugin/
SKILLS_DIR = PLUGIN_DIR / "skills"
AGENTS_DIR = PLUGIN_DIR / "agents"
DATA_DIR = PLUGIN_DIR / "data"
PLUGIN_JSON = PLUGIN_DIR / "plugin.json"


# ── Frontmatter Parsing ─────────────────────────────────────────────

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from a markdown file. Returns (meta, body)."""
    match = _FM_RE.match(text)
    if not match:
        return {}, text
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        meta = {}
    return meta, match.group(2).strip()


# ── Lazy Registries ─────────────────────────────────────────────────


class _LazyRegistry(dict):
    """Dict that auto-populates on first access by scanning skill/agent dirs."""

    def __init__(self, builder: callable) -> None:
        super().__init__()
        self._builder = builder
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self._loaded = True
            self.update(self._builder())

    def __getitem__(self, key: str) -> Any:
        self._ensure_loaded()
        return super().__getitem__(key)

    def __contains__(self, key: object) -> bool:
        self._ensure_loaded()
        return super().__contains__(key)

    def __iter__(self):
        self._ensure_loaded()
        return super().__iter__()

    def __len__(self) -> int:
        self._ensure_loaded()
        return super().__len__()

    def items(self):
        self._ensure_loaded()
        return super().items()

    def keys(self):
        self._ensure_loaded()
        return super().keys()

    def values(self):
        self._ensure_loaded()
        return super().values()

    def get(self, key: str, default: Any = None) -> Any:
        self._ensure_loaded()
        return super().get(key, default)


def _build_skill_agent_registry() -> dict[str, dict]:
    """Scan skills/*/SKILL.md and agents/*/agent.md, return name → {description, type, triggers}."""
    registry: dict[str, dict] = {}

    for skill_md in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        text = skill_md.read_text(encoding="utf-8")
        meta, _ = _parse_frontmatter(text)
        name = meta.get("name", skill_md.parent.name)
        registry[name] = {
            "description": meta.get("description", ""),
            "type": "skill",
            "triggers": meta.get("triggers", []),
            "path": str(skill_md),
        }

    for agent_md in sorted(AGENTS_DIR.glob("*/agent.md")):
        text = agent_md.read_text(encoding="utf-8")
        meta, _ = _parse_frontmatter(text)
        name = meta.get("name", agent_md.parent.name)
        registry[name] = {
            "description": meta.get("description", ""),
            "type": "agent",
            "triggers": meta.get("triggers", []),
            "path": str(agent_md),
        }

    return registry


def _build_plugin_contents() -> dict[str, dict]:
    """Build name → {content, type} for all skills and agents."""
    contents: dict[str, dict] = {}

    for skill_md in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        text = skill_md.read_text(encoding="utf-8")
        meta, body = _parse_frontmatter(text)
        name = meta.get("name", skill_md.parent.name)
        contents[name] = {"content": body, "type": "skill"}

    for agent_md in sorted(AGENTS_DIR.glob("*/agent.md")):
        text = agent_md.read_text(encoding="utf-8")
        meta, body = _parse_frontmatter(text)
        name = meta.get("name", agent_md.parent.name)
        contents[name] = {"content": body, "type": "agent"}

    return contents


SKILL_AGENT_REGISTRY: dict[str, dict] = _LazyRegistry(_build_skill_agent_registry)
PLUGIN_CONTENTS: dict[str, dict] = _LazyRegistry(_build_plugin_contents)


# ── Public API ───────────────────────────────────────────────────────


def load_plugin_config() -> dict:
    """Load plugin.json from the plugin root directory."""
    try:
        return json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def load_data_file(name: str, section: str | None = None) -> dict | list | str:
    """Load a data file by logical name from plugin.json's data index.

    Args:
        name: Logical data name (e.g., "matrix", "far-database")
        section: Optional top-level key to extract from JSON

    Returns:
        Full data or the requested section.
    """
    config = load_plugin_config()
    data_index = config.get("data", {})

    entry = data_index.get(name)
    if not entry:
        return {"error": f"Unknown data file: {name}", "available": list(data_index.keys())}

    file_path = PLUGIN_DIR / entry["file"]
    if not file_path.is_file():
        return {"error": f"Data file not found: {file_path}"}

    data = json.loads(file_path.read_text(encoding="utf-8"))

    if section and isinstance(data, dict):
        return data.get(section, {"error": f"Section '{section}' not found in {name}"})

    return data


def get_supervisor_prompt() -> str:
    """Read the supervisor agent.md body for use as the base system prompt."""
    agent_md = AGENTS_DIR / "supervisor" / "agent.md"
    if not agent_md.is_file():
        return "You are the EAGLE Supervisor Agent for NCI Office of Acquisitions."
    content = agent_md.read_text(encoding="utf-8")
    _, body = _parse_frontmatter(content)
    return body


def get_command_registry() -> list[dict]:
    """Load the command-registry.json for slash command metadata."""
    config = load_plugin_config()
    cmd_file = PLUGIN_DIR / config.get("commands", "command-registry.json")
    try:
        return json.loads(cmd_file.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []
