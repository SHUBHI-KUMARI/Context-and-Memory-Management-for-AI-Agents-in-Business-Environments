"""Embedding utilities.

Beginner-friendly notes:
- "Embeddings" turn text into a list of numbers (a vector).
- Similar text tends to have similar vectors.
- We store vectors in FAISS so we can later search for "similar" memories.

This file keeps things minimal:
- If you set OPENAI_API_KEY, it will use OpenAI embeddings.
- Otherwise it will fall back to a HuggingFace embedding model running locally.

You'll install dependencies later (we'll list them when we reach testing).
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import List, Sequence


DEFAULT_HF_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model():
    """Create (and cache) an embeddings model.

    Why cache?
    - Creating embedding models can be slow.
    - We want to create it once and reuse it across requests.

    Returns:
    - A LangChain embeddings object that supports:
      - embed_documents(list_of_texts)
      - embed_query(single_text)
    """

    # If the user provides an OpenAI API key, prefer OpenAI embeddings.
    if os.getenv("OPENAI_API_KEY"):
        try:
            # Newer LangChain split package
            from langchain_openai import OpenAIEmbeddings
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "OpenAI embeddings selected, but 'langchain-openai' is not installed. "
                "Install it with: pip install langchain-openai"
            ) from exc

        # Keep defaults simple. You can choose another model later.
        return OpenAIEmbeddings()

    # Otherwise, use a local HuggingFace sentence-transformers model.
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "HuggingFace embeddings selected, but 'langchain-community' is not installed. "
            "Install it with: pip install langchain-community"
        ) from exc

    # This will download the model the first time you run it.
    return HuggingFaceEmbeddings(model_name=DEFAULT_HF_MODEL_NAME)


def embed_texts(texts: Sequence[str]) -> List[List[float]]:
    """Generate embeddings for multiple texts.

    Args:
    - texts: list/sequence of text strings

    Returns:
    - list of vectors (one vector per input text)
    """

    model = get_embedding_model()
    return model.embed_documents(list(texts))


def embed_query(query: str) -> List[float]:
    """Generate an embedding for a single query string."""

    model = get_embedding_model()
    return model.embed_query(query)
