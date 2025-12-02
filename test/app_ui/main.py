"""
메인 애플리케이션 실행 파일 (Entry Point)
"""
import sys
import os

# --- [중요] 경로 설정 ---
# 현재 파일(main.py)의 위치를 기준으로 루트 폴더(model_num1)의 경로를 계산합니다.
current_file_path = os.path.abspath(__file__)
app_ui_dir = os.path.dirname(current_file_path)
root_dir = os.path.dirname(app_ui_dir)

# 1. 파이썬 임포트 경로에 루트 폴더 추가
#    (src.preprocessing 등을 임포트하기 위해)
sys.path.append(root_dir)

# 2. 현재 작업 디렉토리를 루트 폴더로 변경
#    (models/..., data/... 등 상대 경로 파일 접근을 위해)
os.chdir(root_dir)

# --- 경로 설정 후 모듈 임포트 ---
from app_ui.main_window import MainWindow
from app_ui.login_dialog import LoginDialog
from app_ui.style import STYLE_SHEET

import app_ui.data_manager as data_manager

from PyQt6.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    
    # 1. 자동 로그인 확인
    config = data_manager.load_config()
    
    # 자동 로그인 설정이 True이고, 저장된 ID가 있다면
    if config.get("is_auto_login") and config.get("saved_id"):
        user_id = config.get("saved_id")
        
        # [중요] 실제로는 여기서 비밀번호 검증 없이 ID만으로 통과시킵니다.
        # (로컬 앱이므로 config를 신뢰함. 보안이 중요하다면 토큰 방식 필요)
        data_manager.set_current_user(user_id)
        print(f"🔄 자동 로그인 성공: {user_id}")
        
        # 바로 메인 윈도우 실행
        window = MainWindow()
        window.show()
        sys.exit(app.exec())

    # 2. 자동 로그인이 아니면 -> 로그인 창 실행
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