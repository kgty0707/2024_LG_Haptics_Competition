import urllib.parse

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
import openai
from pydantic import BaseModel

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from app.routes.model import generate_response
from app.AI.model import detection_cosmatic, detection_hand

router = APIRouter()
templates = Jinja2Templates(directory="templates")

class Query(BaseModel):
    model_type: str

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

class TranscriptionResult(BaseModel):
    text: str

@router.post("/transcribe", response_model=TranscriptionResult)
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        # 오디오 파일을 읽기
        audio_data = await file.read()
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_data)

        # OpenAI Whisper API를 사용하여 음성을 텍스트로 변환
        transcription = openai.Audio.transcribe(
            model="whisper-1",
            file=open("temp_audio.wav", "rb")
        )
        return {"text": transcription['text']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))