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
    def __init__(self, scaler_path, model_path='models/cnn_lstm_model.h5'):
        """실시간 자세 모니터링 시스템 (수치 데이터만 사용)"""
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
        self.sequence_length = 5  # 기본값, 메타데이터에서 덮어씀
        self.feature_columns = None
        self.preprocessor = None
        
        if Path(model_path).exists():
            self.load_model(model_path)
        else:
            logging.warning(f"모델 파일을 찾을 수 없습니다: {model_path}")
        
        # 데이터 버퍼 (시퀀스용 - 수치 데이터만)
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
        
        
    def load_model(self, model_path_arg):
        """모델과 관련 파일들(Scaler, Encoder, Metadata) 로드"""
        try:
            # 경로 설정
            if os.path.exists(model_path_arg):
                h5_path = model_path_arg
                base_dir = os.path.dirname(model_path_arg)
            else:
                base_dir = 'models'
                h5_path = os.path.join(base_dir, 'best_cnn_lstm_model.h5')

            scaler_path = os.path.join(base_dir, 'scaler_cnn_lstm.pkl')
            label_path = os.path.join(base_dir, 'label_encoder_cnn_lstm.pkl')
            meta_path = os.path.join(base_dir, 'model_metadata_cnn_lstm.json')

            logging.info(f"📂 파일 로드 시도:\n - Model: {h5_path}\n - Scaler: {scaler_path}")

            # 파일 존재 확인
            if not os.path.exists(h5_path): raise FileNotFoundError(f"모델 없음: {h5_path}")
            if not os.path.exists(scaler_path): raise FileNotFoundError(f"스케일러 없음: {scaler_path}")
            if not os.path.exists(meta_path): raise FileNotFoundError(f"메타데이터 없음: {meta_path}")

            # 로드 실행 (compile=False는 예측 전용)
            self.model = tf.keras.models.load_model(h5_path, compile=False)
            self.scaler = joblib.load(scaler_path)
            self.label_encoder = joblib.load(label_path)
            
            with open(meta_path, 'r') as f:
                metadata = json.load(f)
            
            self.sequence_length = metadata['sequence_length']
            self.feature_columns = metadata['feature_columns']
            
            # 버퍼 재설정
            self.pose_buffer = deque(maxlen=self.sequence_length)
            
            logging.info(f"✅ 모델 로드 성공 (Seq: {self.sequence_length})")
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
            
            # 상대적 특성 계산 (shoulder_width, hip_width 등)
            relative_features = self.calculate_relative_features(pose_data)
            pose_data.update(relative_features)
            
            return pose_data
            
        except Exception as e:
            logging.error(f"특성 추출 실패: {e}")
            return None
    
    def calculate_angles(self, pose_data: dict) -> dict:
        """자세 각도 계산 (절대값 기반 - 좌우 위치 무관)"""
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
            
            # 목 기울기: y축 차이만 고려 (수직 방향 기울기)
            y_diff = shoulder_center_y - nose_y
            x_diff_abs = abs(nose_x - shoulder_center_x)
            neck_angle = np.degrees(np.arctan2(x_diff_abs, y_diff))
            angles['neck_angle'] = neck_angle
            
            # 어깨 기울기: 절대값으로 좌우 대칭 처리
            shoulder_angle = abs(np.degrees(np.arctan2(
                right_shoulder_y - left_shoulder_y,
                right_shoulder_x - left_shoulder_x
            )))
            angles['shoulder_angle'] = shoulder_angle
            
            # 허리 기울기: 절대값으로 좌우 대칭 처리
            left_hip_x = pose_data['left_hip_x']
            left_hip_y = pose_data['left_hip_y']
            right_hip_x = pose_data['right_hip_x']
            right_hip_y = pose_data['right_hip_y']
            
            hip_angle = abs(np.degrees(np.arctan2(
                right_hip_y - left_hip_y,
                right_hip_x - left_hip_x
            )))
            angles['hip_angle'] = hip_angle
            
            # 상체 전체 기울기: y축 차이만 고려 (수직 방향 기울기)
            hip_center_x = (left_hip_x + right_hip_x) / 2
            hip_center_y = (left_hip_y + right_hip_y) / 2
            
            y_diff = hip_center_y - shoulder_center_y
            x_diff_abs = abs(shoulder_center_x - hip_center_x)
            torso_angle = np.degrees(np.arctan2(x_diff_abs, y_diff))
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
    
    def calculate_relative_features(self, pose_data: dict) -> dict:
        """상대적 특성 계산 (거리, 비율 등) - 위치 무관"""
        features = {}
        
        try:
            # 어깨 너비
            shoulder_width = abs(pose_data['right_shoulder_x'] - pose_data['left_shoulder_x'])
            features['shoulder_width'] = shoulder_width
            
            # 엉덩이 너비
            hip_width = abs(pose_data['right_hip_x'] - pose_data['left_hip_x'])
            features['hip_width'] = hip_width
            
            # 상체 높이 (어깨 중심 - 엉덩이 중심)
            shoulder_center_y = (pose_data['left_shoulder_y'] + pose_data['right_shoulder_y']) / 2
            hip_center_y = (pose_data['left_hip_y'] + pose_data['right_hip_y']) / 2
            torso_height = abs(hip_center_y - shoulder_center_y)
            features['torso_height'] = torso_height
            
            # 목 길이 (코 - 어깨 중심)
            shoulder_center_x = (pose_data['left_shoulder_x'] + pose_data['right_shoulder_x']) / 2
            neck_length = np.sqrt(
                (pose_data['nose_x'] - shoulder_center_x)**2 +
                (pose_data['nose_y'] - shoulder_center_y)**2
            )
            features['neck_length'] = neck_length
            
            # 비율 계산
            if hip_width > 0:
                features['shoulder_hip_ratio'] = shoulder_width / hip_width
            else:
                features['shoulder_hip_ratio'] = 1.0
                
        except Exception as e:
            logging.error(f"상대적 특성 계산 실패: {e}")
            features = {
                'shoulder_width': 0.0,
                'hip_width': 0.0,
                'torso_height': 0.0,
                'neck_length': 0.0,
                'shoulder_hip_ratio': 1.0
            }
        
        return features
    
    def predict_posture(self, pose_data: dict) -> dict:
        """자세 예측 (수치 데이터만 사용)"""
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
            
            # 수치 시퀀스 생성
            num_sequence = np.array(list(self.pose_buffer))
            num_sequence_scaled = self.scaler.transform(num_sequence)
            num_sequence_input = num_sequence_scaled.reshape(1, self.sequence_length, -1)
            
            # 예측 (수치 데이터만)
            prediction_proba = self.model.predict(
                num_sequence_input, 
                verbose=0
            )[0]
            predicted_class_idx = np.argmax(prediction_proba)
            predicted_class = self.label_encoder.inverse_transform([predicted_class_idx])[0]
            confidence = prediction_proba[predicted_class_idx]
            
            # 신뢰도를 백분율로 변환 (0~100)
            confidence_percentage = float(confidence * 100)
            
            # 95 이상: Good (normal), 95 미만: Bad (abnormal)
            if confidence_percentage >= 95:
                final_class = 'normal'
            else:
                final_class = 'abnormal'
            
            return {
                'predicted_class': final_class,
                'confidence': confidence_percentage  # 백분율로 반환
            }
            
        except Exception as e:
            logging.error(f"예측 실패: {e}")
            import traceback
            traceback.print_exc()
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
        
        # 신뢰도 (백분율)
        confidence_text = f"Score: {self.confidence:.1f}%"
        cv2.putText(image, confidence_text, (20, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 상태 메시지 (95 이상 Good, 미만 Bad)
        if self.confidence >= 95:
            message = "GOOD - Excellent Posture!"
            cv2.putText(image, message, (20, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            message = "BAD - Adjust Posture!"
            cv2.putText(image, message, (20, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    def should_alert(self) -> bool:
        """알림이 필요한지 확인 (95 미만일 때)"""
        current_time = time.time()
        if (self.confidence < 95 and 
            current_time - self.last_alert_time > self.alert_interval):
            self.last_alert_time = current_time
            return True
        return False
    
    def run(self, camera_id=0, show_window=True):
        """실시간 모니터링 실행"""
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            logging.error(f"카메라를 열 수 없습니다: {camera_id}")
            return
        
        # 카메라 설정
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        logging.info("실시간 자세 모니터링 시작 (ESC키로 종료)")
        
        fps_counter = 0
        fps_start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                logging.error("프레임을 읽을 수 없습니다")
                break
            
            # 좌우 반전 (거울 효과)
            frame = cv2.flip(frame, 1)
            
            # MediaPipe 처리
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)
            
            # 포즈 특성 추출
            if results.pose_landmarks:
                pose_data = self.extract_pose_features(results.pose_landmarks, frame.shape)
                
                if pose_data:
                    # 자세 예측 (수치 데이터만)
                    prediction = self.predict_posture(pose_data)
                    self.smooth_predictions(prediction)
                    
                    # 알림 확인
                    if self.should_alert():
                        logging.info("⚠️  자세 교정이 필요합니다!")
                
                # 랜드마크 그리기
                self.draw_pose_landmarks(frame, results.pose_landmarks)
            
            # 상태 정보 표시
            self.draw_status_info(frame)
            
            # FPS 계산
            fps_counter += 1
            if fps_counter % 30 == 0:
                fps = 30 / (time.time() - fps_start_time)
                fps_start_time = time.time()
                cv2.putText(frame, f"FPS: {fps:.1f}", (frame.shape[1]-120, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # 화면 표시
            if show_window:
                cv2.imshow('Posture Monitor', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC 키
                    break
                elif key == ord('r'):  # R 키로 리셋
                    self.pose_buffer.clear()
                    self.predictions.clear()
                    self.current_posture = "Unknown"
                    self.confidence = 0.0
                    logging.info("시스템 리셋")
        
        cap.release()
        cv2.destroyAllWindows()
        logging.info("실시간 모니터링 종료")
    
    def process_frame(self, frame):
        """프레임을 받아 자세를 예측하고, 특정 스켈레톤 점만 초록색으로 그린다"""
        if self.model is None:
            return {'predicted_class': 'Loading...', 'confidence': 0.0}

        # 1. MediaPipe로 포즈 추출
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False
        results = self.pose.process(image_rgb)
        
        # 사람이 감지되지 않음
        if not results.pose_landmarks:
            return {'predicted_class': 'No Pose', 'confidence': 0.0}

        if results.pose_landmarks:
            h, w, _ = frame.shape
            landmarks = results.pose_landmarks.landmark

            # 그릴 점들의 좌표를 담을 리스트
            points_to_draw = []

            # 1) 기본 랜드마크 (정수리 대용=코, 양 어깨, 양 골반)
            # 0: 코, 11: 왼어깨, 12: 오른어깨, 23: 왼골반, 24: 오른골반
            target_indices = [0, 11, 12, 23, 24]
            for idx in target_indices:
                lm = landmarks[idx]
                # 가시성이 어느 정도 확보된 경우에만 그리기 (옵션)
                if lm.visibility > 0.5: 
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    points_to_draw.append((cx, cy))

            # 2) 허리 중간 (Mid Hip) 계산 및 추가
            # 왼쪽 골반(23)과 오른쪽 골반(24)의 중점
            try:
                l_hip = landmarks[23]
                r_hip = landmarks[24]
                if l_hip.visibility > 0.5 and r_hip.visibility > 0.5:
                    mid_hip_x = int((l_hip.x + r_hip.x) / 2 * w)
                    mid_hip_y = int((l_hip.y + r_hip.y) / 2 * h)
                    points_to_draw.append((mid_hip_x, mid_hip_y))
            except IndexError:
                pass # 랜드마크 데이터가 불완전할 경우 패스

            # 3) 점 그리기 실행
            for pt in points_to_draw:
                # cv2.circle(이미지, 중심좌표, 반지름, 색상BGR, 두께)
                # 초록색(0, 255, 0), 내부 채움(-1)
                cv2.circle(frame, pt, 6, (0, 255, 0), -1)

        # 2. 특징 추출 (이하 기존 로직 동일)
        features = self.extract_features(results.pose_landmarks.landmark)
        
        if features is None:
            return {'predicted_class': 'Error', 'confidence': 0.0}
            
        # 3. 버퍼에 추가
        self.pose_buffer.append(features)
        
        # 4. 데이터가 충분히 모였는지 확인
        if len(self.pose_buffer) < self.sequence_length:
            return {'predicted_class': 'Buffering...', 'confidence': 0.0}
            
        # 5. 예측 수행
        try:
            sequence_data = np.array(list(self.pose_buffer))
            nsamples, nfeatures = sequence_data.shape
            seq_reshaped = sequence_data.reshape(-1, nfeatures)
            seq_scaled = self.scaler.transform(seq_reshaped)
            seq_input = seq_scaled.reshape(1, nsamples, nfeatures)
            
            prediction = self.model.predict(seq_input, verbose=0)
            predicted_idx = np.argmax(prediction)
            confidence = prediction[0][predicted_idx]
            
            if self.label_encoder:
                label = self.label_encoder.inverse_transform([predicted_idx])[0]
            else:
                label = "normal" if predicted_idx == 1 else "abnormal"
            
            return {'predicted_class': label, 'confidence': float(confidence)}
            
        except Exception as e:
            return {'predicted_class': 'Error', 'confidence': 0.0}

    def extract_features(self, landmarks):
        """9가지 특징 추출 (각도 및 거리)"""
        try:
            coords = {}
            for name, idx in self.upper_body_landmarks.items():
                lm = landmarks[idx]
                coords[name] = np.array([lm.x, lm.y, lm.z])

            # 유틸리티 함수
            def calculate_angle(a, b, c):
                a = np.array(a); b = np.array(b); c = np.array(c)
                radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
                angle = np.abs(radians*180.0/np.pi)
                if angle > 180.0: angle = 360-angle
                return angle

            def calculate_distance(a, b):
                return np.linalg.norm(np.array(a) - np.array(b))

            # 좌표
            nose = coords['nose']
            l_sh = coords['left_shoulder']; r_sh = coords['right_shoulder']
            l_hip = coords['left_hip']; r_hip = coords['right_hip']
            mid_sh = (l_sh + r_sh) / 2
            mid_hip = (l_hip + r_hip) / 2
            
            # --- 9가지 특징 계산 ---
            # 1. neck_angle
            neck_angle = calculate_angle(nose, mid_sh, mid_hip)
            # 2. shoulder_angle
            shoulder_angle = calculate_angle(l_sh, mid_sh, mid_sh + np.array([1, 0, 0]))
            # 3. hip_angle
            hip_angle = calculate_angle(l_hip, mid_hip, mid_hip + np.array([1, 0, 0]))
            # 4. torso_angle
            torso_angle = calculate_angle(mid_sh, mid_hip, mid_hip + np.array([0, -1, 0]))
            # 5. shoulder_width
            shoulder_width = calculate_distance(l_sh, r_sh)
            # 6. hip_width
            hip_width = calculate_distance(l_hip, r_hip)
            # 7. torso_height
            torso_height = calculate_distance(mid_sh, mid_hip)
            # 8. neck_length
            neck_length = calculate_distance(nose, mid_sh)
            # 9. shoulder_hip_ratio
            ratio = shoulder_width / (hip_width + 1e-6)
            
            # 순서 중요 (학습 데이터와 동일해야 함)
            return [neck_angle, shoulder_angle, hip_angle, torso_angle, 
                    shoulder_width, hip_width, torso_height, neck_length, ratio]
            
        except Exception:
            return None


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