# 📚 완전한 문서 가이드

**LSTM 자세 분석 시스템의 모든 문서를 한눈에!**

---

## 📋 **문서 구조**

```
docs/
├── README.md           ← 👈 이 파일 (시작점)
├── QUICK_START.md      ← ⚡ 1분 시작 가이드
├── COMPLETE_GUIDE.md   ← 📖 완전한 사용법
├── TROUBLESHOOTING.md  ← 🔧 문제 해결
└── EXAMPLES.md         ← 💡 실전 예제
```

---

## 🎯 **상황별 문서 찾기**

### 🚀 **처음 사용하는 경우**
1. **[QUICK_START.md](QUICK_START.md)** - 1분만에 시작하기
2. **[COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)** - 자세한 설명이 필요할 때

### 💡 **실전 활용하려는 경우**
1. **[EXAMPLES.md](EXAMPLES.md)** - 6가지 실전 예제
2. **[COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)** - API 참조 가이드

### 🔧 **문제가 생긴 경우**
1. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - 문제 해결 가이드
2. **[COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)** - FAQ 섹션

---

## 📖 **문서별 특징**

### ⚡ **QUICK_START.md**
- **목적**: 최대한 빠르게 시작
- **시간**: 1-3분
- **내용**: 핵심 명령어만
- **대상**: 급한 사람

### 📖 **COMPLETE_GUIDE.md**
- **목적**: 완전한 이해
- **시간**: 10-20분
- **내용**: 모든 기능 설명
- **대상**: 제대로 배우고 싶은 사람

### 🔧 **TROUBLESHOOTING.md**
- **목적**: 문제 해결
- **시간**: 문제에 따라
- **내용**: 에러별 해결법
- **대상**: 오류 발생한 사람

### 💡 **EXAMPLES.md**
- **목적**: 실전 활용
- **시간**: 20-30분
- **내용**: 6가지 실제 사용 예제
- **대상**: 응용하고 싶은 사람

---

## 🗺️ **학습 로드맵**

### 📊 **초급자 경로**
```
QUICK_START.md → COMPLETE_GUIDE.md (기본 사용) → EXAMPLES.md (예제 1,2)
```

### 📈 **중급자 경로**
```
COMPLETE_GUIDE.md → EXAMPLES.md (모든 예제) → 개인 프로젝트
```

### 🎯 **고급자 경로**
```
COMPLETE_GUIDE.md (API 참조) → EXAMPLES.md (웹서비스, 앱연동) → 커스텀 구현
```

---

## 🎓 **핵심 개념 정리**

### 🧠 **LSTM 모델**
- **정의**: 시퀀스 데이터를 학습하는 신경망
- **용도**: 자세의 시간적 변화 패턴 학습
- **구조**: 2층 LSTM (32→16 유닛)

### 📊 **데이터 형식**
- **입력**: CSV 파일 (각도 + 좌표)
- **출력**: 정상/비정상 + 신뢰도
- **전처리**: 정규화 + 시퀀스 생성

### 🔄 **사용 플로우**
```
데이터 준비 → 모델 훈련 → 새 데이터 평가 → 결과 확인
```

---

## 📞 **도움말**

### ❓ **자주 묻는 질문**

**Q: 어떤 문서부터 읽어야 하나요?**
A: 처음이라면 `QUICK_START.md`부터 시작하세요!

**Q: 에러가 계속 발생해요**
A: `TROUBLESHOOTING.md`에서 해당 에러를 찾아보세요!

**Q: 실제 프로젝트에 적용하려면?**
A: `EXAMPLES.md`의 6가지 예제를 참고하세요!

**Q: 모든 기능을 다 알고 싶어요**
A: `COMPLETE_GUIDE.md`를 차근차근 읽어보세요!

### 💌 **문의 사항**
- 문서에서 해결되지 않는 문제
- 새로운 기능 요청
- 개선 사항 제안

**👉 언제든 문의해주세요!**

---

## 🎯 **빠른 액션**

### 🚀 **지금 바로 시작하기**
```bash
# 1단계: 훈련
python main.py --mode train --epochs 15

# 2단계: 평가  
python main.py --mode evaluate
```

### 💡 **예제 코드 실행하기**
```bash
# 실시간 자세 체크
python -c "
from external_data_interface import PostureEvaluator
evaluator = PostureEvaluator()
evaluator.load_model()
print('✅ 모델 로드 완료!')
"
```

### 🔧 **문제 해결하기**
```bash
# 환경 체크
python -c "import tensorflow; print('TensorFlow:', tensorflow.__version__)"
```

---

**🎉 이제 원하는 문서를 선택해서 시작해보세요!**

**⭐ 추천 순서**: QUICK_START → COMPLETE_GUIDE → EXAMPLES → TROUBLESHOOTING