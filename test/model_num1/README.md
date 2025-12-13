# 🤖 웹캠 기반 실시간 자세 판단 AI 시스템# 웹캠 기반 실시간 자세 판단 AI 시스템# skeltonpose 실행 가이드



MediaPipe와 LSTM을 활용한 실시간 자세 교정 AI 시스템입니다.



## 📁 프로젝트 구조이 프로젝트는 MediaPipe와 LSTM을 활용한 실시간 자세 교정 시스템입니다.간단한 사용법만 빠르게 보고 싶을 때 이 파일을 참조하세요.

```

skeleton_ver2/

├── data/                       # 데이터 폴더

│   ├── train_images/          # 훈련 이미지## 프로젝트 구조## 프로젝트 개요

│   │   ├── normal/           # 정상 자세 이미지

│   │   └── abnormal/         # 비정상 자세 이미지```- **주요 기능**: 이미지에서 상체 스켈레톤 검출 및 각도 분석

│   ├── pose_data.csv         # 추출된 포즈 데이터

│   └── pose_statistics.csv   # 통계 데이터skeleton_ver2/- **권장 Python 버전**: 3.10

├── models/                    # 저장된 모델들

│   ├── posture_lstm_model.h5  # 훈련된 LSTM 모델├── data/                    # 데이터 폴더- **현재 Python 환경**: 3.10.1 (venv 활성화됨)

│   ├── scaler.pkl            # 데이터 스케일러

│   ├── label_encoder.pkl     # 라벨 인코더│   └── train_images/       # 훈련 이미지들- **의존성**: `requirements.txt` (mediapipe, opencv-python, pandas, numpy)

│   └── model_metadata.json   # 모델 메타데이터

├── src/                      # 소스 코드├── models/                 # 저장된 모델들

│   ├── preprocessing.py      # 1단계: 이미지 전처리

│   ├── lstm_model.py        # 2단계: LSTM 모델├── src/                   # 소스 코드## 폴더 구조

│   └── realtime_cam.py      # 3단계: 실시간 웹캠 시스템

├── run_system.py            # 통합 실행 스크립트│   ├── preprocessing.py   # 1단계: 이미지 전처리- **입력 폴더**: `labeling_test_images` (분석할 이미지들)

├── requirements.txt         # 의존성 패키지

└── README.md               # 이 파일│   ├── lstm_model.py     # 2단계: LSTM 모델- **출력 폴더**: 

```

│   └── realtime_cam.py   # 3단계: 실시간 웹캠 시스템  - `processed_images` (스켈레톤이 그려진 처리된 이미지)

## 🚀 빠른 시작

├── requirements.txt      # 의존성 패키지  - `csv_results` (좌표 및 각도 분석 결과 CSV)

### 1. 환경 설정

```powershell└── README.md            # 이 파일  - `labeled` (GUI로 라벨링된 이미지)

cd "C:\Users\user\OneDrive\Desktop\test\skeleton_ver2"

python -m venv .venv```

.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt## Windows PowerShell 실행 방법

```

## 설치 및 실행

### 2. 통합 실행 (권장)

```powershell### 1. 의존성 설치 (최초 1회만)

# 샘플 데이터 폴더 생성

.\.venv\Scripts\python.exe run_system.py --setup### 1. 환경 설정```powershell



# 전체 시스템 실행 (전처리 → 훈련 → 실시간 모니터링)```powershell# 프로젝트 폴더로 이동

.\.venv\Scripts\python.exe run_system.py --step all

```cd "C:\Users\user\OneDrive\Desktop\test\skeleton_ver2"cd "C:\Users\user\OneDrive\Desktop\test\skeleton_ver2"



### 3. 단계별 실행python -m venv .venv

```powershell

# 1단계: 이미지 전처리.\.venv\Scripts\Activate.ps1# 가상환경 활성화 (이미 생성되어 있음)

.\.venv\Scripts\python.exe run_system.py --step preprocess

pip install -r requirements.txt.\.venv\Scripts\Activate.ps1

# 2단계: LSTM 모델 훈련

.\.venv\Scripts\python.exe run_system.py --step train```



# 3단계: 실시간 웹캠 실행# 필요한 패키지 설치

.\.venv\Scripts\python.exe run_system.py --step monitor

```### 2. 단계별 실행.\.venv\Scripts\python.exe -m pip install -r requirements.txt



## 📋 개발 단계```powershell```



### 1단계: 이미지 전처리 (preprocessing.py)# 1단계: 이미지 전처리

**목적**: 이미지에서 자세 특성 추출 및 CSV 생성

.\.venv\Scripts\python.exe src/preprocessing.py### 2. 스켈레톤 분석 실행

**기능**:

