# 🚀 빠른 시작 가이드
**3분 만에 자세 분류 모델 실행하기**

> ⚡ **급하신가요?** 아래 4단계만 따라하면 바로 사용할 수 있습---

# 🆕 **새로운 데이터로 자세 분석하기**

## 📋 **1단계: CSV 파일 준비**
---

## ✅ **사전 준비** (30초)
```bash
# Python 설치 확인 (3.8 이상 필요)
python --version

# 프로젝트 폴더로 이동
cd "c:\Users\user\OneDrive\Desktop\test\Lstm_model"
```

## 📦 **1단계: 패키지 설치** (1분)
```bash
# 필수 패키지 한 번에 설치
pip install -r requirements.txt
```

**⚠️ 설치 실패 시:**
```bash
# 개별 설치 (Windows 사용자)
pip install tensorflow pandas numpy scikit-learn matplotlib opencv-python
```

## 🎯 **2단계: 데이터 확인** (30초)
```bash
# 데이터 파일 확인
python data_preprocessing.py
```

**✅ 성공 메시지 예시:**
```
데이터 로딩 중...
각도 데이터: (12, 5)
좌표 데이터: (12, 22)
라벨 분포:
abnormal    9
normal      3
```

## 🏃 **3단계: 모델 훈련** (1분)
```bash
# 빠른 훈련 (테스트용)
python main.py --mode train --epochs 15 --batch_size 4
```

**✅ 성공 메시지 예시:**
```
✅ 모델 훈련 완료!
   최종 정확도: 0.7500
```

## 🔍 **4단계: 모델 평가** (30초)
```bash
# 기존 데이터로 평가 테스트
python main.py --mode evaluate
```

**✅ 성공 메시지 예시:**
```
✅ 데이터 평가 완료!
   총 샘플: 8
   정상 자세: 6
   비정상 자세: 2
```

---

## 🎉 **완료!**
축하합니다! 이제 다음 파일들이 생성되었습니다:

📁 **생성된 파일들:**
- `models/posture_lstm_model_날짜시간.keras` - 훈련된 AI 모델
- `results/training_results_날짜시간.json` - 훈련 결과
- `results/evaluation_results_날짜시간.json` - 평가 결과
- `results/training_history_날짜시간.png` - 훈련 그래프
- `results/confusion_matrix_날짜시간.png` - 성능 분석 차트

---

# 새로운 데이터 사용하기

## 1. CSV 파일 준비
### 📐 **angles.csv** (각도 데이터)
```csv
image_path,neck_angle,shoulder_angle_deg,hip_angle_deg
person1.jpg,125.5,170.2,145.8
person2.jpg,-110.3,-60.1,-140.5
person3.jpg,132.1,168.5,149.3
```

### 📍 **coords.csv** (좌표 데이터)
```csv
image_path,lm_0_x,lm_0_y,lm_0_x_px,lm_0_y_px,lm_11_x,lm_11_y,lm_11_x_px,lm_11_y_px,lm_12_x,lm_12_y,lm_12_x_px,lm_12_y_px,lm_23_x,lm_23_y,lm_23_x_px,lm_23_y_px,lm_24_x,lm_24_y,lm_24_x_px,lm_24_y_px
person1.jpg,0.47,0.19,150,40,0.40,0.25,120,60,0.37,0.26,111,63,0.30,0.46,90,110,0.26,0.48,78,115
person2.jpg,0.38,0.26,280,330,0.49,0.30,375,385,0.51,0.28,385,360,0.75,0.45,568,585,0.72,0.43,548,550
person3.jpg,0.48,0.20,145,48,0.39,0.25,115,60,0.37,0.26,111,63,0.30,0.46,90,113,0.27,0.48,80,118
```

## 🚀 **2단계: 평가 실행**
```bash
python main.py --mode evaluate --angles_csv "angles.csv" --coords_csv "coords.csv"
```

## 📊 **3단계: 결과 확인**
`results/evaluation_results_날짜시간.json` 파일에서 결과를 확인하세요:

```json
{
  "predictions": [
    {
      "image_path": "person1.jpg",
      "prediction": "normal",
      "confidence": 0.823
    },
    {
      "image_path": "person2.jpg", 
      "prediction": "abnormal",
      "confidence": 0.745
    }
  ],
  "summary": {
    "total_samples": 3,
    "normal_count": 2,
    "abnormal_count": 1
  }
}
```

