import cv2
import mediapipe as mp

#신체 랜드마크 감지를 위해 MediaPipe 포즈 모델을 초기화합니다.
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

#mp_drawing 변수를 초기화하고 이를 mp.solutions.raw_utils 클래스와 연결
mp_drawing = mp.solutions.drawing_utils

# 비디오 캡처 객체 생성
cap = cv2.VideoCapture(0)

#비디오 프레임을 지속적으로 처리하고 신체 랜드마크를 오버레이하는 루프를 만들자
while True:
    #웹캠에서 프레임을 읽는다.
    ret, frame = cap.read()
    if not ret:
        break

    #프레임을 RGB로 변화해준다.
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    #MediaPipe Pose로 프레임을 처리한다.
    results = pose.process(frame_rgb)

    #랜드마크가 감지되었는지 확인
    if results.pose_landmarks:
        #프레임에 랜드마크를 렌더링한다.
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        h, w, _ = frame.shape
        # 주요 부위 인덱스 (Neck, Shoulder, Hip)
        landmark_dict = {
            "Neck": 0,         # Nose(대체)
            "Left Shoulder": 11, # Left Shoulder
            "Right Shoulder": 12, # Right Shoulder
            "Left Hip": 23, # Left Hip
            "Right Hip": 24 # Right Hip
        }
        # 텍스트 위치 시작점
        y0 = 30
        for i, (name, idx) in enumerate(landmark_dict.items()):
            landmark = results.pose_landmarks.landmark[idx]
            x, y = int(landmark.x * w), int(landmark.y * h)
            text = f"{name}: ({x}, {y})"
            # 프레임 왼쪽에 부위별 이름과 좌표 표시
            cv2.putText(frame, text, (20, y0 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # 랜드마크가 있는 프레임을 보여준다.
    cv2.imshow('Body Landmarks', frame)

    # q를 누르면 while문 종료됨.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

#프로그램 작업을 마친 후 할당된 리소르를 남기거나 열어두지 않게 함

#비디오 캡처 리소스를 해제
cap.release()
#모든 OpenCV 표시 창을 닫습니다.
cv2.destroyAllWindows()