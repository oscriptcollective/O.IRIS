"""
Convert GIF to MP4 and Create Combined State Transition Animation
Using imageio (no external ffmpeg needed)
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.animation import FuncAnimation
import imageio
from PIL import Image
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURATION
# ============================================================

CANON_DIR = Path(r"C:\Users\sappe\Desktop\OTHEORYTESTS\EEG_tests\CANON")
ANIMATION_DIR = CANON_DIR / "pupil_animations"
OUTPUT_DIR = CANON_DIR / "pupil_videos"

# Create output directory
OUTPUT_DIR.mkdir(exist_ok=True)

# Dataset configurations
DATASETS = {
    "Meditation": {
        "color": "#FF8C00",
        "radius": 0.25,
        "description": "Constricted — Coherent, integrated, effortless",
    },
    "Rest": {
        "color": "#4A90D9",
        "radius": 0.85,
        "description": "Balanced — Drifting, wandering, intermediate",
    },
    "Sternberg": {
        "color": "#2ECC71",
        "radius": 1.15,
        "description": "Partially constricted — Controlled, effortful",
    },
    "Stress": {
        "color": "#E74C3C",
        "radius": 1.25,
        "description": "Unstable — Trying to focus, failing to stabilize",
    },
    "Sleep": {
        "color": "#9B59B6",
        "radius": 1.85,
        "description": "Dilated — Fragmented, restorative",
    },
}

MAX_R = 2.2


def convert_gif_to_mp4(gif_path, mp4_path):
    """Convert GIF to MP4 using imageio."""
    try:
        # Read GIF
        reader = imageio.get_reader(gif_path)
        fps = reader.get_meta_data()['fps']
        
        # Write MP4
        writer = imageio.get_writer(mp4_path, fps=fps, format='FFMPEG', codec='libx264')
        for frame in reader:
            writer.append_data(frame)
        writer.close()
        print(f"  ✓ Converted: {mp4_path.name}")
        return True
    except Exception as e:
        print(f"  ✗ Error converting {gif_path.name}: {e}")
        return False


def create_combined_animation(output_path, duration=12, fps=30):
    """Create a combined animation showing all states transitioning."""
    
    n_frames = duration * fps
    t = np.linspace(0, 2 * np.pi, n_frames)
    
    # Create smooth transitions between states
    states = ["Meditation", "Rest", "Sternberg", "Stress", "Sleep", "Meditation"]
    
    # Define target radius and angle for each state
    targets = []
    for state in states:
        if state == "Meditation":
            targets.append({"r": 0.25, "theta": np.pi/4, "color": DATASETS[state]["color"]})
        elif state == "Rest":
            targets.append({"r": 0.85, "theta": np.pi/2, "color": DATASETS[state]["color"]})
        elif state == "Sternberg":
            targets.append({"r": 1.15, "theta": 3*np.pi/4, "color": DATASETS[state]["color"]})
        elif state == "Stress":
            targets.append({"r": 1.25, "theta": np.pi, "color": DATASETS[state]["color"]})
        elif state == "Sleep":
            targets.append({"r": 1.85, "theta": 5*np.pi/4, "color": DATASETS[state]["color"]})
    
    # Interpolate between targets
    frames_per_segment = n_frames // (len(targets) - 1)
    radius_t = []
    angle_t = []
    color_t = []
    
    for i in range(len(targets) - 1):
        start = targets[i]
        end = targets[i + 1]
        for j in range(frames_per_segment):
            alpha = j / frames_per_segment
            r = start["r"] * (1 - alpha) + end["r"] * alpha
            theta = start["theta"] * (1 - alpha) + end["theta"] * alpha
            # Color interpolation
            start_color = np.array([int(start["color"][j:j+2], 16) for j in (1, 3, 5)])
            end_color = np.array([int(end["color"][j:j+2], 16) for j in (1, 3, 5)])
            color = start_color * (1 - alpha) + end_color * alpha
            color_hex = f"#{int(color[0]):02x}{int(color[1]):02x}{int(color[2]):02x}"
            radius_t.append(r)
            angle_t.append(theta)
            color_t.append(color_hex)
    
    # Ensure we have exactly n_frames
    radius_t = radius_t[:n_frames]
    angle_t = angle_t[:n_frames]
    color_t = color_t[:n_frames]
    
    # Create frames for video
    print("  Generating frames...")
    frames = []
    
    for frame in range(n_frames):
        if frame % 30 == 0:
            print(f"    Frame {frame}/{n_frames}")
        
        fig, ax = plt.subplots(figsize=(8, 8), facecolor='#0A0A0A')
        ax.set_facecolor('#0A0A0A')
        
        # Draw background circles
        for r in [0.5, 1.0, 1.5, 2.0]:
            circle = Circle((0, 0), r, fill=False, color='#333333', linewidth=1, alpha=0.5)
            ax.add_patch(circle)
            ax.text(r * 0.7, r * 0.7, f'r={r:.1f}', color='#666', fontsize=7, ha='center')
        
        # Draw angle lines
        for theta_deg in range(0, 360, 45):
            theta_rad = np.radians(theta_deg)
            x_end = MAX_R * np.cos(theta_rad)
            y_end = MAX_R * np.sin(theta_rad)
            ax.plot([0, x_end], [0, y_end], color='#333333', linewidth=0.5, alpha=0.3)
            label_x = (MAX_R + 0.1) * np.cos(theta_rad)
            label_y = (MAX_R + 0.1) * np.sin(theta_rad)
            ax.text(label_x, label_y, f'{theta_deg}°', color='#666', fontsize=7, ha='center')
        
        # Center φ marker
        center = Circle((0, 0), 0.08, facecolor='#FFD700', alpha=0.8, zorder=2)
        ax.add_patch(center)
        ax.text(0, 0, 'φ', color='white', fontsize=12, ha='center', va='center', fontweight='bold')
        
        # Current point
        r = radius_t[frame]
        theta = angle_t[frame]
        color = color_t[frame]
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        
        # Trail (last 15 frames)
        trail_start = max(0, frame - 15)
        for i in range(trail_start, frame):
            alpha = (i - trail_start + 1) / 15 * 0.5
            r_prev = radius_t[i]
            theta_prev = angle_t[i]
            x_prev = r_prev * np.cos(theta_prev)
            y_prev = r_prev * np.sin(theta_prev)
            ax.plot([x_prev], [y_prev], 'o', color=color_t[i], alpha=alpha, markersize=4, zorder=3)
        
        # Current dot (size changes with radius)
        dot_size = 8 + (1 - min(r, 2.0)/2.0) * 15
        ax.plot([x], [y], 'o', color=color, markersize=dot_size,
                markeredgecolor='white', markeredgewidth=2, zorder=4)
        
        # Determine current state
        current_state = None
        for state, config in DATASETS.items():
            if abs(r - config["radius"]) < 0.2:
                current_state = state
                break
        
        if current_state:
            desc = DATASETS[current_state]["description"]
            state_text = f'{current_state}: {desc}'
        else:
            state_text = 'Transitioning between states'
        
        # Add text
        ax.text(0.05, 0.95, f'Radius: {r:.2f}\nState: {state_text}',
                transform=ax.transAxes, color='white', fontsize=8,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#1A1A1A', edgecolor='#555'))
        
        # Legend
        legend_y = 0.95
        for state, config in DATASETS.items():
            ax.text(0.95, legend_y, f'● {state}', transform=ax.transAxes,
                    color=config['color'], fontsize=7, ha='right', va='top')
            legend_y -= 0.05
        
        # Title
        ax.set_title('Brain State Journey — Through the Pupil of Consciousness',
                     color='white', fontsize=11, pad=15)
        
        ax.set_xlim(-MAX_R - 0.2, MAX_R + 0.2)
        ax.set_ylim(-MAX_R - 0.2, MAX_R + 0.2)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Convert to image
        fig.canvas.draw()
        img = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
        img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        frames.append(img)
        
        plt.close(fig)
    
    # Save as video using imageio
    print("  Saving video...")
    writer = imageio.get_writer(output_path, fps=fps, format='FFMPEG', codec='libx264')
    for frame in frames:
        writer.append_data(frame)
    writer.close()
    print(f"  ✓ Saved: {output_path}")


# ============================================================
# MAIN
# ============================================================

print('\n' + '='*60)
print('CONVERTING GIFs TO MP4 + CREATING COMBINED ANIMATION')
print('='*60 + '\n')

# Check if imageio has ffmpeg
try:
    import imageio
    imageio.plugins.ffmpeg.download()
    print('✓ imageio ffmpeg plugin ready\n')
except:
    print('⚠️ Installing imageio-ffmpeg...')
    import subprocess
    subprocess.run(['pip', 'install', 'imageio-ffmpeg'], capture_output=True)
    print('✓ imageio-ffmpeg installed\n')

# Convert existing GIFs to MP4
if ANIMATION_DIR.exists():
    print('Converting GIFs to MP4...')
    print('-' * 40)
    
    gif_files = list(ANIMATION_DIR.glob('*.gif'))
    if gif_files:
        for gif_path in gif_files:
            mp4_path = OUTPUT_DIR / gif_path.with_suffix('.mp4').name
            convert_gif_to_mp4(gif_path, mp4_path)
    else:
        print('  No GIF files found in animations folder')
else:
    print('No animations folder found, skipping GIF conversion')

# Create combined animation
print('\n' + '-' * 40)
print('Creating combined state transition animation...')
print('-' * 40)

combined_path = OUTPUT_DIR / 'pupil_combined_transition.mp4'
create_combined_animation(combined_path, duration=12, fps=30)

print('\n' + '=' * 60)
print('COMPLETE!')
print('=' * 60)
print(f'\nVideos saved in: {OUTPUT_DIR}')
print('\nFiles created:')
for f in OUTPUT_DIR.glob('*.mp4'):
    print(f'  {f.name}')

print('\nTo upload to Twitter/X:')
print('  • Each video can be attached directly to a tweet')
print('  • The combined animation shows all states transitioning')
print('\n')