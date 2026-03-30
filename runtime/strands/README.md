# EAGLE Plugin — Strands/Bedrock Runtime

Uses the **native Strands AgentSkills plugin** to load SKILL.md files with progressive disclosure, backed by the AWS Bedrock Converse API.

## Architecture

```
eagle-acquisition-plugin/
├── skills/*/SKILL.md          ← 18 skills (AgentSkills.io standard)
├── agents/*/agent.md          ← 8 agents (supervisor + 7 specialists)
├── data/*.json                ← Reference data (FAR, thresholds, matrix)
├── plugin.json                ← Manifest (active skills, agents, data index)
│
└── runtime/strands/           ← Bedrock runtime adapter
    ├── agent_factory.py       ← build_supervisor() — 1 function, ~50 lines
    ├── plugin_loader.py       ← plugin.json + data file helpers
    ├── tool_definitions.py    ← 25 @tool stubs → Bedrock Converse toolSpec
    └── example.py             ← Quick-start script
```

## How It Works

### Native AgentSkills Plugin

Instead of building custom SKILL.md parsers and subagent factories, we use Strands' first-class `AgentSkills` plugin:

```python
from strands import Agent
from strands.plugins import AgentSkills

skills = AgentSkills(skills="./skills/")  # loads all 18 SKILL.md files
agent = Agent(plugins=[skills], tools=[...service_tools...])
```

The plugin handles everything:

| Phase | What Happens | Tokens |
|-------|-------------|--------|
| **1. Discovery** | All skill metadata (name + description) injected as XML at startup | ~100/skill |
| **2. Activation** | Full SKILL.md loaded on-demand when agent decides to use a skill | <5,000 |
| **3. Execution** | Resource files (scripts/, references/, assets/) loaded as needed | Variable |

This replaces ~200 lines of custom code (frontmatter parsing, directory walking, registry building, subagent tool factories) with one line.

### What Gets Sent to Bedrock

```json
{
  "modelId": "us.anthropic.claude-sonnet-4-6-20250514",
  "system": [
    {"text": "<supervisor agent.md + tenant context + slash commands>"},
    {"text": "<skill metadata XML from AgentSkills plugin>"}
  ],
  "messages": [...],
  "toolConfig": {
    "tools": [
      {"toolSpec": {"name": "create_document", ...}},
      {"toolSpec": {"name": "manage_package", ...}},
      {"toolSpec": {"name": "query_compliance_matrix", ...}},
      ...
    ]
  }
}
```

Skills are NOT tools — they're prompt-injected context. The 25 service tools (`create_document`, `manage_package`, etc.) are actual `toolSpec` entries that Bedrock can invoke.

## Quick Start

```bash
pip install strands-agents strands-agents-bedrock
aws configure  # or set AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY

cd eagle-acquisition-plugin/
python -m runtime.strands.example "I need to buy a CT scanner for $500K"
```

## Programmatic Usage

```python
from runtime.strands import build_supervisor

supervisor = build_supervisor(
    tenant_id="nci-oa",
    user_id="john.doe@nih.gov",
    model_id="us.anthropic.claude-sonnet-4-6-20250514",
    region="us-east-1",
)

# Single turn
result = supervisor("I need to buy lab equipment for $85K")

# Multi-turn (pass conversation history)
supervisor = build_supervisor(messages=previous_messages)
result = supervisor("Now generate the SOW")
```

## Wiring Tool Backends

`tool_definitions.py` has 25 stub `@tool` functions. Each has correct signatures and docstrings (so Bedrock generates proper toolSpec schemas) but returns "not_implemented".

Wire to your backend:

```python
# Option A: Import sm_eagle handlers directly
@tool(name="knowledge_search")
def knowledge_search(query: str = "", ...) -> str:
    """Search the acquisition knowledge base."""
    from server.app.tools.knowledge_tools import exec_knowledge_search
    return json.dumps(exec_knowledge_search(params, tenant_id, session_id))

# Option B: Call your own service layer
@tool(name="create_document")
def create_document(doc_type: str = "", ...) -> str:
    """Generate an acquisition document."""
    return my_document_service.generate(doc_type, title, content)
```

## Why Native Strands Over Custom Loader

| Aspect | Custom (old) | Native AgentSkills (current) |
|--------|-------------|------------------------------|
| SKILL.md parsing | Custom regex YAML parser | Strands built-in |
| Progressive disclosure | Manual (all-at-once) | 3-phase (metadata → instructions → resources) |
| Skill activation | All skills always in context | On-demand loading (saves tokens) |
| Subagent isolation | Custom factory + fresh Agent() | Native meta-tool pattern |
| Multi-agent patterns | Manual agents-as-tools only | Agents-as-tools, Swarm, Graph, Workflow |
| Maintenance | We maintain the loader | Strands team maintains it |
| Lines of code | ~400 (loader + factory) | ~50 (agent_factory.py) |

## Sources

- [Strands AgentSkills Plugin](https://strandsagents.com/docs/user-guide/concepts/plugins/skills/)
- [Strands Plugins Overview](https://strandsagents.com/docs/user-guide/concepts/plugins/)
- [Strands Multi-Agent Patterns](https://strandsagents.com/docs/user-guide/concepts/multi-agent/multi-agent-patterns/)
- [AgentSkills.io Specification](https://agentskills.io/specification)
- [AWS Sample: Strands AgentSkills](https://github.com/aws-samples/sample-strands-agents-agentskills)
- [Bedrock Converse API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html)
- [Strands SDK Python](https://github.com/strands-agents/sdk-python)
