# 아름이 모델 추론 결과 반환
from ultralytics import YOLO
from PIL import Image
# from mediapipe import mp
import cv2
import random

# 모델 로드 
model = YOLO('./app/AI/best.pt')

def detection_cosmatic(image):
    '''
    Input: 이미지 경로
    Output: 화장품의 종류, 각 새도우의 바운딩 박스
    '''
    image = "./uploads/test.png"
    image = Image.open(image)
    results = model.predict(image)
    print("\n\n\n\n모델 출력: ", results)
    pallete = None
    shadow_boxes = {}

    class_names = ["2_11", "2_12", "2_21","2_22","2_23", "2_31", "2_32","3_11", "3_12", "3_21", "3_22","pallete2", "pallete3"]

    # 결과에서 boxes 객체 추출
    boxes = results[0].boxes

    for box in boxes:
        bbox = box.xyxy[0]  # 바운딩 박스 좌표 (x1, y1, x2, y2)
        class_id = int(box.cls[0]) 
     
        x1, y1, x2, y2 = [int(val.item()) for val in bbox]
        scaled_bbox = [x1, y1, x2, y2]
        
        class_name = class_names[class_id]

        if class_id == 11 or class_id == 12 :
            pallete = class_name
        else:
            shadow_boxes[class_name] = scaled_bbox
    
    return pallete, shadow_boxes


def detection_hand(image):
    '''
    input : 이미지 경로
    output : 검지손가락의 좌표
    '''

    image = cv2.imread(image)

    mp_hands = mp.solutions.hands

    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    cx,cy = None, None 

    if image is not None:

        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        result = hands.process(img_rgb)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                h, w, _ = image.shape
                cx, cy = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
                cy += 40
        else:
            print('손이 인식되지 않았습니다')
            
    hands.close()
    
    return cx,cy