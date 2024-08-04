from fastapi import FastAPI, File, UploadFile, APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
import shutil

app = FastAPI()
router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"uploaded_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return JSONResponse(content={"filename": file.filename}, status_code=200)

@router.get("/hyunwook")
async def client(request: Request):
    return templates.TemplateResponse("hyunwook.html", {"request": request})
