# skeltonpose 실행 가이드

간단한 사용법만 빠르게 보고 싶을 때 이 파일을 참조하세요.

## 프로젝트 개요
- **주요 기능**: 이미지에서 상체 스켈레톤 검출 및 각도 분석
- **권장 Python 버전**: 3.10
- **현재 Python 환경**: 3.10.1 (venv 활성화됨)
- **의존성**: `requirements.txt` (mediapipe, opencv-python, pandas, numpy)

## 폴더 구조
- **입력 폴더**: `labeling_test_images` (분석할 이미지들)
- **출력 폴더**: 
  - `processed_images` (스켈레톤이 그려진 처리된 이미지)
  - `csv_results` (좌표 및 각도 분석 결과 CSV)
  - `labeled` (GUI로 라벨링된 이미지)

## Windows PowerShell 실행 방법

### 1. 의존성 설치 (최초 1회만)
```powershell
# 프로젝트 폴더로 이동
cd "C:\Users\user\OneDrive\Desktop\test\skeleton_ver2"

# 가상환경 활성화 (이미 생성되어 있음)
.\.venv\Scripts\Activate.ps1

# 필요한 패키지 설치
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. 스켈레톤 분석 실행
```powershell
# 기본 실행 (labeling_test_images 폴더의 이미지들을 분석)
.\.venv\Scripts\python.exe skeltonpose.py

# 사용자 정의 옵션으로 실행
.\.venv\Scripts\python.exe skeltonpose.py --input_folder labeling_test_images --processed_folder processed_images --csv_folder csv_results

# 원본 이미지를 덮어쓰지 않고 _skeleton.jpg로 저장
.\.venv\Scripts\python.exe skeltonpose.py --no_overwrite

# 원본 이미지 백업하면서 실행
.\.venv\Scripts\python.exe skeltonpose.py --backup backup_folder
```

### 3. 이미지 라벨링 GUI 실행
```powershell
# 이미지 라벨링 GUI 시작 (normal/abnormal 분류)
.\.venv\Scripts\python.exe image_labeler_gui.py

# 사용자 정의 옵션으로 GUI 실행
.\.venv\Scripts\python.exe image_labeler_gui.py --input labeling_test_images --out labeled --mode copy
```

## 명령어 옵션 설명

### skeltonpose.py 옵션
- `--input_folder`: 입력 이미지 폴더 (기본: labeling_test_images)
- `--processed_folder`: 처리된 이미지 저장 폴더 (기본: processed_images)
- `--csv_folder`: CSV 결과 저장 폴더 (기본: csv_results)
- `--result`: 결과 CSV 파일명 (기본: skeleton_coords.csv)
- `--no_overwrite`: 원본을 덮어쓰지 않고 _skeleton.jpg로 저장
- `--backup`: 원본을 백업할 폴더 경로

### image_labeler_gui.py 옵션
- `--input`: 입력 폴더 (기본: labeling_test_images)
- `--out`: 출력 기본 폴더 (기본: labeled)
- `--mode`: 동작 모드 - copy(복사) 또는 move(이동) (기본: copy)
- `--normal`: normal 하위폴더명 (기본: normal)
- `--abnormal`: abnormal 하위폴더명 (기본: abnormal)

## GUI 단축키
- **N**: Normal로 분류
- **A**: Abnormal로 분류  
- **S**: 건너뛰기
- **U**: 실행 취소
- **Q**: 종료

## 출력 파일
1. `skeleton_coords.csv`: 랜드마크 좌표 정보
2. `skeleton_angles.csv`: 목, 어깨, 엉덩이 각도 정보
3. 처리된 이미지: 스켈레톤이 그려진 이미지들

## 빠른 실행 (현재 환경에서 바로 실행 가능)

현재 환경은 **모든 패키지가 설치되어 있고 바로 실행 가능한 상태**입니다!

### 🚀 바로 실행하기
```powershell
# 1. 스켈레톤 분석 실행
.\.venv\Scripts\python.exe skeltonpose.py

# 2. 이미지 라벨링 GUI 실행  
.\.venv\Scripts\python.exe image_labeler_gui.py
```

### 📊 결과 확인
- `processed_images/`: 스켈레톤이 그려진 처리된 이미지
- `csv_results/skeleton_coords.csv`: 랜드마크 좌표 데이터
- `csv_results/skeleton_angles.csv`: 각도 분석 데이터
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

