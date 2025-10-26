# 예제 및 튜토리얼
**실제 사용 사례를 통한 학습**

## 📝 예제 1: 기본 모델 훈련

### 상황
기본 데이터셋으로 첫 번째 모델을 훈련하고 싶습니다.

### 코드
```bash
# 1. 데이터 확인
python data_preprocessing.py

# 2. 기본 설정으로 훈련
python main.py --mode train

# 3. 모델 정보 확인
python main.py --mode info
```

### 예상 결과
```
훈련 데이터: (14, 3, 23)
테스트 데이터: (6, 3, 23)
최종 정확도: 0.7500
```

---

## 📝 예제 2: 새로운 CSV 데이터 평가

### 상황
외부에서 받은 새로운 자세 데이터를 평가하고 싶습니다.

### 데이터 준비
**new_angles.csv:**
```csv
image_path,neck_angle,shoulder_angle_deg,hip_angle_deg
person1.jpg,125.3,175.8,142.1
person2.jpg,-108.7,-58.2,-138.9
person3.jpg,132.1,168.5,149.3
```

**new_coords.csv:**
```csv
image_path,lm_0_x,lm_0_y,lm_0_x_px,lm_0_y_px,lm_11_x,lm_11_y,lm_11_x_px,lm_11_y_px,lm_12_x,lm_12_y,lm_12_x_px,lm_12_y_px,lm_23_x,lm_23_y,lm_23_x_px,lm_23_y_px,lm_24_x,lm_24_y,lm_24_x_px,lm_24_y_px
person1.jpg,0.465,0.192,140,45,0.397,0.249,120,58,0.363,0.251,109,59,0.296,0.462,89,108,0.259,0.485,78,113
person2.jpg,0.375,0.254,285,330,0.494,0.298,375,387,0.507,0.279,385,362,0.748,0.452,568,588,0.722,0.426,548,553
person3.jpg,0.483,0.195,145,48,0.385,0.245,115,60,0.371,0.255,111,63,0.302,0.458,90,113,0.267,0.481,80,118
```

### 실행
```bash
python main.py --mode evaluate --angles_csv "new_angles.csv" --coords_csv "new_coords.csv"
```

### 결과 확인
`results/evaluation_results_날짜시간.json` 파일:
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

## 📝 예제 3: Python 코드에서 실시간 평가

### 상황
웹캠이나 실시간 데이터를 처리하여 자세를 평가하고 싶습니다.

### 코드
```python
from external_data_interface import PostureEvaluator
import time

def evaluate_posture_realtime():
    # 평가기 초기화
    evaluator = PostureEvaluator()
    
    if not evaluator.load_model():
        print("모델 로드 실패!")
        return
    
    # 실시간 데이터 시뮬레이션
    sample_data = [
        {
            "angles": {"neck_angle": 125.3, "shoulder_angle_deg": 175.8, "hip_angle_deg": 142.1},
            "coords": {"lm_0_x": 0.465, "lm_0_y": 0.192, "lm_11_x": 0.397, "lm_11_y": 0.249, 
                      "lm_12_x": 0.363, "lm_12_y": 0.251, "lm_23_x": 0.296, "lm_23_y": 0.462,
                      "lm_24_x": 0.259, "lm_24_y": 0.485, "lm_0_x_px": 140, "lm_0_y_px": 45,
                      "lm_11_x_px": 120, "lm_11_y_px": 58, "lm_12_x_px": 109, "lm_12_y_px": 59,
                      "lm_23_x_px": 89, "lm_23_y_px": 108, "lm_24_x_px": 78, "lm_24_y_px": 113},
            "name": "프레임_001"
        },
        {
            "angles": {"neck_angle": -108.7, "shoulder_angle_deg": -58.2, "hip_angle_deg": -138.9},
            "coords": {"lm_0_x": 0.375, "lm_0_y": 0.254, "lm_11_x": 0.494, "lm_11_y": 0.298,
                      "lm_12_x": 0.507, "lm_12_y": 0.279, "lm_23_x": 0.748, "lm_23_y": 0.452,
                      "lm_24_x": 0.722, "lm_24_y": 0.426, "lm_0_x_px": 285, "lm_0_y_px": 330,
                      "lm_11_x_px": 375, "lm_11_y_px": 387, "lm_12_x_px": 385, "lm_12_y_px": 362,
                      "lm_23_x_px": 568, "lm_23_y_px": 588, "lm_24_x_px": 548, "lm_24_y_px": 553},
            "name": "프레임_002"
        }
    ]
    
    print("실시간 자세 평가 시작...")
    print("-" * 50)
    
    for data in sample_data:
        result = evaluator.evaluate_single_sample(
            data["angles"], 
            data["coords"], 
            data["name"]
        )
        
        status_icon = "✅" if result["prediction"] == "normal" else "⚠️"
        print(f"{status_icon} {data['name']}: {result['prediction']} (신뢰도: {result['confidence']:.3f})")
        
        # 실시간 처리 시뮬레이션
        time.sleep(1)
    
    print("-" * 50)
    print("평가 완료!")

if __name__ == "__main__":
    evaluate_posture_realtime()
```

