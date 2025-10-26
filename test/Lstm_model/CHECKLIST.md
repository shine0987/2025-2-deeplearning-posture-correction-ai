# ✅ 설치 및 사용 체크리스트

## 🚀 **설치 전 체크리스트**

### 📋 **시스템 준비**
- [ ] Windows 10/11, macOS 10.15+, 또는 Ubuntu 18.04+ 운영체제
- [ ] Python 3.8 이상 설치됨 (`python --version`으로 확인)
- [ ] pip 최신 버전 (`pip --version`으로 확인)
- [ ] 최소 2GB 여유 저장공간
- [ ] 인터넷 연결 (패키지 설치용)

### 📁 **파일 준비**
- [ ] 프로젝트 폴더 다운로드 완료
- [ ] `skeleton_angles.csv` 파일 존재
- [ ] `skeleton_coords.csv` 파일 존재
- [ ] `labeled/normal/` 폴더에 정상 자세 이미지 (선택사항)
- [ ] `labeled/abnormal/` 폴더에 비정상 자세 이미지 (선택사항)

---

## 🔧 **설치 체크리스트**

### 1️⃣ **환경 확인**
```bash
# 다음 명령어들이 모두 성공해야 함
python --version          # ✅ Python 3.8.x 이상
pip --version             # ✅ pip 20.0+ 
cd "프로젝트_폴더"         # ✅ 폴더 이동 성공
```

### 2️⃣ **패키지 설치**
```bash
pip install -r requirements.txt
```
- [ ] TensorFlow 설치 완료
- [ ] pandas 설치 완료  
- [ ] numpy 설치 완료
- [ ] scikit-learn 설치 완료
- [ ] matplotlib 설치 완료
- [ ] opencv-python 설치 완료

### 3️⃣ **설치 검증**
```bash
python -c "import tensorflow; print('TensorFlow OK')"
python -c "import pandas; print('Pandas OK')"
python -c "import numpy; print('NumPy OK')"
```
- [ ] 모든 import 문 성공
- [ ] 오류 메시지 없음

---

## 🎯 **첫 실행 체크리스트**

### 📊 **데이터 검증**
```bash
python data_preprocessing.py
```
**✅ 성공 시 나타나는 메시지:**
- [ ] "데이터 로딩 중..." 
- [ ] "각도 데이터: (N, M)" 형태 출력
- [ ] "좌표 데이터: (N, K)" 형태 출력
- [ ] "라벨 분포:" 정보 출력
- [ ] "데이터 전처리 완료!" 메시지

### 🤖 **모델 훈련**
```bash
python main.py --mode train --epochs 15
```
**✅ 성공 시 나타나는 메시지:**
- [ ] "모델 구성 중..." 
- [ ] "모델 훈련 시작..."
- [ ] Epoch 진행률 표시 (1/15, 2/15, ...)
- [ ] "모델 훈련 완료!"
- [ ] "최종 테스트 정확도: X.XXXX"

### 🔍 **모델 평가**
```bash
python main.py --mode evaluate
```
**✅ 성공 시 나타나는 메시지:**
- [ ] "최신 모델 발견: ..."
- [ ] "모델 로드 완료!"
- [ ] "CSV 데이터 평가 시작..."
- [ ] "평가 완료! 총 N개 샘플 처리"

---

## 📁 **파일 생성 체크리스트**

### 🗂️ **생성되어야 할 폴더들**
- [ ] `models/` - 훈련된 모델 저장
- [ ] `results/` - 결과 및 로그 파일
- [ ] `__pycache__/` - Python 캐시 (자동 생성)

### 📄 **생성되어야 할 파일들**
**모델 파일:**
- [ ] `models/posture_lstm_model_날짜시간.keras`
- [ ] `models/posture_lstm_model_날짜시간_metadata.json`

**결과 파일:**
- [ ] `results/training_results_날짜시간.json`
- [ ] `results/training_history_날짜시간.png`
- [ ] `results/confusion_matrix_날짜시간.png`
- [ ] `results/evaluation_results_날짜시간.json`

---

## 🧪 **기능 테스트 체크리스트**

### 🎛️ **대화형 모드**
```bash
python main.py
```
- [ ] 메뉴 정상 출력 (1. train, 2. evaluate, 3. info, 4. quit)
- [ ] 각 메뉴 선택 시 해당 기능 실행
- [ ] 'quit' 선택 시 정상 종료

### 📊 **모델 정보 확인**
```bash
python main.py --mode info
```
- [ ] 모델 경로 출력
- [ ] 시퀀스 길이 출력
- [ ] 클래스 정보 출력 (['abnormal', 'normal'])

### 🐍 **Python API 테스트**
```python
from external_data_interface import PostureEvaluator
evaluator = PostureEvaluator()
print("✅ API 로드 성공" if evaluator.load_model() else "❌ API 로드 실패")
```
- [ ] 오류 없이 import 성공
- [ ] 모델 로드 성공 메시지

---

## ⚠️ **문제 발생 시 체크리스트**

### 🚨 **일반적인 오류들**

**❌ "ModuleNotFoundError"**
- [ ] `pip install -r requirements.txt` 재실행
- [ ] Python 가상환경 활성화 확인
- [ ] Python 버전 확인 (3.8+ 필요)

**❌ "KeyError: 컬럼명"**
- [ ] CSV 파일 첫 줄(헤더) 확인
- [ ] 필수 컬럼 존재 확인: neck_angle, shoulder_angle_deg, hip_angle_deg
- [ ] 파일 인코딩 확인 (UTF-8 권장)

**❌ "모델을 찾을 수 없습니다"**
- [ ] `models/` 폴더 존재 확인
- [ ] 먼저 `python main.py --mode train` 실행
- [ ] 훈련 완료 메시지 확인

**❌ "메모리 부족"**  
- [ ] 배치 크기 줄이기: `--batch_size 2`
- [ ] 불필요한 프로그램 종료
- [ ] 시스템 메모리 확인

### 🔍 **디버깅 명령어**
```bash
# 전체 시스템 상태 확인
python --version && pip --version
python -c "import sys; print(f'Python 경로: {sys.executable}')"
ls -la *.csv    # 데이터 파일 확인
ls -la models/  # 모델 파일 확인

# 단계별 테스트
python data_preprocessing.py    # 데이터 처리 테스트
python lstm_model.py           # 모델 아키텍처 테스트
python main.py --mode info     # 전체 시스템 테스트
```

---

## 🎉 **완료 확인**

### ✅ **모든 기능이 정상 작동하는지 최종 확인**
- [ ] 데이터 전처리 성공
- [ ] 모델 훈련 성공 (정확도 0.5 이상)
- [ ] 모델 평가 성공
- [ ] 결과 파일들 생성됨
- [ ] Python API 사용 가능
- [ ] 대화형 모드 작동

### 🚀 **이제 할 수 있는 것들**
- [ ] 새로운 CSV 데이터로 자세 분석
- [ ] Python 코드에서 실시간 자세 평가
- [ ] 모델 파라미터 조정으로 성능 향상
- [ ] 배치 처리로 대량 데이터 분석
- [ ] 웹캠이나 센서와 연동

---

**🎊 축하합니다! 자세 분류 AI 모델이 준비되었습니다!**

> 💡 **다음 단계**: [EXAMPLES.md](EXAMPLES.md)에서 더 많은 활용 예제를 확인해보세요!