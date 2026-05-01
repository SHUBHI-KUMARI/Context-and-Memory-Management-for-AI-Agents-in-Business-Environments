"""Health check routes.

Why this exists:
- A health endpoint is a simple way to confirm the server is up.
- Load balancers / monitoring tools often call `/health`.
"""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict:
    """Simple health check endpoint."""

    return {
        "status": "ok",
        "service": "backend",
    }
