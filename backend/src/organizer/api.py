from fastapi import FastAPI

def create_app():
    app = FastAPI()
    @app.get("/status")
    def get_status():
        return{"state": "stopped", "message": None}

    return app