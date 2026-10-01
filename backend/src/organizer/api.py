from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import secrets

def create_app(token):
    app = FastAPI()
    @app.middleware("http")
    async def require_token(request: Request, call_next):
        expected = f"Bearer {token}"
        received = request.headers.get("Authorization", "")

        if not secrets.compare_digest(received.encode(), expected.encode()):
            return JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "code": "unauthorized",
                        "message": "Missing or invalid token.",
                    }
                },
            )

        return await call_next(request)

    @app.get("/status")
    def get_status():
        return{"state": "stopped", "message": None}

    return app