# 🚀 실행 가이드 - 웹캠 기반 실시간 자세 판단 AI 시스템

## 📋 목차
1. [환경 설정](#환경-설정)
2. [데이터 준비](#데이터-준비)
3. [실행 방법](#실행-방법)
4. [단계별 상세 실행](#단계별-상세-실행)
5. [실시간 모니터링 사용법](#실시간-모니터링-사용법)
6. [문제 해결](#문제-해결)

---

## 🔧 환경 설정

### 1단계: 프로젝트 폴더 이동
```powershell
cd "C:\Users\user\OneDrive\Desktop\test\skeleton_ver2"
```

### 2단계: 가상환경 활성화 (이미 완료됨)
```powershell
.\.venv\Scripts\Activate.ps1
```

### 3단계: 패키지 확인 (이미 설치됨)
```powershell
# 설치 확인
.\.venv\Scripts\python.exe -c "import mediapipe, cv2, tensorflow; print('✅ 모든 패키지 설치됨')"
```

---

## 📂 데이터 준비

### 자동 폴더 생성
```powershell
# 데이터 폴더 자동 생성
.\.venv\Scripts\python.exe run_system.py --setup
```

### 수동 데이터 추가
1. **정상 자세 이미지**: `data/train_images/normal/` 폴더에 넣기
2. **비정상 자세 이미지**: `data/train_images/abnormal/` 폴더에 넣기
3. **권장 개수**: 각 클래스당 최소 10장 이상

---

## 🎯 실행 방법

### 🌟 방법 1: 원클릭 실행 (추천)
```powershell
# 전체 시스템 자동 실행 (전처리 → 훈련 → 실시간 모니터링)
.\.venv\Scripts\python.exe run_system.py --step all
```

### 🔧 방법 2: 단계별 실행
```powershell
# 1단계: 이미지 전처리
.\.venv\Scripts\python.exe run_system.py --step preprocess

# 2단계: LSTM 모델 훈련
.\.venv\Scripts\python.exe run_system.py --step train

# 3단계: 실시간 웹캠 모니터링
.\.venv\Scripts\python.exe run_system.py --step monitor
```

### 🎮 방법 3: 개별 스크립트 실행
```powershell
# 전처리만 실행
.\.venv\Scripts\python.exe src/preprocessing.py --input data/train_images --labeled

# 모델 훈련만 실행
.\.venv\Scripts\python.exe src/lstm_model.py --data data/pose_data.csv --epochs 50

# 실시간 모니터링만 실행
.\.venv\Scripts\python.exe src/realtime_cam.py --camera 0
```

---

## 📊 단계별 상세 실행

### 1️⃣ 1단계: 이미지 전처리
**목적**: 이미지에서 자세 데이터 추출

```powershell
.\.venv\Scripts\python.exe src/preprocessing.py --input data/train_images --labeled --output data
```

**출력 파일**:
- `data/pose_data.csv`: 포즈 데이터
- `data/pose_statistics.csv`: 통계 정보

**성공 메시지**:
```
INFO: 라벨링된 이미지 로드: Normal X개, Abnormal Y개
INFO: CSV 저장 완료: data/pose_data.csv
INFO: 통계 저장 완료: data/pose_statistics.csv
```

### 2️⃣ 2단계: LSTM 모델 훈련
**목적**: 자세 분류 AI 모델 학습

```powershell
.\.venv\Scripts\python.exe src/lstm_model.py --data data/pose_data.csv --epochs 50 --batch_size 16
```

**출력 파일**:
- `models/posture_lstm_model.h5`: 훈련된 모델
- `models/scaler.pkl`: 데이터 스케일러
- `models/label_encoder.pkl`: 라벨 인코더
- `models/model_metadata.json`: 메타데이터

**성공 메시지**:
```
INFO: 모델 구성 중...
INFO: 모델 훈련 시작...
INFO: 테스트 정확도: 0.XXXX
INFO: 모델 저장 완료
```

### 3️⃣ 3단계: 실시간 웹캠 모니터링
**목적**: 실시간 자세 분석 및 피드백

```powershell
.\.venv\Scripts\python.exe src/realtime_cam.py --camera 0
```

**시작 메시지**:
```
INFO: 모델 로드 완료
INFO: 실시간 자세 모니터링 시작 (ESC키로 종료)
```

---

## 📹 실시간 모니터링 사용법

### 🎮 키보드 조작
- **ESC**: 프로그램 종료
- **R**: 시스템 리셋 (예측 버퍼 초기화)

### 📊 화면 정보
- **Posture**: 현재 자세 상태 (NORMAL/ABNORMAL)
- **Confidence**: 예측 신뢰도 (0.0 ~ 1.0)
- **FPS**: 초당 프레임 수
- **상태 메시지**: 자세 교정 알림

### 🎨 색상 의미
- **초록색**: 정상 자세 (Good posture!)
- **빨간색**: 비정상 자세 (Please correct your posture!)
- **회색**: 인식 중 (Unknown)

### ⚠️ 알림 시스템
- 비정상 자세가 3초 이상 지속되면 알림
- 콘솔에 "⚠️ 자세 교정이 필요합니다!" 메시지 출력

---

## 🛠️ 문제 해결

### ❌ 자주 발생하는 문제들

#### 1. 카메라 접근 오류
```
ERROR: 카메라를 열 수 없습니다: 0
```
**해결책**:
- 다른 프로그램에서 카메라 사용 중인지 확인
- 카메라 번호 변경: `--camera 1`

#### 2. 모델 파일 없음
```
WARNING: 모델 파일을 찾을 수 없습니다
```
**해결책**:
- 먼저 훈련 실행: `run_system.py --step train`

#### 3. 훈련 데이터 부족
```
ERROR: 훈련 데이터가 없습니다
```
**해결책**:
- `data/train_images/normal/`과 `abnormal/` 폴더에 이미지 추가

#### 4. 패키지 import 오류
```
ModuleNotFoundError: No module named 'mediapipe'
```
**해결책**:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 💡 성능 개선 팁

#### 더 나은 정확도를 위해:
1. **더 많은 데이터**: 각 클래스당 50장 이상
2. **다양한 각도**: 정면, 측면, 다양한 조명
3. **고품질 이미지**: 선명하고 전신이 보이는 이미지

#### 더 빠른 처리를 위해:
1. **GPU 사용**: CUDA 설치 (선택사항)
2. **카메라 해상도 조정**: 720p 권장
3. **에폭 수 조정**: 빠른 테스트시 `--epochs 20`

---

## 📈 실행 순서 요약

### 🎯 첫 실행 (데이터 준비됨)
```powershell
# 1. 폴더 생성 (선택사항)
.\.venv\Scripts\python.exe run_system.py --setup

# 2. 전체 실행
.\.venv\Scripts\python.exe run_system.py --step all
```

### 🔄 재실행 (모델 이미 훈련됨)
```powershell
# 실시간 모니터링만 실행
.\.venv\Scripts\python.exe run_system.py --step monitor
```

### 🧪 테스트 실행
```powershell
# 빠른 테스트 (적은 에폭)
.\.venv\Scripts\python.exe src/lstm_model.py --epochs 10 --batch_size 8
```

---

## 🎉 성공 지표

### ✅ 전처리 성공
- "CSV 저장 완료" 메시지
- `data/pose_data.csv` 파일 생성
- 통계 정보 출력

### ✅ 훈련 성공
- 정확도 0.7 이상
- "모델 저장 완료" 메시지
- `models/` 폴더에 파일들 생성

### ✅ 실시간 모니터링 성공
- 웹캠 화면 표시
- 자세 인식 및 상태 표시
- FPS 30 이상 유지

---

## 📞 추가 도움

문제가 계속 발생하면:
1. 터미널의 에러 메시지 확인
2. 데이터 폴더 구조 점검
3. 가상환경 활성화 상태 확인
4. README.md의 상세 설명 참조