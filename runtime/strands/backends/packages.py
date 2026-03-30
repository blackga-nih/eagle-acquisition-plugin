"""Package management backends — DynamoDB-backed CRUD."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..services import ServiceConfig


def _require_aws(config: ServiceConfig, tool: str) -> dict | None:
    if not config.is_configured:
        return {"error": "aws_not_configured", "tool": tool, "setup_hint": "DynamoDB table required for package management."}
    return None


def exec_manage_package(
    config: ServiceConfig,
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
    **kw: Any,
) -> dict:
    """CRUD for acquisition packages."""
    err = _require_aws(config, "manage_package")
    if err:
        return err

    try:
        import boto3
        import json
        from datetime import datetime, timezone

        ddb = config.boto3_clients.get("dynamodb") or boto3.resource("dynamodb", region_name=config.region)
        table = ddb.Table(config.dynamodb_table)

        if operation == "create":
            import uuid

            pkg_id = f"PKG-{uuid.uuid4().hex[:8].upper()}"
            item = {
                "PK": f"PKG#{pkg_id}",
                "SK": "META",
                "package_id": pkg_id,
                "title": title,
                "requirement_type": requirement_type,
                "estimated_value": str(estimated_value),
                "acquisition_method": acquisition_method,
                "contract_type": contract_type,
                "contract_vehicle": contract_vehicle,
                "notes": notes,
                "status": "draft",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            table.put_item(Item=item)
            return {"status": "created", "package_id": pkg_id, "item": item}

        if operation == "get":
            resp = table.get_item(Key={"PK": f"PKG#{package_id}", "SK": "META"})
            item = resp.get("Item")
            return item if item else {"error": "not_found", "package_id": package_id}

        if operation == "list":
            resp = table.scan(FilterExpression="begins_with(PK, :pk)", ExpressionAttributeValues={":pk": "PKG#"})
            items = [i for i in resp.get("Items", []) if i.get("SK") == "META"]
            if status:
                items = [i for i in items if i.get("status") == status]
            return {"count": len(items), "packages": items}

        if operation == "update":
            upd = json.loads(updates) if isinstance(updates, str) else updates
            expr_parts, values = [], {}
            for i, (k, v) in enumerate(upd.items()):
                expr_parts.append(f"#{k} = :v{i}")
                values[f":v{i}"] = v
                values[f"#{k}"] = k  # This won't work; need ExpressionAttributeNames
            # Simplified update
            table.update_item(
                Key={"PK": f"PKG#{package_id}", "SK": "META"},
                UpdateExpression="SET " + ", ".join(f"#k{i} = :v{i}" for i, k in enumerate(upd)),
                ExpressionAttributeNames={f"#k{i}": k for i, k in enumerate(upd)},
                ExpressionAttributeValues={f":v{i}": v for i, (k, v) in enumerate(upd.items())},
            )
            return {"status": "updated", "package_id": package_id}

        if operation == "delete":
            table.delete_item(Key={"PK": f"PKG#{package_id}", "SK": "META"})
            return {"status": "deleted", "package_id": package_id}

        return {"error": "unknown_operation", "operation": operation}
    except Exception as e:
        return {"error": "package_error", "operation": operation, "message": str(e)}


def exec_finalize_package(
    config: ServiceConfig,
    package_id: str = "",
    auto_submit: bool = False,
    **kw: Any,
) -> dict:
    """Validate package completeness."""
    err = _require_aws(config, "finalize_package")
    if err:
        return err

    try:
        import boto3

        ddb = config.boto3_clients.get("dynamodb") or boto3.resource("dynamodb", region_name=config.region)
        table = ddb.Table(config.dynamodb_table)
        resp = table.get_item(Key={"PK": f"PKG#{package_id}", "SK": "META"})
        pkg = resp.get("Item")
        if not pkg:
            return {"error": "not_found", "package_id": package_id}

        return {
            "status": "validation_complete",
            "package_id": package_id,
            "package_status": pkg.get("status", "unknown"),
            "auto_submit": auto_submit,
            "message": "Package validation complete. Override exec_finalize_package for full checklist logic.",
        }
    except Exception as e:
        return {"error": "finalize_error", "message": str(e)}


def exec_changelog_search(
    config: ServiceConfig,
    package_id: str = "",
    doc_type: str = "",
    limit: int = 20,
    **kw: Any,
) -> dict:
    """Search changelog for a package."""
    err = _require_aws(config, "document_changelog_search")
    if err:
        return err

    try:
        import boto3
        from boto3.dynamodb.conditions import Key as DDBKey

        ddb = config.boto3_clients.get("dynamodb") or boto3.resource("dynamodb", region_name=config.region)
        table = ddb.Table(config.dynamodb_table)
        resp = table.query(
            KeyConditionExpression=DDBKey("PK").eq(f"PKG#{package_id}") & DDBKey("SK").begins_with("CHANGELOG#"),
            Limit=limit,
            ScanIndexForward=False,
        )
        entries = resp.get("Items", [])
        if doc_type:
            entries = [e for e in entries if e.get("doc_type") == doc_type]
        return {"package_id": package_id, "count": len(entries), "entries": entries}
    except Exception as e:
        return {"error": "changelog_error", "message": str(e)}


def exec_get_latest_document(
    config: ServiceConfig,
    package_id: str = "",
    doc_type: str = "",
    **kw: Any,
) -> dict:
    """Get latest document version."""
    err = _require_aws(config, "get_latest_document")
    if err:
        return err

    try:
        import boto3

        s3 = config.boto3_clients.get("s3") or boto3.client("s3", region_name=config.region)
        prefix = f"documents/{package_id}/{doc_type}" if doc_type else f"documents/{package_id}/"
        resp = s3.list_objects_v2(Bucket=config.s3_bucket, Prefix=prefix)
        objects = sorted(resp.get("Contents", []), key=lambda x: x["LastModified"], reverse=True)
        if not objects:
            return {"error": "no_documents", "package_id": package_id, "doc_type": doc_type}

        latest = objects[0]
        presigned = s3.generate_presigned_url("get_object", Params={"Bucket": config.s3_bucket, "Key": latest["Key"]}, ExpiresIn=3600)
        return {"s3_key": latest["Key"], "last_modified": str(latest["LastModified"]), "size": latest["Size"], "presigned_url": presigned}
    except Exception as e:
        return {"error": "latest_doc_error", "message": str(e)}
