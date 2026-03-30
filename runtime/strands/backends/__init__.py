"""Backend handlers for tool implementations.

Each module exports handler functions that follow the signature:
    def handler(config: ServiceConfig, **params) -> dict

Handlers are registered with the ServiceRegistry at startup.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..services import HandlerFn

from .admin import exec_manage_prompts, exec_manage_skills, exec_manage_templates
from .aws_ops import exec_cloudwatch_logs, exec_dynamodb_intake, exec_s3_document_ops
from .diagnostics import exec_langfuse_traces
from .documents import exec_create_document, exec_edit_docx, exec_generate_html
from .intake import exec_get_intake_status, exec_intake_workflow
from .knowledge import exec_knowledge_fetch, exec_knowledge_search
from .packages import (
    exec_changelog_search,
    exec_finalize_package,
    exec_get_latest_document,
    exec_manage_package,
)
from .web import exec_web_fetch, exec_web_search

DEFAULT_HANDLERS: dict[str, HandlerFn] = {
    # Web
    "web_search": exec_web_search,
    "web_fetch": exec_web_fetch,
    # Documents
    "create_document": exec_create_document,
    "edit_docx_document": exec_edit_docx,
    "generate_html_playground": exec_generate_html,
    # Packages
    "manage_package": exec_manage_package,
    "finalize_package": exec_finalize_package,
    "document_changelog_search": exec_changelog_search,
    "get_latest_document": exec_get_latest_document,
    # Knowledge
    "knowledge_search": exec_knowledge_search,
    "knowledge_fetch": exec_knowledge_fetch,
    # Intake
    "intake_workflow": exec_intake_workflow,
    "get_intake_status": exec_get_intake_status,
    # AWS
    "s3_document_ops": exec_s3_document_ops,
    "dynamodb_intake": exec_dynamodb_intake,
    "cloudwatch_logs": exec_cloudwatch_logs,
    # Admin
    "manage_skills": exec_manage_skills,
    "manage_prompts": exec_manage_prompts,
    "manage_templates": exec_manage_templates,
    # Diagnostics
    "langfuse_traces": exec_langfuse_traces,
}
