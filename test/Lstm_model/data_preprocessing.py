"""
자세 분석을 위한 데이터 전처리 모듈
이 모듈은 CSV 파일에서 데이터를 로드하고 LSTM 모델을 위한 시퀀스 데이터로 변환합니다.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import os
from typing import Tuple, List, Dict, Optional
import warnings
warnings.filterwarnings('ignore')

class PostureDataProcessor:
    """자세 데이터를 처리하는 클래스"""
    
    def __init__(self, sequence_length: int = 5):
        """
        초기화
        
        Args:
            sequence_length (int): LSTM을 위한 시퀀스 길이
        """
        self.sequence_length = sequence_length
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        self.is_fitted = False
        
    def load_data(self, angles_path: str, coords_path: str, labeled_dir: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        CSV 파일에서 데이터를 로드합니다.
        
        Args:
            angles_path (str): 각도 데이터 CSV 파일 경로
            coords_path (str): 좌표 데이터 CSV 파일 경로
            labeled_dir (str): 라벨링된 이미지 폴더 경로
            
        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: 각도 데이터와 좌표 데이터
        """
        print("데이터 로딩 중...")
        
        # CSV 파일 로드
        angles_df = pd.read_csv(angles_path)
        coords_df = pd.read_csv(coords_path)
        
        # 라벨 추가
        angles_df = self._add_labels(angles_df, labeled_dir)
        coords_df = self._add_labels(coords_df, labeled_dir)
        
        print(f"각도 데이터: {angles_df.shape}")
        print(f"좌표 데이터: {coords_df.shape}")
        print(f"라벨 분포:")
        print(angles_df['label'].value_counts())
        
        return angles_df, coords_df
    
    def _add_labels(self, df: pd.DataFrame, labeled_dir: str) -> pd.DataFrame:
        """
        이미지 파일 경로를 기반으로 라벨을 추가합니다.
        
        Args:
            df (pd.DataFrame): 데이터프레임
            labeled_dir (str): 라벨링된 폴더 경로
            
        Returns:
            pd.DataFrame: 라벨이 추가된 데이터프레임
        """
        df = df.copy()
        df['label'] = 'unknown'
        
        # normal 폴더의 이미지들
        normal_dir = os.path.join(labeled_dir, 'normal')
        if os.path.exists(normal_dir):
            normal_images = os.listdir(normal_dir)
            df.loc[df['image_path'].isin(normal_images), 'label'] = 'normal'
        
        # abnormal 폴더의 이미지들
        abnormal_dir = os.path.join(labeled_dir, 'abnormal')
        if os.path.exists(abnormal_dir):
            abnormal_images = os.listdir(abnormal_dir)
            df.loc[df['image_path'].isin(abnormal_images), 'label'] = 'abnormal'
        
        return df
    
    def prepare_features(self, angles_df: pd.DataFrame, coords_df: pd.DataFrame, 
                        use_angles: bool = True, use_coords: bool = True) -> pd.DataFrame:
        """
        각도와 좌표 데이터를 결합하여 특성을 준비합니다.
        
        Args:
            angles_df (pd.DataFrame): 각도 데이터
            coords_df (pd.DataFrame): 좌표 데이터
            use_angles (bool): 각도 특성 사용 여부
            use_coords (bool): 좌표 특성 사용 여부
            
        Returns:
            pd.DataFrame: 결합된 특성 데이터
        """
        print("특성 준비 중...")
        
        # 이미지 경로를 기준으로 데이터 병합
        merged_df = pd.merge(angles_df, coords_df, on=['image_path'], suffixes=('_angles', '_coords'))
        
        # 실제 컬럼 확인
        print(f"병합된 데이터 컬럼: {list(merged_df.columns)}")
        
        # 특성 컬럼 선택
        feature_columns = []
        
        if use_angles:
            angle_features = [col for col in angles_df.columns if col not in ['image_path', 'label']]
            for col in angle_features:
                angle_col = f"{col}_angles"
                if angle_col in merged_df.columns:
                    feature_columns.append(angle_col)
                elif col in merged_df.columns:  # suffix가 없는 경우
                    feature_columns.append(col)
        
        if use_coords:
            coord_features = [col for col in coords_df.columns if col not in ['image_path', 'label']]
            for col in coord_features:
                coord_col = f"{col}_coords"
                if coord_col in merged_df.columns:
                    feature_columns.append(coord_col)
                elif col in merged_df.columns:  # suffix가 없는 경우
                    feature_columns.append(col)
        
        # 라벨 컬럼 찾기
        label_col = None
        if 'label_angles' in merged_df.columns:
            label_col = 'label_angles'
        elif 'label_coords' in merged_df.columns:
            label_col = 'label_coords'
        elif 'label' in merged_df.columns:
            label_col = 'label'
        
        # 최종 데이터프레임 구성
        columns_to_select = ['image_path'] + feature_columns
        if label_col:
            columns_to_select.append(label_col)
        
        final_df = merged_df[columns_to_select].copy()
        
        if label_col and label_col != 'label':
            final_df.rename(columns={label_col: 'label'}, inplace=True)
        
        self.feature_names = feature_columns
        print(f"선택된 특성 컬럼: {feature_columns[:5]}..." if len(feature_columns) > 5 else f"선택된 특성 컬럼: {feature_columns}")
        print(f"총 특성 수: {len(feature_columns)}")
        
        return final_df
    
    def create_sequences(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        시계열 데이터를 시퀀스로 변환합니다.
        데이터가 적을 경우 데이터 증강을 통해 시퀀스를 생성합니다.
        
        Args:
            df (pd.DataFrame): 입력 데이터프레임
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: X (특성), y (라벨)
        """
        print("시퀀스 데이터 생성 중...")
        
        # 특성과 라벨 분리
        feature_columns = [col for col in df.columns if col not in ['image_path', 'label']]
        X = df[feature_columns].values
        y = df['label'].values
        
        # 라벨 인코딩
        y_encoded = self.label_encoder.fit_transform(y)
        
        # 데이터가 적을 경우 데이터 증강
        if len(X) < self.sequence_length:
            print(f"데이터가 적습니다 ({len(X)}개). 데이터 증강을 수행합니다.")
            X, y_encoded = self._augment_data(X, y_encoded)
        
        # 시퀀스 생성
        X_sequences, y_sequences = self._create_sequence_data(X, y_encoded)
        
        print(f"생성된 시퀀스: {X_sequences.shape}")
        print(f"라벨 수: {len(y_sequences)}")
        
        return X_sequences, y_sequences
    
    def _augment_data(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        데이터 증강을 수행합니다.
        
        Args:
            X (np.ndarray): 입력 특성
            y (np.ndarray): 라벨
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: 증강된 데이터
        """
        augmented_X = []
        augmented_y = []
        
        # 원본 데이터 추가
        augmented_X.append(X)
        augmented_y.append(y)
        
        # 노이즈 추가
        for i in range(3):  # 3배 증강
            noise_factor = 0.02 * (i + 1)  # 점진적으로 노이즈 증가
            noisy_X = X + np.random.normal(0, noise_factor * np.std(X, axis=0), X.shape)
            augmented_X.append(noisy_X)
            augmented_y.append(y)
        
        # 스케일링 변형
        for scale_factor in [0.98, 1.02]:
            scaled_X = X * scale_factor
            augmented_X.append(scaled_X)
            augmented_y.append(y)
        
        return np.vstack(augmented_X), np.hstack(augmented_y)
    
    def _create_sequence_data(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        슬라이딩 윈도우를 사용하여 시퀀스 데이터를 생성합니다.
        
        Args:
            X (np.ndarray): 입력 특성
            y (np.ndarray): 라벨
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: 시퀀스 데이터
        """
        sequences = []
        labels = []
        
        # 슬라이딩 윈도우로 시퀀스 생성
        for i in range(len(X) - self.sequence_length + 1):
            sequences.append(X[i:i + self.sequence_length])
            # 시퀀스의 마지막 라벨을 사용
            labels.append(y[i + self.sequence_length - 1])
        
        # 데이터가 여전히 부족한 경우 중복 생성
        if len(sequences) < 20:  # 최소 20개 시퀀스 보장
            while len(sequences) < 20:
                # 랜덤하게 시작점 선택하여 시퀀스 생성
                start_idx = np.random.randint(0, max(1, len(X) - self.sequence_length + 1))
                if start_idx + self.sequence_length <= len(X):
                    sequences.append(X[start_idx:start_idx + self.sequence_length])
                    labels.append(y[start_idx + self.sequence_length - 1])
                else:
                    # 데이터 끝부분에서 반복
                    seq = X[-self.sequence_length:]
                    sequences.append(seq)
                    labels.append(y[-1])
        
        return np.array(sequences), np.array(labels)
    
    def normalize_features(self, X_train: np.ndarray, X_test: Optional[np.ndarray] = None) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        특성을 정규화합니다.
        
        Args:
            X_train (np.ndarray): 훈련 데이터
            X_test (np.ndarray, optional): 테스트 데이터
            
        Returns:
            Tuple[np.ndarray, Optional[np.ndarray]]: 정규화된 데이터
        """
        print("특성 정규화 중...")
        
        # 3D 데이터를 2D로 변환하여 정규화
        original_shape = X_train.shape
        X_train_2d = X_train.reshape(-1, X_train.shape[-1])
        
        # 정규화 수행
        X_train_normalized_2d = self.scaler.fit_transform(X_train_2d)
        X_train_normalized = X_train_normalized_2d.reshape(original_shape)
        
        X_test_normalized = None
        if X_test is not None:
            X_test_2d = X_test.reshape(-1, X_test.shape[-1])
            X_test_normalized_2d = self.scaler.transform(X_test_2d)
            X_test_normalized = X_test_normalized_2d.reshape(X_test.shape)
        
        self.is_fitted = True
        return X_train_normalized, X_test_normalized
    
    def split_data(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2, 
                   random_state: int = 42) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        데이터를 훈련/테스트 세트로 분할합니다.
        
        Args:
            X (np.ndarray): 특성 데이터
            y (np.ndarray): 라벨 데이터
            test_size (float): 테스트 세트 비율
            random_state (int): 랜덤 시드
            
        Returns:
            Tuple: X_train, X_test, y_train, y_test
        """
        return train_test_split(X, y, test_size=test_size, random_state=random_state, 
                               stratify=y if len(np.unique(y)) > 1 else None)
    
    def get_class_names(self) -> List[str]:
        """클래스 이름을 반환합니다."""
        if hasattr(self.label_encoder, 'classes_'):
            return self.label_encoder.classes_.tolist()
        return []
    
    def get_feature_names(self) -> List[str]:
        """특성 이름을 반환합니다."""
        return self.feature_names.copy()

def main():
    """테스트 실행 함수"""
    # 데이터 경로 설정
    base_path = r"c:\Users\user\OneDrive\Desktop\test\Lstm_model"
    angles_path = os.path.join(base_path, "skeleton_angles.csv")
    coords_path = os.path.join(base_path, "skeleton_coords.csv")
    labeled_dir = os.path.join(base_path, "labeled")
    
    # 데이터 처리기 초기화
    processor = PostureDataProcessor(sequence_length=3)
    
    try:
        # 데이터 로드
        angles_df, coords_df = processor.load_data(angles_path, coords_path, labeled_dir)
        
        # 특성 준비
        features_df = processor.prepare_features(angles_df, coords_df)
        
        # 시퀀스 생성
        X, y = processor.create_sequences(features_df)
        
        # 데이터 분할
        X_train, X_test, y_train, y_test = processor.split_data(X, y)
        
        # 정규화
        X_train_norm, X_test_norm = processor.normalize_features(X_train, X_test)
        
        print("="*50)
        print("데이터 전처리 완료!")
        print(f"훈련 데이터: {X_train_norm.shape}")
        print(f"테스트 데이터: {X_test_norm.shape}")
        print(f"클래스: {processor.get_class_names()}")
        print(f"특성 수: {len(processor.get_feature_names())}")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()