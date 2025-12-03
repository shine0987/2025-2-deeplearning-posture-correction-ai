from pathlib import Path

# UI 탭 임포트
from app_ui.tabs.monitor_tab import MonitorTab
from app_ui.tabs.ranking_tab import RankingTab
from app_ui.tabs.profile_tab import ProfileTab
from app_ui.tabs.tutorial_tab import TutorialTab
from app_ui.tabs.friend_tab import FriendTab

# 스레드 및 데이터 관리 임포트
from app_ui.monitor_thread import MonitorThread
import app_ui.data_manager as data_manager # 데이터 매니저 연동

from PyQt6.QtWidgets import QMainWindow, QTabWidget
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Posture Corrector AI")
        self.setGeometry(100, 100, 950, 750)
        
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
        
        # [핵심] 앱 시작 시 데이터 매니저에서 정보 가져오기
        self.update_profile_to_monitor()

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #F4F6F9; }
            QTabWidget::pane {
                border: 1px solid #E1E4E8;
                background: white;
                border-radius: 10px;
                margin: 15px;
            }
            QTabBar::tab {
                background: #FFFFFF;
                color: #6c757d;
                border: 1px solid transparent;
                padding: 12px 25px;
                margin-right: 10px;
                margin-left: 15px;
                border-bottom: 3px solid transparent;
                font-family: 'Malgun Gothic';
                font-size: 11pt;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                color: #0078D7;
                border-bottom: 3px solid #0078D7;
                background: #F4F6F9;
            }
            QTabBar::tab:hover:!selected {
                color: #005a9e;
                background: #f8f9fa;
            }
        """)

    def init_tabs(self):
        self.monitor_tab = MonitorTab()
        self.ranking_tab = RankingTab()
        self.profile_tab = ProfileTab()
        self.friend_tab = FriendTab()
        self.tutorial_tab = TutorialTab()
        
        self.tabs.addTab(self.monitor_tab, "📷 측정")
        self.tabs.addTab(self.ranking_tab, "🏆 랭킹")
        self.tabs.addTab(self.friend_tab, "👫 친구")
        self.tabs.addTab(self.profile_tab, "👤 프로필")
        self.tabs.addTab(self.tutorial_tab, "💡 가이드")
        
        self.tabs.tabBar().setCursor(Qt.CursorShape.PointingHandCursor)

    def connect_signals(self):
        # 1. 버튼 -> 메인 메서드
        self.monitor_tab.start_button.clicked.connect(self.start_monitoring)
        self.monitor_tab.stop_button.clicked.connect(self.stop_monitoring)
        
        # 2. 스레드 데이터 -> 탭 UI 업데이트
        self.monitor_thread.frame_ready.connect(self.monitor_tab.update_frame)
        self.monitor_thread.posture_status.connect(self.monitor_tab.update_posture_status)
        self.monitor_thread.timer_updated.connect(self.monitor_tab.update_timers)
        self.monitor_thread.timer_updated.connect(self.update_session_data)
        
        # 3. [핵심 추가] 로딩 완료 시그널 연결
        self.monitor_thread.load_finished.connect(self.monitor_tab.on_load_finished)
    
    def update_profile_to_monitor(self):
        """data_manager와 연동하여 현재 프로필 정보를 모니터 탭에 반영"""
        # 1. 데이터 매니저에서 현재 로그인된 프로필 로드
        profile = data_manager.load_profile()
        
        # 2. 닉네임 가져오기 (없으면 'Guest' 혹은 ID 표시)
        # data_manager의 CURRENT_USER_ID가 설정되어 있어야 함
        user_name = profile.get("nickname", "Guest")
        
        # 3. 모니터 탭 UI 업데이트
        self.monitor_tab.set_user_name(user_name)

    def start_monitoring(self):
        print("메인: 모니터링 시작")
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

        # 세션 저장 및 랭킹 갱신 (data_manager 활용)
        if self.current_session_data["total"] > 0:
            data_manager.add_ranking_entry(self.current_session_data)
            print("메인: 세션 저장 완료")
            self.ranking_tab.load_ranking()
        
        self.current_session_data = {"total": 0, "correct": 0}

    def update_session_data(self, total_sec, correct_sec):
        self.current_session_data = {"total": total_sec, "correct": correct_sec}

    def closeEvent(self, event):
        if self.monitor_thread.isRunning():
            self.monitor_thread.stop()
            self.monitor_thread.wait()
        event.accept()