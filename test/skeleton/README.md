# skeltonpose 실행 가이드

간단한 사용법만 빠르게 보고 싶을 때 이 파일을 참조하세요. 자세한 환경별 설치/실행 가이드는 `README_RUN.md`를 참고하세요.

요약
- 권장 Python: 3.10
- 의존성: `requirements.txt`
- 기본 입력 폴더: `labeling_test_images`
- 기본 출력 폴더: 처리된 이미지 `processed_images`, CSV `csv_results`

Windows (PowerShell) - 빠른 시작
```powershell
cd C:\path\to\project
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
.\.venv\Scripts\python.exe skeltonpose.py
```

원본을 보존하고 결과를 별도 폴더로 저장
```powershell
.\.venv\Scripts\python.exe skeltonpose.py --processed_folder processed_images --csv_folder csv_results
```

macOS / Linux (빠른 시작)
```bash
cd /path/to/project
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python skeltonpose.py --processed_folder processed_images --csv_folder csv_results
```

Docker (옵션)
- `README_RUN.md`에 예시 Dockerfile이 있습니다. Docker로 실행하려면 그 파일을 참고하세요.

문제 발생 시
- Mediapipe 관련 설치 문제는 공식 문서 참고
- Windows PowerShell 실행 정책 문제는 `Activate.ps1` 대신 `activate` 스크립트로 시도