### 실행 결과
```
실시간 자세 평가 시작...
--------------------------------------------------
✅ 프레임_001: normal (신뢰도: 0.823)
⚠️ 프레임_002: abnormal (신뢰도: 0.745)
--------------------------------------------------
평가 완료!
```

---

## 📝 예제 4: 고급 모델 훈련 (파라미터 튜닝)

### 상황
더 정확한 모델을 위해 하이퍼파라미터를 조정하고 싶습니다.

### 코드
```python
from training_module import PostureTrainer

def train_advanced_model():
    # 훈련기 초기화
    trainer = PostureTrainer("./", sequence_length=5)
    
    # 고급 설정
    advanced_config = {
        'use_angles': True,
        'use_coords': True,
        'lstm_units': [128, 64, 32],    # 더 깊은 네트워크
        'dropout_rate': 0.4,            # 높은 드롭아웃
        'learning_rate': 0.0005,        # 낮은 학습률
        'epochs': 100,                  # 많은 에포크
        'batch_size': 16,               # 큰 배치 크기
        'validation_split': 0.25        # 25% 검증 데이터
    }
    
    print("고급 모델 훈련 시작...")
    results = trainer.full_training_pipeline(advanced_config)
    
    if results:
        print(f"✅ 훈련 완료! 최종 정확도: {results['evaluation_results']['test_accuracy']:.4f}")
        
        # 상세 결과 출력
        report = results['evaluation_results']['classification_report']
        print("\\n📊 상세 성능:")
        for class_name in ['abnormal', 'normal']:
            if class_name in report:
                metrics = report[class_name]
                print(f"  {class_name}:")
                print(f"    정밀도: {metrics['precision']:.3f}")
                print(f"    재현율: {metrics['recall']:.3f}")
                print(f"    F1-점수: {metrics['f1-score']:.3f}")
    else:
        print("❌ 훈련 실패!")

if __name__ == "__main__":
    train_advanced_model()
```

---

## 📝 예제 5: 배치 처리 시스템

### 상황
여러 개의 CSV 파일을 한 번에 처리하고 싶습니다.

### 코드
```python
import os
import glob
from external_data_interface import PostureEvaluator

def batch_evaluate_files():
    # 평가기 초기화
    evaluator = PostureEvaluator()
    
    if not evaluator.load_model():
        print("❌ 모델 로드 실패!")
        return
    
    # 배치 처리할 파일들 찾기
    angles_files = glob.glob("batch_data/*_angles.csv")
    
    print(f"📁 발견된 파일: {len(angles_files)}개")
    print("-" * 60)
    
    total_normal = 0
    total_abnormal = 0
    
    for angles_file in angles_files:
        # 대응하는 좌표 파일 찾기
        base_name = angles_file.replace("_angles.csv", "")
        coords_file = base_name + "_coords.csv"
        
        if not os.path.exists(coords_file):
            print(f"⚠️ {coords_file} 파일을 찾을 수 없습니다.")
            continue
        
        print(f"🔍 처리 중: {os.path.basename(angles_file)}")
        
        try:
            # 평가 실행
            results = evaluator.evaluate_csv_data(
                angles_file, 
                coords_file,
                f"batch_results/{os.path.basename(base_name)}_results.json"
            )
            
            if results:
                normal_count = results['summary']['normal_count']
                abnormal_count = results['summary']['abnormal_count']
                total_samples = results['summary']['total_samples']
                
                total_normal += normal_count
                total_abnormal += abnormal_count
                
                print(f"  ✅ 완료: {total_samples}개 샘플 (정상: {normal_count}, 비정상: {abnormal_count})")
            else:
                print(f"  ❌ 처리 실패")
                
        except Exception as e:
            print(f"  ❌ 오류: {e}")
    
    print("-" * 60)
    print(f"🎯 전체 결과:")
    print(f"  총 정상 자세: {total_normal}개")
    print(f"  총 비정상 자세: {total_abnormal}개")
    print(f"  전체 샘플: {total_normal + total_abnormal}개")
    
    if total_normal + total_abnormal > 0:
        normal_ratio = total_normal / (total_normal + total_abnormal) * 100
        print(f"  정상 자세 비율: {normal_ratio:.1f}%")

# 실행
if __name__ == "__main__":
    # 결과 폴더 생성
    os.makedirs("batch_results", exist_ok=True)
    batch_evaluate_files()
```

