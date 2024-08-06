# 아름이 모델 추론 결과 반환
from ultralytics import YOLO
import random

# 모델 로드 (.pt 파일 있는 경로로 나중에 수정 )
model = YOLO('./app/AI/best.pt')
hand_model = ""

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
            pallete = "pallete1"
        elif class_id == 1: 
            pallete = "pallete2"
        elif class_id == 2: 
            shadow_boxes.append(scaled_bbox)
    
    return pallete, shadow_boxes


def detection_hand(image):
    '''
    Input: 이미지,
    Ouput: 손가락의 바운딩 박스
    '''
    ...
    return


# TODO: User가 (말로) 선택한 바운딩 박스 좌표만 가져오는 알고리즘 필요
# TODO: Inference.py로 옮기기


def get_model_result(image_path):
    image_path = 0
    # results = model.predict(image_path)

    return "results"


def get_pallete_index(image_path):
    image_path = 0
    # results = get_model_result(image_path)

    # result =  {'palette_num': results['pallete']}

    return {'palette_num': "Palette1"}


def get_pallete_bbox(image_path):
    image_path = 0

    return (4, 4, 5, 5)


def get_hand_coords(image_path):
    image_path = 0
    # results = hand_model.predict(image_path)

    # result =  {"cordinates": results["cordinates"]}

    return (random.randint(0, 1), random.randint(0, 1))


