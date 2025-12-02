"""
CNN + LSTM 하이브리드 자세 평가 모델
- 이미지 특징 추출 (CNN) + 시계열 패턴 학습 (LSTM)
- 정상/비정상 자세 분류
"""

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.utils.class_weight import compute_class_weight
from pathlib import Path
import logging
import joblib
import argparse
from typing import Tuple
import os

# TensorFlow GPU 최적화
os.environ['TF_GPU_THREAD_MODE'] = 'gpu_private'
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

# TensorFlow 병렬 처리 최적화
tf.config.threading.set_inter_op_parallelism_threads(4)
tf.config.threading.set_intra_op_parallelism_threads(4)

# GPU가 있을 때만 Mixed Precision 활성화
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        from tensorflow.keras import mixed_precision
        policy = mixed_precision.Policy('mixed_float16')
        mixed_precision.set_global_policy(policy)
        logging.info("✅ Mixed Precision (FP16) 활성화")
    except:
        logging.warning("Mixed Precision을 사용할 수 없습니다")
else:
    logging.info("CPU 모드: Mixed Precision 비활성화")

# 로컬 모듈
from model_utils import (
    load_images_from_folder, create_sequences, split_and_augment_data
)
from model_builder import ModelBuilder
from model_visualizer import evaluate_model, plot_training_history

# 로깅 설정
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)


