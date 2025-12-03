from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QStackedWidget, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap

class TutorialTab(QWidget):
    """
    도움말 탭: 슬라이드 쇼 방식의 인터랙티브 튜토리얼
    """
    def __init__(self):
        super().__init__()
        self.total_pages = 4 
        self.current_page = 0
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # 1. 상단 제목
        self.title_label = QLabel("사용 가이드 (1/4)")
        self.title_label.setFont(QFont("Malgun Gothic", 16, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.title_label)

        # 2. 메인 컨텐츠 (슬라이드 쇼 영역)
        self.stacked_widget = QStackedWidget()
        
        # --- 페이지 1: 시작하기 ---
        page1 = self.create_page(
            title="STEP 1. 자세 측정 시작",
            desc="웹캠이 정면을 향하도록 설정하고\n'시작(Start)' 버튼을 눌러주세요.\nAI가 실시간으로 자세를 분석합니다.",
            img_placeholder_text="[이미지]\n웹캠 화면과 시작 버튼이\n보이는 스크린샷"
        )
        self.stacked_widget.addWidget(page1)

        # --- 페이지 2: 상태 확인 ---
        page2 = self.create_page(
            title="STEP 2. 상태 모니터링",
            desc="화면 상단의 상태 메시지를 확인하세요.\n초록색은 '바른 자세', 빨간색은 '나쁜 자세'입니다.\n거북목이 되지 않도록 주의하세요!",
            img_placeholder_text="[이미지]\n초록색/빨간색 상태 메시지가\n뜨는 화면 예시"
        )
        self.stacked_widget.addWidget(page2)

        # --- 페이지 3: 랭킹 시스템 ---
        page3 = self.create_page(
            title="STEP 3. 랭킹 도전",
            desc="자동으로 기록이 저장됩니다.\n'바른 자세 퍼센트(%)'를 높여\n랭킹 상위권에 도전해보세요!",
            img_placeholder_text="[이미지]\n랭킹 탭의 순위표와\n퍼센트 그래프 예시"
        )
        self.stacked_widget.addWidget(page3)
        
        # --- 페이지 4: 프로필 설정 ---
        page4 = self.create_page(
            title="STEP 4. 내 프로필",
            desc="프로필 탭에서 닉네임과 아바타를 설정하세요.\n랭킹판에 내 캐릭터가 표시됩니다.\n친구들과 함께 경쟁해보세요.",
            img_placeholder_text="[이미지]\n프로필 설정 화면과\n귀여운 아바타 예시"
        )
        self.stacked_widget.addWidget(page4)

        main_layout.addWidget(self.stacked_widget)

        # 3. 하단 네비게이션 버튼 (이전 / 다음)
        nav_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("이전")
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.setFixedSize(100, 40)
        self.prev_btn.clicked.connect(self.go_prev)
        self.prev_btn.setEnabled(False) # 첫 페이지라 비활성
        
        self.next_btn = QPushButton("다음")
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.setFixedSize(100, 40)
        self.next_btn.setStyleSheet("background-color: #007AFF; color: white; font-weight: bold;")
        self.next_btn.clicked.connect(self.go_next)

        nav_layout.addStretch()
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        nav_layout.addStretch()
        
        main_layout.addLayout(nav_layout)

    def create_page(self, title, desc, img_placeholder_text):
        """페이지 생성 헬퍼 함수"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        # 소제목
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Malgun Gothic", 14, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #333;")
        layout.addWidget(lbl_title, alignment=Qt.AlignmentFlag.AlignCenter)

        # 이미지 플레이스홀더 (나중에 이미지로 교체할 영역)
        img_frame = QLabel(img_placeholder_text)
        img_frame.setFixedSize(400, 250)
        img_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        img_frame.setStyleSheet("""
            background-color: #f0f0f0;
            border: 2px dashed #aaa;
            color: #888;
            border-radius: 10px;
        """)
        # 나중에 이미지를 넣으려면: 
        # img_frame.setPixmap(QPixmap("image_path.png").scaled(400, 250)) 
        # 하고 setStyleSheet는 제거하면 됩니다.
        
        layout.addWidget(img_frame, alignment=Qt.AlignmentFlag.AlignCenter)

        # 설명 텍스트
        lbl_desc = QLabel(desc)
        lbl_desc.setFont(QFont("Malgun Gothic", 11))
        lbl_desc.setStyleSheet("color: #555;")
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_desc, alignment=Qt.AlignmentFlag.AlignCenter)

        return page

    def go_next(self):
        """다음 페이지로 이동"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.stacked_widget.setCurrentIndex(self.current_page)
            self.update_nav_buttons()

    def go_prev(self):
        """이전 페이지로 이동"""
        if self.current_page > 0:
            self.current_page -= 1
            self.stacked_widget.setCurrentIndex(self.current_page)
            self.update_nav_buttons()

    def update_nav_buttons(self):
        """버튼 상태 및 페이지 제목 업데이트"""
        # 제목 업데이트 (예: 1/4 -> 2/4)
        self.title_label.setText(f"사용 가이드 ({self.current_page + 1}/{self.total_pages})")

        # 이전 버튼 활성/비활성
        self.prev_btn.setEnabled(self.current_page > 0)

        # 다음 버튼 텍스트 변경 (마지막 페이지면 '완료')
        if self.current_page == self.total_pages - 1:
            self.next_btn.setText("처음으로")
            self.next_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
            # 마지막에서 누르면 다시 처음으로
            self.next_btn.clicked.disconnect()
            self.next_btn.clicked.connect(self.reset_tutorial)
        else:
            self.next_btn.setText("다음")
            self.next_btn.setStyleSheet("background-color: #007AFF; color: white; font-weight: bold;")
            # 연결 복구 (혹시 마지막 페이지 갔다 왔을 때)
            try: self.next_btn.clicked.disconnect() 
            except: pass
            self.next_btn.clicked.connect(self.go_next)

    def reset_tutorial(self):
        """튜토리얼 처음으로 리셋"""
        self.current_page = 0
        self.stacked_widget.setCurrentIndex(0)
        self.update_nav_buttons()