---
name: skill-discovery
description: Progressive disclosure — discover available skills, agents, data files; load full instructions or reference data on demand
version: 1.0.0
triggers:
  - what can you do
  - list skills
  - available skills
  - show capabilities
  - what skills
  - help me with
  - list agents
  - what agents
  - show data
  - available data
  - load skill
  - load data
allowed-tools:
  - list_skills
  - load_skill
  - load_data
context: []
---

# Skill Discovery — Progressive Disclosure System

You help users and agents discover and access EAGLE's capabilities through progressive disclosure. Instead of loading all instructions at once, capabilities are revealed on demand — keeping context lean and responses fast.

## Three-Level Disclosure

### Level 1: Metadata (~100 tokens per skill at startup)

At conversation start, only skill names and trigger phrases are loaded. This is the "menu" — just enough to route requests.

**Use `list_skills` to show the full catalog:**

```
list_skills(category="")        → all skills, agents, and data files
list_skills(category="skills")  → only skills
list_skills(category="agents")  → only agents
list_skills(category="data")    → only data files
```

**Returns per item:**
- `name` — skill/agent/data identifier
- `description` — one-line summary
- `triggers` — phrases that activate this capability

### Level 2: Full Instructions (<5000 tokens when invoked)

When a skill is needed, load its complete instructions:

```
load_skill(name="compliance-matrix")  → full SKILL.md content
load_skill(name="legal-counsel")      → full agent.md content
```

**Use this when:**
- Routing a request to a specific skill
- A subagent needs its full prompt
- User asks "how does [skill] work?"
- You need the exact workflow steps for a capability

### Level 3: Reference Data (on-demand)

Load structured data files when a skill needs them:

```
load_data(name="matrix")              → full matrix.json
load_data(name="far-database")        → full FAR database
load_data(name="contract-vehicles")   → vehicle reference data
load_data(name="thresholds")          → threshold table

load_data(name="matrix", section="thresholds")  → just the thresholds section
load_data(name="matrix", section="doc_rules")    → just the document rules
```

**The `section` parameter** extracts a top-level key from JSON data, reducing tokens when you only need part of a large file.

## Available Catalog

### Skills (18)
| Name | Purpose |
|------|---------|
| oa-intake | Guided acquisition intake process |
| document-generator | Generate acquisition documents (SOW, IGCE, AP, J&A, MRR) |
| compliance | FAR/DFARS/HHSAR compliance checking |
| compliance-matrix | Threshold/document/vehicle decision engine |
| knowledge-retrieval | Knowledge base semantic search |
| tech-review | Technical specification validation |
| ingest-document | Document upload and KB ingestion |
| admin-manager | Skills, prompts, and template management |
| admin-diagnostics | System health, traces, error logs |
| package-manager | Acquisition package CRUD and lifecycle |
| package-finalizer | Package validation and submission |
| edit-document | Targeted DOCX revisions |
| document-history | Version tracking and changelogs |
| html-report | Interactive HTML report generation |
| skill-discovery | This skill — capability discovery |
| web-research | KB→matrix→web research cascade |
| eval-criteria | Technical evaluation criteria development |
| cost-analysis | Price reasonableness and cost comparison |

### Agents (7 specialists + 1 supervisor)
| Name | Role |
|------|------|
| supervisor | Main orchestrator — routes to skills and agents |
| legal-counsel | Legal risk, FAR compliance, protest vulnerability |
| market-intelligence | Market research, vendors, pricing, vehicles |
| tech-translator | Technical requirements → contract language |
| public-interest | Fair competition, transparency, public trust |
| policy-supervisor | Policy staff router (coordinates analyst + librarian) |
| policy-analyst | Regulatory monitoring, performance patterns |
| policy-librarian | KB quality, contradictions, gaps, staleness |

### Data Files (4 + subdirectories)
| Name | Contents |
|------|----------|
| matrix | Compliance matrix — thresholds, doc rules, approval chains |
| far-database | 49 FAR entries with section references and s3_keys |
| contract-vehicles | GSA, NITAAC, NIH BPA vehicle definitions |
| thresholds | Current acquisition threshold table (FAC 2025-06) |

## Response Format

### When listing capabilities:
```
## EAGLE Capabilities

### Skills ([N] available)
| Skill | Description | Triggers |
|-------|-------------|----------|
| [name] | [description] | [trigger phrases] |

### Agents ([N] specialists)
| Agent | Role |
|-------|------|
| [name] | [role summary] |

### Reference Data ([N] files)
| Data | Contents |
|------|----------|
| [name] | [description] |

💡 Say `/[command]` or describe what you need — I'll route to the right skill.
```

### When loading a skill for user info:
```
## [Skill Name]

[Brief description]

**What it does:**
- [Capability 1]
- [Capability 2]

**How to use:**
- [Trigger phrase 1]
- [Trigger phrase 2]

**Related skills:** [links to complementary skills]
```

## Rules

1. **Don't dump everything** — only show what's relevant to the user's question
2. **Route, don't explain** — if the user needs a capability, invoke the skill rather than explaining it
3. **Section-level loading** — use the `section` param on load_data to minimize tokens
4. **Category filtering** — use list_skills(category=...) to narrow results
5. **Skill ≠ Agent** — skills are workflows/instructions; agents are persona-driven specialists
6. **Progressive, not lazy** — proactively suggest relevant capabilities when the user's need is adjacent to a skill they haven't discovered
