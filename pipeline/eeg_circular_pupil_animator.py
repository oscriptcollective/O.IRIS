"""
EEG Circular Pupil Map Animator
Creates animated GIFs showing brain state journey through circular pupil space
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.animation import FuncAnimation, PillowWriter
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURATION
# ============================================================

# Data files with valid data
DATA_FILES = {
    "Meditation": {
        "path": r"C:\Users\sappe\Desktop\OTHEORYTESTS\EEG_tests\CANON\meditation_epoch_metrics_v3_withRp.csv",
        "color": "#FF8C00",
        "subject_col": "subject",
        "time_col": "onset",
        "acf_col": "acf_decay_sec",
        "flicker_col": "flicker",
    },
    "Sternberg": {
        "path": r"C:\Users\sappe\Desktop\OTHEORYTESTS\EEG_tests\CANON\sternberg_epoch_metrics_v3.csv",
        "color": "#2ECC71",
        "subject_col": "subject",
        "time_col": "onset",
        "acf_col": "acf_decay_sec",
        "flicker_col": "flicker",
    },
    "Stress": {
        "path": r"C:\Users\sappe\Desktop\OTHEORYTESTS\EEG_tests\CANON\stress_window_metrics_v4.csv",
        "color": "#E74C3C",
        "subject_col": "subject",
        "time_col": "t_start",
        "acf_col": "acf_decay_sec",
        "flicker_col": "flicker",
    },
    "Rest": {
        "path": r"C:\Users\sappe\Desktop\OTHEORYTESTS\EEG_tests\CANON\resting_window_metrics_v3.csv",
        "color": "#4A90D9",
        "subject_col": "subject",
        "time_col": None,  # Use index order
        "acf_col": "acf_decay_sec",
        "flicker_col": "var_env",
    },
    "Sleep": {
        "path": r"C:\Users\sappe\Desktop\OTHEORYTESTS\EEG_tests\CANON\sleep_bifurcation_runs.csv",
        "color": "#9B59B6",
        "subject_col": "subject",
        "time_col": None,
        "acf_col": "acf_decay_sec",
        "flicker_col": "var_env",
    },
}

PHI_M = 2.18


def compute_pupil_coords(df, acf_col, flicker_col):
    """Compute pupil coordinates from dataframe."""
    # Drop NaN
    df = df.dropna(subset=[acf_col, flicker_col, 'm_slope']).copy()
    
    if len(df) == 0:
        return None
    
    # φ-distance (radius)
    df['phi_dist'] = (df['m_slope'] - PHI_M).abs()
    
    # Get values
    acf = df[acf_col].values
    flicker = df[flicker_col].values
    
    # Clip to avoid log issues
    acf_clipped = np.clip(acf, 1e-30, None)
    flicker_clipped = np.clip(flicker, 1e-30, None)
    
    # Angle using atan2(log_flicker, log_acf) - gives full 360°
    df['theta'] = np.arctan2(np.log10(flicker_clipped), np.log10(acf_clipped))
    
    # Radius = raw φ-distance
    df['r'] = df['phi_dist']
    
    # Cartesian for plotting
    df['pupil_x'] = df['r'] * np.cos(df['theta'])
    df['pupil_y'] = df['r'] * np.sin(df['theta'])
    
    return df


def load_dataset(name, config):
    """Load and process dataset."""
    path = Path(config["path"])
    if not path.exists():
        print(f"  ✗ {name}: file not found")
        return None
    
    df = pd.read_csv(path)
    print(f"  {name}: {len(df)} rows loaded")
    
    # Get m_slope
    if 'm_slope' not in df.columns:
        print(f"    ✗ No m_slope column")
        return None
    
    # Compute pupil coordinates
    df = compute_pupil_coords(df, config["acf_col"], config["flicker_col"])
    
    if df is None:
        return None
    
    # Subject column
    if config["subject_col"] in df.columns:
        df['subject'] = df[config["subject_col"]].astype(str)
    else:
        df['subject'] = 'all'
    
    # Time column
    if config["time_col"] and config["time_col"] in df.columns:
        df['time'] = df[config["time_col"]]
    else:
        df['time'] = np.arange(len(df)) * 10  # assume 10s windows
    
    print(f"    ✓ r: {df['r'].min():.3f} - {df['r'].max():.3f}")
    print(f"    ✓ θ: {np.degrees(df['theta'].min()):.1f}° - {np.degrees(df['theta'].max()):.1f}°")
    
    return df


def create_animation(df, name, color, output_path, max_r, subject=None, max_frames=200):
    """Create animated GIF of brain state journey through pupil."""
    
    # Filter by subject
    if subject and 'subject' in df.columns:
        df_anim = df[df['subject'] == subject].copy()
        if len(df_anim) == 0:
            print(f"  ✗ Subject {subject} not found")
            return
    else:
        df_anim = df.copy()
    
    # Sort by time
    df_anim = df_anim.sort_values('time').reset_index(drop=True)
    
    if len(df_anim) < 5:
        print(f"  ✗ Not enough frames ({len(df_anim)})")
        return
    
    # Limit frames for GIF
    if len(df_anim) > max_frames:
        step = len(df_anim) // max_frames
        df_anim = df_anim.iloc[::step].reset_index(drop=True)
    
    n_frames = len(df_anim)
    print(f"  Creating animation with {n_frames} frames")
    
    # Setup figure
    fig, ax = plt.subplots(figsize=(10, 10), facecolor='#0A0A0A')
    ax.set_facecolor('#0A0A0A')
    
    # Draw background circles
    for r in np.arange(0.5, max_r + 0.1, 0.5):
        circle = Circle((0, 0), r, fill=False, color='#333333', linewidth=1, alpha=0.5)
        ax.add_patch(circle)
        ax.text(r * 0.7, r * 0.7, f'r={r:.1f}', color='#666', fontsize=7, ha='center')
    
    # Draw angle lines
    for theta_deg in range(0, 360, 45):
        theta_rad = np.radians(theta_deg)
        x_end = max_r * np.cos(theta_rad)
        y_end = max_r * np.sin(theta_rad)
        ax.plot([0, x_end], [0, y_end], color='#333333', linewidth=0.5, alpha=0.3)
        label_x = (max_r + 0.1) * np.cos(theta_rad)
        label_y = (max_r + 0.1) * np.sin(theta_rad)
        ax.text(label_x, label_y, f'{theta_deg}°', color='#666', fontsize=8, ha='center')
    
    # Center φ marker
    center = Circle((0, 0), 0.08, facecolor='#FFD700', alpha=0.8, zorder=2)
    ax.add_patch(center)
    ax.text(0, 0, 'φ', color='white', fontsize=14, ha='center', va='center', fontweight='bold')
    
    # Background points (all points faint)
    ax.scatter(df_anim['pupil_x'], df_anim['pupil_y'], 
              c=color, s=3, alpha=0.15, edgecolors='none', zorder=1)
    
    # Set limits
    margin = max_r * 0.1
    ax.set_xlim(-max_r - margin, max_r + margin)
    ax.set_ylim(-max_r - margin, max_r + margin)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Title
    title = ax.set_title(f'{name} — Journey Through Pupil Space\nFrame 0/{n_frames}',
                         color='white', fontsize=12, pad=20)
    
    # Trail elements (15 fading dots)
    trail_dots = []
    for i in range(15):
        dot, = ax.plot([], [], 'o', color=color, alpha=0.1, markersize=4, zorder=3)
        trail_dots.append(dot)
    
    # Current dot (size changes with radius)
    current_dot, = ax.plot([], [], 'o', color=color, markersize=12,
                           markeredgecolor='white', markeredgewidth=2, zorder=4)
    
    # Info text
    info_text = ax.text(0.02, 0.98, '', transform=ax.transAxes,
                        color='white', fontsize=9, verticalalignment='top',
                        fontfamily='monospace',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='#1A1A1A', edgecolor='#555'))
    
    # Trail history
    trail_history = []
    
    def update(frame):
        row = df_anim.iloc[frame]
        x = row['pupil_x']
        y = row['pupil_y']
        r = row['r']
        m = row['m_slope']
        phi_dist = row['phi_dist']
        t_min = row['time'] / 60 if 'time' in row else frame * 10 / 60
        
        # Update trail
        trail_history.append((x, y))
        if len(trail_history) > 15:
            trail_history.pop(0)
        
        for i, dot in enumerate(trail_dots):
            if i < len(trail_history):
                alpha = (i + 1) / len(trail_history) * 0.6
                dot.set_data([trail_history[i][0]], [trail_history[i][1]])
                dot.set_alpha(alpha)
                dot.set_markersize(5)
            else:
                dot.set_data([], [])
        
        # Current dot - size constricts as radius decreases
        dot_size = 8 + (1 - min(r, 2.0)/2.0) * 15
        current_dot.set_data([x], [y])
        current_dot.set_markersize(dot_size)
        
        # State description
        if phi_dist < 0.34:
            state = '● CORE φ-zone — CONSTRICTED'
        elif phi_dist < 0.50:
            state = '○ Near φ-zone'
        elif phi_dist < 1.0:
            state = '◐ Approaching φ'
        else:
            state = f'◯ DILATED — φ-dist = {phi_dist:.2f}'
        
        info_text.set_text(
            f'Dataset: {name}\n'
            f'Subject: {subject if subject else "all"}\n'
            f'Time: {t_min:.1f} min\n'
            f'Frame: {frame+1}/{n_frames}\n'
            f'─────────────────\n'
            f'Pupil Radius: {r:.3f}\n'
            f'm slope: {m:.3f}\n'
            f'φ-distance: {phi_dist:.3f}\n'
            f'─────────────────\n'
            f'{state}'
        )
        
        # Update title
        if r < 0.5:
            dilation = 'CONSTRICTED (meditation-like)'
        elif r > 1.5:
            dilation = 'DILATED (sleep-like)'
        else:
            dilation = 'BALANCED'
        title.set_text(f'{name} — {dilation} — Frame {frame+1}/{n_frames}')
        
        return [current_dot, info_text, title] + trail_dots
    
    # Create animation
    anim = FuncAnimation(fig, update, frames=n_frames, interval=100, blit=False)
    
    # Save as GIF
    writer = PillowWriter(fps=10)
    anim.save(output_path, writer=writer, dpi=100)
    plt.close()
    print(f'  ✓ Saved GIF: {output_path}')


# ============================================================
# MAIN
# ============================================================

print('\n' + '='*60)
print('EEG CIRCULAR PUPIL MAP ANIMATOR')
print('='*60 + '\n')

print('Loading datasets...')
all_dfs = {}
for name, config in DATA_FILES.items():
    df = load_dataset(name, config)
    if df is not None and len(df) > 0:
        all_dfs[name] = df

# Find global max radius
if all_dfs:
    all_radii = []
    for df in all_dfs.values():
        all_radii.extend(df['r'].values)
    global_max_r = max(all_radii)
    global_max_r = np.ceil(global_max_r * 2) / 2
    print(f'\nGlobal max radius: {global_max_r:.2f}')
    
    # Create output folder
    output_dir = Path(r'C:\Users\sappe\Desktop\OTHEORYTESTS\EEG_tests\CANON\pupil_animations')
    output_dir.mkdir(exist_ok=True)
    print(f'\nOutput folder: {output_dir}')
    
    print('\n' + '-'*40)
    print('Creating animations...')
    print('-'*40)
    
    for name, df in all_dfs.items():
        if len(df) < 10:
            print(f'  Skipping {name}: only {len(df)} points')
            continue
        
        # Find a subject with enough data
        if 'subject' in df.columns:
            subjects = df['subject'].value_counts()
            found = False
            for subj, count in subjects.items():
                if 20 <= count <= 500:
                    output = output_dir / f'pupil_animation_{name.lower()}.gif'
                    create_animation(df, name, DATA_FILES[name]['color'], output, global_max_r, subject=subj)
                    found = True
                    break
            if not found:
                output = output_dir / f'pupil_animation_{name.lower()}.gif'
                create_animation(df, name, DATA_FILES[name]['color'], output, global_max_r)
        else:
            output = output_dir / f'pupil_animation_{name.lower()}.gif'
            create_animation(df, name, DATA_FILES[name]['color'], output, global_max_r)
    
    print('\n' + '='*60)
    print('COMPLETE!')
    print('='*60)
    print(f'\nAnimations saved in: {output_dir}')
    print('\nFiles created:')
    for f in output_dir.glob('*.gif'):
        print(f'  {f.name}')
    
else:
    print('\nNo data loaded!')

print('\n')