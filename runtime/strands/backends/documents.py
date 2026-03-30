"""Document generation backends — delegate to ServiceRegistry config."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..services import ServiceConfig


def exec_create_document(
    config: ServiceConfig,
    doc_type: str = "",
    title: str = "",
    content: str = "",
    data: str = "{}",
    package_id: str = "",
    output_format: str = "",
    update_existing_key: str = "",
    template_id: str = "",
    **kw: Any,
) -> dict:
    """Create an acquisition document and save to S3."""
    if not config.is_configured:
        return {
            "error": "aws_not_configured",
            "tool": "create_document",
            "setup_hint": "S3 bucket required for document storage. Configure via ServiceConfig.",
        }

    import json
    from datetime import datetime, timezone

    try:
        import boto3

        s3 = config.boto3_clients.get("s3") or boto3.client("s3", region_name=config.region)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        key = f"documents/{package_id or 'unpackaged'}/{ts}-{doc_type}-v1.md"

        if update_existing_key:
            key = update_existing_key

        s3.put_object(
            Bucket=config.s3_bucket,
            Key=key,
            Body=content.encode("utf-8"),
            ContentType="text/markdown",
            Metadata={"doc_type": doc_type, "title": title, "package_id": package_id},
        )

        presigned = s3.generate_presigned_url("get_object", Params={"Bucket": config.s3_bucket, "Key": key}, ExpiresIn=3600)
        metadata = json.loads(data) if isinstance(data, str) else data

        return {
            "status": "created",
            "doc_type": doc_type,
            "title": title,
            "s3_key": key,
            "presigned_url": presigned,
            "metadata": metadata,
        }
    except Exception as e:
        return {"error": "create_failed", "tool": "create_document", "message": str(e)}


def exec_edit_docx(
    config: ServiceConfig,
    document_key: str = "",
    edits: str = "[]",
    checkbox_edits: str = "[]",
    **kw: Any,
) -> dict:
    """Apply targeted edits to a DOCX document."""
    if not config.is_configured:
        return {"error": "aws_not_configured", "tool": "edit_docx_document", "setup_hint": "S3 bucket required."}

    return {
        "status": "edit_queued",
        "document_key": document_key,
        "edit_count": len(__import__("json").loads(edits)),
        "checkbox_count": len(__import__("json").loads(checkbox_edits)),
        "message": "DOCX editing requires python-docx. Install and wire exec_edit_docx for full support.",
    }


def exec_generate_html(
    config: ServiceConfig,
    title: str = "",
    html_content: str = "",
    doc_type: str = "document",
    **kw: Any,
) -> dict:
    """Generate self-contained HTML and upload to S3."""
    if not config.is_configured:
        return {"error": "aws_not_configured", "tool": "generate_html_playground", "setup_hint": "S3 bucket required."}

    try:
        import boto3
        import re
        from datetime import datetime, timezone

        s3 = config.boto3_clients.get("s3") or boto3.client("s3", region_name=config.region)
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower())[:50].strip("-")
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        key = f"html/{doc_type}/{ts}-{slug}.html"

        s3.put_object(Bucket=config.s3_bucket, Key=key, Body=html_content.encode("utf-8"), ContentType="text/html")
        presigned = s3.generate_presigned_url("get_object", Params={"Bucket": config.s3_bucket, "Key": key}, ExpiresIn=3600)

        return {"status": "created", "s3_key": key, "presigned_url": presigned, "title": title}
    except Exception as e:
        return {"error": "html_generation_failed", "message": str(e)}
