"""
Probe script for testing chairman synthesis in isolation.

Connects directly to Ollama on localhost — no Docker rebuild, no full deliberation.
One LLM call, ~30 seconds.

Usage:
    cd backend
    python scripts/probe_synthesis.py
    python scripts/probe_synthesis.py --model llama3.2:1b
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import GatewayConfig
from src.council import CouncilOrchestrator, Perspective, format_perspectives_for_prompt
from src.gateway import InferenceGateway

logging.basicConfig(level=logging.WARNING)

GATEWAY_URL = "http://localhost:11434/v1"

FAKE_QUESTION = "Should I quit my job?"

FAKE_PERSPECTIVES = [
    Perspective(
        member_id="phi",
        model="probe",
        character="analytical",
        content=(
            "If your job is consistently causing burnout or impacting your personal "
            "well-being, it's likely time to reevaluate. No salary justifies chronic stress. "
            "Burnout compounds over time and damages your long-term career trajectory."
        ),
    ),
    Perspective(
        member_id="psi",
        model="probe",
        character="pragmatic",
        content=(
            "Before leaving, exhaust internal options: request a role change, raise concerns "
            "with your manager, or negotiate a leave of absence. Quitting without a plan "
            "creates financial pressure that narrows your options."
        ),
    ),
    Perspective(
        member_id="omega",
        model="probe",
        character="cautious",
        content=(
            "The right time to leave is when you have clarity on what you're moving toward, "
            "not just what you're running from. Have another role lined up, or at minimum "
            "a financial runway of 3–6 months."
        ),
    ),
]


async def main(model: str) -> None:
    config = GatewayConfig(
        provider="ollama",
        url=GATEWAY_URL,
        timeout_seconds=60,
        retry_attempts=1,
        warmup=False,
    )

    print(f"\nModel   : {model}")
    print(f"Question: {FAKE_QUESTION}\n")
    print("-" * 60)
    print("Perspectives:")
    for p in FAKE_PERSPECTIVES:
        print(f"  {p.member_id}: {p.content[:80]}...")
    print("-" * 60)

    async with InferenceGateway(config) as gateway:
        # Call the synthesis method directly via a minimal orchestrator setup
        perspectives_text = format_perspectives_for_prompt(FAKE_PERSPECTIVES)

        from src.council import _parse_synthesis_response

        # Reproduce the exact prompt the chairman sees
        system_prompt = CouncilOrchestrator._CHAIRMAN_SYSTEM_PROMPT
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Question: {FAKE_QUESTION}\n\nCouncil Perspectives:\n{perspectives_text}\n\nGive a direct synthesis that answers the question.",
            },
        ]

        response = await gateway.complete(
            model=model,
            messages=messages,
            temperature=0.3,
        )

    content, _, _ = _parse_synthesis_response(response.content)

    print(f"\nRAW ({len(response.content)} chars):\n{response.content}\n")
    print("-" * 60)
    print(f"\nPARSED CONTENT:\n{content}")
    print("\nLook for: direct opening, no per-member paragraphs, no filler phrases.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Probe chairman synthesis")
    parser.add_argument("--model", default="llama3.2:1b", help="Ollama model to use")
    args = parser.parse_args()
    asyncio.run(main(args.model))
