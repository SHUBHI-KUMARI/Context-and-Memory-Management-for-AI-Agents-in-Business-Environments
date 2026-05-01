"""Pydantic model for a single piece of business memory.

Beginner-friendly notes:
- A "model" is just a structured definition of data.
- Pydantic validates input data (types, required fields, etc.).
- We'll store each Memory as text + metadata, and later embed the text
  into vectors for similarity search.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """Allowed categories for memories.

    We use an Enum so the API can only accept one of these values.
    """

    immediate = "immediate"
    historical = "historical"
    temporal = "temporal"
    experiential = "experiential"


class Memory(BaseModel):
    """Represents one stored memory item.

    Fields:
    - id: unique identifier for this memory
    - type: category of memory (immediate/historical/temporal/experiential)
    - content: the text we want to store and search later
    - timestamp: when the memory happened / was recorded
    - metadata: extra info like supplier name, issue type, tags, etc.

    Note:
    - For now, we keep the model small and flexible.
    """

    # Auto-generate a unique id if the client doesn't provide one.
    id: str = Field(default_factory=lambda: str(uuid4()))

    # Memory type is required and must be one of MemoryType values.
    type: MemoryType

    # The main text content we will embed and search.
    content: str = Field(min_length=1)

    # Default to "now" in UTC if not provided.
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Optional extra details. default_factory avoids the common "mutable default" bug.
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Optional helper field: sometimes you might want to mark state without changing content.
    # We won't rely on this yet, but it's handy for later features.
    is_stale: Optional[bool] = None

    class Config:
        """Pydantic configuration.

        - extra = "allow" lets you send extra fields without crashing.
          As a beginner-friendly choice, this makes the API more forgiving.
        """

        extra = "allow"
        json_encoders = {
            # Ensure datetimes serialize cleanly in JSON responses.
            datetime: lambda dt: dt.isoformat(),
        }
