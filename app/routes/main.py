import urllib.parse

from fastapi import APIRouter, Request
from pydantic import BaseModel

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

router = APIRouter()
templates = Jinja2Templates(directory="templates")

class Query(BaseModel):
    model_type: str
    query: str


# 사진 추출하는 함수 구현
def extract_frame():
    ...

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

@router.get("/main")
def hello(request: Request):
    return templates.TemplateResponse(
        name="second.html",
        request=request
    )

@router.get("/main/second")
def test(request: Request):
    return templates.TemplateResponse(
        name="second.html",
        request=request
    )

@router.get("/main/test")
def test(request: Request):
    return templates.TemplateResponse(
        name="test.html",
        request=request
    )

@router.get("/arduino")
async def test(request: Request):
    return templates.TemplateResponse(
        name="arduino.html",
        context={"request": request}
    )