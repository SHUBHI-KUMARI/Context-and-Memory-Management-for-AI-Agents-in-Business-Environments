"""Vector store wrapper (FAISS + stored memory data).

Beginner-friendly notes:
- FAISS stores ONLY vectors (numbers).
- But our app needs to return full memories (content, timestamp, metadata).

So this module combines:
1) FAISS index (for similarity search)
2) A Python in-memory dictionary mapping memory_id -> Memory record

Important:
- This is an in-memory store (good for learning + prototyping).
- If you restart the server, the data is gone.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from app.db.faiss_setup import add_memory_to_index, reset_faiss_index, search_similar_memories
from app.models.memory_model import Memory


@dataclass
class StoredMemory:
    """A simple container we keep in Python memory.

    We store:
    - the original Memory object
    - its embedding vector (for debugging / optional future use)

    Note:
    - FAISS already stores the embedding, so saving it again is optional.
      We keep it because your spec asked to store embeddings too.
    """

    memory: Memory
    embedding: List[float]


class InMemoryVectorStore:
    """A tiny vector store built on top of FAISS.

    Responsibilities:
    - Add a Memory + embedding
    - Search similar memories by query embedding
    - Return full Memory objects with similarity scores

    This is intentionally simple and beginner-friendly.
    """

    def __init__(self) -> None:
        # Map memory_id -> StoredMemory
        self._items: Dict[str, StoredMemory] = {}

    def add(self, memory: Memory, embedding: List[float]) -> None:
        """Add a memory to the store.

        Steps:
        1) Add vector to FAISS (for similarity search)
        2) Save the full Memory + embedding in a dict

        Note about duplicates:
        - FAISS (in our simple setup) does not support deleting/updating vectors easily.
        - So if an id already exists, we raise an error to avoid inconsistent state.
        """

        if memory.id in self._items:
            raise ValueError(
                f"Memory with id '{memory.id}' already exists. "
                "Use a new id (or restart the server during early testing)."
            )

        add_memory_to_index(memory_id=memory.id, embedding=embedding)
        self._items[memory.id] = StoredMemory(memory=memory, embedding=embedding)

    def get(self, memory_id: str) -> Optional[Memory]:
        """Fetch a stored memory by id (or return None if not found)."""

        item = self._items.get(memory_id)
        return item.memory if item else None

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[Memory, float]]:
        """Search for similar memories.

        Args:
        - query_embedding: embedding vector for the user's query
        - top_k: number of results

        Returns:
        - list of (Memory, similarity_score)

        Note:
        - The score comes from FAISS inner-product similarity.
        - Higher score means more similar.
        """

        id_and_scores = search_similar_memories(query_embedding=query_embedding, top_k=top_k)

        results: List[Tuple[Memory, float]] = []
        for memory_id, score in id_and_scores:
            item = self._items.get(memory_id)
            if item is None:
                # This should not happen, but we handle it safely.
                continue
            results.append((item.memory, score))

        return results

    def count(self) -> int:
        """How many memories are currently stored?"""

        return len(self._items)

    def reset(self) -> None:
        """Reset EVERYTHING (dev/testing only).

        - Clears FAISS index
        - Clears in-memory dict
        """

        reset_faiss_index()
        self._items = {}


# A single shared instance (simple for a beginner project)
vector_store = InMemoryVectorStore()
