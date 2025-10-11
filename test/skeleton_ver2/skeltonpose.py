import cv2
import mediapipe as mp
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Optional, Tuple, List


def safe_imread(path: Path) -> Optional[np.ndarray]:
    """Read image safely, supporting non-ASCII/Windows paths.

    Uses numpy.fromfile + cv2.imdecode to avoid cv2.imread path issues on Windows.
    """
    try:
        data = np.fromfile(str(path), dtype=np.uint8)
        if data.size == 0:
            return None
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)
        return img
    except Exception:
        return None


def safe_imwrite(path: Path, img: np.ndarray) -> bool:
    """Write image using cv2.imencode + tofile to avoid cv2.imwrite issues."""
    try:
        ext = Path(path).suffix
        if ext == '':
            ext = '.jpg'
        if not ext.startswith('.'):
            ext = '.' + ext
        result, buf = cv2.imencode(ext, img)
        if not result:
            return False
        buf.tofile(str(path))
        return True
    except Exception:
        return False


# basic logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)


def angle_deg(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """Return angle in degrees from point a to b (atan2 dy,dx)."""
    dy = b[1] - a[1]
    dx = b[0] - a[0]
    return float(np.degrees(np.arctan2(dy, dx)))

# Mediapipe 초기화
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# 상수 정의: 상체 랜드마크 인덱스 (Mediapipe Pose Landmarks 기준)
UPPER_BODY_LANDMARKS = [
    0,   # nose
    11,  # left_shoulder
    12,  # right_shoulder
    23,  # left_hip
    24   # right_hip
]

def calculate_neck_angle(nose, shoulder_center):
    """목 기울기 각도를 계산합니다.

    반환값: 도 단위, 0에 가까울수록 수직에 가깝습니다.
    """
    dy = nose[1] - shoulder_center[1]
    dx = nose[0] - shoulder_center[0]
    # 어깨중앙->코 벡터와 수직(화면 위쪽 방향)을 비교하는 방식으로 각도 계산
    angle_rad = np.arctan2(dx, dy)  # dx,dy 순서를 바꿔 수직 기준 각도 산출
    return np.degrees(angle_rad)


def classify_posture(landmarks):
    """이전 버전 호환용 더미 함수 — 분류는 더 이상 수행하지 않습니다.
    반환: 빈 dict
    """
    return {}


def get_upper_body_connections():
    """Mediapipe의 전체 연결 중 상체(목/어깨/허리)만 남긴 연결 리스트를 반환합니다."""
    upper_set = set(UPPER_BODY_LANDMARKS)
    # mp_pose.POSE_CONNECTIONS은 Landmark enum pair들의 집합
    return [c for c in mp_pose.POSE_CONNECTIONS if c[0] in upper_set and c[1] in upper_set]


def process_images_in_folder(input_folder, output_csv="skeleton_coords.csv", overwrite=True, backup_folder=None, processed_folder=None, csv_folder=None):
    input_folder = Path(input_folder)
    if not input_folder.exists():
        raise FileNotFoundError(f"입력 폴더를 찾을 수 없습니다: {input_folder}")

    image_paths = list(input_folder.glob("*.jpg")) + list(input_folder.glob("*.png")) + list(input_folder.glob("*.jpeg"))
    if not image_paths:
        logging.warning("이미지 파일을 찾지 못했습니다. 폴더에 .jpg/.png/.jpeg 파일이 있는지 확인하세요.")
        return

    if backup_folder:
        Path(backup_folder).mkdir(parents=True, exist_ok=True)
    if processed_folder:
        Path(processed_folder).mkdir(parents=True, exist_ok=True)
    if csv_folder:
        Path(csv_folder).mkdir(parents=True, exist_ok=True)

    results = []
    angles_list = []
    upper_connections = get_upper_body_connections()
    # 전체 연결도 따로 보관 — 이미지는 전체 스켈레톤을 그리기 위해 사용
    full_connections = list(mp_pose.POSE_CONNECTIONS)

    # helper functions are defined at module level

    with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
        for p in image_paths:
            img = safe_imread(p)
            if img is None:
                logging.warning(f"이미지 로드 실패: {p}")
                continue

            h, w = img.shape[:2]
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            res = pose.process(img_rgb)
            if not res.pose_landmarks:
                logging.info(f"랜드마크 미검출: {p.name}")
                continue

            landmarks = [(lm.x, lm.y) for lm in res.pose_landmarks.landmark]
            # 분류 단계 제거: posture 정보는 더 이상 저장하지 않음
            info = {}

            # CSV용 레코드: 목, 좌/우 어깨, 좌/우 엉덩이 좌표(정규화 및 픽셀)
            rec = {"image_path": str(p.name)}
            for i in UPPER_BODY_LANDMARKS:
                x_norm = float(landmarks[i][0])
                y_norm = float(landmarks[i][1])
                rec[f"lm_{i}_x"] = x_norm
                rec[f"lm_{i}_y"] = y_norm
                rec[f"lm_{i}_x_px"] = int(x_norm * w)
                rec[f"lm_{i}_y_px"] = int(y_norm * h)

            results.append(rec)

            # 각도 정보 수집 (별도 CSV 저장용)
            try:
                left_sh = landmarks[11]
                right_sh = landmarks[12]
                left_hp = landmarks[23]
                right_hp = landmarks[24]
                nose = landmarks[0]

                # neck angle: using calculate_neck_angle (already returns degrees)
                neck_angle = float(calculate_neck_angle(nose, ((left_sh[0]+right_sh[0])/2.0, (left_sh[1]+right_sh[1])/2.0)))

                # shoulder angle (left->right)
                def angle_deg(a, b):
                    dy = b[1] - a[1]
                    dx = b[0] - a[0]
                    return float(np.degrees(np.arctan2(dy, dx)))

                shoulder_angle = angle_deg(left_sh, right_sh)
                hip_angle = angle_deg(left_hp, right_hp)
            except Exception:
                neck_angle = None
                shoulder_angle = None
                hip_angle = None

            angles_list.append({
                'image_path': str(p.name),
                'neck_angle': neck_angle,
                'shoulder_angle_deg': shoulder_angle,
                'hip_angle_deg': hip_angle
            })

            # 시각화: 원본 이미지에 상체 스켈레톤만 그리기
            annotated = img.copy()

            # 점과 연결선 그리기
            # 랜드마크 좌표 -> 픽셀 좌표
            for i in UPPER_BODY_LANDMARKS:
                x_px = int(landmarks[i][0] * w)
                y_px = int(landmarks[i][1] * h)
                # 분류가 제거되어 기본 색(초록)으로 표시
                cv2.circle(annotated, (x_px, y_px), 4, (0, 255, 0), -1)

            # 연결선 그리기 (전체 스켈레톤)
            for a, b in full_connections:
                # 일부 랜드마크는 존재하지 않을 수 있으므로 안전하게 접근
                try:
                    ax, ay = int(landmarks[a][0] * w), int(landmarks[a][1] * h)
                    bx, by = int(landmarks[b][0] * w), int(landmarks[b][1] * h)
                except Exception:
                    continue
                cv2.line(annotated, (ax, ay), (bx, by), (0, 255, 0), 2)

            # 분류를 제거했으므로 텍스트는 표시하지 않거나 기본 텍스트를 사용할 수 있습니다.
            # 여기서는 간단히 'Skeleton' 텍스트(초록)를 표시합니다.
            cv2.putText(annotated, 'Skeleton', (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,255,0), 2)

            # 저장: 백업(선택), 그리고 처리된(annotated) 이미지는 processed_folder로 보내거나
            # overwrite 옵션에 따라 원본을 덮어쓰거나 _skeleton.jpg로 저장
            if backup_folder:
                backup_path = Path(backup_folder) / p.name
                safe_imwrite(backup_path, img)  # 원본 백업

            if processed_folder:
                save_path = str(Path(processed_folder) / p.name)
            else:
                if overwrite:
                    save_path = str(p)
                else:
                    save_path = str(p.with_name(p.stem + "_skeleton.jpg"))

            ok = safe_imwrite(save_path, annotated)
            if not ok:
                logging.error(f"이미지 저장 실패: {save_path}")
            else:
                logging.info(f"처리완료: {p.name} -> {save_path}")

    # CSV 저장
    df = pd.DataFrame(results)
    # if csv_folder provided, write CSVs there
    if csv_folder:
        coords_path = Path(csv_folder) / Path(output_csv).name
    else:
        coords_path = Path(output_csv)
    df.to_csv(str(coords_path), index=False, encoding='utf-8-sig')
    logging.info(f"결과 CSV 저장: {coords_path}")

    # 각도 정보 별도 저장 및 요약 (posture 컬럼 없음)
    angles_df = pd.DataFrame(angles_list)
    if csv_folder:
        angles_csv = Path(csv_folder) / 'skeleton_angles.csv'
    else:
        angles_csv = Path(output_csv).with_name('skeleton_angles.csv')
    angles_df.to_csv(str(angles_csv), index=False, encoding='utf-8-sig')
    logging.info(f"각도 CSV 저장: {angles_csv}")

    # 요약 통계(평균, 분산)
    summary = {}
    numeric_cols = ['neck_angle', 'shoulder_angle_deg', 'hip_angle_deg']
    for c in numeric_cols:
        if c in angles_df.columns:
            col = pd.to_numeric(angles_df[c], errors='coerce')
            summary[f"{c}_mean"] = float(col.mean()) if not col.dropna().empty else None
            summary[f"{c}_var"] = float(col.var(ddof=0)) if not col.dropna().empty else None
        else:
            summary[f"{c}_mean"] = None
            summary[f"{c}_var"] = None


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='이미지 폴더의 상체 스켈레톤 생성 및 자세 판별')
    parser.add_argument('--input_folder', default='labeling_test_images', help='이미지 폴더 경로 (기본: labeling_test_images)')
    parser.add_argument('--result', default='skeleton_coords.csv', help='결과 CSV 파일명')
    parser.add_argument('--no_overwrite', action='store_true', help='원본을 덮어쓰지 않고 _skeleton.jpg로 저장')
    parser.add_argument('--backup', default=None, help='원본을 백업할 폴더 경로 (선택)')
    parser.add_argument('--processed_folder', default='processed_images', help='처리된(annotated) 이미지를 모을 폴더 경로 (기본: processed_images)')
    parser.add_argument('--csv_folder', default='csv_results', help='결과 CSV를 모을 폴더 경로 (기본: csv_results)')
    # 분류/자동 임계값 옵션 제거 — 현재는 좌표/각도 추출만 수행합니다.
    args = parser.parse_args()

    try:
        process_images_in_folder(args.input_folder, output_csv=args.result, overwrite=not args.no_overwrite, backup_folder=args.backup, processed_folder=args.processed_folder, csv_folder=args.csv_folder)
    except Exception:
        logging.exception('오류 발생')
