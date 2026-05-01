"""Memory service (business logic for storing memories).

Beginner-friendly notes:
- "Routes" (API endpoints) should stay thin: they receive a request and return a response.
- "Services" contain the core logic (the real work).

This service is responsible for:
1) Creating/validating a Memory object
2) Generating an embedding for the Memory content
3) Storing it in our vector store (FAISS + in-memory mapping)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.db.vector_store import vector_store
from app.models.memory_model import Memory, MemoryType
from app.utils.embeddings import embed_texts


class MemoryService:
    """Core logic for adding and managing memories."""

    def add_memory(
        self,
        *,
        memory_type: MemoryType,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        memory_id: Optional[str] = None,
    ) -> Memory:
        """Create and store a new memory.

        Args:
        - memory_type: one of immediate/historical/temporal/experiential
        - content: the main text we want to remember
        - metadata: optional extra info (supplier, issue_type, etc.)
        - timestamp: optional; defaults to now in UTC
        - memory_id: optional; if not provided a UUID will be generated

        Returns:
        - The saved Memory object

        What happens inside:
        1) Build a Memory (Pydantic validates it)
        2) Create an embedding for the content
        3) Store in vector_store
        """

        if metadata is None:
            metadata = {}

        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        # 1) Build the Memory object (validates fields)
        memory = Memory(
            id=memory_id or None,
            type=memory_type,
            content=content,
            timestamp=timestamp,
            metadata=metadata,
        )

        # 2) Generate embedding for the content
        # embed_texts expects a list of strings, so we pass [memory.content]
        embedding = embed_texts([memory.content])[0]

        # 3) Store in the vector store (FAISS + dict)
        vector_store.add(memory=memory, embedding=embedding)

        return memory

    def seed_dummy_data(self) -> None:
        """Add a few sample memories (dummy data) for learning/testing.

        This matches your project examples:
        - Supplier XYZ had quality issues 4 months ago
        - Payment dispute 8 months ago
        - Good performance in last 2 months

        Note:
        - We do NOT run this automatically yet.
        - Later, we can call it from a FastAPI startup event if you want.
        """

        now = datetime.now(timezone.utc)

        # Helper: approximate months as 30 days to keep logic simple.
        def months_ago(months: int) -> datetime:
            from datetime import timedelta

            return now - timedelta(days=30 * months)

        self.add_memory(
            memory_type=MemoryType.historical,
            content="Supplier XYZ had quality issues with delivered components.",
            timestamp=months_ago(4),
            metadata={
                "supplier": "XYZ",
                "issue_type": "quality",
                "severity": "high",
            },
        )

        self.add_memory(
            memory_type=MemoryType.historical,
            content="Payment dispute occurred with Supplier XYZ regarding invoice INV-1008.",
            timestamp=months_ago(8),
            metadata={
                "supplier": "XYZ",
                "issue_type": "payment_dispute",
                "invoice": "INV-1008",
            },
        )

        self.add_memory(
            memory_type=MemoryType.experiential,
            content="Supplier XYZ showed good on-time delivery performance recently.",
            timestamp=months_ago(2),
            metadata={
                "supplier": "XYZ",
                "issue_type": "positive_performance",
                "metric": "on_time_delivery",
            },
        )


# A shared service instance (simple for beginners)
memory_service = MemoryService()
