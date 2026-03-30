"""AWS operations backends — S3, DynamoDB, CloudWatch."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..services import ServiceConfig


def exec_s3_document_ops(
    config: ServiceConfig,
    operation: str = "list",
    bucket: str = "",
    key: str = "",
    content: str = "",
    destination_key: str = "",
    expiry_seconds: int = 3600,
    **kw: Any,
) -> dict:
    """S3 document operations."""
    if not config.is_configured:
        return {"error": "aws_not_configured", "tool": "s3_document_ops", "setup_hint": "S3 bucket required."}

    try:
        import boto3

        s3 = config.boto3_clients.get("s3") or boto3.client("s3", region_name=config.region)
        bkt = bucket or config.s3_bucket

        if operation == "list":
            resp = s3.list_objects_v2(Bucket=bkt, Prefix=key or "")
            objects = [{"key": o["Key"], "size": o["Size"], "modified": str(o["LastModified"])} for o in resp.get("Contents", [])]
            return {"bucket": bkt, "count": len(objects), "objects": objects}

        if operation == "read":
            resp = s3.get_object(Bucket=bkt, Key=key)
            body = resp["Body"].read().decode("utf-8")
            return {"key": key, "content": body[:50000], "truncated": len(body) > 50000}

        if operation == "write":
            s3.put_object(Bucket=bkt, Key=key, Body=content.encode("utf-8"))
            return {"status": "written", "key": key}

        if operation == "delete":
            s3.delete_object(Bucket=bkt, Key=key)
            return {"status": "deleted", "key": key}

        if operation == "copy":
            s3.copy_object(Bucket=bkt, Key=destination_key, CopySource={"Bucket": bkt, "Key": key})
            return {"status": "copied", "source": key, "destination": destination_key}

        if operation == "exists":
            try:
                s3.head_object(Bucket=bkt, Key=key)
                return {"exists": True, "key": key}
            except s3.exceptions.ClientError:
                return {"exists": False, "key": key}

        if operation == "presign":
            url = s3.generate_presigned_url("get_object", Params={"Bucket": bkt, "Key": key}, ExpiresIn=expiry_seconds)
            return {"presigned_url": url, "key": key, "expires_in": expiry_seconds}

        if operation in ("rename", "move"):
            s3.copy_object(Bucket=bkt, Key=destination_key, CopySource={"Bucket": bkt, "Key": key})
            s3.delete_object(Bucket=bkt, Key=key)
            return {"status": "moved", "source": key, "destination": destination_key}

        return {"error": "unknown_operation", "operation": operation}
    except Exception as e:
        return {"error": "s3_error", "operation": operation, "message": str(e)}


def exec_dynamodb_intake(
    config: ServiceConfig,
    operation: str = "list",
    table: str = "eagle",
    item_id: str = "",
    data: str = "{}",
    item_ids: str = "",
    items: str = "[]",
    **kw: Any,
) -> dict:
    """DynamoDB CRUD operations."""
    if not config.is_configured:
        return {"error": "aws_not_configured", "tool": "dynamodb_intake", "setup_hint": "DynamoDB table required."}

    import json

    try:
        import boto3

        ddb = config.boto3_clients.get("dynamodb") or boto3.resource("dynamodb", region_name=config.region)
        tbl = ddb.Table(table or config.dynamodb_table)

        if operation == "create":
            item_data = json.loads(data) if isinstance(data, str) else data
            tbl.put_item(Item=item_data)
            return {"status": "created", "item": item_data}

        if operation == "read":
            resp = tbl.get_item(Key={"PK": item_id, "SK": "META"})
            return resp.get("Item", {"error": "not_found", "item_id": item_id})

        if operation == "list":
            resp = tbl.scan(Limit=100)
            return {"count": len(resp.get("Items", [])), "items": resp.get("Items", [])}

        if operation == "count":
            resp = tbl.scan(Select="COUNT")
            return {"count": resp.get("Count", 0)}

        if operation == "delete":
            tbl.delete_item(Key={"PK": item_id, "SK": "META"})
            return {"status": "deleted", "item_id": item_id}

        return {"error": "unknown_operation", "operation": operation}
    except Exception as e:
        return {"error": "dynamodb_error", "operation": operation, "message": str(e)}


def exec_cloudwatch_logs(
    config: ServiceConfig,
    operation: str = "recent",
    log_group: str = "/eagle/app",
    filter_pattern: str = "",
    start_time: str = "-1h",
    end_time: str = "",
    limit: int = 50,
    query: str = "",
    prefix: str = "",
    **kw: Any,
) -> dict:
    """CloudWatch Logs operations."""
    if not config.is_configured:
        return {"error": "aws_not_configured", "tool": "cloudwatch_logs", "setup_hint": "AWS credentials required."}

    try:
        import boto3
        from datetime import datetime, timedelta, timezone

        logs = config.boto3_clients.get("logs") or boto3.client("logs", region_name=config.region)

        if operation == "list_groups":
            resp = logs.describe_log_groups(logGroupNamePrefix=prefix or "/eagle")
            groups = [{"name": g["logGroupName"], "stored_bytes": g.get("storedBytes", 0)} for g in resp.get("logGroups", [])]
            return {"groups": groups}

        # Parse relative time
        now = datetime.now(timezone.utc)
        if start_time.startswith("-"):
            val = int(start_time[1:-1])
            unit = start_time[-1]
            delta = timedelta(hours=val) if unit == "h" else timedelta(minutes=val)
            start_ms = int((now - delta).timestamp() * 1000)
        else:
            start_ms = int(now.timestamp() * 1000) - 3600000

        if operation == "recent":
            resp = logs.filter_log_events(logGroupName=log_group, startTime=start_ms, limit=limit)
            events = [{"timestamp": e["timestamp"], "message": e["message"]} for e in resp.get("events", [])]
            return {"log_group": log_group, "count": len(events), "events": events}

        if operation == "search":
            resp = logs.filter_log_events(logGroupName=log_group, startTime=start_ms, filterPattern=filter_pattern, limit=limit)
            events = [{"timestamp": e["timestamp"], "message": e["message"]} for e in resp.get("events", [])]
            return {"log_group": log_group, "filter": filter_pattern, "count": len(events), "events": events}

        if operation == "insights":
            resp = logs.start_query(
                logGroupName=log_group,
                startTime=start_ms // 1000,
                endTime=int(now.timestamp()),
                queryString=query or "fields @timestamp, @message | sort @timestamp desc | limit 50",
            )
            return {"status": "query_started", "query_id": resp["queryId"]}

        return {"error": "unknown_operation", "operation": operation}
    except Exception as e:
        return {"error": "cloudwatch_error", "operation": operation, "message": str(e)}
