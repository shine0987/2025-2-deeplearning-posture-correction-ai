"""
자세 분류를 위한 LSTM 모델 아키텍처
정상/비정상 자세를 분류하는 딥러닝 모델을 구현합니다.
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, callbacks
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
from typing import Tuple, List, Dict, Optional
import os
import json

class PostureLSTMModel:
    """자세 분류를 위한 LSTM 모델 클래스"""
    
    def __init__(self, sequence_length: int, n_features: int, n_classes: int = 2):
        """
        초기화
        
        Args:
            sequence_length (int): 입력 시퀀스 길이
            n_features (int): 특성 수
            n_classes (int): 클래스 수 (기본값: 2 - 정상/비정상)
        """
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.n_classes = n_classes
        self.model = None
        self.history = None
        self.class_names = ['abnormal', 'normal']  # 기본 클래스 이름
        
    def build_model(self, lstm_units: List[int] = [64, 32], dropout_rate: float = 0.3,
                   learning_rate: float = 0.001) -> keras.Model:
        """
        LSTM 모델을 구성합니다.
        
        Args:
            lstm_units (List[int]): LSTM 레이어의 유닛 수
            dropout_rate (float): 드롭아웃 비율
            learning_rate (float): 학습률
            
        Returns:
            keras.Model: 구성된 모델
        """
        print("LSTM 모델 구성 중...")
        
        model = models.Sequential([
            # 첫 번째 LSTM 레이어
            layers.LSTM(lstm_units[0], 
                       return_sequences=True if len(lstm_units) > 1 else False,
                       input_shape=(self.sequence_length, self.n_features),
                       name='lstm_1'),
            layers.Dropout(dropout_rate, name='dropout_1'),
        ])
        
        # 추가 LSTM 레이어들
        for i, units in enumerate(lstm_units[1:], 1):
            return_sequences = i < len(lstm_units) - 1
            model.add(layers.LSTM(units, 
                                return_sequences=return_sequences,
                                name=f'lstm_{i+1}'))
            model.add(layers.Dropout(dropout_rate, name=f'dropout_{i+1}'))
        
        # 완전연결 레이어들
        model.add(layers.Dense(32, activation='relu', name='dense_1'))
        model.add(layers.Dropout(dropout_rate, name='dropout_dense'))
        model.add(layers.Dense(16, activation='relu', name='dense_2'))
        
        # 출력 레이어
        if self.n_classes == 2:
            model.add(layers.Dense(1, activation='sigmoid', name='output'))
            loss = 'binary_crossentropy'
            metrics = ['accuracy']
        else:
            model.add(layers.Dense(self.n_classes, activation='softmax', name='output'))
            loss = 'sparse_categorical_crossentropy'
            metrics = ['accuracy']
        
        # 모델 컴파일
        optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
        model.compile(optimizer=optimizer, loss=loss, metrics=metrics)
        
        self.model = model
        
        print("모델 구성 완료!")
        print(f"총 파라미터 수: {model.count_params():,}")
        
        return model
    
    def get_model_summary(self) -> str:
        """모델 요약 정보를 반환합니다."""
        if self.model is None:
            return "모델이 구성되지 않았습니다."
        
        summary_lines = []
        self.model.summary(print_fn=lambda x: summary_lines.append(x))
        return '\\n'.join(summary_lines)
    
    def train_model(self, X_train: np.ndarray, y_train: np.ndarray,
                   X_val: Optional[np.ndarray] = None, y_val: Optional[np.ndarray] = None,
                   epochs: int = 100, batch_size: int = 8, patience: int = 15,
                   save_path: Optional[str] = None) -> Dict:
        """
        모델을 훈련합니다.
        
        Args:
            X_train (np.ndarray): 훈련 데이터
            y_train (np.ndarray): 훈련 라벨
            X_val (np.ndarray, optional): 검증 데이터
            y_val (np.ndarray, optional): 검증 라벨
            epochs (int): 에포크 수
            batch_size (int): 배치 크기
            patience (int): 조기 종료 인내심
            save_path (str, optional): 모델 저장 경로
            
        Returns:
            Dict: 훈련 히스토리
        """
        if self.model is None:
            raise ValueError("모델이 구성되지 않았습니다. build_model()을 먼저 호출하세요.")
        
        print("모델 훈련 시작...")
        
        # 콜백 설정
        callback_list = []
        
        # 조기 종료
        early_stopping = callbacks.EarlyStopping(
            monitor='val_loss' if X_val is not None else 'loss',
            patience=patience,
            restore_best_weights=True,
            verbose=1
        )
        callback_list.append(early_stopping)
        
        # 학습률 감소
        reduce_lr = callbacks.ReduceLROnPlateau(
            monitor='val_loss' if X_val is not None else 'loss',
            factor=0.5,
            patience=patience//2,
            min_lr=1e-7,
            verbose=1
        )
        callback_list.append(reduce_lr)
        
        # 모델 체크포인트 (저장 경로가 제공된 경우)
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            checkpoint = callbacks.ModelCheckpoint(
                save_path,
                monitor='val_loss' if X_val is not None else 'loss',
                save_best_only=True,
                verbose=1
            )
            callback_list.append(checkpoint)
        
        # 검증 데이터 설정
        validation_data = (X_val, y_val) if X_val is not None and y_val is not None else None
        
        # 훈련 실행
        history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callback_list,
            verbose=1
        )
        
        self.history = history
        print("모델 훈련 완료!")
        
        return history.history
    
    def evaluate_model(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """
        모델 성능을 평가합니다.
        
        Args:
            X_test (np.ndarray): 테스트 데이터
            y_test (np.ndarray): 테스트 라벨
            
        Returns:
            Dict: 평가 결과
        """
        if self.model is None:
            raise ValueError("모델이 구성되지 않았습니다.")
        
        print("모델 평가 중...")
        
        # 예측
        y_pred_proba = self.model.predict(X_test, verbose=0)
        
        if self.n_classes == 2:
            y_pred = (y_pred_proba > 0.5).astype(int).flatten()
        else:
            y_pred = np.argmax(y_pred_proba, axis=1)
        
        # 평가 지표 계산
        test_loss, test_accuracy = self.model.evaluate(X_test, y_test, verbose=0)
        
        # 분류 리포트
        report = classification_report(y_test, y_pred, 
                                     target_names=self.class_names,
                                     output_dict=True)
        
        # 혼동 행렬
        cm = confusion_matrix(y_test, y_pred)
        
        results = {
            'test_loss': test_loss,
            'test_accuracy': test_accuracy,
            'classification_report': report,
            'confusion_matrix': cm,
            'predictions': y_pred,
            'prediction_probabilities': y_pred_proba
        }
        
        print(f"테스트 정확도: {test_accuracy:.4f}")
        print("\\n분류 리포트:")
        print(classification_report(y_test, y_pred, target_names=self.class_names))
        
        return results
    
    def plot_training_history(self, save_path: Optional[str] = None) -> None:
        """
        훈련 히스토리를 시각화합니다.
        
        Args:
            save_path (str, optional): 그래프 저장 경로
        """
        if self.history is None:
            print("훈련 히스토리가 없습니다.")
            return
        
        history = self.history.history
        epochs = range(1, len(history['loss']) + 1)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # 손실 그래프
        ax1.plot(epochs, history['loss'], 'b-', label='Training Loss')
        if 'val_loss' in history:
            ax1.plot(epochs, history['val_loss'], 'r-', label='Validation Loss')
        ax1.set_title('Model Loss')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax1.legend()
        ax1.grid(True)
        
        # 정확도 그래프
        ax2.plot(epochs, history['accuracy'], 'b-', label='Training Accuracy')
        if 'val_accuracy' in history:
            ax2.plot(epochs, history['val_accuracy'], 'r-', label='Validation Accuracy')
        ax2.set_title('Model Accuracy')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Accuracy')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"훈련 히스토리 그래프 저장: {save_path}")
        
        plt.show()
    
    def plot_confusion_matrix(self, cm: np.ndarray, save_path: Optional[str] = None) -> None:
        """
        혼동 행렬을 시각화합니다.
        
        Args:
            cm (np.ndarray): 혼동 행렬
            save_path (str, optional): 그래프 저장 경로
        """
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=self.class_names,
                   yticklabels=self.class_names)
        plt.title('Confusion Matrix')
        plt.xlabel('Predicted Label')
        plt.ylabel('True Label')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"혼동 행렬 그래프 저장: {save_path}")
        
        plt.show()
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        새로운 데이터에 대해 예측을 수행합니다.
        
        Args:
            X (np.ndarray): 입력 데이터
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: 예측 결과와 확률
        """
        if self.model is None:
            raise ValueError("모델이 구성되지 않았습니다.")
        
        proba = self.model.predict(X, verbose=0)
        
        if self.n_classes == 2:
            pred = (proba > 0.5).astype(int).flatten()
        else:
            pred = np.argmax(proba, axis=1)
        
        return pred, proba
    
    def save_model(self, filepath: str) -> None:
        """
        모델을 저장합니다.
        
        Args:
            filepath (str): 저장 경로
        """
        if self.model is None:
            raise ValueError("모델이 구성되지 않았습니다.")
        
        # 모델 저장
        self.model.save(filepath)
        
        # 메타데이터 저장
        metadata = {
            'sequence_length': self.sequence_length,
            'n_features': self.n_features,
            'n_classes': self.n_classes,
            'class_names': self.class_names
        }
        
        metadata_path = filepath.replace('.h5', '_metadata.json').replace('.keras', '_metadata.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"모델 저장 완료: {filepath}")
        print(f"메타데이터 저장 완료: {metadata_path}")
    
    def load_model(self, filepath: str) -> None:
        """
        저장된 모델을 로드합니다.
        
        Args:
            filepath (str): 모델 파일 경로
        """
        # 모델 로드
        self.model = keras.models.load_model(filepath)
        
        # 메타데이터 로드
        metadata_path = filepath.replace('.h5', '_metadata.json').replace('.keras', '_metadata.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            self.sequence_length = metadata.get('sequence_length', self.sequence_length)
            self.n_features = metadata.get('n_features', self.n_features)
            self.n_classes = metadata.get('n_classes', self.n_classes)
            self.class_names = metadata.get('class_names', self.class_names)
        
        print(f"모델 로드 완료: {filepath}")
    
    def set_class_names(self, class_names: List[str]) -> None:
        """클래스 이름을 설정합니다."""
        self.class_names = class_names.copy()

def main():
    """테스트 실행 함수"""
    print("LSTM 모델 테스트 시작...")
    
    # 임시 데이터 생성 (실제로는 전처리된 데이터 사용)
    sequence_length = 5
    n_features = 23  # skeleton_angles(3) + skeleton_coords(20)
    n_samples = 50
    
    # 가상 데이터 생성
    X = np.random.randn(n_samples, sequence_length, n_features)
    y = np.random.randint(0, 2, n_samples)
    
    # 모델 초기화
    model_manager = PostureLSTMModel(
        sequence_length=sequence_length,
        n_features=n_features,
        n_classes=2
    )
    
    # 모델 구성
    model = model_manager.build_model()
    
    # 모델 요약 출력
    print("\\n" + "="*50)
    print("모델 요약:")
    print(model_manager.get_model_summary())
    
    print("\\nLSTM 모델 아키텍처 테스트 완료!")

if __name__ == "__main__":
    main()