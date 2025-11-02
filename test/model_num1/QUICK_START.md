# ⚡ 빠른 실행 가이드

## 🎯 3가지 실행 방법

### 방법 1: 배치 파일 실행 (가장 쉬움) 
```
start.bat 더블클릭 → 메뉴에서 선택
```

### 방법 2: 원클릭 명령어 (추천)
```powershell
.\.venv\Scripts\python.exe run_system.py --step all
```

### 방법 3: 단계별 실행
```powershell
# 1단계: 전처리
.\.venv\Scripts\python.exe run_system.py --step preprocess

# 2단계: 훈련  
.\.venv\Scripts\python.exe run_system.py --step train

# 3단계: 모니터링
.\.venv\Scripts\python.exe run_system.py --step monitor
```

## 📂 데이터 준비
1. 정상 자세 이미지 → `data/train_images/normal/`
2. 비정상 자세 이미지 → `data/train_images/abnormal/`
3. 각 폴더당 최소 10장 이상

## 🎮 웹캠 조작법
- **ESC**: 종료
- **R**: 리셋

## 🎨 색상 의미
- 🟢 초록: 정상 자세
- 🔴 빨강: 비정상 자세  
- ⚪ 회색: 인식 중

## 📞 문제 발생시
자세한 해결방법은 `EXECUTION_GUIDE.md` 참고