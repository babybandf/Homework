"""
Generate detailed figures for Case 1 (FG=EG) and Case 2 (FG=EF)
with all key angles labeled.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# ========== Utility Functions ==========
def draw_triangle(ax, pts, color='black', linewidth=1.5, fill=False, fill_color='lightgray', alpha=0.3):
    A, B, C = pts
    triangle = plt.Polygon([A, B, C], fill=fill, facecolor=fill_color, edgecolor=color, linewidth=linewidth, alpha=alpha)
    ax.add_patch(triangle)

def draw_polygon(ax, pts, color='black', linewidth=1.5, fill=False, fill_color='lightgray', alpha=0.3):
    polygon = plt.Polygon(pts, fill=fill, facecolor=fill_color, edgecolor=color, linewidth=linewidth, alpha=alpha)
    ax.add_patch(polygon)

def draw_segment(ax, p1, p2, color='black', linewidth=1.5, linestyle='-', alpha=1.0):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linewidth=linewidth, linestyle=linestyle, alpha=alpha)

def label_point(ax, point, label, offset=(0, 0.25), fontsize=13, fontweight='bold'):
    ax.text(point[0] + offset[0], point[1] + offset[1], label,
            ha='center', va='center', fontsize=fontsize, fontweight=fontweight)

def rotate_point(center, point, angle_deg):
    angle_rad = np.radians(angle_deg)
    cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)
    dx = point[0] - center[0]
    dy = point[1] - center[1]
    new_x = center[0] + dx * cos_a - dy * sin_a
    new_y = center[1] + dx * sin_a + dy * cos_a
    return np.array([new_x, new_y])

def angle_between(p1, vertex, p2):
    v1 = p1 - vertex
    v2 = p2 - vertex
    dot = np.dot(v1, v2)
    n = np.linalg.norm(v1) * np.linalg.norm(v2)
    if n < 1e-10:
        return 0
    return np.degrees(np.arccos(max(-1.0, min(1.0, dot / n))))

def draw_angle_arc(ax, center, p1, p2, radius=0.3, color='blue', label=None, linewidth=1.5, label_fontsize=11):
    angle1 = np.degrees(np.arctan2(p1[1]-center[1], p1[0]-center[0]))
    angle2 = np.degrees(np.arctan2(p2[1]-center[1], p2[0]-center[0]))
    if angle2 < angle1:
        angle1, angle2 = angle2, angle1
    if angle2 - angle1 > 180:
        angle1, angle2 = angle2, angle1 + 360
    arc = patches.Arc(center, 2*radius, 2*radius, angle=0,
                      theta1=angle1, theta2=angle2, color=color, linewidth=linewidth)
    ax.add_patch(arc)
    if label:
        mid_angle = np.radians((angle1 + angle2) / 2)
        label_r = radius + 0.25
        ax.text(center[0] + label_r * np.cos(mid_angle),
                center[1] + label_r * np.sin(mid_angle),
                label, ha='center', va='center', fontsize=label_fontsize, color=color, fontweight='bold')

# ========== Common Geometry ==========
base = 3.5
half_base = base / 2
CA_len = base * np.sin(np.radians(72)) / np.sin(np.radians(36))
height = np.sqrt(CA_len**2 - half_base**2)

B = np.array([0.0, 0.0])
A = np.array([base, 0.0])
C = np.array([half_base, height])
E = np.array([5.5, 0.0])

def solve_case(t):
    D = A + t * (C - A)
    F = rotate_point(D, E, 36)
    G = rotate_point(D, A, 36)
    return D, F, G

# Case 1: FG = EG
lo, hi = 0.90, 0.99
for _ in range(50):
    mid = (lo + hi) / 2
    D, F, G = solve_case(mid)
    if np.linalg.norm(F - G) > np.linalg.norm(E - G):
        lo = mid
    else:
        hi = mid
t1 = (lo + hi) / 2
D1, F1, G1 = solve_case(t1)

# Case 2: FG = EF
lo, hi = 0.30, 0.40
for _ in range(50):
    mid = (lo + hi) / 2
    D, F, G = solve_case(mid)
    if np.linalg.norm(F - G) > np.linalg.norm(E - F):
        lo = mid
    else:
        hi = mid
t2 = (lo + hi) / 2
D2, F2, G2 = solve_case(t2)

# ========== Compute all angles ==========
def compute_angles(D, F, G):
    return {
        'DAE': angle_between(D, A, E),
        'DAG': angle_between(D, A, G),
        'EAG': angle_between(E, A, G),
        'DGA': angle_between(D, G, A),
        'EGA': angle_between(E, G, A),
        'DGF': angle_between(D, G, F),
        'EG_F': angle_between(E, G, F),  # EGF
        'FGE': angle_between(F, G, E),
        'FEG': angle_between(F, E, G),
        'EFG': angle_between(E, F, G),
        'ADG': angle_between(A, D, G),
        'AED': angle_between(A, E, D),
        'FED': angle_between(F, E, D),
        'DFG': angle_between(D, F, G),
        'EFD': angle_between(E, F, D),
        'AEG': angle_between(A, E, G),
    }

a1 = compute_angles(D1, F1, G1)
a2 = compute_angles(D2, F2, G2)

# ========== Helper: draw full configuration for a case ==========
def draw_case_figure(ax, D, F, G, angles, case_label, fge_label, is_case1):
    # Draw ABC faintly
    draw_triangle(ax, (A, B, C), color='gray', linewidth=1, fill=False, alpha=0.4)
    draw_segment(ax, A, E, color='gray', linewidth=1, alpha=0.4)
    
    # Draw EDF lightly
    draw_triangle(ax, (E, D, F), color='lightcoral', linewidth=1.5, fill=True, fill_color='lightyellow', alpha=0.3)
    
    # Draw DA and DG
    draw_segment(ax, D, A, color='purple', linewidth=2)
    draw_segment(ax, D, G, color='purple', linewidth=2, linestyle='--')
    
    # Draw AE and AG (dashed)
    draw_segment(ax, A, E, color='brown', linewidth=2)
    draw_segment(ax, A, G, color='gray', linewidth=1.5, linestyle='--', alpha=0.7)
    
    # Highlight triangle EGF
    draw_triangle(ax, (E, G, F), color='blue', linewidth=3, fill=True, fill_color='lavender', alpha=0.5)
    
    # Label points
    label_point(ax, B, 'B', offset=(-0.3, -0.3))
    label_point(ax, A, 'A', offset=(0.3, -0.3))
    label_point(ax, C, 'C', offset=(0.1, 0.3))
    label_point(ax, D, 'D', offset=(0, -0.35))
    label_point(ax, E, 'E', offset=(0.3, -0.3))
    label_point(ax, F, 'F', offset=(0.3, 0.1))
    label_point(ax, G, 'G', offset=(0.3, 0.3))

    # === Angle arcs at G ===
    # DGA (purple, 72)
    draw_angle_arc(ax, G, D, A, radius=0.5, color='purple', label='72°', linewidth=2)
    # DGF (green, 108)
    draw_angle_arc(ax, G, D, F, radius=1.0, color='green', label='108°', linewidth=2)
    
    if is_case1:
        # EGA (magenta, 36) - the base angle of AEG
        draw_angle_arc(ax, G, E, A, radius=0.75, color='magenta', label='36°', linewidth=2)
        # FGE (red, 144) - the target angle
        draw_angle_arc(ax, G, F, E, radius=1.5, color='red', label='144°', linewidth=3)
    else:
        # EGA (magenta, 108) - apex of isos AEG
        draw_angle_arc(ax, G, E, A, radius=0.75, color='magenta', label='108°', linewidth=2)
        # FGE (red, 72) - the target angle
        draw_angle_arc(ax, G, F, E, radius=1.5, color='red', label='72°', linewidth=3)
    
    # === Angle arcs at A ===
    draw_angle_arc(ax, A, D, E, radius=0.5, color='orange', label='108°', linewidth=1.5)
    draw_angle_arc(ax, A, D, G, radius=0.8, color='darkorange', label='72°', linewidth=1.5)
    
    if is_case1:
        # EAG = 36
        draw_angle_arc(ax, A, E, G, radius=1.0, color='magenta', label='36°', linewidth=1.5)
    else:
        # EAG also 36
        draw_angle_arc(ax, A, E, G, radius=1.0, color='magenta', label='36°', linewidth=1.5)
    
    # Title
    ax.set_xlim(-0.5, 8.5)
    ax.set_ylim(-1, 7)
    ax.axis('off')
    tit = f'Case: FG = EG' if is_case1 else f'Case: FG = EF'
    ax.set_title(tit, fontsize=14, fontweight='bold', pad=10, color='darkblue')
    
    # Legend box for angles
    if is_case1:
        legend_text = (
            'Key Angles at G:\n'
            '  ∠DGF = 108° (green)\n'
            '  ∠DGA =  72° (purple)\n'
            '  ∠EGA =  36° (magenta)\n'
            '  ─────────────────\n'
            '  ∠FGE = 360°−108°−72°−36°\n'
            '       = 144°  (red)  ← answer'
        )
    else:
        legend_text = (
            'Key Angles at G:\n'
            '  ∠DGF = 108° (green)\n'
            '  ∠DGA =  72° (purple)\n'
            '  ∠EGA = 108° (magenta)\n'
            '  ─────────────────\n'
            '  ∠FGE = 360°−108°−72°−108°\n'
            '       =  72°  (red)  ← answer'
        )
    
    ax.text(7.8, 5.5, legend_text, ha='left', va='top', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray', alpha=0.9),
            family='monospace')

# ========== Figure for Case 1 ==========
fig, ax = plt.subplots(1, 1, figsize=(11, 8))
ax.set_aspect('equal')
draw_case_figure(ax, D1, F1, G1, a1, 'Case 1: FG = EG', '∠FGE = 144°', is_case1=True)
plt.tight_layout()
plt.savefig('case1_detail.png', dpi=150, bbox_inches='tight')
plt.close()

# ========== Figure for Case 2 ==========
fig, ax = plt.subplots(1, 1, figsize=(11, 8))
ax.set_aspect('equal')
draw_case_figure(ax, D2, F2, G2, a2, 'Case 2: FG = EF', '∠FGE = 72°', is_case1=False)
plt.tight_layout()
plt.savefig('case2_detail.png', dpi=150, bbox_inches='tight')
plt.close()

print("Case figures generated successfully!")
print(f"Case 1 (FG=EG): t={t1:.6f}, FGE={a1['FGE']:.2f}°")
print(f"Case 2 (FG=EF): t={t2:.6f}, FGE={a2['FGE']:.2f}°")
