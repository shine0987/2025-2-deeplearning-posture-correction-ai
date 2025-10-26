"""
자세 분류 모델의 훈련 및 검증을 담당하는 모듈
데이터 전처리부터 모델 훈련, 평가까지 전체 파이프라인을 관리합니다.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict, Tuple, Optional
import json

from data_preprocessing import PostureDataProcessor
from lstm_model import PostureLSTMModel

class PostureTrainer:
    """자세 분류 모델 훈련 클래스"""
    
    def __init__(self, base_path: str, sequence_length: int = 5):
        """
        초기화
        
        Args:
            base_path (str): 데이터가 있는 기본 경로
            sequence_length (int): LSTM 시퀀스 길이
        """
        self.base_path = base_path
        self.sequence_length = sequence_length
        
        # 데이터 경로 설정
        self.angles_path = os.path.join(base_path, "skeleton_angles.csv")
        self.coords_path = os.path.join(base_path, "skeleton_coords.csv")
        self.labeled_dir = os.path.join(base_path, "labeled")
        
        # 결과 저장 경로 설정
        self.results_dir = os.path.join(base_path, "results")
        self.models_dir = os.path.join(base_path, "models")
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        
        # 컴포넌트 초기화
        self.data_processor = PostureDataProcessor(sequence_length=sequence_length)
        self.model_manager = None
        
    def prepare_data(self, use_angles: bool = True, use_coords: bool = True) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        데이터를 준비하고 전처리합니다.
        
        Args:
            use_angles (bool): 각도 특성 사용 여부
            use_coords (bool): 좌표 특성 사용 여부
            
        Returns:
            Tuple: X_train, X_test, y_train, y_test
        """
        print("="*60)
        print("데이터 준비 및 전처리 시작")
        print("="*60)
        
        # 데이터 로드
        angles_df, coords_df = self.data_processor.load_data(
            self.angles_path, self.coords_path, self.labeled_dir
        )
        
        # 특성 준비
        features_df = self.data_processor.prepare_features(
            angles_df, coords_df, use_angles=use_angles, use_coords=use_coords
        )
        
        # 시퀀스 생성
        X, y = self.data_processor.create_sequences(features_df)
        
        # 데이터 분할
        X_train, X_test, y_train, y_test = self.data_processor.split_data(X, y, test_size=0.3)
        
        # 정규화
        X_train_norm, X_test_norm = self.data_processor.normalize_features(X_train, X_test)
        
        print("\\n데이터 준비 완료!")
        print(f"훈련 데이터: {X_train_norm.shape}")
        print(f"테스트 데이터: {X_test_norm.shape}")
        print(f"특성 수: {X_train_norm.shape[-1]}")
        print(f"클래스: {self.data_processor.get_class_names()}")
        
        return X_train_norm, X_test_norm, y_train, y_test
    
    def create_model(self, n_features: int, lstm_units: list = [64, 32], 
                    dropout_rate: float = 0.3, learning_rate: float = 0.001) -> PostureLSTMModel:
        """
        LSTM 모델을 생성합니다.
        
        Args:
            n_features (int): 특성 수
            lstm_units (list): LSTM 유닛 수 리스트
            dropout_rate (float): 드롭아웃 비율
            learning_rate (float): 학습률
            
        Returns:
            PostureLSTMModel: 생성된 모델 매니저
        """
        print("\\n" + "="*60)
        print("모델 생성 및 구성")
        print("="*60)
        
        # 모델 매니저 초기화
        self.model_manager = PostureLSTMModel(
            sequence_length=self.sequence_length,
            n_features=n_features,
            n_classes=2
        )
        
        # 클래스 이름 설정
        self.model_manager.set_class_names(self.data_processor.get_class_names())
        
        # 모델 구성
        model = self.model_manager.build_model(
            lstm_units=lstm_units,
            dropout_rate=dropout_rate,
            learning_rate=learning_rate
        )
        
        return self.model_manager
    
    def train_model(self, X_train: np.ndarray, y_train: np.ndarray,
                   X_test: np.ndarray, y_test: np.ndarray,
                   epochs: int = 100, batch_size: int = 8, 
                   validation_split: float = 0.2) -> Dict:
        """
        모델을 훈련합니다.
        
        Args:
            X_train (np.ndarray): 훈련 데이터
            y_train (np.ndarray): 훈련 라벨
            X_test (np.ndarray): 테스트 데이터
            y_test (np.ndarray): 테스트 라벨
            epochs (int): 에포크 수
            batch_size (int): 배치 크기
            validation_split (float): 검증 데이터 비율
            
        Returns:
            Dict: 훈련 결과
        """
        if self.model_manager is None:
            raise ValueError("모델이 생성되지 않았습니다. create_model()을 먼저 호출하세요.")
        
        print("\\n" + "="*60)
        print("모델 훈련 시작")
        print("="*60)
        
        # 타임스탬프로 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = os.path.join(self.models_dir, f"posture_lstm_model_{timestamp}.keras")
        
        # 검증 데이터 분할
        val_size = int(len(X_train) * validation_split)
        if val_size > 0:
            X_val = X_train[-val_size:]
            y_val = y_train[-val_size:]
            X_train_split = X_train[:-val_size]
            y_train_split = y_train[:-val_size]
        else:
            X_val, y_val = None, None
            X_train_split, y_train_split = X_train, y_train
        
        print(f"훈련 데이터: {X_train_split.shape}")
        if X_val is not None:
            print(f"검증 데이터: {X_val.shape}")
        
        # 모델 훈련
        history = self.model_manager.train_model(
            X_train_split, y_train_split,
            X_val, y_val,
            epochs=epochs,
            batch_size=batch_size,
            patience=20,
            save_path=model_path
        )
        
        # 모델 평가
        print("\\n" + "="*60)
        print("모델 평가")
        print("="*60)
        
        eval_results = self.model_manager.evaluate_model(X_test, y_test)
        
        # 결과 저장
        results = {
            'training_history': history,
            'evaluation_results': {
                'test_loss': float(eval_results['test_loss']),
                'test_accuracy': float(eval_results['test_accuracy']),
                'classification_report': eval_results['classification_report']
            },
            'model_config': {
                'sequence_length': self.sequence_length,
                'n_features': X_train.shape[-1],
                'epochs': epochs,
                'batch_size': batch_size,
                'validation_split': validation_split
            },
            'data_info': {
                'train_samples': len(X_train_split),
                'validation_samples': len(X_val) if X_val is not None else 0,
                'test_samples': len(X_test),
                'feature_names': self.data_processor.get_feature_names(),
                'class_names': self.data_processor.get_class_names()
            }
        }
        
        # 결과 파일 저장
        results_path = os.path.join(self.results_dir, f"training_results_{timestamp}.json")
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\\n훈련 결과 저장: {results_path}")
        print(f"모델 저장: {model_path}")
        
        # 시각화
        self._save_visualizations(eval_results['confusion_matrix'], timestamp)
        
        return results
    
    def _save_visualizations(self, confusion_matrix: np.ndarray, timestamp: str) -> None:
        """
        훈련 결과를 시각화하고 저장합니다.
        
        Args:
            confusion_matrix (np.ndarray): 혼동 행렬
            timestamp (str): 타임스탬프
        """
        print("\\n시각화 결과 저장 중...")
        
        # 훈련 히스토리 그래프
        history_path = os.path.join(self.results_dir, f"training_history_{timestamp}.png")
        self.model_manager.plot_training_history(save_path=history_path)
        
        # 혼동 행렬 그래프
        cm_path = os.path.join(self.results_dir, f"confusion_matrix_{timestamp}.png")
        self.model_manager.plot_confusion_matrix(confusion_matrix, save_path=cm_path)
        
        print(f"시각화 파일 저장 완료!")
    
    def full_training_pipeline(self, config: Optional[Dict] = None) -> Dict:
        """
        전체 훈련 파이프라인을 실행합니다.
        
        Args:
            config (Dict, optional): 설정 딕셔너리
            
        Returns:
            Dict: 전체 결과
        """
        # 기본 설정
        default_config = {
            'use_angles': True,
            'use_coords': True,
            'lstm_units': [64, 32],
            'dropout_rate': 0.3,
            'learning_rate': 0.001,
            'epochs': 50,
            'batch_size': 8,
            'validation_split': 0.2
        }
        
        if config:
            default_config.update(config)
        
        config = default_config
        
        print("자세 분류 모델 훈련 파이프라인 시작!")
        print(f"설정: {config}")
        
        try:
            # 1. 데이터 준비
            X_train, X_test, y_train, y_test = self.prepare_data(
                use_angles=config['use_angles'],
                use_coords=config['use_coords']
            )
            
            # 2. 모델 생성
            self.create_model(
                n_features=X_train.shape[-1],
                lstm_units=config['lstm_units'],
                dropout_rate=config['dropout_rate'],
                learning_rate=config['learning_rate']
            )
            
            # 3. 모델 훈련
            results = self.train_model(
                X_train, y_train, X_test, y_test,
                epochs=config['epochs'],
                batch_size=config['batch_size'],
                validation_split=config['validation_split']
            )
            
            print("\\n" + "="*60)
            print("훈련 파이프라인 완료!")
            print("="*60)
            print(f"최종 테스트 정확도: {results['evaluation_results']['test_accuracy']:.4f}")
            
            return results
            
        except Exception as e:
            print(f"훈련 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            return {}

def main():
    """메인 실행 함수"""
    # 기본 경로 설정
    base_path = r"c:\\Users\\user\\OneDrive\\Desktop\\test\\Lstm_model"
    
    # 훈련기 초기화
    trainer = PostureTrainer(base_path, sequence_length=3)
    
    # 훈련 설정
    config = {
        'use_angles': True,
        'use_coords': True,
        'lstm_units': [32, 16],  # 작은 데이터셋에 맞게 조정
        'dropout_rate': 0.2,
        'learning_rate': 0.001,
        'epochs': 30,  # 빠른 테스트를 위해 줄임
        'batch_size': 4,  # 작은 배치 크기
        'validation_split': 0.2
    }
    
    # 전체 파이프라인 실행
    results = trainer.full_training_pipeline(config)
    
    if results:
        print("\\n훈련이 성공적으로 완료되었습니다!")
    else:
        print("\\n훈련 중 오류가 발생했습니다.")

if __name__ == "__main__":
    main()