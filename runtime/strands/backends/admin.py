"""Admin backends — skill, prompt, and template management."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..services import ServiceConfig


def exec_manage_skills(
    config: ServiceConfig,
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
    **kw: Any,
) -> dict:
    """CRUD for custom skills."""
    if not config.is_configured:
        return {"error": "aws_not_configured", "tool": "manage_skills", "setup_hint": "DynamoDB required for skill management."}

    try:
        import boto3
        import json

        ddb = config.boto3_clients.get("dynamodb") or boto3.resource("dynamodb", region_name=config.region)
        table = ddb.Table(config.dynamodb_table)

        if action == "list":
            resp = table.scan(FilterExpression="begins_with(PK, :pk)", ExpressionAttributeValues={":pk": "SKILL#"})
            skills = [i for i in resp.get("Items", []) if i.get("SK") == "META"]
            return {"count": len(skills), "skills": skills}

        if action == "get":
            resp = table.get_item(Key={"PK": f"SKILL#{skill_id}", "SK": "META"})
            return resp.get("Item", {"error": "not_found", "skill_id": skill_id})

        if action == "create":
            item = {
                "PK": f"SKILL#{name}",
                "SK": "META",
                "name": name,
                "display_name": display_name,
                "description": description,
                "prompt_body": prompt_body,
                "triggers": json.loads(triggers) if isinstance(triggers, str) else triggers,
                "tools": json.loads(tools_list) if isinstance(tools_list, str) else tools_list,
                "model": model,
                "visibility": visibility,
                "status": "active",
            }
            table.put_item(Item=item)
            return {"status": "created", "skill": item}

        if action == "delete":
            table.delete_item(Key={"PK": f"SKILL#{skill_id}", "SK": "META"})
            return {"status": "deleted", "skill_id": skill_id}

        return {"error": "unknown_action", "action": action}
    except Exception as e:
        return {"error": "manage_skills_error", "message": str(e)}


def exec_manage_prompts(
    config: ServiceConfig,
    action: str = "list",
    agent_name: str = "",
    prompt_body: str = "",
    is_append: bool = False,
    **kw: Any,
) -> dict:
    """Manage agent prompt overrides."""
    if not config.is_configured:
        return {"error": "aws_not_configured", "tool": "manage_prompts", "setup_hint": "DynamoDB required."}

    try:
        import boto3

        ddb = config.boto3_clients.get("dynamodb") or boto3.resource("dynamodb", region_name=config.region)
        table = ddb.Table(config.dynamodb_table)

        if action == "list":
            resp = table.scan(FilterExpression="begins_with(PK, :pk)", ExpressionAttributeValues={":pk": "PROMPT#"})
            return {"count": len(resp.get("Items", [])), "prompts": resp.get("Items", [])}

        if action == "get":
            resp = table.get_item(Key={"PK": f"PROMPT#{agent_name}", "SK": "OVERRIDE"})
            return resp.get("Item", {"error": "no_override", "agent_name": agent_name})

        if action == "set":
            existing = ""
            if is_append:
                resp = table.get_item(Key={"PK": f"PROMPT#{agent_name}", "SK": "OVERRIDE"})
                existing = resp.get("Item", {}).get("prompt_body", "")
            body = (existing + "\n\n" + prompt_body).strip() if is_append and existing else prompt_body
            table.put_item(Item={"PK": f"PROMPT#{agent_name}", "SK": "OVERRIDE", "agent_name": agent_name, "prompt_body": body})
            return {"status": "set", "agent_name": agent_name}

        if action == "delete":
            table.delete_item(Key={"PK": f"PROMPT#{agent_name}", "SK": "OVERRIDE"})
            return {"status": "deleted", "agent_name": agent_name}

        return {"error": "unknown_action", "action": action}
    except Exception as e:
        return {"error": "manage_prompts_error", "message": str(e)}


def exec_manage_templates(
    config: ServiceConfig,
    action: str = "list",
    doc_type: str = "",
    template_body: str = "",
    display_name: str = "",
    scope: str = "shared",
    **kw: Any,
) -> dict:
    """Manage document templates."""
    if not config.is_configured:
        return {"error": "aws_not_configured", "tool": "manage_templates", "setup_hint": "DynamoDB required."}

    try:
        import boto3

        ddb = config.boto3_clients.get("dynamodb") or boto3.resource("dynamodb", region_name=config.region)
        table = ddb.Table(config.dynamodb_table)

        if action == "list":
            resp = table.scan(FilterExpression="begins_with(PK, :pk)", ExpressionAttributeValues={":pk": "TMPL#"})
            return {"count": len(resp.get("Items", [])), "templates": resp.get("Items", [])}

        if action == "get":
            resp = table.get_item(Key={"PK": f"TMPL#{doc_type}", "SK": scope})
            return resp.get("Item", {"error": "no_template", "doc_type": doc_type})

        if action == "set":
            table.put_item(Item={
                "PK": f"TMPL#{doc_type}",
                "SK": scope,
                "doc_type": doc_type,
                "display_name": display_name,
                "template_body": template_body,
                "scope": scope,
            })
            return {"status": "set", "doc_type": doc_type, "scope": scope}

        if action == "delete":
            table.delete_item(Key={"PK": f"TMPL#{doc_type}", "SK": scope})
            return {"status": "deleted", "doc_type": doc_type}

        return {"error": "unknown_action", "action": action}
    except Exception as e:
        return {"error": "manage_templates_error", "message": str(e)}