- MediaPipe를 이용한 스켈레톤 추출```powershell

- 상체 랜드마크 (목, 어깨, 허리) 좌표 추출

- 자세 각도 계산 (목 기울기, 어깨 기울기, 허리 기울기, 상체 기울기)# 2단계: LSTM 모델 훈련# 기본 실행 (labeling_test_images 폴더의 이미지들을 분석)

- 통계 계산 (평균, 분산, 표준편차)

- 라벨별 분석 (normal/abnormal).\.venv\Scripts\python.exe src/lstm_model.py.\.venv\Scripts\python.exe skeltonpose.py



**출력**:

- `pose_data.csv`: 모든 이미지의 포즈 데이터

- `pose_statistics.csv`: 통계 정보# 3단계: 실시간 웹캠 실행# 라벨링된 이미지 분석 (normal/abnormal 폴더 구조)



### 2단계: LSTM 평가 모델 (lstm_model.py).\.venv\Scripts\python.exe src/realtime_cam.py.\.venv\Scripts\python.exe skeltonpose.py --input_folder labeled --use_labeled --processed_folder processed_labeled --csv_folder csv_labeled

**목적**: 시계열 자세 데이터를 학습하는 분류 모델

```

**기능**:

- CSV 데이터 기반 LSTM 신경망# 사용자 정의 옵션으로 실행

- 시퀀스 데이터 생성 (시간적 패턴 학습)

- 데이터 증강 (노이즈 추가, 스케일링)## 개발 단계.\.venv\Scripts\python.exe skeltonpose.py --input_folder labeling_test_images --processed_folder processed_images --csv_folder csv_results

- 정상/비정상 자세 이진 분류

- 모델 성능 평가 및 시각화



**특징**:### 1단계: 이미지 전처리 (preprocessing.py)# 원본 이미지를 덮어쓰지 않고 _skeleton.jpg로 저장

- 양방향 LSTM 레이어

- Dropout과 BatchNormalization으로 과적합 방지- MediaPipe로 스켈레톤 추출.\.venv\Scripts\python.exe skeltonpose.py --no_overwrite

- EarlyStopping과 학습률 조절

- 상체 데이터(목, 어깨, 허리) CSV 저장

### 3단계: 실시간 웹캠 시스템 (realtime_cam.py)

**목적**: 웹캠을 통한 실시간 자세 모니터링- 통계(평균, 분산) 계산# 원본 이미지 백업하면서 실행



**기능**:.\.venv\Scripts\python.exe skeltonpose.py --backup backup_folder

- 실시간 웹캠 입력 처리

- MediaPipe로 실시간 포즈 추출### 2단계: LSTM 평가 모델 (lstm_model.py)```

- 학습된 LSTM 모델로 자세 예측

- 시각적 피드백 (포즈 랜드마크, 상태 표시)- CSV 데이터 기반 LSTM 모델

- 자세 교정 알림 시스템

- 예측 결과 스무딩 (노이즈 제거)- 정상/비정상 자세 분류### 3. 이미지 라벨링 GUI 실행



**제어**:```powershell

- `ESC`: 종료

- `R`: 시스템 리셋### 3단계: 실시간 웹캠 시스템 (realtime_cam.py)# 이미지 라벨링 GUI 시작 (normal/abnormal 분류)



## 🎯 사용법- 웹캠 입력으로 실시간 자세 평가.\.venv\Scripts\python.exe image_labeler_gui.py



### 데이터 준비- 시각적 피드백 제공

1. `data/train_images/normal/`에 정상 자세 이미지 추가# 사용자 정의 옵션으로 GUI 실행

2. `data/train_images/abnormal/`에 비정상 자세 이미지 추가.\.venv\Scripts\python.exe image_labeler_gui.py --input labeling_test_images --out labeled --mode copy

3. 최소 각 클래스당 10장 이상 권장```



### 모델 훈련## 명령어 옵션 설명

```powershell

# 개별 실행### skeltonpose.py 옵션

.\.venv\Scripts\python.exe src/preprocessing.py --input data/train_images --labeled- `--input_folder`: 입력 이미지 폴더 (기본: labeling_test_images)

.\.venv\Scripts\python.exe src/lstm_model.py --data data/pose_data.csv --epochs 100- `--processed_folder`: 처리된 이미지 저장 폴더 (기본: processed_images)

- `--csv_folder`: CSV 결과 저장 폴더 (기본: csv_results)

# 통합 실행- `--result`: 결과 CSV 파일명 (기본: skeleton_coords.csv)

.\.venv\Scripts\python.exe run_system.py --step all- `--use_labeled`: 라벨링된 폴더 구조 사용 (normal/abnormal 하위폴더)

```- `--no_overwrite`: 원본을 덮어쓰지 않고 _skeleton.jpg로 저장

- `--backup`: 원본을 백업할 폴더 경로

### 실시간 모니터링

```powershell### image_labeler_gui.py 옵션

.\.venv\Scripts\python.exe src/realtime_cam.py --camera 0- `--input`: 입력 폴더 (기본: labeling_test_images)

```- `--out`: 출력 기본 폴더 (기본: labeled)

- `--mode`: 동작 모드 - copy(복사) 또는 move(이동) (기본: copy)

