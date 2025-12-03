import cv2
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFrame, QProgressBar, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QFont, QColor
from app_ui.data_manager import format_time

class MonitorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 전체 레이아웃 (좌: 카메라 / 우: 대시보드)
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # --- [LEFT] 카메라 영역 ---
        cam_container = QFrame()
        cam_container.setStyleSheet("background: black; border-radius: 15px;")
        cam_layout = QVBoxLayout(cam_container)
        cam_layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_label = QLabel("Loading Camera...")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("color: white; font-size: 14px;")
        # 카메라 꽉 차게 표시
        self.video_label.setScaledContents(True) 
        
        cam_layout.addWidget(self.video_label)
        main_layout.addWidget(cam_container, stretch=2) # 2/3 비율

        # --- [RIGHT] 대시보드 영역 ---
        dashboard_layout = QVBoxLayout()
        dashboard_layout.setSpacing(20)

        # 1. 현재 상태 카드 (Score Board)
        self.score_card = self.create_card("현재 상태")
        score_layout = QVBoxLayout(self.score_card)
        
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Malgun Gothic", 24, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #aaa;")
        
        self.score_label = QLabel("Score: 0")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_label.setFont(QFont("Malgun Gothic", 16))
        
        score_layout.addWidget(self.status_label)
        score_layout.addWidget(self.score_label)
        dashboard_layout.addWidget(self.score_card)

        # 2. 실시간 리포트 (게이지 바)
        self.report_card = self.create_card("실시간 리포트")
        report_layout = QVBoxLayout(self.report_card)
        
        report_layout.addWidget(QLabel("바른 자세 유지율"))
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #0078D7;
                width: 10px;
            }
        """)
        self.progress_bar.setValue(0)
        report_layout.addWidget(self.progress_bar)
        
        # 시간 표시
        time_layout = QGridLayout()
        self.lbl_total_time = QLabel("00:00")
        self.lbl_good_time = QLabel("00:00")
        self.lbl_total_time.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.lbl_good_time.setStyleSheet("color: #28A745; font-weight: bold; font-size: 14px;")
        
        time_layout.addWidget(QLabel("총 시간:"), 0, 0)
        time_layout.addWidget(self.lbl_total_time, 0, 1)
        time_layout.addWidget(QLabel("바른 시간:"), 1, 0)
        time_layout.addWidget(self.lbl_good_time, 1, 1)
        report_layout.addLayout(time_layout)
        
        dashboard_layout.addWidget(self.report_card)

        # 3. 컨트롤 버튼
        btn_layout = QHBoxLayout()
        self.start_button = QPushButton("측정 시작")
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_button.setFixedHeight(50)
        self.start_button.setStyleSheet("""
            background-color: #0078D7; color: white; border-radius: 10px; font-size: 16px; font-weight: bold;
        """)
        
        self.stop_button = QPushButton("종료")
        self.stop_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_button.setFixedHeight(50)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton { background-color: #dc3545; color: white; border-radius: 10px; font-size: 16px; font-weight: bold; }
            QPushButton:disabled { background-color: #e0e0e0; color: #aaa; }
        """)
        
        btn_layout.addWidget(self.start_button)
        btn_layout.addWidget(self.stop_button)
        dashboard_layout.addLayout(btn_layout)
        
        dashboard_layout.addStretch() # 남은 공간 채우기
        main_layout.addLayout(dashboard_layout, stretch=1) # 1/3 비율

    def create_card(self, title_text):
        """카드 스타일의 프레임 생성 헬퍼"""
        frame = QFrame()
        frame.setStyleSheet("background: white; border-radius: 10px; border: 1px solid #e0e0e0;")
        
        # 내부 레이아웃 설정이 필요하므로 여기서는 프레임만 리턴하고,
        # 타이틀은 사용하는 쪽에서 추가하거나, 이 함수 안에서 처리하려면 레이아웃을 리턴해야 함.
        # 편의상 프레임만 리턴하고 외부에서 레이아웃 잡는 방식 사용.
        # (하지만 타이틀을 여기서 박아주는게 깔끔하므로 수정)
        
        layout = QVBoxLayout(frame)
        title = QLabel(title_text)
        title.setFont(QFont("Malgun Gothic", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #333; border: none; padding-bottom: 5px; border-bottom: 2px solid #f0f0f0;")
        layout.addWidget(title)
        
        return frame

    # --- 기능 메서드 ---

    def set_loading_state(self):
        self.video_label.setText("모델 로딩 중...")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)

    def update_frame(self, frame):
        """웹캠 프레임을 QLabel에 표시 (색상 보정 적용)"""
        # 버튼 상태 동기화 (최초 1회)
        if not self.stop_button.isEnabled():
            self.stop_button.setEnabled(True)
            self.start_button.setEnabled(False)

        try:
            # frame은 OpenCV에서 온 BGR 데이터입니다.
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            
            # [수정] BGR -> RGB 변환을 명확하게 처리
            # 방법 1: OpenCV로 변환 후 QImage 생성 (가장 안전함)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # QImage 생성 (Format_RGB888 사용)
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            
            # 비율 유지하면서 라벨 크기에 맞게 조정
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(
                self.video_label.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.video_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            print(f"프레임 업데이트 오류: {e}")

    def update_posture_status(self, status):
        if status == "normal":
            self.status_label.setText("GOOD")
            self.status_label.setStyleSheet("color: #28A745;") # Green
            # 바른 자세일 때 파란 테두리 효과 (영상 컨테이너)
            self.video_label.parent().setStyleSheet("background: black; border-radius: 15px; border: 3px solid #0078D7;")
        elif status == "abnormal":
            self.status_label.setText("BAD")
            self.status_label.setStyleSheet("color: #dc3545;") # Red
            self.video_label.parent().setStyleSheet("background: black; border-radius: 15px; border: 3px solid #dc3545;")
        else:
            self.status_label.setText(status)
            self.video_label.parent().setStyleSheet("background: black; border-radius: 15px;")

    def update_timers(self, total_sec, correct_sec):
        # 1. 텍스트 업데이트
        self.lbl_total_time.setText(format_time(total_sec))
        self.lbl_good_time.setText(format_time(correct_sec))
        
        # 2. 프로그레스 바 및 점수 계산
        if total_sec > 0:
            ratio = int((correct_sec / total_sec) * 100)
            self.progress_bar.setValue(ratio)
            
            # 현재 점수 (비율 기반)
            self.score_label.setText(f"Score: {ratio}점")
            
            # 점수에 따라 게이지 색상 변경
            if ratio >= 80:
                self.progress_bar.setStyleSheet(self.progress_bar.styleSheet() + "QProgressBar::chunk { background-color: #28A745; }")
            elif ratio >= 50:
                self.progress_bar.setStyleSheet(self.progress_bar.styleSheet() + "QProgressBar::chunk { background-color: #FFC107; }")
            else:
                self.progress_bar.setStyleSheet(self.progress_bar.styleSheet() + "QProgressBar::chunk { background-color: #dc3545; }")

    def reset_ui(self):
        self.video_label.clear()
        self.video_label.setText("Camera OFF")
        self.status_label.setText("Ready")
        self.status_label.setStyleSheet("color: #aaa;")
        self.video_label.parent().setStyleSheet("background: black; border-radius: 15px;") # 테두리 제거
        
        self.lbl_total_time.setText("00:00")
        self.lbl_good_time.setText("00:00")
        self.progress_bar.setValue(0)
        self.score_label.setText("Score: 0")
        
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)