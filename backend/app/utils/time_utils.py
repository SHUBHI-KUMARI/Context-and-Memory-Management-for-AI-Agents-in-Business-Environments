"""Time utilities.

Beginner-friendly notes:
- We need a simple way to decide if a memory is "stale".
- Your rule: older than 6 months => stale.

To keep it simple, we approximate:
- 6 months ~= 180 days

(You can always make this more accurate later.)

Stale handling (for retrieval scoring):
- We do NOT delete/ignore stale memories.
- We simply reduce their score using a multiplier (default 0.5).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional


DEFAULT_STALE_DAYS = 180
DEFAULT_STALE_MULTIPLIER = 0.5


def to_utc(dt: datetime) -> datetime:
    """Ensure a datetime is timezone-aware and in UTC.

    Why?
    - Some timestamps might be "naive" (no timezone info).
    - For consistent comparisons, we treat naive timestamps as UTC.

    Args:
    - dt: datetime

    Returns:
    - timezone-aware datetime in UTC
    """

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


def is_stale(
    timestamp: datetime,
    *,
    now: Optional[datetime] = None,
    stale_days: int = DEFAULT_STALE_DAYS,
) -> bool:
    """Return True if the timestamp is older than `stale_days`.

    Args:
    - timestamp: when the memory happened / was saved
    - now: current time (optional). If None, uses current UTC time.
    - stale_days: how many days until a memory is considered stale

    Returns:
    - True if stale, else False
    """

    if now is None:
        now = datetime.now(timezone.utc)

    ts_utc = to_utc(timestamp)
    now_utc = to_utc(now)

    age_days = (now_utc - ts_utc).days
    return age_days > stale_days


def stale_score_multiplier(
    timestamp: datetime,
    *,
    now: Optional[datetime] = None,
    stale_days: int = DEFAULT_STALE_DAYS,
    multiplier_if_stale: float = DEFAULT_STALE_MULTIPLIER,
) -> float:
    """Return a score multiplier based on staleness.

    This is a tiny helper used during retrieval ranking.

    Rule:
    - If stale -> return `multiplier_if_stale` (example: 0.5)
    - If not stale -> return 1.0

    Args:
    - timestamp: memory timestamp
    - now: current time (optional)
    - stale_days: days threshold for staleness
    - multiplier_if_stale: penalty multiplier when stale

    Returns:
    - 1.0 (fresh) or `multiplier_if_stale` (stale)
    """

    return multiplier_if_stale if is_stale(timestamp, now=now, stale_days=stale_days) else 1.0


def apply_stale_penalty(
    score: float,
    timestamp: datetime,
    *,
    now: Optional[datetime] = None,
    stale_days: int = DEFAULT_STALE_DAYS,
    multiplier_if_stale: float = DEFAULT_STALE_MULTIPLIER,
) -> float:
    """Apply the stale penalty to a score.

    Example:
    - If score = 0.8 and memory is stale -> returns 0.8 * 0.5 = 0.4
    """

    return score * stale_score_multiplier(
        timestamp,
        now=now,
        stale_days=stale_days,
        multiplier_if_stale=multiplier_if_stale,
    )
