"""
Problem 006: Isosceles triangle divided into two isosceles triangles
In isosceles triangle ABC with AB=AC, a line through C divides it into 
two smaller isosceles triangles. Find angle A.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


def draw_angle_arc(ax, center, p1, p2, radius=0.3, color='blue', label=None, fontsize=10):
    """Draw an angle arc between two rays from center."""
    angle1 = np.degrees(np.arctan2(p1[1]-center[1], p1[0]-center[0]))
    angle2 = np.degrees(np.arctan2(p2[1]-center[1], p2[0]-center[0]))
    # Ensure arc is drawn on the smaller angle side
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


def mark_equal_sides(ax, p1, p2, num_marks=1, color='red', mark_size=0.1):
    """Mark equal sides with tick marks."""
    mid = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2)
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = np.sqrt(dx**2 + dy**2)
    # Perpendicular direction
    perp_x = -dy / length * mark_size
    perp_y = dx / length * mark_size
    # Direction along the segment
    along_x = dx / length * 0.08
    along_y = dy / length * 0.08
    
    for i in range(num_marks):
        offset = (i - (num_marks-1)/2) * 0.12
        cx = mid[0] + offset * along_x / 0.08
        cy = mid[1] + offset * along_y / 0.08
        ax.plot([cx - perp_x, cx + perp_x], [cy - perp_y, cy + perp_y], 
                color=color, linewidth=2)


def label_vertex(ax, point, centroid, name, offset=0.35, fontsize=14):
    """Label a vertex, placing the label away from the centroid."""
    direction = np.array(point) - np.array(centroid)
    norm = np.linalg.norm(direction)
    if norm > 0:
        direction = direction / norm * offset
    ax.text(point[0] + direction[0], point[1] + direction[1], name,
            ha='center', va='center', fontsize=fontsize, fontweight='bold')


# ========== Figure 1: Setup diagram ==========
fig, ax = plt.subplots(1, 1, figsize=(6, 7))
ax.set_aspect('equal')
ax.axis('off')

# Isosceles triangle with AB=AC, generic angle
angle_A = 50 * np.pi / 180  # Just for illustration
base = 4
height = base / (2 * np.tan(angle_A / 2))

A = np.array([0, height])
B = np.array([base/2, 0])
C = np.array([-base/2, 0])

# Draw triangle
triangle = plt.Polygon([A, B, C], fill=False, edgecolor='black', linewidth=2)
ax.add_patch(triangle)

centroid = (A + B + C) / 3
label_vertex(ax, A, centroid, 'A', offset=0.4)
label_vertex(ax, B, centroid, 'B', offset=0.4)
label_vertex(ax, C, centroid, 'C', offset=0.4)

# Mark equal sides
mark_equal_sides(ax, A, B, num_marks=1, color='red')
mark_equal_sides(ax, A, C, num_marks=1, color='red')

# Label conditions
ax.text(0, -0.8, 'AB = AC', ha='center', fontsize=12, style='italic')
ax.set_title('Step 1: Isosceles Triangle ABC', fontsize=13, pad=10)

# Set limits
all_x = [A[0], B[0], C[0]]
all_y = [A[1], B[1], C[1]]
margin = 1.0
ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
ax.set_ylim(min(all_y) - margin, max(all_y) + margin)

plt.tight_layout()
plt.savefig('step1_setup.png', dpi=150, bbox_inches='tight')
plt.close()


# ========== Figure 2: Case 1 — AD=DC, BD=BC ==========
fig, ax = plt.subplots(1, 1, figsize=(6, 7))
ax.set_aspect('equal')
ax.axis('off')

# Case 1: angle A = 180/7 degrees
angle_A_case1 = 180.0 / 7
angle_B_case1 = (180 - angle_A_case1) / 2  # = 3 * 180/7

# Build triangle
# Place C at origin, B on x-axis
BC_len = 4.0
C = np.array([0, 0])
B = np.array([BC_len, 0])

# A is above, using angle B
AB_len = BC_len * np.sin(np.radians(angle_B_case1)) / np.sin(np.radians(angle_A_case1))
A = np.array([B[0] - AB_len * np.cos(np.radians(angle_B_case1)),
              AB_len * np.sin(np.radians(angle_B_case1))])

# Find D on AB such that AD = DC
# In triangle ACD: AD = DC, angle A = angle DCA = x = 180/7
# angle ADC = 180 - 2x
# D divides AB. We use the property AD = DC.
# From A, D is at distance AD along AB direction.
# AD/sin(angle_DCA) = AC/sin(angle_ADC)  (sine rule in triangle ACD)
AC_len = AB_len  # since AB = AC
angle_DCA = angle_A_case1
angle_ADC = 180 - 2 * angle_A_case1
AD_len = AC_len * np.sin(np.radians(angle_DCA)) / np.sin(np.radians(angle_ADC))

# D is on AB at distance AD from A
AB_dir = (B - A) / np.linalg.norm(B - A)
D = A + AD_len * AB_dir

# Draw triangle
triangle = plt.Polygon([A, B, C], fill=False, edgecolor='black', linewidth=2)
ax.add_patch(triangle)

# Draw cevian CD
ax.plot([C[0], D[0]], [C[1], D[1]], 'b-', linewidth=1.5)

# Fill triangles with different colors
tri_ACD = plt.Polygon([A, C, D], alpha=0.15, facecolor='skyblue', edgecolor='blue', linewidth=1.5)
tri_BCD = plt.Polygon([B, C, D], alpha=0.15, facecolor='lightyellow', edgecolor='orange', linewidth=1.5)
ax.add_patch(tri_ACD)
ax.add_patch(tri_BCD)

centroid = (A + B + C) / 3
label_vertex(ax, A, centroid, 'A', offset=0.45)
label_vertex(ax, B, centroid, 'B', offset=0.45)
label_vertex(ax, C, centroid, 'C', offset=0.45)
# Label D
D_label_dir = np.array([0.2, 0.3])
ax.text(D[0] + D_label_dir[0], D[1] + D_label_dir[1], 'D',
        ha='center', va='center', fontsize=14, fontweight='bold')

# Mark equal sides
mark_equal_sides(ax, A, D, num_marks=1, color='blue')
mark_equal_sides(ax, D, C, num_marks=1, color='blue')
mark_equal_sides(ax, B, D, num_marks=2, color='orange')
mark_equal_sides(ax, B, C, num_marks=2, color='orange')

# Angle labels
draw_angle_arc(ax, A, C, B, radius=0.5, color='green', label='x')
draw_angle_arc(ax, C, A, D, radius=0.6, color='blue', label='x')
draw_angle_arc(ax, C, D, B, radius=0.45, color='orange', label='2x')

ax.set_title('Case (a): AD = DC, BD = BC', fontsize=13, pad=10)
ax.text((C[0]+B[0])/2, -0.8, r'$\angle A = 180°/7 \approx 25.7°$', 
        ha='center', fontsize=11, color='darkred')

all_x = [A[0], B[0], C[0], D[0]]
all_y = [A[1], B[1], C[1], D[1]]
margin = 1.2
ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
ax.set_ylim(min(all_y) - margin, max(all_y) + margin)

plt.tight_layout()
plt.savefig('step2_case1.png', dpi=150, bbox_inches='tight')
plt.close()


# ========== Figure 3: Case 2 — AD=DC, DC=CB ==========
fig, ax = plt.subplots(1, 1, figsize=(6, 7))
ax.set_aspect('equal')
ax.axis('off')

# Case 2: angle A = 36 degrees
angle_A_case2 = 36.0
angle_B_case2 = (180 - 36) / 2  # = 72

# Build triangle
BC_len = 4.0
C = np.array([0, 0])
B = np.array([BC_len, 0])

AB_len = BC_len * np.sin(np.radians(angle_B_case2)) / np.sin(np.radians(angle_A_case2))
A = np.array([B[0] - AB_len * np.cos(np.radians(angle_B_case2)),
              AB_len * np.sin(np.radians(angle_B_case2))])

# Find D on AB such that AD = DC
AC_len = AB_len  # AB = AC
angle_DCA = angle_A_case2  # = 36
angle_ADC = 180 - 2 * angle_A_case2  # = 108
AD_len = AC_len * np.sin(np.radians(angle_DCA)) / np.sin(np.radians(angle_ADC))

AB_dir = (B - A) / np.linalg.norm(B - A)
D = A + AD_len * AB_dir

# Draw triangle
triangle = plt.Polygon([A, B, C], fill=False, edgecolor='black', linewidth=2)
ax.add_patch(triangle)

# Draw cevian CD
ax.plot([C[0], D[0]], [C[1], D[1]], 'b-', linewidth=1.5)

# Fill triangles
tri_ACD = plt.Polygon([A, C, D], alpha=0.15, facecolor='lightcyan', edgecolor='blue', linewidth=1.5)
tri_BCD = plt.Polygon([B, C, D], alpha=0.15, facecolor='lightyellow', edgecolor='orange', linewidth=1.5)
ax.add_patch(tri_ACD)
ax.add_patch(tri_BCD)

centroid = (A + B + C) / 3
label_vertex(ax, A, centroid, 'A', offset=0.45)
label_vertex(ax, B, centroid, 'B', offset=0.45)
label_vertex(ax, C, centroid, 'C', offset=0.45)
# Label D
D_label_dir = np.array([0.2, 0.3])
ax.text(D[0] + D_label_dir[0], D[1] + D_label_dir[1], 'D',
        ha='center', va='center', fontsize=14, fontweight='bold')

# Mark equal sides
mark_equal_sides(ax, A, D, num_marks=1, color='blue')
mark_equal_sides(ax, D, C, num_marks=1, color='blue')
mark_equal_sides(ax, D, C, num_marks=2, color='orange')
mark_equal_sides(ax, C, B, num_marks=2, color='orange')

# Angle labels
draw_angle_arc(ax, A, C, B, radius=0.5, color='green', label='x')
draw_angle_arc(ax, C, A, D, radius=0.6, color='blue', label='x')
draw_angle_arc(ax, B, C, D, radius=0.5, color='orange', label='2x')

ax.set_title('Case (b): AD = DC = CB', fontsize=13, pad=10)
ax.text((C[0]+B[0])/2, -0.8, r'$\angle A = 36°$', 
        ha='center', fontsize=11, color='darkred')

all_x = [A[0], B[0], C[0], D[0]]
all_y = [A[1], B[1], C[1], D[1]]
margin = 1.2
ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
ax.set_ylim(min(all_y) - margin, max(all_y) + margin)

plt.tight_layout()
plt.savefig('step3_case2.png', dpi=150, bbox_inches='tight')
plt.close()


print("All figures generated successfully!")
