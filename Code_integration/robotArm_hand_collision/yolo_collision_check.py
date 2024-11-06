import os
from ultralytics import YOLO

yolo_weight_path = '/home/hjpark/dev_hjp/aris-repo-1/Code_integration/robotArm_hand_collision/aris_top_3class_best_1106.pt'
image_source = "/home/hjpark/dev_hjp/aris-repo-1/Code_integration/robotArm_hand_collision/test_data/captured_image_50.jpg"

def check_hand_collision(hand_boxes, robot_box, threshold=0):
    """
    손과 로봇 간의 충돌/접촉 여부를 확인
    
    Returns:
    bool: 충돌 여부 (True/False)
    list: 각 손별 충돌 정보 [(hand_index, is_colliding, iou), ...]
    """
    if not isinstance(hand_boxes[0], list):
        hand_boxes = [hand_boxes]  # 단일 손 좌표를 리스트로 변환
    
    any_collision = False
    collision_info = []
    
    for idx, hand_box in enumerate(hand_boxes):
        hand_x1, hand_y1, hand_x2, hand_y2 = hand_box
        robot_x1, robot_y1, robot_x2, robot_y2 = robot_box
        
        # 겹치는 영역 계산
        x_left = max(hand_x1, robot_x1)
        y_top = max(hand_y1, robot_y1)
        x_right = min(hand_x2, robot_x2)
        y_bottom = min(hand_y2, robot_y2)
        
        # threshold를 적용한 겹침 확인
        is_colliding = False
        iou = 0.0
        
        if (x_right + threshold >= x_left - threshold and 
            y_bottom + threshold >= y_top - threshold):
            
            # 겹치는 영역의 넓이 계산
            intersection_area = max(0, x_right - x_left) * max(0, y_bottom - y_top)
            
            # 각 박스의 넓이 계산
            hand_area = (hand_x2 - hand_x1) * (hand_y2 - hand_y1)
            robot_area = (robot_x2 - robot_x1) * (robot_y2 - robot_y1)
            
            # 합집합 넓이 계산
            union_area = hand_area + robot_area - intersection_area
            
            # IoU (Intersection over Union) 계산
            iou = intersection_area / union_area if union_area > 0 else 0
            is_colliding = True
            any_collision = True
            
        collision_info.append((idx, is_colliding, iou))
    
    return any_collision, collision_info

# -----------------------------------------------------------------------

# Load a pretrained model
model = YOLO(yolo_weight_path)

# Run inference on an image
results = model.predict(image_source)

robot_arm_xyxy = []
hand_xyxy = []
cap_xyxy=[]
for i in range(len(results[0])):
    class_num = int(results[0][i].boxes.cls) 
    xyxy_list = results[0][i].boxes.xyxy.tolist()[0]
    if class_num == 0:
      robot_arm_xyxy=xyxy_list
    elif class_num == 1:
      hand_xyxy.append(xyxy_list)
    else:
      cap_xyxy.append(xyxy_list)


robot_area = robot_arm_xyxy

hands1 = hand_xyxy

print("케이스 1 (다중 손) 결과:")
is_colliding, details = check_hand_collision(hands1, robot_area, threshold=0)
print(f"충돌 발생 여부: {is_colliding}")
print("상세 정보:")
for hand_idx, is_coll, iou in details:
    print(f"손 #{hand_idx}: 충돌={is_coll}, IoU={iou:.2f}")
