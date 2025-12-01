# 모델 배포 파일 가이드 📦

## ✅ 필수 파일 4개

---

### 1️⃣ **best_cnn_lstm_model.h5** (511 KB)

**역할**: 학습된 LSTM 신경망 모델

**내용**:
- LSTM 레이어의 모든 가중치 (36,178개 파라미터)
- 모델 구조 (3개 LSTM + 2개 Dense 레이어)
- 최고 성능을 기록한 에폭의 상태

**왜 필요한가?**
- 자세를 예측하려면 이 모델이 **반드시** 필요
- 재훈련 없이 바로 추론 가능

**사용 예시**:
```python
import tensorflow as tf
model = tf.keras.models.load_model('best_cnn_lstm_model.h5')
prediction = model.predict(data)
```

---

### 2️⃣ **scaler_cnn_lstm.pkl** (815 Bytes)

**역할**: 데이터 정규화 도구 (StandardScaler)

**내용**:
- 9개 특징의 평균값 (mean)
- 9개 특징의 표준편차 (std)
- 훈련 시 사용한 정규화 규칙

**왜 필요한가?**
- 새로운 데이터를 **훈련 때와 똑같은 방법**으로 정규화해야 함
- 정규화 안 하면 예측이 완전히 틀려짐

**예시**:
```
원본: 목 각도 60도
정규화: -0.52
→ 같은 변환 규칙을 써야 모델이 이해함
```

**사용 예시**:
```python
import joblib
scaler = joblib.load('scaler_cnn_lstm.pkl')
normalized_data = scaler.transform(raw_data)
```

---

### 3️⃣ **label_encoder_cnn_lstm.pkl** (492 Bytes)

**역할**: 라벨 변환기

**내용**:
- `abnormal` → 0
- `normal` → 1

**왜 필요한가?**
- 모델은 숫자(0, 1)로 예측함
- 사람이 이해하려면 단어('abnormal', 'normal')로 변환 필요

**사용 예시**:
```python
import joblib
label_encoder = joblib.load('label_encoder_cnn_lstm.pkl')

# 모델 출력: 0 → 'abnormal'
predicted_label = label_encoder.inverse_transform([0])
print(predicted_label)  # ['abnormal']
```

---

### 4️⃣ **model_metadata_cnn_lstm.json** (367 Bytes)

**역할**: 모델 설정 정보

**내용**:
```json
{
  "sequence_length": 5,
  "dropout_rate": 0.35,
  "feature_columns": [
    "neck_angle",
    "shoulder_angle", 
    "hip_angle",
    "torso_angle",
    "shoulder_width",
    "hip_width",
    "torso_height",
    "neck_length",
    "shoulder_hip_ratio"
  ],
  "classes": ["abnormal", "normal"]
}
```

**왜 필요한가?**
- **몇 개 프레임**이 필요한지 (5개)
- **어떤 특징**을 **어떤 순서**로 넣어야 하는지
- 순서가 틀리면 예측이 엉망이 됨

**사용 예시**:
```python
import json
with open('model_metadata_cnn_lstm.json', 'r') as f:
    metadata = json.load(f)

sequence_length = metadata['sequence_length']  # 5
features = metadata['feature_columns']  # 9개 특징
```

---

## 🎯 요약

| 파일 | 크기 | 역할 | 필수 |
|------|------|------|------|
| `best_cnn_lstm_model.h5` | 511 KB | 모델 가중치 | ✅ |
| `scaler_cnn_lstm.pkl` | 815 B | 데이터 정규화 | ✅ |
| `label_encoder_cnn_lstm.pkl` | 492 B | 라벨 변환 | ✅ |
| `model_metadata_cnn_lstm.json` | 367 B | 설정 정보 | ✅ |

**총 용량**: 약 513 KB

---

## 🚀 사용 방법

```python
import tensorflow as tf
import joblib
import json
import numpy as np

# 1. 모델 로드
model = tf.keras.models.load_model('best_cnn_lstm_model.h5')

# 2. 스케일러 로드
scaler = joblib.load('scaler_cnn_lstm.pkl')

# 3. 라벨 인코더 로드
label_encoder = joblib.load('label_encoder_cnn_lstm.pkl')

# 4. 메타데이터 로드
with open('model_metadata_cnn_lstm.json', 'r') as f:
    metadata = json.load(f)

# 5. 새 데이터로 예측
# (5 프레임 × 9 특징)
new_data = np.array([...])  # MediaPipe에서 추출한 데이터

# 정규화
normalized = scaler.transform(new_data)

# 시퀀스 형태로 변환 (1, 5, 9)
sequence = normalized.reshape(1, 5, 9)

# 예측
prediction = model.predict(sequence)
predicted_class = np.argmax(prediction[0])
predicted_label = label_encoder.inverse_transform([predicted_class])[0]

print(f"예측: {predicted_label}")
print(f"신뢰도: {prediction[0][predicted_class]*100:.2f}%")
```

---

## ⚠️ 주의사항

1. **4개 파일은 모두 함께 있어야 함**
   - 하나라도 빠지면 작동 안 됨

2. **파일 이름 변경 금지**
   - 코드에 파일명이 하드코딩되어 있음

3. **특징 순서 중요**
   - `model_metadata_cnn_lstm.json`에 명시된 순서대로 입력해야 함

4. **시퀀스 길이 고정**
   - 반드시 5개 프레임이 필요함
   - 4개나 6개는 안 됨

---

## 📤 배포 시

이 4개 파일을 함께 압축해서 공유하세요:
```bash
best_cnn_lstm_model.h5
scaler_cnn_lstm.pkl
label_encoder_cnn_lstm.pkl
model_metadata_cnn_lstm.json
```

**압축 후 크기**: 약 400 KB
