"""
Problem 008: Hand-in-hand Model with Equilateral Triangles
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Font configuration for Chinese text support
from matplotlib import font_manager
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(base_dir, '..', '..', 'font', 'STHeiti Medium.ttc')
font_manager.fontManager.addfont(font_path)
plt.rcParams['font.family'] = 'Heiti TC'
plt.rcParams['axes.unicode_minus'] = False

# ========== Utility Functions ==========
def draw_triangle(ax, A, B, C, color='black', linewidth=1.5, fill=False, fill_color='lightgray', alpha=0.3):
    """Draw a triangle with vertices A, B, C."""
    triangle = plt.Polygon([A, B, C], fill=fill, facecolor=fill_color, edgecolor=color, linewidth=linewidth, alpha=alpha)
    ax.add_patch(triangle)
    ax.plot([A[0], B[0]], [A[1], B[1]], color=color, linewidth=linewidth)
    ax.plot([B[0], C[0]], [B[1], C[1]], color=color, linewidth=linewidth)
    ax.plot([C[0], A[0]], [C[1], A[1]], color=color, linewidth=linewidth)

def draw_right_angle(ax, vertex, p1, p2, size=0.2, color='blue', linewidth=1.5):
    """Draw a right angle marker."""
    v = np.array(vertex)
    v1 = np.array(p1) - v
    v2 = np.array(p2) - v
    v1_unit = v1 / np.linalg.norm(v1) * size
    v2_unit = v2 / np.linalg.norm(v2) * size
    corner = v + v1_unit + v2_unit
    ax.plot([v[0] + v1_unit[0], corner[0]], [v[1] + v1_unit[1], corner[1]], color=color, linewidth=linewidth)
    ax.plot([corner[0], v[0] + v2_unit[0]], [corner[1], v[1] + v2_unit[1]], color=color, linewidth=linewidth)

def draw_angle_arc(ax, center, p1, p2, radius=0.3, color='blue', label=None, linewidth=1.5):
    """Draw an angle arc between two rays from center."""
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
    """Label a point with text."""
    ax.text(point[0] + offset[0], point[1] + offset[1], label, 
            ha='center', va='center', fontsize=fontsize, fontweight=fontweight)

def draw_line(ax, p1, p2, color='black', linewidth=1.5, linestyle='-'):
    """Draw a line between two points."""
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linewidth=linewidth, linestyle=linestyle)

# ========== Figure 1: Problem (1) - Basic Configuration ==========
fig, ax = plt.subplots(1, 1, figsize=(8, 7))
ax.set_aspect('equal')

# Define points for equilateral triangle ABC (side length 4)
A = np.array([2, 3.5])
B = np.array([0, 0])
C = np.array([4, 0])

# Point D on BC (closer to B)
D = np.array([1.2, 0])

# Construct equilateral triangle ADE (E on the right side)
# AD vector
AD = D - A
# Rotate AD by 60 degrees counterclockwise to get AE
angle_60 = np.radians(60)
rotation_matrix = np.array([[np.cos(angle_60), -np.sin(angle_60)],
                            [np.sin(angle_60), np.cos(angle_60)]])
AE_vec = rotation_matrix @ AD
E = A + AE_vec

# Draw triangles
draw_triangle(ax, A, B, C, color='black', linewidth=1.5)
draw_triangle(ax, A, D, E, color='red', linewidth=1.5)

# Draw CE
ax.plot([C[0], E[0]], [C[1], E[1]], color='blue', linewidth=2, linestyle='--')

# Draw BD (part of BC)
ax.plot([B[0], D[0]], [B[1], D[1]], color='green', linewidth=2)

# Label points
label_point(ax, A, 'A', offset=(0, 0.3))
label_point(ax, B, 'B', offset=(-0.25, -0.25))
label_point(ax, C, 'C', offset=(0.25, -0.25))
label_point(ax, D, 'D', offset=(0, -0.3))
label_point(ax, E, 'E', offset=(0.3, 0))

# Mark 60 degree angles
draw_angle_arc(ax, A, B, C, radius=0.5, color='purple', label='60°')
draw_angle_arc(ax, A, D, E, radius=0.5, color='purple', label='60°')

# Add legend for congruent triangles
ax.text(2, -1, '△ABD ≅ △ACE (SAS)', ha='center', fontsize=12, 
        bbox=dict(boxstyle='round', facecolor='lightyellow', edgecolor='orange'))

ax.set_xlim(-1, 5.5)
ax.set_ylim(-1.5, 5)
ax.axis('off')
ax.set_title('Step 1: Hand-in-hand Model - Parallel Lines', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('step1_parallel.png', dpi=150, bbox_inches='tight')
plt.close()

# ========== Figure 2: Problem (2) - Collinear Points ==========
fig, ax = plt.subplots(1, 1, figsize=(8, 7))
ax.set_aspect('equal')

# Define points - B, D, E collinear configuration
A = np.array([2, 3.5])
B = np.array([0, 0])
C = np.array([4, 0])

# D is positioned so that B-D-E are collinear
# Let's place D on BC extended
D = np.array([1.5, 0])

# For B, D, E to be collinear with ∠DEC = 60°, we need special positioning
# E should be such that ∠ADE = 60° (equilateral) and B-D-E collinear
# This means E is on the line extending from B through D

# Vector from D away from B (direction B->D extended)
DB_vec = B - D
DB_unit = DB_vec / np.linalg.norm(DB_vec)
# Length of AD
AD_len = np.linalg.norm(D - A)
# E is at distance AD from D, in direction opposite to B
E = D - DB_unit * AD_len

# Verify it's equilateral
AE_len = np.linalg.norm(E - A)
DE_len = np.linalg.norm(E - D)
print(f"AD={AD_len:.3f}, AE={AE_len:.3f}, DE={DE_len:.3f}")

# Draw triangles
draw_triangle(ax, A, B, C, color='black', linewidth=1.5)
draw_triangle(ax, A, D, E, color='red', linewidth=1.5, fill=True, fill_color='lightyellow')

# Draw CE and BD
ax.plot([C[0], E[0]], [C[1], E[1]], color='blue', linewidth=2, linestyle='--')
ax.plot([B[0], D[0]], [B[1], D[1]], color='green', linewidth=2)
ax.plot([D[0], E[0]], [D[1], E[1]], color='green', linewidth=2)

# Draw the line B-D-E
ax.plot([B[0], E[0]], [B[1], E[1]], color='orange', linewidth=3, alpha=0.5)

# Label points
label_point(ax, A, 'A', offset=(0, 0.3))
label_point(ax, B, 'B', offset=(-0.25, -0.25))
label_point(ax, C, 'C', offset=(0.25, -0.25))
label_point(ax, D, 'D', offset=(0, -0.35))
label_point(ax, E, 'E', offset=(0.3, 0.1))

# Mark angles
draw_angle_arc(ax, D, A, E, radius=0.5, color='purple', label='60°')
draw_angle_arc(ax, E, D, C, radius=0.5, color='darkgreen', label='60°')

# Add note
ax.text(2, -1, 'B, D, E are collinear', ha='center', fontsize=12,
        bbox=dict(boxstyle='round', facecolor='lightgreen', edgecolor='green'))

ax.set_xlim(-1, 6)
ax.set_ylim(-2, 5)
ax.axis('off')
ax.set_title('Step 2: Collinear Points B-D-E', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('step2_collinear.png', dpi=150, bbox_inches='tight')
plt.close()

# ========== Figure 3: Problem (3) - Construction with Auxiliary Triangle ==========
fig, ax = plt.subplots(1, 1, figsize=(9, 8))
ax.set_aspect('equal')

# Define equilateral triangle ABC in a more compact layout (similar to 008.jpg)
# Scaled to 0.8x of original size (BC from 6 to 4.8)
A = np.array([2.4, 3.5])  # x scaled to 0.8, y kept same
B = np.array([0, 0])
C = np.array([4.8, 0])

# Calculate E position such that:
# 1. CE = 2
# 2. Visual appearance is good

# Let's place E at a position that looks good relative to ABC
# A at (2.4, 3.5), B at (0,0), C at (4.8,0)

# Let's place E to the right and slightly above, similar to 008.jpg
# Move slightly left and up to make AE closer to AF
E = np.array([5.2, 2.8])

# Now scale to make CE=2
CE_actual = np.linalg.norm(E - C)
scale_factor = 2 / CE_actual
E = C + (E - C) * scale_factor

# Now compute F = point on BE such that BF=2
BE_vec = E - B
BE_unit = BE_vec / np.linalg.norm(BE_vec)
F = B + BE_unit * 2  # BF=2

# Verify lengths
CE_actual = np.linalg.norm(E - C)
BE_actual = np.linalg.norm(E - B)
BF_actual = np.linalg.norm(F - B)
FE_actual = np.linalg.norm(E - F)
AF_actual = np.linalg.norm(A - F)
AE_actual = np.linalg.norm(A - E)
EB_vec = B - E
EC_vec = C - E
angle_BEC = np.degrees(np.arccos(np.dot(EB_vec, EC_vec) / (np.linalg.norm(EB_vec) * np.linalg.norm(EC_vec))))
print(f"BE = {BE_actual:.2f}, CE = {CE_actual:.2f}, ∠BEC = {angle_BEC:.1f}°")
print(f"BF = {BF_actual:.2f}, FE = {FE_actual:.2f}")
print(f"AF = {AF_actual:.2f}, AE = {AE_actual:.2f}")

# Compute intersection point O of AC and BE
def line_intersection(p1, p2, p3, p4):
    x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
    denom = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    t = ((x1-x3)*(y3-y4) - (y1-y3)*(x3-x4)) / denom
    return p1 + t * (p2 - p1)

O = line_intersection(A, C, B, E)

# Draw main triangle ABC
draw_triangle(ax, A, B, C, color='black', linewidth=2)

# Draw lines from E
ax.plot([E[0], A[0]], [E[1], A[1]], color='blue', linewidth=1.5)
ax.plot([E[0], B[0]], [E[1], B[1]], color='blue', linewidth=1.5)
ax.plot([E[0], C[0]], [E[1], C[1]], color='blue', linewidth=1.5)

# Draw BF and FE on BE
ax.plot([B[0], F[0]], [B[1], F[1]], color='#E74C3C', linewidth=2)
ax.plot([F[0], E[0]], [F[1], E[1]], color='#3498DB', linewidth=2)

# Draw AF (not CF!) - this is the correct auxiliary line!
ax.plot([A[0], F[0]], [A[1], F[1]], color='#2ECC71', linewidth=2, linestyle='--')

# Label points
label_point(ax, A, 'A', offset=(0, 0.3))
label_point(ax, B, 'B', offset=(-0.3, -0.3))
label_point(ax, C, 'C', offset=(0.3, -0.3))
label_point(ax, E, 'E', offset=(0.35, 0.15))
label_point(ax, F, 'F', offset=(0.2, -0.2))
label_point(ax, O, 'O', offset=(0.25, -0.15))

# Mark angle BEC = 60°
draw_angle_arc(ax, E, B, C, radius=0.6, color='darkgreen', label='60°')

# Mark angle BAC = 60°
draw_angle_arc(ax, A, B, C, radius=0.5, color='#E74C3C', label='60°')

# Mark angle FAE = 60° (will be proven)
draw_angle_arc(ax, A, F, E, radius=0.4, color='#2ECC71', label='60°')

# Add length labels
ax.text((A[0]+E[0])/2 + 0.3, (A[1]+E[1])/2, 'AE=3', fontsize=11, color='blue', fontweight='bold')
ax.text((E[0]+C[0])/2 + 0.2, (E[1]+C[1])/2, 'CE=2', fontsize=11, color='blue', fontweight='bold')
# Calculate perpendicular offsets for labels relative to BE direction
BE_dir = E - B
perp_vec = np.array([-BE_dir[1], BE_dir[0]])  # perpendicular to BE
perp_unit = perp_vec / np.linalg.norm(perp_vec)

bf_mid = (B + F) / 2
fe_mid = (F + E) / 2
ax.text(bf_mid[0] - perp_unit[0]*0.3, bf_mid[1] - perp_unit[1]*0.3, 'BF=2',
        fontsize=11, color='#E74C3C', fontweight='bold', ha='center', va='center')
ax.text(fe_mid[0] + perp_unit[0]*0.3, fe_mid[1] + perp_unit[1]*0.3, 'FE=3',
        fontsize=11, color='#3498DB', fontweight='bold', ha='center', va='center')
ax.text((A[0]+F[0])/2 - 0.3, (A[1]+F[1])/2 + 0.1, 'AF=3', fontsize=11, color='#2ECC71', fontweight='bold')

# Add solution note
ax.text(2.4, -1.0, 'BE = BF + FE = 2 + 3 = 5', ha='center', fontsize=14, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='lightblue', edgecolor='blue'))

ax.set_xlim(-1, 7.5)
ax.set_ylim(-1.5, 5)
ax.axis('off')
ax.set_title('Step 3: Auxiliary Construction - Finding BE', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('step3_solution.png', dpi=150, bbox_inches='tight')
plt.close()

# ========== Figure 4: Summary - All Configurations ==========
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Subplot 1: Problem (1)
ax = axes[0]
ax.set_aspect('equal')
A = np.array([2, 3]); B = np.array([0, 0]); C = np.array([4, 0])
D = np.array([1.2, 0])
AD = D - A
rotation_matrix = np.array([[np.cos(angle_60), -np.sin(angle_60)],
                            [np.sin(angle_60), np.cos(angle_60)]])
AE_vec = rotation_matrix @ AD
E = A + AE_vec
draw_triangle(ax, A, B, C, color='black', linewidth=1.5)
draw_triangle(ax, A, D, E, color='red', linewidth=1.5)
ax.plot([C[0], E[0]], [C[1], E[1]], color='blue', linewidth=2, linestyle='--')
label_point(ax, A, 'A', offset=(0, 0.25))
label_point(ax, B, 'B', offset=(-0.2, -0.2))
label_point(ax, C, 'C', offset=(0.2, -0.2))
label_point(ax, D, 'D', offset=(0, -0.25))
label_point(ax, E, 'E', offset=(0.25, 0))
ax.set_xlim(-0.5, 5)
ax.set_ylim(-1, 4.5)
ax.axis('off')
ax.set_title('(1) AB // CE', fontsize=12, fontweight='bold')

# Subplot 2: Problem (2)
ax = axes[1]
ax.set_aspect('equal')
A = np.array([2, 3.5]); B = np.array([0, 0]); C = np.array([4, 0])
D = np.array([1.5, 0])
DB_vec = B - D
DB_unit = DB_vec / np.linalg.norm(DB_vec)
AD_len = np.linalg.norm(D - A)
E = D - DB_unit * AD_len
draw_triangle(ax, A, B, C, color='black', linewidth=1.5)
draw_triangle(ax, A, D, E, color='red', linewidth=1.5)
ax.plot([C[0], E[0]], [C[1], E[1]], color='blue', linewidth=2, linestyle='--')
ax.plot([B[0], E[0]], [B[1], E[1]], color='orange', linewidth=3, alpha=0.5)
label_point(ax, A, 'A', offset=(0, 0.25))
label_point(ax, B, 'B', offset=(-0.2, -0.2))
label_point(ax, C, 'C', offset=(0.2, -0.2))
label_point(ax, D, 'D', offset=(0, -0.3))
label_point(ax, E, 'E', offset=(0.25, 0))
ax.set_xlim(-0.5, 5.5)
ax.set_ylim(-1.5, 4.5)
ax.axis('off')
ax.set_title('(2) B, D, E Collinear', fontsize=12, fontweight='bold')

# Subplot 3: Problem (3)
ax = axes[2]
ax.set_aspect('equal')
# Scaled to 0.8x of original size (BC from 5 to 4)
A = np.array([2.0, 2.8]); B = np.array([0, 0]); C = np.array([4.0, 0])

# Place E similar to 008.jpg - above and to the right
# Adjusted for 0.8x scaled triangle ABC
E = np.array([4.4, 2.3])
CE_actual = np.linalg.norm(E - C)
scale_factor = 2 / CE_actual
E = C + (E - C) * scale_factor

BE_vec = E - B
BE_unit = BE_vec / np.linalg.norm(BE_vec)
F = B + BE_unit * 2  # BF=2

draw_triangle(ax, A, B, C, color='black', linewidth=1.5)
ax.plot([E[0], A[0]], [E[1], A[1]], color='blue', linewidth=1.5)
ax.plot([E[0], B[0]], [E[1], B[1]], color='blue', linewidth=1.5)
ax.plot([E[0], C[0]], [E[1], C[1]], color='blue', linewidth=1.5)
ax.plot([A[0], F[0]], [A[1], F[1]], color='green', linewidth=2, linestyle='--')
label_point(ax, A, 'A', offset=(0, 0.25))
label_point(ax, B, 'B', offset=(-0.2, -0.2))
label_point(ax, C, 'C', offset=(0.2, -0.2))
label_point(ax, E, 'E', offset=(0.25, 0.1))
label_point(ax, F, 'F', offset=(0.2, -0.2))
ax.text(2.0, -0.8, 'BE = 5', ha='center', fontsize=11, fontweight='bold')
ax.set_xlim(-0.8, 6.5)
ax.set_ylim(-1.2, 4)
ax.axis('off')
ax.set_title('(3) BE = 5', fontsize=12, fontweight='bold')

plt.suptitle('Hand-in-hand Model: Complete Solution', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('step4_summary.png', dpi=150, bbox_inches='tight')
plt.close()

# ========== Figure 5: Step 5 - Summary Illustration ==========
fig, ax = plt.subplots(figsize=(12, 9))
ax.set_aspect('equal')
ax.set_xlim(-2, 14)
ax.set_ylim(-1.5, 8)
ax.axis('off')

# Background colors for sections
bg_colors = ['#dbeafe', '#dcfce7', '#f3e8ff', '#fed7aa']
section_titles = ['手拉手模型\nHand-in-hand', '三点共线\nCollinearity', '辅助线\nAuxiliary', '计算方法\nCalculation']
section_x = [1, 4.5, 8, 11.5]

for i, (x, color, title) in enumerate(zip(section_x, bg_colors, section_titles)):
    bg = patches.Rectangle((x-1.5, 1.5), 3, 5, color=color, alpha=0.3, ec=color, lw=2)
    ax.add_patch(bg)
    ax.text(x, 5.7, title, ha='center', va='center', fontsize=11, fontweight='bold', color='#1f2937')

# Draw hand-in-hand model (Section 1)
x1, y1 = 1, 3.5
# Triangle 1 - ABC
A1 = np.array([x1, y1 + 1.2])
B1 = np.array([x1 - 1, y1 - 0.6])
C1 = np.array([x1 + 1, y1 - 0.6])
draw_triangle(ax, A1, B1, C1, color='#1e40af', linewidth=2)
label_point(ax, A1, 'A', offset=(0, 0.2))
label_point(ax, B1, 'B', offset=(-0.2, -0.2))
label_point(ax, C1, 'C', offset=(0.2, -0.2))

# Triangle 2 - ADE
AD1 = np.array([x1 - 0.5, y1 - 0.4]) - A1
theta = np.radians(60)
rot = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
AE1 = rot @ AD1
D1 = A1 + AD1
E1 = A1 + AE1
draw_triangle(ax, A1, D1, E1, color='#dc2626', linewidth=2)
label_point(ax, D1, 'D', offset=(-0.2, -0.2))
label_point(ax, E1, 'E', offset=(0.2, -0.2))

# Rotation arrow
arc1 = patches.FancyArrowPatch(B1, E1, connectionstyle="arc3,rad=-0.8", arrowstyle='->,head_width=0.3', color='#9333ea', linewidth=2)
ax.add_patch(arc1)
ax.text(x1, y1 - 1.3, '旋转60°', ha='center', fontsize=9, fontweight='bold', color='#7c3aed')

# Draw collinearity (Section 2)
x2, y2 = 4.5, 3.5
# Three points on line
p_col1 = np.array([x2 - 1.2, y2])
p_col2 = np.array([x2, y2])
p_col3 = np.array([x2 + 1.2, y2])
ax.plot([p_col1[0], p_col3[0]], [p_col1[1], p_col3[1]], color='#065f46', linewidth=3, alpha=0.6)
label_point(ax, p_col1, 'B', offset=(0, 0.2))
label_point(ax, p_col2, 'D', offset=(0, 0.2))
label_point(ax, p_col3, 'E', offset=(0, 0.2))

# 180 degree arc
arc_col = patches.Arc(p_col2, 0.8, 0.8, angle=0, theta1=0, theta2=180, color='#059669', linewidth=2)
ax.add_patch(arc_col)
ax.text(x2, y2 + 0.5, '180°', ha='center', fontsize=10, fontweight='bold', color='#047857')
ax.text(x2, y2 - 1.3, '平角=180°', ha='center', fontsize=9, fontweight='bold', color='#065f46')

# Draw auxiliary line (Section 3)
x3, y3 = 8, 3.5
# Triangle ABC
A3 = np.array([x3, y3 + 1])
B3 = np.array([x3 - 1, y3 - 0.8])
C3 = np.array([x3 + 1, y3 - 0.8])
draw_triangle(ax, A3, B3, C3, color='#7c3aed', linewidth=2)
label_point(ax, A3, 'A', offset=(0, 0.2))
label_point(ax, B3, 'B', offset=(-0.2, -0.2))
label_point(ax, C3, 'C', offset=(0.2, -0.2))

# Point E and F on BE
E3 = np.array([x3 + 1.6, y3 + 0.6])
F3 = np.array([x3 + 0.6, y3 - 0.2])
ax.plot([B3[0], E3[0]], [B3[1], E3[1]], color='#c026d3', linewidth=2)
ax.plot([A3[0], F3[0]], [A3[1], F3[1]], color='#22c55e', linewidth=2, linestyle='--')
label_point(ax, E3, 'E', offset=(0.2, 0))
label_point(ax, F3, 'F', offset=(0.2, -0.2))

ax.text(x3, y3 - 1.3, '截长补短', ha='center', fontsize=9, fontweight='bold', color='#7c3aed')

# Draw calculation method (Section 4)
x4, y4 = 11.5, 3.5
# Right triangle 30-60-90
rt_A = np.array([x4, y4 + 1])
rt_B = np.array([x4 - 0.8, y4 - 0.6])
rt_C = np.array([x4 + 0.8, y4 - 0.6])
draw_triangle(ax, rt_A, rt_B, rt_C, color='#c2410c', linewidth=2)
draw_right_angle(ax, rt_C, rt_A, rt_B, size=0.25, color='#ea580c')

label_point(ax, rt_A, '30°', offset=(0, 0.25))
label_point(ax, rt_B, '60°', offset=(-0.3, -0.2))
label_point(ax, rt_C, '', offset=(0.25, -0.2))

# Formula a²+b²=c²
ax.text(x4, y4 - 1.3, 'a²+b²=c²', ha='center', fontsize=10, fontweight='bold', color='#c2410c')

# Main title
ax.text(7, 7.2, '手拉手模型解题技巧总结\nSummary of Hand-in-hand Problem Solving', 
        ha='center', va='center', fontsize=16, fontweight='bold', color='#1f2937')

plt.tight_layout()
plt.savefig('step5_summary_illustration.png', dpi=150, bbox_inches='tight')
plt.close()

print("All figures generated successfully!")
