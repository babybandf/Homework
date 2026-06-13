"""
Problem 004: Find angle BMC in triangle ABC
Given: triangle ABC with BAC = BCA = 44,
      point M inside, MCA = 30, MAC = 16
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

output_dir = os.path.dirname(os.path.abspath(__file__))

# ==================== Coordinate Calculation ====================
# Place A = (0,0), C = (2,0) on x-axis
# BAC = BCA = 44, so ABC = 92, triangle is isosceles with AB = BC
AC = 2.0
angle_BAC = np.radians(44)
angle_ABC = np.radians(92)

# AB = BC = AC * sin(44) / sin(92)
AB = AC * np.sin(angle_BAC) / np.sin(angle_ABC)
A = np.array([0.0, 0.0])
C = np.array([AC, 0.0])
B = np.array([AB * np.cos(angle_BAC), AB * np.sin(angle_BAC)])

# Point M: from A at angle 16 to AC, distance AM = AC * sin(30) / sin(134)
angle_MAC = np.radians(16)
angle_ACM = np.radians(30)
angle_AMC = np.radians(180 - 16 - 30)
AM = AC * np.sin(angle_ACM) / np.sin(angle_AMC)
M = np.array([AM * np.cos(angle_MAC), AM * np.sin(angle_MAC)])

# Equilateral triangle ACE on side AC, above AC (same side as B)
# E is the third vertex of the equilateral triangle with base AC
E = np.array([AC/2, AC * np.sqrt(3)/2])


# ==================== Utility Functions ====================
def draw_triangle(ax, pts, color='black', linewidth=1.5, linestyle='-'):
    tri = plt.Polygon(pts, fill=False, color=color, linewidth=linewidth, linestyle=linestyle)
    ax.add_patch(tri)


def draw_filled_triangle(ax, pts, facecolor, edgecolor='black', alpha=0.15, linewidth=1.5):
    tri = plt.Polygon(pts, facecolor=facecolor, edgecolor=edgecolor,
                      alpha=alpha, linewidth=linewidth)
    ax.add_patch(tri)


def draw_angle_arc(ax, center, p1, p2, radius=0.3, color='blue', label=None):
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
        label_r = radius + 0.15
        ax.text(center[0] + label_r * np.cos(mid_angle),
                center[1] + label_r * np.sin(mid_angle),
                label, ha='center', va='center', fontsize=9, color=color)


def label_point(ax, pt, name, offset=0.15, fontsize=12, fontweight='bold'):
    # offset direction away from triangle center
    centroid = (A + B + C) / 3
    direction = pt - centroid
    norm = np.linalg.norm(direction)
    if norm > 0:
        direction = direction / norm * offset
    ax.text(pt[0] + direction[0], pt[1] + direction[1], name,
            ha='center', va='center', fontsize=fontsize, fontweight=fontweight)


def mark_equal_sides(ax, p1, p2, num_marks=1, color='red', offset_dist=0.06):
    mid = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2)
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = np.sqrt(dx**2 + dy**2)
    perp_x = -dy / length * offset_dist
    perp_y = dx / length * offset_dist
    along_x = dx / length * 0.04
    along_y = dy / length * 0.04
    for i in range(num_marks):
        offset = (i - (num_marks-1)/2)
        cx = mid[0] + offset * along_x
        cy = mid[1] + offset * along_y
        ax.plot([cx - perp_x, cx + perp_x], [cy - perp_y, cy + perp_y],
                color=color, linewidth=2)


def setup_axes(ax, title=''):
    ax.set_aspect('equal')
    ax.set_xlim(-0.5, 2.5)
    ax.set_ylim(-0.2, 2.0)
    ax.axis('off')
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', pad=10)


# ==================== Figure 1: Initial Setup ====================
fig, ax = plt.subplots(1, 1, figsize=(8, 7))
setup_axes(ax, 'Step 1: Initial Triangle ABC with Point M')

# Draw main triangle ABC
draw_triangle(ax, [A, B, C], color='black', linewidth=2)

# Draw point M and lines from M to vertices
draw_triangle(ax, [A, M, C], color='blue', linewidth=1.5, linestyle='--')
ax.plot([M[0], B[0]], [M[1], B[1]], 'b--', linewidth=1.5)

# Label vertices
label_point(ax, A, 'A', offset=0.18)
label_point(ax, B, 'B', offset=0.18)
label_point(ax, C, 'C', offset=0.18)
label_point(ax, M, 'M', offset=0.15, fontsize=11)

# Draw known angles
draw_angle_arc(ax, A, C, B, radius=0.35, color='red', label='44')
draw_angle_arc(ax, C, A, B, radius=0.35, color='red', label='44')
draw_angle_arc(ax, B, A, C, radius=0.3, color='purple', label='92')
draw_angle_arc(ax, A, M, C, radius=0.25, color='green', label='16')     # ∠MAC at A (between AM and AC)
draw_angle_arc(ax, C, M, A, radius=0.45, color='blue', label='30')     # ∠MCA at C (between CM and CA)
draw_angle_arc(ax, A, C, M, radius=0.45, color='blue', label='16')     # ∠CAM at A (between AC and AM)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'step1_init.png'), dpi=150, bbox_inches='tight')
plt.close()
print("Figure 1 saved: step1_init.png")


# ==================== Figure 2: Construction of Equilateral Triangle ====================
fig, ax = plt.subplots(1, 1, figsize=(8, 7))
setup_axes(ax, 'Step 2: Construct Equilateral Triangle ACE')

# Fill sub-triangles for visual clarity
draw_filled_triangle(ax, [A, M, C], facecolor='lightblue', alpha=0.15)
draw_filled_triangle(ax, [A, B, C], facecolor='lightyellow', alpha=0.1)

# Draw main triangle
draw_triangle(ax, [A, B, C], color='black', linewidth=2)

# Draw equilateral triangle ACE
draw_triangle(ax, [A, C, E], color='green', linewidth=2.5)
label_point(ax, E, 'E', offset=0.18)

# Connect E to B
ax.plot([E[0], B[0]], [E[1], B[1]], 'purple', linewidth=1.5, linestyle='-')

# Draw M connections
draw_triangle(ax, [A, M, C], color='blue', linewidth=1.2, linestyle='--')
ax.plot([M[0], B[0]], [M[1], B[1]], 'blue', linewidth=1.2, linestyle='--')

# Label all points
label_point(ax, A, 'A', offset=0.18)
label_point(ax, B, 'B', offset=0.18)
label_point(ax, C, 'C', offset=0.18)
label_point(ax, M, 'M', offset=0.15, fontsize=11)
label_point(ax, E, 'E', offset=0.18)

# Mark equal sides of equilateral triangle
mark_equal_sides(ax, A, C, num_marks=1, color='green')
mark_equal_sides(ax, C, E, num_marks=1, color='green')
mark_equal_sides(ax, A, E, num_marks=1, color='green')

# Mark equal sides of isosceles triangle ABC
mark_equal_sides(ax, A, B, num_marks=2, color='red')
mark_equal_sides(ax, B, C, num_marks=2, color='red')

# Angle markings
draw_angle_arc(ax, A, E, C, radius=0.3, color='green', label='60')
draw_angle_arc(ax, C, A, E, radius=0.45, color='green', label='60')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'step2_construction.png'), dpi=150, bbox_inches='tight')
plt.close()
print("Figure 2 saved: step2_construction.png")


# ==================== Figure 3: Congruence Analysis ====================
fig, ax = plt.subplots(1, 1, figsize=(8, 7))
setup_axes(ax, 'Step 3: Triangle Congruence ABE ≅ AMC (ASA)')

# Highlight triangle ABE
draw_filled_triangle(ax, [A, B, E], facecolor='lightcoral', alpha=0.2)
# Highlight triangle AMC
draw_filled_triangle(ax, [A, M, C], facecolor='lightblue', alpha=0.2)

# Draw main triangle
draw_triangle(ax, [A, B, C], color='black', linewidth=2)

# Draw equilateral triangle
draw_triangle(ax, [A, C, E], color='green', linewidth=2)

# Connect B-E
ax.plot([E[0], B[0]], [E[1], B[1]], 'purple', linewidth=2, linestyle='-')

# Draw M connections
draw_triangle(ax, [A, M, C], color='blue', linewidth=1.5, linestyle='--')
ax.plot([M[0], B[0]], [M[1], B[1]], 'blue', linewidth=1.2, linestyle='--')

# Label points
label_point(ax, A, 'A', offset=0.18)
label_point(ax, B, 'B', offset=0.18)
label_point(ax, C, 'C', offset=0.18)
label_point(ax, M, 'M', offset=0.15, fontsize=11)
label_point(ax, E, 'E', offset=0.18)

# Mark equal sides
mark_equal_sides(ax, A, C, num_marks=1, color='green')

# Show congruent angles
draw_angle_arc(ax, A, E, B, radius=0.3, color='purple', label='16=16')   # ∠EAB at A = 16 = ∠MAC
draw_angle_arc(ax, C, M, A, radius=0.45, color='purple', label='30=30') # ∠MCA at C = 30 = ∠AEB
draw_angle_arc(ax, E, A, B, radius=0.35, color='darkorange', label='30=30') # ∠AEB at E = 30 = ∠MCA
draw_angle_arc(ax, A, C, M, radius=0.35, color='blue', label='16')     # ∠CAM at A = 16

# Mark sides AB = AM with a special notation
mark_equal_sides(ax, A, B, num_marks=3, color='darkred', offset_dist=0.08)
mark_equal_sides(ax, A, M, num_marks=3, color='darkred', offset_dist=0.08)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'step3_congruence.png'), dpi=150, bbox_inches='tight')
plt.close()
print("Figure 3 saved: step3_congruence.png")


# ==================== Figure 4: Final Answer ====================
fig, ax = plt.subplots(1, 1, figsize=(8, 7))
setup_axes(ax, 'Step 4: Final Answer - Angle BMC = 150')

# Fill the key triangle BMC with light highlight
draw_filled_triangle(ax, [B, M, C], facecolor='lightyellow', alpha=0.25)

# Draw main triangle ABC
draw_triangle(ax, [A, B, C], color='black', linewidth=2)

# Draw M connections
draw_triangle(ax, [A, M, C], color='gray', linewidth=1, linestyle='--')
ax.plot([M[0], B[0]], [M[1], B[1]], 'blue', linewidth=2, linestyle='-')

# Label points
label_point(ax, A, 'A', offset=0.18)
label_point(ax, B, 'B', offset=0.18)
label_point(ax, C, 'C', offset=0.18)
label_point(ax, M, 'M', offset=0.15, fontsize=11)

# Angle labels for key angles
# draw_angle_arc(center, p1, p2): arc at center between rays center->p1 and center->p2 = ∠(p1-center-p2)
draw_angle_arc(ax, M, B, C, radius=0.5, color='red', label='150')     # ∠BMC at M (between MB and MC)
draw_angle_arc(ax, B, A, M, radius=0.45, color='orange', label='76')  # ∠ABM at B (between BA and BM)
draw_angle_arc(ax, B, M, C, radius=0.3, color='purple', label='16')   # ∠MBC at B (between BM and BC)
draw_angle_arc(ax, C, B, M, radius=0.35, color='blue', label='14')    # ∠BCM at C (between CB and CM)

# Also mark the base angles of triangle ABC for context
draw_angle_arc(ax, A, B, C, radius=0.25, color='darkgreen', label='44')  # ∠BAC at A (between BA and CA)
draw_angle_arc(ax, C, B, A, radius=0.25, color='darkgreen', label='44')  # ∠BCA at C (between BC and AC)

# Add a text box with the answer - placed below the x-axis, away from AC
ax.text(1.0, -0.35, 'Answer: ∠BMC = 150', ha='center', va='center',
        fontsize=16, fontweight='bold', color='red',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='lightyellow', edgecolor='red', alpha=0.8))

# Extend y-axis lower bound to show the answer box
ax.set_ylim(-0.55, 2.0)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'step4_final.png'), dpi=150, bbox_inches='tight')
plt.close()
print("Figure 4 saved: step4_final.png")

print("\nAll figures generated successfully!")
