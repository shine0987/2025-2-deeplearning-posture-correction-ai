"""
2단계: LSTM 평가 모델
- CSV 데이터를 입력으로 받는 LSTM 모델
- 정상/비정상 자세 분류 모델 구현
"""

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
import joblib
import argparse

# 로깅 설정
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

class PostureLSTMModel:
    def __init__(self, sequence_length=10, lstm_units=128, dropout_rate=0.3):
        """
        자세 분류를 위한 LSTM 모델
        
        Args:
            sequence_length: 시퀀스 길이 (시간 단계)
            lstm_units: LSTM 유닛 수
            dropout_rate: 드롭아웃 비율
        """
        self.sequence_length = sequence_length
        self.lstm_units = lstm_units
        self.dropout_rate = dropout_rate
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_columns = None
        
    def load_data(self, csv_path: str) -> tuple:
        """CSV 데이터 로드 및 전처리"""
        try:
            df = pd.read_csv(csv_path)
            logging.info(f"데이터 로드 완료: {len(df)}개 샘플")
            
            # 필요한 컬럼 확인
            required_columns = ['neck_angle', 'shoulder_angle', 'hip_angle', 'torso_angle', 'label']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"필수 컬럼이 없습니다: {missing_columns}")
            
            # 특성 컬럼 정의
            self.feature_columns = [
                'neck_angle', 'shoulder_angle', 'hip_angle', 'torso_angle'
            ]
            
            # 좌표 특성 추가 (있는 경우)
            coordinate_features = []
            for body_part in ['nose', 'left_shoulder', 'right_shoulder', 'left_hip', 'right_hip']:
                for coord in ['x', 'y']:
                    col_name = f'{body_part}_{coord}'
                    if col_name in df.columns:
                        coordinate_features.append(col_name)
            
            if coordinate_features:
                self.feature_columns.extend(coordinate_features)
                logging.info(f"좌표 특성 {len(coordinate_features)}개 추가")
            
            # 결측값 처리
            df = df.dropna(subset=self.feature_columns + ['label'])
            logging.info(f"결측값 제거 후: {len(df)}개 샘플")
            
            # 라벨 분포 확인
            label_counts = df['label'].value_counts()
            logging.info(f"라벨 분포: {dict(label_counts)}")
            
            # 'unlabeled' 제거
            if 'unlabeled' in df['label'].values:
                df = df[df['label'] != 'unlabeled']
                logging.info(f"unlabeled 제거 후: {len(df)}개 샘플")
            
            return df
            
        except Exception as e:
            logging.error(f"데이터 로드 실패: {e}")
            raise
    
    def create_sequences(self, data: np.ndarray, labels: np.ndarray) -> tuple:
        """시퀀스 데이터 생성"""
        sequences = []
        sequence_labels = []
        
        # 라벨별로 그룹화
        unique_labels = np.unique(labels)
        
        for label in unique_labels:
            label_indices = np.where(labels == label)[0]
            label_data = data[label_indices]
            
            # 시퀀스 생성
            for i in range(len(label_data) - self.sequence_length + 1):
                sequence = label_data[i:i + self.sequence_length]
                sequences.append(sequence)
                sequence_labels.append(label)
        
        sequences = np.array(sequences)
        sequence_labels = np.array(sequence_labels)
        
        logging.info(f"시퀀스 생성 완료: {len(sequences)}개 시퀀스")
        return sequences, sequence_labels
    
    def augment_data(self, data: np.ndarray, labels: np.ndarray, augment_factor: int = 3) -> tuple:
        """데이터 증강"""
        augmented_data = []
        augmented_labels = []
        
        for i in range(len(data)):
            # 원본 데이터
            augmented_data.append(data[i])
            augmented_labels.append(labels[i])
            
            # 증강 데이터 생성
            for _ in range(augment_factor):
                # 노이즈 추가
                noise = np.random.normal(0, 0.02, data[i].shape)
                augmented_sample = data[i] + noise
                
                # 약간의 스케일링
                scale_factor = np.random.uniform(0.98, 1.02)
                augmented_sample *= scale_factor
                
                augmented_data.append(augmented_sample)
                augmented_labels.append(labels[i])
        
        augmented_data = np.array(augmented_data)
        augmented_labels = np.array(augmented_labels)
        
        logging.info(f"데이터 증강 완료: {len(augmented_data)}개 샘플")
        return augmented_data, augmented_labels
    
    def prepare_data(self, df: pd.DataFrame, augment: bool = True) -> tuple:
        """데이터 전처리 및 준비"""
        # 특성과 라벨 분리
        X = df[self.feature_columns].values
        y = df['label'].values
        
        # 라벨 인코딩
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        
        # 데이터 정규화
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # 시퀀스 생성
        X_sequences, y_sequences = self.create_sequences(X_scaled, y_encoded)
        
        # 데이터 증강
        if augment and len(X_sequences) > 0:
            X_sequences, y_sequences = self.augment_data(X_sequences, y_sequences)
        
        # 훈련/테스트 분할
        X_train, X_test, y_train, y_test = train_test_split(
            X_sequences, y_sequences, test_size=0.2, random_state=42, stratify=y_sequences
        )
        
        logging.info(f"훈련 데이터: {len(X_train)}개, 테스트 데이터: {len(X_test)}개")
        
        return X_train, X_test, y_train, y_test
    
    def build_model(self, input_shape: tuple, num_classes: int):
        """LSTM 모델 구성"""
        self.model = Sequential([
            # 첫 번째 LSTM 레이어
            LSTM(self.lstm_units, 
                 return_sequences=True, 
                 input_shape=input_shape,
                 dropout=self.dropout_rate,
                 recurrent_dropout=self.dropout_rate),
            BatchNormalization(),
            
            # 두 번째 LSTM 레이어
            LSTM(self.lstm_units // 2,
                 return_sequences=False,
                 dropout=self.dropout_rate,
                 recurrent_dropout=self.dropout_rate),
            BatchNormalization(),
            
            # 완전연결 레이어
            Dense(64, activation='relu'),
            Dropout(self.dropout_rate),
            
            Dense(32, activation='relu'),
            Dropout(self.dropout_rate),
            
            # 출력 레이어
            Dense(num_classes, activation='softmax' if num_classes > 2 else 'sigmoid')
        ])
        
        # 모델 컴파일
        optimizer = Adam(learning_rate=0.001)
        if num_classes > 2:
            loss = 'sparse_categorical_crossentropy'
        else:
            loss = 'sparse_categorical_crossentropy'  # 이진 분류도 sparse_categorical_crossentropy 사용
        metrics = ['accuracy']
        
        self.model.compile(optimizer=optimizer, loss=loss, metrics=metrics)
        
        # 모델 요약
        self.model.summary()
        
        return self.model
    
    def train(self, X_train, X_test, y_train, y_test, epochs=100, batch_size=32):
        """모델 훈련"""
        if self.model is None:
            raise ValueError("모델이 구성되지 않았습니다. build_model()을 먼저 호출하세요.")
        
        # 콜백 설정
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True),
            ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=10, min_lr=1e-7),
            ModelCheckpoint('models/best_lstm_model.h5', save_best_only=True, monitor='val_accuracy')
        ]
        
        # 모델 훈련
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        return history
    
    def evaluate(self, X_test, y_test):
        """모델 평가"""
        if self.model is None:
            raise ValueError("훈련된 모델이 없습니다.")
        
        # 예측
        y_pred_proba = self.model.predict(X_test)
        y_pred = np.argmax(y_pred_proba, axis=1)
        
        # 평가 메트릭
        accuracy = accuracy_score(y_test, y_pred)
        
        logging.info(f"테스트 정확도: {accuracy:.4f}")
        
        # 분류 보고서
        class_names = self.label_encoder.classes_
        report = classification_report(y_test, y_pred, target_names=class_names)
        logging.info(f"분류 보고서:\\n{report}")
        
        # 혼동 행렬
        cm = confusion_matrix(y_test, y_pred)
        
        # 혼동 행렬 시각화
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=class_names, yticklabels=class_names)
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig('models/confusion_matrix.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return accuracy, report, cm
    
    def plot_training_history(self, history):
        """훈련 히스토리 시각화"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        # 정확도
        ax1.plot(history.history['accuracy'], label='Training Accuracy')
        ax1.plot(history.history['val_accuracy'], label='Validation Accuracy')
        ax1.set_title('Model Accuracy')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Accuracy')
        ax1.legend()
        ax1.grid(True)
        
        # 손실
        ax2.plot(history.history['loss'], label='Training Loss')
        ax2.plot(history.history['val_loss'], label='Validation Loss')
        ax2.set_title('Model Loss')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Loss')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig('models/training_history.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def save_model(self, model_path: str = 'models/posture_lstm_model.h5'):
        """모델 저장"""
        if self.model is None:
            raise ValueError("저장할 모델이 없습니다.")
        
        # 모델 저장
        self.model.save(model_path)
        
        # 스케일러와 라벨 인코더 저장
        joblib.dump(self.scaler, 'models/scaler.pkl')
        joblib.dump(self.label_encoder, 'models/label_encoder.pkl')
        
        # 메타데이터 저장
        metadata = {
            'sequence_length': self.sequence_length,
            'lstm_units': self.lstm_units,
            'dropout_rate': self.dropout_rate,
            'feature_columns': self.feature_columns,
            'classes': self.label_encoder.classes_.tolist()
        }
        
        import json
        with open('models/model_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logging.info(f"모델 저장 완료: {model_path}")
    
    def load_model(self, model_path: str = 'models/posture_lstm_model.h5'):
        """저장된 모델 로드"""
        self.model = tf.keras.models.load_model(model_path)
        self.scaler = joblib.load('models/scaler.pkl')
        self.label_encoder = joblib.load('models/label_encoder.pkl')
        
        # 메타데이터 로드
        import json
        with open('models/model_metadata.json', 'r') as f:
            metadata = json.load(f)
        
        self.sequence_length = metadata['sequence_length']
        self.lstm_units = metadata['lstm_units']
        self.dropout_rate = metadata['dropout_rate']
        self.feature_columns = metadata['feature_columns']
        
        logging.info("모델 로드 완료")
    
    def predict_posture(self, pose_data: np.ndarray) -> dict:
        """단일 자세 데이터 예측"""
        if self.model is None:
            raise ValueError("로드된 모델이 없습니다.")
        
        # 데이터 전처리
        if len(pose_data.shape) == 1:
            pose_data = pose_data.reshape(1, -1)
        
        pose_data_scaled = self.scaler.transform(pose_data)
        
        # 시퀀스 생성 (단일 예측용)
        if len(pose_data_scaled) < self.sequence_length:
            # 데이터가 시퀀스 길이보다 짧으면 패딩
            padding = np.repeat(pose_data_scaled[0:1], 
                              self.sequence_length - len(pose_data_scaled), axis=0)
            pose_data_scaled = np.vstack([padding, pose_data_scaled])
        
        sequence = pose_data_scaled[-self.sequence_length:].reshape(1, self.sequence_length, -1)
        
        # 예측
        prediction_proba = self.model.predict(sequence, verbose=0)[0]
        predicted_class_idx = np.argmax(prediction_proba)
        predicted_class = self.label_encoder.inverse_transform([predicted_class_idx])[0]
        confidence = prediction_proba[predicted_class_idx]
        
        return {
            'predicted_class': predicted_class,
            'confidence': float(confidence),
            'probabilities': {
                class_name: float(prob) 
                for class_name, prob in zip(self.label_encoder.classes_, prediction_proba)
            }
        }


def main():
    parser = argparse.ArgumentParser(description='LSTM 자세 분류 모델 훈련')
    parser.add_argument('--data', default='data/pose_data.csv', 
                       help='훈련 데이터 CSV 파일 경로')
    parser.add_argument('--epochs', type=int, default=100, 
                       help='훈련 에폭 수')
    parser.add_argument('--batch_size', type=int, default=32, 
                       help='배치 크기')
    parser.add_argument('--sequence_length', type=int, default=10, 
                       help='LSTM 시퀀스 길이')
    parser.add_argument('--lstm_units', type=int, default=128, 
                       help='LSTM 유닛 수')
    parser.add_argument('--no_augment', action='store_true', 
                       help='데이터 증강 사용 안 함')
    
    args = parser.parse_args()
    
    # 모델 저장 폴더 생성
    Path('models').mkdir(exist_ok=True)
    
    # LSTM 모델 초기화
    lstm_model = PostureLSTMModel(
        sequence_length=args.sequence_length,
        lstm_units=args.lstm_units
    )
    
    try:
        # 데이터 로드
        logging.info("데이터 로드 중...")
        df = lstm_model.load_data(args.data)
        
        # 데이터 전처리
        logging.info("데이터 전처리 중...")
        X_train, X_test, y_train, y_test = lstm_model.prepare_data(
            df, augment=not args.no_augment
        )
        
        if len(X_train) == 0:
            logging.error("훈련 데이터가 없습니다. 데이터를 확인하세요.")
            return
        
        # 모델 구성
        logging.info("모델 구성 중...")
        num_classes = len(lstm_model.label_encoder.classes_)
        input_shape = (args.sequence_length, len(lstm_model.feature_columns))
        
        lstm_model.build_model(input_shape, num_classes)
        
        # 모델 훈련
        logging.info("모델 훈련 시작...")
        history = lstm_model.train(
            X_train, X_test, y_train, y_test,
            epochs=args.epochs,
            batch_size=args.batch_size
        )
        
        # 훈련 히스토리 시각화
        lstm_model.plot_training_history(history)
        
        # 모델 평가
        logging.info("모델 평가 중...")
        accuracy, report, cm = lstm_model.evaluate(X_test, y_test)
        
        # 모델 저장
        logging.info("모델 저장 중...")
        lstm_model.save_model()
        
        logging.info("LSTM 모델 훈련 완료!")
        
    except Exception as e:
        logging.error(f"훈련 중 오류 발생: {e}")
        raise


if __name__ == '__main__':
    main()