import cv2
import numpy as np
import time
import sys
import os 
import logging
from PyQt6.QtCore import QThread, pyqtSignal

current_dir = os.path.dirname(os.path.abspath(__file__)) 
test_dir = os.path.dirname(current_dir) 

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
    frame_ready = pyqtSignal(np.ndarray)  # 영상 프레임
    posture_status = pyqtSignal(str)      # 자세 상태 텍스트
    timer_updated = pyqtSignal(int, int)  # (총 시간, 바른 자세 시간)
    
    # 로딩 완료 시그널
    load_finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._is_running = False
        self.cap = None
        self.monitor = None
        
        # 타이머 관련 변수
        self.total_time_sec = 0
        self.correct_time_sec = 0
        self.start_time = None
        
        # 에러 로그 도배 방지
        self.last_error_time = 0  
        self.error_log_interval = 3.0

    def run(self):
        logging.info("모니터링 스레드 시작")
        
        model_base_dir = "models"
        h5_file = "best_cnn_lstm_model.h5" 
        scaler_file = "scaler_cnn_lstm.pkl"

        # 절대 경로 생성
        abs_model_path = os.path.abspath(os.path.join(model_base_dir, h5_file))
        abs_scaler_path = os.path.abspath(os.path.join(model_base_dir, scaler_file))
        
        # 2. 필수 파일 존재 여부 체크
        missing_files = []
        if not os.path.exists(abs_model_path): missing_files.append(model_filename)
        if not os.path.exists(abs_scaler_path): missing_files.append(scaler_filename)
    
        if missing_files:
            logging.error(f"필수 모델 파일이 누락되었습니다: {missing_files}")
            logging.error(f"현재 위치에서 'models' 폴더를 찾을 수 없습니다. (현재위치: {os.getcwd()})")
            return # 파일이 없으면 시작하지 않음

        # 3. 모델 로딩
        if self.monitor is None:
            try:
                logging.info(f"모델 로드 시작: {abs_model_path}")
                
                # 키워드 인자(model_path=...)를 명시
                self.monitor = RealtimePostureMonitor(
                    model_path=abs_model_path,
                    scaler_path=abs_scaler_path
                )
                logging.info("✅ 모델 로드 완료")
                
            except Exception as e:
                logging.error(f"❌ 모델 초기화 실패: {e}")
                return

        # 로딩 완료 시그널 
        self.load_finished.emit()
        
        # 4. 카메라 연결
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
            
            # 거울 모드
            frame = cv2.flip(frame, 1)

            # 5. 예측 실행
            try:
                result = self.monitor.process_frame(frame)
                current_posture = result.get('predicted_class', 'Unknown')
                
            except Exception as e:
                now = time.time()
                if now - self.last_error_time > self.error_log_interval:
                    logging.error(f"예측 중 오류: {e}")
                    self.last_error_time = now
                pass

            # 6. 화면 텍스트 (디버깅용, 실제 UI는 Qt에서 처리)
            if current_posture == "normal":
                color = (0, 255, 0) # Green
            elif current_posture == "abnormal":
                color = (0, 0, 255) # Red
            else:
                color = (200, 200, 200) # Gray

            cv2.putText(frame, f"Status: {current_posture}", (10, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            # 7. GUI 전송
            self.frame_ready.emit(frame)
            self.posture_status.emit(current_posture)
            
            # 8. 타이머 
            cur_time = time.time()
            if cur_time - last_timer_update >= 1.0:
                elapsed = cur_time - self.start_time
                self.total_time_sec = int(elapsed)
                
                if current_posture == "normal":
                    self.correct_time_sec += 1
                
                self.timer_updated.emit(self.total_time_sec, self.correct_time_sec)
                last_timer_update = cur_time

        # 종료 처리
        if self.cap:
            self.cap.release()
            logging.info("카메라 해제")

    def stop(self):
        self._is_running = False
        self.wait()