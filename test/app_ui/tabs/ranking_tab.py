from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLabel, QComboBox, QFrame
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
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.date_filter_combo = QComboBox()
        self.date_filter_combo.setMinimumWidth(150)
        self.date_filter_combo.setStyleSheet("""
            QComboBox { padding: 5px; border: 1px solid #ccc; border-radius: 5px; background: white; }
        """)
        self.date_filter_combo.currentIndexChanged.connect(self.apply_filter_and_sort)
        header_layout.addWidget(self.date_filter_combo)
        
        layout.addLayout(header_layout)

        # --- 2. 랭킹 테이블 (수정됨) ---
        self.ranking_table = QTableWidget()
        
        # [변경] 컬럼 수 5개로 증가 (사용자, 날짜, 총 시간, 바른 자세, 성공률)
        self.ranking_table.setColumnCount(5)
        self.ranking_table.setHorizontalHeaderLabels(["사용자", "날짜", "총 시간", "바른 자세", "성공률"])
        
        self.ranking_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ranking_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.ranking_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.ranking_table.setAlternatingRowColors(True)
        # 사용자 컬럼(0번)은 내용에 맞게 줄이고, 나머지는 늘리기 옵션 (선택사항)
        self.ranking_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        
        self.ranking_table.setStyleSheet("""
            QTableWidget { border: 1px solid #e0e0e0; gridline-color: #f0f0f0; }
            QHeaderView::section { background-color: #f5f5f5; padding: 8px; border: none; font-weight: bold; }
        """)
        
        layout.addWidget(self.ranking_table)

        self.load_ranking()

    # ... (get_week_label, update_filter_options, load_ranking, apply_filter_and_sort 함수는 기존과 동일) ...
    # ... (생략된 부분은 위에서 작성해주신 코드 그대로 유지하세요) ...
    
    def get_week_label(self, date_str):
        """날짜 문자열 -> 주차 변환"""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            week_no = (dt.day - 1) // 7 + 1
            return f"{dt.year}년 {dt.month}월 {week_no}주차"
        except Exception:
            return "기타"

    def update_filter_options(self):
        """필터 옵션 갱신"""
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
        """[수정] 사용자 정보를 포함하여 테이블 표시"""
        self.ranking_table.setRowCount(len(records))
        
        for i, record in enumerate(records):
            total_sec = record.get("total_time", 0)
            correct_sec = record.get("correct_time", 0)
            date_str = record.get("date", "")
            
            # [NEW] 사용자 정보 파싱
            nickname = record.get("nickname", "Guest")
            avatar_raw = record.get("avatar", "👤")
            
            # 아바타 이모지 추출 로직 (MonitorTab과 동일)
            if "(" in avatar_raw and ")" in avatar_raw:
                emoji = avatar_raw.split("(")[1].split(")")[0]
            else:
                emoji = "👤" if "기본" in avatar_raw else avatar_raw
            
            user_display = f"{emoji} {nickname}"
            
            # 퍼센트 계산
            if total_sec > 0:
                percent_val = (correct_sec / total_sec) * 100
                percentage_text = f"{percent_val:.1f}%"
            else:
                percent_val = 0
                percentage_text = "0.0%"
            
            # 아이템 생성
            item_user = QTableWidgetItem(user_display) # [NEW]
            item_date = QTableWidgetItem(date_str)
            item_total = QTableWidgetItem(data_manager.format_time(total_sec))
            item_correct = QTableWidgetItem(data_manager.format_time(correct_sec))
            item_percent = QTableWidgetItem(percentage_text)
            
            # 정렬 설정
            item_user.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter) # 이름은 왼쪽 정렬이 예쁨
            item_date.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_total.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_correct.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_percent.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # [Design] 사용자 이름 약간 강조
            item_user.setFont(QFont("Malgun Gothic", 9, QFont.Weight.Bold))

            # 색상 적용
            if percent_val >= 80:
                color = QColor("#4CAF50")
                item_percent.setFont(QFont("Malgun Gothic", 9, QFont.Weight.Bold))
            elif percent_val >= 50:
                color = QColor("#FF9800")
            else:
                color = QColor("#F44336")
            item_percent.setForeground(color)

            # 테이블에 추가 (컬럼 인덱스 주의: 0부터 시작)
            self.ranking_table.setItem(i, 0, item_user)    # 0: 사용자
            self.ranking_table.setItem(i, 1, item_date)    # 1: 날짜
            self.ranking_table.setItem(i, 2, item_total)   # 2: 총 시간
            self.ranking_table.setItem(i, 3, item_correct) # 3: 바른 시간
            self.ranking_table.setItem(i, 4, item_percent) # 4: 성공률
            
        self.ranking_table.resizeRowsToContents()