class CNNLSTMModel:
    """CNN + LSTM 하이브리드 자세 분류 모델"""
    
    def __init__(self, csv_path=None, image_dir=None, model_name='cnn_lstm',
                 img_height=112, img_width=112, sequence_length=5, dropout_rate=0.35):
        self.csv_path = csv_path
        self.image_dir = image_dir
        self.model_name = model_name
        self.img_height = img_height
        self.img_width = img_width
        self.sequence_length = sequence_length
        self.dropout_rate = dropout_rate
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_columns = None
        
    def load_data(self, csv_path: str, image_dir: str) -> Tuple:
        """CSV 데이터 및 이미지 경로 로드"""
        try:
            df = pd.read_csv(csv_path)
            logging.info(f"데이터 로드 완료: {len(df)}개 샘플")
            
            # 필수 컬럼 확인
            required_columns = ['neck_angle', 'shoulder_angle', 'hip_angle', 'torso_angle', 'label']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"필수 컬럼이 없습니다: {missing_columns}")
            
            # 특성 컬럼 정의 (절대 좌표 제거, 각도와 비율만 사용)
            self.feature_columns = [
                'neck_angle', 'shoulder_angle', 'hip_angle', 'torso_angle'
            ]
            
            # 상대적 특성 추가 (비율, 거리 등)
            relative_features = [
                'shoulder_width', 'hip_width', 'torso_height', 
                'neck_length', 'shoulder_hip_ratio'
            ]
            
            available_relative_features = [f for f in relative_features if f in df.columns]
            if available_relative_features:
                self.feature_columns.extend(available_relative_features)
                logging.info(f"상대적 특성 {len(available_relative_features)}개 추가: {available_relative_features}")
            
            logging.info(f"최종 특성: {self.feature_columns} (절대 좌표 제외)")
            
            # 결측값 및 unlabeled 제거
            df = df.dropna(subset=self.feature_columns + ['label'])
            logging.info(f"결측값 제거 후: {len(df)}개 샘플")
            
            if 'unlabeled' in df['label'].values:
                df = df[df['label'] != 'unlabeled']
                logging.info(f"unlabeled 제거 후: {len(df)}개 샘플")
            
            label_counts = df['label'].value_counts()
            logging.info(f"라벨 분포: {dict(label_counts)}")
            
            return df, image_dir
            
        except Exception as e:
            logging.error(f"데이터 로드 실패: {e}")
            raise
    
    def prepare_data(self, df: pd.DataFrame, image_dir: str, augment: bool = True) -> Tuple:
        """데이터 전처리 및 준비 (수치 데이터만 사용)"""
        X_numeric = df[self.feature_columns].values
        y = df['label'].values
        
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        
        self.scaler = StandardScaler()
        X_numeric_scaled = self.scaler.fit_transform(X_numeric)
        
        # 시퀀스 생성 (이미지 없이 수치 데이터만)
        X_num_seq, y_seq = self.create_numeric_sequences(
            X_numeric_scaled, y_encoded, self.sequence_length
        )
        
        if len(X_num_seq) == 0:
            raise ValueError("시퀀스를 생성할 수 없습니다.")
        
        # 데이터 분할 및 증강 (수치 데이터만)
        return self.split_and_augment_numeric_data(X_num_seq, y_seq, augment)
    
    def create_numeric_sequences(self, numeric_data: np.ndarray, 
                                labels: np.ndarray, 
                                sequence_length: int) -> Tuple:
        """수치 데이터 시퀀스 생성"""
        num_sequences = []
        seq_labels = []
        
        unique_labels = np.unique(labels)
        
        logging.info(f"시퀀스 생성 시작 (sequence_length={sequence_length})")
        
        for label in unique_labels:
            label_indices = np.where(labels == label)[0]
            
            if len(label_indices) < sequence_length:
                logging.warning(
                    f"라벨 '{label}'의 데이터가 부족합니다: "
                    f"{len(label_indices)}개 < {sequence_length}개"
                )
                continue
            
            for i in range(len(label_indices) - sequence_length + 1):
                indices = label_indices[i:i + sequence_length]
                num_sequences.append(numeric_data[indices])
                seq_labels.append(labels[indices[-1]])
        
        if len(num_sequences) == 0:
            raise ValueError(
                f"시퀀스를 생성할 수 없습니다. "
                f"각 라벨당 최소 {sequence_length}개의 데이터가 필요합니다."
            )
        
        num_sequences = np.array(num_sequences)
        seq_labels = np.array(seq_labels)
        
        logging.info(
            f"시퀀스 생성 완료: {len(num_sequences)}개 "
            f"(라벨: {dict(zip(*np.unique(seq_labels, return_counts=True)))})"
        )
        
        return num_sequences, seq_labels
    
    def split_and_augment_numeric_data(self, X_num, y, augment: bool):
        """수치 데이터 분할 및 증강"""
        from sklearn.model_selection import train_test_split
        
        # Train/Test 분할 (85/15)
        X_num_temp, X_num_test, y_temp, y_test = train_test_split(
            X_num, y, test_size=0.15, random_state=42, stratify=y
        )
        
        # Train/Val 분할 (70/15)
        X_num_train, X_num_val, y_train, y_val = train_test_split(
            X_num_temp, y_temp, test_size=0.18, random_state=42, stratify=y_temp
        )
        
        original_train_count = len(X_num_train)
        
        logging.info(f"="*60)
        logging.info(f"원본 데이터 분할 - 훈련: {len(X_num_train)}, 검증: {len(X_num_val)}, 테스트: {len(X_num_test)}")
        logging.info(f"="*60)
        
        # 훈련 데이터 증강 (수치 데이터)
        if augment and len(X_num_train) > 0:
            aug_factor = 1.5
            logging.info(f"📈 수치 데이터를 {aug_factor}배 증강합니다.")
            
            X_num_train, y_train = self.augment_numeric_data(
                X_num_train, y_train, aug_factor
            )
        
        augmented_train_count = len(X_num_train)
        
        if augment and augmented_train_count > original_train_count:
            increase_count = augmented_train_count - original_train_count
            increase_percent = (increase_count / original_train_count) * 100
            
            logging.info(f"="*60)
            logging.info(f"✅ 데이터 증강 완료!")
            logging.info(f"원본 훈련 데이터: {original_train_count}개")
            logging.info(f"증강 후 훈련 데이터: {augmented_train_count}개")
            logging.info(f"증가량: +{increase_count}개 ({increase_percent:.1f}% 증가)")
            logging.info(f"="*60)
        
        total = len(X_num_train) + len(X_num_val) + len(X_num_test)
        logging.info(
            f"최종 분포 - 훈련: {len(X_num_train)} ({len(X_num_train)/total*100:.1f}%), "
            f"검증: {len(X_num_val)} ({len(X_num_val)/total*100:.1f}%), "
            f"테스트: {len(X_num_test)} ({len(X_num_test)/total*100:.1f}%)"
        )
        
        return (X_num_train, y_train,
                X_num_val, y_val,
                X_num_test, y_test)
    
    def augment_numeric_data(self, X_num, y, factor=1.5):
        """수치 데이터 증강 (노이즈 추가)"""
        aug_X = [X_num]
        aug_y = [y]
        
        num_augmentations = int(factor) if factor >= 1 else 0
        extra_augment_prob = factor - int(factor)
        
        for _ in range(num_augmentations):
            # 가우시안 노이즈 추가
            noise = np.random.normal(0, 0.01, X_num.shape)
            X_augmented = X_num + noise
            X_augmented = np.clip(X_augmented, -10, 10)
            
            aug_X.append(X_augmented)
            aug_y.append(y)
        
        # 추가 증강 (확률적)
        if extra_augment_prob > 0:
            num_extra = int(len(X_num) * extra_augment_prob)
            indices = np.random.choice(len(X_num), num_extra, replace=False)
            
            noise = np.random.normal(0, 0.01, (num_extra, X_num.shape[1], X_num.shape[2]))
            X_extra = X_num[indices] + noise
            X_extra = np.clip(X_extra, -10, 10)
            
            aug_X.append(X_extra)
            aug_y.append(y[indices])
        
        return np.vstack(aug_X), np.hstack(aug_y)
    
    def build_model(self, num_numeric_features: int, num_classes: int):
        """모델 구성 (수치 데이터만 사용)"""
        builder = ModelBuilder(
            self.img_height, self.img_width, 
            self.sequence_length, self.dropout_rate
        )
        self.model = builder.build_numeric_only(num_numeric_features, num_classes)
        return self.model
    
    def train(self, X_num_train, y_train,
              X_num_val, y_val,
              epochs=100, batch_size=8):
        """모델 훈련 (수치 데이터만)"""
        if self.model is None:
            raise ValueError("모델이 구성되지 않았습니다.")
        
        # 클래스 가중치
        class_weights = compute_class_weight(
            'balanced',
            classes=np.unique(y_train),
            y=y_train
        )
        class_weights = np.clip(class_weights, 0.6, 2.5)
        class_weight_dict = dict(enumerate(class_weights))
        
        logging.info(f"클래스 가중치: {class_weight_dict}")
        
        # 배치 크기 자동 최적화 (메모리 효율)
        optimal_batch_size = self._optimize_batch_size(batch_size, len(X_num_train))
        logging.info(f"최적화된 배치 크기: {optimal_batch_size}")
        
        callbacks = [
            EarlyStopping(
                monitor='val_loss', 
                patience=7,
                restore_best_weights=True,
                min_delta=0.001,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss', 
                factor=0.5,
                patience=3,
                min_lr=1e-7,
                min_delta=0.001,
                verbose=1
            ),
            ModelCheckpoint(
                'models/best_cnn_lstm_model.h5',
                save_best_only=True,
                monitor='val_accuracy',
                verbose=1
            )
        ]
        
        # TensorFlow Dataset으로 변환
        train_dataset = tf.data.Dataset.from_tensor_slices(
            (X_num_train, y_train)
        )
        train_dataset = train_dataset.cache()
        train_dataset = train_dataset.shuffle(buffer_size=1000)
        train_dataset = train_dataset.batch(optimal_batch_size)
        train_dataset = train_dataset.prefetch(tf.data.AUTOTUNE)
        
        val_dataset = tf.data.Dataset.from_tensor_slices(
            (X_num_val, y_val)
        )
        val_dataset = val_dataset.cache()
        val_dataset = val_dataset.batch(optimal_batch_size)
        val_dataset = val_dataset.prefetch(tf.data.AUTOTUNE)
        
        history = self.model.fit(
            train_dataset,
            validation_data=val_dataset,
            epochs=epochs,
            class_weight=class_weight_dict,
            callbacks=callbacks,
            verbose=1
        )
        
        return history
    
    def _optimize_batch_size(self, requested_batch_size, dataset_size):
        """메모리 기반 배치 크기 최적화"""
        # GPU 메모리 확인
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            # GPU 사용 시 더 큰 배치 (속도 향상)
            optimal = min(requested_batch_size * 2, 64)  # 최대 64
        else:
            # CPU 사용 시 큰 배치로 속도 향상
            optimal = min(requested_batch_size, 32)  # 최대 32
        
        # 데이터셋 크기에 맞춰 조정
        return min(optimal, max(8, dataset_size // 5))  # 최소 8
    
    def evaluate(self, X_num, y, dataset_name="Test"):
        """모델 평가 (수치 데이터만)"""
        if self.model is None:
            raise ValueError("훈련된 모델이 없습니다.")
        
        from model_visualizer import evaluate_model_numeric_only
        return evaluate_model_numeric_only(
            self.model, X_num, y, 
            self.label_encoder, dataset_name
        )
    
    def save_model(self, model_path: str = 'models/cnn_lstm_model.h5'):
        """모델 및 전처리 객체 저장"""
        if self.model is None:
            raise ValueError("저장할 모델이 없습니다.")
        
        self.model.save(model_path)
        joblib.dump(self.scaler, 'models/scaler_cnn_lstm.pkl')
        joblib.dump(self.label_encoder, 'models/label_encoder_cnn_lstm.pkl')
        
        metadata = {
            'img_height': self.img_height,
            'img_width': self.img_width,
            'sequence_length': self.sequence_length,
            'dropout_rate': self.dropout_rate,
            'feature_columns': self.feature_columns,
            'classes': self.label_encoder.classes_.tolist()
        }
        
        import json
        with open('models/model_metadata_cnn_lstm.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logging.info(f"모델 저장 완료: {model_path}")


def main():
    parser = argparse.ArgumentParser(description='CNN + LSTM 자세 분류 모델 훈련')
    parser.add_argument('--data', default='data/pose_data.csv',
                       help='훈련 데이터 CSV 파일 경로')
    parser.add_argument('--images', default='data/train_images',
                       help='이미지 폴더 경로')
    parser.add_argument('--epochs', type=int, default=100,
                       help='훈련 에폭 수 (기본: 100)')
    parser.add_argument('--batch_size', type=int, default=16,
                       help='배치 크기 (기본: 16)')
    parser.add_argument('--img_size', type=int, default=112,
                       help='이미지 크기')
    parser.add_argument('--sequence_length', type=int, default=5,
                       help='LSTM 시퀀스 길이')
    parser.add_argument('--no_augment', action='store_true',
                       help='데이터 증강 사용 안 함')
    
    args = parser.parse_args()
    
    Path('models').mkdir(exist_ok=True)
    
    model = CNNLSTMModel(
        csv_path=args.data,
        image_dir=args.images,
        model_name='cnn_lstm',
        img_height=args.img_size,
        img_width=args.img_size,
        sequence_length=args.sequence_length,
        dropout_rate=0.35  # 기존 dropout 값
    )
    
    try:
        logging.info("데이터 로드 중...")
        df, image_dir = model.load_data(args.data, args.images)
        
        logging.info("데이터 전처리 중...")
        (X_num_train, y_train,
         X_num_val, y_val,
         X_num_test, y_test) = model.prepare_data(
            df, image_dir, augment=not args.no_augment
        )
        
        if len(X_num_train) == 0:
            logging.error("훈련 데이터가 없습니다.")
            return
        
        logging.info("모델 구성 중...")
        num_classes = len(model.label_encoder.classes_)
        num_numeric_features = len(model.feature_columns)
        
        model.build_model(num_numeric_features, num_classes)
        
        logging.info("모델 훈련 시작...")
        history = model.train(
            X_num_train, y_train,
            X_num_val, y_val,
            epochs=args.epochs,
            batch_size=args.batch_size
        )
        
        plot_training_history(history)
        
        # 평가
        logging.info("훈련 세트 평가...")
        train_accuracy, _, _, train_metrics = model.evaluate(
            X_num_train, y_train, "Train"
        )
        
        logging.info("검증 세트 평가...")
        val_accuracy, _, _, val_metrics = model.evaluate(
            X_num_val, y_val, "Validation"
        )
        
        logging.info("테스트 세트 평가...")
        test_accuracy, _, _, test_metrics = model.evaluate(
            X_num_test, y_test, "Test"
        )
        
        logging.info("모델 저장 중...")
        model.save_model()
        
        # 최종 결과 요약
        logging.info("\n" + "="*70)
        logging.info("CNN + LSTM 모델 훈련 완료!")
        logging.info("="*70)
        
        logging.info("\n[훈련 세트] 정확도: {:.4f} ({:.2f}%)".format(
            train_accuracy, train_accuracy*100))
        logging.info("[검증 세트] 정확도: {:.4f} ({:.2f}%)".format(
            val_accuracy, val_accuracy*100))
        logging.info("[테스트 세트] 정확도: {:.4f} ({:.2f}%) ⭐".format(
            test_accuracy, test_accuracy*100))
        
        # 과적합 검사
        overfitting_gap = train_accuracy - val_accuracy
        if overfitting_gap > 0.1:
            logging.warning(f"\n⚠️  과적합 가능성: {overfitting_gap:.4f}")
        else:
            logging.info(f"\n✅ 좋은 일반화 성능: {overfitting_gap:.4f}")
        
        logging.info("\n" + "="*70)
        
    except Exception as e:
        logging.error(f"훈련 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    main()
