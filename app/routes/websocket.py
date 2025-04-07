from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
from datetime import datetime
from app.AI.model import detection_cosmatic, detect_lipstick, detect_lips, detect_hands
from app.routes.service import tts

from dotenv import load_dotenv
from openai import OpenAI

import time
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
condition_met = 0
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
        if check_condition() == 1:
            await haptic_guidance(websocket)
        elif check_condition() == 2:
            await face_haptic_guidance(websocket)


def check_condition():
    global condition_met
    value = condition_met
    print("....check....", value)
    return value


async def receive_and_save_image(websocket, upload_dir="uploads", prefix="received_image"):
    print("[receive_and_save_image] 이미지 수신 대기 중...")
    image_data = await websocket.receive_bytes()
    if image_data:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        sub_dir = os.path.join(upload_dir, prefix)
        os.makedirs(sub_dir, exist_ok=True)
        filename = f"{prefix}_{now}.png"
        path = os.path.join(sub_dir, filename)

        with open(path, "wb") as buffer:
            buffer.write(image_data)

        return path

    print("이미지 데이터 없음")
    return None


# TODO 중간에 손가락이 사라지거나 팔레트가 가려지더라도 계속 진행될 수 있도록 몇 초 정도 기다리는 로직 필요 -> 5초 정도 (구현 완)
async def get_valid_detection(websocket, pallete_index, max_retries=5):
    print("인식 재시도 중...")
    for attempt in range(max_retries):
        await websocket.send_text(json.dumps({"text": "False", "data": ""}))
        image_path = await receive_and_save_image(websocket)
        if not image_path:
            print("이미지 수신 실패")
            return None, None
        _, finger, boxes = detection_cosmatic(image_path)
        if not finger or not boxes:
            print("손가락 & 박스 인식 실패")
            return None, None
        
        print(f"Attempt {attempt + 1}: finger: {finger}, boxes: {boxes}")
        if finger and boxes and pallete_index in boxes:
            return finger, boxes.get(pallete_index)

        print(f"[{attempt + 1}/{max_retries}] 인식 실패 - finger: {finger}, boxes: {boxes}")
        await asyncio.sleep(1)
    
    return None, None


async def get_valid_face_detection(websocket, max_retries=5):
    """
    얼굴 가이던스용 재시도 로직 (립스틱, 입술 좌표 모두 인식될 때까지 반복)
    """
    print("[get_valid_face_detection] 인식 재시도 중...")
    for attempt in range(max_retries):
        await websocket.send_text(json.dumps({"text": "False", "data": ""}))
        image_path = await receive_and_save_image(websocket)

        x, y = detect_lipstick(image_path)
        lip_x, lip_y = detect_lips(image_path)

        if x and y and lip_x and lip_y:
            print(f"재시도 성공: Lipstick({x}, {y}) / Lip({lip_x}, {lip_y})")
            return x, y, lip_x, lip_y
        else:
            print(f"[{attempt + 1}/{max_retries}] 재시도 실패 - lipstick or lips 없음")
            await asyncio.sleep(1)

    print("❌ 최대 재시도 초과")
    return None, None, None, None


async def send_guidance(websocket, direction, audio_text):
    message = json.dumps({"text": "", "data": direction, "audio": tts(audio_text)})
    print(message)
    await websocket.send_text(message)


