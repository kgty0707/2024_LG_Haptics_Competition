from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect, Request
import time
import random
import asyncio

app = FastAPI()
router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/client")
async def client(request: Request):
    return templates.TemplateResponse("websocket.html", {"request": request})

connected_clients = []

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        await monitor_conditions(websocket)
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

async def monitor_conditions(websocket: WebSocket):
    while True:
        await asyncio.sleep(5)  # Check the condition every 5 seconds
        if check_condition():
            await haptic_guidance(websocket)

def check_condition():
    value = random.choice([True, False])
    print("..................check....", value)
    return value

async def haptic_guidance(websocket: WebSocket):
    """
    TODO: Timeout 되면 진동 울리는 로직 추가
    TODO: Check value 전역 변수 설정, True 될 때 질문하기 버튼 비활성화
    """
    await websocket.send_text("Welcome client")
    
    x1_min, y1_min, x1_max, y1_max = get_model1_bbox()
    x2, y2 = get_model2_coords()

    print(f"Initial model1_bbox: {(x1_min, y1_min, x1_max, y1_max)}")
    print(f"Initial model2_coords: {(x2, y2)}")

    start_time = time.time()
    timeout = 60  # 1분 타임아웃

    while not (x1_min <= x2 <= x1_max and y1_min <= y1_max):
        if time.time() - start_time > timeout:
            print("Time out reached")
            return

        x2, y2 = get_model2_coords()

        if x2 > x1_max:
            print("오른쪽 (right)")
            await websocket.send_text("오른쪽 (right)")
        elif x2 < x1_min:
            print("왼쪽 (left)")
            await websocket.send_text("왼쪽 (left)")
        if y2 > y1_max:
            print("아래 (down)")
            await websocket.send_text("아래 (down)")
        elif y2 < y1_min:
            print("위 (up)")
            await websocket.send_text("위 (up)")

        await asyncio.sleep(1)

    print("범위 내에 있음 (inside)")
    await websocket.send_text("범위 내에 있음 (inside)")

def get_model1_bbox():
    '''
    모델1의 경계 상자를 반환하는 함수
    이 함수는 임시로 고정된 값을 반환하지만 실제로는 모델의 추론 결과를 반환해야 함
    '''
    return (0, 0, 5, 5)

def get_model2_coords():
    '''
    모델2의 좌표값을 추론해서 반환하는 함수
    이 함수는 임시로 랜덤값을 반환하지만 실제로는 모델의 추론 결과를 반환해야 함
    '''
    return (random.randint(0, 10), random.randint(0, 10))