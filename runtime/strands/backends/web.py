"""Web research backends — fully standalone (no AWS required)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..services import ServiceConfig


def exec_web_search(config: ServiceConfig, query: str = "", **kw: Any) -> dict:
    """Web search via Bedrock Nova grounding (if available) or informative error."""
    if not query:
        return {"error": "missing_param", "message": "query is required"}

    try:
        import boto3

        client = config.boto3_clients.get("bedrock-runtime") or boto3.client(
            "bedrock-runtime", region_name=config.region
        )
        # Use Amazon Nova grounding for web search
        response = client.invoke_model(
            modelId="amazon.nova-pro-v1:0",
            contentType="application/json",
            accept="application/json",
            body=__import__("json").dumps({
                "inferenceConfig": {"maxTokens": 2048},
                "messages": [{"role": "user", "content": [{"text": f"Search the web for: {query}"}]}],
            }),
        )
        import json

        result = json.loads(response["body"].read())
        return {"query": query, "source": "bedrock-nova", "result": result}
    except Exception as e:
        return {
            "error": "web_search_unavailable",
            "query": query,
            "message": str(e),
            "hint": "Configure Bedrock access or use web_fetch with a known URL instead.",
        }


def exec_web_fetch(config: ServiceConfig, url: str = "", **kw: Any) -> dict:
    """Fetch a web page and return clean markdown (standalone via httpx + bs4)."""
    if not url:
        return {"error": "missing_param", "message": "url is required"}

    try:
        import httpx
    except ImportError:
        return {"error": "missing_dependency", "message": "Install httpx: pip install httpx"}

    try:
        resp = httpx.get(url, timeout=30, follow_redirects=True, headers={"User-Agent": "EAGLE-Bot/1.0"})
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")

        if "html" in content_type:
            try:
                from bs4 import BeautifulSoup
                from markdownify import markdownify

                soup = BeautifulSoup(resp.text, "html.parser")
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                md = markdownify(str(soup.body or soup), heading_style="ATX", strip=["img"])
                content = md[:15000]
            except ImportError:
                content = resp.text[:15000]
        else:
            content = resp.text[:15000]

        return {"url": url, "status": resp.status_code, "content": content, "truncated": len(resp.text) > 15000}
    except httpx.HTTPError as e:
        return {"error": "fetch_failed", "url": url, "message": str(e)}
