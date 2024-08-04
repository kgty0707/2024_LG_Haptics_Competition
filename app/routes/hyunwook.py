from fastapi import File, UploadFile, APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from app.routes.model import stt, generate_response

import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def sanitize_filename(filename: str) -> str:
    return filename.replace(":", "_").replace(" ", "_")


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    sanitized_filename = sanitize_filename(f"audio_{file.filename}")

    file_path = os.path.join(upload_dir, sanitized_filename)
    
    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = stt(file_path)

    # TODO: model_result 실제 추론 결과로 변경
    model_result = {'palette_num': "Palette1"}
    print(text)

    result = generate_response(model_result, text)
    print(f"모델 출력: {result}")
    
    return JSONResponse(content={"message": "Uploaded successfully", "text": text})


@router.get("/hyunwook")
async def client(request: Request):
    return templates.TemplateResponse("hyunwook.html", {"request": request})
