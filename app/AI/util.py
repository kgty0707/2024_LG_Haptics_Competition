import os

from datetime import datetime


def save_result_image(image, save_dir="./uploads_inference_results", prefix="inference_result"):
    sub_dir = os.path.join(save_dir, prefix)
    os.makedirs(sub_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.png"
    save_path = os.path.join(sub_dir, filename)
    image.save(save_path)
    print(f"추론 결과 이미지 저장 경로: {save_path}")
    return save_path


def draw_shadow_bounding_box(draw, bbox, label=None, color="green", mode="box+label", corner_points=False):
    x1, y1, x2, y2 = bbox

    if "box" in mode:
        draw.rectangle([x1, y1, x2, y2], outline=color, width=2)

    if "label" in mode and label:
        draw.text((x1 + 5, y1 - 10), label, fill=color)

    if corner_points:
        r = 4
        corners = {
            "Top-Left": (x1, y1),
            "Top-Right": (x2, y1),
            "Bottom-Left": (x1, y2),
            "Bottom-Right": (x2, y2)
        }
        for (px, py) in corners.values():
            draw.ellipse((px - r, py - r, px + r, py + r), fill=color)
            draw.text((px + 5, py), f"[{px}, {py}]", fill=color)


def draw_lipstick_data(draw, lips_data, point_radius=3):
    x1 = lips_data["x1"]
    y1 = lips_data["y1"]
    x2 = lips_data["x2"]
    y2 = lips_data["y2"]
    top_middle_x = lips_data["top_middle_x"]
    top_middle_y = lips_data["top_middle_y"]

    draw.rectangle([(x1, y1), (x2, y2)], outline="red", width=2)

    draw.ellipse(
        (top_middle_x - point_radius, top_middle_y - point_radius,
         top_middle_x + point_radius, top_middle_y + point_radius),
        fill="blue"
    )

    draw.text((x1 + 4, y1 - 12), "Lipstick", fill="red")


def draw_lips_data(draw, lips_data, point_radius=1):
    for name, pt in lips_data["key_points"].items():
        x, y = int(pt["x"]), int(pt["y"])
        draw.ellipse((x - point_radius, y - point_radius, x + point_radius, y + point_radius), fill="red")
    
    center = lips_data["key_points"]["right_corner"]
    lip_x, lip_y = int(center["x"]), int(center["y"])

    box_x1 = lip_x - 10
    box_y1 = lip_y - 10
    box_x2 = lip_x + 10
    box_y2 = lip_y + 10

    draw.rectangle([(box_x1, box_y1), (box_x2, box_y2)], outline="green", width=2)

def draw_hand_data(draw, hand_data, point_radius=3):
    x = int(hand_data["index_tip_location"]["x"])
    y = int(hand_data["index_tip_location"]["y"])

    draw.ellipse(
        (x - point_radius, y - point_radius, x + point_radius, y + point_radius),
        fill="blue"
    )

    draw.text((x + 5, y), "Index Tip", fill="blue")

