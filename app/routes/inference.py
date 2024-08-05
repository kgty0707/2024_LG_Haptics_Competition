from fastapi import File, UploadFile, APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from app.routes.model import stt, tts, generate_response
import base64
from io import BytesIO
from PIL import Image

import os

router = APIRouter()

def sanitize_filename(filename: str) -> str:
    return filename.replace(":", "_").replace(" ", "_")

@router.post("/uploads")
async def upload(audioFile: UploadFile = File(...), imageFile: UploadFile = File(...)):

    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    sanitized_audio_filename = sanitize_filename(audioFile.filename)
    audio_path = f"uploads/{sanitized_audio_filename}"
    with open(audio_path, "wb") as buffer:
        buffer.write(audioFile.file.read())

    sanitized_image_filename = sanitize_filename(imageFile.filename)
    image_path = f"uploads/{sanitized_image_filename}"
    with open(image_path, "wb") as buffer:
        buffer.write(imageFile.file.read())

    # 음성 인식 수행
    text = stt(audio_path)

    # 모델 결과를 사용하여 응답 생성
    # TODO: 이미지 인식 결과로 얻은 팔레트 종류 필요
    model_result = {'palette_num': "Palette1"}
    print(text)
    result = generate_response(model_result, text)
    print(f"모델 출력: {result}")

    audio = tts(result)

    return {"message": "Uploaded successfully", "result": result, "audio_url": audio}
