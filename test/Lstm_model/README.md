# 🤖 자세 분류 LSTM 모델
**AI로 정상/비정상 자세를 자동 분류하는 딥러닝 시스템**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.20+-orange.svg)](https://tensorflow.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> 🚀 **3분 만에 시작하기**: [빠른 시작 가이드](QUICK_START.md)를 확인하세요!

---

## 🎯 **무엇을 할 수 있나요?**

| 기능 | 설명 | 소요시간 |
|------|------|----------|
| 🤖 **자세 분류** | 정상 vs 비정상 자세 자동 판별 | 즉시 |
| 📊 **배치 분석** | 여러 이미지/데이터를 한 번에 처리 | 1-5분 |
| ⚡ **실시간 평가** | 웹캠, 센서 데이터 실시간 분석 | 실시간 |
| 📈 **성능 분석** | 정확도, 신뢰도 등 상세 리포트 | 자동 |
| 🔧 **모델 커스터마이징** | 새로운 자세 타입 추가 학습 | 5-30분 |

### ✨ **핵심 특징**
- 🎯 **높은 정확도**: LSTM 딥러닝으로 시계열 패턴 인식
- 🚀 **간편한 사용**: 3단계로 바로 실행 가능
- 📱 **확장 가능**: Python API로 다른 프로그램에 통합
- 🔄 **실시간 처리**: 즉시 결과 확인
- 📊 **시각화**: 훈련 과정과 결과를 그래프로 확인

## 🗂️ 프로젝트 구조

```
Lstm_model/
├── main.py                     # 메인 실행 스크립트
├── data_preprocessing.py       # 데이터 전처리 모듈
├── lstm_model.py              # LSTM 모델 아키텍처
├── training_module.py         # 모델 훈련 모듈
├── external_data_interface.py # 외부 데이터 인터페이스
├── skeleton_angles.csv        # 예제 각도 데이터
├── skeleton_coords.csv        # 예제 좌표 데이터
├── labeled/                   # 라벨링된 이미지 폴더
│   ├── normal/               # 정상 자세 이미지
│   └── abnormal/             # 비정상 자세 이미지
├── models/                   # 훈련된 모델 저장 폴더
├── results/                  # 결과 및 로그 저장 폴더
└── requirements.txt          # 필요한 패키지 목록
```

## 📊 데이터 형식

### 각도 데이터 (skeleton_angles.csv)
```csv
image_path,neck_angle,shoulder_angle_deg,hip_angle_deg
image1.jpg,124.17,176.51,148.50
image2.jpg,-105.28,-56.03,-136.44
...
```

### 좌표 데이터 (skeleton_coords.csv)
```csv
image_path,lm_0_x,lm_0_y,lm_0_x_px,lm_0_y_px,lm_11_x,lm_11_y,...
image1.jpg,0.465,0.192,128,35,0.397,0.249,109,45,...
image2.jpg,0.375,0.254,270,325,0.494,0.298,356,382,...
...
```

## 🚀 설치 및 실행

### 1. 환경 설정
```bash
# Python 3.8+ 권장
pip install -r requirements.txt
```

### 2. 데이터 준비
- `skeleton_angles.csv`: 각도 데이터
- `skeleton_coords.csv`: 좌표 데이터
- `labeled/normal/`: 정상 자세 이미지
- `labeled/abnormal/`: 비정상 자세 이미지

### 3. 실행 방법

#### 대화형 모드 (권장)
```bash
python main.py
```

#### 모델 훈련
```bash
python main.py --mode train --epochs 50 --batch_size 8
```

#### 데이터 평가
```bash
python main.py --mode evaluate --angles_csv "새로운_각도데이터.csv" --coords_csv "새로운_좌표데이터.csv"
```

#### 모델 정보 확인
```bash
python main.py --mode info
```

## 🎯 사용 예제

### Python 코드에서 직접 사용

```python
from external_data_interface import PostureEvaluator

# 평가기 초기화
evaluator = PostureEvaluator(base_path="./")

# 모델 로드
if evaluator.load_model():
    # CSV 데이터 평가
    results = evaluator.evaluate_csv_data("angles.csv", "coords.csv")
    
    # 단일 샘플 평가
    angles_data = {
        "neck_angle": 130, 
        "shoulder_angle_deg": 160, 
        "hip_angle_deg": 140
    }
    coords_data = {
        "lm_0_x": 0.5, "lm_0_y": 0.2,
        "lm_11_x": 0.4, "lm_11_y": 0.25,
        # ... 기타 좌표 데이터
    }
    
    result = evaluator.evaluate_single_sample(
        angles_data, coords_data, "test_image.jpg"
    )
    
    print(f"예측: {result['prediction']}")
    print(f"신뢰도: {result['confidence']:.3f}")
```

### 새로운 데이터 추가하기

1. **CSV 파일 형식으로 데이터 준비**
   - 각도 데이터: `neck_angle`, `shoulder_angle_deg`, `hip_angle_deg`
   - 좌표 데이터: `lm_0_x`, `lm_0_y`, `lm_0_x_px`, `lm_0_y_px`, ...

2. **평가 실행**
   ```python
   evaluator = PostureEvaluator()
   evaluator.load_model()
   results = evaluator.evaluate_csv_data("new_angles.csv", "new_coords.csv")
   ```

## 🔧 모델 구성

### LSTM 아키텍처
- **입력**: 시퀀스 길이 3-5의 특성 벡터
- **LSTM 레이어**: 2층 (기본: 32, 16 유닛)
- **드롭아웃**: 0.2 (과적합 방지)
- **출력**: 이진 분류 (정상/비정상)

### 특성
- **각도 특성**: 목, 어깨, 엉덩이 각도 (3개)
- **좌표 특성**: 주요 랜드마크 좌표 (20개)
- **총 특성 수**: 23개

## 📊 성능 및 결과

모델 훈련 후 다음 정보가 제공됩니다:
- 훈련/검증 손실 및 정확도 그래프
- 혼동 행렬 (Confusion Matrix)
- 분류 보고서 (Precision, Recall, F1-score)
- 예측 결과 및 신뢰도

## 📁 출력 파일

### 모델 파일
- `models/posture_lstm_model_YYYYMMDD_HHMMSS.keras`: 훈련된 모델
- `models/posture_lstm_model_YYYYMMDD_HHMMSS_metadata.json`: 모델 메타데이터

### 결과 파일
- `results/training_results_YYYYMMDD_HHMMSS.json`: 훈련 결과
- `results/training_history_YYYYMMDD_HHMMSS.png`: 훈련 히스토리 그래프
- `results/confusion_matrix_YYYYMMDD_HHMMSS.png`: 혼동 행렬 그래프
- `results/evaluation_results_YYYYMMDD_HHMMSS.json`: 평가 결과

## 🛠️ 커스터마이징

### 모델 파라미터 조정
```python
config = {
    'use_angles': True,           # 각도 특성 사용
    'use_coords': True,           # 좌표 특성 사용
    'lstm_units': [64, 32],       # LSTM 유닛 수
    'dropout_rate': 0.3,          # 드롭아웃 비율
    'learning_rate': 0.001,       # 학습률
    'epochs': 50,                 # 에포크 수
    'batch_size': 8,              # 배치 크기
    'validation_split': 0.2       # 검증 데이터 비율
}
```

### 새로운 특성 추가
`data_preprocessing.py`의 `prepare_features()` 함수를 수정하여 새로운 특성을 추가할 수 있습니다.

## ⚠️ 주의사항

1. **데이터 일관성**: 훈련 데이터와 평가 데이터의 특성이 일치해야 합니다.
2. **스케일링**: 새로운 데이터는 훈련 시 사용된 스케일러로 정규화되어야 합니다.
3. **시퀀스 길이**: 시퀀스 길이보다 적은 데이터는 자동으로 증강됩니다.

## 🆘 문제 해결

### 일반적인 오류

1. **모델을 찾을 수 없음**
   ```
   해결: main.py --mode train을 먼저 실행하여 모델을 훈련시키세요.
   ```

2. **메모리 부족**
   ```
   해결: batch_size를 줄이거나 시퀀스 길이를 줄여보세요.
   ```

3. **정확도가 낮음**
   ```
   해결: 더 많은 데이터를 수집하거나 에포크 수를 늘려보세요.
   ```

## 📧 연락처

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.

## � 문서 및 가이드

### 📖 **완전한 문서 세트**
- 🚀 **[빠른 시작 가이드](QUICK_START.md)** - 3분 만에 시작하기
- 📋 **[상세 사용 설명서](USER_MANUAL.md)** - 완전한 사용법 가이드 (50+ 페이지)
- 💡 **[예제 및 튜토리얼](EXAMPLES.md)** - 6가지 실제 사용 사례
- 🆘 **[지원 및 문제해결](SUPPORT.md)** - 도움말 센터
- ✅ **[설치 체크리스트](CHECKLIST.md)** - 단계별 설치 확인

### 🗺️ **어떤 문서를 봐야 할까요?**

| 👤 상황 | 📖 추천 문서 | ⏱️ 소요시간 |
|---------|-------------|------------|
| 🆕 **처음 사용** | [📱 빠른 시작](QUICK_START.md) | 3분 |
| 🔍 **자세한 사용법** | [📋 사용 설명서](USER_MANUAL.md) | 15분 |
| 💻 **코드 예제** | [💡 예제 모음](EXAMPLES.md) | 10분 |
| 🐛 **문제 해결** | [🆘 지원 센터](SUPPORT.md) | 5분 |
| ⚡ **API 참조** | [📚 API 문서](USER_MANUAL.md#api-참조) | 5분 |

> 💡 **추천 학습 경로**: QUICK_START.md → EXAMPLES.md → USER_MANUAL.md

## �📄 라이선스

이 프로젝트는 MIT 라이선스하에 배포됩니다.