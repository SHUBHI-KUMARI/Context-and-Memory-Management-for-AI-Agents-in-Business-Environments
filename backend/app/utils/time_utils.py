"""Time utilities.

Beginner-friendly notes:
- We need a simple way to decide if a memory is "stale".
- Your rule: older than 6 months => stale.

To keep it simple, we approximate:
- 6 months ~= 180 days

(You can always make this more accurate later.)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional


DEFAULT_STALE_DAYS = 180


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
