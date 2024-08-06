from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
from datetime import datetime
from app.AI.model import detection_cosmatic, detection_hand

from dotenv import load_dotenv
from openai import OpenAI

import time
import random
import asyncio
import json
import os

load_dotenv()

api_key = os.getenv('GPT_API_KEY')

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/client")
async def client(request: Request):
    return templates.TemplateResponse("websocket.html", {"request": request})


connected_clients = []
condition_met = False
input_query = []

def update_condition_met(value: bool):
    global condition_met
    condition_met = value


def update_input_query(query: str, info: str):
    global input_query
    input_query = [query, info]


def init_input_query():
    global input_query
    input_query = []


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
    global input_query
    query, info = input_query

    pallete_index = select_cosmatic_num(query, info)
    
    upload_dir = "uploads"

    message = json.dumps({"text": "True", "data": ""})
    await websocket.send_text(message)

    init_input_query()
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

    _, boxes = detection_cosmatic(image_path)
    boxes = sorted(boxes.items())

    x2, y2 = detection_hand(image_path)

    if x2 is None or y2 is None or boxes is None:
        return print("햅틱 가이던스 도중 인식하지 못한 좌표값이 있어요")

    x1_min, y1_min, x1_max, y1_max = boxes[pallete_index][1]


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

        _, boxes = detection_cosmatic(image_path)
        boxes = sorted(boxes.items())
        x2, y2 = detection_hand(image_path)

        if x2 is None or y2 is None or boxes is None:
            return print("햅틱 가이던스 도중 인식하지 못한 좌표값이 있어요")

        x1_min, y1_min, x1_max, y1_max = boxes[pallete_index][1]

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


client = OpenAI(api_key=api_key)


# TODO: 이 아래 코드는 숫자만 추출하는 코드, 사용자가 원하는 색을 말했을 때 해당하는 색깔을 찾음(완)

def extract_color_number(text):
    start_index = text.find('Color number: ') + len('Color number: ')
    end_index = text.find('\n', start_index)
    if end_index == -1:
        end_index = len(text)
    return text[start_index:end_index].strip()


def select_cosmatic_num(query, info):
    messages = [
        {
            "role": "system",
            "content": "You are an assistant."
        },
        {
            "role": "user",
            "content": (
                f"Please identify the color names and their corresponding numbers from the palette."
                f"Take your time. First, write down the color name, then write down its corresponding number."
                f"Use the provided info to find the color names and numbers."
                f"If you can't find the number for a color in the provided info, output 0.\n\n"
                f"The user might ask for the color in different ways, such as:"
                f"'Find the last color in the first row', 'I want the last color in the first row', 'The first color in the last row looks delicious'."
                f"Please interpret these queries correctly and provide the corresponding color name and number.\n\n"
                f"If the question is '살구색 찾고 싶은데 햅틱 가이던스 실행시켜줘', identify the color number for 살구색 and include a message saying: '살구색에 해당하는 색상 번호 하나를 적어주세요.'\n\n"
                f"info: {info}\n"
                f"question: {query}\n"
                f"answer:\n"
                f"Color name: [name]\n"
                f"Color number: [number]\n"
                f"Ensure that the color number matches the color name from the info."
            )
        }
    ]
    print('prompt: ', messages)

    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=messages,
        temperature=0
    )
    response_message = response.choices[0].message.content
    color_number = extract_color_number(response_message)
    print('\n\n\n\n\n\n\n최종 색상:', color_number)
    return color_number
