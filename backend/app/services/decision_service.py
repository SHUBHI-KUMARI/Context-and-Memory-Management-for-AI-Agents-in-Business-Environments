"""Decision service (simple rule-based decision making).

Beginner-friendly notes:
- This is NOT an LLM-based system.
- We use simple rules to turn retrieved memories into an action.

Rule (as requested):
- If there are recent negative issues -> "Flag for inspection"
- Else -> "Approve"

"Recent" (simple definition):
- Within the last ~6 months (180 days)

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

# Approx: "recent" = last 180 days (~6 months)
# This lines up nicely with the demo sample memory: "quality issues 4 months ago".
RECENT_DAYS = 180

# Some issue types are "more risky" than others.
HIGH_RISK_ISSUE_TYPES = {
    "quality",
    "failed_inspection",
}

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

    def _age_days(self, timestamp: datetime, *, now: Optional[datetime] = None) -> int:
        """Return how many days old a memory is."""

        if now is None:
            now = datetime.now(timezone.utc)

        return (to_utc(now) - to_utc(timestamp)).days

    def _is_recent(self, timestamp: datetime, *, now: Optional[datetime] = None) -> bool:
        """Return True if timestamp is within RECENT_DAYS."""

        if now is None:
            now = datetime.now(timezone.utc)

        return self._age_days(timestamp, now=now) <= RECENT_DAYS

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
                    - risk_level: "Low" | "Medium" | "High"
                    - explanation: a readable sentence explaining WHY
                    - relevant_memories: the retrieved memories
                    - recent_negative_memories: only the ones that triggered the rule

        Note:
        - We return a dict to keep things beginner-simple.
        - Later you can introduce Pydantic response models if you want.
        """

        retrieved: List[RetrievedMemory] = retrieval_service.search(query=query, top_k=top_k)

        now = datetime.now(timezone.utc)

        recent_negative: List[Memory] = []
        recent_negative_summaries: List[str] = []

        any_high_risk_issue = False
        for item in retrieved:
            memory = item.memory
            if not self._is_negative(memory):
                continue

            age_days = self._age_days(memory.timestamp, now=now)
            issue_type = str(memory.metadata.get("issue_type", "")).strip().lower()
            severity = str(memory.metadata.get("severity", "")).strip().lower()

            if issue_type in HIGH_RISK_ISSUE_TYPES or severity in {"high", "critical"}:
                any_high_risk_issue = True

            if age_days <= RECENT_DAYS:
                recent_negative.append(memory)
                # Short, beginner-friendly summary used in the explanation.
                label = issue_type or "negative_issue"
                recent_negative_summaries.append(f"{label} ({age_days} days ago)")

        if recent_negative:
            decision = "Flag for inspection"

            if any_high_risk_issue or len(recent_negative) >= 2:
                risk_level = "High"
            else:
                risk_level = "Medium"

            triggers = ", ".join(recent_negative_summaries[:3])
            explanation = (
                "Decision flagged because recent negative issues were found in memory "
                f"(last {RECENT_DAYS} days): {triggers}."
            )
            reason = f"Found {len(recent_negative)} recent negative issue(s)."
        else:
            decision = "Approve"
            risk_level = "Low"
            explanation = (
                f"Decision approved because no negative issues were found in the last {RECENT_DAYS} days "
                "among the most relevant memories."
            )
            reason = "No recent negative issues found in memory."

        return {
            "query": query,
            "decision": decision,
            "risk_level": risk_level,
            "explanation": explanation,
            # Keep 'reason' for backward compatibility with the current API model.
            "reason": reason,
            "relevant_memories": [item.memory for item in retrieved],
            "recent_negative_memories": recent_negative,
        }


# Shared service instance
decision_service = DecisionService()
