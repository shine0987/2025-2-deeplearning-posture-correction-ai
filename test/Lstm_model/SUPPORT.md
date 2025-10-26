# 자세 분류 LSTM 모델 - 도움말 센터

## 📞 지원 채널

### 🔧 기술 지원
- **이슈 트래킹**: GitHub Issues
- **문서**: README.md, USER_MANUAL.md
- **예제**: EXAMPLES.md

### 📚 학습 자료
- **빠른 시작**: QUICK_START.md
- **API 문서**: USER_MANUAL.md의 API 참조 섹션
- **튜토리얼**: EXAMPLES.md

## 🆘 문제 해결 단계

### 1단계: 기본 확인사항
```bash
# Python 버전 확인
python --version

# 패키지 설치 확인
pip list | grep tensorflow
pip list | grep pandas

# 파일 구조 확인
ls -la *.csv
ls -la labeled/
```

### 2단계: 로그 확인
```bash
# 상세 오류 정보와 함께 실행
python main.py --mode train 2>&1 | tee training.log
```

### 3단계: 데이터 검증
```bash
# 데이터 전처리 단독 실행
python data_preprocessing.py
```

### 4단계: 단계별 디버깅
```python
# 각 모듈을 개별적으로 테스트
python -c "from data_preprocessing import PostureDataProcessor; print('데이터 모듈 OK')"
python -c "from lstm_model import PostureLSTMModel; print('모델 모듈 OK')"
python -c "from external_data_interface import PostureEvaluator; print('평가 모듈 OK')"
```

## 🐛 일반적인 오류 및 해결책

### 오류 1: ModuleNotFoundError
```
오류: ModuleNotFoundError: No module named 'tensorflow'
해결: pip install -r requirements.txt
```

### 오류 2: KeyError (컬럼 누락)
```
오류: KeyError: "['neck_angle'] not in index"
해결: CSV 파일에 필수 컬럼 확인
- skeleton_angles.csv: neck_angle, shoulder_angle_deg, hip_angle_deg
- skeleton_coords.csv: lm_0_x, lm_0_y, lm_11_x, lm_11_y, 등
```

### 오류 3: 메모리 부족
```
오류: ResourceExhaustedError: OOM when allocating tensor
해결: 배치 크기 줄이기
python main.py --mode train --batch_size 2
```

### 오류 4: 모델 파일 없음
```
오류: 모델을 찾을 수 없습니다
해결: 먼저 모델 훈련
python main.py --mode train
```

### 오류 5: 데이터 부족
```
오류: 생성된 시퀀스: (5, 3, 23) - 데이터가 너무 적음
해결: 더 많은 데이터 수집 또는 sequence_length 줄이기
```

## 📋 체크리스트

### 설치 전 체크리스트
- [ ] Python 3.8+ 설치됨
- [ ] pip 최신 버전
- [ ] 충분한 저장공간 (최소 1GB)
- [ ] 인터넷 연결 (패키지 설치용)

### 데이터 준비 체크리스트
- [ ] skeleton_angles.csv 파일 존재
- [ ] skeleton_coords.csv 파일 존재
- [ ] 필수 컬럼 모두 포함
- [ ] 결측값 없음
- [ ] image_path 컬럼 일치
- [ ] labeled/ 폴더 구조 올바름

### 훈련 전 체크리스트
- [ ] 모든 패키지 설치됨
- [ ] 데이터 검증 완료
- [ ] 충분한 메모리 확보
- [ ] models/ 폴더 쓰기 권한
- [ ] results/ 폴더 쓰기 권한

### 평가 전 체크리스트
- [ ] 훈련된 모델 존재
- [ ] 평가할 CSV 파일 준비
- [ ] 파일 형식 일치
- [ ] 컬럼명 일치

## 🔍 디버깅 도구

