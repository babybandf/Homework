"""
Problem 005: Prove PA + PB = PC
In triangle ABC, angle ABC = angle BAC = 70 degrees, P is inside the triangle,
angle PAB = 40 degrees, angle PBA = 20 degrees. Prove PA + PB = PC.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# ========== Utility Functions ==========

def draw_angle_arc(ax, center, p1, p2, radius=0.3, color='blue', label=None, fontsize=10):
    """Draw an angle arc between two rays from center.
    center: vertex of the angle
    p1: point on one ray
    p2: point on the other ray
    """
    angle1 = np.degrees(np.arctan2(p1[1]-center[1], p1[0]-center[0]))
    angle2 = np.degrees(np.arctan2(p2[1]-center[1], p2[0]-center[0]))
    if angle2 < angle1:
        angle1, angle2 = angle2, angle1
    if angle2 - angle1 > 180:
        angle1, angle2 = angle2, angle1 + 360
    arc = patches.Arc(center, 2*radius, 2*radius, angle=0,
                      theta1=angle1, theta2=angle2, color=color, linewidth=1.5)
    ax.add_patch(arc)
    if label:
        mid_angle = np.radians((angle1 + angle2) / 2)
        label_r = radius + 0.2
        ax.text(center[0] + label_r * np.cos(mid_angle),
                center[1] + label_r * np.sin(mid_angle),
                label, ha='center', va='center', fontsize=fontsize, color=color)


def mark_equal_sides(ax, p1, p2, num_marks=1, color='red'):
    """Mark equal sides with tick marks at midpoint."""
    mid = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2)
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = np.sqrt(dx**2 + dy**2)
    perp_x = -dy / length * 0.12
    perp_y = dx / length * 0.12
    along_x = dx / length * 0.08
    along_y = dy / length * 0.08
    for i in range(num_marks):
        offset = (i - (num_marks-1)/2) * 0.1
        cx = mid[0] + offset * along_x / 0.08
        cy = mid[1] + offset * along_y / 0.08
        ax.plot([cx - perp_x, cx + perp_x], [cy - perp_y, cy + perp_y],
                color=color, linewidth=2)


def label_point(ax, point, name, offset_dir, offset_dist=0.3, fontsize=14):
    """Label a point with offset in a given direction (angle in degrees)."""
    rad = np.radians(offset_dir)
    ax.text(point[0] + offset_dist * np.cos(rad),
            point[1] + offset_dist * np.sin(rad),
            name, ha='center', va='center', fontsize=fontsize, fontweight='bold')


# ========== Compute Key Points ==========

# Triangle ABC: AB = 6, angle A = angle B = 70 degrees, angle C = 40 degrees
AB = 6.0
A = np.array([0.0, 0.0])
B = np.array([AB, 0.0])
# C is on perpendicular bisector of AB (isosceles)
h = (AB / 2) * np.tan(np.radians(70))
C = np.array([AB / 2, h])

# Point P: angle PAB = 40 deg, angle PBA = 20 deg
# Ray from A at 40 degrees from AB
# Ray from B at 160 degrees from positive x-axis (180 - 20 = 160)
# Solve intersection
angle_AP = np.radians(40)
angle_BP = np.radians(180 - 20)

# Parametric: A + t*(cos40, sin40) = B + s*(cos160, sin160)
# t*cos40 = 6 + s*cos160
# t*sin40 = s*sin160
# t = s*sin160/sin40
sin40 = np.sin(np.radians(40))
sin160 = np.sin(np.radians(160))  # = sin20
cos40 = np.cos(np.radians(40))
cos160 = np.cos(np.radians(160))  # = -cos20

s_P = AB / (sin160/sin40 * cos40 - cos160)
t_P = s_P * sin160 / sin40
P = A + t_P * np.array([np.cos(angle_AP), np.sin(angle_AP)])

PA = np.linalg.norm(P - A)
PB = np.linalg.norm(P - B)

# Point N: on BP extension past P, PN = PA
BP_dir = (P - B) / np.linalg.norm(P - B)
N = P + PA * BP_dir

# Point M: rotate N around C by 40 degrees counterclockwise (maps A->B, N->M)
rot_angle = np.radians(40)
CN = N - C
CM_x = CN[0] * np.cos(rot_angle) - CN[1] * np.sin(rot_angle)
CM_y = CN[0] * np.sin(rot_angle) + CN[1] * np.cos(rot_angle)
M = C + np.array([CM_x, CM_y])

# Point H: foot of altitude from C to AB (midpoint of AB for isosceles)
H = np.array([AB / 2, 0.0])

# Point K: intersection of CH with PM (should be at x = AB/2, y = P[1])
K = np.array([AB / 2, P[1]])

# Verify key properties
print(f"A = ({A[0]:.3f}, {A[1]:.3f})")
print(f"B = ({B[0]:.3f}, {B[1]:.3f})")
print(f"C = ({C[0]:.3f}, {C[1]:.3f})")
print(f"P = ({P[0]:.3f}, {P[1]:.3f})")
print(f"N = ({N[0]:.3f}, {N[1]:.3f})")
print(f"M = ({M[0]:.3f}, {M[1]:.3f})")
print(f"PA = {PA:.4f}, PB = {PB:.4f}, PC = {np.linalg.norm(P - C):.4f}")
print(f"PA + PB = {PA + PB:.4f}")
print(f"AN = {np.linalg.norm(N - A):.4f}, PN = {PA:.4f} (equilateral check)")
print(f"NC = {np.linalg.norm(N - C):.4f}, PC = {np.linalg.norm(P - C):.4f} (NC=PC check)")
print(f"BM = {np.linalg.norm(M - B):.4f}, AP = {PA:.4f} (BM=AP check)")
print(f"PM = {np.linalg.norm(M - P):.4f}, BM = {np.linalg.norm(M - B):.4f} (PM=BM check)")
print(f"NB = {np.linalg.norm(N - B):.4f}, NC = {np.linalg.norm(N - C):.4f} (NB=NC check)")
print()

# ========== Figure 1: Problem Setup ==========

fig, ax = plt.subplots(1, 1, figsize=(8, 8))
ax.set_aspect('equal')

# Draw triangle ABC
triangle = plt.Polygon([A, B, C], fill=False, edgecolor='#2c3e50', linewidth=2)
ax.add_patch(triangle)

# Draw PA, PB, PC
ax.plot([P[0], A[0]], [P[1], A[1]], color='#e74c3c', linewidth=1.5, linestyle='--')
ax.plot([P[0], B[0]], [P[1], B[1]], color='#3498db', linewidth=1.5, linestyle='--')
ax.plot([P[0], C[0]], [P[1], C[1]], color='#27ae60', linewidth=1.5, linestyle='--')

# Mark point P
ax.plot(*P, 'ko', markersize=5)

# Label vertices
label_point(ax, A, 'A', 225)
label_point(ax, B, 'B', 315)
label_point(ax, C, 'C', 90)
label_point(ax, P, 'P', 180, offset_dist=0.35)

# Mark angles
draw_angle_arc(ax, A, B, P, radius=0.6, color='#e74c3c', label='40°')  # ∠PAB at A
draw_angle_arc(ax, B, P, A, radius=0.6, color='#3498db', label='20°')  # ∠PBA at B
draw_angle_arc(ax, A, B, C, radius=0.9, color='#8e44ad', label='70°')  # ∠BAC at A (full)

# Set limits
margin = 1.0
all_x = [A[0], B[0], C[0], P[0]]
all_y = [A[1], B[1], C[1], P[1]]
ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
ax.axis('off')
ax.set_title('Step 1: Problem Setup', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('step1_problem.png', dpi=150, bbox_inches='tight')
plt.close()
print("Figure 1 saved: step1_problem.png")

# ========== Figure 1b: Angle Analysis ==========

fig, ax = plt.subplots(1, 1, figsize=(8, 8))
ax.set_aspect('equal')

# Draw triangle ABC
triangle = plt.Polygon([A, B, C], fill=False, edgecolor='#2c3e50', linewidth=2)
ax.add_patch(triangle)

# Draw PA, PB, PC
ax.plot([P[0], A[0]], [P[1], A[1]], color='#e74c3c', linewidth=1.5, linestyle='--')
ax.plot([P[0], B[0]], [P[1], B[1]], color='#3498db', linewidth=1.5, linestyle='--')
ax.plot([P[0], C[0]], [P[1], C[1]], color='#27ae60', linewidth=1.5, linestyle='--')

# Mark point P
ax.plot(*P, 'ko', markersize=5)

# Label vertices
label_point(ax, A, 'A', 225)
label_point(ax, B, 'B', 315)
label_point(ax, C, 'C', 90)
label_point(ax, P, 'P', 180, offset_dist=0.35)

# Mark ALL computed angles
draw_angle_arc(ax, A, B, P, radius=0.6, color='#e74c3c', label='40°')    # ∠PAB
draw_angle_arc(ax, A, P, C, radius=0.9, color='#e74c3c', label='30°')    # ∠PAC
draw_angle_arc(ax, B, P, A, radius=0.6, color='#3498db', label='20°')    # ∠PBA
draw_angle_arc(ax, B, P, C, radius=1.2, color='#3498db', label='50°')   # ∠PBC
draw_angle_arc(ax, C, A, B, radius=0.5, color='#8e44ad', label='40°')    # ∠ACB
draw_angle_arc(ax, P, B, A, radius=0.4, color='#e67e22', label='120°')   # ∠APB

# Mark equal sides AC = BC
mark_equal_sides(ax, A, C, num_marks=1, color='#27ae60')
mark_equal_sides(ax, B, C, num_marks=1, color='#27ae60')

# Set limits
all_x = [A[0], B[0], C[0], P[0]]
all_y = [A[1], B[1], C[1], P[1]]
ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
ax.axis('off')
ax.set_title('Step 1b: Angle Analysis', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('step1b_angles.png', dpi=150, bbox_inches='tight')
plt.close()
print("Figure 1b saved: step1b_angles.png")

# ========== Figure 2: Auxiliary Construction (Point N, Equilateral Triangle) ==========

fig, ax = plt.subplots(1, 1, figsize=(8, 8))
ax.set_aspect('equal')

# Draw triangle ABC
triangle = plt.Polygon([A, B, C], fill=False, edgecolor='#2c3e50', linewidth=2)
ax.add_patch(triangle)

# Draw PA, PB, PC
ax.plot([P[0], A[0]], [P[1], A[1]], color='#2c3e50', linewidth=1.5)
ax.plot([P[0], B[0]], [P[1], B[1]], color='#2c3e50', linewidth=1.5)
ax.plot([P[0], C[0]], [P[1], C[1]], color='#2c3e50', linewidth=1.5)

# Draw BP extension to N
ax.plot([B[0], N[0]], [B[1], N[1]], color='#9b59b6', linewidth=1.5, linestyle='--')

# Draw equilateral triangle APN
equi_tri = plt.Polygon([A, P, N], fill=True, facecolor='#f3e5f5', edgecolor='#9b59b6', linewidth=2, alpha=0.5)
ax.add_patch(equi_tri)

# Draw AN, CN
ax.plot([A[0], N[0]], [A[1], N[1]], color='#9b59b6', linewidth=2)
ax.plot([C[0], N[0]], [C[1], N[1]], color='#e67e22', linewidth=1.5, linestyle='--')

# Mark points
for pt in [A, B, C, P, N]:
    ax.plot(*pt, 'ko', markersize=5)

# Labels
label_point(ax, A, 'A', 225)
label_point(ax, B, 'B', 315)
label_point(ax, C, 'C', 90)
label_point(ax, P, 'P', 0, offset_dist=0.35)
label_point(ax, N, 'N', 135)

# Mark equal sides of equilateral triangle
mark_equal_sides(ax, A, P, num_marks=1, color='#9b59b6')
mark_equal_sides(ax, P, N, num_marks=1, color='#9b59b6')
mark_equal_sides(ax, A, N, num_marks=1, color='#9b59b6')

# Mark 60 degree angle at P
draw_angle_arc(ax, P, A, N, radius=0.4, color='#9b59b6', label='60°')  # ∠APN at P

# Set limits
all_x = [A[0], B[0], C[0], P[0], N[0]]
all_y = [A[1], B[1], C[1], P[1], N[1]]
ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
ax.axis('off')
ax.set_title('Step 2: Equilateral Triangle APN (PN = PA)', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('step2_auxiliary.png', dpi=150, bbox_inches='tight')
plt.close()
print("Figure 2 saved: step2_auxiliary.png")

# ========== Figure 3: Congruent Triangles NAC ≅ PAC ==========

fig, ax = plt.subplots(1, 1, figsize=(8, 8))
ax.set_aspect('equal')

# Draw triangle ABC
triangle = plt.Polygon([A, B, C], fill=False, edgecolor='#2c3e50', linewidth=2)
ax.add_patch(triangle)

# Highlight triangle NAC
tri_NAC = plt.Polygon([N, A, C], fill=True, facecolor='#bbdefb', edgecolor='#1565c0', linewidth=2, alpha=0.4)
ax.add_patch(tri_NAC)

# Highlight triangle PAC
tri_PAC = plt.Polygon([P, A, C], fill=True, facecolor='#fff9c4', edgecolor='#f57f17', linewidth=2, alpha=0.4)
ax.add_patch(tri_PAC)

# Draw lines
ax.plot([P[0], B[0]], [P[1], B[1]], color='#2c3e50', linewidth=1)
ax.plot([B[0], N[0]], [B[1], N[1]], color='#2c3e50', linewidth=1, linestyle='--')
ax.plot([A[0], N[0]], [A[1], N[1]], color='#1565c0', linewidth=2)
ax.plot([C[0], N[0]], [C[1], N[1]], color='#1565c0', linewidth=2)
ax.plot([P[0], C[0]], [P[1], C[1]], color='#f57f17', linewidth=2)
ax.plot([P[0], A[0]], [P[1], A[1]], color='#2c3e50', linewidth=1.5)

# Mark points
for pt in [A, B, C, P, N]:
    ax.plot(*pt, 'ko', markersize=5)

# Labels
label_point(ax, A, 'A', 270)
label_point(ax, B, 'B', 315)
label_point(ax, C, 'C', 90)
label_point(ax, P, 'P', 0, offset_dist=0.35)
label_point(ax, N, 'N', 135)

# Mark equal sides: AN = AP
mark_equal_sides(ax, A, N, num_marks=2, color='#e74c3c')
mark_equal_sides(ax, A, P, num_marks=2, color='#e74c3c')

# Mark angles at A
draw_angle_arc(ax, A, N, C, radius=0.7, color='#1565c0', label='30°')  # ∠NAC at A
draw_angle_arc(ax, A, C, P, radius=0.5, color='#f57f17', label='30°')  # ∠PAC at A... wait

# Actually ∠PAC means angle at A between AP and AC. Let me recalculate the correct call.
# ∠NAC at A: angle between AN and AC -> draw_angle_arc(ax, A, N, C, ...)
# ∠PAC at A: angle between AP and AC -> draw_angle_arc(ax, A, P, C, ...)
# But wait, N is below AC and P is below AC too. Let me check positions.
# A=(0,0), N=(-0.41, 2.33), C=(3, 8.24), P=(1.82, 1.52)
# angle from A to N: atan2(2.33, -0.41) ≈ 100°
# angle from A to C: atan2(8.24, 3) ≈ 70°
# angle from A to P: atan2(1.52, 1.82) ≈ 40°
# So ∠NAC = 100° - 70° = 30° ✓
# ∠PAC = 70° - 40° = 30° ✓

# Set limits
all_x = [A[0], B[0], C[0], P[0], N[0]]
all_y = [A[1], B[1], C[1], P[1], N[1]]
ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
ax.axis('off')
ax.set_title('Step 3: Triangle NAC ≅ Triangle PAC (SAS)', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('step3_congruent1.png', dpi=150, bbox_inches='tight')
plt.close()
print("Figure 3 saved: step3_congruent1.png")

# ========== Figure 4: Rotation and Point M ==========

fig, ax = plt.subplots(1, 1, figsize=(8, 8))
ax.set_aspect('equal')

# Draw triangle ABC
triangle = plt.Polygon([A, B, C], fill=False, edgecolor='#2c3e50', linewidth=2)
ax.add_patch(triangle)

# Draw PA, PB, PC
ax.plot([P[0], A[0]], [P[1], A[1]], color='#2c3e50', linewidth=1.5)
ax.plot([P[0], B[0]], [P[1], B[1]], color='#2c3e50', linewidth=1.5)
ax.plot([P[0], C[0]], [P[1], C[1]], color='#2c3e50', linewidth=1.5)

# Draw BP extension to N
ax.plot([B[0], N[0]], [B[1], N[1]], color='#2c3e50', linewidth=1, linestyle='--')

# Draw CN, CM
ax.plot([C[0], N[0]], [C[1], N[1]], color='#1565c0', linewidth=1.5, linestyle='--')
ax.plot([C[0], M[0]], [C[1], M[1]], color='#e67e22', linewidth=1.5, linestyle='--')

# Draw AN
ax.plot([A[0], N[0]], [A[1], N[1]], color='#2c3e50', linewidth=1, linestyle='--')

# Draw BM
ax.plot([B[0], M[0]], [B[1], M[1]], color='#e67e22', linewidth=2)

# Draw PM
ax.plot([P[0], M[0]], [P[1], M[1]], color='#27ae60', linewidth=2)

# Highlight rotation: triangle CAN (blue) and triangle CBM (orange)
tri_CAN = plt.Polygon([C, A, N], fill=True, facecolor='#bbdefb', edgecolor='#1565c0', linewidth=1.5, alpha=0.3)
ax.add_patch(tri_CAN)
tri_CBM = plt.Polygon([C, B, M], fill=True, facecolor='#fff9c4', edgecolor='#f57f17', linewidth=1.5, alpha=0.3)
ax.add_patch(tri_CBM)

# Mark points
for pt in [A, B, C, P, N, M]:
    ax.plot(*pt, 'ko', markersize=5)

# Labels
label_point(ax, A, 'A', 225)
label_point(ax, B, 'B', 315)
label_point(ax, C, 'C', 90)
label_point(ax, P, 'P', 270, offset_dist=0.35)
label_point(ax, N, 'N', 135)
label_point(ax, M, 'M', 45)

# Mark rotation angle at C
draw_angle_arc(ax, C, N, M, radius=0.5, color='#e67e22', label='40°')  # ∠NCM at C

# Mark equal CN, CM, CP
mark_equal_sides(ax, C, N, num_marks=3, color='#e74c3c')
mark_equal_sides(ax, C, M, num_marks=3, color='#e74c3c')
mark_equal_sides(ax, C, P, num_marks=3, color='#e74c3c')

# Set limits
all_x = [A[0], B[0], C[0], P[0], N[0], M[0]]
all_y = [A[1], B[1], C[1], P[1], N[1], M[1]]
ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
ax.axis('off')
ax.set_title('Step 4: Rotation - Triangle CAN to Triangle CBM', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('step4_rotation.png', dpi=150, bbox_inches='tight')
plt.close()
print("Figure 4 saved: step4_rotation.png")

# ========== Figure 5: PM // AB and Isosceles Triangle BPM ==========

fig, ax = plt.subplots(1, 1, figsize=(8, 8))
ax.set_aspect('equal')

# Draw triangle ABC
triangle = plt.Polygon([A, B, C], fill=False, edgecolor='#2c3e50', linewidth=2)
ax.add_patch(triangle)

# Draw PA, PB
ax.plot([P[0], A[0]], [P[1], A[1]], color='#2c3e50', linewidth=1.5)
ax.plot([P[0], B[0]], [P[1], B[1]], color='#2c3e50', linewidth=1.5)

# Draw CP, CM
ax.plot([C[0], P[0]], [C[1], P[1]], color='#e67e22', linewidth=1.5, linestyle='--')
ax.plot([C[0], M[0]], [C[1], M[1]], color='#e67e22', linewidth=1.5, linestyle='--')

# Draw AN, PN, CN
ax.plot([A[0], N[0]], [A[1], N[1]], color='#9b59b6', linewidth=1.5, linestyle='--')
ax.plot([P[0], N[0]], [P[1], N[1]], color='#9b59b6', linewidth=1.5, linestyle='--')
ax.plot([C[0], N[0]], [C[1], N[1]], color='#9b59b6', linewidth=1.5, linestyle='--')

# Draw PM, BM
ax.plot([P[0], M[0]], [P[1], M[1]], color='#27ae60', linewidth=2.5)
ax.plot([B[0], M[0]], [B[1], M[1]], color='#27ae60', linewidth=2.5)

# Draw CH (altitude)
ax.plot([C[0], H[0]], [C[1], H[1]], color='#9b59b6', linewidth=1.5, linestyle='-.')

# Draw dashed extension lines to show PM // AB
extend = 0.5
ax.plot([P[0] - extend, M[0] + extend], [P[1], M[1]], color='#27ae60', linewidth=1, linestyle=':')

# Highlight triangle BPM
tri_BPM = plt.Polygon([B, P, M], fill=True, facecolor='#c8e6c9', edgecolor='#27ae60', linewidth=2, alpha=0.4)
ax.add_patch(tri_BPM)

# Mark points
for pt in [A, B, C, P, M, H, N]:
    ax.plot(*pt, 'ko', markersize=5)

# Labels
label_point(ax, A, 'A', 225)
label_point(ax, B, 'B', 315)
label_point(ax, C, 'C', 90)
label_point(ax, P, 'P', 180, offset_dist=0.35)
label_point(ax, M, 'M', 0, offset_dist=0.35)
label_point(ax, H, 'H', 270)
label_point(ax, N, 'N', 135)

# Mark parallel arrows
mid_AB = (A + B) / 2
mid_PM = (P + M) / 2
ax.annotate('', xy=(mid_AB[0]+0.3, mid_AB[1]), xytext=(mid_AB[0]-0.3, mid_AB[1]),
            arrowprops=dict(arrowstyle='->', color='#27ae60', lw=1.5))
ax.annotate('', xy=(mid_PM[0]+0.3, mid_PM[1]), xytext=(mid_PM[0]-0.3, mid_PM[1]),
            arrowprops=dict(arrowstyle='->', color='#27ae60', lw=1.5))

# Mark angles in triangle BPM
draw_angle_arc(ax, B, P, M, radius=0.5, color='#27ae60', label='20°')  # ∠MBP at B
draw_angle_arc(ax, P, M, B, radius=0.5, color='#27ae60', label='20°')  # ∠MPB at P
draw_angle_arc(ax, B, A, P, radius=0.8, color='#f39c12', label='20°')  # ∠PBA at B

# Mark equal sides PM = BM
mark_equal_sides(ax, P, M, num_marks=2, color='#e74c3c')
mark_equal_sides(ax, B, M, num_marks=2, color='#e74c3c')

# Right angle mark at K (CH ⊥ PM)
sq_size = 0.15
ax.plot([K[0], K[0]+sq_size, K[0]+sq_size, K[0]], 
        [K[1], K[1], K[1]+sq_size, K[1]+sq_size], color='#9b59b6', linewidth=1.5)

# Set limits
all_x = [A[0], B[0], C[0], P[0], M[0], N[0]]
all_y = [A[1], B[1], C[1], P[1], M[1], N[1]]
ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
ax.axis('off')
ax.set_title('Step 5: PM // AB, Triangle BPM is Isosceles', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('step5_isosceles.png', dpi=150, bbox_inches='tight')
plt.close()
print("Figure 5 saved: step5_isosceles.png")

# ========== Figure 6: Final Conclusion ==========

fig, ax = plt.subplots(1, 1, figsize=(8, 8))
ax.set_aspect('equal')

# Draw triangle ABC
triangle = plt.Polygon([A, B, C], fill=False, edgecolor='#2c3e50', linewidth=2)
ax.add_patch(triangle)

# Draw all key segments
ax.plot([P[0], A[0]], [P[1], A[1]], color='#e74c3c', linewidth=2.5, label='PA')
ax.plot([P[0], B[0]], [P[1], B[1]], color='#3498db', linewidth=2.5, label='PB')
ax.plot([P[0], C[0]], [P[1], C[1]], color='#27ae60', linewidth=2.5, label='PC')

# Draw BP extension to N
ax.plot([B[0], N[0]], [B[1], N[1]], color='#2c3e50', linewidth=1.5, linestyle='--')

# Draw NC
ax.plot([N[0], C[0]], [N[1], C[1]], color='#9b59b6', linewidth=2, linestyle='--')

# Draw AN
ax.plot([A[0], N[0]], [A[1], N[1]], color='#e74c3c', linewidth=1.5)

# Draw MC, MB
ax.plot([M[0], C[0]], [M[1], C[1]], color='#9b59b6', linewidth=2, linestyle='--')
ax.plot([M[0], B[0]], [M[1], B[1]], color='#27ae60', linewidth=1.5)

# Draw PM
ax.plot([P[0], M[0]], [P[1], M[1]], color='#f39c12', linewidth=1.5)

# Highlight NB = NC = PC
ax.plot([N[0], B[0]], [N[1], B[1]], color='#f39c12', linewidth=2.5)

# Mark NP = PA
mark_equal_sides(ax, N, P, num_marks=1, color='#e74c3c')

# Mark NC = PC = MC
mark_equal_sides(ax, N, C, num_marks=3, color='#27ae60')
mark_equal_sides(ax, P, C, num_marks=3, color='#27ae60')
mark_equal_sides(ax, M, C, num_marks=3, color='#27ae60')

# Mark NB with combined marks
mark_equal_sides(ax, N, B, num_marks=3, color='#27ae60')

# Mark points
for pt in [A, B, C, P, N, M]:
    ax.plot(*pt, 'ko', markersize=6)

# Labels
label_point(ax, A, 'A', 225)
label_point(ax, B, 'B', 315)
label_point(ax, C, 'C', 90)
label_point(ax, P, 'P', 270, offset_dist=0.4)
label_point(ax, N, 'N', 135)
label_point(ax, M, 'M', 0, offset_dist=0.35)

# Mark angles
# From B: angle to P/N ≈ 160°, M ≈ 140°, C ≈ 110°
# ∠NBM = 20°, ∠MBC = 30°, ∠NBC = 50°
draw_angle_arc(ax, B, N, M, radius=0.5, color='#e74c3c', label='20°')   # ∠NBM at B
draw_angle_arc(ax, B, M, C, radius=0.8, color='#3498db', label='30°')   # ∠MBC at B
draw_angle_arc(ax, B, A, P, radius=1.1, color='#f39c12', label='20°')   # ∠PBA at B
draw_angle_arc(ax, P, M, B, radius=0.4, color='#27ae60', label='20°')   # ∠MPB at P
draw_angle_arc(ax, C, N, A, radius=0.5, color='#8e44ad')                # ∠NCA arc only

# Place ∠NCA label to the left of NC with arrow pointing to arc midpoint
angle_CN = np.degrees(np.arctan2(N[1]-C[1], N[0]-C[0]))
angle_CA = np.degrees(np.arctan2(A[1]-C[1], A[0]-C[0]))
# C to N ≈ 240°, C to A ≈ 250° (both in 3rd quadrant)
# Midpoint of arc
mid_angle_raw = (angle_CN + angle_CA) / 2
mid_angle_NCA = np.radians(mid_angle_raw)
# Arc midpoint (where arrow points to)
arc_x = C[0] + 0.55 * np.cos(mid_angle_NCA)
arc_y = C[1] + 0.55 * np.sin(mid_angle_NCA)
# Label position: left side of NC line (away from CA), shifted up
label_angle = np.radians(angle_CN - 12)  # offset past CN, away from CA
label_x = C[0] + 1.5 * np.cos(label_angle)
label_y = C[1] + 1.5 * np.sin(label_angle) + 0.3
ax.annotate('10°', xy=(arc_x, arc_y), xytext=(label_x, label_y),
            fontsize=11, color='#8e44ad', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=1.0,
                           linestyle='dashed', connectionstyle='arc3,rad=0.2'),
            ha='center', va='center')

# Add conclusion text
ax.text(3, -1.2, 'PC = NC = NB = NP + PB = PA + PB', 
        ha='center', va='center', fontsize=13, fontweight='bold',
        color='#c0392b', bbox=dict(boxstyle='round,pad=0.4', facecolor='#ffeaa7', edgecolor='#c0392b'))

# Set limits
all_x = [A[0], B[0], C[0], P[0], N[0]]
all_y = [A[1], B[1], C[1], P[1], N[1]]
ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
ax.set_ylim(min(all_y) - 2.0, max(all_y) + margin)
ax.axis('off')
ax.set_title('Step 6: Final - PC = NB = NP + PB = PA + PB', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('step6_final.png', dpi=150, bbox_inches='tight')
plt.close()
print("Figure 6 saved: step6_final.png")

print("\nAll figures generated successfully!")
