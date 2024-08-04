import os
from openai import OpenAI
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

client = OpenAI(api_key=api_key)

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
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        
        user_text = transcription['text']
        
        # GPT-3.5에게 텍스트 전달 및 응답 받기
        System_Role="당신은 고도로 숙련된 메이크업 아티스트로 친절하게 색깔을 추천해 주고 소개를 해줍니다"
        Prompt="여름 쿨톤에 어울리는 셰이더의 색깔을 알려줘"
        gpt_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": System_Role},
                {"role": "user", "content": Prompt}
            ],
            stream=True,
        )
        gpt_response=gpt_response.choices[0].delta.content
        

        # OpenAI TTS API를 사용하여 텍스트를 음성으로 변환
        speech_response = client.audio.speech.create(
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
