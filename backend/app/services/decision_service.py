"""Decision service (simple rule-based decision making).

Beginner-friendly notes:
- This is NOT an LLM-based system.
- We use simple rules to turn retrieved memories into an action.

Rule (as requested):
- If there are recent negative issues -> "Flag for inspection"
- Else -> "Approve"

"Recent" (simple definition):
- Within the last 90 days

"Negative" (simple definition):
- memory.metadata["issue_type"] is in a known negative list, OR
- the memory.content contains negative keywords

You can tweak these rules later as your project grows.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.models.memory_model import Memory
from app.services.retrieval_service import RetrievedMemory, retrieval_service
from app.utils.time_utils import to_utc


# ----------------------
# Simple rule parameters
# ----------------------

# Approx: "recent" = last 90 days
RECENT_DAYS = 90

# If metadata contains these issue types, we treat it as negative.
NEGATIVE_ISSUE_TYPES = {
    "quality",
    "payment_dispute",
    "dispute",
    "late_delivery",
    "delay",
    "complaint",
}

# If memory content contains these words/phrases, we treat it as negative.
NEGATIVE_KEYWORDS = [
    "quality issue",
    "quality issues",
    "defect",
    "defects",
    "complaint",
    "dispute",
    "rejected",
    "failed inspection",
    "late delivery",
    "delay",
]


class DecisionService:
    """Core logic for making decisions using retrieved memories."""

    def _is_recent(self, timestamp: datetime, *, now: Optional[datetime] = None) -> bool:
        """Return True if timestamp is within RECENT_DAYS."""

        if now is None:
            now = datetime.now(timezone.utc)

        age_days = (to_utc(now) - to_utc(timestamp)).days
        return age_days <= RECENT_DAYS

    def _is_negative(self, memory: Memory) -> bool:
        """Return True if a memory looks like a negative issue."""

        issue_type = str(memory.metadata.get("issue_type", "")).strip().lower()
        if issue_type in NEGATIVE_ISSUE_TYPES:
            return True

        content = memory.content.lower()
        return any(keyword in content for keyword in NEGATIVE_KEYWORDS)

    def decide(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Make a decision for a given query.

        Args:
        - query: e.g. "Supplier XYZ"
        - top_k: how many relevant memories to consider

        Returns:
        - a simple dict with:
          - decision: "Flag for inspection" | "Approve"
          - reason: short explanation
          - relevant_memories: the retrieved memories
          - recent_negative_memories: only the ones that triggered the rule

        Note:
        - We return a dict to keep things beginner-simple.
        - Later you can introduce Pydantic response models if you want.
        """

        retrieved: List[RetrievedMemory] = retrieval_service.search(query=query, top_k=top_k)

        now = datetime.now(timezone.utc)

        recent_negative: List[Memory] = []
        for item in retrieved:
            memory = item.memory
            if self._is_negative(memory) and self._is_recent(memory.timestamp, now=now):
                recent_negative.append(memory)

        if recent_negative:
            decision = "Flag for inspection"
            reason = (
                f"Found {len(recent_negative)} recent negative issue(s) "
                f"in the last {RECENT_DAYS} days."
            )
        else:
            decision = "Approve"
            reason = "No recent negative issues found in memory."

        return {
            "query": query,
            "decision": decision,
            "reason": reason,
            "relevant_memories": [item.memory for item in retrieved],
            "recent_negative_memories": recent_negative,
        }


# Shared service instance
decision_service = DecisionService()
