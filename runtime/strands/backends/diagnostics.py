"""Diagnostics backends — Langfuse trace queries."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..services import ServiceConfig


def exec_langfuse_traces(
    config: ServiceConfig,
    operation: str = "health_summary",
    trace_id: str = "",
    user_id_filter: str = "",
    session_id_filter: str = "",
    tags_filter: str = "",
    start_time: str = "-1h",
    end_time: str = "",
    limit: int = 20,
    **kw: Any,
) -> dict:
    """Query Langfuse traces for diagnostics."""
    langfuse_config = config.extras.get("langfuse", {})
    if not langfuse_config.get("public_key"):
        return {
            "error": "langfuse_not_configured",
            "tool": "langfuse_traces",
            "setup_hint": (
                "Langfuse not configured. Set extras={'langfuse': {'public_key': '...', 'secret_key': '...', 'host': '...'}} "
                "in ServiceConfig to enable trace queries."
            ),
        }

    try:
        from langfuse import Langfuse

        lf = Langfuse(
            public_key=langfuse_config["public_key"],
            secret_key=langfuse_config["secret_key"],
            host=langfuse_config.get("host", "https://cloud.langfuse.com"),
        )

        if operation == "health_summary":
            traces = lf.fetch_traces(limit=limit)
            return {
                "operation": "health_summary",
                "trace_count": len(traces.data),
                "traces": [{"id": t.id, "name": t.name, "status": t.status} for t in traces.data],
            }

        if operation == "get_trace":
            trace = lf.fetch_trace(trace_id)
            return {"trace_id": trace_id, "trace": {"id": trace.id, "name": trace.name, "input": str(trace.input)[:1000]}}

        if operation == "list_recent":
            traces = lf.fetch_traces(limit=limit)
            return {"count": len(traces.data), "traces": [{"id": t.id, "name": t.name} for t in traces.data]}

        if operation == "search_errors":
            traces = lf.fetch_traces(limit=limit)
            errors = [t for t in traces.data if t.status == "ERROR"]
            return {"error_count": len(errors), "errors": [{"id": t.id, "name": t.name} for t in errors]}

        return {"error": "unknown_operation", "operation": operation}
    except ImportError:
        return {"error": "missing_dependency", "message": "Install langfuse: pip install langfuse"}
    except Exception as e:
        return {"error": "langfuse_error", "operation": operation, "message": str(e)}
