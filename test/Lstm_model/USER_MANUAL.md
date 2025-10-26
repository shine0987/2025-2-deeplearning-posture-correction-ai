# 자세 분류 LSTM 모델 사용 설명서
**정상/비정상 자세 분류를 위한 딥러닝 모델 완전 가이드**

---

## 📖 **목차**
1. [🎯 시작하기 전에](#시작하기-전에) - 이 프로그램이 하는 일
2. [⚙️ 설치 및 환경 설정](#설치-및-환경-설정) - 4단계 설치 가이드  
3. [📁 데이터 준비하기](#데이터-준비하기) - CSV 파일 형식 및 구조
4. [🚀 기본 사용법](#기본-사용법) - 대화형/명령행 모드
5. [🔥 고급 사용법](#고급-사용법) - Python 코드 활용
6. [📚 API 참조](#api-참조) - 함수 및 클래스 문서
7. [🔧 문제 해결](#문제-해결) - 오류 해결 가이드
8. [❓ FAQ](#faq) - 자주 묻는 질문

> 💡 **급하신가요?** [빠른 시작 가이드](QUICK_START.md)를 먼저 보세요!

---

## 🎯 시작하기 전에

### 🤖 **이 프로그램이 하는 일**
- 📊 **스켈레톤 데이터 분석**: 각도(목, 어깨, 엉덩이)와 좌표 정보를 AI로 분석
- ✅ **자세 분류**: 정상 자세 vs 비정상 자세 자동 판별 (slouch, hunchback 등)
- ⚡ **실시간 평가**: 새로운 데이터에 대한 즉시 분석 결과 제공
- 📈 **성능 분석**: 정확도, 신뢰도 등 상세한 분석 리포트

### 👨‍💻 **필요한 기본 지식**
- ✅ **필수**: Python 기본 사용법 (변수, 함수 호출)
- ✅ **필수**: CSV 파일 열기/저장하기
- ✅ **권장**: 명령 프롬프트/터미널 기본 사용법
- ❌ **불필요**: 딥러닝, 머신러닝 전문 지식

### 💻 **시스템 요구사항**

| 구분 | 최소 사양 | 권장 사양 |
|------|-----------|-----------|
| **OS** | Windows 10, macOS 10.15, Ubuntu 18.04 | Windows 11, macOS 12+, Ubuntu 20.04+ |
| **Python** | 3.8+ | 3.9+ |
| **RAM** | 4GB | 8GB+ |
| **저장공간** | 2GB | 5GB+ |
| **CPU** | 듀얼코어 | 쿼드코어+ |
| **GPU** | 불필요 (CPU만으로 충분) | NVIDIA GPU (선택사항) |

### 🕐 **예상 소요 시간**
- **설치**: 5-10분
- **첫 모델 훈련**: 2-5분 (데이터 크기에 따라)
- **데이터 평가**: 30초-2분
- **전체 학습**: 30분-1시간

---

## ⚙️ 설치 및 환경 설정

### 1단계: Python 설치 확인
```bash
python --version
```
Python 3.8 이상이 설치되어 있는지 확인하세요.

### 2단계: 프로젝트 다운로드
프로젝트 폴더를 원하는 위치에 복사하세요.

### 3단계: 필요한 패키지 설치
```bash
cd "프로젝트_폴더_경로"
pip install -r requirements.txt
```

### 4단계: 설치 확인
```bash
python main.py --mode info
```
오류 없이 실행되면 설치가 완료된 것입니다.

---

## 📁 데이터 준비하기

### 필요한 파일들

#### 1. 각도 데이터 파일 (skeleton_angles.csv)
```csv
image_path,neck_angle,shoulder_angle_deg,hip_angle_deg
image1.jpg,124.17,176.51,148.50
image2.jpg,-105.28,-56.03,-136.44
```

**컬럼 설명:**
- `image_path`: 이미지 파일명
- `neck_angle`: 목 각도
- `shoulder_angle_deg`: 어깨 각도
- `hip_angle_deg`: 엉덩이 각도

#### 2. 좌표 데이터 파일 (skeleton_coords.csv)
```csv
image_path,lm_0_x,lm_0_y,lm_0_x_px,lm_0_y_px,lm_11_x,lm_11_y,...
image1.jpg,0.465,0.192,128,35,0.397,0.249,...
image2.jpg,0.375,0.254,270,325,0.494,0.298,...
```

**컬럼 설명:**
- `image_path`: 이미지 파일명
- `lm_N_x`, `lm_N_y`: N번 랜드마크의 정규화된 좌표 (0-1)
- `lm_N_x_px`, `lm_N_y_px`: N번 랜드마크의 픽셀 좌표

#### 3. 라벨링된 이미지 (선택사항)
```
labeled/
├── normal/          # 정상 자세 이미지들
│   ├── img1.jpg
│   └── img2.jpg
└── abnormal/        # 비정상 자세 이미지들
    ├── slouch.jpg
    └── hunchback.jpg
```

### 데이터 형식 검증
```bash
python data_preprocessing.py
```
이 명령으로 데이터가 올바른 형식인지 확인할 수 있습니다.

---

## 🚀 기본 사용법

### 방법 1: 대화형 모드 (초보자 추천)

```bash
python main.py
```

메뉴가 나타나면 원하는 작업을 선택하세요:
```
1. train    - 모델 훈련
2. evaluate - 데이터 평가
3. info     - 모델 정보
4. quit     - 종료
```

### 방법 2: 명령행 모드

#### 모델 훈련하기
```bash
python main.py --mode train
```

**추가 옵션:**
```bash
python main.py --mode train --epochs 50 --batch_size 8
```

#### 데이터 평가하기
```bash
python main.py --mode evaluate
```

**새로운 CSV 파일 평가:**
```bash
python main.py --mode evaluate --angles_csv "새로운_각도.csv" --coords_csv "새로운_좌표.csv"
```

#### 모델 정보 확인
```bash
python main.py --mode info
```

---

## 🔥 고급 사용법

### Python 코드에서 직접 사용

#### 1. 모델 훈련
```python
from training_module import PostureTrainer

# 훈련기 초기화
trainer = PostureTrainer("데이터_폴더_경로", sequence_length=3)

# 사용자 정의 설정
config = {
    'use_angles': True,      # 각도 데이터 사용
    'use_coords': True,      # 좌표 데이터 사용
    'lstm_units': [64, 32],  # LSTM 유닛 수
    'dropout_rate': 0.3,     # 드롭아웃 비율
    'learning_rate': 0.001,  # 학습률
    'epochs': 100,           # 에포크 수
    'batch_size': 8,         # 배치 크기
}

# 훈련 실행
results = trainer.full_training_pipeline(config)
```

#### 2. 데이터 평가
```python
from external_data_interface import PostureEvaluator

# 평가기 초기화
evaluator = PostureEvaluator()

# 모델 로드
if evaluator.load_model():
    # CSV 파일 평가
    results = evaluator.evaluate_csv_data(
        "angles.csv", 
        "coords.csv",
        "결과저장경로.json"
    )
    
    print(f"총 샘플: {results['summary']['total_samples']}")
    print(f"정상: {results['summary']['normal_count']}")
    print(f"비정상: {results['summary']['abnormal_count']}")
```

#### 3. 단일 샘플 평가
```python
# 단일 이미지의 데이터
angles_data = {
    "neck_angle": 130.5,
    "shoulder_angle_deg": 165.2,
    "hip_angle_deg": 142.8
}

coords_data = {
    "lm_0_x": 0.465, "lm_0_y": 0.192,
    "lm_11_x": 0.397, "lm_11_y": 0.249,
    # ... 기타 좌표 데이터
}

# 평가 실행
result = evaluator.evaluate_single_sample(
    angles_data, 
    coords_data, 
    "test_image.jpg"
)

print(f"예측: {result['prediction']}")
print(f"신뢰도: {result['confidence']:.3f}")
```

### 모델 파라미터 커스터마이징

#### LSTM 아키텍처 변경
```python
# 더 복잡한 모델
config = {
    'lstm_units': [128, 64, 32],  # 3층 LSTM
    'dropout_rate': 0.4,          # 높은 드롭아웃
    'learning_rate': 0.0005,      # 낮은 학습률
}

# 더 간단한 모델
config = {
    'lstm_units': [16],           # 1층 LSTM
    'dropout_rate': 0.1,          # 낮은 드롭아웃
    'learning_rate': 0.01,        # 높은 학습률
}
```

#### 데이터 증강 설정
```python
from data_preprocessing import PostureDataProcessor

processor = PostureDataProcessor(sequence_length=5)
# sequence_length 조정으로 시계열 길이 변경
```

---

## 📚 API 참조

### PostureTrainer 클래스

#### `__init__(base_path, sequence_length=5)`
- **base_path**: 데이터 폴더 경로
- **sequence_length**: LSTM 시퀀스 길이

#### `full_training_pipeline(config=None)`
전체 훈련 파이프라인 실행

**config 옵션:**
```python
{
    'use_angles': bool,          # 각도 특성 사용 여부
    'use_coords': bool,          # 좌표 특성 사용 여부
    'lstm_units': list,          # LSTM 유닛 수 리스트
    'dropout_rate': float,       # 드롭아웃 비율 (0.0-1.0)
    'learning_rate': float,      # 학습률
    'epochs': int,               # 에포크 수
    'batch_size': int,           # 배치 크기
    'validation_split': float    # 검증 데이터 비율
}
```

### PostureEvaluator 클래스

#### `__init__(model_path=None, base_path=None)`
- **model_path**: 모델 파일 경로 (None이면 자동 탐지)
- **base_path**: 기본 폴더 경로

#### `load_model(model_path=None)`
모델 로드. 성공시 True 반환

#### `evaluate_csv_data(angles_csv, coords_csv, output_path=None)`
CSV 파일 평가

#### `evaluate_single_sample(angles_data, coords_data, image_name)`
단일 샘플 평가

---

## 🔧 문제 해결

### 자주 발생하는 오류들

#### 1. "모델을 찾을 수 없습니다"
```
원인: 훈련된 모델이 없음
해결: python main.py --mode train 실행
```

#### 2. "KeyError: 컬럼명"
```
원인: CSV 파일의 컬럼명이 예상과 다름
해결: 
- skeleton_angles.csv에 neck_angle, shoulder_angle_deg, hip_angle_deg 컬럼 확인
- skeleton_coords.csv에 lm_N_x, lm_N_y 형태의 컬럼 확인
```

#### 3. "메모리 부족"
```
원인: 배치 크기가 너무 큼
해결: --batch_size 4 옵션 사용
```

#### 4. "ModuleNotFoundError"
```
원인: 필요한 패키지가 설치되지 않음
해결: pip install -r requirements.txt 재실행
```

### 성능 개선 방법

#### 정확도가 낮을 때
1. **더 많은 데이터** 수집
2. **에포크 수 증가**: `--epochs 100`
3. **학습률 조정**: `learning_rate: 0.0001`
4. **모델 복합도 증가**: `lstm_units: [64, 32, 16]`

#### 훈련이 느릴 때
1. **배치 크기 증가**: `--batch_size 16`
2. **시퀀스 길이 감소**: `sequence_length=3`
3. **특성 수 줄이기**: `use_coords: False`

#### 과적합 발생 시
1. **드롭아웃 증가**: `dropout_rate: 0.5`
2. **조기 종료 활용** (자동 적용됨)
3. **검증 데이터 비율 증가**: `validation_split: 0.3`

---

## ❓ FAQ

### Q1: 어떤 형태의 데이터가 필요한가요?
**A**: 스켈레톤 키포인트에서 추출한 각도 데이터와 좌표 데이터가 필요합니다. OpenPose, MediaPipe 등에서 추출한 데이터를 사용할 수 있습니다.

### Q2: 몇 개의 데이터가 필요한가요?
**A**: 최소 20-30개의 샘플이 필요하지만, 좋은 성능을 위해서는 각 클래스당 최소 100개 이상을 권장합니다.

### Q3: 실시간으로 사용할 수 있나요?
**A**: 네, `evaluate_single_sample()` 함수를 사용하여 실시간 평가가 가능합니다.

### Q4: 다른 자세 분류도 가능한가요?
**A**: 네, labeled 폴더에 새로운 클래스를 추가하면 다중 클래스 분류도 가능합니다.

### Q5: GPU를 사용할 수 있나요?
**A**: TensorFlow가 자동으로 GPU를 감지하여 사용합니다. CUDA가 설치되어 있으면 GPU 가속이 적용됩니다.

### Q6: 모델을 다른 프로젝트에 사용할 수 있나요?
**A**: 네, 훈련된 .keras 파일을 복사하여 다른 프로젝트에서 사용할 수 있습니다.

---

## 📞 지원 및 연락처

문제가 해결되지 않으면:
1. README.md 파일 확인
2. 오류 메시지와 함께 이슈 등록
3. 데이터 샘플과 함께 문의

---

## 📄 라이선스
이 프로젝트는 MIT 라이선스하에 배포됩니다.

---

*마지막 업데이트: 2025년 10월 26일*