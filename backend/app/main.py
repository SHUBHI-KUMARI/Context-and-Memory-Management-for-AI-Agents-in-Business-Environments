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

# Import routers (collections of endpoints)
from app.api.routes.health_routes import router as health_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI app.

    We use a factory function so the app setup stays organized as the project grows.
    """

    app = FastAPI(
        title="Context & Memory Management System (Backend)",
        version="0.1.0",
    )

    # Register routers
    app.include_router(health_router)

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