---

# 💻 **Python 코드에서 직접 사용하기**

### 🔧 **실시간 자세 분석 예제**
```python
from external_data_interface import PostureEvaluator

# 1. 평가기 초기화 및 모델 로드
evaluator = PostureEvaluator()
if not evaluator.load_model():
    print("❌ 모델 로드 실패! 먼저 훈련을 진행하세요.")
    exit()

# 2. 단일 샘플 평가 (실시간 데이터)
angles_data = {
    "neck_angle": 130, 
    "shoulder_angle_deg": 160, 
    "hip_angle_deg": 140
}

coords_data = {
    "lm_0_x": 0.5, "lm_0_y": 0.2, "lm_0_x_px": 150, "lm_0_y_px": 40,
    "lm_11_x": 0.4, "lm_11_y": 0.25, "lm_11_x_px": 120, "lm_11_y_px": 50,
    "lm_12_x": 0.37, "lm_12_y": 0.26, "lm_12_x_px": 111, "lm_12_y_px": 52,
    "lm_23_x": 0.3, "lm_23_y": 0.46, "lm_23_x_px": 90, "lm_23_y_px": 92,
    "lm_24_x": 0.26, "lm_24_y": 0.48, "lm_24_x_px": 78, "lm_24_y_px": 96
}

# 3. 예측 실행
result = evaluator.evaluate_single_sample(angles_data, coords_data, "실시간_데이터.jpg")

# 4. 결과 출력
status_icon = "✅" if result['prediction'] == "normal" else "⚠️"
print(f"{status_icon} 자세 분석 결과:")
print(f"   예측: {result['prediction']}")
print(f"   신뢰도: {result['confidence']:.3f}")

# 5. 조건부 알림
if result['prediction'] == "abnormal" and result['confidence'] > 0.7:
    print("🚨 경고: 비정상 자세가 감지되었습니다!")
```

### 📊 **실행 결과 예시:**
```
✅ 자세 분석 결과:
   예측: normal
   신뢰도: 0.823
```

---

# 🛠️ **문제 해결 (1분 진단)**

## 🚨 **자주 발생하는 문제들**

### ❌ **"모델을 찾을 수 없습니다"**
```bash
# 해결: 모델을 먼저 훈련하세요
python main.py --mode train --epochs 15
```

### ❌ **"KeyError: neck_angle"** 
```bash
# 해결: CSV 파일 컬럼명 확인
# 필수 컬럼: neck_angle, shoulder_angle_deg, hip_angle_deg
head -1 skeleton_angles.csv  # 첫 줄 확인
```

### ❌ **"메모리 부족" 오류**
```bash
# 해결: 배치 크기 줄이기
python main.py --mode train --batch_size 2 --epochs 10
```

### ❌ **"ModuleNotFoundError: tensorflow"**
```bash
# 해결: 패키지 재설치
pip uninstall tensorflow
pip install tensorflow
```

### ❌ **정확도가 너무 낮음 (50% 미만)**
```bash
# 해결책 1: 더 많은 에포크로 훈련
python main.py --mode train --epochs 50

# 해결책 2: 더 많은 데이터 준비 (각 클래스당 최소 20개)
```

## 💡 **빠른 진단 명령어**
```bash
# 1. 환경 확인
python --version
pip list | grep tensorflow

# 2. 데이터 확인
python data_preprocessing.py

# 3. 모델 확인
python main.py --mode info

# 4. 전체 테스트
python main.py --mode train --epochs 5
```

---

# 📚 **다음 단계**

🎯 **더 자세한 내용이 필요하다면:**
- **[상세 사용법](USER_MANUAL.md)** - 완전한 가이드
- **[실제 예제](EXAMPLES.md)** - 6가지 사용 사례
- **[문제해결](SUPPORT.md)** - 상세한 도움말

🚀 **고급 기능을 사용하고 싶다면:**
- 모델 파라미터 튜닝
- 실시간 웹캠 연동
- 배치 처리 시스템
- REST API 서버 구축

---

## 🎉 **축하합니다!**
이제 당신만의 자세 분류 AI 모델을 사용할 수 있습니다! 
새로운 데이터로 실험해보고, 필요에 따라 모델을 개선해보세요! 💪