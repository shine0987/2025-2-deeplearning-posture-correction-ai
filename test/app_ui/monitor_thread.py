import cv2
import numpy as np
import time
import sys
import os 
import logging
from PyQt6.QtCore import QThread, pyqtSignal

# --- [경로 설정] ---
# 현재 파일: .../test/app_ui/monitor_thread.py
current_dir = os.path.dirname(os.path.abspath(__file__)) 
test_dir = os.path.dirname(current_dir) # test 폴더

if test_dir not in sys.path:
    sys.path.append(test_dir)

# --- [Import] ---
try:
    from model_num2.src.realtime_cam import RealtimePostureMonitor
    print("✅ RealtimePostureMonitor 모듈 로드 성공")
except ImportError as e:
    print(f"⚠️ 모듈 로드 실패: {e}")
    sys.path.append(os.path.join(test_dir, 'model_num2'))
    try:
        from model_num2.src.realtime_cam import RealtimePostureMonitor
    except Exception as e2:
        print(f"❌ 치명적 오류: {e2}")

class MonitorThread(QThread):
    """
    웹캠 피드 처리 및 자세 추론을 담당하는 QThread
    """
    # GUI로 보낼 시그널
    frame_ready = pyqtSignal(np.ndarray)  # 영상 프레임
    posture_status = pyqtSignal(str)      # 자세 상태 텍스트
    timer_updated = pyqtSignal(int, int)  # (총 시간, 바른 자세 시간)
    
    def __init__(self):
        super().__init__()
        self._is_running = False
        self.cap = None
        self.monitor = None  # RealtimePostureMonitor 객체
        
        # 타이머 관련 변수
        self.total_time_sec = 0
        self.correct_time_sec = 0
        self.start_time = None
        
        # 에러 로그 도배 방지
        self.last_error_time = 0  
        self.error_log_interval = 3.0

    def run(self):
        logging.info("모니터링 스레드 시작")
        
        # 1. 절대 경로 계산 (test/model_num2/models 기준)
        model_base_dir = os.path.join(test_dir, 'model_num2', 'models')
        abs_model_path = os.path.join(model_base_dir, 'cnn_lstm_model.h5')
        abs_scaler_path = os.path.join(model_base_dir, 'scaler_cnn_lstm.pkl')
        
        # 2. 모니터링 객체 생성 (여기서만 모델을 로드합니다)
        if self.monitor is None:
            try:
                logging.info(f"모델 로드 시도: {abs_model_path}")
                # [중요] 키워드 인자(model_path=...)를 명시하여 순서가 바뀌는 실수를 방지합니다.
                self.monitor = RealtimePostureMonitor(
                    model_path=abs_model_path,
                    scaler_path=abs_scaler_path
                )
            except Exception as e:
                logging.error(f"❌ 모델 초기화 실패: {e}")
                return # 모델 없으면 스레드 종료

        # 3. 카메라 연결
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            logging.error("카메라를 열 수 없습니다.")
            return

        self._is_running = True
        self.start_time = time.time()
        last_timer_update = time.time()
        
        current_posture = "Ready"

        while self._is_running:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # 거울 모드 (좌우 반전)
            frame = cv2.flip(frame, 1)

            # 4. 예측 실행 (RealtimePostureMonitor에게 위임)
            try:
                result = self.monitor.process_frame(frame)
                current_posture = result.get('predicted_class', 'Unknown')
                
            except Exception as e:
                # 반복적인 에러 로그 출력 방지
                now = time.time()
                if now - self.last_error_time > self.error_log_interval:
                    logging.error(f"예측 중 오류: {e}")
                    self.last_error_time = now
                pass

            # 5. 화면에 텍스트 그리기 (간단 상태 표시)
            if current_posture == "normal":
                color = (0, 255, 0) # Green
            elif current_posture == "abnormal":
                color = (0, 0, 255) # Red
            else:
                color = (200, 200, 200) # Gray

            cv2.putText(frame, f"Status: {current_posture}", (10, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            # 6. GUI로 데이터 전송
            self.frame_ready.emit(frame)
            self.posture_status.emit(current_posture)
            
            # 7. 타이머 로직 (1초마다 업데이트)
            cur_time = time.time()
            if cur_time - last_timer_update >= 1.0:
                elapsed = cur_time - self.start_time
                self.total_time_sec = int(elapsed)
                
                if current_posture == "normal":
                    self.correct_time_sec += 1
                
                self.timer_updated.emit(self.total_time_sec, self.correct_time_sec)
                last_timer_update = cur_time

            # CPU 점유율 조절 (약 30 FPS)
            time.sleep(0.03)

        # 종료 처리
        if self.cap:
            self.cap.release()
            logging.info("카메라 해제 완료")

    def stop(self):
        self._is_running = False
        self.wait()