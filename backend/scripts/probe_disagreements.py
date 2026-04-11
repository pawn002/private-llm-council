"""
Probe script for testing disagreement analysis in isolation.

Connects directly to Ollama on localhost — no Docker rebuild, no full deliberation.
One LLM call, ~30 seconds.

Usage:
    cd backend
    python scripts/probe_disagreements.py
    python scripts/probe_disagreements.py --model qwen2.5:0.5b
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis import DeliberationAnalyzer
from src.config import GatewayConfig
from src.council import Perspective
from src.gateway import InferenceGateway

logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")

GATEWAY_URL = "http://localhost:11434/v1"

# Fixtures that reproduce the reported false-disagreement bug:
# phi talks about personal burnout → consider leaving
# psi talks about employer termination → consult employer first
# These are different subtopics; the model was wrongly labelling this FUNDAMENTAL.
FAKE_QUESTION = "Should I quit my job?"

FAKE_PERSPECTIVES = [
    Perspective(
        member_id="phi",
        model="probe",
        character="analytical",
        content=(
            "If your job is consistently causing burnout or impacting your personal "
            "well-being, it's likely time to reevaluate. No salary justifies chronic stress."
        ),
    ),
    Perspective(
        member_id="psi",
        model="probe",
        character="pragmatic",
        content=(
            "Terminating an employee early can also be a viable option, although this "
            "requires consulting with the employer first to understand the contractual obligations."
        ),
    ),
    Perspective(
        member_id="omega",
        model="probe",
        character="cautious",
        content=(
            "Before quitting, ensure you have another role lined up. Financial security "
            "matters, but so does mental health. A planned exit is better than a reactive one."
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

    async with InferenceGateway(config) as gateway:
        analyzer = DeliberationAnalyzer(gateway, model)
        disagreements = await analyzer.analyze_disagreements(
            question=FAKE_QUESTION,
            perspectives=FAKE_PERSPECTIVES,
        )

    print("\n" + "-" * 60)
    print(f"\nPARSED - DISAGREEMENTS ({len(disagreements)}):")
    for i, d in enumerate(disagreements, 1):
        print(f"\n  [{i}] {d.topic} ({d.severity})")
        for member, position in d.positions.items():
            print(f"      {member}: {position}")
        if d.description:
            print(f"      => {d.description}")

    if not disagreements:
        print("  (none)")

    print("\nExpected: 0 or 1 disagreement (phi vs omega on timing/planning).")
    print("NOT expected: phi vs psi grouped as Work-Life Balance (different subtopics).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Probe disagreement analysis")
    parser.add_argument("--model", default="llama3.2:1b", help="Ollama model to use")
    args = parser.parse_args()
    asyncio.run(main(args.model))
