"""Tool definitions — @tool-decorated functions for the Bedrock Converse API.

Each function maps to a Strands toolSpec sent to Bedrock. The supervisor
agent sees these as callable tools alongside the skill subagent tools.

Tools are grouped by category:
  - Service tools:  create_document, edit_docx_document, manage_package, etc.
  - KB tools:       knowledge_search, knowledge_fetch, search_far
  - Web tools:      web_search, web_fetch
  - Admin tools:    manage_skills, manage_prompts, manage_templates
  - Diagnostic:     cloudwatch_logs, langfuse_traces
  - Discovery:      list_skills, load_skill, load_data
  - Compliance:     query_compliance_matrix
  - Intake:         intake_workflow, get_intake_status
  - Package:        manage_package, finalize_package, document_changelog_search,
                    get_latest_document
  - HTML:           generate_html_playground

Tool implementations are wired to backend handlers via the ServiceRegistry.
When running standalone, tools return informative errors. When running within
sm_eagle, the registry is configured with real AWS services automatically.
"""

from __future__ import annotations

import json
from typing import Any

from strands import tool

from .services import get_registry


# ── Helpers ──────────────────────────────────────────────────────────


def _json_response(data: Any) -> str:
    """Serialize tool response to JSON string (required by Strands)."""
    return json.dumps(data, indent=2, default=str)


def _dispatch(tool_name: str, **params: Any) -> str:
    """Dispatch a tool call through the ServiceRegistry."""
    result = get_registry().execute(tool_name, params)
    return _json_response(result)


# ═══════════════════════════════════════════════════════════════════════
# COMPLIANCE
# ═══════════════════════════════════════════════════════════════════════


@tool(name="query_compliance_matrix")
def query_compliance_matrix(
    operation: str = "query",
    contract_value: float = 0,
    acquisition_method: str = "",
    contract_type: str = "",
    is_it: bool = False,
    is_small_business: bool = False,
    is_rd: bool = False,
    is_human_subjects: bool = False,
    is_services: bool = True,
    keyword: str = "",
) -> str:
    """Query NCI/NIH contract requirements decision tree for thresholds, required documents, contract types, and vehicle suggestions.

    Args:
        operation: query, list_methods, list_types, list_thresholds, search_far, suggest_vehicle
        contract_value: Estimated dollar value of the acquisition
        acquisition_method: sap, sealed_bidding, negotiated, sole_source, 8a, micro_purchase
        contract_type: ffp, fpif, cpff, cpif, cpaf, cr, tm, idiq, bpa
        is_it: Whether this is an IT acquisition
        is_small_business: Whether this is a small business set-aside
        is_rd: Whether this is R&D
        is_human_subjects: Whether human subjects are involved
        is_services: Whether this is services (default true) vs supplies
        keyword: Keyword for search_far operation
    """
    # TODO: Wire to compliance_matrix.execute_operation() from sm_eagle
    # For now, load matrix.json directly for basic queries
    from .plugin_loader import load_data_file

    matrix = load_data_file("matrix")
    if isinstance(matrix, dict) and "error" in matrix:
        return _json_response(matrix)

    if operation == "list_thresholds":
        return _json_response(matrix.get("thresholds", []))
    if operation == "list_types":
        return _json_response(matrix.get("contract_types", []))

    return _json_response({
        "operation": operation,
        "contract_value": contract_value,
        "matrix_loaded": True,
        "note": "Connect to compliance_matrix.execute_operation() for full logic",
    })


# ═══════════════════════════════════════════════════════════════════════
# KNOWLEDGE BASE
# ═══════════════════════════════════════════════════════════════════════


@tool(name="knowledge_search")
def knowledge_search(
    query: str = "",
    topic: str = "",
    document_type: str = "",
    agent: str = "",
    authority_level: str = "",
    keywords: list[str] | None = None,
    limit: int = 10,
) -> str:
    """Search the acquisition knowledge base (DynamoDB metadata + built-in templates). MUST be called BEFORE web_search.

    Args:
        query: Natural language search query
        topic: Broad subject filter (competition, small business, pricing, etc.)
        document_type: Filter by document type
        agent: Filter by agent/specialist
        authority_level: Filter by authority level
        keywords: Additional keyword filters
        limit: Maximum results (default 10)
    """
    return _dispatch("knowledge_search", query=query, topic=topic, document_type=document_type,
                      agent=agent, authority_level=authority_level, keywords=keywords, limit=limit)


