"""FastAPI application entrypoint.

Beginner-friendly notes:
- This file creates the FastAPI app object.
- We keep routes modular (each set of endpoints lives in its own file).
- You will run the server with Uvicorn (an ASGI server).

Run (from the `backend/` folder):
    uvicorn app.main:app --reload

`--reload` auto-restarts the server when you change code.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Import routers (collections of endpoints)
from app.api.routes.health_routes import router as health_router
from app.api.routes.memory_routes import router as memory_router
from app.api.routes.decision_routes import router as decision_router

# Services / stores (used for optional dummy-data seeding)
from app.db.vector_store import vector_store
from app.services.memory_service import memory_service


def create_app() -> FastAPI:
    """Create and configure the FastAPI app.

    We use a factory function so the app setup stays organized as the project grows.
    """

    app = FastAPI(
        title="Context & Memory Management System (Backend)",
        version="0.1.0",
    )

    # Configure CORS - allows frontend (localhost:5173) to call backend API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Adjust for frontend origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
        allow_headers=["*"],  # Allows all headers
    )

    # Register routers
    app.include_router(health_router)
    app.include_router(memory_router)
    app.include_router(decision_router)

    # Optional: seed sample memories on startup (beginner-friendly)
    # Disable by setting: SEED_DUMMY_DATA=false
    @app.on_event("startup")
    def _seed_dummy_data() -> None:
        seed_flag = os.getenv("SEED_DUMMY_DATA", "true").strip().lower()
        should_seed = seed_flag not in {"0", "false", "no"}

        # Seed only once (per process) to avoid duplicates.
        if should_seed and vector_store.count() == 0:
            memory_service.seed_dummy_data()

    return app


# ASGI app instance (Uvicorn looks for this variable by default)
app = create_app()


if __name__ == "__main__":
    # Optional convenience:
    # Run from the `backend/` folder with:
    #     python -m app.main
    # (Most commonly you'll run with: `uvicorn app.main:app --reload`)
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
