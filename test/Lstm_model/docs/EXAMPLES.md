# 💡 실전 활용 예제

**실제로 사용할 수 있는 6가지 예제**

---

## 📋 **예제 목록**

1. [🚀 기본 사용법](#기본-사용법) - 처음 사용자용
2. [📊 배치 처리](#배치-처리) - 여러 파일 한번에
3. [⚡ 실시간 분석](#실시간-분석) - 웹캠 연동용
4. [🎯 정확도 향상](#정확도-향상) - 성능 개선
5. [🌐 웹서비스](#웹서비스) - API 서버 만들기
6. [📱 앱 연동](#앱-연동) - 다른 프로그램에서 사용

---

## 🚀 **1. 기본 사용법**

### 📝 **상황**: 처음으로 자세 분석해보기

```bash
# 1단계: 설치
pip install tensorflow pandas numpy scikit-learn matplotlib opencv-python

# 2단계: 훈련
python main.py --mode train --epochs 15

# 3단계: 분석
python main.py --mode evaluate
```

**✅ 결과**: `results/` 폴더에 분석 결과 생성

---

## 📊 **2. 배치 처리**

### 📝 **상황**: 100개 이미지를 한 번에 분석하기

```python
# batch_analyzer.py
from external_data_interface import PostureEvaluator
import glob
import os

def analyze_multiple_files():
    evaluator = PostureEvaluator()
    evaluator.load_model()
    
    # 여러 CSV 파일 찾기
    angle_files = glob.glob("data/*_angles.csv")
    
    results = []
    for angle_file in angle_files:
        coord_file = angle_file.replace("_angles.csv", "_coords.csv")
        
        if os.path.exists(coord_file):
            print(f"분석 중: {angle_file}")
            result = evaluator.evaluate_csv_data(angle_file, coord_file)
            results.append(result)
    
    # 전체 결과 요약
    total_normal = sum(r['summary']['normal_count'] for r in results)
    total_abnormal = sum(r['summary']['abnormal_count'] for r in results)
    
    print(f"🎯 전체 결과: 정상 {total_normal}개, 비정상 {total_abnormal}개")

# 실행
analyze_multiple_files()
```

---

## ⚡ **3. 실시간 분석**

### 📝 **상황**: 실시간으로 자세 체크하기

```python
# realtime_checker.py
from external_data_interface import PostureEvaluator
import time

def realtime_posture_check():
    evaluator = PostureEvaluator()
    evaluator.load_model()
    
    print("🎯 실시간 자세 체크 시작! (Ctrl+C로 종료)")
    
    while True:
        # 실제로는 웹캠이나 센서 데이터를 받아와야 함
        # 여기서는 시뮬레이션 데이터 사용
        angles = {"neck_angle": 130, "shoulder_angle_deg": 160, "hip_angle_deg": 140}
        coords = {"lm_0_x": 0.5, "lm_0_y": 0.2, "lm_11_x": 0.4, "lm_11_y": 0.25,
                  "lm_12_x": 0.37, "lm_12_y": 0.26, "lm_23_x": 0.3, "lm_23_y": 0.46,
                  "lm_24_x": 0.26, "lm_24_y": 0.48, "lm_0_x_px": 150, "lm_0_y_px": 40,
                  "lm_11_x_px": 120, "lm_11_y_px": 50, "lm_12_x_px": 111, "lm_12_y_px": 52,
                  "lm_23_x_px": 90, "lm_23_y_px": 92, "lm_24_x_px": 78, "lm_24_y_px": 96}
        
        result = evaluator.evaluate_single_sample(angles, coords, f"frame_{time.time()}")
        
        # 결과 출력
        status = "✅ 정상" if result['prediction'] == 'normal' else "⚠️ 주의"
        print(f"{status} | 신뢰도: {result['confidence']:.1%} | {time.strftime('%H:%M:%S')}")
        
        # 경고 알림
        if result['prediction'] == 'abnormal' and result['confidence'] > 0.8:
            print("🚨 자세를 바르게 해주세요!")
        
        time.sleep(2)  # 2초마다 체크

# 실행
realtime_posture_check()
```

---

## 🎯 **4. 정확도 향상**

### 📝 **상황**: 모델 성능을 90% 이상으로 올리기

```python
# accuracy_booster.py
from training_module import PostureTrainer

def train_high_accuracy_model():
    trainer = PostureTrainer("./", sequence_length=5)
    
    # 고성능 설정
    config = {
        'lstm_units': [128, 64, 32],    # 더 깊은 네트워크
        'dropout_rate': 0.3,            # 과적합 방지
        'learning_rate': 0.0005,        # 정밀한 학습
        'epochs': 100,                  # 충분한 훈련
        'batch_size': 16,               # 안정적 학습
        'validation_split': 0.2
    }
    
    print("🚀 고성능 모델 훈련 시작...")
    results = trainer.full_training_pipeline(config)
    
    accuracy = results['evaluation_results']['test_accuracy']
    print(f"🎯 최종 정확도: {accuracy:.1%}")
    
    if accuracy > 0.9:
        print("🏆 90% 이상 달성!")
    else:
        print("💪 더 많은 데이터가 필요해요!")

# 실행
train_high_accuracy_model()
```

---

## 🌐 **5. 웹서비스**

### 📝 **상황**: 웹 API로 서비스 만들기

```python
# web_api.py
from flask import Flask, request, jsonify
from external_data_interface import PostureEvaluator

app = Flask(__name__)
evaluator = PostureEvaluator()
evaluator.load_model()

@app.route('/analyze', methods=['POST'])
def analyze_posture():
    data = request.json
    
    try:
        angles = data['angles']
        coords = data['coords']
        image_name = data.get('image_name', 'unknown')
        
        result = evaluator.evaluate_single_sample(angles, coords, image_name)
        
        return jsonify({
            'success': True,
            'prediction': result['prediction'],
            'confidence': result['confidence'],
            'message': '정상 자세입니다!' if result['prediction'] == 'normal' else '자세를 교정해주세요!'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'model_loaded': True})

if __name__ == '__main__':
    print("🌐 자세 분석 API 서버 시작!")
    print("사용법: POST http://localhost:5000/analyze")
    app.run(debug=True, host='0.0.0.0', port=5000)
```

**사용 예시**:
```bash
# 서버 실행
python web_api.py

# API 호출 테스트
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"angles": {"neck_angle": 130, "shoulder_angle_deg": 160, "hip_angle_deg": 140}, "coords": {...}}'
```

---

## 📱 **6. 앱 연동**

### 📝 **상황**: 다른 Python 프로그램에서 사용하기

```python
# my_app.py
class PostureApp:
    def __init__(self):
        from external_data_interface import PostureEvaluator
        self.evaluator = PostureEvaluator()
        self.evaluator.load_model()
        print("✅ 자세 분석 엔진 준비 완료!")
    
    def check_posture(self, person_data):
        """한 사람의 자세를 체크"""
        angles = person_data['angles']
        coords = person_data['coords']
        name = person_data.get('name', 'Unknown')
        
        result = self.evaluator.evaluate_single_sample(angles, coords, name)
        
        return {
            'name': name,
            'posture': result['prediction'],
            'confidence': result['confidence'],
            'recommendation': self._get_recommendation(result)
        }
    
    def _get_recommendation(self, result):
        """자세에 따른 권장사항"""
        if result['prediction'] == 'normal':
            return "👍 좋은 자세를 유지하고 있어요!"
        else:
            confidence = result['confidence']
            if confidence > 0.8:
                return "🚨 자세 교정이 시급해요!"
            elif confidence > 0.6:
                return "⚠️ 자세를 조금 바르게 해주세요."
            else:
                return "💡 자세를 다시 한번 확인해보세요."

# 사용 예시
app = PostureApp()

# 가상의 사용자 데이터
user_data = {
    'name': '김철수',
    'angles': {'neck_angle': 130, 'shoulder_angle_deg': 160, 'hip_angle_deg': 140},
    'coords': {'lm_0_x': 0.5, 'lm_0_y': 0.2, 'lm_11_x': 0.4, 'lm_11_y': 0.25,
               'lm_12_x': 0.37, 'lm_12_y': 0.26, 'lm_23_x': 0.3, 'lm_23_y': 0.46,
               'lm_24_x': 0.26, 'lm_24_y': 0.48, 'lm_0_x_px': 150, 'lm_0_y_px': 40,
               'lm_11_x_px': 120, 'lm_11_y_px': 50, 'lm_12_x_px': 111, 'lm_12_y_px': 52,
               'lm_23_x_px': 90, 'lm_23_y_px': 92, 'lm_24_x_px': 78, 'lm_24_y_px': 96}
}

result = app.check_posture(user_data)
print(f"👤 {result['name']}: {result['posture']} ({result['confidence']:.1%})")
print(f"💡 {result['recommendation']}")
```

---

## 🎓 **추가 아이디어**

### 🏫 **교육용 활용**
- 학생들 자세 모니터링
- 온라인 수업 중 자세 체크
- 자세 교정 게임 만들기

### 🏢 **업무용 활용**  
- 사무실 직원 건강 관리
- 재택근무 자세 모니터링
- 작업자 안전 관리

### 🏥 **의료용 활용**
- 환자 재활 모니터링
- 물리치료 진도 체크
- 자세 개선 프로그램

---

**💡 더 많은 아이디어가 있으시면 직접 구현해보세요!**
**막히는 부분이 있으면 언제든 문의해주세요!** 🙋‍♂️