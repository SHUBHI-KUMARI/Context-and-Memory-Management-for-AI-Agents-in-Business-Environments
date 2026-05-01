"""FAISS setup (vector index).

Beginner-friendly notes:
- FAISS is a library for fast similarity search over vectors.
- We'll store embeddings (vectors) in a FAISS index.
- FAISS only stores vectors (numbers). It does NOT store your original text.

So in this module we keep:
- the FAISS index (vectors)
- a simple list that maps FAISS row -> memory_id

Later (in vector_store.py) we will also store full metadata/content.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np

try:
    import faiss  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "FAISS is not installed. Install it with: pip install faiss-cpu"
    ) from exc


# -----------------------------
# Module-level (in-memory) state
# -----------------------------

# The FAISS index instance. We create it lazily once we know vector dimension.
_faiss_index: Optional[faiss.Index] = None

# Mapping from vector position -> memory_id
# Example: if memory_ids[7] == "abc", then vector at index row 7 is memory "abc".
_memory_ids: List[str] = []


def _normalize(vector: np.ndarray) -> np.ndarray:
    """Normalize a vector to unit length.

    Why?
    - We'll use IndexFlatIP (inner product).
    - If vectors are normalized, inner product ~= cosine similarity.

    Args:
    - vector: shape (d,)

    Returns:
    - normalized vector with shape (d,)
    """

    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm


def _ensure_index(dimension: int) -> faiss.Index:
    """Create the FAISS index if it doesn't exist yet.

    We use IndexFlatIP:
    - IP = inner product
    - Fast and simple (no training needed)

    Args:
    - dimension: number of floats in each vector

    Returns:
    - a ready-to-use FAISS index
    """

    global _faiss_index

    if _faiss_index is None:
        # Inner Product index. With normalized vectors, this behaves like cosine similarity.
        _faiss_index = faiss.IndexFlatIP(dimension)

    return _faiss_index


def add_memory_to_index(memory_id: str, embedding: List[float]) -> None:
    """Add ONE memory embedding to the FAISS index.

    Args:
    - memory_id: your memory's unique identifier (string)
    - embedding: list of floats (vector)

    What it does:
    - Creates the index lazily (first time) based on embedding dimension
    - Normalizes the vector
    - Adds it to FAISS
    - Stores the memory_id in a parallel list
    """

    # Convert to numpy float32 (FAISS expects float32 arrays).
    vector = np.array(embedding, dtype="float32")

    # Create the index if needed.
    index = _ensure_index(dimension=vector.shape[0])

    # Normalize for cosine-like similarity.
    vector = _normalize(vector)

    # Add a single vector. FAISS expects shape (n_vectors, dimension).
    index.add(vector.reshape(1, -1))

    # Save mapping so we can convert FAISS results back to our memory IDs.
    _memory_ids.append(memory_id)


def search_similar_memories(query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
    """Search FAISS for the top-k most similar memories.

    Args:
    - query_embedding: embedding of the search query
    - top_k: number of results to return

    Returns:
    - list of (memory_id, score)

    Notes:
    - Higher score = more similar (because we use inner product).
    - If the index is empty, returns an empty list.
    """

    if _faiss_index is None or _faiss_index.ntotal == 0:
        return []

    # Convert query to numpy float32 and normalize.
    query_vec = np.array(query_embedding, dtype="float32")
    query_vec = _normalize(query_vec)

    # Search expects shape (n_queries, dimension).
    scores, indices = _faiss_index.search(query_vec.reshape(1, -1), top_k)

    results: List[Tuple[str, float]] = []

    # scores and indices are 2D arrays: (1, top_k)
    for idx, score in zip(indices[0], scores[0]):
        # FAISS uses -1 when it cannot find a result.
        if idx == -1:
            continue

        # Convert FAISS row index back to our memory_id.
        # Defensive check: idx should always be in range.
        if 0 <= idx < len(_memory_ids):
            results.append((_memory_ids[idx], float(score)))

    return results


def reset_faiss_index() -> None:
    """Reset the in-memory FAISS index (useful for local dev/testing).

    Warning:
    - This deletes ALL vectors and memory_id mappings in memory.
    - We'll NOT call this in normal API flow.
    """

    global _faiss_index, _memory_ids

    _faiss_index = None
    _memory_ids = []
