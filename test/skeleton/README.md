skeltonpose 사용 안내

요약
- 이 저장소에는 `skeltonpose.py`가 포함되어 있으며, Mediapipe를 사용해 이미지에서 포즈 랜드마크를 추출하고 상체(목/어깨/허리) 좌표를 CSV로 저장합니다.
- 이미지에는 전체 스켈레톤을 그려 덮어쓰거나(옵션) 백업 폴더로 원본을 보존할 수 있습니다.

권장 환경
- Windows 10/11
- Python 3.8+ (3.10~3.12 권장)
- 가상환경을 프로젝트 루트 대신 ASCII 경로(예: `C:\temp\mp_env`)에 생성하는 것을 권장합니다.
  - 이유: OneDrive나 비ASCII 경로에 설치된 일부 바이너리(예: Mediapipe)가 동작하지 않을 수 있습니다.

설치 (PowerShell)
```powershell
# 권장: ASCII 경로에 venv 생성
py -3 -m venv C:\temp\mp_env
& 'C:\temp\mp_env\Scripts\python.exe' -m pip install --upgrade pip
& 'C:\temp\mp_env\Scripts\python.exe' -m pip install -r requirements.txt
```

실행 예시 (PowerShell)
- 기본 실행 (labeling_test_images 폴더 사용, CSV 저장명 기본값):
```powershell
& 'C:\temp\mp_env\Scripts\python.exe' 'C:\Users\user\OneDrive\Desktop\과제\딥러닝\skeleton\skeltonpose.py'
```
- 입력 폴더와 결과 파일명 지정, 원본 백업:
```powershell
& 'C:\temp\mp_env\Scripts\python.exe' 'C:\Users\user\OneDrive\Desktop\과제\딥러닝\skeleton\skeltonpose.py' --input_folder 'C:\Users\user\OneDrive\Desktop\과제\딥러닝\skeleton\labeling_test_images' --result 'C:\Users\user\OneDrive\Desktop\과제\딥러닝\skeleton\skeleton_coords.csv' --backup 'C:\Users\user\OneDrive\Desktop\과제\딥러닝\skeleton\backup_A1'
```
- 백업 없이 입력 폴더의 이미지 덮어쓰기:
```powershell
& 'C:\temp\mp_env\Scripts\python.exe' 'C:\Users\user\skeleton\skeltonpose.py' --input_folder 'C:\Users\user\skeleton\labeling_test_images' --result 'C:\Users\user\OneDrive\Desktop\과제\딥러닝\skeleton\skeleton_coords.csv'
```

옵션 설명
- --input_folder: 처리할 이미지 폴더 경로 (기본: labeling_test_images)
- --result: 결과 CSV 파일 경로/이름 (기본: skeleton_coords.csv)
- --no_overwrite: 원본 이미지를 덮어쓰지 않고 `_skeleton.jpg`로 저장
- --backup: 원본 이미지를 복사할 백업 폴더 경로 (선택)

출력
- `skeleton_coords.csv`: 이미지별 상체(목/좌/우 어깨/좌/우 엉덩이) 정규화 좌표 및 픽셀 좌표
- `skeleton_angles.csv`: neck/shoulder/hip 각도(도 단위)
- (옵션) `skeleton_angles_summary.csv`: 각도 평균/분산 (요청 시 생성)

문제 해결 팁
- Mediapipe import 또는 초기화 에러가 발생하면 가상환경을 OneDrive/한글 경로가 아닌 ASCII 경로에 만들어 실행해 보세요.
- OpenCV가 한글/OneDrive 경로에서 imread/imwrite에 실패하면 스크립트는 내부적으로 안전한 I/O(`numpy.fromfile` + `cv2.imdecode`, `cv2.imencode` + `tofile`)를 사용합니다.

GUI 사용
- `gui.py`를 실행하면 간단한 Tkinter 창이 뜨며, 폴더 선택과 실행 버튼으로 동일한 처리를 수행할 수 있습니다.
- GUI 실행 (PowerShell):
```powershell
& 'C:\temp\mp_env\Scripts\python.exe' 'C:\Users\user\skeleton\gui.py'
```

추가 요청
- 원하는 출력 형식(예: 추가 메타 정보, 타임스탬프, JSON 출력 등)이 있으면 알려주세요.

만약 오류나 문제 시 Visual_Studio 안의 ai모델 "GitHub Copilot" 사용 추천

