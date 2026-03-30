"""Knowledge base backends — DynamoDB metadata + S3 content."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..services import ServiceConfig


def exec_knowledge_search(
    config: ServiceConfig,
    query: str = "",
    topic: str = "",
    document_type: str = "",
    agent: str = "",
    authority_level: str = "",
    keywords: list[str] | None = None,
    limit: int = 10,
    **kw: Any,
) -> dict:
    """Search the acquisition knowledge base."""
    if not config.is_configured:
        return {"error": "aws_not_configured", "tool": "knowledge_search", "setup_hint": "DynamoDB + S3 required for KB search."}

    try:
        import boto3

        ddb = config.boto3_clients.get("dynamodb") or boto3.resource("dynamodb", region_name=config.region)
        table = ddb.Table(config.dynamodb_table)

        # Scan KB entries matching query
        scan_kwargs: dict[str, Any] = {"Limit": limit}
        filter_parts, values = [], {}

        filter_parts.append("begins_with(PK, :pk)")
        values[":pk"] = "KB#"

        if topic:
            filter_parts.append("contains(topic, :topic)")
            values[":topic"] = topic
        if document_type:
            filter_parts.append("document_type = :dtype")
            values[":dtype"] = document_type
        if agent:
            filter_parts.append("agent = :agent")
            values[":agent"] = agent

        if filter_parts:
            scan_kwargs["FilterExpression"] = " AND ".join(filter_parts)
            scan_kwargs["ExpressionAttributeValues"] = values

        resp = table.scan(**scan_kwargs)
        results = resp.get("Items", [])[:limit]
        return {"query": query, "count": len(results), "results": results}
    except Exception as e:
        return {"error": "knowledge_search_error", "message": str(e)}


def exec_knowledge_fetch(config: ServiceConfig, s3_key: str = "", **kw: Any) -> dict:
    """Fetch full document from S3."""
    if not s3_key:
        return {"error": "missing_param", "message": "s3_key is required"}

    if not config.is_configured:
        return {"error": "aws_not_configured", "tool": "knowledge_fetch", "setup_hint": "S3 bucket required."}

    try:
        import boto3

        s3 = config.boto3_clients.get("s3") or boto3.client("s3", region_name=config.region)
        resp = s3.get_object(Bucket=config.s3_bucket, Key=s3_key)
        content = resp["Body"].read().decode("utf-8")
        return {"s3_key": s3_key, "content": content[:50000], "truncated": len(content) > 50000}
    except Exception as e:
        return {"error": "knowledge_fetch_error", "s3_key": s3_key, "message": str(e)}
