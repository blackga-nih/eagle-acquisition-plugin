#!/usr/bin/env python3
"""Quick-start — run EAGLE supervisor on Bedrock with native AgentSkills.

Prerequisites:
    pip install strands-agents strands-agents-bedrock
    # AWS credentials configured (aws configure or env vars)

Usage:
    cd eagle-acquisition-plugin/
    python -m runtime.strands.example
    python -m runtime.strands.example "I need to buy a CT scanner for $500K"
"""

from __future__ import annotations

import sys

from runtime.strands import build_supervisor


def main():
    prompt = " ".join(sys.argv[1:]) or "What can you help me with?"

    print("Building EAGLE supervisor...")
    print("  - Loading skills via native Strands AgentSkills plugin")
    print("  - Connecting to Bedrock Converse API")
    print()

    supervisor = build_supervisor(
        tenant_id="demo-tenant",
        user_id="demo-user",
        model_id="us.anthropic.claude-sonnet-4-6-20250514",
        region="us-east-1",
    )

    print(f">>> {prompt}\n")
    result = supervisor(prompt)
    print(str(result))


if __name__ == "__main__":
    main()
