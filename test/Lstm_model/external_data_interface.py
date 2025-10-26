"""
외부 데이터 입력 및 평가를 위한 인터페이스 모듈
새로운 이미지나 CSV 데이터를 입력받아 자세를 분류합니다.
"""

import os
import pandas as pd
import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional, Union
import json
from datetime import datetime

from data_preprocessing import PostureDataProcessor
from lstm_model import PostureLSTMModel

class PostureEvaluator:
    """외부 데이터에 대한 자세 평가 클래스"""
    
    def __init__(self, model_path: Optional[str] = None, base_path: Optional[str] = None):
        """
        초기화
        
        Args:
            model_path (str, optional): 훈련된 모델 경로
            base_path (str, optional): 기본 경로 (모델 자동 찾기용)
        """
        self.model_path = model_path
        self.base_path = base_path or os.getcwd()
        
        # 컴포넌트 초기화
        self.data_processor = None
        self.model_manager = None
        self.is_loaded = False
        
        # 자동으로 최신 모델 로드 시도
        if model_path is None:
            self._find_latest_model()
    
    def _find_latest_model(self) -> None:
        """가장 최신의 훈련된 모델을 찾습니다."""
        models_dir = os.path.join(self.base_path, "models")
        if not os.path.exists(models_dir):
            print("모델 폴더를 찾을 수 없습니다. 수동으로 모델을 로드해주세요.")
            return
        
        # 모델 파일들 찾기
        model_files = [f for f in os.listdir(models_dir) if f.endswith(('.h5', '.keras'))]
        
        if not model_files:
            print("훈련된 모델을 찾을 수 없습니다.")
            return
        
        # 가장 최신 모델 선택 (파일명의 타임스탬프 기준)
        model_files.sort(reverse=True)
        latest_model = model_files[0]
        self.model_path = os.path.join(models_dir, latest_model)
        
        print(f"최신 모델 발견: {latest_model}")
    
    def load_model(self, model_path: Optional[str] = None) -> bool:
        """
        훈련된 모델을 로드합니다.
        
        Args:
            model_path (str, optional): 모델 파일 경로
            
        Returns:
            bool: 로드 성공 여부
        """
        if model_path:
            self.model_path = model_path
        
        if not self.model_path or not os.path.exists(self.model_path):
            print(f"모델 파일을 찾을 수 없습니다: {self.model_path}")
            return False
        
        try:
            print(f"모델 로드 중: {self.model_path}")
            
            # 메타데이터 로드
            metadata_path = self.model_path.replace('.h5', '_metadata.json').replace('.keras', '_metadata.json')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                sequence_length = metadata.get('sequence_length', 5)
                n_features = metadata.get('n_features', 23)
                n_classes = metadata.get('n_classes', 2)
                class_names = metadata.get('class_names', ['abnormal', 'normal'])
            else:
                print("메타데이터 파일을 찾을 수 없습니다. 기본값을 사용합니다.")
                sequence_length = 5
                n_features = 23
                n_classes = 2
                class_names = ['abnormal', 'normal']
            
            # 데이터 처리기 초기화
            self.data_processor = PostureDataProcessor(sequence_length=sequence_length)
            
            # 더미 데이터로 스케일러 초기화 (실제 사용 시에는 실제 데이터로 피팅해야 함)
            dummy_data = np.random.randn(100, n_features)
            self.data_processor.scaler.fit(dummy_data)
            self.data_processor.is_fitted = True
            
            # 모델 매니저 초기화 및 로드
            self.model_manager = PostureLSTMModel(
                sequence_length=sequence_length,
                n_features=n_features,
                n_classes=n_classes
            )
            self.model_manager.load_model(self.model_path)
            
            self.is_loaded = True
            print("모델 로드 완료!")
            return True
            
        except Exception as e:
            print(f"모델 로드 중 오류 발생: {e}")
            return False
    
    def evaluate_csv_data(self, angles_csv: str, coords_csv: str, 
                         output_path: Optional[str] = None) -> Dict:
        """
        CSV 파일로부터 자세 데이터를 평가합니다.
        
        Args:
            angles_csv (str): 각도 데이터 CSV 파일 경로
            coords_csv (str): 좌표 데이터 CSV 파일 경로
            output_path (str, optional): 결과 저장 경로
            
        Returns:
            Dict: 평가 결과
        """
        if not self.is_loaded:
            raise ValueError("모델이 로드되지 않았습니다. load_model()을 먼저 호출하세요.")
        
        print(f"CSV 데이터 평가 시작...")
        print(f"각도 데이터: {angles_csv}")
        print(f"좌표 데이터: {coords_csv}")
        
        try:
            # CSV 데이터 로드
            angles_df = pd.read_csv(angles_csv)
            coords_df = pd.read_csv(coords_csv)
            
            print(f"각도 데이터 로드: {angles_df.shape}")
            print(f"좌표 데이터 로드: {coords_df.shape}")
            
            # 특성 준비 (라벨 없이)
            features_df = self._prepare_features_for_prediction(angles_df, coords_df)
            
            # 시퀀스 생성 및 정규화
            X = self._create_prediction_sequences(features_df)
            
            # 예측 수행
            predictions, probabilities = self.model_manager.predict(X)
            
            # 결과 정리
            results = self._format_prediction_results(
                features_df['image_path'].values, predictions, probabilities
            )
            
            # 결과 저장
            if output_path:
                self._save_prediction_results(results, output_path)
            
            print(f"평가 완료! 총 {len(results['predictions'])}개 샘플 처리")
            
            return results
            
        except Exception as e:
            print(f"CSV 데이터 평가 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def evaluate_single_sample(self, angles_data: Dict, coords_data: Dict, 
                              image_name: str = "unknown") -> Dict:
        """
        단일 샘플에 대해 자세를 평가합니다.
        
        Args:
            angles_data (Dict): 각도 데이터 딕셔너리
            coords_data (Dict): 좌표 데이터 딕셔너리
            image_name (str): 이미지 이름
            
        Returns:
            Dict: 평가 결과
        """
        if not self.is_loaded:
            raise ValueError("모델이 로드되지 않았습니다. load_model()을 먼저 호출하세요.")
        
        try:
            # 딕셔너리를 DataFrame으로 변환
            angles_df = pd.DataFrame([angles_data])
            coords_df = pd.DataFrame([coords_data])
            
            # 이미지 경로 추가
            angles_df['image_path'] = image_name
            coords_df['image_path'] = image_name
            
            # 특성 준비
            features_df = self._prepare_features_for_prediction(angles_df, coords_df)
            
            # 시퀀스 생성 (단일 샘플의 경우 복제해서 시퀀스 생성)
            X = self._create_single_sample_sequence(features_df)
            
            # 예측 수행
            prediction, probability = self.model_manager.predict(X)
            
            # 결과 반환
            class_name = self.model_manager.class_names[prediction[0]]
            confidence = float(probability[0][0] if self.model_manager.n_classes == 2 else np.max(probability[0]))
            
            result = {
                'image_name': image_name,
                'prediction': class_name,
                'confidence': confidence,
                'probability': probability[0].tolist() if hasattr(probability[0], 'tolist') else [confidence],
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"예측 결과: {class_name} (신뢰도: {confidence:.3f})")
            
            return result
            
        except Exception as e:
            print(f"단일 샘플 평가 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _prepare_features_for_prediction(self, angles_df: pd.DataFrame, 
                                       coords_df: pd.DataFrame) -> pd.DataFrame:
        """예측을 위한 특성 준비"""
        # 이미지 경로를 기준으로 데이터 병합
        merged_df = pd.merge(angles_df, coords_df, on=['image_path'], suffixes=('_angles', '_coords'))
        
        # 특성 컬럼 선택 (라벨 제외)
        feature_columns = []
        
        # 각도 특성
        angle_features = [col for col in angles_df.columns if col not in ['image_path']]
        for col in angle_features:
            angle_col = f"{col}_angles"
            if angle_col in merged_df.columns:
                feature_columns.append(angle_col)
            elif col in merged_df.columns:  # suffix가 없는 경우
                feature_columns.append(col)
        
        # 좌표 특성
        coord_features = [col for col in coords_df.columns if col not in ['image_path']]
        for col in coord_features:
            coord_col = f"{col}_coords"
            if coord_col in merged_df.columns:
                feature_columns.append(coord_col)
            elif col in merged_df.columns:  # suffix가 없는 경우
                feature_columns.append(col)
        
        # 최종 데이터프레임 구성
        final_df = merged_df[['image_path'] + feature_columns].copy()
        
        return final_df
    
    def _create_prediction_sequences(self, features_df: pd.DataFrame) -> np.ndarray:
        """예측을 위한 시퀀스 생성"""
        feature_columns = [col for col in features_df.columns if col != 'image_path']
        X = features_df[feature_columns].values
        
        # 데이터가 시퀀스 길이보다 적은 경우 복제
        if len(X) < self.data_processor.sequence_length:
            # 마지막 샘플을 반복해서 시퀀스 길이 맞추기
            last_sample = X[-1:] if len(X) > 0 else np.zeros((1, X.shape[1]))
            while len(X) < self.data_processor.sequence_length:
                X = np.vstack([X, last_sample])
        
        # 슬라이딩 윈도우로 시퀀스 생성
        sequences = []
        for i in range(len(X) - self.data_processor.sequence_length + 1):
            sequences.append(X[i:i + self.data_processor.sequence_length])
        
        X_sequences = np.array(sequences)
        
        # 정규화
        original_shape = X_sequences.shape
        X_sequences_2d = X_sequences.reshape(-1, X_sequences.shape[-1])
        X_sequences_normalized_2d = self.data_processor.scaler.transform(X_sequences_2d)
        X_sequences_normalized = X_sequences_normalized_2d.reshape(original_shape)
        
        return X_sequences_normalized
    
    def _create_single_sample_sequence(self, features_df: pd.DataFrame) -> np.ndarray:
        """단일 샘플을 위한 시퀀스 생성"""
        feature_columns = [col for col in features_df.columns if col != 'image_path']
        sample = features_df[feature_columns].values[0]
        
        # 동일한 샘플을 시퀀스 길이만큼 복제
        sequence = np.tile(sample, (self.data_processor.sequence_length, 1))
        
        # 배치 차원 추가
        X = sequence.reshape(1, self.data_processor.sequence_length, -1)
        
        # 정규화
        original_shape = X.shape
        X_2d = X.reshape(-1, X.shape[-1])
        X_normalized_2d = self.data_processor.scaler.transform(X_2d)
        X_normalized = X_normalized_2d.reshape(original_shape)
        
        return X_normalized
    
    def _format_prediction_results(self, image_paths: np.ndarray, 
                                 predictions: np.ndarray, 
                                 probabilities: np.ndarray) -> Dict:
        """예측 결과를 포맷팅합니다."""
        results = {
            'predictions': [],
            'summary': {
                'total_samples': len(predictions),
                'normal_count': 0,
                'abnormal_count': 0,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        for i, (image_path, pred, prob) in enumerate(zip(image_paths, predictions, probabilities)):
            if i < len(image_paths):  # 이미지 경로가 있는 경우만
                class_name = self.model_manager.class_names[pred]
                confidence = float(prob[0] if self.model_manager.n_classes == 2 else np.max(prob))
                
                result_item = {
                    'image_path': image_path,
                    'prediction': class_name,
                    'confidence': confidence,
                    'probability': prob.tolist() if hasattr(prob, 'tolist') else [confidence]
                }
                
                results['predictions'].append(result_item)
                
                # 카운트 업데이트
                if class_name == 'normal':
                    results['summary']['normal_count'] += 1
                else:
                    results['summary']['abnormal_count'] += 1
        
        return results
    
    def _save_prediction_results(self, results: Dict, output_path: str) -> None:
        """예측 결과를 파일로 저장합니다."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"예측 결과 저장: {output_path}")
    
    def get_model_info(self) -> Dict:
        """모델 정보를 반환합니다."""
        if not self.is_loaded:
            return {"error": "모델이 로드되지 않았습니다."}
        
        return {
            'model_path': self.model_path,
            'sequence_length': self.data_processor.sequence_length,
            'class_names': self.model_manager.class_names,
            'n_classes': self.model_manager.n_classes,
            'model_summary': self.model_manager.get_model_summary()
        }

def main():
    """테스트 실행 함수"""
    base_path = r"c:\\Users\\user\\OneDrive\\Desktop\\test\\Lstm_model"
    
    # 평가기 초기화
    evaluator = PostureEvaluator(base_path=base_path)
    
    # 모델 로드
    if evaluator.load_model():
        # 모델 정보 출력
        model_info = evaluator.get_model_info()
        print("="*50)
        print("모델 정보:")
        for key, value in model_info.items():
            if key != 'model_summary':
                print(f"{key}: {value}")
        
        # 기존 데이터로 테스트
        angles_csv = os.path.join(base_path, "skeleton_angles.csv")
        coords_csv = os.path.join(base_path, "skeleton_coords.csv")
        
        if os.path.exists(angles_csv) and os.path.exists(coords_csv):
            print("\\n기존 데이터로 테스트 평가 수행...")
            results = evaluator.evaluate_csv_data(angles_csv, coords_csv)
            
            if results:
                print("\\n평가 결과 요약:")
                print(f"총 샘플 수: {results['summary']['total_samples']}")
                print(f"정상 자세: {results['summary']['normal_count']}")
                print(f"비정상 자세: {results['summary']['abnormal_count']}")
    else:
        print("모델을 로드할 수 없습니다. 먼저 모델을 훈련해주세요.")

if __name__ == "__main__":
    main()