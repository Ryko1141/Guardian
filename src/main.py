"""FastAPI entrypoint exposing the Guardian compliance API.

This module exists to provide a conventional `app` object for deployment tools
that auto-discover ASGI applications (e.g., uvicorn, gunicorn, Fly.io).
"""
from src.compliance_api import app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8010, log_level="info")
