# Contributing to eagle-acquisition-plugin

Thank you for your interest in contributing to the EAGLE acquisition plugin.

## Getting Started

1. Clone the repository
2. Install dependencies: `pip install -e ".[dev]"`
3. Run tests: `pytest tests/ -v`
4. Run linting: `ruff check .`

## Plugin Structure

```
eagle-acquisition-plugin/
  agents/       <- Agent definitions (agent.md with YAML frontmatter)
  skills/       <- Skill definitions (SKILL.md with YAML frontmatter)
  runtime/      <- Python runtime (Strands SDK integration)
  data/         <- Reference data (FAR database, thresholds, etc.)
  tests/        <- Test suite
  plugin.json   <- Manifest (agents, skills, data index)
```

## Adding a New Skill

1. Create `skills/<skill-name>/SKILL.md` with YAML frontmatter
2. Add the skill name to `plugin.json` `skills` array
3. Add trigger keywords for automatic routing
4. Run tests to verify plugin discovery

## Adding a New Agent

1. Create `agents/<agent-name>/agent.md` with YAML frontmatter
2. Add the agent name to `plugin.json` `agents` array
3. Update supervisor prompt if needed
4. Run tests to verify

## Modifying Tool Definitions

Tool stubs live in `runtime/strands/tool_definitions.py`. Backend implementations live in `runtime/strands/backends/`. To add a new tool:

1. Add the `@tool` function in `tool_definitions.py`
2. Create or update the backend handler in `backends/`
3. Register the handler in `backends/__init__.py`
4. Add to `ALL_TOOLS` list

## Code Standards

- Python 3.11+
- Type hints required
- `ruff` for linting and formatting
- Docstrings for public functions

## Testing

```bash
pytest tests/ -v              # All tests
pytest tests/ -k "plugin"     # Plugin tests only
ruff check .                  # Lint
```
