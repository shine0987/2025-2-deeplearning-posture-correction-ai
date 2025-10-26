# 자세 분류 LSTM 모델 사용 예제

## 1. 모델 훈련
python main.py --mode train --epochs 50 --batch_size 8

## 2. 데이터 평가
python main.py --mode evaluate --angles_csv "새로운_각도데이터.csv" --coords_csv "새로운_좌표데이터.csv"

## 3. 모델 정보 확인
python main.py --mode info

## 4. 대화형 모드 (기본)
python main.py

## Python 코드에서 직접 사용하는 방법:

```python
from external_data_interface import PostureEvaluator

# 평가기 초기화
evaluator = PostureEvaluator(base_path="./")

# 모델 로드
if evaluator.load_model():
    # CSV 데이터 평가
    results = evaluator.evaluate_csv_data("angles.csv", "coords.csv")
    
    # 단일 샘플 평가
    angles_data = {"neck_angle": 130, "shoulder_angle_deg": 160, "hip_angle_deg": 140}
    coords_data = {"lm_0_x": 0.5, "lm_0_y": 0.2, ...}  # 좌표 데이터
    
    result = evaluator.evaluate_single_sample(angles_data, coords_data, "test_image.jpg")
    print(f"예측: {result['prediction']}, 신뢰도: {result['confidence']}")
```
