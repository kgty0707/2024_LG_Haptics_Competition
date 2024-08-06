import os

from fastapi import APIRouter, Request
from pydantic import BaseModel

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from app.routes.model import generate_response
from app.AI.model import detection_cosmatic, detection_hand


router = APIRouter()
templates = Jinja2Templates(directory="templates")

class Query(BaseModel):
    query: str

@router.get("/", response_class=HTMLResponse)
def main(request: Request):
    return templates.TemplateResponse(
        name="main.html",
        request=request
    )

@router.get("/makeup")
def test(request: Request):
    return templates.TemplateResponse(
        name="makeup.html",
        request=request
    )