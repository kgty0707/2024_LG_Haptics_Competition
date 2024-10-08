from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from app.common.util import register

def create_app():
    app = FastAPI()
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.mount("/config", StaticFiles(directory="."), name="config")
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_mime_types(request: Request, call_next):
        response = await call_next(request)
        path = request.url.path
        if path.endswith(".js"):
            response.headers["Content-Type"] = "text/javascript"
        elif path.endswith(".module.js"):
            response.headers["Content-Type"] = "application/javascript"
        return response
    
    register(app, 'app.routes.main')
    register(app, 'app.routes.model')
    register(app, 'app.routes.inference')
    register(app, 'app.routes.websocket')
    return app


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("manage:create_app", host="0.0.0.0", port=8000, reload=True, factory=True)

