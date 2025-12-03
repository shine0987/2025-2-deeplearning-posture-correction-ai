from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLabel, QComboBox, QFrame, 
    QAbstractItemView, QDialog, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from datetime import datetime
import app_ui.data_manager as data_manager

class RankingTab(QWidget):
    def __init__(self):
        super().__init__()
        self.all_records = [] 
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- 1. 상단 헤더 ---
        header_layout = QHBoxLayout()
        title = QLabel("🏆 명예의 전당")
        title.setFont(QFont("Malgun Gothic", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #333;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # 필터 콤보박스 디자인 개선
        self.date_filter_combo = QComboBox()
        self.date_filter_combo.setMinimumWidth(150)
        self.date_filter_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.date_filter_combo.setStyleSheet("""
            QComboBox { 
                padding: 8px; border: 1px solid #ccc; border-radius: 8px; background: white; 
            }
            QComboBox::drop-down { border: none; }
        """)
        self.date_filter_combo.currentIndexChanged.connect(self.apply_filter_and_sort)
        header_layout.addWidget(self.date_filter_combo)
        
        layout.addLayout(header_layout)

        # --- 2. 랭킹 테이블 (디자인 대폭 개선) ---
        self.ranking_table = QTableWidget()
        
        # 컬럼 정의
        self.ranking_table.setColumnCount(5)
        self.ranking_table.setHorizontalHeaderLabels(["순위/사용자", "날짜", "총 시간", "바른 자세", "성공률"])
        
        # 헤더 설정
        header = self.ranking_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # 이름은 내용만큼
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents) # 날짜도 내용만큼
        
        # 테이블 속성 설정
        self.ranking_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # 수정 불가
        self.ranking_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows) # 행 단위 선택
        self.ranking_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection) # 하나만 선택 가능
        self.ranking_table.setShowGrid(False) # [Design] 격자무늬 제거 (깔끔함)
        self.ranking_table.setAlternatingRowColors(True)
        self.ranking_table.verticalHeader().setVisible(False) # 행 번호 숨김
        
        # [NEW] 더블 클릭 시 상세 정보 팝업 연결
        self.ranking_table.cellDoubleClicked.connect(self.show_user_details)

        # 테이블 스타일시트 (오피스 블루 테마)
        self.ranking_table.setStyleSheet("""
            QTableWidget { 
                border: 1px solid #e0e0e0; 
                border-radius: 10px;
                background-color: white;
                alternate-background-color: #F9FAFB;
            }
            QHeaderView::section { 
                background-color: white; 
                padding: 12px; 
                border: none; 
                border-bottom: 2px solid #0078D7; /* 파란 밑줄 포인트 */
                font-family: 'Malgun Gothic';
                font-weight: bold;
                font-size: 13px;
                color: #555;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #f0f0f0; /* 옅은 구분선 */
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD; /* 선택 시 아주 연한 파랑 */
                color: #000;
            }
        """)
        
        layout.addWidget(self.ranking_table)

        # 하단 팁 메시지
        tip_label = QLabel("💡 팁: 목록을 더블 클릭하면 친구 추가를 할 수 있습니다.")
        tip_label.setStyleSheet("color: #888; font-size: 12px;")
        tip_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(tip_label)

        self.load_ranking()

    # --- 유틸리티 메서드 ---
    def get_week_label(self, date_str):
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            week_no = (dt.day - 1) // 7 + 1
            return f"{dt.year}년 {dt.month}월 {week_no}주차"
        except Exception:
            return "기타"
            
    def format_display_date(self, date_str):
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%Y.%m.%d %H:%M") 
        except Exception:
            return date_str

    def update_filter_options(self):
        current_selection = self.date_filter_combo.currentText()
        unique_weeks = set()
        for record in self.all_records:
            date_str = record.get("date", "")
            if date_str:
                unique_weeks.add(self.get_week_label(date_str))
        
        sorted_weeks = sorted(list(unique_weeks), reverse=True)
        self.date_filter_combo.blockSignals(True)
        self.date_filter_combo.clear()
        self.date_filter_combo.addItem("전체 기간")
        self.date_filter_combo.addItems(sorted_weeks)
        
        index = self.date_filter_combo.findText(current_selection)
        if index >= 0: self.date_filter_combo.setCurrentIndex(index)
        else: self.date_filter_combo.setCurrentIndex(0)
        self.date_filter_combo.blockSignals(False)

    def load_ranking(self):
        self.all_records = data_manager.load_ranking()
        self.update_filter_options()
        self.apply_filter_and_sort()

    def apply_filter_and_sort(self):
        filter_text = self.date_filter_combo.currentText()
        filtered_records = []
        
        if filter_text == "전체 기간":
            filtered_records = self.all_records[:]
        else:
            for record in self.all_records:
                if self.get_week_label(record.get("date", "")) == filter_text:
                    filtered_records.append(record)
        
        filtered_records.sort(
            key=lambda x: (x.get("correct_time", 0), x.get("total_time", 0), x.get("date", "")), 
            reverse=True
        )
        self.display_records(filtered_records)

    def display_records(self, records):
        """테이블 데이터 표시 (메달 추가)"""
        self.ranking_table.setRowCount(len(records))
        
        for i, record in enumerate(records):
            total_sec = record.get("total_time", 0)
            correct_sec = record.get("correct_time", 0)
            raw_date = record.get("date", "")
            clean_date = self.format_display_date(raw_date)

            nickname = record.get("nickname", "Guest")
            avatar_raw = record.get("avatar", "👤")
            
            if "(" in avatar_raw and ")" in avatar_raw:
                emoji = avatar_raw.split("(")[1].split(")")[0]
            else:
                emoji = "👤" if "기본" in avatar_raw else avatar_raw
            
            # [Design] 순위에 따른 메달 표시
            if i == 0:
                rank_display = f"🥇 {emoji} {nickname}"
            elif i == 1:
                rank_display = f"🥈 {emoji} {nickname}"
            elif i == 2:
                rank_display = f"🥉 {emoji} {nickname}"
            else:
                rank_display = f"{i+1}. {emoji} {nickname}"
            
            # 퍼센트 계산
            if total_sec > 0:
                percent_val = (correct_sec / total_sec) * 100
                percentage_text = f"{percent_val:.1f}%"
            else:
                percent_val = 0
                percentage_text = "0.0%"
            
            # 아이템 생성
            item_user = QTableWidgetItem(rank_display)
            # 나중에 팝업에서 쓸 실제 닉네임을 숨겨진 데이터로 저장
            item_user.setData(Qt.ItemDataRole.UserRole, nickname) 
            
            item_date = QTableWidgetItem(clean_date)
            item_total = QTableWidgetItem(data_manager.format_time(total_sec))
            item_correct = QTableWidgetItem(data_manager.format_time(correct_sec))
            item_percent = QTableWidgetItem(percentage_text)
            
            # 정렬 및 폰트
            item_user.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            item_date.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_total.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_correct.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_percent.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            font_bold = QFont("Malgun Gothic", 9, QFont.Weight.Bold)
            item_user.setFont(font_bold)
            item_date.setFont(QFont("Malgun Gothic", 9))
            
            # 색상 적용
            if percent_val >= 80:
                color = QColor("#28A745") # Green
                item_percent.setFont(font_bold)
            elif percent_val >= 50:
                color = QColor("#0078D7") # Blue (변경: 오피스 테마에 맞춰 파랑으로)
            else:
                color = QColor("#DC3545") # Red
            item_percent.setForeground(color)

            self.ranking_table.setItem(i, 0, item_user)
            self.ranking_table.setItem(i, 1, item_date)
            self.ranking_table.setItem(i, 2, item_total)
            self.ranking_table.setItem(i, 3, item_correct)
            self.ranking_table.setItem(i, 4, item_percent)
            
        self.ranking_table.resizeRowsToContents()

    # --- [NEW] 상세 정보 팝업 ---
    def show_user_details(self, row, col):
        """더블 클릭 시 호출되는 사용자 상세 팝업"""
        # 클릭한 행의 0번째 컬럼(사용자 이름) 아이템 가져오기
        item = self.ranking_table.item(row, 0)
        if not item: return

        # 숨겨둔 닉네임 가져오기 (메달 등 장식 제거된 순수 이름)
        nickname = item.data(Qt.ItemDataRole.UserRole)
        
        # 팝업 다이얼로그 생성
        dialog = QDialog(self)
        dialog.setWindowTitle("사용자 정보")
        dialog.setFixedSize(300, 200)
        dialog.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        
        # 프로필 표시
        lbl_icon = QLabel("👤")
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icon.setStyleSheet("font-size: 50px;")
        layout.addWidget(lbl_icon)
        
        lbl_name = QLabel(nickname)
        lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_name.setFont(QFont("Malgun Gothic", 14, QFont.Weight.Bold))
        layout.addWidget(lbl_name)
        
        # 버튼 영역
        btn_layout = QHBoxLayout()
        
        btn_add = QPushButton("친구 추가")
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #0078D7; color: white; 
                border-radius: 5px; padding: 8px; font-weight: bold;
            }
            QPushButton:hover { background-color: #005a9e; }
        """)
        btn_add.clicked.connect(lambda: self.add_friend_action(nickname, dialog))
        
        btn_close = QPushButton("닫기")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0; color: #333; 
                border-radius: 5px; padding: 8px;
            }
        """)
        btn_close.clicked.connect(dialog.accept)
        
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)
        
        dialog.exec()

    def add_friend_action(self, nickname, dialog):
        """친구 추가 로직 (여기서는 메시지만)"""
        # 실제로는 여기서 FriendTab의 리스트에 추가하거나 DB에 저장해야 함
        QMessageBox.information(self, "친구 추가", f"'{nickname}'님을 친구 목록에 추가했습니다!")
        dialog.accept()