import urllib.parse

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

# 사진 추출하는 함수 구현
def extract_frame():
    ...

@router.post("/send_query", response_class=HTMLResponse)
def send_query(request: Request, data: Query):

    image = extract_frame()
    model_result = detection_cosmatic(image)

    answer = generate_response(model_result, data.query)
    print(f"답변: {answer}")

    json_data = {
        'answer': answer,
    }

    return JSONResponse(content=json_data)

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