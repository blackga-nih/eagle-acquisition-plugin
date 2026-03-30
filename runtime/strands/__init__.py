# EAGLE Acquisition Plugin — Strands/Bedrock Runtime
#
# Uses native Strands AgentSkills plugin to load SKILL.md files
# with progressive disclosure, backed by Bedrock Converse API.
#
# Usage:
#   from runtime.strands import build_supervisor
#   supervisor = build_supervisor(tenant_id="nci", user_id="john.doe")
#   result = supervisor("I need to buy a CT scanner for $500K")
#
# Sources:
#   - Strands AgentSkills: strandsagents.com/docs/user-guide/concepts/plugins/skills/
#   - AgentSkills.io spec: agentskills.io/specification
#   - AWS sample: github.com/aws-samples/sample-strands-agents-agentskills

try:
    from .agent_factory import build_supervisor  # noqa: F401
except ImportError:
    build_supervisor = None  # Strands SDK not installed — standalone mode

from .services import ServiceConfig, configure, get_registry  # noqa: F401
