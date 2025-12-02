from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFrame, QFormLayout
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QImage, QFont, QColor

# data_manager에서 format_time, load_profile 함수 임포트
from app_ui.data_manager import format_time, load_profile

class MonitorTab(QWidget):
    """
    자세 측정 탭 UI
    """
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        
        # 좌측: 비디오 피드 및 컨트롤
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)
        
        # --- [수정] 비디오 라벨 스타일 강화 ---
        self.video_label = QLabel("웹캠 피드를 여기에 표시합니다.")
        self.video_label.setObjectName("VideoLabel") 
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setFixedSize(640, 480)
        # 기본 배경색 지정 (로딩 텍스트가 잘 보이게)
        self.video_label.setStyleSheet("background-color: #000; color: #fff; font-size: 16px;")
        
        left_layout.addWidget(self.video_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        control_layout = QHBoxLayout()
        self.start_button = QPushButton("시작 (Start)") # 시작 버튼
        
        self.stop_button = QPushButton("종료 (Stop)") # 종료 버튼
        self.stop_button.setEnabled(False)
        
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        left_layout.addLayout(control_layout)
        
        main_layout.addLayout(left_layout, 2) # 좌측 영역이 2의 비율
        
        # 우측: 프로필, 상태 및 정보
        right_layout = QVBoxLayout()
        right_layout.setSpacing(20)
        right_layout.setContentsMargins(10, 0, 10, 0)
        
        # --- [NEW] 프로필 프레임 (우측 상단) ---
        profile_frame = QFrame()
        profile_frame.setFrameShape(QFrame.Shape.StyledPanel)
        profile_frame.setStyleSheet("background-color: #e5e5e5; border-radius: 5px;")
        profile_layout = QFormLayout(profile_frame)
        profile_layout.setSpacing(10)
        
        profile_title = QLabel("사용자 프로필")
        profile_title.setFont(QFont("Malgun Gothic", 14, QFont.Weight.Bold))
        profile_layout.addRow(profile_title)
        
        # --- [NEW] 프로필 프레임 (우측 상단) ---
        profile_frame = QFrame()
        profile_frame.setFrameShape(QFrame.Shape.StyledPanel)
        profile_frame.setStyleSheet("background-color: #e5e5e5; border-radius: 5px;")
        profile_layout = QFormLayout(profile_frame)
        profile_layout.setSpacing(10)
        
        profile_title = QLabel("사용자 프로필")
        profile_title.setFont(QFont("Malgun Gothic", 14, QFont.Weight.Bold))
        profile_layout.addRow(profile_title)
        
        # 1. 프로필 데이터 로드 (json 파일에서 읽기)
        profile_data = load_profile()
        
        # 2. 데이터 추출 (저장된 키: nickname, height, weight, avatar)
        # 데이터가 없을 경우 기본값(Default)을 설정합니다.
        user_nickname = profile_data.get("nickname", "게스트")
        user_height = profile_data.get("height", "-")
        user_weight = profile_data.get("weight", "-")
        user_avatar = profile_data.get("avatar", "👤") # 아바타 텍스트

        # 아바타에서 이모지만 추출 
        # 괄호가 있다면 괄호 안의 내용만, 없다면 전체 표시
        if "(" in user_avatar and ")" in user_avatar:
            emoji = user_avatar.split("(")[1].split(")")[0]
        else:
            # "기본 아바타 (A)" 같은 경우 처리 혹은 단순화
            emoji = "👤" if "기본" in user_avatar else user_avatar

        # 3. UI 라벨 생성
        # 이름 라벨 (아바타 이모지 + 닉네임)
        name_display = f"{emoji} {user_nickname}"
        name_label = QLabel(name_display)
        name_label.setStyleSheet("font-weight: bold; color: #333; font-size: 14px;")
        
        # 신체 정보 라벨 (키 / 몸무게)
        info_display = f"{user_height}cm / {user_weight}kg"
        info_label = QLabel(info_display)
        info_label.setStyleSheet("color: #555;")
        
        # 4. 레이아웃에 추가
        profile_layout.addRow("사용자:", name_label)
        profile_layout.addRow("정보:", info_label)
        
        right_layout.addWidget(profile_frame)
        
        # 상태 프레임
        status_frame = QFrame()
        status_frame.setFrameShape(QFrame.Shape.StyledPanel)
        status_frame.setStyleSheet("background-color: #e5e5e5; border-radius: 5px;")
        status_layout = QVBoxLayout(status_frame)
        status_layout.setSpacing(10)
        
        status_title = QLabel("현재 상태")
        status_title.setObjectName("StatusTitle")
        status_layout.addWidget(status_title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.current_posture_label = QLabel("대기 중...")
        self.current_posture_label.setObjectName("StatusLabel")
        self.current_posture_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.current_posture_label)
        
        right_layout.addWidget(status_frame)
        
        # 타이머 프레임
        timer_frame = QFrame()
        timer_frame.setFrameShape(QFrame.Shape.StyledPanel)
        timer_frame.setStyleSheet("background-color: #e5e5e5; border-radius: 5px;")
        timer_layout = QFormLayout(timer_frame)
        timer_layout.setSpacing(15)
        
        timer_title = QLabel("측정 시간")
        timer_title.setFont(QFont("Malgun Gothic", 14, QFont.Weight.Bold))
        timer_layout.addRow(timer_title)

        self.total_time_label = QLabel("00:00:00")
        self.total_time_label.setObjectName("TimerLabel")
        timer_layout.addRow("총 시간:", self.total_time_label)
        
        self.correct_time_label = QLabel("00:00:00")
        self.correct_time_label.setObjectName("CorrectTimerLabel")
        timer_layout.addRow("바른 자세 시간:", self.correct_time_label)

        right_layout.addWidget(timer_frame)
        
        # 환경 조언 (Placeholder)
        env_frame = QFrame()
        env_frame.setFrameShape(QFrame.Shape.StyledPanel)
        env_frame.setStyleSheet("background-color: #e5e5e5; border-radius: 5px;")
        env_layout = QVBoxLayout(env_frame)
        
        env_title = QLabel("업무 환경 조언 (준비 중)")
        env_title.setFont(QFont("Malgun Gothic", 14, QFont.Weight.Bold))
        env_layout.addWidget(env_title)
        
        self.env_advice_label = QLabel("모니터, 의자, 책상 높이 분석 기능이\n여기에 추가될 예정입니다.")
        self.env_advice_label.setStyleSheet("color: #014ff8;")
        env_layout.addWidget(self.env_advice_label)
        
        right_layout.addWidget(env_frame)

        right_layout.addStretch(1) 
        main_layout.addLayout(right_layout, 1) 

    # --- 기능 메서드 ---

    def set_loading_state(self):
        """[NEW] 모델 로딩 중 UI 표시"""
        self.video_label.clear()
        self.video_label.setText("로딩 중...\n잠시만 기다려주세요.")
        self.video_label.setStyleSheet("""
            background-color: #222; 
            color: #FFD700; 
            font-size: 20px; 
            font-weight: bold;
            border: 2px solid #555;
        """)
        
        self.current_posture_label.setText("초기화 중...")
        self.current_posture_label.setStyleSheet("color: #888;")
        
        # 로딩 중 버튼 비활성화 (중복 클릭 방지)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)

    def update_frame(self, frame):
        """웹캠 프레임을 QLabel에 표시"""
        # 첫 프레임이 들어오면 버튼 상태 변경 (혹은 MainController에서 제어)
        if not self.stop_button.isEnabled():
            self.stop_button.setEnabled(True)
            self.start_button.setEnabled(False)

        try:
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            rgb_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_BGR888).rgbSwapped()
            pixmap = QPixmap.fromImage(rgb_image)
            
            scaled_pixmap = pixmap.scaled(self.video_label.size(), 
                                          Qt.AspectRatioMode.KeepAspectRatio, 
                                          Qt.TransformationMode.SmoothTransformation)
            self.video_label.setPixmap(scaled_pixmap)
            
            # 영상이 나오면 스타일 초기화 (테두리 등 제거)
            self.video_label.setStyleSheet("background-color: black; border: none;")
            
        except Exception as e:
            print(f"프레임 업데이트 오류: {e}")

    def update_posture_status(self, status):
        """자세 상태 텍스트 및 색상 업데이트"""
        if status == "normal":
            self.current_posture_label.setText("바른 자세")
            self.current_posture_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 18px;") 
        elif status == "abnormal":
            self.current_posture_label.setText("나쁜 자세!")
            self.current_posture_label.setStyleSheet("color: #F44336; font-weight: bold; font-size: 18px;") 
        else:
            self.current_posture_label.setText(status)
            self.current_posture_label.setStyleSheet("color: #E0E0E0;") 

    def update_timers(self, total_sec, correct_sec):
        """타이머 라벨 업데이트"""
        self.total_time_label.setText(format_time(total_sec))
        self.correct_time_label.setText(format_time(correct_sec))

    def reset_ui(self):
        """모니터링 종료 시 UI 초기화"""
        self.video_label.clear()
        self.video_label.setText("웹캠 피드를 여기에 표시합니다.")
        self.video_label.setStyleSheet("background-color: #000; color: #fff; font-size: 16px;")
        
        self.current_posture_label.setText("대기 중...")
        self.current_posture_label.setStyleSheet("color: #E0E0E0;")
        
        self.total_time_label.setText("00:00:00")
        self.correct_time_label.setText("00:00:00")
        
        # 버튼 상태 복구
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)