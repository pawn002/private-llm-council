"""
Probe script for testing consensus/insights extraction in isolation.

Connects directly to Ollama on localhost — no Docker rebuild, no full deliberation.
One LLM call, ~30 seconds.

Usage:
    cd backend
    python scripts/probe_consensus.py
    python scripts/probe_consensus.py --model qwen2.5:0.5b
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Allow running from the backend/ directory without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis import DeliberationAnalyzer
from src.config import GatewayConfig
from src.council import Perspective
from src.gateway import InferenceGateway

logging.basicConfig(level=logging.INFO, format="%(name)s — %(message)s")

GATEWAY_URL = "http://localhost:11434/v1"

FAKE_QUESTION = "Should our startup accelerate growth despite internal operational immaturity?"

FAKE_PERSPECTIVES = [
    Perspective(
        member_id="phi",
        model="probe",
        character="analytical",
        content=(
            "The key risk is overextension. Companies that grow too fast often collapse "
            "under operational complexity. Internal systems must be hardened before scaling."
        ),
    ),
    Perspective(
        member_id="psi",
        model="probe",
        character="pragmatic",
        content=(
            "Growth requires risk. Waiting for perfect internal maturity means ceding "
            "market share. The speed of expansion must match the maturity of core systems, "
            "but some controlled risk-taking is essential."
        ),
    ),
]

FAKE_SYNTHESIS = (
    "The council is divided on the pace of expansion. Both perspectives acknowledge "
    "that growth carries inherent risk, but differ on whether current conditions justify "
    "acceleration. Phi warns of operational collapse through overextension and argues "
    "internal systems must be hardened first. Psi contends that waiting for perfect "
    "maturity cedes the market, and that controlled risk-taking is unavoidable."
)


async def main(model: str) -> None:
    config = GatewayConfig(
        provider="ollama",
        url=GATEWAY_URL,
        timeout_seconds=60,
        retry_attempts=1,
        warmup=False,
    )

    print(f"\nModel : {model}")
    print(f"Question: {FAKE_QUESTION}\n")
    print("-" * 60)

    async with InferenceGateway(config) as gateway:
        analyzer = DeliberationAnalyzer(gateway, model)
        consensus, insights = await analyzer.extract_consensus_and_insights(
            question=FAKE_QUESTION,
            perspectives=FAKE_PERSPECTIVES,
            synthesis=FAKE_SYNTHESIS,
        )

    print("\n" + "-" * 60)
    print(f"\nPARSED — CONSENSUS POINTS ({len(consensus)}):")
    for p in consensus:
        print(f"  • {p}")

    print(f"\nPARSED — UNIQUE INSIGHTS ({len(insights)}):")
    for i in insights:
        print(f"  • {i}")

    if not consensus and not insights:
        print("  (none — check the raw response above to diagnose)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Probe consensus/insights extraction")
    parser.add_argument("--model", default="llama3.2:1b", help="Ollama model to use")
    args = parser.parse_args()
    asyncio.run(main(args.model))
