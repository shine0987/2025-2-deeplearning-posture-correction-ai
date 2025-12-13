import cv2
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFrame, QProgressBar, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QFont
from app_ui.data_manager import format_time

class MonitorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_user_name = "사용자" # 초기값 (main_window에서 덮어씌움)
        self.init_ui()

    def init_ui(self):
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
        self.video_label.setScaledContents(True) 
        
        cam_layout.addWidget(self.video_label)
        main_layout.addWidget(cam_container, stretch=2)

        # --- [RIGHT] 대시보드 영역 ---
        dashboard_layout = QVBoxLayout()
        dashboard_layout.setSpacing(15)

        # 0. 프로필 섹션
        # create_card로부터 layout 객체를 직접 받습니다.
        self.profile_card, profile_layout = self.create_card("사용자 정보")
        
        profile_inner_layout = QHBoxLayout()
        icon_label = QLabel("👤")
        icon_label.setFont(QFont("Segoe UI Emoji", 20))
        
        self.user_name_label = QLabel(f"{self.current_user_name}님")
        self.user_name_label.setFont(QFont("Malgun Gothic", 14, QFont.Weight.Bold))
        
        profile_inner_layout.addWidget(icon_label)
        profile_inner_layout.addWidget(self.user_name_label)
        profile_inner_layout.addStretch()
        
        profile_layout.addLayout(profile_inner_layout)
        dashboard_layout.addWidget(self.profile_card)

        # 1. 바른 자세 유지율 (Score Board)
        self.score_card, score_layout = self.create_card("바른 자세 유지율")
        
        self.rate_label = QLabel("0%")
        self.rate_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rate_label.setFont(QFont("Malgun Gothic", 36, QFont.Weight.Bold))
        self.rate_label.setStyleSheet("color: #aaa;")
        
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Malgun Gothic", 14))
        self.status_label.setStyleSheet("color: #777; margin-bottom: 10px;")

        score_layout.addWidget(self.rate_label)
        score_layout.addWidget(self.status_label)
        dashboard_layout.addWidget(self.score_card)

        # 2. 실시간 리포트 (게이지 & 타이머)
        self.report_card, report_layout = self.create_card("실시간 리포트")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(self.get_progress_style("#e0e0e0"))
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setTextVisible(False)
        report_layout.addWidget(self.progress_bar)
        
        time_layout = QGridLayout()
        time_layout.setContentsMargins(0, 10, 0, 0)
        
        lbl_total = QLabel("총 시간")
        self.lbl_total_time = QLabel("00:00")
        self.lbl_total_time.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_total_time.setStyleSheet("font-family: monospace; font-size: 14px; font-weight: bold;")
        
        lbl_good = QLabel("바른 시간")
        self.lbl_good_time = QLabel("00:00")
        self.lbl_good_time.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_good_time.setStyleSheet("font-family: monospace; font-size: 14px; font-weight: bold; color: #28A745;")
        
        time_layout.addWidget(lbl_total, 0, 0)
        time_layout.addWidget(self.lbl_total_time, 0, 1)
        time_layout.addWidget(lbl_good, 1, 0)
        time_layout.addWidget(self.lbl_good_time, 1, 1)
        
        report_layout.addLayout(time_layout)
        dashboard_layout.addWidget(self.report_card)

        # 3. 컨트롤 버튼
        dashboard_layout.addStretch()
        
        btn_layout = QHBoxLayout()
        self.start_button = QPushButton("측정 시작")
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_button.setFixedHeight(50)
        self.start_button.setStyleSheet("""
            QPushButton { background-color: #0078D7; color: white; border-radius: 10px; font-size: 16px; font-weight: bold; }
            QPushButton:hover { background-color: #0063b1; }
        """)
        
        self.stop_button = QPushButton("종료")
        self.stop_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_button.setFixedHeight(50)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton { background-color: #dc3545; color: white; border-radius: 10px; font-size: 16px; font-weight: bold; }
            QPushButton:disabled { background-color: #e0e0e0; color: #aaa; }
            QPushButton:hover:!disabled { background-color: #c82333; }
        """)
        
        btn_layout.addWidget(self.start_button)
        btn_layout.addWidget(self.stop_button)
        dashboard_layout.addLayout(btn_layout)
        
        main_layout.addLayout(dashboard_layout, stretch=1)

    def create_card(self, title_text):
        """카드 스타일 프레임 생성 (frame과 layout을 동시에 리턴)"""
        frame = QFrame()
        frame.setStyleSheet("background: white; border-radius: 10px; border: 1px solid #e0e0e0;")
        
        layout = QVBoxLayout(frame) # 이 레이아웃에 위젯을 추가해야 보입니다.
        
        title = QLabel(title_text)
        title.setFont(QFont("Malgun Gothic", 11, QFont.Weight.Bold))
        title.setStyleSheet("color: #555; border: none; padding-bottom: 5px; border-bottom: 1px solid #eee;")
        layout.addWidget(title)
        
        return frame, layout

    def get_progress_style(self, color_hex):
        return f"""
            QProgressBar {{
                border: 1px solid #ddd;
                border-radius: 10px;
                background-color: #f5f5f5;
            }}
            QProgressBar::chunk {{
                background-color: {color_hex};
                border-radius: 9px; 
            }}
        """

    def set_user_name(self, name):
        """외부에서 사용자 이름을 변경할 때 호출"""
        self.current_user_name = name
        self.user_name_label.setText(f"{name}님")

    def set_loading_state(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        
        # 화면에 안내 문구 표시
        self.video_label.setText("AI 엔진 초기화 중...\n잠시만 기다려주세요 (약 8초)")
        self.video_label.setStyleSheet("color: #FFC107; font-size: 16px; font-weight: bold;")
        
        self.status_label.setText("Loading...")

    def on_load_finished(self):
        """모델 로딩 완료 시 호출: UI 활성화"""
        print("UI: 로딩 완료됨. 측정 화면으로 전환.")
        self.video_label.setText("")
        self.stop_button.setEnabled(True) # 종료 버튼 활성화
        self.status_label.setText("측정 중...")

    def update_frame(self, frame):
        # 영상이 들어오면 표시
        try:
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(self.video_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.video_label.setPixmap(scaled_pixmap)
        except Exception:
            pass

    def update_posture_status(self, status):
        if status == "normal":
            self.status_label.setText("바른 자세입니다")
            self.status_label.setStyleSheet("color: #28A745; font-weight: bold;")
            self.video_label.parent().setStyleSheet("background: black; border-radius: 15px; border: 3px solid #28A745;")
        elif status == "abnormal":
            self.status_label.setText("자세가 흐트러졌어요!")
            self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            self.video_label.parent().setStyleSheet("background: black; border-radius: 15px; border: 3px solid #dc3545;")
        else:
            self.status_label.setText(status)
            self.video_label.parent().setStyleSheet("background: black; border-radius: 15px;")

    def update_timers(self, total_sec, correct_sec):
        self.lbl_total_time.setText(format_time(total_sec))
        self.lbl_good_time.setText(format_time(correct_sec))
        
        ratio = 0
        if total_sec > 0:
            ratio = int((correct_sec / total_sec) * 100)
            
        self.rate_label.setText(f"{ratio}%")
        self.progress_bar.setValue(ratio)
        
        if ratio >= 80:
            color = "#28A745"
        elif ratio >= 50:
            color = "#FFC107"
        else:
            color = "#dc3545"
            
        self.rate_label.setStyleSheet(f"color: {color};")
        self.progress_bar.setStyleSheet(self.get_progress_style(color))

    def reset_ui(self):
        self.video_label.clear()
        self.video_label.setText("Camera OFF")
        self.status_label.setText("Ready")
        self.status_label.setStyleSheet("color: #aaa;")
        self.video_label.parent().setStyleSheet("background: black; border-radius: 15px;")
        
        self.lbl_total_time.setText("00:00")
        self.lbl_good_time.setText("00:00")
        self.rate_label.setText("0%")
        self.rate_label.setStyleSheet("color: #aaa;")
        
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(self.get_progress_style("#e0e0e0"))
        
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)