@tool(name="knowledge_fetch")
def knowledge_fetch(s3_key: str = "") -> str:
    """Fetch full document content from S3 knowledge base. Requires s3_key from prior knowledge_search or search_far.

    Args:
        s3_key: S3 object key from a prior KB search result
    """
    return _dispatch("knowledge_fetch", s3_key=s3_key)


@tool(name="search_far")
def search_far(query: str = "", parts: list[str] | None = None) -> str:
    """Search FAR/DFARS for clauses, requirements, and guidance. Returns part numbers, section titles, summaries, and s3_keys.

    Args:
        query: Topic, clause number, or keyword to search
        parts: Optional FAR part numbers to filter (e.g., ["6", "13", "15"])
    """
    # TODO: Wire to far_search.exec_search_far() — uses far-database.json
    from .plugin_loader import load_data_file

    far_db = load_data_file("far-database")
    if isinstance(far_db, dict) and "error" in far_db:
        return _json_response(far_db)

    # Basic keyword search over FAR entries
    results = []
    q = query.lower()
    entries = far_db if isinstance(far_db, list) else far_db.get("entries", [])
    for entry in entries:
        text = json.dumps(entry).lower()
        if q in text:
            results.append(entry)
        if len(results) >= 10:
            break

    return _json_response({"query": query, "count": len(results), "results": results})


# ═══════════════════════════════════════════════════════════════════════
# WEB RESEARCH
# ═══════════════════════════════════════════════════════════════════════


@tool(name="web_search")
def web_search(query: str = "") -> str:
    """Search the web for real-time information. MUST call knowledge_search or search_far BEFORE using this tool.

    Args:
        query: Natural language web search query
    """
    return _dispatch("web_search", query=query)


@tool(name="web_fetch")
def web_fetch(url: str = "") -> str:
    """Fetch a web page and return clean markdown content (max 15K chars). MUST call on top 2-3 URLs after every web_search.

    Args:
        url: HTTP or HTTPS URL to fetch
    """
    return _dispatch("web_fetch", url=url)


# ═══════════════════════════════════════════════════════════════════════
# DOCUMENT GENERATION & EDITING
# ═══════════════════════════════════════════════════════════════════════


@tool(name="create_document")
def create_document(
    doc_type: str = "",
    title: str = "Untitled Acquisition",
    content: str = "",
    data: str = "{}",
    package_id: str = "",
    output_format: str = "",
    update_existing_key: str = "",
    template_id: str = "",
) -> str:
    """Generate an acquisition document and save to S3. Supports: sow, igce, market_research, justification, acquisition_plan, eval_criteria, security_checklist, section_508, cor_certification, contract_type_justification, son_products, son_services, purchase_request, price_reasonableness, required_sources.

    Args:
        doc_type: Document type (sow, igce, market_research, justification, acquisition_plan, eval_criteria, etc.)
        title: Descriptive document title with program/acquisition name
        content: FULL markdown document body — write the complete document, not placeholders
        data: JSON string of structured metadata (estimated_value, period_of_performance, naics_code, etc.)
        package_id: Associated acquisition package ID
        output_format: Output format override (docx, xlsx, md)
        update_existing_key: S3 key for updating existing document instead of creating new
        template_id: Template identifier for provenance tracking
    """
    return _dispatch("create_document", doc_type=doc_type, title=title, content=content,
                      data=data, package_id=package_id, output_format=output_format,
                      update_existing_key=update_existing_key, template_id=template_id)


@tool(name="edit_docx_document")
def edit_docx_document(
    document_key: str = "",
    edits: str = "[]",
    checkbox_edits: str = "[]",
) -> str:
    """Apply targeted edits to an existing DOCX document while preserving formatting.

    Args:
        document_key: Full S3 key of the .docx file to edit
        edits: JSON array of {search_text, replacement_text} objects for text replacements
        checkbox_edits: JSON array of {label_text, checked} objects for checkbox state changes
    """
    return _dispatch("edit_docx_document", document_key=document_key, edits=edits, checkbox_edits=checkbox_edits)


