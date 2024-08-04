import os
from openai import OpenAI
from pydantic import BaseModel
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
my_api_key = os.getenv('GPT_API_KEY')
if not my_api_key:
    raise ValueError("API key is missing. Please set GPT_API_KEY in the environment variables.")

router = APIRouter()

client = OpenAI(api_key=my_api_key, base_url="https://api.openai.com/v1",)

class TranscriptionResult(BaseModel):
    text: str

class GPTResponseResult(BaseModel):
    gpt_text: str

class AudioResult(BaseModel):
    audio_url: str


@router.post("/transcribe_audio", response_model=TranscriptionResult)
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
                response_format="json"
            )
        
        return {"text": transcription['text']}
    except Exception as e:
        raise HTTPException(status_code=501, detail=str(e))
        

@router.post("/generate_gpt_response", response_model=GPTResponseResult)
async def generate_gpt_response(user_text: str):
    try:
        # GPT-3.5에게 텍스트 전달 및 응답 받기
        system_role="당신은 고도로 숙련된 메이크업 아티스트로 친절하게 색깔을 추천해 주고 소개를 해줍니다"
        prompt = f"{user_text}"
        gpt_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt}
            ]
        )
        gpt_text = gpt_response.choices[0].message.content
        return {"gpt_text": gpt_text}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
        
@router.post("/generate_audio", response_model=AudioResult)
async def generate_audio(gpt_text: str):
    try:
        # OpenAI TTS API를 사용하여 텍스트를 음성으로 변환
        speech_response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=gpt_text
        )
        speech_file_path = Path("static/response.mp3")
        with open(speech_file_path, "wb") as f:
            f.write(speech_response['audio'])
        return {"audio_url": str(speech_file_path)}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
    