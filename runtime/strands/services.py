"""ServiceRegistry — configurable backend dispatch for tool implementations.

Provides a registry pattern where tool stubs delegate to backend handlers.
Works standalone (returns informative errors) and can be overridden by sm_eagle
to wire in real AWS services (S3, DynamoDB, Bedrock, etc.).

Usage (standalone):
    from runtime.strands.services import get_registry
    result = get_registry().execute("knowledge_search", {"query": "FAR Part 15"})
    # Returns: {"error": "aws_not_configured", "tool": "knowledge_search", ...}

Usage (sm_eagle integration):
    from runtime.strands.services import configure, ServiceConfig
    configure(ServiceConfig(s3_bucket="eagle-docs", dynamodb_table="eagle", region="us-east-1"))
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

logger = logging.getLogger(__name__)

HandlerFn = Callable[..., dict | list | str]


@dataclass
class ServiceConfig:
    """Configuration for AWS service backends."""

    s3_bucket: str = ""
    dynamodb_table: str = "eagle"
    region: str = "us-east-1"
    boto3_clients: dict[str, Any] = field(default_factory=dict)
    extras: dict[str, Any] = field(default_factory=dict)

    @property
    def is_configured(self) -> bool:
        return bool(self.s3_bucket)


class ServiceRegistry:
    """Registry for tool backend handlers with override support."""

    def __init__(self) -> None:
        self._handlers: dict[str, HandlerFn] = {}
        self._config: ServiceConfig = ServiceConfig()

    @property
    def config(self) -> ServiceConfig:
        return self._config

    def configure(self, config: ServiceConfig) -> None:
        self._config = config
        logger.info("ServiceRegistry configured: bucket=%s, table=%s", config.s3_bucket, config.dynamodb_table)

    def register(self, tool_name: str, handler: HandlerFn) -> None:
        self._handlers[tool_name] = handler

    def override(self, tool_name: str, handler: HandlerFn) -> None:
        self._handlers[tool_name] = handler
        logger.debug("Handler overridden: %s", tool_name)

    def execute(self, tool_name: str, params: dict[str, Any] | None = None) -> dict:
        params = params or {}
        handler = self._handlers.get(tool_name)
        if handler:
            try:
                return handler(self._config, **params)
            except Exception as e:
                logger.exception("Handler error for %s", tool_name)
                return {"error": "handler_error", "tool": tool_name, "message": str(e)}

        if not self._config.is_configured:
            return {
                "error": "aws_not_configured",
                "tool": tool_name,
                "params": params,
                "setup_hint": (
                    "AWS services not configured. Call configure(ServiceConfig(s3_bucket=...)) "
                    "to enable this tool, or run within sm_eagle which wires backends automatically."
                ),
            }

        return {"error": "no_handler", "tool": tool_name, "message": f"No handler registered for '{tool_name}'."}


# ── Singleton ────────────────────────────────────────────────────────

_registry: ServiceRegistry | None = None


def get_registry() -> ServiceRegistry:
    """Get or create the global ServiceRegistry singleton."""
    global _registry
    if _registry is None:
        _registry = ServiceRegistry()
        _register_defaults(_registry)
    return _registry


def configure(config: ServiceConfig, overrides: dict[str, HandlerFn] | None = None) -> ServiceRegistry:
    """Configure the global registry with AWS service config and optional handler overrides."""
    registry = get_registry()
    registry.configure(config)
    if overrides:
        for name, handler in overrides.items():
            registry.override(name, handler)
    return registry


def _register_defaults(registry: ServiceRegistry) -> None:
    """Register default backend handlers (standalone-capable)."""
    from .backends import DEFAULT_HANDLERS

    for tool_name, handler in DEFAULT_HANDLERS.items():
        registry.register(tool_name, handler)