@tool(name="generate_html_playground")
def generate_html_playground(
    title: str = "",
    html_content: str = "",
    doc_type: str = "document",
) -> str:
    """Generate self-contained HTML document and upload to S3 with presigned URL. HTML must start with <!DOCTYPE html>.

    Args:
        title: Document title (sanitized to filename, max 50 chars)
        html_content: Complete self-contained HTML document string
        doc_type: Type label — sow, igce, ap, ja, mrr, playground, report
    """
    return _dispatch("generate_html_playground", title=title, html_content=html_content, doc_type=doc_type)


# ═══════════════════════════════════════════════════════════════════════
# PACKAGE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════


@tool(name="manage_package")
def manage_package(
    operation: str = "list",
    package_id: str = "",
    title: str = "",
    requirement_type: str = "services",
    estimated_value: float = 0,
    acquisition_method: str = "",
    contract_type: str = "",
    contract_vehicle: str = "",
    notes: str = "",
    updates: str = "{}",
    status: str = "",
) -> str:
    """Create, read, update, delete, list, checklist, clone, or export acquisition packages.

    Args:
        operation: create, get, update, delete, list, checklist, clone, exports
        package_id: Package ID (required for get, update, delete, checklist, clone, exports)
        title: Package title (for create/clone)
        requirement_type: services, supplies, IT, construction, R&D
        estimated_value: Estimated contract value in dollars
        acquisition_method: sap, sealed_bidding, negotiated, sole_source, 8a, micro_purchase
        contract_type: ffp, fpif, cpff, cpif, cpaf, cr, tm, idiq, bpa
        contract_vehicle: NITAAC, GSA, BPA, etc.
        notes: Additional notes
        updates: JSON string of fields to update (for update operation)
        status: Filter by status (for list operation)
    """
    return _dispatch("manage_package", operation=operation, package_id=package_id, title=title,
                      requirement_type=requirement_type, estimated_value=estimated_value,
                      acquisition_method=acquisition_method, contract_type=contract_type,
                      contract_vehicle=contract_vehicle, notes=notes, updates=updates, status=status)


@tool(name="finalize_package")
def finalize_package(package_id: str = "", auto_submit: bool = False) -> str:
    """Validate acquisition package completeness and optionally submit for review.

    Args:
        package_id: Package ID to finalize (required)
        auto_submit: If true and package is ready, automatically submit for review
    """
    return _dispatch("finalize_package", package_id=package_id, auto_submit=auto_submit)


@tool(name="document_changelog_search")
def document_changelog_search(
    package_id: str = "",
    doc_type: str = "",
    limit: int = 20,
) -> str:
    """Search changelog history for a document or package.

    Args:
        package_id: Acquisition package ID (required)
        doc_type: Optional document type filter
        limit: Maximum entries to return (default 20)
    """
    return _dispatch("document_changelog_search", package_id=package_id, doc_type=doc_type, limit=limit)


@tool(name="get_latest_document")
def get_latest_document(package_id: str = "", doc_type: str = "") -> str:
    """Get latest document version with recent changelog entries.

    Args:
        package_id: Acquisition package ID (required)
        doc_type: Document type (required) — sow, igce, market_research, etc.
    """
    return _dispatch("get_latest_document", package_id=package_id, doc_type=doc_type)


# ═══════════════════════════════════════════════════════════════════════
# INTAKE WORKFLOW
# ═══════════════════════════════════════════════════════════════════════


@tool(name="intake_workflow")
def intake_workflow(
    action: str = "status",
    intake_id: str = "",
    data: str = "{}",
) -> str:
    """Manage acquisition intake workflow state machine with 4 stages: Requirements, Compliance, Documents, Review.

    Args:
        action: start, status, advance, complete, reset
        intake_id: Intake identifier (auto-generated on start, optional for status/advance)
        data: JSON string of stage-specific data to merge into workflow state
    """
    return _dispatch("intake_workflow", action=action, intake_id=intake_id, data=data)


@tool(name="get_intake_status")
def get_intake_status(intake_id: str = "") -> str:
    """Get current intake package status, document completeness, and next actions.

    Args:
        intake_id: Optional intake identifier (uses current session if omitted)
    """
    return _dispatch("get_intake_status", intake_id=intake_id)


# ═══════════════════════════════════════════════════════════════════════
# AWS OPERATIONS
# ═══════════════════════════════════════════════════════════════════════


