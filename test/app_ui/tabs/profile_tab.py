from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, 
    QComboBox, QFormLayout, QFrame, QStackedLayout, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor
import app_ui.data_manager as data_manager
import sys

class ProfileTab(QWidget):
    """
    프로필 탭 UI: 조회 모드와 수정 모드를 스위칭하며 제공
    """
    def __init__(self):
        super().__init__()
        # 메인 레이아웃은 페이지를 겹쳐서 보여주는 StackedLayout 사용
        self.stacked_layout = QStackedLayout()
        self.setLayout(self.stacked_layout)

        self.init_view_page()   # 페이지 0: 프로필 조회 (카드 UI)
        self.init_edit_page()   # 페이지 1: 프로필 수정/생성 (입력 폼)

        self.check_and_load_initial_view() # 초기 화면 결정

    def init_view_page(self):
        """페이지 0: 저장된 프로필을 예쁘게 보여주는 뷰"""
        page_widget = QWidget()
        layout = QVBoxLayout(page_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        # === 프로필 카드 (배경 박스) ===
        card_frame = QFrame()
        card_frame.setFixedWidth(320)
        card_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #e0e0e0;
            }
        """)
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(30, 40, 30, 40)
        card_layout.setSpacing(15)
        
        # [NEW] 로그아웃 버튼 (수정 버튼 아래나 옆에 추가)
        self.logout_btn = QPushButton("로그아웃")
        self.logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_btn.setStyleSheet("""
            background-color: #f44336; color: white; border-radius: 8px; padding: 10px; font-weight: bold;
        """)
        self.logout_btn.clicked.connect(self.logout)
        
        # 버튼 레이아웃에 추가 (예: 수정 버튼과 나란히 두거나 아래에)
        layout.addWidget(self.logout_btn, alignment=Qt.AlignmentFlag.AlignCenter) 
        
        self.stacked_layout.addWidget(page_widget)

        # 1. 아바타 아이콘 (텍스트로 대체하거나 이미지 로드 가능)
        self.view_avatar_label = QLabel("👤")
        self.view_avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.view_avatar_label.setFont(QFont("Segoe UI Emoji", 48))
        self.view_avatar_label.setStyleSheet("border: none; background: transparent;")
        card_layout.addWidget(self.view_avatar_label)

        # 2. 닉네임 표시
        self.view_nickname_label = QLabel("사용자 이름")
        self.view_nickname_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.view_nickname_label.setFont(QFont("Malgun Gothic", 18, QFont.Weight.Bold))
        self.view_nickname_label.setStyleSheet("color: #333; border: none;")
        card_layout.addWidget(self.view_nickname_label)

        # 3. 구분선
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #f0f0f0; border: none; max-height: 1px;")
        card_layout.addWidget(line)

        # 4. 신체 정보 (키/몸무게)
        stats_layout = QHBoxLayout()
        
        # 키
        self.view_height_label = QLabel("0 cm")
        self.view_height_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.view_height_label.setStyleSheet("color: #666; font-size: 14px; border: none;")
        
        # 몸무게
        self.view_weight_label = QLabel("0 kg")
        self.view_weight_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.view_weight_label.setStyleSheet("color: #666; font-size: 14px; border: none;")

        stats_layout.addWidget(self.view_height_label)
        stats_layout.addWidget(self.view_weight_label)
        card_layout.addLayout(stats_layout)

        layout.addWidget(card_frame)

        # === 수정 버튼 ===
        self.edit_btn = QPushButton("프로필 수정")
        self.edit_btn.setFixedWidth(200)
        self.edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
                font-family: 'Malgun Gothic';
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        self.edit_btn.clicked.connect(self.go_to_edit_mode)
        layout.addWidget(self.edit_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.stacked_layout.addWidget(page_widget)

    def init_edit_page(self):
        """페이지 1: 정보를 입력하는 수정 폼"""
        page_widget = QWidget()
        layout = QVBoxLayout(page_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 폼 컨테이너
        form_frame = QFrame()
        form_frame.setFixedWidth(350)
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border-radius: 12px;
                border: 1px solid #ddd;
            }
            QLabel {
                font-size: 13px;
                color: #555;
                border: none;
            }
            QLineEdit, QComboBox {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(15)

        # 제목
        title = QLabel("프로필 설정")
        title.setFont(QFont("Malgun Gothic", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #333; margin-bottom: 10px; border: none;")
        form_layout.addWidget(title)

        # 입력 필드들
        self.input_nickname = QLineEdit()
        self.input_nickname.setPlaceholderText("닉네임")

        self.input_height = QLineEdit()
        self.input_height.setPlaceholderText("키 (cm)")

        self.input_weight = QLineEdit()
        self.input_weight.setPlaceholderText("몸무게 (kg)")

        self.input_avatar = QComboBox()
        self.input_avatar.addItems(["기본 아바타 (👤)", "고양이 (🐱)", "강아지 (🐶)", "로봇 (🤖)"])

        # Form Layout으로 라벨과 배치
        fl = QFormLayout()
        fl.addRow("닉네임", self.input_nickname)
        fl.addRow("키", self.input_height)
        fl.addRow("몸무게", self.input_weight)
        fl.addRow("아바타", self.input_avatar)
        form_layout.addLayout(fl)

        layout.addWidget(form_frame)

        # 버튼 영역
        btn_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("취소")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            background-color: #e0e0e0; border-radius: 5px; padding: 8px 15px; color: #333;
        """)
        cancel_btn.clicked.connect(self.cancel_edit)
        
        save_btn = QPushButton("저장하기")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet("""
            background-color: #007AFF; border-radius: 5px; padding: 8px 15px; color: white; font-weight: bold;
        """)
        save_btn.clicked.connect(self.save_profile)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
        self.stacked_layout.addWidget(page_widget)

    # --- 로직 ---

    def check_and_load_initial_view(self):
        """데이터 존재 여부에 따라 초기 화면 결정"""
        data = data_manager.load_profile()
        if data and data.get("nickname"):
            self.update_view_page(data)
            self.stacked_layout.setCurrentIndex(0) # 조회 모드
        else:
            self.stacked_layout.setCurrentIndex(1) # 수정 모드 (데이터 없음)

    def update_view_page(self, data):
        """조회 페이지 UI 데이터 갱신"""
        self.view_nickname_label.setText(data.get("nickname", "이름 없음"))
        self.view_height_label.setText(f"{data.get('height', '-')} cm")
        self.view_weight_label.setText(f"{data.get('weight', '-')} kg")
        
        # 아바타 텍스트에서 이모지만 추출하거나 맵핑 (간단히 구현)
        avatar_txt = data.get("avatar", "👤")
        if "🐱" in avatar_txt: self.view_avatar_label.setText("🐱")
        elif "🐶" in avatar_txt: self.view_avatar_label.setText("🐶")
        elif "🤖" in avatar_txt: self.view_avatar_label.setText("🤖")
        else: self.view_avatar_label.setText("👤")

    def go_to_edit_mode(self):
        """수정 버튼 클릭 시: 입력 폼에 기존 데이터 채워넣고 화면 전환"""
        data = data_manager.load_profile()
        self.input_nickname.setText(data.get("nickname", ""))
        self.input_height.setText(data.get("height", ""))
        self.input_weight.setText(data.get("weight", ""))
        self.input_avatar.setCurrentText(data.get("avatar", "기본 아바타 (👤)"))
        
        self.stacked_layout.setCurrentIndex(1) # 수정 모드로 이동

    def cancel_edit(self):
        """취소 버튼: 데이터가 있으면 조회화면, 없으면 그대로"""
        data = data_manager.load_profile()
        if data and data.get("nickname"):
            self.stacked_layout.setCurrentIndex(0)
        else:
            # 데이터가 아예 없는데 취소하면 할 게 없음 (앱 종료 혹은 빈 폼 유지)
            pass

    def save_profile(self):
        """저장 버튼: 파일 저장 후 조회 화면으로 이동"""
        new_data = {
            "nickname": self.input_nickname.text(),
            "height": self.input_height.text(),
            "weight": self.input_weight.text(),
            "avatar": self.input_avatar.currentText()
        }
        
        data_manager.save_profile(new_data)
        
        # 저장 후 뷰 갱신 및 이동
        self.update_view_page(new_data)
        self.stacked_layout.setCurrentIndex(0)
        
        
    def logout(self):
        """로그아웃 처리: 설정 초기화 및 앱 재시작"""
        # 1. 설정 파일에서 '자동 로그인' 해제
        # (현재 아이디는 남겨둘지 말지 결정. 보통 자동로그인만 끕니다)
        current_config = data_manager.load_config()
        data_manager.save_config(
            current_config.get("saved_id", ""), 
            current_config.get("is_remember_id", False), 
            False # 자동 로그인 OFF
        )
        
        # 2. 안내 메시지
        # QMessageBox.information(self, "로그아웃", "로그아웃 되었습니다.\n프로그램을 종료합니다.")
        
        # 3. 앱 종료 (사용자가 다시 켜면 로그인 창이 뜸)
        sys.exit(0)
        