import mediapipe as mp

# MediaPipe hand 초기화
mp_hands = mp.solutions.hands

# 입술 관련 랜드마크 인덱스
LIPS_INDEXES = {
    "outer_lips": [
        61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270, 269, 267, 0, 37, 39, 40, 185
    ],
    "inner_lips": [
        78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308, 415, 310, 311, 312, 13, 82, 81, 80, 191
    ],
    "upper_lip": [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291],
    "lower_lip": [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291],
    
    # 특정 랜드마크 포인트
    "upper_lip_top": 0,      # 윗입술 중앙 상단
    "upper_lip_bottom": 13,  # 윗입술 중앙 하단
    "lower_lip_top": 14,     # 아랫입술 중앙 상단
    "lower_lip_bottom": 17,  # 아랫입술 중앙 하단
    "left_corner": 61,       # 왼쪽 입꼬리
    "right_corner": 291      # 오른쪽 입꼬리
}

# 손 랜드마크 이름 매핑
HAND_LANDMARK_NAMES = {
    # mp_hands.HandLandmark.WRIST: "WRIST",
    # mp_hands.HandLandmark.THUMB_CMC: "THUMB_CMC",
    # mp_hands.HandLandmark.THUMB_MCP: "THUMB_MCP",
    # mp_hands.HandLandmark.THUMB_IP: "THUMB_IP",
    # mp_hands.HandLandmark.THUMB_TIP: "THUMB_TIP",
    mp_hands.HandLandmark.INDEX_FINGER_MCP: "INDEX_FINGER_MCP",
    # mp_hands.HandLandmark.INDEX_FINGER_PIP: "INDEX_FINGER_PIP",
    # mp_hands.HandLandmark.INDEX_FINGER_DIP: "INDEX_FINGER_DIP",
    # mp_hands.HandLandmark.INDEX_FINGER_TIP: "INDEX_FINGER_TIP",
    # mp_hands.HandLandmark.MIDDLE_FINGER_MCP: "MIDDLE_FINGER_MCP",
    # mp_hands.HandLandmark.MIDDLE_FINGER_PIP: "MIDDLE_FINGER_PIP",
    # mp_hands.HandLandmark.MIDDLE_FINGER_DIP: "MIDDLE_FINGER_DIP",
    # mp_hands.HandLandmark.MIDDLE_FINGER_TIP: "MIDDLE_FINGER_TIP",
    # mp_hands.HandLandmark.RING_FINGER_MCP: "RING_FINGER_MCP",
    # mp_hands.HandLandmark.RING_FINGER_PIP: "RING_FINGER_PIP",
    # mp_hands.HandLandmark.RING_FINGER_DIP: "RING_FINGER_DIP",
    # mp_hands.HandLandmark.RING_FINGER_TIP: "RING_FINGER_TIP",
    # mp_hands.HandLandmark.PINKY_MCP: "PINKY_MCP",
    # mp_hands.HandLandmark.PINKY_PIP: "PINKY_PIP",
    # mp_hands.HandLandmark.PINKY_DIP: "PINKY_DIP",
    # mp_hands.HandLandmark.PINKY_TIP: "PINKY_TIP"
}

def extract_lips_data(landmarks, image_width, image_height):
    # 랜드마크를 픽셀 좌표로 변환하는 함수
    def landmark_to_pixel(landmark):
        return {
            "x": landmark.x * image_width,
            "y": landmark.y * image_height,
            # "z": landmark.z * image_width  # z값도 픽셀 단위로 변환
        }
    
    # 주요 입술 포인트
    upper_lip_top = landmark_to_pixel(landmarks.landmark[LIPS_INDEXES["upper_lip_top"]])
    upper_lip_bottom = landmark_to_pixel(landmarks.landmark[LIPS_INDEXES["upper_lip_bottom"]])
    lower_lip_top = landmark_to_pixel(landmarks.landmark[LIPS_INDEXES["lower_lip_top"]])
    lower_lip_bottom = landmark_to_pixel(landmarks.landmark[LIPS_INDEXES["lower_lip_bottom"]])
    left_corner = landmark_to_pixel(landmarks.landmark[LIPS_INDEXES["left_corner"]])
    right_corner = landmark_to_pixel(landmarks.landmark[LIPS_INDEXES["right_corner"]])
    
    # 데이터 구성
    lips_data = {
        "key_points": {
            "upper_lip_top": {"index": LIPS_INDEXES["upper_lip_top"], **upper_lip_top},
            "upper_lip_bottom": {"index": LIPS_INDEXES["upper_lip_bottom"], **upper_lip_bottom},
            "lower_lip_top": {"index": LIPS_INDEXES["lower_lip_top"], **lower_lip_top},
            "lower_lip_bottom": {"index": LIPS_INDEXES["lower_lip_bottom"], **lower_lip_bottom},
            "left_corner": {"index": LIPS_INDEXES["left_corner"], **left_corner},
            "right_corner": {"index": LIPS_INDEXES["right_corner"], **right_corner}
        },
    }
    
    return lips_data


def extract_hand_data(landmarks, handedness, image_width, image_height):
    
    def landmark_to_pixel(landmark):
        return {
            "x": landmark.x * image_width,
            "y": landmark.y * image_height,
            # "z": landmark.z * image_width  # z값도 픽셀 단위로 변환
        }
    # 손의 좌/우 구분
    hand_type = handedness.classification[0].label
    index_tip_location = landmark_to_pixel(landmarks.landmark[8])

    hand_data = {
        "hand_type": hand_type,
        "index_tip_location": index_tip_location
    }

    return hand_data