"""
EEG Circular Pupil Map Generator
Recreates the original pupil maps with full circular distribution
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURATION
# ============================================================

# Data files (use the ones with valid ACF data)
DATA_FILES = {
    "Meditation": r"C:\Users\sappe\Desktop\OTHEORYTESTS\EEG_tests\CANON\meditation_epoch_metrics_v3_withRp.csv",
    "Rest": r"C:\Users\sappe\Desktop\OTHEORYTESTS\EEG_tests\CANON\resting_window_metrics_v3.csv",
    "Sleep": r"C:\Users\sappe\Desktop\OTHEORYTESTS\EEG_tests\CANON\sleep_bifurcation_runs.csv",
    "Sternberg": r"C:\Users\sappe\Desktop\OTHEORYTESTS\EEG_tests\CANON\sternberg_epoch_metrics_v3.csv",
    "Stress": r"C:\Users\sappe\Desktop\OTHEORYTESTS\EEG_tests\CANON\stress_window_metrics_v4.csv",
}

COLORS = {
    "Meditation": "#FF8C00",
    "Rest": "#4A90D9",
    "Sleep": "#9B59B6",
    "Sternberg": "#2ECC71",
    "Stress": "#E74C3C",
}

PHI_M = 2.18

# ============================================================
# FUNCTIONS
# ============================================================

def load_and_compute_pupil_coords(filepath, name):
    """Load data and compute pupil coordinates."""
    if not Path(filepath).exists():
        print(f"  ✗ {name}: file not found")
        return None
    
    df = pd.read_csv(filepath)
    print(f"  {name}: {len(df)} rows")
    
    # Get m_slope
    if 'm_slope' not in df.columns:
        print(f"    ✗ No m_slope column")
        return None
    
    # Get ACF column
    acf_col = None
    for col in ['acf_decay_sec', 'acf_decay', 'acf']:
        if col in df.columns:
            acf_col = col
            break
    
    if acf_col is None:
        print(f"    ✗ No ACF column")
        return None
    
    # Get flicker column
    flicker_col = None
    for col in ['flicker', 'var_env', 'var_env_dimless']:
        if col in df.columns:
            flicker_col = col
            break
    
    if flicker_col is None:
        print(f"    ✗ No flicker column")
        return None
    
    # Drop NaN
    df = df.dropna(subset=[acf_col, flicker_col, 'm_slope'])
    
    if len(df) == 0:
        print(f"    ✗ No valid data after dropping NaN")
        return None
    
    # Compute φ-distance (radius)
    df['phi_dist'] = (df['m_slope'] - PHI_M).abs()
    
    # Get values
    acf = df[acf_col].values
    flicker = df[flicker_col].values
    
    # Clip to avoid log issues
    acf_clipped = np.clip(acf, 1e-30, None)
    flicker_clipped = np.clip(flicker, 1e-30, None)
    
    # Angle calculation - TRY METHOD 2 (log_flicker, log_acf)
    # This should give full 360° spread
    df['theta'] = np.arctan2(np.log10(flicker_clipped), np.log10(acf_clipped))
    
    # Radius = raw φ-distance
    df['r'] = df['phi_dist']
    
    # Convert to Cartesian
    df['pupil_x'] = df['r'] * np.cos(df['theta'])
    df['pupil_y'] = df['r'] * np.sin(df['theta'])
    
    print(f"    ✓ r: {df['r'].min():.3f} - {df['r'].max():.3f}")
    print(f"    ✓ θ: {np.degrees(df['theta'].min()):.1f}° - {np.degrees(df['theta'].max()):.1f}°")
    
    return df


def create_circular_pupil_map(df, name, color, output_path, max_r):
    """Create a single circular pupil map."""
    fig, ax = plt.subplots(figsize=(10, 10), facecolor='#0A0A0A')
    ax.set_facecolor('#0A0A0A')
    
    n_points = len(df)
    
    # Draw concentric circles
    for r in np.arange(0.5, max_r + 0.1, 0.5):
        circle = Circle((0, 0), r, fill=False, color='#333333', linewidth=1, alpha=0.5)
        ax.add_patch(circle)
        ax.text(r * 0.7, r * 0.7, f'r={r:.1f}', color='#666', fontsize=8, ha='center')
    
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
    
    # Plot points
    ax.scatter(df['pupil_x'], df['pupil_y'], c=color, s=8, alpha=0.5, edgecolors='none', zorder=1)
    
    # Set limits
    margin = max_r * 0.1
    ax.set_xlim(-max_r - margin, max_r + margin)
    ax.set_ylim(-max_r - margin, max_r + margin)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Title
    ax.set_title(f'Pupil Map — {name}\n{n_points} points | φ-seam at center\nθ = atan2(log_flicker, log_acf)',
                 color='white', fontsize=12, pad=20)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, facecolor='#0A0A0A', bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {output_path}")


def create_combined_pupil_map(all_dfs, output_path, max_r):
    """Create combined pupil map with all datasets."""
    fig, ax = plt.subplots(figsize=(12, 12), facecolor='#0A0A0A')
    ax.set_facecolor('#0A0A0A')
    
    # Draw concentric circles
    for r in np.arange(0.5, max_r + 0.1, 0.5):
        circle = Circle((0, 0), r, fill=False, color='#333333', linewidth=1, alpha=0.5)
        ax.add_patch(circle)
        ax.text(r * 0.7, r * 0.7, f'r={r:.1f}', color='#666', fontsize=8, ha='center')
    
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
    
    # Plot each dataset
    for name, df in all_dfs.items():
        if df is not None and len(df) > 0:
            ax.scatter(df['pupil_x'], df['pupil_y'], c=COLORS[name], 
                      s=5, alpha=0.4, edgecolors='none', label=name, zorder=1)
    
    ax.legend(frameon=True, facecolor='#1A1A1A', edgecolor='#444', 
              labelcolor='white', fontsize=10, loc='upper right')
    
    # Set limits
    margin = max_r * 0.1
    ax.set_xlim(-max_r - margin, max_r + margin)
    ax.set_ylim(-max_r - margin, max_r + margin)
    ax.set_aspect('equal')
    ax.axis('off')
    
    ax.set_title('All Brain States in Pupil Space\nφ-seam at Center | Raw φ-Distance\nθ = atan2(log_flicker, log_acf)',
                 color='white', fontsize=14, pad=20)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, facecolor='#0A0A0A', bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {output_path}")


# ============================================================
# MAIN
# ============================================================

print("\n" + "="*60)
print("EEG CIRCULAR PUPIL MAP GENERATOR")
print("="*60 + "\n")

print("Loading data...")
all_dfs = {}
for name, filepath in DATA_FILES.items():
    df = load_and_compute_pupil_coords(filepath, name)
    if df is not None and len(df) > 0:
        all_dfs[name] = df

# Find global max radius
if all_dfs:
    all_radii = []
    for df in all_dfs.values():
        all_radii.extend(df['r'].values)
    global_max_r = max(all_radii)
    global_max_r = np.ceil(global_max_r * 2) / 2
    print(f"\nGlobal max radius: {global_max_r:.2f}")
    
    print("\n" + "-"*40)
    print("Creating individual pupil maps...")
    print("-"*40)
    
    for name, df in all_dfs.items():
        output = f"pupil_map_{name.lower()}_circular.png"
        create_circular_pupil_map(df, name, COLORS[name], output, global_max_r)
    
    print("\n" + "-"*40)
    print("Creating combined pupil map...")
    print("-"*40)
    
    create_combined_pupil_map(all_dfs, "pupil_map_all_circular.png", global_max_r)
    
    print("\n" + "="*60)
    print("COMPLETE!")
    print("="*60)
    
    import os
    for f in os.listdir('.'):
        if f.startswith('pupil_map') and f.endswith('.png'):
            print(f"  {f}")
else:
    print("\nNo data loaded!")

print("\n")