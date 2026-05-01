"""Memory API routes.

Beginner-friendly notes:
- This file defines the HTTP endpoints related to memory.
- Routes should be thin: they call the service layer which does the real work.

Endpoints in this file:
- POST /memory/add    -> add a new memory
- GET  /memory/search -> retrieve relevant memories
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.models.memory_model import Memory, MemoryType
from app.services.memory_service import memory_service
from app.services.retrieval_service import RetrievedMemory, retrieval_service


router = APIRouter(prefix="/memory", tags=["memory"])


class AddMemoryRequest(BaseModel):
    """Request body for adding a memory."""

    # We accept "type" and map it to MemoryType.
    type: MemoryType = Field(..., description="Memory type: immediate/historical/temporal/experiential")

    # The main text we want to store and search.
    content: str = Field(..., min_length=1, description="The memory text/content")

    # Extra details like supplier name, issue type, invoice number, etc.
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    # Optional: if not provided, the backend will set it to now (UTC)
    timestamp: Optional[datetime] = None

    # Optional: if not provided, the backend will generate a UUID
    id: Optional[str] = None


class SearchMemoryResponseItem(BaseModel):
    """One search result item."""

    memory: Memory
    raw_score: float
    adjusted_score: float


@router.post("/add", response_model=Memory)
def add_memory(payload: AddMemoryRequest) -> Memory:
    """Add a new memory to the system.

    This endpoint:
    1) Validates the request body
    2) Generates an embedding for the content
    3) Stores it in FAISS (vector index) and in-memory mapping
    """

    return memory_service.add_memory(
        memory_type=payload.type,
        content=payload.content,
        metadata=payload.metadata,
        timestamp=payload.timestamp,
        memory_id=payload.id,
    )


@router.get("/search", response_model=List[SearchMemoryResponseItem])
def search_memories(
    query: str = Query(..., description="Search query, e.g. 'Supplier XYZ invoice'"),
    top_k: int = Query(5, ge=1, le=10, description="Number of results (we typically use 3-5)"),
) -> List[SearchMemoryResponseItem]:
    """Search for relevant memories.

    This endpoint:
    1) Embeds the query text
    2) Searches the vector store
    3) Applies a stale-memory penalty (older than ~6 months)

    Returns:
    - A list of results with memory + scores
    """

    results: List[RetrievedMemory] = retrieval_service.search(query=query, top_k=top_k)

    return [
        SearchMemoryResponseItem(
            memory=item.memory,
            raw_score=item.raw_score,
            adjusted_score=item.adjusted_score,
        )
        for item in results
    ]
