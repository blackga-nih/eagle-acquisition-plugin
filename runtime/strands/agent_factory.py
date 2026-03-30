"""Agent factory — builds Strands Agents using native AgentSkills plugin.

Uses Strands' first-class AgentSkills plugin to load SKILL.md files
with progressive disclosure (3-phase: metadata → instructions → resources).
No custom frontmatter parsing or subagent factories needed.

Usage:
    from runtime.strands import build_supervisor

    supervisor = build_supervisor(
        tenant_id="nci-oa",
        user_id="john.doe@nih.gov",
        model_id="us.anthropic.claude-sonnet-4-6",
    )
    result = supervisor("I need to buy a CT scanner for $500K")

Sources:
    - Strands AgentSkills plugin: strandsagents.com/docs/user-guide/concepts/plugins/skills/
    - Strands multi-agent patterns: strandsagents.com/docs/user-guide/concepts/multi-agent/
    - AWS sample: github.com/aws-samples/sample-strands-agents-agentskills
    - AgentSkills.io spec: agentskills.io/specification
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from strands import Agent
from strands.models.bedrock import BedrockModel
from strands.plugins import AgentSkills

from .plugin_loader import (
    AGENTS_DIR,
    SKILLS_DIR,
    get_command_registry,
    get_supervisor_prompt,
    load_plugin_config,
)
from .services import ServiceConfig, configure, get_registry
from .tool_definitions import ALL_TOOLS

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────

DEFAULT_MODEL_ID = "us.anthropic.claude-sonnet-4-6-20250514"


# ── Supervisor Prompt ────────────────────────────────────────────────


def _build_system_prompt(tenant_id: str, user_id: str) -> str:
    """Build the supervisor system prompt.

    The AgentSkills plugin handles skill metadata injection (Phase 1)
    and on-demand skill loading (Phase 2). We only need to provide:
      - Tenant/user context
      - The supervisor agent.md body
      - Slash command reference
    """
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S UTC")
    base_prompt = get_supervisor_prompt()

    # Slash commands for routing hints
    commands = get_command_registry()
    cmd_lines = "\n".join(
        f"  {cmd['command']}: {cmd['description']}"
        for cmd in commands
        if cmd.get("routesTo")
    )

    return (
        f"Current datetime: {now_utc}\n"
        f"Tenant: {tenant_id} | User: {user_id}\n\n"
        f"{base_prompt}\n\n"
        f"--- AVAILABLE SLASH COMMANDS ---\n"
        f"{cmd_lines}\n"
    )


# ── Main Entry Point ─────────────────────────────────────────────────


def build_supervisor(
    tenant_id: str = "demo-tenant",
    user_id: str = "demo-user",
    model_id: str = DEFAULT_MODEL_ID,
    region: str = "us-east-1",
    messages: list | None = None,
    service_config: ServiceConfig | None = None,
) -> Agent:
    """Build the EAGLE supervisor agent using native Strands AgentSkills.

    How it works:
      1. AgentSkills plugin loads all skills/ SKILL.md files
         - Phase 1 (startup): skill metadata (~100 tokens each) injected into context
         - Phase 2 (on-demand): full SKILL.md loaded when the agent decides to use it
         - Phase 3 (execution): resource files loaded as needed
      2. Service tools (@tool functions) registered for AWS operations
      3. Supervisor agent.md provides the base system prompt
      4. Strands handles the Bedrock Converse API loop

    Args:
        tenant_id: Tenant identifier for multi-tenant isolation
        user_id: User identifier for document scoping
        model_id: Bedrock model ID (default: Claude Sonnet 4.6)
        region: AWS region (default: us-east-1)
        messages: Optional conversation history (for session resume)

    Returns:
        Strands Agent. Call with: result = supervisor("your prompt")
    """
    # 0. Configure ServiceRegistry (backends for tool dispatch)
    if service_config:
        configure(service_config)

    # 1. Bedrock model
    model = BedrockModel(
        model_id=model_id,
        region_name=region,
    )

    # 2. Native AgentSkills plugin — loads all SKILL.md files with progressive disclosure
    #    This replaces our custom: _parse_frontmatter, _discover, _build_registry,
    #    _make_subagent_tool, build_skill_tools (entire plugin_loader.py + subagent factory)
    skills_plugin = AgentSkills(skills=str(SKILLS_DIR))

    # 3. System prompt from supervisor agent.md
    system_prompt = _build_system_prompt(tenant_id, user_id)

    # 4. Build supervisor with native skills + service tools
    supervisor = Agent(
        model=model,
        system_prompt=system_prompt,
        tools=ALL_TOOLS,
        plugins=[skills_plugin],
        messages=messages,
    )

    config = load_plugin_config()
    logger.info(
        "EAGLE supervisor built: %d skills (native AgentSkills), %d service tools, model=%s",
        len(config.get("skills", [])),
        len(ALL_TOOLS),
        model_id,
    )

    return supervisor
