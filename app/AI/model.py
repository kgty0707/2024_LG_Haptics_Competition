import torch
import requests
import mediapipe as mp
import numpy as np
import os

from dotenv import load_dotenv
from ultralytics import YOLO
from PIL import ImageDraw, Image
from app.AI.mideapipe_utill import extract_lips_data, extract_hand_data
from app.AI.util import save_result_image, draw_shadow_bounding_box, draw_lips_data, draw_hand_data, draw_lipstick_data

# MediaPipe FaceMesh 초기화
mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands

device = torch.device('cpu')

model = YOLO('./app/AI/best.pt')
model.to(device)

load_dotenv()

ROBOFLOW_API_KEY = os.getenv('ROBOFLOW_API_KEY')
PROJECT = os.getenv('PROJECT')
VERSION = os.getenv('VERSION')
ENDPOINT = f"https://detect.roboflow.com/{PROJECT}/{VERSION}?api_key={ROBOFLOW_API_KEY}"

print("ENDPOINT", ENDPOINT)
CONFIDENCE = 0.5
OVERLAP = 0.2

def detection_cosmatic(image_path):
    '''
    Input: 이미지 경로
    Output: 화장품의 종류, 손가락 위치, 각 섀도우의 바운딩 박스
    '''
    image = Image.open(image_path)
    results = model.predict(image)
    pallete = None
    finger = None
    shadow_boxes = {}

    class_names = [
        "2_11", "2_12", "2_21", "2_22", "2_23", "2_31", "2_32",
        "3_11", "3_12", "3_21", "3_22", "finger", "pallete2", "pallete3"
    ]
    
    boxes = results[0].boxes
    draw = ImageDraw.Draw(image) # pil.ImageDraw 객체 생성

    for box in boxes:
        bbox = box.xyxy[0]
        class_id = int(box.cls[0])
        x1, y1, x2, y2 = [int(val.item()) for val in bbox]
        scaled_bbox = [x1, y1, x2, y2]
        class_name = class_names[class_id]

        if class_id == 12 or class_id == 13:  # 팔레트
            if pallete is None:
                pallete = class_name
            draw_shadow_bounding_box(draw, scaled_bbox, label=class_name, color="red")

        elif class_id == 11:  # 손가락
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            finger = [center_x, center_y]

            draw_shadow_bounding_box(draw, scaled_bbox, label="finger", color="blue", corner_points=True)

            # 중심점(손가락 끝 위치) 표시
            r = 4
            draw.ellipse((center_x - r, center_y - r, center_x + r, center_y + r), fill="red")
            draw.text((center_x + 5, center_y), "finger", fill="red")

        else:  # 각 섀도우 박스
            shadow_boxes[class_name] = scaled_bbox
            draw_shadow_bounding_box(draw, scaled_bbox, label=class_name, color="green")

    save_result_image(image, prefix="cosmatic")

    print(f"모델 출력 팔레트: {pallete}, 손가락: {finger}, 바운딩 박스: {shadow_boxes}")
    return pallete, finger, shadow_boxes


def detect_lipstick(face_image_path):
    response = requests.post(
        ENDPOINT,
        files={"file": open(face_image_path, "rb")},
        data={"format": "pandas", "confidence": CONFIDENCE, "overlap": OVERLAP}
    )

    response.raise_for_status()

    face_image = Image.open(face_image_path).convert("RGB")
    face_image_copy = face_image.copy()

    draw = ImageDraw.Draw(face_image_copy)

    if response.status_code == 200:
        prediction = response.json().get("predictions", [])
        print("립스틱 예측 결과:", prediction)

        prediction = prediction[0] if prediction else None

        if prediction:
            x_center = prediction["x"]
            y_center = prediction["y"]
            width = prediction["width"]
            height = prediction["height"]
            label = prediction["class"]
            confidence = prediction["confidence"]

            # 바운딩 박스 좌표
            x1 = int(x_center - width / 2)
            y1 = int(y_center - height / 2)
            x2 = int(x_center + width / 2)
            y2 = int(y_center + height / 2)

            top_middle_x = (x1 + x2) // 2
            top_middle_y = y1

            draw_data = {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "top_middle_x": top_middle_x,
                "top_middle_y": top_middle_y,
            }
            draw_lipstick_data(draw, draw_data)
            save_result_image(face_image_copy, prefix="lipstick_data")
            return top_middle_x, top_middle_y
        else:
            print("No predictions found.")
    return []


def detect_lips(face_image):
    face_image = Image.open(face_image).convert("RGB")

    lips_data = None
    width, height = face_image.size

    face_image_np = np.array(face_image)  # for MediaPipe

    face_image_copy = face_image.copy()
    draw = ImageDraw.Draw(face_image_copy)

    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5
    ) as face_mesh:
        face_results = face_mesh.process(face_image_np)

        if face_results.multi_face_landmarks:
            face_landmarks = face_results.multi_face_landmarks[0]
            lips_data = extract_lips_data(face_landmarks, width, height)

            if lips_data:
                draw_lips_data(draw, lips_data)
                save_result_image(face_image_copy, prefix="lips_data")
                if lips_data["outer_lips_points"][0]["x"] and lips_data["outer_lips_points"][0]["y"]:
                    return lips_data["outer_lips_points"][0]["x"], lips_data["outer_lips_points"][0]["y"]
        else:
            print("얼굴이 감지되지 않았습니다.")
            return []

    
    # print("61 입술 데이터:", lips_data["outer_lips_points"][0]["x"])
    # print("61 입술 데이터:", lips_data["outer_lips_points"][0]["y"])

    return []


def detect_hands(image_path):
    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    image_np = np.array(image)

    hands_data = []

    with mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=2,
        min_detection_confidence=0.5) as hands:

        hand_results = hands.process(image_np)

        if hand_results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(hand_results.multi_hand_landmarks):
                handedness = hand_results.multi_handedness[idx]
                hand_data = extract_hand_data(hand_landmarks, handedness, width, height)
                hands_data.append(hand_data)
        else:
            print("손이 감지되지 않았습니다.")

    image_copy = image.copy()
    draw = ImageDraw.Draw(image_copy)
    draw_hand_data(draw, hands_data)

    save_result_image(image_copy, prefix="hands_data")

    return hands_data

# print(detect_lips("./test/images2.jpg"))