# ⚡ 1분 시작 가이드

**AI 자세 분류기를 1분 만에 실행하세요!**

---

## 🎯 **단 3줄로 시작하기**

```bash
cd "c:\Users\user\OneDrive\Desktop\test\Lstm_model"
pip install tensorflow pandas numpy scikit-learn matplotlib opencv-python
python main.py --mode train --epochs 10
```

**끝!** 이제 AI 모델이 훈련되었습니다! 🎉

---

## 🔍 **내 자세 분석해보기**

```bash
python main.py --mode evaluate
```

**결과**: `results/` 폴더에서 확인하세요!

---

## 💻 **Python에서 바로 사용하기**

```python
from external_data_interface import PostureEvaluator

# 모델 로드
evaluator = PostureEvaluator()
evaluator.load_model()

# 자세 분석 (예시 데이터)
angles = {"neck_angle": 130, "shoulder_angle_deg": 160, "hip_angle_deg": 140}
coords = {"lm_0_x": 0.5, "lm_0_y": 0.2, "lm_11_x": 0.4, "lm_11_y": 0.25, 
          "lm_12_x": 0.37, "lm_12_y": 0.26, "lm_23_x": 0.3, "lm_23_y": 0.46,
          "lm_24_x": 0.26, "lm_24_y": 0.48, "lm_0_x_px": 150, "lm_0_y_px": 40,
          "lm_11_x_px": 120, "lm_11_y_px": 50, "lm_12_x_px": 111, "lm_12_y_px": 52,
          "lm_23_x_px": 90, "lm_23_y_px": 92, "lm_24_x_px": 78, "lm_24_y_px": 96}

result = evaluator.evaluate_single_sample(angles, coords, "test.jpg")
print(f"자세: {result['prediction']}, 확률: {result['confidence']:.1%}")
```

---

## 🚨 **문제 해결**

| 오류 | 해결법 |
|------|--------|
| "모델을 찾을 수 없습니다" | `python main.py --mode train` 실행 |
| "KeyError: neck_angle" | CSV 파일 컬럼명 확인 |
| "메모리 부족" | `--batch_size 2` 추가 |
| "ModuleNotFoundError" | `pip install -r requirements.txt` |

---

## ✅ **체크리스트**

- [ ] Python 3.8+ 설치됨
- [ ] 패키지 설치 완료  
- [ ] 모델 훈련 완료
- [ ] 결과 파일 생성됨

**모든 체크가 완료되면 성공!** 🎊

---

**더 자세한 설명이 필요하면 [`COMPLETE_GUIDE.md`](COMPLETE_GUIDE.md)를 보세요!**