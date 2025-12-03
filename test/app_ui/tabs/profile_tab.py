from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, 
    QComboBox, QFormLayout, QFrame, QStackedLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import sys
import app_ui.data_manager as data_manager

class ProfileTab(QWidget):
    """
    프로필 탭: 명함(Card) 스타일 조회 화면 (칭호, 뱃지, 랭킹 포함) & 수정 화면
    """
    def __init__(self):
        super().__init__()
        # 메인 레이아웃: 조회 모드 <-> 수정 모드 전환
        self.stacked_layout = QStackedLayout()
        self.setLayout(self.stacked_layout)

        self.init_view_page()   # Page 0: 조회 (ID Card 스타일)
        self.init_edit_page()   # Page 1: 수정 (Form 스타일)

        self.check_and_load_initial_view()

    # --- 1. 조회 페이지 (View Mode) ---
    def init_view_page(self):
        page_widget = QWidget()
        layout = QVBoxLayout(page_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        # [Card Design] 프로필 카드 프레임
        card_frame = QFrame()
        card_frame.setFixedWidth(380) # 너비 약간 넓힘
        card_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 20px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(30, 40, 30, 40)
        card_layout.setSpacing(10)

        # 1-1. 아바타
        self.view_avatar_label = QLabel("👤")
        self.view_avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.view_avatar_label.setStyleSheet("font-size: 80px; border: none; background: transparent;")
        card_layout.addWidget(self.view_avatar_label)

        # [NEW] 1-2. 칭호 (Title)
        self.view_title_label = QLabel("칭호 없음")
        self.view_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.view_title_label.setFont(QFont("Malgun Gothic", 10, QFont.Weight.Bold))
        # 캡슐 모양 스타일
        self.view_title_label.setStyleSheet("""
            color: white; 
            background-color: #6C757D; 
            border-radius: 10px; 
            padding: 4px 10px;
            margin-bottom: 5px;
        """)
        # 라벨 자체 크기를 글자에 맞추기 위해 레이아웃 감싸기
        title_container = QHBoxLayout()
        title_container.addStretch()
        title_container.addWidget(self.view_title_label)
        title_container.addStretch()
        card_layout.addLayout(title_container)

        # 1-3. 닉네임
        self.view_nickname_label = QLabel("Guest")
        self.view_nickname_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.view_nickname_label.setFont(QFont("Malgun Gothic", 20, QFont.Weight.Bold))
        self.view_nickname_label.setStyleSheet("color: #0078D7; border: none;")
        card_layout.addWidget(self.view_nickname_label)

        # [NEW] 1-4. 대표 뱃지 (Badge)
        self.view_badge_label = QLabel("🏅 뱃지 정보 없음")
        self.view_badge_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.view_badge_label.setFont(QFont("Malgun Gothic", 11))
        self.view_badge_label.setStyleSheet("color: #FF9800; border: none; font-weight: bold; margin-bottom: 15px;")
        card_layout.addWidget(self.view_badge_label)

        # 1-5. 구분선
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #f0f0f0; max-height: 1px;")
        card_layout.addWidget(line)

        # [NEW] 1-6. 정보 (랭킹 추가)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(0)
        
        # 키
        self.view_height_label = self.create_stat_widget("키", "0 cm")
        stats_layout.addLayout(self.view_height_label)
        
        # 구분선 1
        stats_layout.addWidget(self.create_v_line())

        # 몸무게
        self.view_weight_label = self.create_stat_widget("몸무게", "0 kg")
        stats_layout.addLayout(self.view_weight_label)

        # 구분선 2
        stats_layout.addWidget(self.create_v_line())

        # [NEW] 랭킹
        self.view_rank_label = self.create_stat_widget("랭킹", "- 위")
        stats_layout.addLayout(self.view_rank_label)

        card_layout.addLayout(stats_layout)
        layout.addWidget(card_frame)

        # 1-7. 버튼 그룹
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(10)
        
        # 수정 버튼
        self.edit_btn = QPushButton("프로필 수정")
        self.edit_btn.setFixedWidth(380)
        self.edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078D7; 
                color: white; 
                border-radius: 8px; 
                padding: 12px; 
                font-weight: bold; font-size: 14px;
            }
            QPushButton:hover { background-color: #005a9e; }
        """)
        self.edit_btn.clicked.connect(self.go_to_edit_mode)
        btn_layout.addWidget(self.edit_btn)

        # 로그아웃 버튼
        self.logout_btn = QPushButton("로그아웃")
        self.logout_btn.setFixedWidth(380)
        self.logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: white; 
                color: #dc3545; 
                border: 1px solid #dc3545;
                border-radius: 8px; 
                padding: 12px; 
                font-weight: bold;
            }
            QPushButton:hover { background-color: #dc3545; color: white; }
        """)
        self.logout_btn.clicked.connect(self.logout)
        btn_layout.addWidget(self.logout_btn)

        layout.addLayout(btn_layout)
        self.stacked_layout.addWidget(page_widget)

    def create_stat_widget(self, title, value):
        """정보 표시용 소형 레이아웃"""
        l = QVBoxLayout()
        l.setContentsMargins(5, 5, 5, 5)
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #888; font-size: 12px; border: none;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_val = QLabel(value)
        lbl_val.setStyleSheet("color: #333; font-size: 15px; font-weight: bold; border: none;")
        lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        l.addWidget(lbl_title)
        l.addWidget(lbl_val)
        return l

    def create_v_line(self):
        """세로 구분선 생성"""
        v_line = QFrame()
        v_line.setFrameShape(QFrame.Shape.VLine)
        v_line.setStyleSheet("background-color: #e0e0e0; max-width: 1px; margin-top: 10px; margin-bottom: 10px;")
        return v_line

    # --- 2. 수정 페이지 (Edit Mode) ---
    def init_edit_page(self):
        page_widget = QWidget()
        layout = QVBoxLayout(page_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 폼 컨테이너
        form_frame = QFrame()
        form_frame.setFixedWidth(380)
        form_frame.setStyleSheet("""
            QFrame { background-color: white; border-radius: 15px; border: 1px solid #e0e0e0; }
            QLineEdit, QComboBox { 
                padding: 10px; border: 1px solid #ddd; border-radius: 5px; background: #fafafa;
            }
            QLineEdit:focus { border: 1px solid #0078D7; background: white; }
            QLabel { font-weight: bold; color: #555; border: none; }
        """)
        
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(20)

        title = QLabel("프로필 설정")
        title.setFont(QFont("Malgun Gothic", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #333; margin-bottom: 10px; border: none;")
        form_layout.addWidget(title)

        # 입력 필드
        self.input_nickname = QLineEdit()
        self.input_nickname.setPlaceholderText("닉네임")

        self.input_height = QLineEdit()
        self.input_height.setPlaceholderText("키 (cm)")

        self.input_weight = QLineEdit()
        self.input_weight.setPlaceholderText("몸무게 (kg)")

        self.input_avatar = QComboBox()
        self.input_avatar.addItems([
            "기본 아바타 (👤)", "고양이 (🐱)", "강아지 (🐶)", "로봇 (🤖)", 
            "외계인 (👽)", "유령 (👻)", "여우 (🦊)", "판다 (🐼)"
        ])

        # Form Layout
        fl = QFormLayout()
        fl.setVerticalSpacing(15)
        fl.addRow("닉네임", self.input_nickname)
        fl.addRow("키", self.input_height)
        fl.addRow("몸무게", self.input_weight)
        fl.addRow("아바타", self.input_avatar)
        form_layout.addLayout(fl)

        layout.addWidget(form_frame)

        # 버튼 그룹 (저장/취소)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        cancel_btn = QPushButton("취소")
        cancel_btn.setFixedSize(185, 45)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("background-color: #f0f0f0; color: #333; border-radius: 8px; font-weight: bold;")
        cancel_btn.clicked.connect(self.cancel_edit)
        
        save_btn = QPushButton("저장 (Save)")
        save_btn.setFixedSize(185, 45)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet("background-color: #28A745; color: white; border-radius: 8px; font-weight: bold;")
        save_btn.clicked.connect(self.save_profile)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        self.stacked_layout.addWidget(page_widget)

    # --- Logic ---

    def check_and_load_initial_view(self):
        data = data_manager.load_profile()
        if data and data.get("nickname"):
            self.update_view_page(data)
            self.stacked_layout.setCurrentIndex(0) # View
        else:
            self.stacked_layout.setCurrentIndex(1) # Edit

    def update_view_page(self, data):
        """조회 화면 데이터 갱신 (예시 데이터 포함)"""
        # 1. 기본 정보
        self.view_nickname_label.setText(data.get("nickname", "Guest"))
        
        # 2. [NEW] 칭호, 뱃지, 랭킹 (DB에 없으면 예시 데이터 표시)
        # 실제로는 data_manager나 서버에서 계산된 값을 가져와야 합니다.
        title = data.get("title", "바른 자세 입문자")  # 예시 데이터
        badge = data.get("badge", "🐢 거북목 탈출기") # 예시 데이터
        ranking = data.get("ranking", "상위 15%")     # 예시 데이터

        self.view_title_label.setText(title)
        self.view_badge_label.setText(badge)

        # 3. 신체 정보 및 랭킹 업데이트
        # 레이아웃 내부 위젯 접근 (Label)
        h_val_label = self.view_height_label.itemAt(1).widget()
        w_val_label = self.view_weight_label.itemAt(1).widget()
        r_val_label = self.view_rank_label.itemAt(1).widget()
        
        h_val_label.setText(f"{data.get('height', '-')} cm")
        w_val_label.setText(f"{data.get('weight', '-')} kg")
        r_val_label.setText(ranking)

        # 4. 아바타
        avatar_txt = data.get("avatar", "👤")
        if "(" in avatar_txt:
            emoji = avatar_txt.split("(")[1].split(")")[0]
        else:
            emoji = "👤"
        self.view_avatar_label.setText(emoji)

    def go_to_edit_mode(self):
        data = data_manager.load_profile()
        self.input_nickname.setText(data.get("nickname", ""))
        self.input_height.setText(data.get("height", ""))
        self.input_weight.setText(data.get("weight", ""))
        
        current_avatar = data.get("avatar", "기본 아바타 (👤)")
        index = self.input_avatar.findText(current_avatar)
        if index >= 0:
            self.input_avatar.setCurrentIndex(index)
        
        self.stacked_layout.setCurrentIndex(1)

    def cancel_edit(self):
        data = data_manager.load_profile()
        if data and data.get("nickname"):
            self.stacked_layout.setCurrentIndex(0)
        else:
            pass 

    def save_profile(self):
        # 칭호/뱃지/랭킹은 사용자가 수정하는 정보가 아니므로 저장하지 않음 (유지)
        new_data = {
            "nickname": self.input_nickname.text(),
            "height": self.input_height.text(),
            "weight": self.input_weight.text(),
            "avatar": self.input_avatar.currentText(),
            
            # (옵션) 기존에 있던 칭호/뱃지 정보가 사라지지 않게 하려면 로드해서 merge 해야 함
            # 여기서는 편의상 생략하거나, DB 로직에서 처리
        }
        
        data_manager.save_profile(new_data)
        self.update_view_page(new_data)
        self.stacked_layout.setCurrentIndex(0)

    def logout(self):
        try:
            current_config = data_manager.load_config()
            data_manager.save_config(
                current_config.get("saved_id", ""), 
                current_config.get("is_remember_id", False), 
                False 
            )
            QMessageBox.information(self, "로그아웃", "로그아웃 되었습니다.\n프로그램을 종료합니다.")
            sys.exit(0)
        except Exception as e:
            print(f"로그아웃 오류: {e}")
            sys.exit(0)