### 데이터 검사 스크립트
```python
import pandas as pd
import numpy as np

def debug_data(angles_csv, coords_csv):
    print("🔍 데이터 디버깅 시작")
    
    # 파일 존재 확인
    import os
    print(f"각도 파일 존재: {os.path.exists(angles_csv)}")
    print(f"좌표 파일 존재: {os.path.exists(coords_csv)}")
    
    if not os.path.exists(angles_csv) or not os.path.exists(coords_csv):
        return
    
    # 데이터 로드
    angles_df = pd.read_csv(angles_csv)
    coords_df = pd.read_csv(coords_csv)
    
    print(f"\\n📊 데이터 형태:")
    print(f"각도: {angles_df.shape}")
    print(f"좌표: {coords_df.shape}")
    
    print(f"\\n📋 각도 컬럼: {list(angles_df.columns)}")
    print(f"📋 좌표 컬럼: {list(coords_df.columns)}")
    
    # 필수 컬럼 확인
    required_angle_cols = ['image_path', 'neck_angle', 'shoulder_angle_deg', 'hip_angle_deg']
    missing_angle_cols = [col for col in required_angle_cols if col not in angles_df.columns]
    
    if missing_angle_cols:
        print(f"❌ 누락된 각도 컬럼: {missing_angle_cols}")
    else:
        print("✅ 각도 컬럼 모두 존재")
    
    # 결측값 확인
    print(f"\\n🔍 결측값:")
    print(f"각도: {angles_df.isnull().sum().sum()}")
    print(f"좌표: {coords_df.isnull().sum().sum()}")
    
    # 공통 이미지 확인
    common_images = set(angles_df['image_path']) & set(coords_df['image_path'])
    print(f"\\n🔗 공통 이미지: {len(common_images)}개")
    print(f"각도만: {len(set(angles_df['image_path']) - common_images)}")
    print(f"좌표만: {len(set(coords_df['image_path']) - common_images)}")

# 사용법
debug_data('skeleton_angles.csv', 'skeleton_coords.csv')
```

### 모델 상태 확인 스크립트
```python
import os
import glob

def debug_model():
    print("🔍 모델 상태 확인")
    
    # 모델 폴더 확인
    models_dir = "models"
    if not os.path.exists(models_dir):
        print("❌ models/ 폴더가 없습니다.")
        return
    
    # 모델 파일 찾기
    model_files = glob.glob(os.path.join(models_dir, "*.keras"))
    
    if not model_files:
        print("❌ 훈련된 모델이 없습니다.")
        print("해결: python main.py --mode train 실행")
    else:
        print(f"✅ {len(model_files)}개 모델 발견:")
        for model_file in model_files:
            file_size = os.path.getsize(model_file) / 1024 / 1024  # MB
            print(f"  - {os.path.basename(model_file)} ({file_size:.1f}MB)")
    
    # 결과 폴더 확인
    results_dir = "results"
    if os.path.exists(results_dir):
        result_files = os.listdir(results_dir)
        print(f"\\n📊 결과 파일: {len(result_files)}개")
    else:
        print("\\n📊 결과 폴더 없음")
```

## 📞 지원 요청 시 포함할 정보

### 기본 정보
```bash
# 시스템 정보
python --version
pip --version
whoami
pwd

# 파일 목록
ls -la *.csv
ls -la models/
ls -la results/
```

### 오류 정보
- 전체 오류 메시지 (traceback 포함)
- 실행한 명령어
- 사용한 데이터 파일 정보
- 예상했던 결과

### 데이터 샘플
```bash
# CSV 파일 첫 5줄
head -5 skeleton_angles.csv
head -5 skeleton_coords.csv
```

### 환경 정보
```bash
pip freeze > environment.txt
```

## 📧 연락 방법

### GitHub Issues (권장)
1. https://github.com/your-repo/issues 방문
2. "New Issue" 클릭
3. 템플릿에 따라 정보 입력
4. 라벨 선택 (bug, question, enhancement 등)

### 이슈 템플릿
```markdown
## 🐛 버그 리포트 / ❓ 질문

### 환경 정보
- OS: Windows 10 / macOS / Ubuntu
- Python 버전: 3.x.x
- 설치 방법: pip install -r requirements.txt

### 문제 설명
[문제를 자세히 설명해주세요]

### 재현 단계
1. 실행한 명령어: `python main.py --mode train`
2. 발생한 오류: [오류 메시지 전체]
3. 예상 결과: [기대했던 동작]

### 추가 정보
- 데이터 크기: X개 샘플
- 실행 환경: 로컬 / 서버
- 기타 특이사항: [있다면 작성]
```

---

**💡 팁**: 문제 해결이 안 되면 단계별로 천천히 진행하고, 각 단계의 결과를 확인하세요!