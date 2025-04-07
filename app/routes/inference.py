from fastapi import File, UploadFile, APIRouter
from app.routes.model import generate_response
from app.routes.service import stt, tts

import os
import aiofiles

router = APIRouter()

def sanitize_filename(filename: str) -> str:
    return filename.replace(":", "_").replace(" ", "_")

@router.post("/uploads")
async def upload(audioFile: UploadFile = File(...), imageFile: UploadFile = File(...)):
    base_dir = "uploads"
    audio_dir = os.path.join(base_dir, "audio")
    image_dir = os.path.join(base_dir, "image")

    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)

    sanitized_audio_filename = sanitize_filename(audioFile.filename)
    sanitized_image_filename = sanitize_filename(imageFile.filename)

    audio_path = os.path.join(audio_dir, sanitized_audio_filename)
    image_path = os.path.join(image_dir, sanitized_image_filename)

    # 파일 저장 (await 사용)
    async with aiofiles.open(audio_path, "wb") as buffer:
        await buffer.write(await audioFile.read())

    async with aiofiles.open(image_path, "wb") as buffer:
        await buffer.write(await imageFile.read())

    user_text = stt(audio_path)
    
    print(f"🗣️ 사용자가 말한 텍스트: {user_text}")


    result = generate_response(image_path, user_text)

    audio = tts(result)

    return {
        "message": "Uploaded successfully",
        "result": result,
        "audio_url": audio
    }