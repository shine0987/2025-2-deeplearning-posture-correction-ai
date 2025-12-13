from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, 
    QMessageBox, QFrame, QCheckBox, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import app_ui.data_manager as data_manager

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setFixedSize(300, 400)
        self.setStyleSheet("background-color: white;")
        
        # UI 초기화
        self.init_ui()
        
        self.load_initial_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 1. 로고/타이틀
        title_label = QLabel("Posture AI")
        title_label.setFont(QFont("Malgun Gothic", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #333;")
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 2. 입력 폼 컨테이너
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                background-color: #fafafa;
            }
            QLineEdit:focus {
                border: 1px solid #007AFF;
                background-color: #fff;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(10)
        
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("아이디")
        
        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("비밀번호")
        self.pw_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw_input.returnPressed.connect(self.try_login) # 엔터키로 로그인
        
        form_layout.addWidget(self.id_input)
        form_layout.addWidget(self.pw_input)
        layout.addWidget(form_frame)
        
        # [NEW] 체크박스 영역 (입력창 아래, 버튼 위)
        check_layout = QHBoxLayout()
        check_layout.setContentsMargins(10, 0, 10, 0)
        
        self.remember_id_check = QCheckBox("아이디 저장")
        self.auto_login_check = QCheckBox("자동 로그인")
        
        # 스타일링 (선택 사항)
        checkbox_style = "QCheckBox { font-size: 13px; color: #555; }"
        self.remember_id_check.setStyleSheet(checkbox_style)
        self.auto_login_check.setStyleSheet(checkbox_style)

        check_layout.addWidget(self.remember_id_check)
        check_layout.addStretch() # 사이 간격 벌리기
        check_layout.addWidget(self.auto_login_check)
        
        layout.addLayout(check_layout) # 메인 레이아웃에 추가
        
        # 3. 버튼 영역
        self.login_btn = QPushButton("로그인")
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                padding: 12px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.login_btn.clicked.connect(self.try_login)
        
        self.register_btn = QPushButton("계정 만들기")
        self.register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666;
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                text-decoration: underline;
                color: #333;
            }
        """)
        self.register_btn.clicked.connect(self.try_register)
        
        layout.addWidget(self.login_btn)
        layout.addWidget(self.register_btn)
        
    def load_initial_settings(self):
        """[NEW] 저장된 설정으로 UI 초기화"""
        config = data_manager.load_config()
        
        # 1. 아이디 저장 체크 여부
        if config.get("is_remember_id"):
            self.remember_id_check.setChecked(True)
            self.id_input.setText(config.get("saved_id", ""))
            
        # 2. 자동 로그인 체크 여부
        if config.get("is_auto_login"):
            self.auto_login_check.setChecked(True)
            # 자동 로그인이 켜져있으면 아이디 저장도 켜는게 일반적
            self.remember_id_check.setChecked(True) 
            self.id_input.setText(config.get("saved_id", ""))    
    
    def try_login(self):
        user_id = self.id_input.text().strip()
        password = self.pw_input.text().strip()
        
        if not user_id or not password:
            QMessageBox.warning(self, "알림", "아이디와 비밀번호를 입력해주세요.")
            return

        # 로그인 시도
        if data_manager.login_user(user_id, password):
            # [NEW] 로그인 성공 시 -> 설정(Config) 파일 업데이트
            is_remember = self.remember_id_check.isChecked()
            is_auto = self.auto_login_check.isChecked()
            
            # 자동 로그인이면 아이디 저장은 필수
            if is_auto: 
                is_remember = True
            
            data_manager.save_config(user_id, is_remember, is_auto)
            
            self.accept()
        else:
            QMessageBox.critical(self, "로그인 실패", "아이디 또는 비밀번호가 틀렸습니다.")
    
    
    def try_register(self):
        user_id = self.id_input.text().strip()
        password = self.pw_input.text().strip()
        
        if not user_id or not password:
            QMessageBox.warning(self, "알림", "가입할 아이디와 비밀번호를 입력해주세요.")
            return
            
        if data_manager.register_user(user_id, password):
            QMessageBox.information(self, "성공", "회원가입이 완료되었습니다.\n로그인해주세요.")
        else:
            QMessageBox.warning(self, "실패", "이미 존재하는 아이디입니다.")