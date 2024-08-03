import os
import openai
from pydantic import BaseModel
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
api_key = os.getenv('GPT_API_KEY')

router = APIRouter()
templates = Jinja2Templates(directory="templates")

openai.api_key = api_key

class TranscriptionResult(BaseModel):
    text: str
    gpt_text: str
    audio_url: str

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
        
        user_text = transcription['text']
        
        # GPT-3.5에게 텍스트 전달 및 응답 받기
        response = openai.completions.create(
            engine="text-davinci-003",
            prompt=user_text,
            max_tokens=150
        )
        
        gpt_response = response.choices[0].text.strip()

        # OpenAI TTS API를 사용하여 텍스트를 음성으로 변환
        speech_response = openai.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=gpt_response
        )

        speech_file_path = Path("static/response.mp3")
        with open(speech_file_path, "wb") as f:
            f.write(speech_response['audio'])

        return {"text": user_text, "gpt_text": gpt_response, "audio_url": str(speech_file_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
