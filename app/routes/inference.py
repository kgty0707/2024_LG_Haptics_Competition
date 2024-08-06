from fastapi import File, UploadFile, APIRouter
from app.routes.model import stt, tts, generate_response
from app.AI.model import get_hand_coords, get_pallete_index

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
    user_text = stt(audio_path)

    # 모델 결과를 사용하여 응답 생성
    # TODO: 이미지 인식 결과로 얻은 팔레트 종류 필요
    model_index = get_pallete_index(image_path)

    print(user_text)

    result = generate_response(model_index, user_text)
    print(f"모델 출력: {result}")

    audio = tts(result)

    return {"message": "Uploaded successfully", "result": result, "audio_url": audio}
