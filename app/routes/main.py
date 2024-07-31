import urllib.parse

from fastapi import APIRouter, Request
from pydantic import BaseModel

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
# from app.routes.model import generate_answer


router = APIRouter()
templates = Jinja2Templates(directory="templates")

class Query(BaseModel):
    model_type: str
    query: str


@router.get("/main")
def hello(request: Request):
    return templates.TemplateResponse(
        name="back_test.html",
        request=request
    )

@router.get("/", response_class=HTMLResponse)
def main(request: Request):
    return templates.TemplateResponse(
        name="main.html",
        request=request
    )
