import os
import json
from datetime import datetime

# 파일 경로는 main.py에서 os.chdir()로 설정한 루트 폴더 기준입니다.
DATA_DIR = "data"
PROFILE_FILE = os.path.join(DATA_DIR, "posture_profile.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
RANKING_FILE = os.path.join(DATA_DIR, "posture_ranking.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

# 현재 로그인한 사용자 ID (전역 변수처럼 사용)
CURRENT_USER_ID = None

# --- [NEW] 사용자 관리 (로그인/회원가입) ---

def load_all_users():
    """모든 사용자 정보 로드 (DB 역할)"""
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_all_users(data):
    """모든 사용자 정보 저장"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def register_user(user_id, password):
    """회원가입: 성공 시 True 반환"""
    users = load_all_users()
    if user_id in users:
        return False # 이미 존재하는 ID
    
    # 새 유저 초기 데이터
    users[user_id] = {
        "password": password,
        "profile": { # 기본 프로필
            "nickname": user_id,
            "height": "",
            "weight": "",
            "avatar": "기본 아바타 (👤)"
        }
    }
    save_all_users(users)
    return True

def login_user(user_id, password):
    """로그인: 성공 시 True 반환 및 전역 변수 설정"""
    global CURRENT_USER_ID
    users = load_all_users()
    
    if user_id in users and users[user_id]["password"] == password:
        CURRENT_USER_ID = user_id
        return True
    return False

# --- [NEW] 앱 설정 관리 (자동 로그인, 아이디 저장) ---

def load_config():
    """설정 파일 로드 (없으면 기본값 반환)"""
    default_config = {
        "saved_id": "",
        "is_remember_id": False,
        "is_auto_login": False
    }
    
    if not os.path.exists(CONFIG_FILE):
        return default_config
        
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default_config

def save_config(saved_id, is_remember_id, is_auto_login):
    """설정 파일 저장"""
    config = {
        "saved_id": saved_id if (is_remember_id or is_auto_login) else "",
        "is_remember_id": is_remember_id,
        "is_auto_login": is_auto_login
    }
    
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def set_current_user(user_id):
    """전역 변수에 현재 유저 설정 (로그인 처리)"""
    global CURRENT_USER_ID
    CURRENT_USER_ID = user_id

def format_time(seconds):
    """초를 HH:MM:SS 형식의 문자열로 변환"""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:02}"

# --- 프로필 관리 ---

def load_profile():
    """현재 로그인된 사용자의 프로필 반환"""
    global CURRENT_USER_ID
    if CURRENT_USER_ID is None:
        return {} # 로그인 안됨
    
    users = load_all_users()
    # 유저 정보가 있으면 profile 리턴, 없으면 빈 딕셔너리
    return users.get(CURRENT_USER_ID, {}).get("profile", {})

def save_profile(profile_data):
    """현재 로그인된 사용자의 프로필 저장"""
    global CURRENT_USER_ID
    if CURRENT_USER_ID is None:
        print("오류: 로그인된 사용자가 없습니다.")
        return

    users = load_all_users()
    if CURRENT_USER_ID in users:
        users[CURRENT_USER_ID]["profile"] = profile_data
        save_all_users(users)
    else:
        print("오류: 사용자 정보를 찾을 수 없습니다.")


# --- 랭킹 관리 ---

def load_ranking():
    """랭킹 파일에서 데이터 읽기 및 퍼센트 기준 내림차순 정렬"""
    if not os.path.exists(RANKING_FILE):
        return [] # 파일이 없으면 빈 리스트
    
    try:
        with open(RANKING_FILE, 'r', encoding='utf-8') as f:
            records = json.load(f)
        
        # [핵심 수정] 바른 자세 퍼센트(posture_percent) 기준으로 내림차순 정렬
        # 기존 데이터에 'posture_percent' 키가 없을 경우를 대비해 0으로 처리하는 로직 포함
        records.sort(key=lambda x: x.get("posture_percent", 0), reverse=True)
        
        return records
    except Exception as e:
        print(f"랭킹 로드 오류: {e}")
        return []

# data_manager.py 내부

def add_ranking_entry(session_data):
    """세션 데이터를 랭킹에 저장 (사용자 정보 포함)"""
    if session_data["total"] == 0:
        return

    percent = (session_data["correct"] / session_data["total"]) * 100

    # [핵심] 현재 로그인된 프로필 정보 가져오기
    profile = load_profile() 
    
    new_record = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_time": session_data["total"],
        "correct_time": session_data["correct"],
        "posture_percent": round(percent, 1),
        
        # [NEW] 랭킹 박제 시점의 닉네임과 아바타 저장
        "nickname": profile.get("nickname", "Guest"),
        "avatar": profile.get("avatar", "👤")
    }
    
    records = load_ranking()
    records.append(new_record)
    
    # ... (이하 저장 로직 동일) ...
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(RANKING_FILE, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=4)
        print(f"세션 기록 저장 완료: {RANKING_FILE}")
    except Exception as e:
        print(f"세션 기록 저장 오류: {e}")