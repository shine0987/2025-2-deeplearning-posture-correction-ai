"""
통합 실행 및 테스트 스크립트
"""

import os
import sys
import logging
from pathlib import Path
import argparse

# 현재 디렉토리를 파이썬 패스에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 로깅 설정
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

def setup_sample_data():
    """샘플 데이터 설정"""
    data_dir = Path('data/train_images')
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # 샘플 폴더 구조 생성
    normal_dir = data_dir / 'normal'
    abnormal_dir = data_dir / 'abnormal'
    
    normal_dir.mkdir(exist_ok=True)
    abnormal_dir.mkdir(exist_ok=True)
    
    logging.info("샘플 데이터 폴더 구조 생성 완료")
    logging.info(f"정상 자세 이미지를 {normal_dir}에 넣어주세요")
    logging.info(f"비정상 자세 이미지를 {abnormal_dir}에 넣어주세요")
    
    return data_dir

def run_preprocessing(data_dir, labeled=True):
    """1단계: 전처리 실행"""
    logging.info("=== 1단계: 이미지 전처리 시작 ===")
    
    from src.preprocessing import PosePreprocessor
    
    preprocessor = PosePreprocessor()
    
    try:
        if labeled:
            # 라벨링된 데이터 처리
            all_data = preprocessor.process_labeled_data(str(data_dir))
        else:
            # 단일 폴더 처리
            all_data = preprocessor.process_image_folder(str(data_dir))
        
        if all_data:
            # 데이터 저장
            preprocessor.save_data(all_data, 'data')
            logging.info(f"전처리 완료: 총 {len(all_data)}개 이미지 처리")
            return True
        else:
            logging.warning("처리된 데이터가 없습니다.")
            return False
            
    except Exception as e:
        logging.error(f"전처리 중 오류 발생: {e}")
        return False

def run_training():
    """2단계: LSTM 모델 훈련"""
    logging.info("=== 2단계: LSTM 모델 훈련 시작 ===")
    
    from src.lstm_model import PostureLSTMModel
    
    # 모델 저장 폴더 생성
    Path('models').mkdir(exist_ok=True)
    
    # LSTM 모델 초기화
    lstm_model = PostureLSTMModel(sequence_length=5, lstm_units=64)
    
    try:
        # 데이터 로드
        df = lstm_model.load_data('data/pose_data.csv')
        
        # 데이터 전처리
        X_train, X_test, y_train, y_test = lstm_model.prepare_data(df, augment=True)
        
        if len(X_train) == 0:
            logging.error("훈련 데이터가 없습니다.")
            return False
        
        # 모델 구성
        num_classes = len(lstm_model.label_encoder.classes_)
        input_shape = (5, len(lstm_model.feature_columns))
        
        lstm_model.build_model(input_shape, num_classes)
        
        # 모델 훈련
        history = lstm_model.train(
            X_train, X_test, y_train, y_test,
            epochs=50,  # 빠른 테스트를 위해 에폭 수 줄임
            batch_size=16
        )
        
        # 모델 평가
        accuracy, report, cm = lstm_model.evaluate(X_test, y_test)
        
        # 모델 저장
        lstm_model.save_model()
        
        logging.info("LSTM 모델 훈련 완료!")
        return True
        
    except Exception as e:
        logging.error(f"훈련 중 오류 발생: {e}")
        return False

def run_realtime_monitor():
    """3단계: 실시간 웹캠 모니터링"""
    logging.info("=== 3단계: 실시간 웹캠 모니터링 시작 ===")
    
    from src.realtime_cam import RealtimePostureMonitor
    
    try:
        # 모니터링 시스템 초기화
        monitor = RealtimePostureMonitor(model_path='models/posture_lstm_model.h5')
        
        # 실행
        monitor.run(camera_id=0, show_window=True)
        
        return True
        
    except Exception as e:
        logging.error(f"실시간 모니터링 중 오류 발생: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='자세 교정 AI 시스템')
    parser.add_argument('--step', choices=['all', 'preprocess', 'train', 'monitor'], 
                       default='all', help='실행할 단계 선택')
    parser.add_argument('--setup', action='store_true', 
                       help='샘플 데이터 폴더 설정')
    
    args = parser.parse_args()
    
    # 현재 디렉토리 확인
    os.chdir(Path(__file__).parent)
    
    try:
        if args.setup:
            setup_sample_data()
            return
        
        success = True
        
        if args.step in ['all', 'preprocess']:
            # 데이터 폴더 확인
            data_dir = Path('data/train_images')
            if not data_dir.exists():
                data_dir = setup_sample_data()
            
            success = run_preprocessing(data_dir, labeled=True)
            if not success:
                logging.error("전처리 실패")
                return
        
        if args.step in ['all', 'train'] and success:
            # CSV 파일 확인
            if not Path('data/pose_data.csv').exists():
                logging.error("전처리 데이터가 없습니다. 먼저 전처리를 실행하세요.")
                return
            
            success = run_training()
            if not success:
                logging.error("모델 훈련 실패")
                return
        
        if args.step in ['all', 'monitor'] and success:
            # 모델 파일 확인
            if not Path('models/posture_lstm_model.h5').exists():
                logging.error("훈련된 모델이 없습니다. 먼저 모델을 훈련하세요.")
                return
            
            run_realtime_monitor()
        
        if success:
            logging.info("🎉 모든 단계가 성공적으로 완료되었습니다!")
        
    except KeyboardInterrupt:
        logging.info("사용자에 의해 중단됨")
    except Exception as e:
        logging.error(f"실행 중 오류 발생: {e}")

if __name__ == '__main__':
    main()