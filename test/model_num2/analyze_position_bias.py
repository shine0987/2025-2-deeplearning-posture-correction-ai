"""
위치 편향 분석 스크립트
- 훈련 데이터에서 화면 위치와 라벨의 상관관계 분석
- 이미지 입력이 위치 정보를 학습하는지 확인
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# 데이터 로드
df = pd.read_csv('data/pose_data.csv')

print("="*70)
print("📊 위치 편향 분석")
print("="*70)

# 1. 라벨별 평균 좌표 분석
print("\n1️⃣ 라벨별 평균 x 좌표 (화면 위치)")
print("-" * 50)

for label in df['label'].unique():
    if label == 'unlabeled':
        continue
    
    label_data = df[df['label'] == label]
    
    # 상체 중심 x 좌표 계산
    center_x = (label_data['left_shoulder_x'] + label_data['right_shoulder_x']) / 2
    nose_x = label_data['nose_x']
    
    print(f"\n[{label.upper()}]")
    print(f"  어깨 중심 x: {center_x.mean():.4f} (std: {center_x.std():.4f})")
    print(f"  코 x 좌표: {nose_x.mean():.4f} (std: {nose_x.std():.4f})")
    print(f"  샘플 수: {len(label_data)}")

# 2. 각도와 좌표의 상관관계
print("\n\n2️⃣ 각도와 화면 위치의 상관관계")
print("-" * 50)

df_clean = df[df['label'] != 'unlabeled'].copy()
df_clean['center_x'] = (df_clean['left_shoulder_x'] + df_clean['right_shoulder_x']) / 2

correlations = {
    'neck_angle vs center_x': df_clean[['neck_angle', 'center_x']].corr().iloc[0, 1],
    'shoulder_angle vs center_x': df_clean[['shoulder_angle', 'center_x']].corr().iloc[0, 1],
    'hip_angle vs center_x': df_clean[['hip_angle', 'center_x']].corr().iloc[0, 1],
    'torso_angle vs center_x': df_clean[['torso_angle', 'center_x']].corr().iloc[0, 1],
}

for name, corr in correlations.items():
    print(f"{name}: {corr:.4f}")

# 3. 좌표 분포 시각화 (화면 위치 분석)
print("\n\n3️⃣ 화면 위치 분포 분석")
print("-" * 50)

fig, axes = plt.subplots(2, 2, figsize=(15, 12))

for label in ['normal', 'abnormal']:
    if label not in df_clean['label'].values:
        continue
    
    label_data = df_clean[df_clean['label'] == label]
    center_x = (label_data['left_shoulder_x'] + label_data['right_shoulder_x']) / 2
    
    # X 좌표 분포
    axes[0, 0].hist(center_x, bins=20, alpha=0.5, label=label)
    axes[0, 0].set_title('화면 X 위치 분포 (어깨 중심)')
    axes[0, 0].set_xlabel('X 좌표 (0=왼쪽, 1=오른쪽)')
    axes[0, 0].legend()
    axes[0, 0].axvline(0.5, color='red', linestyle='--', label='중앙')
    
    # 각도 분포
    axes[0, 1].hist(label_data['neck_angle'], bins=20, alpha=0.5, label=label)
    axes[0, 1].set_title('목 각도 분포')
    axes[0, 1].set_xlabel('각도')
    axes[0, 1].legend()
    
    axes[1, 0].hist(label_data['shoulder_angle'], bins=20, alpha=0.5, label=label)
    axes[1, 0].set_title('어깨 각도 분포')
    axes[1, 0].set_xlabel('각도')
    axes[1, 0].legend()
    
    axes[1, 1].hist(label_data['torso_angle'], bins=20, alpha=0.5, label=label)
    axes[1, 1].set_title('상체 각도 분포')
    axes[1, 1].set_xlabel('각도')
    axes[1, 1].legend()

plt.tight_layout()
plt.savefig('position_bias_analysis.png', dpi=150)
print("📈 시각화 저장: position_bias_analysis.png")

# 4. 위치별 라벨 분포
print("\n\n4️⃣ 화면 위치별 라벨 분포")
print("-" * 50)

df_clean['position_bin'] = pd.cut(df_clean['center_x'], bins=5, labels=['최좌측', '좌측', '중앙', '우측', '최우측'])

position_label_counts = pd.crosstab(df_clean['position_bin'], df_clean['label'], normalize='index') * 100
print(position_label_counts)

# 5. 이미지 파일명 샘플 확인
print("\n\n5️⃣ 이미지 파일 샘플 (각 라벨별)")
print("-" * 50)

for label in ['normal', 'abnormal']:
    if label not in df_clean['label'].values:
        continue
    
    print(f"\n[{label.upper()}] 샘플 5개:")
    label_samples = df_clean[df_clean['label'] == label].head(5)
    for idx, row in label_samples.iterrows():
        print(f"  - {row['image_name']}: center_x={row['center_x']:.3f}, neck_angle={row['neck_angle']:.1f}°")

# 6. 결론
print("\n\n" + "="*70)
print("🔍 분석 결론")
print("="*70)

normal_center_x = df_clean[df_clean['label'] == 'normal']['center_x'].mean()
abnormal_center_x = df_clean[df_clean['label'] == 'abnormal']['center_x'].mean()
position_diff = abs(normal_center_x - abnormal_center_x)

if position_diff > 0.15:
    print(f"⚠️  위치 편향 발견!")
    print(f"   Normal 평균 위치: {normal_center_x:.3f}")
    print(f"   Abnormal 평균 위치: {abnormal_center_x:.3f}")
    print(f"   차이: {position_diff:.3f} (임계값: 0.15)")
    print(f"\n💡 모델이 자세가 아닌 화면 위치를 학습했을 가능성이 높습니다!")
else:
    print(f"✅ 위치 편향 없음")
    print(f"   Normal 평균 위치: {normal_center_x:.3f}")
    print(f"   Abnormal 평균 위치: {abnormal_center_x:.3f}")
    print(f"   차이: {position_diff:.3f}")
    print(f"\n💡 모델이 자세를 제대로 학습했을 가능성이 높습니다.")

print("\n" + "="*70)
