"""
자세 분류 LSTM 모델 통합 실행 스크립트
훈련부터 평가까지 전체 과정을 관리하는 메인 스크립트입니다.
"""

import os
import sys
import argparse
from datetime import datetime
from typing import Dict, Optional

# 로컬 모듈 import
from training_module import PostureTrainer
from external_data_interface import PostureEvaluator

def print_banner():
    """프로그램 시작 배너 출력"""
    print("="*70)
    print("  자세 분류 LSTM 모델 - 정상/비정상 자세 평가 시스템")
    print("  Posture Classification LSTM Model")
    print("="*70)
    print()

def train_model(base_path: str, config: Optional[Dict] = None) -> bool:
    """
    모델 훈련을 수행합니다.
    
    Args:
        base_path (str): 데이터가 있는 기본 경로
        config (Dict, optional): 훈련 설정
        
    Returns:
        bool: 훈련 성공 여부
    """
    print("🚀 모델 훈련 시작...")
    
    # 기본 설정
    default_config = {
        'use_angles': True,
        'use_coords': True,
        'lstm_units': [32, 16],
        'dropout_rate': 0.2,
        'learning_rate': 0.001,
        'epochs': 30,
        'batch_size': 4,
        'validation_split': 0.2
    }
    
    if config:
        default_config.update(config)
    
    try:
        # 훈련기 초기화
        trainer = PostureTrainer(base_path, sequence_length=3)
        
        # 훈련 실행
        results = trainer.full_training_pipeline(default_config)
        
        if results:
            print("\\n✅ 모델 훈련 완료!")
            print(f"   최종 정확도: {results['evaluation_results']['test_accuracy']:.4f}")
            return True
        else:
            print("\\n❌ 모델 훈련 실패!")
            return False
            
    except Exception as e:
        print(f"\\n❌ 훈련 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

def evaluate_data(base_path: str, angles_csv: str, coords_csv: str, 
                 output_path: Optional[str] = None) -> bool:
    """
    새로운 데이터를 평가합니다.
    
    Args:
        base_path (str): 모델이 있는 기본 경로
        angles_csv (str): 각도 데이터 CSV 파일 경로
        coords_csv (str): 좌표 데이터 CSV 파일 경로
        output_path (str, optional): 결과 저장 경로
        
    Returns:
        bool: 평가 성공 여부
    """
    print("🔍 데이터 평가 시작...")
    
    try:
        # 평가기 초기화 및 모델 로드
        evaluator = PostureEvaluator(base_path=base_path)
        
        if not evaluator.load_model():
            print("❌ 모델을 로드할 수 없습니다.")
            return False
        
        # 출력 경로 설정
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(base_path, "results", f"evaluation_results_{timestamp}.json")
        
        # 데이터 평가
        results = evaluator.evaluate_csv_data(angles_csv, coords_csv, output_path)
        
        if results:
            print("\\n✅ 데이터 평가 완료!")
            print(f"   총 샘플: {results['summary']['total_samples']}")
            print(f"   정상 자세: {results['summary']['normal_count']}")
            print(f"   비정상 자세: {results['summary']['abnormal_count']}")
            print(f"   결과 저장: {output_path}")
            return True
        else:
            print("\\n❌ 데이터 평가 실패!")
            return False
            
    except Exception as e:
        print(f"\\n❌ 평가 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_model_info(base_path: str) -> None:
    """모델 정보를 출력합니다."""
    print("ℹ️  모델 정보 조회...")
    
    try:
        evaluator = PostureEvaluator(base_path=base_path)
        
        if evaluator.load_model():
            model_info = evaluator.get_model_info()
            
            print("\\n📊 모델 정보:")
            print(f"   모델 경로: {model_info.get('model_path', 'N/A')}")
            print(f"   시퀀스 길이: {model_info.get('sequence_length', 'N/A')}")
            print(f"   클래스: {model_info.get('class_names', 'N/A')}")
            print(f"   클래스 수: {model_info.get('n_classes', 'N/A')}")
        else:
            print("❌ 모델을 찾을 수 없습니다.")
            
    except Exception as e:
        print(f"❌ 모델 정보 조회 중 오류: {e}")

def interactive_mode(base_path: str) -> None:
    """대화형 모드로 실행합니다."""
    print("🎯 대화형 모드")
    print("사용 가능한 명령:")
    print("  1. train    - 모델 훈련")
    print("  2. evaluate - 데이터 평가")
    print("  3. info     - 모델 정보")
    print("  4. quit     - 종료")
    print()
    
    while True:
        try:
            command = input("명령을 입력하세요 (1-4): ").strip().lower()
            
            if command in ['1', 'train']:
                print("\\n모델 훈련을 시작합니다...")
                train_model(base_path)
                
            elif command in ['2', 'evaluate']:
                print("\\n데이터 평가를 시작합니다...")
                
                # 기본 데이터 파일 사용
                angles_csv = os.path.join(base_path, "skeleton_angles.csv")
                coords_csv = os.path.join(base_path, "skeleton_coords.csv")
                
                if os.path.exists(angles_csv) and os.path.exists(coords_csv):
                    evaluate_data(base_path, angles_csv, coords_csv)
                else:
                    print("❌ 기본 데이터 파일을 찾을 수 없습니다.")
                    print(f"   필요한 파일: {angles_csv}, {coords_csv}")
                
            elif command in ['3', 'info']:
                show_model_info(base_path)
                
            elif command in ['4', 'quit', 'exit']:
                print("👋 프로그램을 종료합니다.")
                break
                
            else:
                print("❌ 잘못된 명령입니다. 1-4 중에서 선택하세요.")
                
            print()  # 빈 줄 추가
            
        except KeyboardInterrupt:
            print("\\n\\n👋 프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"❌ 오류 발생: {e}")

def main():
    """메인 함수"""
    print_banner()
    
    # 명령행 인자 파싱
    parser = argparse.ArgumentParser(description="자세 분류 LSTM 모델")
    parser.add_argument("--base_path", type=str, 
                       default=r"c:\\Users\\user\\OneDrive\\Desktop\\test\\Lstm_model",
                       help="데이터 및 모델이 있는 기본 경로")
    parser.add_argument("--mode", type=str, choices=['train', 'evaluate', 'info', 'interactive'],
                       default='interactive', help="실행 모드")
    parser.add_argument("--angles_csv", type=str, help="각도 데이터 CSV 파일 경로")
    parser.add_argument("--coords_csv", type=str, help="좌표 데이터 CSV 파일 경로")
    parser.add_argument("--output", type=str, help="결과 저장 경로")
    parser.add_argument("--epochs", type=int, default=30, help="훈련 에포크 수")
    parser.add_argument("--batch_size", type=int, default=4, help="배치 크기")
    
    args = parser.parse_args()
    
    # 기본 경로 확인
    if not os.path.exists(args.base_path):
        print(f"❌ 기본 경로를 찾을 수 없습니다: {args.base_path}")
        return
    
    print(f"📁 기본 경로: {args.base_path}")
    print(f"🎯 실행 모드: {args.mode}")
    print()
    
    # 모드에 따른 실행
    if args.mode == 'train':
        config = {
            'epochs': args.epochs,
            'batch_size': args.batch_size
        }
        success = train_model(args.base_path, config)
        sys.exit(0 if success else 1)
        
    elif args.mode == 'evaluate':
        if not args.angles_csv or not args.coords_csv:
            # 기본 파일 사용
            angles_csv = os.path.join(args.base_path, "skeleton_angles.csv")
            coords_csv = os.path.join(args.base_path, "skeleton_coords.csv")
        else:
            angles_csv = args.angles_csv
            coords_csv = args.coords_csv
        
        success = evaluate_data(args.base_path, angles_csv, coords_csv, args.output)
        sys.exit(0 if success else 1)
        
    elif args.mode == 'info':
        show_model_info(args.base_path)
        
    elif args.mode == 'interactive':
        interactive_mode(args.base_path)

def create_sample_usage_script():
    """사용 예제 스크립트를 생성합니다."""
    usage_script = '''# 자세 분류 LSTM 모델 사용 예제

## 1. 모델 훈련
python main.py --mode train --epochs 50 --batch_size 8

## 2. 데이터 평가
python main.py --mode evaluate --angles_csv "새로운_각도데이터.csv" --coords_csv "새로운_좌표데이터.csv"

## 3. 모델 정보 확인
python main.py --mode info

## 4. 대화형 모드 (기본)
python main.py

## Python 코드에서 직접 사용하는 방법:

```python
from external_data_interface import PostureEvaluator

# 평가기 초기화
evaluator = PostureEvaluator(base_path="./")

# 모델 로드
if evaluator.load_model():
    # CSV 데이터 평가
    results = evaluator.evaluate_csv_data("angles.csv", "coords.csv")
    
    # 단일 샘플 평가
    angles_data = {"neck_angle": 130, "shoulder_angle_deg": 160, "hip_angle_deg": 140}
    coords_data = {"lm_0_x": 0.5, "lm_0_y": 0.2, ...}  # 좌표 데이터
    
    result = evaluator.evaluate_single_sample(angles_data, coords_data, "test_image.jpg")
    print(f"예측: {result['prediction']}, 신뢰도: {result['confidence']}")
```
'''
    
    with open("USAGE_EXAMPLES.md", "w", encoding="utf-8") as f:
        f.write(usage_script)
    
    print("✅ 사용 예제 파일 생성: USAGE_EXAMPLES.md")

if __name__ == "__main__":
    # 사용 예제 스크립트 생성
    create_sample_usage_script()
    
    # 메인 프로그램 실행
    main()