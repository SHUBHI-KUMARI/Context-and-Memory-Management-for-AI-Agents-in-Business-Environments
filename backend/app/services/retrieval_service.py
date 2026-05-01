"""Retrieval service (business logic for searching memories).

Beginner-friendly notes:
- We store memories as vectors in FAISS.
- To search, we embed the user's query into a vector.
- FAISS returns the most similar stored vectors.

Memory lifecycle rule (simple):
- If a memory is older than 6 months, we mark it as "stale".
- Stale memories still show up, but we reduce their importance (score).

Why reduce importance?
- Old events might be less relevant than recent ones.
- This is a simple way to simulate memory decay without an LLM.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

from app.db.vector_store import vector_store
from app.models.memory_model import Memory
from app.utils.embeddings import embed_query


# We approximate 6 months as 180 days to keep it beginner-simple.
STALE_DAYS = 180


@dataclass
class RetrievedMemory:
    """A retrieval result with scoring details.

    - memory: the stored Memory
    - raw_score: score returned by FAISS (higher = more similar)
    - adjusted_score: score after applying stale penalty
    """

    memory: Memory
    raw_score: float
    adjusted_score: float


class RetrievalService:
    """Core logic for retrieving relevant memories."""

    def _is_stale(self, memory: Memory, *, now: Optional[datetime] = None) -> bool:
        """Check if a memory is older than ~6 months.

        We keep this logic inside the retrieval service for now.
        (In the next step, we'll also create a reusable helper in time_utils.py.)
        """

        if now is None:
            now = datetime.now(timezone.utc)

        ts = memory.timestamp

        # If someone provides a naive datetime, treat it as UTC.
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)

        age_days = (now - ts).days
        return age_days > STALE_DAYS

    def search(self, query: str, top_k: int = 5) -> List[RetrievedMemory]:
        """Search for relevant memories.

        Args:
        - query: user query like "Supplier XYZ invoice"
        - top_k: return up to this many results (default 5)

        Returns:
        - list of RetrievedMemory items, sorted by adjusted_score desc

        Notes:
        - If you have fewer than top_k memories stored, you'll get fewer results.
        """

        # 1) Convert query text -> query embedding vector
        query_vector = embed_query(query)

        # 2) Ask vector_store (FAISS) for the top matches
        # vector_store.search returns a list of (Memory, raw_score)
        matches = vector_store.search(query_embedding=query_vector, top_k=top_k)

        # 3) Apply stale penalty and return results
        results: List[RetrievedMemory] = []

        for memory, raw_score in matches:
            stale = self._is_stale(memory)

            # Store stale flag on the object (useful for debugging / UI later)
            memory.is_stale = stale

            # Simple decay rule:
            # - Fresh memory: keep score as-is
            # - Stale memory: reduce score by 50%
            adjusted_score = raw_score * (0.5 if stale else 1.0)

            results.append(
                RetrievedMemory(
                    memory=memory,
                    raw_score=raw_score,
                    adjusted_score=adjusted_score,
                )
            )

        # 4) Sort by adjusted_score so fresh relevant memories rank higher
        results.sort(key=lambda r: r.adjusted_score, reverse=True)

        return results


# Shared service instance
retrieval_service = RetrievalService()
