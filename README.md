# EAGLE Acquisition Plugin

**E**nterprise **A**cquisitions **G**uidance & **L**ogistics **E**ngine

NCI Office of Acquisitions plugin — 25 skills, 6 agents, full federal procurement lifecycle. Built on Strands Agents SDK with BedrockModel for supervisor-orchestrated multi-agent workflows.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    EAGLE Supervisor Agent                    │
│              (Intent Detection, Routing, Tools)              │
└──────────┬──────────────────────────────────────────────────┘
           │
     ┌─────┴─────────────────────────────────────┐
     │              5 Specialist Agents            │
     ├── legal-counsel      Policy/legal analysis  │
     ├── market-intelligence Vendor/market research │
     ├── tech-translator    Technical requirements  │
     ├── public-interest    Fairness/accessibility  │
     └── policy            KB quality + regulatory  │
           │
     ┌─────┴─────────────────────────────────────┐
     │              25 Skills (AgentSkills)        │
     │  Progressive disclosure: metadata → full    │
     │  instructions → resources on demand         │
     └────────────────────────────────────────────┘
           │
     ┌─────┴─────────────────────────────────────┐
     │         25 Service Tools (@tool)            │
     │  Wired to ServiceRegistry → backend         │
     │  handlers (standalone or sm_eagle)           │
     └────────────────────────────────────────────┘
```

## Quick Start

```python
from runtime.strands import build_supervisor, ServiceConfig, configure

# Standalone (tools return informative errors)
supervisor = build_supervisor(tenant_id="nci-oa", user_id="john.doe@nih.gov")
result = supervisor("I need to buy a CT scanner for $500K")

# With AWS backends
configure(ServiceConfig(s3_bucket="eagle-docs", dynamodb_table="eagle", region="us-east-1"))
supervisor = build_supervisor(tenant_id="nci-oa", user_id="john.doe@nih.gov")
```

## Plugin Structure

```
eagle-acquisition-plugin/
├── plugin.json                    # Manifest — 25 skills, 6 agents, data index
├── command-registry.json          # 34 slash commands for frontend routing
│
├── agents/                        # 6 agents (supervisor + 5 specialists)
│   ├── supervisor/agent.md        # Main orchestrator
│   ├── legal-counsel/agent.md     # Legal/J&A guidance
│   ├── market-intelligence/agent.md # Vendor/market research
│   ├── tech-translator/agent.md   # Technical requirements
│   ├── public-interest/agent.md   # Fairness/accessibility
│   └── policy/agent.md            # KB quality + regulatory intelligence
│
├── skills/                        # 25 skills (SKILL.md with YAML frontmatter)
│   ├── oa-intake/                 # Acquisition intake workflow
│   ├── document-generator/        # SOW, IGCE, AP, J&A, MRR generation
│   ├── compliance/                # FAR/DFARS/HHSAR compliance
│   ├── compliance-matrix/         # Decision tree — thresholds, vehicles
│   ├── knowledge-retrieval/       # KB search (DynamoDB + S3)
│   ├── tech-review/               # Technical spec validation
│   ├── ingest-document/           # Document upload/processing
│   ├── admin-manager/             # Skill/prompt/template management
│   ├── admin-diagnostics/         # System health, Langfuse traces
│   ├── package-manager/           # Acquisition package CRUD
│   ├── package-finalizer/         # Package completeness validation
│   ├── edit-document/             # Targeted DOCX revisions
│   ├── document-history/          # Version history, changelog
│   ├── html-report/               # Interactive HTML reports
│   ├── skill-discovery/           # Progressive disclosure registry
│   ├── web-research/              # KB→matrix→web cascade
│   ├── eval-criteria/             # Evaluation criteria builder
│   ├── cost-analysis/             # Cost/price analysis
│   ├── solicitation-builder/      # RFP/RFQ/RFI package assembly
│   ├── small-business-analysis/   # FAR Part 19 set-aside analysis
│   ├── far-reference/             # FAR/DFARS lookup with cross-refs
│   ├── clause-selector/           # FAR 52 clause selection engine
│   ├── contract-vehicles/         # GSA, NITAAC, BPA recommendations
│   ├── acquisition-glossary/      # Term definitions with FAR citations
│   └── risk-assessment/           # 5-dimension risk analysis
│
├── runtime/                       # Python runtime
│   └── strands/
│       ├── __init__.py            # Exports: build_supervisor, configure, ServiceConfig
│       ├── agent_factory.py       # Strands Agent builder with AgentSkills plugin
│       ├── plugin_loader.py       # plugin.json, data files, SKILL_AGENT_REGISTRY
│       ├── services.py            # ServiceRegistry — configurable backend dispatch
│       ├── tool_definitions.py    # 25 @tool functions wired to ServiceRegistry
│       └── backends/              # Backend handler implementations
│           ├── web.py             # web_search (Bedrock Nova), web_fetch (httpx+bs4)
│           ├── documents.py       # create_document, edit_docx, generate_html
│           ├── packages.py        # manage_package, finalize, changelog, latest
│           ├── knowledge.py       # knowledge_search, knowledge_fetch
│           ├── intake.py          # intake_workflow state machine
│           ├── aws_ops.py         # s3_document_ops, dynamodb_intake, cloudwatch
│           ├── admin.py           # manage_skills, manage_prompts, manage_templates
│           └── diagnostics.py     # langfuse_traces
│
├── data/                          # Reference data
│   ├── far-database.json          # FAR entries for search_far tool
│   ├── thresholds.json            # Dollar thresholds (micro-purchase, SAT, etc.)
│   ├── contract-vehicles.json     # NIH IDIQs, GSA schedules, BPAs
│   └── matrix.json                # Compliance decision matrix
│
├── tests/                         # Test suite (31 tests)
│   ├── test_plugin_discovery.py   # plugin.json, frontmatter, file existence
│   ├── test_service_registry.py   # ServiceRegistry + plugin_loader registries
│   └── test_tool_definitions.py   # Tool wiring, dispatch, no stubs remaining
│
├── .github/workflows/ci.yml      # Lint → Test → Validate pipeline
├── pyproject.toml                 # Build config, deps, ruff + pytest settings
├── LICENSE                        # CC0-1.0
├── CONTRIBUTING.md                # Contribution guide
└── .gitignore
```

## ServiceRegistry Pattern

Tools use a `ServiceRegistry` for backend dispatch. This allows the plugin to work in two modes:

**Standalone** — Tools return informative errors explaining what AWS config is needed:
```json
{"error": "aws_not_configured", "tool": "knowledge_search", "setup_hint": "..."}
```

**Integrated (sm_eagle)** — The registry is configured with real AWS clients:
```python
from runtime.strands.services import configure, ServiceConfig

