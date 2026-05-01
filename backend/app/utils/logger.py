"""Logging utilities.

Beginner-friendly notes:
- Logging helps you understand what your backend is doing.
- For demos, logs make the system feel "real" and explainable.

This file provides:
1) A simple logging configuration (console output)
2) Helper functions to log:
   - memory added
   - retrieval results
   - decision output

Important:
- These helpers don't automatically run by themselves.
- In the next steps (or whenever you want), we can call them from services/routes.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Iterable, List, Optional


def setup_logging() -> None:
    """Configure application logging (console).

    We keep this very simple:
    - Log level from env var LOG_LEVEL (default: INFO)
    - Log format includes time, level, logger name, and message

    Note:
    - If logging is already configured (handlers exist), we don't overwrite it.
    """

    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    level_name = os.getenv("LOG_LEVEL", "INFO").upper().strip()
    level = getattr(logging, level_name, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def get_logger(name: str = "app") -> logging.Logger:
    """Get a configured logger."""

    setup_logging()
    return logging.getLogger(name)


def _shorten(text: str, max_len: int = 120) -> str:
    """Shorten long strings for cleaner logs."""

    text = text.replace("\n", " ").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def log_memory_added(*, memory_id: str, memory_type: str, timestamp: str, content: str, metadata: Dict[str, Any]) -> None:
    """Log that a memory was added."""

    logger = get_logger("app.memory")
    logger.info(
        "Memory added id=%s type=%s ts=%s content='%s' metadata_keys=%s",
        memory_id,
        memory_type,
        timestamp,
        _shorten(content),
        sorted(list(metadata.keys())),
    )


def log_retrieval_results(
    *,
    query: str,
    results: Iterable[Dict[str, Any]],
) -> None:
    """Log retrieval results.

    Args:
    - query: the search query
    - results: iterable of dicts with keys like:
        - id
        - adjusted_score
        - reason (optional)

    We keep it flexible so you can pass data from different layers.
    """

    logger = get_logger("app.retrieval")

    results_list: List[Dict[str, Any]] = list(results)

    top_summary = []
    for item in results_list[:5]:
        top_summary.append(
            {
                "id": item.get("id"),
                "score": item.get("adjusted_score"),
                "reason": item.get("reason"),
            }
        )

    logger.info("Retrieval query='%s' results=%s", _shorten(query), top_summary)


def log_decision_output(
    *,
    query: str,
    decision: str,
    risk_level: Optional[str],
    explanation: Optional[str],
    recent_negative_memory_ids: Optional[List[str]] = None,
) -> None:
    """Log the final decision output."""

    logger = get_logger("app.decision")

    logger.info(
        "Decision query='%s' decision=%s risk=%s negatives=%s explanation='%s'",
        _shorten(query),
        decision,
        risk_level,
        recent_negative_memory_ids or [],
        _shorten(explanation or ""),
    )
