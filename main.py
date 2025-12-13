"""
메인 애플리케이션 실행 파일 (Entry Point)
위치: 프로젝트 루트 (2025-2-deeplearning-posture-correction-ai/main.py)
"""
import sys
import os
import warnings

# 불필요한 경고 메시지 무시
warnings.filterwarnings("ignore", category=UserWarning, message="SymbolDatabase.GetPrototype")

# --- [중요] 경로 설정 ---
# 1. 현재 실행 중인 파일(main.py)의 위치를 루트로 잡습니다.
current_file_path = os.path.abspath(__file__)
root_dir = os.path.dirname(current_file_path)

# 2. 'test' 폴더 경로를 계산합니다.
#    (app_ui가 test 폴더 안에 있으므로, test 폴더를 경로에 추가해야 app_ui를 찾습니다)
test_dir = os.path.join(root_dir, "test")

# 3. 파이썬에게 검색 경로 추가 (순서 중요)
#    루트 경로 추가
if root_dir not in sys.path:
    sys.path.append(root_dir)

#    [핵심 수정] test 경로도 추가! -> 그래야 'from app_ui ...' 가 작동함
if test_dir not in sys.path:
    sys.path.append(test_dir)

# 4. 작업 디렉토리를 루트로 고정 (모델 파일 로드를 위해)
os.chdir(root_dir)

print(f"📂 실행 위치(Root): {root_dir}")

# --- 모듈 임포트 ---
try:
    # test 폴더가 sys.path에 있으므로, 그 안의 app_ui를 바로 부를 수 있습니다.
    from app_ui.main_window import MainWindow
    from app_ui.login_dialog import LoginDialog
    import app_ui.data_manager as data_manager
except ImportError as e:
    print(f"\n❌ 임포트 오류 발생: {e}")
    print(f"확인: '{test_dir}' 폴더 안에 'app_ui' 폴더가 있는지 확인하세요.")
    print(f"확인: 'app_ui' 폴더 안에 '__init__.py' 파일이 있는지 확인하세요.\n")
    sys.exit(1)

from PyQt6.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    
    # 1. 자동 로그인 확인
    config = data_manager.load_config()
    
    if config.get("is_auto_login") and config.get("saved_id"):
        user_id = config.get("saved_id")
        data_manager.set_current_user(user_id)
        print(f"🔄 자동 로그인 성공: {user_id}")
        
        window = MainWindow()
        window.show()
        sys.exit(app.exec())

    # 2. 로그인 창 실행
    login = LoginDialog()
    if login.exec() == LoginDialog.DialogCode.Accepted:
        print(f"로그인 성공! 환영합니다.")
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit()

if __name__ == "__main__":
    main()