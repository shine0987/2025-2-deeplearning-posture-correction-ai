"""
CNN + LSTM 하이브리드 자세 평가 모델
- 이미지 특징 추출 (CNN) + 시계열 패턴 학습 (LSTM)
- 정상/비정상 자세 분류
"""

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    Input, Conv2D, MaxPooling2D, Dense, Dropout, 
    BatchNormalization, concatenate, GlobalAveragePooling2D,
    LSTM, TimeDistributed, Reshape, Flatten
)
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.utils.class_weight import compute_class_weight
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
import joblib
import argparse
import cv2
from typing import Tuple, List

# 로깅 설정
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

class CNNLSTMModel:
    def __init__(self, img_height=128, img_width=128, sequence_length=5, dropout_rate=0.3):
        """
        CNN + LSTM 하이브리드 자세 분류 모델
        
        Args:
            img_height: 이미지 높이
            img_width: 이미지 너비
            sequence_length: LSTM 시퀀스 길이
            dropout_rate: 드롭아웃 비율
        """
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
            
            # 특성 컬럼 정의
            self.feature_columns = [
                'neck_angle', 'shoulder_angle', 'hip_angle', 'torso_angle'
            ]
            
            # 좌표 특성 추가
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
            
            # 'unlabeled' 제거
            if 'unlabeled' in df['label'].values:
                df = df[df['label'] != 'unlabeled']
                logging.info(f"unlabeled 제거 후: {len(df)}개 샘플")
            
            # 라벨 분포 확인
            label_counts = df['label'].value_counts()
            logging.info(f"라벨 분포: {dict(label_counts)}")
            
            return df, image_dir
            
        except Exception as e:
            logging.error(f"데이터 로드 실패: {e}")
            raise
    
    def load_images_from_folder(self, image_dir: str, labels: np.ndarray) -> Tuple:
        """폴더에서 이미지 로드"""
        image_path = Path(image_dir)
        images = []
        valid_indices = []
        
        for idx, label in enumerate(labels):
            label_folder = image_path / label
            if not label_folder.exists():
                logging.warning(f"폴더가 없습니다: {label_folder}")
                continue
            
            img_files = list(label_folder.glob('*.jpg')) + \
                       list(label_folder.glob('*.png')) + \
                       list(label_folder.glob('*.jpeg'))
            
            if img_files:
                img_path = img_files[min(idx % len(img_files), len(img_files)-1)]
                img = cv2.imread(str(img_path))
                if img is not None:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img = cv2.resize(img, (self.img_width, self.img_height))
                    images.append(img)
                    valid_indices.append(idx)
        
        if len(images) == 0:
            raise ValueError("이미지를 로드할 수 없습니다. 이미지 폴더를 확인하세요.")
        
        images = np.array(images, dtype=np.float32) / 255.0
        logging.info(f"이미지 로드 완료: {len(images)}개")
        
        return images, valid_indices
    
    def create_sequences(self, images: np.ndarray, numeric_data: np.ndarray, 
                        labels: np.ndarray) -> Tuple:
        """시퀀스 데이터 생성"""
        img_sequences = []
        num_sequences = []
        seq_labels = []
        
        # 라벨별로 시퀀스 생성
        unique_labels = np.unique(labels)
        
        for label in unique_labels:
            label_indices = np.where(labels == label)[0]
            
            for i in range(len(label_indices) - self.sequence_length + 1):
                indices = label_indices[i:i + self.sequence_length]
                img_sequences.append(images[indices])
                num_sequences.append(numeric_data[indices])
                seq_labels.append(label)
        
        img_sequences = np.array(img_sequences)
        num_sequences = np.array(num_sequences)
        seq_labels = np.array(seq_labels)
        
        logging.info(f"시퀀스 생성 완료: {len(img_sequences)}개")
        
        return img_sequences, num_sequences, seq_labels
    
    def augment_data(self, img_seqs: np.ndarray, num_seqs: np.ndarray, 
                    labels: np.ndarray, augment_factor: int = 2) -> Tuple:
        """데이터 증강"""
        aug_img_seqs = []
        aug_num_seqs = []
        aug_labels = []
        
        datagen = ImageDataGenerator(
            rotation_range=8,
            width_shift_range=0.08,
            height_shift_range=0.08,
            zoom_range=0.08,
            fill_mode='nearest'
        )
        
        for i in range(len(img_seqs)):
            # 원본
            aug_img_seqs.append(img_seqs[i])
            aug_num_seqs.append(num_seqs[i])
            aug_labels.append(labels[i])
            
            # 증강
            for _ in range(augment_factor):
                aug_img_seq = []
                for frame in img_seqs[i]:
                    img = frame.reshape((1,) + frame.shape)
                    aug_img = datagen.flow(img, batch_size=1)[0][0]
                    aug_img_seq.append(aug_img)
                
                aug_img_seqs.append(np.array(aug_img_seq))
                
                noise = np.random.normal(0, 0.01, num_seqs[i].shape)
                aug_num_seqs.append(num_seqs[i] + noise)
                aug_labels.append(labels[i])
        
        aug_img_seqs = np.array(aug_img_seqs)
        aug_num_seqs = np.array(aug_num_seqs)
        aug_labels = np.array(aug_labels)
        
        logging.info(f"데이터 증강 완료: {len(aug_img_seqs)}개")
        
        return aug_img_seqs, aug_num_seqs, aug_labels
    
    def prepare_data(self, df: pd.DataFrame, image_dir: str, 
                    augment: bool = True) -> Tuple:
        """데이터 전처리 및 준비"""
        X_numeric = df[self.feature_columns].values
        y = df['label'].values
        
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        
        X_images, valid_indices = self.load_images_from_folder(image_dir, y)
        
        X_numeric = X_numeric[valid_indices]
        y_encoded = y_encoded[valid_indices]
        
        self.scaler = StandardScaler()
        X_numeric_scaled = self.scaler.fit_transform(X_numeric)
        
        # 시퀀스 생성
        X_img_seq, X_num_seq, y_seq = self.create_sequences(
            X_images, X_numeric_scaled, y_encoded
        )
        
        if len(X_img_seq) == 0:
            raise ValueError("시퀀스를 생성할 수 없습니다.")
        
        # 분할 (70/20/10)
        X_img_temp, X_img_test, X_num_temp, X_num_test, y_temp, y_test = train_test_split(
            X_img_seq, X_num_seq, y_seq, 
            test_size=0.15, random_state=42, stratify=y_seq
        )
        
        X_img_train, X_img_val, X_num_train, X_num_val, y_train, y_val = train_test_split(
            X_img_temp, X_num_temp, y_temp,
            test_size=0.18, random_state=42, stratify=y_temp
        )
        
        logging.info(f"분할 후 - 훈련: {len(X_img_train)}, 검증: {len(X_img_val)}, 테스트: {len(X_img_test)}")
        
        # 훈련 세트만 증강
        if augment and len(X_img_train) > 0:
            X_img_train, X_num_train, y_train = self.augment_data(
                X_img_train, X_num_train, y_train, augment_factor=2
            )
        
        total = len(X_img_train) + len(X_img_val) + len(X_img_test)
        logging.info(f"최종 데이터 분포:")
        logging.info(f"  훈련: {len(X_img_train)}개 ({len(X_img_train)/total*100:.1f}%)")
        logging.info(f"  검증: {len(X_img_val)}개 ({len(X_img_val)/total*100:.1f}%)")
        logging.info(f"  테스트: {len(X_img_test)}개 ({len(X_img_test)/total*100:.1f}%)")
        
        return (X_img_train, X_num_train, y_train,
                X_img_val, X_num_val, y_val,
                X_img_test, X_num_test, y_test)
    
    def build_model(self, num_numeric_features: int, num_classes: int):
        """CNN + LSTM 하이브리드 모델 구성"""
        
        # === 이미지 시퀀스 브랜치 (CNN + LSTM) ===
        image_input = Input(shape=(self.sequence_length, self.img_height, self.img_width, 3), 
                           name='image_input')
        
        # TimeDistributed CNN으로 각 프레임 처리
        x = TimeDistributed(Conv2D(32, (3, 3), activation='relu', padding='same'))(image_input)
        x = TimeDistributed(BatchNormalization())(x)
        x = TimeDistributed(MaxPooling2D((2, 2)))(x)
        x = TimeDistributed(Dropout(self.dropout_rate * 0.5))(x)
        
        x = TimeDistributed(Conv2D(64, (3, 3), activation='relu', padding='same'))(x)
        x = TimeDistributed(BatchNormalization())(x)
        x = TimeDistributed(MaxPooling2D((2, 2)))(x)
        x = TimeDistributed(Dropout(self.dropout_rate * 0.5))(x)
        
        x = TimeDistributed(Conv2D(128, (3, 3), activation='relu', padding='same'))(x)
        x = TimeDistributed(BatchNormalization())(x)
        x = TimeDistributed(GlobalAveragePooling2D())(x)
        
        # LSTM으로 시간적 패턴 학습
        x = LSTM(64, return_sequences=True, dropout=self.dropout_rate)(x)
        x = BatchNormalization()(x)
        x = LSTM(32, dropout=self.dropout_rate)(x)
        x = BatchNormalization()(x)
        image_features = Dense(32, activation='relu', name='image_features')(x)
        
        # === 수치 시퀀스 브랜치 (LSTM) ===
        numeric_input = Input(shape=(self.sequence_length, num_numeric_features), 
                             name='numeric_input')
        
        y = LSTM(32, return_sequences=True, dropout=self.dropout_rate)(numeric_input)
        y = BatchNormalization()(y)
        y = LSTM(16, dropout=self.dropout_rate)(y)
        y = BatchNormalization()(y)
        numeric_features = Dense(16, activation='relu', name='numeric_features')(y)
        
        # === 융합 ===
        merged = concatenate([image_features, numeric_features], name='fusion')
        
        z = Dense(32, activation='relu')(merged)
        z = BatchNormalization()(z)
        z = Dropout(self.dropout_rate)(z)
        
        z = Dense(16, activation='relu')(z)
        z = Dropout(self.dropout_rate)(z)
        
        output = Dense(num_classes, activation='softmax', name='output')(z)
        
        self.model = Model(
            inputs=[image_input, numeric_input],
            outputs=output,
            name='CNN_LSTM_Posture_Model'
        )
        
        optimizer = Adam(learning_rate=0.001)
        self.model.compile(
            optimizer=optimizer,
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.model.summary()
        
        return self.model
    
    def train(self, X_img_train, X_num_train, y_train,
              X_img_val, X_num_val, y_val,
              epochs=100, batch_size=8):
        """모델 훈련 (클래스 가중치 적용)"""
        if self.model is None:
            raise ValueError("모델이 구성되지 않았습니다.")
        
        # 클래스 가중치 계산 (불균형 해결)
        class_weights = compute_class_weight(
            'balanced',
            classes=np.unique(y_train),
            y=y_train
        )
        class_weight_dict = dict(enumerate(class_weights))
        
        logging.info(f"클래스 가중치: {class_weight_dict}")
        
        callbacks = [
            EarlyStopping(
                monitor='val_loss', 
                patience=20, 
                restore_best_weights=True, 
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss', 
                factor=0.5, 
                patience=8, 
                min_lr=1e-7, 
                verbose=1
            ),
            ModelCheckpoint(
                'models/best_cnn_lstm_model.h5',
                save_best_only=True,
                monitor='val_accuracy',
                verbose=1
            )
        ]
        
        history = self.model.fit(
            [X_img_train, X_num_train], y_train,
            validation_data=([X_img_val, X_num_val], y_val),
            epochs=epochs,
            batch_size=batch_size,
            class_weight=class_weight_dict,  # 클래스 가중치 적용
            callbacks=callbacks,
            verbose=1
        )
        
        return history
    
    def evaluate(self, X_img, X_num, y, dataset_name="Test"):
        """모델 평가"""
        if self.model is None:
            raise ValueError("훈련된 모델이 없습니다.")
        
        y_pred_proba = self.model.predict([X_img, X_num], verbose=0)
        y_pred = np.argmax(y_pred_proba, axis=1)
        
        accuracy = accuracy_score(y, y_pred)
        
        logging.info(f"{dataset_name} 정확도: {accuracy:.4f}")
        
        class_names = self.label_encoder.classes_
        report = classification_report(y, y_pred, target_names=class_names, zero_division=0)
        logging.info(f"{dataset_name} 분류 보고서:\n{report}")
        
        cm = confusion_matrix(y, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=class_names, yticklabels=class_names)
        plt.title(f'{dataset_name} Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(f'models/confusion_matrix_{dataset_name.lower()}_cnn_lstm.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        return accuracy, report, cm
    
    def plot_training_history(self, history):
        """훈련 히스토리 시각화"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        ax1.plot(history.history['accuracy'], label='Training Accuracy', linewidth=2)
        ax1.plot(history.history['val_accuracy'], label='Validation Accuracy', linewidth=2)
        ax1.set_title('Model Accuracy', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Epoch', fontsize=12)
        ax1.set_ylabel('Accuracy', fontsize=12)
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        ax2.plot(history.history['loss'], label='Training Loss', linewidth=2)
        ax2.plot(history.history['val_loss'], label='Validation Loss', linewidth=2)
        ax2.set_title('Model Loss', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Epoch', fontsize=12)
        ax2.set_ylabel('Loss', fontsize=12)
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('models/training_history_cnn_lstm.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def save_model(self, model_path: str = 'models/cnn_lstm_model.h5'):
        """모델 저장"""
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
                       help='훈련 에폭 수')
    parser.add_argument('--batch_size', type=int, default=8,
                       help='배치 크기')
    parser.add_argument('--img_size', type=int, default=128,
                       help='이미지 크기 (정사각형)')
    parser.add_argument('--sequence_length', type=int, default=5,
                       help='LSTM 시퀀스 길이')
    parser.add_argument('--no_augment', action='store_true',
                       help='데이터 증강 사용 안 함')
    
    args = parser.parse_args()
    
    Path('models').mkdir(exist_ok=True)
    
    model = CNNLSTMModel(
        img_height=args.img_size,
        img_width=args.img_size,
        sequence_length=args.sequence_length
    )
    
    try:
        logging.info("데이터 로드 중...")
        df, image_dir = model.load_data(args.data, args.images)
        
        logging.info("데이터 전처리 중...")
        (X_img_train, X_num_train, y_train,
         X_img_val, X_num_val, y_val,
         X_img_test, X_num_test, y_test) = model.prepare_data(
            df, image_dir, augment=not args.no_augment
        )
        
        if len(X_img_train) == 0:
            logging.error("훈련 데이터가 없습니다.")
            return
        
        logging.info("모델 구성 중...")
        num_classes = len(model.label_encoder.classes_)
        num_numeric_features = len(model.feature_columns)
        
        model.build_model(num_numeric_features, num_classes)
        
        logging.info("모델 훈련 시작...")
        history = model.train(
            X_img_train, X_num_train, y_train,
            X_img_val, X_num_val, y_val,
            epochs=args.epochs,
            batch_size=args.batch_size
        )
        
        model.plot_training_history(history)
        
        logging.info("훈련 세트 평가 중...")
        train_accuracy, train_report, train_cm = model.evaluate(
            X_img_train, X_num_train, y_train, dataset_name="Train"
        )
        
        logging.info("검증 세트 평가 중...")
        val_accuracy, val_report, val_cm = model.evaluate(
            X_img_val, X_num_val, y_val, dataset_name="Validation"
        )
        
        logging.info("테스트 세트 평가 중...")
        test_accuracy, test_report, test_cm = model.evaluate(
            X_img_test, X_num_test, y_test, dataset_name="Test"
        )
        
        logging.info("모델 저장 중...")
        model.save_model()
        
        logging.info("CNN + LSTM 모델 훈련 완료!")
        logging.info(f"최종 훈련 정확도: {train_accuracy:.4f}")
        logging.info(f"최종 검증 정확도: {val_accuracy:.4f}")
        logging.info(f"최종 테스트 정확도: {test_accuracy:.4f}")
        
    except Exception as e:
        logging.error(f"훈련 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    main()