@tool(name="s3_document_ops")
def s3_document_ops(
    operation: str = "list",
    bucket: str = "",
    key: str = "",
    content: str = "",
    destination_key: str = "",
    expiry_seconds: int = 3600,
) -> str:
    """Read, write, list, delete, copy, rename, move, check existence, or presign URLs for S3 documents.

    Args:
        operation: list, read, write, delete, copy, rename, move, exists, presign
        bucket: S3 bucket name (uses default if empty)
        key: S3 object key
        content: Content to write (for write operation)
        destination_key: Target key (for copy/rename/move)
        expiry_seconds: URL expiry for presign (default 3600)
    """
    return _dispatch("s3_document_ops", operation=operation, bucket=bucket, key=key,
                      content=content, destination_key=destination_key, expiry_seconds=expiry_seconds)


@tool(name="dynamodb_intake")
def dynamodb_intake(
    operation: str = "list",
    table: str = "eagle",
    item_id: str = "",
    data: str = "{}",
    item_ids: str = "",
    items: str = "[]",
) -> str:
    """Create, read, update, delete, list, query, count, batch_get, or batch_write DynamoDB intake records.

    Args:
        operation: create, read, update, delete, list, query, count, batch_get, batch_write
        table: DynamoDB table name (default: eagle)
        item_id: Item ID for read/update/delete
        data: JSON string of data for create/update
        item_ids: Comma-separated IDs for batch_get
        items: JSON array for batch_write
    """
    return _dispatch("dynamodb_intake", operation=operation, table=table, item_id=item_id,
                      data=data, item_ids=item_ids, items=items)


# ═══════════════════════════════════════════════════════════════════════
# ADMIN & DIAGNOSTICS
# ═══════════════════════════════════════════════════════════════════════


@tool(name="manage_skills")
def manage_skills(
    action: str = "list",
    skill_id: str = "",
    name: str = "",
    display_name: str = "",
    description: str = "",
    prompt_body: str = "",
    triggers: str = "[]",
    tools_list: str = "[]",
    model: str = "",
    visibility: str = "private",
) -> str:
    """Create, list, update, delete, publish, or disable custom skills.

    Args:
        action: list, get, create, update, delete, submit, publish, disable
        skill_id: Skill identifier
        name: Skill name
        display_name: Human-readable name
        description: Skill description
        prompt_body: Skill prompt content
        triggers: JSON array of trigger phrases
        tools_list: JSON array of available tools
        model: Model override
        visibility: private or shared
    """
    return _dispatch("manage_skills", action=action, skill_id=skill_id, name=name,
                      display_name=display_name, description=description, prompt_body=prompt_body,
                      triggers=triggers, tools_list=tools_list, model=model, visibility=visibility)


@tool(name="manage_prompts")
def manage_prompts(
    action: str = "list",
    agent_name: str = "",
    prompt_body: str = "",
    is_append: bool = False,
) -> str:
    """List, view, set, or delete agent prompt overrides.

    Args:
        action: list, get, set, delete, resolve
        agent_name: Agent to manage
        prompt_body: Prompt content (for set)
        is_append: Append to existing prompt instead of replacing (default false)
    """
    return _dispatch("manage_prompts", action=action, agent_name=agent_name,
                      prompt_body=prompt_body, is_append=is_append)


@tool(name="manage_templates")
def manage_templates(
    action: str = "list",
    doc_type: str = "",
    template_body: str = "",
    display_name: str = "",
    scope: str = "shared",
) -> str:
    """List, view, set, or delete document templates.

    Args:
        action: list, get, set, delete, resolve
        doc_type: Document type (sow, igce, etc.)
        template_body: Template content with {{VARIABLE}} placeholders
        display_name: Human-readable template name
        scope: shared or user-specific
    """
    return _dispatch("manage_templates", action=action, doc_type=doc_type,
                      template_body=template_body, display_name=display_name, scope=scope)