configure(ServiceConfig(
    s3_bucket="eagle-docs",
    dynamodb_table="eagle",
    region="us-east-1",
))
```

**Override** — Individual handlers can be replaced for custom backends:
```python
from runtime.strands.services import get_registry

def my_custom_search(config, **params):
    return {"results": [...]}

get_registry().override("knowledge_search", my_custom_search)
```

## Slash Commands

34 commands for frontend routing (see `command-registry.json`):

| Command | Routes To | Description |
|---------|-----------|-------------|
| `/intake` | oa-intake | Start acquisition intake |
| `/document:SOW` | document-generator | Draft a Statement of Work |
| `/document:IGCE` | document-generator | Draft an IGCE |
| `/document:AP` | document-generator | Draft an Acquisition Plan |
| `/compliance:FAR` | compliance | Search FAR clauses |
| `/matrix` | compliance-matrix | Query decision engine |
| `/package` | package-manager | Create/manage packages |
| `/research` | web-research | KB→matrix→web cascade |
| `/cost` | cost-analysis | Price analysis |
| `/eval` | eval-criteria | Evaluation criteria |
| `/skills` | skill-discovery | List available skills |
| `/admin` | admin-diagnostics | System diagnostics |

## Development

```bash
# Install
pip install -e ".[dev,web]"

# Test
pytest tests/ -v

# Lint
ruff check runtime/ tests/

# Verify plugin integrity
python -c "
from runtime.strands.plugin_loader import SKILL_AGENT_REGISTRY, load_plugin_config
config = load_plugin_config()
print(f'{len(config[\"skills\"])} skills, {len(config[\"agents\"])} agents')
print(f'{len(SKILL_AGENT_REGISTRY)} entries in registry')
"
```

## Key Thresholds

| Threshold | Amount | Reference |
|-----------|--------|-----------|
| Micro-Purchase | $10,000 | FAR 2.101 |
| Simplified (SAT) | $250,000 | FAR 2.101 |
| Sole Source 8(a) Services | $4,500,000 | FAR 19.805-1 |
| Sole Source 8(a) Manufacturing | $7,000,000 | FAR 19.805-1 |
| Cost/Pricing Data (TINA) | $2,000,000 | FAR 15.403-4 |
| Subcontracting Plan | $750,000 | FAR 19.702 |

## Requirements

- Python 3.11+
- `strands-agents` (Bedrock Converse SDK)
- `boto3` (AWS services)
- `pyyaml` (frontmatter parsing)
- Optional: `httpx`, `beautifulsoup4`, `markdownify` (web_fetch)

## License

CC0-1.0 — Public Domain
