import os
import openai
from pydantic import BaseModel
from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GPT_API_KEY')

router = APIRouter()
templates = Jinja2Templates(directory="templates")

openai.api_key = api_key

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
        with open("temp_audio.wav", "rb") as audio_file:
            transcription = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        
        return {"text": transcription['text']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))