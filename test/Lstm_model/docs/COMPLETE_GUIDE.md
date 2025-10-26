# 🤖 자세 분류 AI - 완전 가이드

> **⚡ 3분 만에 AI로 자세 분석하기**

---

## 🎯 **이 프로그램이 하는 일**

- 📸 **이미지 분석**: 사람의 자세를 AI로 자동 분석
- ✅ **자세 판별**: 정상 자세 vs 비정상 자세 구분
- 📊 **결과 제공**: 정확도와 신뢰도를 포함한 상세 결과

---

## 🚀 **바로 시작하기 (3단계)**

### 1️⃣ **설치하기** (1분)
```bash
# 폴더로 이동
cd "c:\Users\user\OneDrive\Desktop\test\Lstm_model"

# 패키지 설치
pip install tensorflow pandas numpy scikit-learn matplotlib opencv-python
```

### 2️⃣ **AI 훈련하기** (2분)
```bash
python main.py --mode train --epochs 15
```
**✅ 성공하면:** "모델 훈련 완료! 최종 정확도: 0.XXXX" 메시지

### 3️⃣ **자세 분석하기** (30초)
```bash
python main.py --mode evaluate
```
**✅ 성공하면:** "데이터 평가 완료! 총 샘플: X개" 메시지

---

## ✅ **완료!** 이제 다음이 생성되었습니다:
- 🤖 **훈련된 AI 모델**: `models/` 폴더
- 📊 **분석 결과**: `results/` 폴더
- 📈 **성능 그래프**: PNG 파일들

---

# 📝 **새로운 데이터 분석하기**

## 🔍 **내 데이터 준비하기**

### 📐 **angles.csv** (각도 정보)
```csv
image_path,neck_angle,shoulder_angle_deg,hip_angle_deg
my_photo1.jpg,125.5,170.2,145.8
my_photo2.jpg,-110.3,-60.1,-140.5
```

### 📍 **coords.csv** (위치 정보)  
```csv
image_path,lm_0_x,lm_0_y,lm_0_x_px,lm_0_y_px,lm_11_x,lm_11_y,lm_11_x_px,lm_11_y_px,lm_12_x,lm_12_y,lm_12_x_px,lm_12_y_px,lm_23_x,lm_23_y,lm_23_x_px,lm_23_y_px,lm_24_x,lm_24_y,lm_24_x_px,lm_24_y_px
my_photo1.jpg,0.47,0.19,150,40,0.40,0.25,120,60,0.37,0.26,111,63,0.30,0.46,90,110,0.26,0.48,78,115
my_photo2.jpg,0.38,0.26,280,330,0.49,0.30,375,385,0.51,0.28,385,360,0.75,0.45,568,585,0.72,0.43,548,550
```

## 🚀 **내 데이터 분석하기**
```bash
python main.py --mode evaluate --angles_csv "angles.csv" --coords_csv "coords.csv" 
```

## 📊 **결과 확인하기**
`results/evaluation_results_날짜시간.json` 파일을 열어보세요:
```json
{
  "predictions": [
    {"image_path": "my_photo1.jpg", "prediction": "normal", "confidence": 0.823},
    {"image_path": "my_photo2.jpg", "prediction": "abnormal", "confidence": 0.745}
  ]
}
```

---

# 💻 **Python 코드로 사용하기**

```python
from external_data_interface import PostureEvaluator

# AI 모델 로드
evaluator = PostureEvaluator()
evaluator.load_model()

# 자세 데이터 (예시)
angles = {"neck_angle": 130, "shoulder_angle_deg": 160, "hip_angle_deg": 140}
coords = {"lm_0_x": 0.5, "lm_0_y": 0.2, "lm_11_x": 0.4, "lm_11_y": 0.25,
          "lm_12_x": 0.37, "lm_12_y": 0.26, "lm_23_x": 0.3, "lm_23_y": 0.46,
          "lm_24_x": 0.26, "lm_24_y": 0.48, "lm_0_x_px": 150, "lm_0_y_px": 40,
          "lm_11_x_px": 120, "lm_11_y_px": 50, "lm_12_x_px": 111, "lm_12_y_px": 52,
          "lm_23_x_px": 90, "lm_23_y_px": 92, "lm_24_x_px": 78, "lm_24_y_px": 96}

# 자세 분석
result = evaluator.evaluate_single_sample(angles, coords, "test.jpg")

# 결과 출력
print(f"자세: {result['prediction']}, 신뢰도: {result['confidence']:.3f}")
```

---

# 🛠️ **문제 해결**

## ❌ **자주 발생하는 문제들**

### "모델을 찾을 수 없습니다"
```bash
# 해결: AI 모델을 먼저 훈련하세요
python main.py --mode train --epochs 15
```

### "KeyError: neck_angle" 
```bash
# 해결: CSV 파일 첫 줄을 확인하세요
# 필요한 컬럼: neck_angle, shoulder_angle_deg, hip_angle_deg
```

### "메모리 부족"
```bash
# 해결: 더 작은 배치로 훈련하세요
python main.py --mode train --batch_size 2 --epochs 10
```

### "ModuleNotFoundError"
```bash
# 해결: 패키지를 다시 설치하세요
pip install -r requirements.txt
```

## 💡 **빠른 진단**
```bash
# 1단계: 환경 확인
python --version
pip list | grep tensorflow

# 2단계: 데이터 확인  
python data_preprocessing.py

# 3단계: 모델 확인
python main.py --mode info
```

---

# 🎓 **더 알아보기**

## 🔧 **고급 기능**
- **모델 성능 향상**: 더 많은 데이터, 더 많은 에포크
- **실시간 분석**: 웹캠 연결하여 실시간 자세 체크
- **배치 처리**: 여러 파일을 한 번에 분석
- **API 서버**: 웹 서비스로 만들기

## 📚 **참고 자료**
- `requirements.txt`: 필요한 패키지 목록
- `models/`: 훈련된 AI 모델들
- `results/`: 분석 결과와 그래프들
- `labeled/`: 학습용 이미지 샘플들

---

## 🎉 **축하합니다!**

이제 당신만의 자세 분류 AI를 사용할 수 있습니다! 🎊

💪 **다음 단계**: 
- 더 많은 데이터로 정확도 향상시키기
- 친구들 자세도 분석해보기  
- 나만의 자세 분류 앱 만들기

**문의사항이 있으시면 GitHub에 이슈를 남겨주세요!** 🙋‍♂️