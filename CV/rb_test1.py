import cv2
from ultralytics import YOLO  # YOLO 라이브러리를 import

# YOLO 모델 불러오기
model = YOLO('/home/zl/Downloads/best (2).pt')

# 웹캠 열기
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Failed to open the camera")
else:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # YOLO 모델로 예측 수행
        results = model.predict(source=frame, conf=0.30, show=True)

        # ESC 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == 27:
            break

# 카메라와 창 닫기
cap.release()
cv2.destroyAllWindows()
