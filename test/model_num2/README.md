# 자세 교정 시스템 (Pure LSTM v2.0)# 자세 분류 모델 - 최적화 버전



## ✨ 주요 특징## 🚀 속도 최적화 기능

- 🎯 **Pure LSTM 모델**: CNN 없이 수치 데이터만 사용 (이미지 불필요)

- 📍 **위치 독립적**: 화면 어디서든 동일하게 작동### 1. **병렬 이미지 로딩**

- ⚡ **초고속 훈련**: 에폭당 ~1초 (기존 대비 360배 향상)- ThreadPoolExecutor를 사용한 멀티스레드 이미지 로드

- 🎨 **경량 모델**: 36,178 파라미터, 141KB- 최대 8개의 워커로 병렬 처리

- 📊 **높은 정확도**: 85.37% 검증 정확도- **약 2-3배 빠른 데이터 로딩**

- 🔍 **엄격한 기준**: 95% 이상만 GOOD 판정

### 2. **TensorFlow Dataset 캐싱**

---- 메모리 캐싱으로 반복적인 데이터 읽기 제거

- Auto-tuning prefetch로 자동 최적화

## 🚀 빠른 시작- **에폭당 학습 시간 단축**



### 1단계: 전처리 (이미지 → 스켈레톤 데이터)### 3. **배치 크기 자동 최적화**

```bash- GPU 감지 후 자동으로 배치 크기 조정

python src/preprocessing.py- GPU 사용 시: 배치 크기 x2 (최대 32)

```- CPU 사용 시: 적정 배치 크기 유지

- MediaPipe로 이미지에서 스켈레톤 추출- **메모리 효율성 향상**

- 9개 특징 계산 (각도 4개 + 비율 5개)

- `data/pose_data.csv` 생성### 4. **Mixed Precision 학습 (GPU only)**

- FP16 연산으로 GPU 학습 속도 향상

### 2단계: 모델 훈련 (LSTM)- Loss Scaling으로 수치 안정성 보장

```bash- CPU에서는 자동으로 비활성화

python src/lstm_posture_model.py- **GPU 학습 속도 약 1.5-2배 향상**

```

- Pure LSTM 모델 훈련### 5. **Early Stopping 최적화**

- 100 에폭 (Early Stopping 적용)- Patience: 18 → 12로 단축

- 약 14초 소요- 더 빠른 학습 종료 결정

- 모델 저장: `models/best_cnn_lstm_model.h5`- **불필요한 에폭 제거**



### 3단계: 실시간 모니터링 (웹캠)### 6. **학습률 스케줄링 개선**

```bash- ReduceLROnPlateau patience: 7 → 5

python src/realtime_cam.py- factor: 0.6 → 0.5로 더 공격적 감소

```- **더 빠른 수렴**

- 실시간 자세 판단 (95% 이상 GOOD)

- `q` 키로 종료## 📊 실행 방법



---### 기본 학습 (최적화 적용)

```bash

## 📁 프로젝트 구조.venv\Scripts\python.exe src\cnn_lstm_model.py --epochs 35 --batch_size 16

```

```

model_num2/### 빠른 테스트 (5 에폭)

├── src/```bash

│   ├── lstm_posture_model.py   ⭐ 메인 훈련 스크립트.venv\Scripts\python.exe src\cnn_lstm_model.py --epochs 5 --batch_size 16

│   ├── realtime_cam.py          실시간 웹캠```

│   ├── preprocessing.py         전처리

│   ├── model_builder.py         모델 아키텍처### 옵션

│   ├── model_visualizer.py      평가 및 시각화- `--epochs`: 에폭 수 (기본: 35)

│   └── model_utils.py           유틸리티- `--batch_size`: 배치 크기 (기본: 16, 자동 최적화됨)

│- `--img_size`: 이미지 크기 (기본: 112)

├── models/                      학습된 모델- `--no_augment`: 데이터 증강 비활성화

├── data/                        데이터셋

├── app_ui/                      UI (선택사항)## ⚡ 예상 속도 향상

└── PROJECT_STRUCTURE.md         📝 상세 문서

```| 환경 | 기존 속도 | 최적화 후 | 개선율 |

|------|----------|----------|--------|

자세한 설명은 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)를 참고하세요.| CPU | 3-7 min/epoch | 2-4 min/epoch | **~40% 향상** |

| GPU | 30-60 sec/epoch | 15-30 sec/epoch | **~50% 향상** |

---

## 🔧 핵심 파일

## 🏗️ 모델 아키텍처

- `src/cnn_lstm_model.py`: 메인 학습 스크립트 (최적화 적용)