async def haptic_guidance(websocket: WebSocket):
    global input_query
    query, info = input_query
    pallete_index = select_cosmatic_num(query, info)

    await websocket.send_text(json.dumps({
        "text": "True", "data": "", "audio": tts("햅틱 가이던스를 시작할게요")
    }))
    
    init_input_query()
    update_condition_met(False)

    await websocket.send_text(json.dumps({"text": "False", "data": ""}))
    image_path = await receive_and_save_image(websocket)

    _, finger, boxes = detection_cosmatic(image_path)
    if not finger or not boxes or pallete_index not in boxes:
        # 재시도 로직
        print("초기 인식 실패, 재시도 중...")
        finger, bbox = await get_valid_detection(websocket, pallete_index)
        if not finger or not bbox:
            await websocket.send_text(json.dumps({
                "text": "인식 실패", "data": 0
            }))
            return print("손가락 또는 팔레트를 인식하지 못했습니다.")
    else:
        bbox = boxes.get(pallete_index)

    x1_min, y1_min, x1_max, y1_max = bbox
    x2, y2 = finger

    print(f"Target BBox: {bbox}")
    print(f"Finger Position: {finger}")

    start_time = time.time()
    timeout = 18

    await websocket.send_text(json.dumps({
        "text": "햅틱 가이던스가 시작돼요!", "data": ""
    }))

    while not (x1_min <= x2 <= x1_max and y1_min <= y2 <= y1_max):
        if time.time() - start_time > timeout:
            await websocket.send_text(json.dumps({"text": "", "data": 0}))
            return print("시간 초과")

        await websocket.send_text(json.dumps({"text": "False", "data": ""}))
        image_path = await receive_and_save_image(websocket)
        _, finger, boxes = detection_cosmatic(image_path)

        if not finger or not boxes or pallete_index not in boxes:
            finger, bbox = await get_valid_detection(websocket, pallete_index)
            if not finger or not bbox:
                await websocket.send_text(json.dumps({
                    "text": "인식 실패", "data": 0
                }))
                return print("손가락 또는 팔레트를 인식하지 못했습니다.")
        else:
            bbox = boxes.get(pallete_index)

        x1_min, y1_min, x1_max, y1_max = bbox
        x2, y2 = finger

        if x2 > x1_max:
            await send_guidance(websocket, 3, "왼쪽이에요")
        elif x2 < x1_min:
            await send_guidance(websocket, 4, "오른쪽이에요")

        await asyncio.sleep(0.5)

        if y2 > y1_max:
            await send_guidance(websocket, 2, "위쪽이에요")
        elif y2 < y1_min:
            await send_guidance(websocket, 1, "아래쪽이에요")

        await asyncio.sleep(0.5)

    await websocket.send_text(json.dumps({"text": "", "data": 0}))
    print("목표 지점 도달")


async def face_haptic_guidance(websocket: WebSocket):
    await websocket.send_text(json.dumps({
        "text": "True", "data": "", "audio": tts("얼굴 햅틱 가이던스를 시작할게요")
    }))
    
    init_input_query()
    update_condition_met(False)

    await websocket.send_text(json.dumps({"text": "False", "data": ""}))
    image_path = await receive_and_save_image(websocket)

    x, y = detect_lipstick(image_path)
    lip_x, lip_y = detect_lips(image_path)

    if not all([x, y, lip_x, lip_y]):
            print("초기 인식 실패, 재시도 중...")
            x, y, lip_x, lip_y = await get_valid_face_detection(websocket)
            if not all([x, y, lip_x, lip_y]):
                await websocket.send_text(json.dumps({
                    "text": "인식 실패", "data": 0
                }))
                return print("lipstick 또는 lips를 인식하지 못했습니다.")

    start_time = time.time()
    timeout = 18

    await websocket.send_text(json.dumps({
        "text": "얼굴 햅틱 가이던스가 시작돼요!", "data": ""
    }))

    while not (lip_x - 10 <= x <= lip_x + 10 and lip_y - 10 <= y <= lip_y + 10):
        if time.time() - start_time > timeout:
            await websocket.send_text(json.dumps({"text": "", "data": 0}))
            return print("시간 초과")

        await websocket.send_text(json.dumps({"text": "False", "data": ""}))
        image_path = await receive_and_save_image(websocket)

        x, y = detect_lipstick(image_path)
        lip_x, lip_y = detect_lips(image_path)

        if not all([x, y, lip_x, lip_y]):
            print("초기 인식 실패, 재시도 중...")
            x, y, lip_x, lip_y = await get_valid_face_detection(websocket)
            if not all([x, y, lip_x, lip_y]):
                await websocket.send_text(json.dumps({
                    "text": "인식 실패", "data": 0
                }))
                return print("lipstick 또는 lips를 인식하지 못했습니다.")
                
        if x > lip_x + 10:
            await send_guidance(websocket, 3, "왼쪽이에요")
        elif x < lip_x - 10:
            await send_guidance(websocket, 4, "오른쪽이에요")

        await asyncio.sleep(0.5)

        if y > lip_y + 10:
            await send_guidance(websocket, 2, "위쪽이에요")
        elif y < lip_y - 10:
            await send_guidance(websocket, 1, "아래쪽이에요")

        await asyncio.sleep(0.5)

    await websocket.send_text(json.dumps({"text": "", "data": 0}))
    print("목표 지점 도달")


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
                f"Note that '3_12' refers to the second color in the first row, '3_22' refers to the second color in the second row, and '3_31' refers to the first color in the third row.\n\n"
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
