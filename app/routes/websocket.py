from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
from datetime import datetime

import time
import random
import asyncio
import json
import os

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/client")
async def client(request: Request):
    return templates.TemplateResponse("websocket.html", {"request": request})


connected_clients = []
condition_met = False

def update_condition_met(value: bool):
    global condition_met
    condition_met = value


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print("connect websocket")
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        await monitor_conditions(websocket)
    except WebSocketDisconnect:
        connected_clients.remove(websocket)


async def monitor_conditions(websocket: WebSocket):
    while True:
        await asyncio.sleep(5)
        if check_condition():
            await haptic_guidance(websocket)


def check_condition():
    global condition_met
    value = condition_met
    print("....check....", value)
    return value
    

async def haptic_guidance(websocket: WebSocket):
    """
    TODO: Timeout 되면 진동 울리는 로직 추가(완)
    TODO: Check value 전역 변수 설정(완), True 될 때 질문하기 버튼 비활성화
    """
    upload_dir = "uploads"

    message = json.dumps({"text": "True", "data": ""})
    await websocket.send_text(message)

    update_condition_met(False)

    # TODO: User가 (말로) 선택한 바운딩 박스 좌표만 가져오는 알고리즘 필요(완 -> model.py에 존재 연결 아직 안함)
    message = json.dumps({"text": "False", "data": ""})
    await websocket.send_text(message)
    image_data = await websocket.receive_bytes()

    if image_data:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_image_filename = f"received_image_{now}.png"
        image_path = os.path.join(upload_dir, sanitized_image_filename)
        with open(image_path, "wb") as buffer:
            buffer.write(image_data)
        print(f"Image saved to {image_path}")
    
    x1_min, y1_min, x1_max, y1_max = get_model1_bbox(image_path)
    x2, y2 = get_model2_coords(image_path)

    print(f"Initial model1_bbox: {(x1_min, y1_min, x1_max, y1_max)}")
    print(f"Initial model2_coords: {(x2, y2)}")

    start_time = time.time()
    timeout = 10  # 10초 타임아웃

    message = json.dumps({"text": "햅틱 가이던스가 시작돼요!", "data": ""})
    await websocket.send_text(message)

    while not (x1_min <= x2 <= x1_max and y1_min <= y1_max):

        print(f"Initial model1_bbox: {(x1_min, y1_min, x1_max, y1_max)}")
        print(f"Initial model2_coords: {(x2, y2)}")
    
        if time.time() - start_time > timeout:
            print("Time out reached")
            message = json.dumps({"text": "", "data": 0})
            await websocket.send_text(message)
            return

        # TODO: Haptic Guidance 도중 팔레트에 위치가 변한다고 가정?
        message = json.dumps({"text": "False", "data": ""})
        await websocket.send_text(message)
        image_data = await websocket.receive_bytes()

        if image_data:
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            sanitized_image_filename = f"received_image_{now}.png"
            image_path = os.path.join(upload_dir, sanitized_image_filename)
            with open(image_path, "wb") as buffer:
                buffer.write(image_data)
            print(f"Image saved to {image_path}")

        x1_min, y1_min, x1_max, y1_max = get_model1_bbox(image_path)
        x2, y2 = get_model2_coords(image_path)

        if x2 > x1_max: # 오른쪽
            message = json.dumps({"text": "", "data": 4})
            print(message)
            await websocket.send_text(message)
        elif x2 < x1_min: # 왼쪽
            message = json.dumps({"text": "", "data": 3})
            print(message)
            await websocket.send_text(message)

        await asyncio.sleep(3)

        if y2 > y1_max: # 아래
            message = json.dumps({"text": "", "data": 2})
            print(message)
            await websocket.send_text(message)
        elif y2 < y1_min: # 위
            message = json.dumps({"text": "", "data": 1})
            print(message)
            await websocket.send_text(message)

        await asyncio.sleep(1)

    message = json.dumps({"text": "", "data": 0})
    print(message)
    await websocket.send_text(message)


# TODO: User가 (말로) 선택한 바운딩 박스 좌표만 가져오는 알고리즘 필요
# TODO: Inference.py로 옮기기
def get_model1_bbox(image_path):
    image_path = 0
    '''
    모델1의 경계 상자를 반환하는 함수
    이 함수는 임시로 고정된 값을 반환하지만 실제로는 모델의 추론 결과를 반환해야 함
    '''
    return (4, 4, 5, 5)

def get_model2_coords(image_path):
    image_path = 0
    '''
    모델2의 좌표값을 추론해서 반환하는 함수
    이 함수는 임시로 랜덤값을 반환하지만 실제로는 모델의 추론 결과를 반환해야 함
    '''
    return (random.randint(0, 1), random.randint(0, 1))