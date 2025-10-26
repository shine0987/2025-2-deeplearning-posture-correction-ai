# 🛠️ 문제 해결 센터

**오류가 발생했나요? 여기서 해결하세요!**

---

## 🚨 **긴급 복구**

### 💥 **모든 게 안 될 때**
```bash
# 1. 폴더 확인
cd "c:\Users\user\OneDrive\Desktop\test\Lstm_model"

# 2. 패키지 재설치
pip uninstall tensorflow pandas numpy scikit-learn matplotlib opencv-python -y
pip install tensorflow pandas numpy scikit-learn matplotlib opencv-python

# 3. 처음부터 다시
python main.py --mode train --epochs 10
```

---

## ❌ **자주 발생하는 오류들**

### 1. "모델을 찾을 수 없습니다"
**원인**: AI 모델이 아직 훈련되지 않음
```bash
# 해결
python main.py --mode train --epochs 15
```

### 2. "KeyError: 'neck_angle'"
**원인**: CSV 파일 컬럼명이 잘못됨
```bash
# CSV 파일 첫 줄 확인
head -1 skeleton_angles.csv

# 필요한 컬럼들:
# neck_angle, shoulder_angle_deg, hip_angle_deg
```

### 3. "ModuleNotFoundError: No module named 'tensorflow'"
**원인**: 패키지가 설치되지 않음
```bash
# 해결
pip install tensorflow
# 또는
pip install -r requirements.txt
```

### 4. "ResourceExhaustedError: OOM" (메모리 부족)
**원인**: 컴퓨터 메모리 부족
```bash
# 해결: 더 작은 배치 크기 사용
python main.py --mode train --batch_size 2 --epochs 10
```

### 5. "Permission denied"
**원인**: 파일 쓰기 권한 없음
```bash
# Windows에서 해결
# 1. 관리자 권한으로 명령 프롬프트 실행
# 2. 또는 다른 폴더로 프로젝트 복사
```

---

## 🔍 **진단 도구**

### 📊 **시스템 체크**
```bash
# Python 버전 확인 (3.8+ 필요)
python --version

# 패키지 설치 확인
pip list | grep tensorflow
pip list | grep pandas

# 데이터 파일 확인
ls *.csv
dir *.csv  # Windows
```

### 🧪 **단계별 테스트**
```bash
# 1단계: 데이터 처리 테스트
python data_preprocessing.py

# 2단계: 모델 구조 테스트  
python -c "from lstm_model import PostureLSTMModel; print('모델 OK')"

# 3단계: 전체 시스템 테스트
python main.py --mode info
```

---

## 💡 **성능 문제 해결**

### 🐌 **훈련이 너무 느려요**
```bash
# 해결: 에포크 수와 배치 크기 조정
python main.py --mode train --epochs 10 --batch_size 8
```

### 📉 **정확도가 너무 낮아요 (50% 미만)**
```bash
# 해결 1: 더 많이 훈련
python main.py --mode train --epochs 50

# 해결 2: 더 많은 데이터 준비 (각 클래스당 최소 20개)
```

### 💾 **용량이 너무 커요**
```bash
# 해결: 불필요한 파일 삭제
rm -rf __pycache__  # Linux/Mac
rmdir /s __pycache__  # Windows
```

---

## 🆘 **도움 요청하기**

### 📋 **버그 리포트 템플릿**
```
🐛 **문제**: [간단히 설명]

💻 **환경**:
- OS: Windows 10/11
- Python: [버전]
- 오류 메시지: [전체 복사]

🔄 **재현 단계**:
1. [실행한 명령어]
2. [발생한 오류]

📎 **추가 정보**:
- 데이터 크기: [X개 샘플]
- 실행 시간: [X분]
```

### 📞 **연락처**
- **GitHub Issues**: 프로젝트 저장소의 Issues 탭
- **빠른 질문**: README.md 하단 연락처

---

## ✅ **해결 완료 체크리스트**

문제가 해결되었는지 확인하세요:

- [ ] 오류 메시지가 사라짐
- [ ] 모델 훈련이 완료됨 ("훈련 완료!" 메시지)
- [ ] `models/` 폴더에 `.keras` 파일 생성됨
- [ ] `results/` 폴더에 결과 파일들 생성됨
- [ ] 평가 명령어가 정상 작동함

**모든 항목이 체크되면 성공!** 🎉

---

**여전히 문제가 있으시면 GitHub Issues에 자세한 정보와 함께 문의해주세요!** 🙋‍♂️