"""
3단계: 실시간 웹캠 AI 시스템
- 웹캠 입력으로 실시간 자세 평가
- 학습된 모델로 자세 평가
- 실시간 피드백 제공
"""

import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
from pathlib import Path
import logging
import time
from collections import deque
import json
import os
import joblib

# 로깅 설정
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

class RealtimePostureMonitor:
    def __init__(self, model_path='models/cnn_lstm_model.h5', scaler_path='models/scaler_cnn_lstm.pkl'):
        """실시간 자세 모니터링 시스템"""
        # MediaPipe 초기화
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
            model_complexity=1
        )
        
        # 모델 및 데이터 관련 변수 초기화
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.sequence_length = 10
        self.feature_columns = None
        self.preprocessor = None
        
        if Path(model_path).exists():
            self.load_model(model_path)
        else:
            logging.warning(f"모델 파일을 찾을 수 없습니다: {model_path}")
            
        # [추가] 스케일러 경로
        if Path(scaler_path).exists():
            self.load_model(scaler_path)
        else:
            logging.warning(f"스케일러 파일을 찾을 수 없습니다: {scaler_path}")
        
        # 데이터 버퍼 (시퀀스용)
        self.pose_buffer = deque(maxlen=self.sequence_length)
        
        # 예측 결과 저장
        self.predictions = deque(maxlen=30)  # 30프레임 평균
        self.current_posture = "Unknown"
        self.confidence = 0.0
        
        # 알림 설정
        self.last_alert_time = 0
        self.alert_interval = 3.0  # 3초 간격으로 알림
        
        # 상체 랜드마크 인덱스
        self.upper_body_landmarks = {
            'nose': 0,
            'left_shoulder': 11,
            'right_shoulder': 12,
            'left_hip': 23,
            'right_hip': 24
        }
        
        # 색상 정의
        self.colors = {
            'normal': (0, 255, 0),      # 초록색
            'abnormal': (0, 0, 255),    # 빨간색
            'unknown': (128, 128, 128)  # 회색
        }
        
        
    def load_model(self, model_path_arg=None):
        """저장된 모델 로드 (경로 완전 자동화 버전)"""
        try:
            # 1. 경로 기준점 잡기 (현재 파일 위치 기준)
            # .../test/model_num2/src/realtime_cam.py
            current_file = os.path.abspath(__file__)
            src_dir = os.path.dirname(current_file)           # .../src
            model_num2_dir = os.path.dirname(src_dir)         # .../model_num2
            models_dir = os.path.join(model_num2_dir, 'models') # .../model_num2/models

            logging.info(f"📂 모델 폴더 탐색 경로: {models_dir}")

            # 2. 파일 경로 확정
            if model_path_arg and os.path.isabs(model_path_arg):
                h5_path = model_path_arg
            else:
                h5_path = os.path.join(models_dir, 'cnn_lstm_model.h5')

            scaler_path = os.path.join(models_dir, 'scaler_cnn_lstm.pkl')
            label_path = os.path.join(models_dir, 'label_encoder_cnn_lstm.pkl')
            meta_path = os.path.join(models_dir, 'model_metadata_cnn_lstm.json')

            # 3. 파일 존재 확인
            if not os.path.exists(h5_path):
                raise FileNotFoundError(f"모델 파일 없음: {h5_path}")

            # 4. 로드 실행
            self.model = tf.keras.models.load_model(h5_path)
            self.scaler = joblib.load(scaler_path)
            self.label_encoder = joblib.load(label_path)
            
            with open(meta_path, 'r') as f:
                metadata = json.load(f)
            
            self.sequence_length = metadata['sequence_length']
            self.feature_columns = metadata['feature_columns']
            
            # 버퍼 크기 재설정
            self.pose_buffer = deque(maxlen=self.sequence_length)
            
            logging.info(f"✅ 모델 및 메타데이터 로드 완료!")
            return True

        except Exception as e:
            logging.error(f"❌ 모델 로드 실패: {e}")
            self.model = None
            return False
    
    
    def extract_pose_features(self, landmarks, image_shape) -> dict:
        """포즈 랜드마크에서 특성 추출"""
        if not landmarks:
            return None
        
        try:
            h, w = image_shape[:2]
            
            # 상체 랜드마크 추출
            pose_data = {}
            for name, idx in self.upper_body_landmarks.items():
                landmark = landmarks.landmark[idx]
                pose_data[f'{name}_x'] = landmark.x
                pose_data[f'{name}_y'] = landmark.y
                pose_data[f'{name}_visibility'] = landmark.visibility
            
            # 각도 계산
            angles = self.calculate_angles(pose_data)
            pose_data.update(angles)
            
            return pose_data
            
        except Exception as e:
            logging.error(f"특성 추출 실패: {e}")
            return None
    
    def calculate_angles(self, pose_data: dict) -> dict:
        """자세 각도 계산"""
        angles = {}
        
        try:
            # 목 각도
            nose_x, nose_y = pose_data['nose_x'], pose_data['nose_y']
            left_shoulder_x = pose_data['left_shoulder_x']
            left_shoulder_y = pose_data['left_shoulder_y']
            right_shoulder_x = pose_data['right_shoulder_x']
            right_shoulder_y = pose_data['right_shoulder_y']
            
            shoulder_center_x = (left_shoulder_x + right_shoulder_x) / 2
            shoulder_center_y = (left_shoulder_y + right_shoulder_y) / 2
            
            neck_angle = np.degrees(np.arctan2(
                nose_x - shoulder_center_x,
                shoulder_center_y - nose_y
            ))
            angles['neck_angle'] = neck_angle
            
            # 어깨 기울기
            shoulder_angle = np.degrees(np.arctan2(
                right_shoulder_y - left_shoulder_y,
                right_shoulder_x - left_shoulder_x
            ))
            angles['shoulder_angle'] = shoulder_angle
            
            # 허리 기울기
            left_hip_x = pose_data['left_hip_x']
            left_hip_y = pose_data['left_hip_y']
            right_hip_x = pose_data['right_hip_x']
            right_hip_y = pose_data['right_hip_y']
            
            hip_angle = np.degrees(np.arctan2(
                right_hip_y - left_hip_y,
                right_hip_x - left_hip_x
            ))
            angles['hip_angle'] = hip_angle
            
            # 상체 전체 기울기
            hip_center_x = (left_hip_x + right_hip_x) / 2
            hip_center_y = (left_hip_y + right_hip_y) / 2
            
            torso_angle = np.degrees(np.arctan2(
                shoulder_center_x - hip_center_x,
                hip_center_y - shoulder_center_y
            ))
            angles['torso_angle'] = torso_angle
            
        except Exception as e:
            logging.error(f"각도 계산 실패: {e}")
            angles = {
                'neck_angle': 0.0,
                'shoulder_angle': 0.0,
                'hip_angle': 0.0,
                'torso_angle': 0.0
            }
        
        return angles
    
    def predict_posture(self, pose_data: dict) -> dict:
        """자세 예측"""
        if self.model is None or not pose_data:
            return {'predicted_class': 'unknown', 'confidence': 0.0}
        
        try:
            # 특성 벡터 생성
            feature_vector = []
            for col in self.feature_columns:
                if col in pose_data:
                    feature_vector.append(pose_data[col])
                else:
                    feature_vector.append(0.0)  # 기본값
            
            feature_vector = np.array(feature_vector).reshape(1, -1)
            
            # 버퍼에 추가
            self.pose_buffer.append(feature_vector[0])
            
            # 시퀀스가 충분히 쌓이지 않았으면 대기
            if len(self.pose_buffer) < self.sequence_length:
                return {'predicted_class': 'unknown', 'confidence': 0.0}
            
            # 시퀀스 생성
            sequence = np.array(list(self.pose_buffer))
            sequence_scaled = self.scaler.transform(sequence)
            sequence_input = sequence_scaled.reshape(1, self.sequence_length, -1)
            
            # 예측
            prediction_proba = self.model.predict(sequence_input, verbose=0)[0]
            predicted_class_idx = np.argmax(prediction_proba)
            predicted_class = self.label_encoder.inverse_transform([predicted_class_idx])[0]
            confidence = prediction_proba[predicted_class_idx]
            
            return {
                'predicted_class': predicted_class,
                'confidence': float(confidence)
            }
            
        except Exception as e:
            logging.error(f"예측 실패: {e}")
            return {'predicted_class': 'unknown', 'confidence': 0.0}
    
    def smooth_predictions(self, prediction: dict):
        """예측 결과 스무딩"""
        self.predictions.append(prediction)
        
        if len(self.predictions) < 5:
            return
        
        # 최근 예측 결과들의 다수결
        recent_predictions = list(self.predictions)[-10:]
        
        # 클래스별 가중 평균
        class_weights = {}
        for pred in recent_predictions:
            class_name = pred['predicted_class']
            confidence = pred['confidence']
            
            if class_name in class_weights:
                class_weights[class_name] += confidence
            else:
                class_weights[class_name] = confidence
        
        if class_weights:
            best_class = max(class_weights, key=class_weights.get)
            avg_confidence = class_weights[best_class] / len(recent_predictions)
            
            self.current_posture = best_class
            self.confidence = avg_confidence
    
    def draw_pose_landmarks(self, image, landmarks):
        """포즈 랜드마크 그리기"""
        if landmarks:
            # 상체 랜드마크만 그리기
            for name, idx in self.upper_body_landmarks.items():
                landmark = landmarks.landmark[idx]
                h, w = image.shape[:2]
                x, y = int(landmark.x * w), int(landmark.y * h)
                
                # 자세에 따른 색상
                color = self.colors.get(self.current_posture.lower(), self.colors['unknown'])
                cv2.circle(image, (x, y), 8, color, -1)
                cv2.circle(image, (x, y), 10, (255, 255, 255), 2)
    
    def draw_status_info(self, image):
        """상태 정보 표시"""
        h, w = image.shape[:2]
        
        # 배경 박스
        overlay = image.copy()
        cv2.rectangle(overlay, (10, 10), (w-10, 120), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, image, 0.3, 0, image)
        
        # 자세 상태
        color = self.colors.get(self.current_posture.lower(), self.colors['unknown'])
        status_text = f"Posture: {self.current_posture.upper()}"
        cv2.putText(image, status_text, (20, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
        
        # 신뢰도
        confidence_text = f"Confidence: {self.confidence:.2f}"
        cv2.putText(image, confidence_text, (20, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 상태 메시지
        if self.current_posture.lower() == 'abnormal' and self.confidence > 0.7:
            message = "Please correct your posture!"
            cv2.putText(image, message, (20, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        elif self.current_posture.lower() == 'normal':
            message = "Good posture!"
            cv2.putText(image, message, (20, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    def should_alert(self) -> bool:
        """알림이 필요한지 확인"""
        current_time = time.time()
        if (self.current_posture.lower() == 'abnormal' and 
            self.confidence > 0.8 and 
            current_time - self.last_alert_time > self.alert_interval):
            self.last_alert_time = current_time
            return True
        return False
    
    
    def process_frame(self, frame):
        """
        [통합 예측 함수]
        이미지 프레임 -> 전처리 -> 예측 -> 결과 반환
        """
        if self.model is None:
            return {'predicted_class': 'Loading...', 'confidence': 0.0}

        try:
            # --- 1. CNN 입력 준비 (이미지) ---
            # 학습 시 사용한 이미지 크기 (cnn_lstm_model.py 참고, 보통 128 또는 224)
            IMG_SIZE = 128 
            
            img_resized = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
            img_normalized = img_resized / 255.0
            cnn_input = np.expand_dims(img_normalized, axis=0) # (1, 128, 128, 3)

            # --- 2. LSTM 입력 준비 (시퀀스) ---
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(frame_rgb)
            
            if not results.pose_landmarks:
                return {'predicted_class': 'No Pose', 'confidence': 0.0}

            # 랜드마크 -> 특징 벡터 추출
            landmarks = results.pose_landmarks.landmark
            angles_dict = self.preprocessor.calculate_angles(landmarks) # preprocessing 사용
            
            feature_vector = []
            for col in self.feature_columns:
                if col in angles_dict:
                    feature_vector.append(angles_dict[col])
                else:
                    feature_vector.append(0.0) # 좌표값 등은 0 처리 혹은 추가 로직 구현

            # 버퍼에 추가
            self.pose_buffer.append(feature_vector)
            
            # 시퀀스가 아직 덜 찼으면 대기
            if len(self.pose_buffer) < self.sequence_length:
                return {'predicted_class': 'Initializing...', 'confidence': 0.0}
            
            # 시퀀스 데이터 변환
            seq_data = list(self.pose_buffer)
            seq_scaled = self.scaler.transform(seq_data)
            lstm_input = np.expand_dims(seq_scaled, axis=0) # (1, seq_len, features)

            # --- 3. 듀얼 인풋 예측 ---
            # [주의] 모델 학습 시 Input 순서가 [img_input, num_input] 인지 확인 필요
            prediction = self.model.predict([cnn_input, lstm_input], verbose=0)
            
            label_idx = np.argmax(prediction[0])
            confidence = prediction[0][label_idx]
            predicted_class = self.label_encoder.classes_[label_idx]

            return {
                'predicted_class': predicted_class,
                'confidence': float(confidence)
            }

        except Exception as e:
            # 여기서 에러는 monitor_thread에서 잡아서 스로틀링함
            raise e


def main():
    parser = argparse.ArgumentParser(description='실시간 자세 모니터링')
    parser.add_argument('--camera', type=int, default=0, 
                       help='카메라 ID (기본: 0)')
    parser.add_argument('--model', default='models/cnn_lstm_model.h5', 
                       help='CNN+LSTM 모델 파일 경로')
    parser.add_argument('--no_window', action='store_true', 
                       help='화면 표시 안 함 (백그라운드 실행)')
    
    args = parser.parse_args()
    
    try:
        # 모니터링 시스템 초기화
        monitor = RealtimePostureMonitor(model_path=args.model)
        
        # 실행
        monitor.run(camera_id=args.camera, show_window=not args.no_window)
        
    except KeyboardInterrupt:
        logging.info("사용자에 의해 중단됨")
    except Exception as e:
        logging.error(f"실행 중 오류 발생: {e}")
        raise


if __name__ == '__main__':
    main()