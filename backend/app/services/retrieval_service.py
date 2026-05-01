"""Retrieval service (business logic for searching memories).

Beginner-friendly notes:
- We store memories as vectors in FAISS.
- To search, we embed the user's query into a vector.
- FAISS returns the most similar stored vectors.

Ranking goal (simple + demo-friendly):
- We don't want *only* "most similar text".
- We also want *recent* and *important types* of memories to show first.

So we combine 3 simple factors:
1) Semantic similarity (from FAISS)
2) Recency (newer memories get a small boost)
3) Type priority (experiential > historical > temporal > immediate)

Stale memory rule:
- If a memory is older than ~6 months, we mark it as "stale".
- Stale memories are still returned, but we reduce their score.

Why reduce importance?
- Old events might be less relevant than recent ones.
- This is a simple way to simulate memory decay without an LLM.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

from app.db.vector_store import vector_store
from app.models.memory_model import Memory, MemoryType
from app.utils.embeddings import embed_query
from app.utils.time_utils import DEFAULT_STALE_DAYS, is_stale, to_utc


# ----------------------
# Simple ranking weights
# ----------------------

# We approximate 6 months as 180 days to keep it beginner-simple.
STALE_DAYS = DEFAULT_STALE_DAYS

# Memory type priority (as requested):
# experiential > historical > temporal > immediate
TYPE_MULTIPLIER = {
    MemoryType.experiential: 1.30,
    MemoryType.historical: 1.20,
    MemoryType.temporal: 1.10,
    MemoryType.immediate: 1.00,
}


@dataclass
class RetrievedMemory:
    """A retrieval result with scoring details.

    - memory: the stored Memory
    - raw_score: score returned by FAISS (higher = more similar)
    - adjusted_score: final score after all simple factors
    - reason: short explanation (why this memory ranked high)
    """

    memory: Memory
    raw_score: float
    adjusted_score: float
    reason: str


class RetrievalService:
    """Core logic for retrieving relevant memories."""

    def _recency_multiplier(self, timestamp: datetime, *, now: datetime) -> float:
        """Give a small boost to newer memories.

        This is intentionally simple and "good enough" for a demo.
        """

        age_days = (to_utc(now) - to_utc(timestamp)).days

        if age_days <= 7:
            return 1.30
        if age_days <= 30:
            return 1.20
        if age_days <= 90:
            return 1.10
        if age_days <= STALE_DAYS:
            return 1.00

        # Older than ~6 months
        return 0.80

    def _type_multiplier(self, memory_type: MemoryType) -> float:
        """Boost certain memory types so they appear earlier."""

        return TYPE_MULTIPLIER.get(memory_type, 1.0)

    def _build_reason(
        self,
        *,
        raw_score: float,
        recency_mult: float,
        type_mult: float,
        stale_mult: float,
        age_days: int,
        memory_type: MemoryType,
        adjusted_score: float,
    ) -> str:
        """Human-readable explanation for ranking."""

        return (
            f"similarity={raw_score:.3f} * "
            f"recency(age_days={age_days})={recency_mult:.2f} * "
            f"type({memory_type.value})={type_mult:.2f} * "
            f"stale_penalty={stale_mult:.2f} => score={adjusted_score:.3f}"
        )

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

        # 2) Ask vector_store (FAISS) for candidates
        # IMPORTANT: We intentionally fetch MORE than top_k and then re-rank.
        # Why?
        # - FAISS only knows semantic similarity.
        # - We also want to factor in recency and type priority.
        candidate_k = min(max(top_k * 3, top_k), 20)
        matches = vector_store.search(query_embedding=query_vector, top_k=candidate_k)

        # 3) Apply simple scoring factors and build reasons
        now = datetime.now(timezone.utc)

        results: List[RetrievedMemory] = []
        for memory, raw_score in matches:
            # Stale check (older than ~6 months)
            stale = is_stale(memory.timestamp, now=now, stale_days=STALE_DAYS)
            memory.is_stale = stale

            # Multipliers
            recency_mult = self._recency_multiplier(memory.timestamp, now=now)
            type_mult = self._type_multiplier(memory.type)

            # Simple stale penalty: reduce score (do not remove from results)
            stale_mult = 0.50 if stale else 1.00

            # Final score (easy to reason about)
            adjusted_score = float(raw_score) * recency_mult * type_mult * stale_mult

            age_days = (to_utc(now) - to_utc(memory.timestamp)).days
            reason = self._build_reason(
                raw_score=float(raw_score),
                recency_mult=recency_mult,
                type_mult=type_mult,
                stale_mult=stale_mult,
                age_days=age_days,
                memory_type=memory.type,
                adjusted_score=adjusted_score,
            )

            results.append(
                RetrievedMemory(
                    memory=memory,
                    raw_score=float(raw_score),
                    adjusted_score=adjusted_score,
                    reason=reason,
                )
            )

        # 4) Sort by adjusted_score so recent/important memories rank higher
        results.sort(key=lambda r: r.adjusted_score, reverse=True)

        # 5) Return only the final top_k
        return results[:top_k]


# Shared service instance
retrieval_service = RetrievalService()
