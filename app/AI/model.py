# 아름이 모델 추론 결과 반환
from ultralytics import YOLO
from PIL import Image

import torch

device = torch.device('cpu')

model = YOLO('./app/AI/best.pt')
model.to(device)

def detection_cosmatic(image):
    '''
    Input: 이미지 경로
    Output: 화장품의 종류, 손가락 위치, 각 새도우의 바운딩 박스
    '''
    
    image = Image.open(image)
    results = model.predict(image)
    pallete = None
    finger = None
    shadow_boxes = {}

    class_names = ["2_11", "2_12", "2_21", "2_22", "2_23", "2_31", "2_32", "3_11", "3_12", "3_21", "3_22", "finger", "pallete2", "pallete3"]

    # 결과에서 boxes 객체 추출
    boxes = results[0].boxes

    for box in boxes:
        bbox = box.xyxy[0]  # 바운딩 박스 좌표 (x1, y1, x2, y2)
        class_id = int(box.cls[0]) 
     
        x1, y1, x2, y2 = [int(val.item()) for val in bbox]
        scaled_bbox = [x1, y1, x2, y2]
        
        class_name = class_names[class_id]

        if class_id == 12 or class_id == 13 :
            if pallete is None:
                pallete = class_name
            
        elif class_id == 11 : # 손가락 좌표
            center_x = (x1 + x2) // 2
            center_y = y2
            finger = [center_x, center_y]
        else:
            shadow_boxes[class_name] = scaled_bbox
    print(f"모델 출력 팔레트: {pallete}, 손가락: {finger}, 바운딩 박스: {shadow_boxes}")
    return pallete, finger, shadow_boxes