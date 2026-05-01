"""Simple CLI script to test the system end-to-end (no frontend).

Beginner-friendly notes:
- This script runs IN-PROCESS (it directly calls your Python services).
- It does NOT require the FastAPI server to be running.
- It uses the same services your API routes use.

What it does:
1) Reset the in-memory vector store
2) Insert sample memories
3) Run retrieval for a query (prints scores + reasons)
4) Run decision engine (prints decision + risk + explanation)

Run (from backend/):
- python3 test_system.py

Optional:
- python3 test_system.py --query "Supplier XYZ" --top-k 5
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List

from app.db.vector_store import vector_store
from app.models.memory_model import MemoryType
from app.services.decision_service import decision_service
from app.services.memory_service import memory_service
from app.services.retrieval_service import retrieval_service
from app.utils.logger import get_logger, log_decision_output, log_memory_added, log_retrieval_results
from app.utils.time_utils import is_stale, to_utc


def _months_ago(months: int) -> datetime:
    """Return a datetime for ~N months ago (1 month ~= 30 days)."""

    return datetime.now(timezone.utc) - timedelta(days=30 * months)


def seed_sample_memories() -> None:
    """Insert a small set of sample memories for demo/testing."""

    samples: List[Dict[str, Any]] = [
        {
            "memory_type": MemoryType.historical,
            "content": "Supplier XYZ had quality issues with delivered components.",
            "timestamp": _months_ago(4),
            "metadata": {"supplier": "XYZ", "issue_type": "quality", "severity": "high"},
        },
        {
            "memory_type": MemoryType.historical,
            "content": "Supplier XYZ had a payment dispute about invoice INV-1008.",
            "timestamp": _months_ago(8),
            "metadata": {"supplier": "XYZ", "issue_type": "payment_dispute", "invoice": "INV-1008"},
        },
        {
            "memory_type": MemoryType.experiential,
            "content": "Supplier XYZ performed well recently with on-time deliveries.",
            "timestamp": _months_ago(2),
            "metadata": {"supplier": "XYZ", "issue_type": "positive_performance", "metric": "on_time_delivery"},
        },
        {
            "memory_type": MemoryType.temporal,
            "content": "Delivery delays increased during monsoon season due to road flooding.",
            "timestamp": _months_ago(1),
            "metadata": {"issue_type": "late_delivery", "season": "monsoon", "cause": "road_flooding"},
        },
    ]

    for payload in samples:
        memory = memory_service.add_memory(
            memory_type=payload["memory_type"],
            content=payload["content"],
            timestamp=payload["timestamp"],
            metadata=payload["metadata"],
        )

        # Log what we inserted (useful for demos)
        log_memory_added(
            memory_id=memory.id,
            memory_type=memory.type.value,
            timestamp=memory.timestamp.isoformat(),
            content=memory.content,
            metadata=memory.metadata,
        )


def print_retrieval_results(query: str, top_k: int) -> None:
    """Run retrieval and print the results."""

    logger = get_logger("app.cli")

    results = retrieval_service.search(query=query, top_k=top_k)

    print("\n=== Retrieval Results ===")
    print(f"Query: {query}")
    print(f"Returned: {len(results)} memories\n")

    rows_for_log: List[Dict[str, Any]] = []

    now = datetime.now(timezone.utc)
    for i, item in enumerate(results, start=1):
        memory = item.memory
        age_days = (to_utc(now) - to_utc(memory.timestamp)).days
        stale = is_stale(memory.timestamp, now=now)

        print(f"#{i}")
        print(f"- id: {memory.id}")
        print(f"- type: {memory.type.value}")
        print(f"- age_days: {age_days} | stale: {stale}")
        print(f"- content: {memory.content}")
        print(f"- metadata: {memory.metadata}")
        print(f"- raw_score: {item.raw_score:.4f}")
        print(f"- adjusted_score: {item.adjusted_score:.4f}")
        print(f"- reason: {item.reason}")
        print("-")

        rows_for_log.append(
            {
                "id": memory.id,
                "adjusted_score": item.adjusted_score,
                "reason": item.reason,
            }
        )

    log_retrieval_results(query=query, results=rows_for_log)

    logger.info("Retrieval printed to console")


def print_decision(query: str, top_k: int) -> None:
    """Run decision engine and print output."""

    out = decision_service.decide(query=query, top_k=top_k)

    decision = out.get("decision")
    risk_level = out.get("risk_level")
    explanation = out.get("explanation")

    print("\n=== Decision ===")
    print(f"Decision: {decision}")
    print(f"Risk Level: {risk_level}")
    print(f"Explanation: {explanation}\n")

    negatives = out.get("recent_negative_memories", [])
    negative_ids = [m.id for m in negatives]

    if negatives:
        print("Recent negative memories:")
        for m in negatives:
            print(f"- {m.id} | {m.type.value} | {m.content}")
    else:
        print("No recent negative memories found.")

    log_decision_output(
        query=query,
        decision=str(decision),
        risk_level=str(risk_level) if risk_level is not None else None,
        explanation=str(explanation) if explanation is not None else None,
        recent_negative_memory_ids=negative_ids,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="CLI test for memory retrieval + decision")
    parser.add_argument("--query", default="Supplier XYZ", help="Query to test (default: Supplier XYZ)")
    parser.add_argument("--top-k", type=int, default=5, help="Number of memories to retrieve (default: 5)")
    parser.add_argument(
        "--no-seed",
        action="store_true",
        help="Do not seed sample memories (use existing in-memory store)",
    )

    args = parser.parse_args()

    # Start clean (helpful for repeatable demo runs)
    vector_store.reset()

    if not args.no_seed:
        seed_sample_memories()

    print_retrieval_results(query=args.query, top_k=args.top_k)
    print_decision(query=args.query, top_k=args.top_k)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
