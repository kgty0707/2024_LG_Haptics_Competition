# 아름이 모델 추론 결과 반환
from ultralytics import YOLO
from mediapipe import mp
import cv2

# 모델 로드 
model = YOLO('./app/AI/best.pt')

def detection_cosmatic(image):
    '''
    Input: 이미지,
    Output: 화장품의 종류 (1, 2), 각 새도우의 바운딩 박스, 화장품의 앞 뒤 구별(?)
    '''
    ...
     # 이미지 추론
    results = model.predict(image)

    
    # 클래스와 바운딩 박스 저장 리스트 초기화
    pallete = None
    shadow_boxes = []

    # 결과에서 boxes 객체 추출
    boxes = results[0].boxes

    for box in boxes:
        bbox = box.xyxy[0]  # 바운딩 박스 좌표 (x1, y1, x2, y2)
        class_id = int(box.cls[0])  # 클래스 ID
        
        # 좌표를 정수형으로 변환하여 사용
        x1, y1, x2, y2 = [int(val.item()) for val in bbox]
        scaled_bbox = [x1, y1, x2, y2]
        
        # 클래스 ID에 따른 처리
        if class_id == 0:
            pallete = "pallete2"
        elif class_id == 1: 
            pallete = "pallete1"
        elif class_id == 2: 
            shadow_boxes.append(scaled_bbox)
    
    return pallete, shadow_boxes


def detection_hand(image):
    '''
    input : 이미지
    output : 검지손가락의 좌표
    '''
    
    mp_hands = mp.solutions.hands

    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    if image is not None:

        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        result = hands.process(img_rgb)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                h, w, _ = image.shape
                cx, cy = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
        else:
            print('손이 인식되지 않았습니다')
            
    hands.close()
    
    return cx,cy