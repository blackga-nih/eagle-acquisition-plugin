"""Intake workflow backends — state machine for acquisition intake."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..services import ServiceConfig

STAGES = ["requirements", "compliance", "documents", "review"]


def exec_intake_workflow(
    config: ServiceConfig,
    action: str = "status",
    intake_id: str = "",
    data: str = "{}",
    **kw: Any,
) -> dict:
    """Manage intake workflow state machine."""
    if not config.is_configured:
        return {"error": "aws_not_configured", "tool": "intake_workflow", "setup_hint": "DynamoDB required for intake state."}

    import json
    import uuid
    from datetime import datetime, timezone

    try:
        import boto3

        ddb = config.boto3_clients.get("dynamodb") or boto3.resource("dynamodb", region_name=config.region)
        table = ddb.Table(config.dynamodb_table)

        if action == "start":
            iid = f"INTAKE-{uuid.uuid4().hex[:8].upper()}"
            item = {
                "PK": f"INTAKE#{iid}",
                "SK": "STATE",
                "intake_id": iid,
                "stage": "requirements",
                "stage_index": 0,
                "data": json.loads(data) if isinstance(data, str) else data,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "in_progress",
            }
            table.put_item(Item=item)
            return {"status": "started", "intake_id": iid, "stage": "requirements"}

        if not intake_id:
            return {"error": "missing_param", "message": "intake_id required for this action"}

        resp = table.get_item(Key={"PK": f"INTAKE#{intake_id}", "SK": "STATE"})
        state = resp.get("Item")
        if not state:
            return {"error": "not_found", "intake_id": intake_id}

        if action == "status":
            return {
                "intake_id": intake_id,
                "stage": state.get("stage"),
                "stage_index": state.get("stage_index", 0),
                "status": state.get("status"),
                "stages": STAGES,
            }

        if action == "advance":
            idx = state.get("stage_index", 0) + 1
            if idx >= len(STAGES):
                return {"status": "already_complete", "intake_id": intake_id}
            table.update_item(
                Key={"PK": f"INTAKE#{intake_id}", "SK": "STATE"},
                UpdateExpression="SET stage = :s, stage_index = :i",
                ExpressionAttributeValues={":s": STAGES[idx], ":i": idx},
            )
            return {"status": "advanced", "intake_id": intake_id, "stage": STAGES[idx]}

        if action == "complete":
            table.update_item(
                Key={"PK": f"INTAKE#{intake_id}", "SK": "STATE"},
                UpdateExpression="SET #st = :s",
                ExpressionAttributeNames={"#st": "status"},
                ExpressionAttributeValues={":s": "complete"},
            )
            return {"status": "completed", "intake_id": intake_id}

        if action == "reset":
            table.update_item(
                Key={"PK": f"INTAKE#{intake_id}", "SK": "STATE"},
                UpdateExpression="SET stage = :s, stage_index = :i, #st = :st",
                ExpressionAttributeNames={"#st": "status"},
                ExpressionAttributeValues={":s": "requirements", ":i": 0, ":st": "in_progress"},
            )
            return {"status": "reset", "intake_id": intake_id, "stage": "requirements"}

        return {"error": "unknown_action", "action": action}
    except Exception as e:
        return {"error": "intake_error", "action": action, "message": str(e)}


def exec_get_intake_status(config: ServiceConfig, intake_id: str = "", **kw: Any) -> dict:
    """Get intake status shorthand."""
    return exec_intake_workflow(config, action="status", intake_id=intake_id)
