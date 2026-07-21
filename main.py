"""API entrypoint: uvicorn main:app --reload --port 8000"""

from dotenv import load_dotenv

load_dotenv()

from fsm_platform.host.http.app import app  # noqa: E402

__all__ = ["app"]
