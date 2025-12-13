from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, 
    QLineEdit, QPushButton, QLabel, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

class FriendTab(QWidget):
    def __init__(self):
        super().__init__()
        # 예시 데이터 (나중엔 users.json이나 DB에서 불러와야 함)
        self.friends = ["Dr.Strange", "IronMan", "SpiderMan"]
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # 1. 친구 추가 영역
        add_layout = QHBoxLayout()
        self.input_friend = QLineEdit()
        self.input_friend.setPlaceholderText("친구 ID 입력 (예: User123)")
        self.input_friend.setStyleSheet("padding: 10px; border: 1px solid #ddd; border-radius: 5px;")
        
        btn_add = QPushButton("친구 추가")
        btn_add.setStyleSheet("background-color: #0078D7; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
        btn_add.clicked.connect(self.add_friend)
        
        add_layout.addWidget(self.input_friend)
        add_layout.addWidget(btn_add)
        layout.addLayout(add_layout)

        # 2. 친구 목록 타이틀
        lbl_list = QLabel("내 친구 목록")
        lbl_list.setFont(QFont("Malgun Gothic", 14, QFont.Weight.Bold))
        layout.addWidget(lbl_list)

        # 3. 친구 리스트 위젯
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget { border: 1px solid #e0e0e0; border-radius: 10px; padding: 10px; }
            QListWidget::item { padding: 10px; border-bottom: 1px solid #f0f0f0; }
        """)
        layout.addWidget(self.list_widget)

        # 초기 목록 로드
        self.refresh_list()

        # 4. 하단 액션 버튼 (대결 신청)
        self.btn_battle = QPushButton("자세 대결 신청")
        self.btn_battle.setFixedHeight(50)
        self.btn_battle.setStyleSheet("""
            background-color: #6f42c1; color: white; font-size: 16px; font-weight: bold; border-radius: 10px;
        """)
        self.btn_battle.clicked.connect(self.request_battle)
        layout.addWidget(self.btn_battle)

    def refresh_list(self):
        self.list_widget.clear()
        for name in self.friends:
            item = QListWidgetItem(f"👤 {name}")
            # 폰트 등 설정 가능
            self.list_widget.addItem(item)

    def add_friend(self):
        text = self.input_friend.text().strip()
        if not text:
            return
        
        if text in self.friends:
            QMessageBox.warning(self, "중복", "이미 친구 목록에 있습니다.")
            return

        # 실제로는 여기서 DB 조회를 해야 함
        self.friends.append(text)
        self.refresh_list()
        self.input_friend.clear()
        QMessageBox.information(self, "성공", f"{text}님을 친구로 추가했습니다!")

    def request_battle(self):
        # 선택된 친구 확인
        current_item = self.list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "알림", "대결할 친구를 목록에서 선택해주세요.")
            return
        
        friend_name = current_item.text().replace("👤 ", "")
        # 대결 로직 (여기서는 메시지만 표시)
        QMessageBox.information(self, "대결 신청", f"'{friend_name}'님에게 자세 대결을 신청했습니다!\n(수락 대기...)")