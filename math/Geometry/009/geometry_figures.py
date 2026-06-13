"""
Problem 009: Isosceles Triangle Rotation Problem
Redesigned: base BA horizontal, B left, A right, C above BA
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# ========== Utility Functions ==========
def draw_triangle(ax, A, B, C, color='black', linewidth=1.5, fill=False, fill_color='lightgray', alpha=0.3):
    triangle = plt.Polygon([A, B, C], fill=fill, facecolor=fill_color, edgecolor=color, linewidth=linewidth, alpha=alpha)
    ax.add_patch(triangle)
    ax.plot([A[0], B[0]], [A[1], B[1]], color=color, linewidth=linewidth)
    ax.plot([B[0], C[0]], [B[1], C[1]], color=color, linewidth=linewidth)
    ax.plot([C[0], A[0]], [C[1], A[1]], color=color, linewidth=linewidth)

def draw_angle_arc(ax, center, p1, p2, radius=0.3, color='blue', label=None, linewidth=1.5):
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
        label_r = radius + 0.2
        ax.text(center[0] + label_r * np.cos(mid_angle),
                center[1] + label_r * np.sin(mid_angle),
                label, ha='center', va='center', fontsize=11, color=color, fontweight='bold')

def label_point(ax, point, label, offset=(0, 0.25), fontsize=12, fontweight='bold'):
    ax.text(point[0] + offset[0], point[1] + offset[1], label,
            ha='center', va='center', fontsize=fontsize, fontweight=fontweight)

def draw_line(ax, p1, p2, color='black', linewidth=1.5, linestyle='-'):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linewidth=linewidth, linestyle=linestyle)

def rotate_point(center, point, angle_deg):
    angle_rad = np.radians(angle_deg)
    cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)
    dx = point[0] - center[0]
    dy = point[1] - center[1]
    new_x = center[0] + dx * cos_a - dy * sin_a
    new_y = center[1] + dx * sin_a + dy * cos_a
    return np.array([new_x, new_y])

# ========== Common Geometry ==========
# Triangle ABC: B left, A right, C above BA, apex angle at C = 36 deg
base = 3.5
half_base = base / 2
# Using law of sines: CA/sin(72) = base/sin(36)
CA_len = base * np.sin(np.radians(72)) / np.sin(np.radians(36))
height = np.sqrt(CA_len**2 - half_base**2)

B = np.array([0.0, 0.0])
A = np.array([base, 0.0])
C = np.array([half_base, height])

# D on AC at 55% from A
D = A + 0.55 * (C - A)

# E on BA extended beyond A (to the right)
E = np.array([5.5, 0.0])

# F: rotate E around D by +36 deg CCW (so triangle EDF has apex D = 36 deg)
F = rotate_point(D, E, 36)

# G: rotate A around D by +36 deg CCW (DA rotated 36 deg CCW = DG)
G = rotate_point(D, A, 36)

# ========== Figure 1: Problem Setup ==========
fig, ax = plt.subplots(1, 1, figsize=(10, 8))
ax.set_aspect('equal')

draw_triangle(ax, B, A, C, color='black', linewidth=2)  # note: triangle ABC drawn with vertices B, A, C
draw_triangle(ax, E, D, F, color='red', linewidth=2, fill=True, fill_color='lightyellow')

# AE segment (BA extended to E)
ax.plot([A[0], E[0]], [A[1], E[1]], color='brown', linewidth=2, linestyle='-')

# DA and DG
ax.plot([D[0], A[0]], [D[1], A[1]], color='purple', linewidth=2)
ax.plot([D[0], G[0]], [D[1], G[1]], color='purple', linewidth=2, linestyle='--')

# EG and FG (dashed for emphasis)
ax.plot([E[0], G[0]], [E[1], G[1]], color='blue', linewidth=2, linestyle='--')
ax.plot([F[0], G[0]], [F[1], G[1]], color='green', linewidth=2, linestyle='--')

# Angle markers
draw_angle_arc(ax, C, A, B, radius=0.7, color='orange', label='36')
draw_angle_arc(ax, D, E, F, radius=0.5, color='red', label='36')
draw_angle_arc(ax, D, A, G, radius=0.6, color='purple', label='36')

# Labels
label_point(ax, B, 'B', offset=(-0.3, -0.3))
label_point(ax, A, 'A', offset=(0.3, -0.3))
label_point(ax, C, 'C', offset=(0, 0.3))
label_point(ax, D, 'D', offset=(0, -0.35))
label_point(ax, E, 'E', offset=(0.3, -0.3))
label_point(ax, F, 'F', offset=(0.3, 0.1))
label_point(ax, G, 'G', offset=(0.3, 0.3))

ax.set_xlim(-1, 8.5)
ax.set_ylim(-1, 7)
ax.axis('off')
ax.set_title('Step 1: Problem Setup - Isosceles Triangles', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('step1_setup.png', dpi=150, bbox_inches='tight')
plt.close()

# ========== Figure 2: Congruent Triangles ADE and GDF ==========
fig, ax = plt.subplots(1, 1, figsize=(10, 8))
ax.set_aspect('equal')

draw_triangle(ax, B, A, C, color='black', linewidth=1.5, fill=True, fill_color='lightgray', alpha=0.15)
draw_triangle(ax, E, D, F, color='red', linewidth=1.5, fill=True, fill_color='lightyellow', alpha=0.3)

# AE segment
ax.plot([A[0], E[0]], [A[1], E[1]], color='brown', linewidth=2, linestyle='-')

# Highlight DA and DG (rotation)
ax.plot([D[0], A[0]], [D[1], A[1]], color='purple', linewidth=3)
ax.plot([D[0], G[0]], [D[1], G[1]], color='purple', linewidth=3, linestyle='--')

# Highlight EG and FG
ax.plot([E[0], G[0]], [E[1], G[1]], color='blue', linewidth=2)
ax.plot([F[0], G[0]], [F[1], G[1]], color='green', linewidth=2)

# Label points
label_point(ax, B, 'B', offset=(-0.3, -0.3))
label_point(ax, A, 'A', offset=(0.3, -0.3))
label_point(ax, C, 'C', offset=(0, 0.3))
label_point(ax, D, 'D', offset=(0, -0.35))
label_point(ax, E, 'E', offset=(0.3, -0.3))
label_point(ax, F, 'F', offset=(0.3, 0.1))
label_point(ax, G, 'G', offset=(0.3, 0.3))

# Congruent triangles label
ax.text(3.75, -0.9, 'Triangle ADE ≅ Triangle GDF (SAS)', ha='center', fontsize=12,
        bbox=dict(boxstyle='round', facecolor='lightgreen', edgecolor='green'))

ax.set_xlim(-1, 8.5)
ax.set_ylim(-1, 7)
ax.axis('off')
ax.set_title('Step 2: Congruent Triangles ADE and GDF', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('step2_congruent.png', dpi=150, bbox_inches='tight')
plt.close()

# ========== Figure 3: Isosceles Triangle EGF ==========
fig, ax = plt.subplots(1, 1, figsize=(10, 8))
ax.set_aspect('equal')

# Draw triangle EGF highlighted
draw_triangle(ax, E, G, F, color='purple', linewidth=3, fill=True, fill_color='lavender')

# Draw other elements in gray
draw_triangle(ax, B, A, C, color='gray', linewidth=1, alpha=0.4)
draw_triangle(ax, E, D, F, color='gray', linewidth=1, alpha=0.4)
ax.plot([A[0], E[0]], [A[1], E[1]], color='gray', linewidth=1, alpha=0.4)
ax.plot([D[0], A[0]], [D[1], A[1]], color='gray', linewidth=1, alpha=0.4)
ax.plot([D[0], G[0]], [D[1], G[1]], color='gray', linewidth=1, alpha=0.4)

# Label points
label_point(ax, B, 'B', offset=(-0.3, -0.3))
label_point(ax, A, 'A', offset=(0.3, -0.3))
label_point(ax, C, 'C', offset=(0, 0.3))
label_point(ax, D, 'D', offset=(0, -0.35))
label_point(ax, E, 'E', offset=(0.3, -0.3))
label_point(ax, F, 'F', offset=(0.3, 0.1))
label_point(ax, G, 'G', offset=(0.3, 0.3))

# Mark angle FGE
draw_angle_arc(ax, G, E, F, radius=0.5, color='red', label='?')

ax.set_xlim(-1, 8.5)
ax.set_ylim(-1, 7)
ax.axis('off')
ax.set_title('Step 3: Isosceles Triangle EGF', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('step3_solution.png', dpi=150, bbox_inches='tight')
plt.close()

# ========== Figure 4: Summary ==========
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Left: Full configuration
ax = axes[0]
ax.set_aspect('equal')

draw_triangle(ax, B, A, C, color='black', linewidth=1.5)
draw_triangle(ax, E, D, F, color='red', linewidth=1.5, fill=True, fill_color='lightyellow', alpha=0.3)
ax.plot([A[0], E[0]], [A[1], E[1]], color='brown', linewidth=2)
ax.plot([D[0], A[0]], [D[1], A[1]], color='purple', linewidth=2)
ax.plot([D[0], G[0]], [D[1], G[1]], color='purple', linewidth=2, linestyle='--')
ax.plot([E[0], G[0]], [E[1], G[1]], color='blue', linewidth=2, linestyle='--')
ax.plot([F[0], G[0]], [F[1], G[1]], color='green', linewidth=2, linestyle='--')

label_point(ax, B, 'B', offset=(-0.25, -0.25))
label_point(ax, A, 'A', offset=(0.25, -0.25))
label_point(ax, C, 'C', offset=(0, 0.25))
label_point(ax, D, 'D', offset=(0, -0.3))
label_point(ax, E, 'E', offset=(0.25, -0.25))
label_point(ax, F, 'F', offset=(0.25, 0))
label_point(ax, G, 'G', offset=(0.25, 0.25))

ax.set_xlim(-1, 8.5)
ax.set_ylim(-1, 7)
ax.axis('off')
ax.set_title('Full Configuration', fontsize=12, fontweight='bold')

# Right: Triangle EGF
ax = axes[1]
ax.set_aspect('equal')

draw_triangle(ax, E, G, F, color='purple', linewidth=2, fill=True, fill_color='lavender')

label_point(ax, E, 'E', offset=(0, -0.3))
label_point(ax, G, 'G', offset=(0, 0.3))
label_point(ax, F, 'F', offset=(0.3, 0.1))

draw_angle_arc(ax, G, E, F, radius=0.5, color='red', label='36')

mid_x = (E[0] + G[0] + F[0]) / 3
mid_y = (E[1] + G[1] + F[1]) / 3
ax.text(mid_x, mid_y - 1.8, 'FGE = 36', ha='center', fontsize=14, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='gold', edgecolor='red'))

ax.set_xlim(3, 7.5)
ax.set_ylim(-1.5, 4)
ax.axis('off')
ax.set_title('Triangle EGF', fontsize=12, fontweight='bold')

plt.suptitle('Problem 009: Complete Solution', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('step4_summary.png', dpi=150, bbox_inches='tight')
plt.close()

print("All figures generated successfully!")