@tool(name="cloudwatch_logs")
def cloudwatch_logs(
    operation: str = "recent",
    log_group: str = "/eagle/app",
    filter_pattern: str = "",
    start_time: str = "-1h",
    end_time: str = "",
    limit: int = 50,
    query: str = "",
    prefix: str = "",
) -> str:
    """Query CloudWatch Logs for application monitoring and diagnostics.

    Args:
        operation: recent, search, get_stream, insights, list_groups
        log_group: Log group path (default: /eagle/app)
        filter_pattern: CloudWatch filter pattern
        start_time: ISO 8601 or relative (-1h, -30m)
        end_time: ISO 8601 or relative
        limit: Max entries (default 50)
        query: Logs Insights query string
        prefix: Log group prefix for list_groups
    """
    return _dispatch("cloudwatch_logs", operation=operation, log_group=log_group,
                      filter_pattern=filter_pattern, start_time=start_time, end_time=end_time,
                      limit=limit, query=query, prefix=prefix)


@tool(name="langfuse_traces")
def langfuse_traces(
    operation: str = "health_summary",
    trace_id: str = "",
    user_id_filter: str = "",
    session_id_filter: str = "",
    tags_filter: str = "",
    start_time: str = "-1h",
    end_time: str = "",
    limit: int = 20,
) -> str:
    """Query Langfuse traces for system diagnostics, error analysis, and cost tracking.

    Args:
        operation: list_recent, get_trace, search_errors, health_summary
        trace_id: Trace ID (required for get_trace)
        user_id_filter: Filter by user
        session_id_filter: Filter by session
        tags_filter: Comma-separated tags
        start_time: ISO 8601 or relative
        end_time: ISO 8601 or relative
        limit: Max traces (default 20)
    """
    return _dispatch("langfuse_traces", operation=operation, trace_id=trace_id,
                      user_id_filter=user_id_filter, session_id_filter=session_id_filter,
                      tags_filter=tags_filter, start_time=start_time, end_time=end_time, limit=limit)


# ═══════════════════════════════════════════════════════════════════════
# PROGRESSIVE DISCLOSURE
# ═══════════════════════════════════════════════════════════════════════


@tool(name="list_skills")
def list_skills(category: str = "") -> str:
    """Discover available skills, agents, and data files with descriptions.

    Args:
        category: Filter by category — skills, agents, data, or empty for all
    """
    from .plugin_loader import SKILL_AGENT_REGISTRY, load_plugin_config

    config = load_plugin_config()
    result: dict[str, list] = {}

    if category in ("", "skills"):
        result["skills"] = [
            {"name": name, "description": meta["description"]}
            for name, meta in SKILL_AGENT_REGISTRY.items()
        ]
    if category in ("", "data"):
        data_index = config.get("data", {})
        result["data"] = [
            {"name": name, "file": entry.get("file", "")}
            for name, entry in data_index.items()
        ]

    return _json_response(result)


@tool(name="load_skill")
def load_skill(name: str = "") -> str:
    """Load full skill or agent instructions by name. Use to follow workflows without spawning subagents.

    Args:
        name: Skill or agent name (e.g., "oa-intake", "legal-counsel")
    """
    from .plugin_loader import PLUGIN_CONTENTS

    entry = PLUGIN_CONTENTS.get(name)
    if not entry:
        return _json_response({"error": f"Skill '{name}' not found"})
    return entry["content"]


@tool(name="load_data")
def load_data(name: str = "", section: str = "") -> str:
    """Load reference data from the plugin data directory.

    Args:
        name: Data file name (e.g., "matrix", "far-database", "contract-vehicles", "thresholds")
        section: Optional top-level key to extract (reduces token usage)
    """
    from .plugin_loader import load_data_file

    data = load_data_file(name, section or None)
    return _json_response(data)


# ═══════════════════════════════════════════════════════════════════════
# ALL TOOLS — Export list for Agent(tools=[...])
# ═══════════════════════════════════════════════════════════════════════

SERVICE_TOOLS = [
    create_document,
    edit_docx_document,
    generate_html_playground,
    manage_package,
    finalize_package,
    document_changelog_search,
    get_latest_document,
    intake_workflow,
    get_intake_status,
    s3_document_ops,
    dynamodb_intake,
    query_compliance_matrix,
    manage_skills,
    manage_prompts,
    manage_templates,
    cloudwatch_logs,
    langfuse_traces,
]

KB_TOOLS = [
    knowledge_search,
    knowledge_fetch,
    search_far,
    web_search,
    web_fetch,
]

DISCOVERY_TOOLS = [
    list_skills,
    load_skill,
    load_data,
]

ALL_TOOLS = SERVICE_TOOLS + KB_TOOLS + DISCOVERY_TOOLS