## 📊 성능 최적화- `--normal`: normal 하위폴더명 (기본: normal)

- `--abnormal`: abnormal 하위폴더명 (기본: abnormal)

### 모델 파라미터 조정

- `sequence_length`: 시퀀스 길이 (기본: 10)## GUI 단축키

- `lstm_units`: LSTM 유닛 수 (기본: 128)- **N**: Normal로 분류

- `epochs`: 훈련 에폭 (기본: 100)- **A**: Abnormal로 분류  

- `batch_size`: 배치 크기 (기본: 32)- **S**: 건너뛰기

- **U**: 실행 취소

### 데이터 품질 향상- **Q**: 종료

- 다양한 각도의 이미지 수집

- 조명 조건 다양화## 출력 파일

- 충분한 데이터량 확보 (클래스당 50장 이상)1. `skeleton_coords.csv`: 랜드마크 좌표 정보 (라벨 정보 포함)

2. `skeleton_angles.csv`: 목, 어깨, 엉덩이 각도 정보 (라벨 정보 포함)

## 🔧 문제 해결3. 처리된 이미지: 스켈레톤이 그려진 이미지들 (라벨에 따른 색상 구분)

   - Normal: 초록색 텍스트

### 일반적인 문제   - Abnormal: 빨간색 텍스트

- **카메라 접근 오류**: 다른 프로그램에서 카메라 사용 중인지 확인

- **모델 로드 실패**: 모델 파일 경로와 의존성 파일 확인## 라벨링된 분석 결과 예시 (현재 데이터)

- **낮은 정확도**: 훈련 데이터 품질과 양 확인- **Normal 이미지 (3개)**: 

  - 목 각도 평균: 132.34°, 표준편차: 3.85°

### 성능 개선  - 어깨 각도 평균: 102.40°, 표준편차: 67.69°

- GPU 사용 설정 (CUDA 설치)  - 엉덩이 각도 평균: 89.54°, 표준편차: 64.46°

- 더 많은 훈련 데이터 수집

- 하이퍼파라미터 튜닝- **Abnormal 이미지 (9개)**:

  - 목 각도 평균: 8.08°, 표준편차: 123.70°

## 📈 확장 가능성  - 어깨 각도 평균: -2.43°, 표준편차: 120.75°

  - 엉덩이 각도 평균: -8.60°, 표준편차: 113.01°

### 추가 기능

- 더 많은 자세 클래스 (slouching, leaning, etc.)## 빠른 실행 (현재 환경에서 바로 실행 가능)

- 음성 알림 시스템

- 웹 인터페이스 개발현재 환경은 **모든 패키지가 설치되어 있고 바로 실행 가능한 상태**입니다!

- 자세 기록 및 분석 리포트

- 모바일 앱 연동### 🚀 바로 실행하기

```powershell

### 고급 기능# 1. 스켈레톤 분석 실행 (기본)

- 3D 포즈 추정.\.venv\Scripts\python.exe skeltonpose.py

- 실시간 자세 교정 가이드

- 개인별 맞춤 임계값 설정# 2. 라벨링된 이미지 분석 (추천)

- 장시간 자세 패턴 분석.\.venv\Scripts\python.exe skeltonpose.py --input_folder labeled --use_labeled --processed_folder processed_labeled --csv_folder csv_labeled



## 💡 현재 환경 상태# 3. 이미지 라벨링 GUI 실행  

- ✅ Python 3.10.1 가상환경 활성화됨.\.venv\Scripts\python.exe image_labeler_gui.py

- ✅ 모든 의존성 패키지 설치 완료```

- ✅ 바로 실행 가능한 상태

### 📊 결과 확인

## 📞 지원- `processed_images/`: 스켈레톤이 그려진 처리된 이미지

문제가 발생하면 각 단계별 로그를 확인하고, 데이터와 모델 파일 상태를 점검해주세요.- `csv_results/skeleton_coords.csv`: 랜드마크 좌표 데이터
- `csv_results/skeleton_angles.csv`: 각도 분석 데이터
- `processed_labeled/`: 라벨링된 이미지의 스켈레톤 처리 결과 (라벨 정보 포함)
- `csv_labeled/`: 라벨별 분석 결과 (normal/abnormal별 통계 포함)
- `labeled/normal/`, `labeled/abnormal/`: GUI로 분류된 이미지

## 문제 해결
- **가상환경 활성화 오류**: PowerShell 실행 정책 문제시 `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` 실행
- **Mediapipe 설치 오류**: Visual C++ 재배포 패키지 설치 필요
- **이미지 로드 실패**: 파일 경로에 한글이나 특수문자가 있는지 확인
- **메모리 부족**: 큰 이미지들은 배치로 나누어 처리

## 환경 상태 확인
- ✅ Python 3.10.1 가상환경 활성화됨
- ✅ 모든 의존성 패키지 설치 완료 (mediapipe, opencv-python, pandas, numpy, pillow 등)
- ✅ 바로 실행 가능한 상태

