from pathlib import Path

# UI 탭 임포트
from app_ui.tabs.monitor_tab import MonitorTab
from app_ui.tabs.ranking_tab import RankingTab
from app_ui.tabs.profile_tab import ProfileTab
from app_ui.tabs.tutorial_tab import TutorialTab
from app_ui.tabs.friend_tab import FriendTab

# 스레드 및 데이터 관리 임포트
from app_ui.monitor_thread import MonitorThread
import app_ui.data_manager as data_manager

from PyQt6.QtWidgets import QMainWindow, QTabWidget, QLabel, QHBoxLayout, QWidget
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Posture Corrector AI") # 조금 더 심플한 영문 타이틀
        self.setGeometry(100, 100, 950, 750) # 여백을 위해 사이즈 약간 증대
        
        # [Design] 전체 앱 스타일시트 적용 (심플 & 오피스 블루 테마)
        self.apply_stylesheet()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # 모니터링 스레드 초기화
        self.monitor_thread = MonitorThread()
        self.current_session_data = {"total": 0, "correct": 0}
        
        # 탭 생성 및 추가
        self.init_tabs()
        
        # 시그널 연결
        self.connect_signals()

    def apply_stylesheet(self):
        """앱 전체 디자인 스타일 정의"""
        self.setStyleSheet("""
            /* 전체 배경: 눈이 편안한 밝은 회색 */
            QMainWindow {
                background-color: #F4F6F9;
            }
            
            /* 탭 위젯 컨테이너 */
            QTabWidget::pane {
                border: 1px solid #E1E4E8;
                background: white;
                border-radius: 10px; /* 둥근 모서리 */
                margin: 15px; /* 외곽 여백 */
                /* 그림자 효과는 코드 레벨에서 추가 가능하나, 여기선 깔끔함을 위해 제외 */
            }

            /* 탭 바 (상단 버튼 영역) */
            QTabBar::tab {
                background: #FFFFFF;
                color: #6c757d; /* 비활성 텍스트 회색 */
                border: 1px solid transparent;
                padding: 12px 25px;
                margin-right: 10px;
                margin-left: 15px;
                border-bottom: 3px solid transparent; /* 하단 밑줄 준비 */
                font-family: 'Malgun Gothic';
                font-size: 11pt;
                font-weight: bold;
            }

            /* 탭 선택되었을 때 (오피스 블루 포인트) */
            QTabBar::tab:selected {
                color: #0078D7; /* 파란색 텍스트 */
                border-bottom: 3px solid #0078D7; /* 파란색 밑줄 */
                background: #F4F6F9; /* 배경과 자연스럽게 연결 */
            }

            /* 탭 마우스 오버 */
            QTabBar::tab:hover:!selected {
                color: #005a9e;
                background: #f8f9fa;
            }
        """)

    def init_tabs(self):
        # 각 탭 위젯 생성
        self.monitor_tab = MonitorTab()
        self.ranking_tab = RankingTab()
        self.profile_tab = ProfileTab()
        self.friend_tab = FriendTab()
        self.tutorial_tab = TutorialTab()
        
        # QTabWidget에 탭 추가 (아이콘은 나중에 추가 가능)
        self.tabs.addTab(self.monitor_tab, "📷 측정")
        self.tabs.addTab(self.ranking_tab, "🏆 랭킹")
        self.tabs.addTab(self.friend_tab, "👫 친구")
        self.tabs.addTab(self.profile_tab, "👤 프로필")
        self.tabs.addTab(self.tutorial_tab, "💡 가이드")
        
        # 탭 폰트 강제 설정 (스타일시트 외)
        self.tabs.tabBar().setCursor(Qt.CursorShape.PointingHandCursor)

    def connect_signals(self):
        # 1. 모니터 탭의 버튼 -> 메인 윈도우의 스레드 제어 함수
        self.monitor_tab.start_button.clicked.connect(self.start_monitoring)
        self.monitor_tab.stop_button.clicked.connect(self.stop_monitoring)
        
        # 2. 스레드 시그널 -> UI 업데이트
        self.monitor_thread.frame_ready.connect(self.monitor_tab.update_frame)
        self.monitor_thread.posture_status.connect(self.monitor_tab.update_posture_status)
        self.monitor_thread.timer_updated.connect(self.monitor_tab.update_timers)
        self.monitor_thread.timer_updated.connect(self.update_session_data)

    # --- 기능 로직 (기존과 동일) ---

    def start_monitoring(self):
        print("메인: 모니터링 시작 요청")
        self.monitor_tab.set_loading_state()
        
        if not self.monitor_thread.isRunning():
            self.monitor_thread.start()

    def stop_monitoring(self):
        print("메인: 모니터링 중지")
        if self.monitor_thread.isRunning():
            self.monitor_thread.stop()
        
        self.monitor_tab.start_button.setEnabled(True)
        self.monitor_tab.stop_button.setEnabled(False)
        self.monitor_tab.reset_ui()

        # 세션 저장 및 랭킹 갱신
        if self.current_session_data["total"] > 0:
            data_manager.add_ranking_entry(self.current_session_data)
            print("메인: 세션 저장 완료")
            self.ranking_tab.load_ranking()
        
        self.current_session_data = {"total": 0, "correct": 0}

    def update_session_data(self, total_sec, correct_sec):
        self.current_session_data = {"total": total_sec, "correct": correct_sec}

    def closeEvent(self, event):
        print("애플리케이션 종료 중...")
        if self.monitor_thread.isRunning():
            self.monitor_thread.stop()
            self.monitor_thread.wait()
        event.accept()