---

## 📝 예제 6: 모델 성능 비교

### 상황
다른 설정으로 훈련한 여러 모델의 성능을 비교하고 싶습니다.

### 코드
```python
from training_module import PostureTrainer
import json

def compare_models():
    trainer = PostureTrainer("./")
    
    # 비교할 설정들
    configs = [
        {
            'name': '기본 모델',
            'config': {
                'lstm_units': [32, 16],
                'dropout_rate': 0.2,
                'learning_rate': 0.001,
                'epochs': 30
            }
        },
        {
            'name': '깊은 모델', 
            'config': {
                'lstm_units': [64, 32, 16],
                'dropout_rate': 0.3,
                'learning_rate': 0.0005,
                'epochs': 50
            }
        },
        {
            'name': '단순 모델',
            'config': {
                'lstm_units': [16],
                'dropout_rate': 0.1,
                'learning_rate': 0.01,
                'epochs': 20
            }
        }
    ]
    
    results_comparison = []
    
    print("🔬 모델 성능 비교 실험 시작")
    print("=" * 60)
    
    for i, model_config in enumerate(configs, 1):
        print(f"\\n📊 실험 {i}: {model_config['name']}")
        print("-" * 40)
        
        # 모델 훈련
        results = trainer.full_training_pipeline(model_config['config'])
        
        if results:
            accuracy = results['evaluation_results']['test_accuracy']
            loss = results['evaluation_results']['test_loss']
            
            comparison_result = {
                'name': model_config['name'],
                'accuracy': accuracy,
                'loss': loss,
                'config': model_config['config']
            }
            results_comparison.append(comparison_result)
            
            print(f"✅ 정확도: {accuracy:.4f}")
            print(f"✅ 손실: {loss:.4f}")
        else:
            print("❌ 훈련 실패")
    
    # 결과 정리 및 출력
    print("\\n" + "=" * 60)
    print("🏆 최종 비교 결과")
    print("=" * 60)
    
    # 정확도 순으로 정렬
    results_comparison.sort(key=lambda x: x['accuracy'], reverse=True)
    
    for i, result in enumerate(results_comparison, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
        print(f"{medal} {i}위: {result['name']}")
        print(f"    정확도: {result['accuracy']:.4f}")
        print(f"    손실: {result['loss']:.4f}")
        print()
    
    # 결과를 JSON 파일로 저장
    with open('model_comparison_results.json', 'w', encoding='utf-8') as f:
        json.dump(results_comparison, f, ensure_ascii=False, indent=2)
    
    print("📄 상세 결과가 'model_comparison_results.json'에 저장되었습니다.")

if __name__ == "__main__":
    compare_models()
```

---

## 🎯 실전 팁

### 💡 팁 1: 데이터 품질 확인
```python
import pandas as pd

def check_data_quality(angles_csv, coords_csv):
    angles_df = pd.read_csv(angles_csv)
    coords_df = pd.read_csv(coords_csv)
    
    print("📊 데이터 품질 체크")
    print(f"각도 데이터: {angles_df.shape}")
    print(f"좌표 데이터: {coords_df.shape}")
    print(f"결측값 - 각도: {angles_df.isnull().sum().sum()}")
    print(f"결측값 - 좌표: {coords_df.isnull().sum().sum()}")
    
    # 이상값 검출
    angle_cols = ['neck_angle', 'shoulder_angle_deg', 'hip_angle_deg']
    for col in angle_cols:
        if col in angles_df.columns:
            values = angles_df[col]
            print(f"{col}: 범위 [{values.min():.1f}, {values.max():.1f}]")
```

### 💡 팁 2: 모델 백업 및 버전 관리
```bash
# 중요한 모델 백업
cp models/posture_lstm_model_20251026_181704.keras models/backup/best_model_v1.keras

# 모델 버전별 성능 기록
echo "v1.0: accuracy=0.85, date=2025-10-26" >> models/model_versions.txt
```

### 💡 팁 3: 자동화 스크립트
```bash
#!/bin/bash
# auto_training.sh

echo "자동 훈련 시작..."

# 데이터 검증
python data_preprocessing.py
if [ $? -ne 0 ]; then
    echo "데이터 오류 발생!"
    exit 1
fi

# 모델 훈련
python main.py --mode train --epochs 50

# 성능 평가
python main.py --mode evaluate

echo "자동 훈련 완료!"
```

---

더 많은 예제와 튜토리얼은 지속적으로 업데이트됩니다!