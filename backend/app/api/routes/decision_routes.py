"""Decision API routes.

Beginner-friendly notes:
- This file defines the HTTP endpoint for making a decision.
- It calls the DecisionService, which uses retrieved memories + simple rules.

Endpoint in this file:
- POST /decision -> returns a decision based on stored memories
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.models.memory_model import Memory
from app.services.decision_service import decision_service


router = APIRouter(tags=["decision"])


class DecisionRequest(BaseModel):
    """Request body for /decision."""

    query: str = Field(..., min_length=1, description="Question/context to decide on, e.g. 'Supplier XYZ'")
    top_k: int = Field(5, ge=1, le=10, description="How many relevant memories to consider")


class DecisionResponse(BaseModel):
    """Response model for /decision."""

    query: str
    decision: str
    reason: str

    # Useful context for debugging/explaining why the decision happened
    relevant_memories: List[Memory]
    recent_negative_memories: List[Memory]


@router.post("/decision", response_model=DecisionResponse)
def make_decision(payload: DecisionRequest) -> Dict[str, Any]:
    """Make a decision using memory + simple rules."""

    return decision_service.decide(query=payload.query, top_k=payload.top_k)
