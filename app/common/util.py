import importlib
from fastapi import FastAPI

def register(app: FastAPI, module_path: str):
    module = importlib.import_module(module_path)
    if hasattr(module, "router"):
        app.include_router(module.router)