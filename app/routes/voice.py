import os
import openai
import logging
from pydantic import BaseModel
from fastapi import APIRouter, File, HTTPException, UploadFile, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='app.log', filemode='a')
logger = logging.getLogger(__name__)

load_dotenv()
api_key = os.getenv('GPT_API_KEY')
if not api_key:
    raise ValueError("API key is missing. Please set GPT_API_KEY in the environment variables.")

router = APIRouter()

client = openai.OpenAI(api_key=api_key)


@router.post("/transcribe_audio")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        logger.debug("Received file for transcription.")
        # 오디오 파일을 읽기
        audio_data = await file.read()
        file_path = "temp_audio.wav"
        logger.debug(f"Saving audio to {file_path}")

        with open(file_path, "wb") as f:
            f.write(audio_data)

        logger.debug(f"Audio saved to {file_path}")

        # OpenAI Whisper API를 사용하여 음성을 텍스트로 변환
        with open(file_path, "rb") as audio_file:
            logger.debug(f"Audio file {file_path} opened successfully.")
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
        
        logger.debug(f"Transcription result: {transcription.text}")
        return {"text": transcription.text}
    except Exception as e:
        logger.error(f"Error in transcribe_audio: {str(e)}")
        raise HTTPException(status_code=501, detail=str(e))
        

@router.post("/generate_gpt_response")
async def generate_gpt_response(user_text: str):
    try:
        logger.debug("Received user text for GPT response.")
        logger.debug(f"User text: {user_text}")
        
        # GPT-3.5에게 텍스트 전달 및 응답 받기
        system_role = "당신은 고도로 숙련된 메이크업 아티스트로 친절하게 색깔을 추천해 주고 소개를 해줍니다"
        prompt = f"{user_text}"
        logger.debug("Sending request to GPT-3.5.")
        gpt_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt}
            ]
        )
        gpt_text = gpt_response.choices[0].message.content
        logger.debug(f"GPT response: {gpt_text}")
        return {"gpt_text": gpt_text}
    except Exception as e:
        logger.error(f"Error in generate_gpt_response: {str(e)}")
        raise HTTPException(status_code=502, detail=str(e))
        
@router.post("/generate_audio")
async def generate_audio(gpt_text: str):
    try:
        logger.debug("Received GPT text for TTS conversion.")
        logger.debug(f"GPT text: {gpt_text}")
        
        # OpenAI TTS API를 사용하여 텍스트를 음성으로 변환
        logger.debug("Sending request to TTS API.")
        speech_response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=gpt_text
        )
        speech_file_path = Path("static/response.mp3")
        logger.debug(f"Saving speech audio to {speech_file_path}")

        with open(speech_file_path, "wb") as f:
            f.write(speech_response['audio'])

        logger.debug(f"Speech audio saved to {speech_file_path}")
        return {"audio_url": str(speech_file_path)}
    except Exception as e:
        logger.error(f"Error in generate_audio: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))
