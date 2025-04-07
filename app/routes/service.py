import os

from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GPT_API_KEY')

if not api_key:
    raise ValueError("API key is missing. Please set GPT_API_KEY in the environment variables.")

client = OpenAI(api_key=api_key)

def stt(audio_path):
    audio_file= open(audio_path, "rb")
    transcription = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file
    )
    audio_file.close()
    print("transcription", transcription.text)
    return transcription.text


def tts(text_path):
    response = client.audio.speech.create(
        model="gpt-4o-mini-tts", # 모델 버전 업데이트 "tts-1" -> "gpt-4o-mini-tts"
        voice="fable",
        input=text_path,
        # speed=1.2
    )

    now = datetime.now()
    file_name = now.strftime("text_%Y%m%d_%H%M%S.wav")
    file_path = f"./uploads/{file_name}"
    
    response.stream_to_file(file_path)
    return file_path