### Pure LSTM (이미지 없음)- `src/model_utils.py`: 병렬 이미지 로딩

```- `src/model_builder.py`: Mixed Precision 지원

입력: 9개 특징 × 5 프레임- `src/preprocessing.py`: 데이터 전처리

  ↓- `src/realtime_cam.py`: 웹캠 실시간 적용

LSTM(64) → BatchNorm

  ↓## 📝 주요 변경사항

LSTM(32) → BatchNorm

  ↓### cnn_lstm_model.py

LSTM(16) → BatchNorm- TensorFlow Dataset API 사용 (캐싱 + prefetch)

  ↓- 자동 배치 크기 최적화

Dense(32) → Dropout(0.35)- GPU 감지 후 Mixed Precision 조건부 활성화

  ↓- Early Stopping patience 단축

Dense(16) → Dropout(0.35)

  ↓### model_utils.py

출력: 2 classes- ThreadPoolExecutor로 병렬 이미지 로딩

```- 최대 8개 워커로 동시 처리

- 진행률 실시간 표시

**총 파라미터**: 36,178개 (141KB)

### model_builder.py

---- Mixed Precision Loss Scaling 지원

- GPU 전용 최적화

## 📊 성능

## 💡 팁

### 훈련 결과

- **검증 정확도**: 85.37%1. **GPU 사용 시**: Mixed Precision이 자동 활성화되어 최대 성능 발휘

- **훈련 시간**: 14초 (Early Stopping at epoch 14)2. **CPU 사용 시**: 병렬 로딩과 캐싱으로 속도 개선

- **에폭당 시간**: ~1초3. **배치 크기**: 자동 최적화되므로 기본값 사용 권장

- **모델 크기**: 141KB4. **메모리 부족 시**: `--batch_size` 를 8로 낮추기



### 특징## 🎯 성능 모니터링

✅ 위치 편향 제거 (이미지 미사용)  

✅ 실시간 추론 가능  학습 시작 시 다음 정보가 표시됩니다:

✅ 경량 모델 (스마트폰 배포 가능)  ```

✅ 순수 스켈레톤 기반 판단  ✅ Mixed Precision (FP16) 활성화  # GPU 전용

최적화된 배치 크기: 32            # 자동 조정

---진행률: 100% (544/636)           # 병렬 로딩

```

## 🎯 판단 기준

## ⚠️ 주의사항

### 95% 엄격 모드 (현재)

- **95% 이상**: GOOD (정상 자세)- Mixed Precision은 GPU에서만 활성화됩니다

- **95% 미만**: BAD (자세 교정 필요)- CPU에서는 자동으로 비활성화되어 안정성 보장

- 배치 크기는 메모리와 데이터셋 크기에 따라 자동 조정됩니다

### 커스터마이징
`realtime_cam.py` 파일에서 기준 변경 가능:
```python
# 엄격한 기준 (95%)
if confidence_percentage >= 95:
    final_class = 'normal'

# 느슨한 기준 (90%)
if confidence_percentage >= 90:
    final_class = 'normal'
```

---

## 🔧 의존성

```bash
pip install -r requirements.txt
```

주요 패키지:
- TensorFlow >= 2.10.0
- MediaPipe >= 0.10.0
- OpenCV >= 4.8.0
- NumPy, Pandas, Scikit-learn

---

## 📈 개선 히스토리

### v1.0 - CNN + LSTM 하이브리드
- ❌ 문제: 화면 위치 편향 (이미지 사용)
- ⏱️ 속도: 에폭당 ~6분
- 💾 크기: 116K 파라미터

### v2.0 - Pure LSTM (현재) ⭐
- ✅ 해결: 이미지 완전 제거
- ⚡ 속도: 에폭당 ~1초 (360배 향상)
- 🎨 크기: 36K 파라미터 (70% 감소)
- 📍 위치 독립적 판단 성공

---

## 🛠️ 문제 해결

### 웹캠 실행 오류
```bash
pip install --upgrade opencv-python mediapipe
```

### 모델 로드 오류
모델 파일 존재 확인:
```bash
ls models/best_cnn_lstm_model.h5
```

### 위치 편향 문제
현재 버전(v2.0)은 이미지를 사용하지 않으므로 위치 편향 없음

---

## 📝 라이선스
MIT License

## 🤝 기여
Issues와 Pull Requests를 환영합니다!

---

## 📚 추가 문서
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - 상세 프로젝트 구조
- [EXECUTION_GUIDE.md](EXECUTION_GUIDE.md) - 실행 가이드
- [TECHNOLOGIES.md](TECHNOLOGIES.md) - 기술 스택
