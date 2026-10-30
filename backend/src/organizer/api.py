import logging
import secrets

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from organizer.config import ConfigError
from organizer.lock import LockHeldError
from organizer.service import OrganizerRunningError

# Where the Tauri window loads the interface from (development and built app).
DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:1420",
    "tauri://localhost",
    "http://tauri.localhost",
]


class SettingsUpdate(BaseModel):
    watch_folder: str
    destination_root: str


def error_response(status_code, code, message):
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


def create_app(token, service, on_shutdown=None, allowed_origins=None):
    app = FastAPI()

    @app.middleware("http")
    async def require_token(request: Request, call_next):
        expected = f"Bearer {token}"
        received = request.headers.get("Authorization", "")

        if not secrets.compare_digest(received.encode(), expected.encode()):
            return error_response(401, "unauthorized", "Missing or invalid token.")

        return await call_next(request)

    # Added after the token check so it runs first and can answer the
    # browser's preflight request, which never carries the token.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins if allowed_origins is not None else DEFAULT_ALLOWED_ORIGINS,
        allow_methods=["GET", "POST", "PUT"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.exception_handler(ConfigError)
    async def invalid_settings(request: Request, error: ConfigError):
        return error_response(400, "invalid_settings", str(error))

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, error: RequestValidationError):
        return error_response(
            400, "invalid_request", "The request body is missing fields or has the wrong format."
        )

    @app.exception_handler(LockHeldError)
    async def already_running(request: Request, error: LockHeldError):
        return error_response(409, "already_running", str(error))

    @app.exception_handler(OrganizerRunningError)
    async def organizer_running(request: Request, error: OrganizerRunningError):
        return error_response(409, "organizer_running", str(error))

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, error: Exception):
        logging.exception("Unexpected API error")
        return error_response(500, "internal_error", "Something went wrong. Check the logs.")

    @app.get("/status")
    def get_status():
        return service.status()

    @app.post("/start")
    def start():
        return service.start()

    @app.post("/stop")
    def stop():
        return service.stop()

    @app.get("/settings")
    def get_settings():
        return service.settings()

    @app.put("/settings")
    def put_settings(update: SettingsUpdate):
        return service.update_settings(update.watch_folder, update.destination_root)

    @app.get("/activity")
    def get_activity():
        return service.activity.events()

    @app.post("/shutdown")
    def shutdown(background_tasks: BackgroundTasks):
        service.stop()
        # Exit only after this response has been sent.
        if on_shutdown is not None:
            background_tasks.add_task(on_shutdown)
        return {"state": "stopped", "message": None}

    return app
