"""
Problem 003: Geometry Figures
In Rt△ABC, ∠C = 90°, ∠A ≠ 30°, ∠A ≠ 45°.
On line BC or AC, find point P such that △PAB is isosceles.
Find how many such points P exist.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Use a specific angle for illustration: ∠A = 55°, ∠B = 35°
angle_A = 55  # degrees
angle_B = 35  # degrees

# Set up the right triangle
# C at origin, B on x-axis, A on y-axis
a = 3.0  # BC length
b = a * np.tan(np.radians(angle_B))  # AC length = a * tan(B) = a * (AC/BC)
# Actually: tan(∠A) = BC/AC = a/b, so b = a / tan(∠A)
b = a / np.tan(np.radians(angle_A))

C = np.array([0, 0])
B = np.array([a, 0])
A = np.array([0, b])
AB = np.sqrt(a**2 + b**2)


def draw_base_triangle(ax, extend_lines=True, line_extend=2.0):
    """Draw the base right triangle with optional line extensions."""
    # Draw the triangle
    triangle = plt.Polygon([A, B, C], fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(triangle)
    
    # Right angle mark at C
    size = 0.15
    ax.plot([size, size, 0], [0, size, size], 'k-', linewidth=1)
    
    # Labels
    ax.text(A[0] - 0.2, A[1] + 0.1, 'A', fontsize=14, fontweight='bold', ha='center')
    ax.text(B[0] + 0.2, B[1] - 0.15, 'B', fontsize=14, fontweight='bold', ha='center')
    ax.text(C[0] - 0.2, C[1] - 0.15, 'C', fontsize=14, fontweight='bold', ha='center')
    
    if extend_lines:
        # Extend line BC (x-axis) in both directions
        ax.plot([-line_extend, a + line_extend], [0, 0], 'k--', linewidth=0.8, alpha=0.4)
        # Extend line AC (y-axis) in both directions
        ax.plot([0, 0], [-line_extend, b + line_extend], 'k--', linewidth=0.8, alpha=0.4)


def mark_point(ax, point, label, color='red', offset=(0.15, 0.15)):
    """Mark a point with a dot and label."""
    ax.plot(point[0], point[1], 'o', color=color, markersize=8, zorder=5)
    ax.text(point[0] + offset[0], point[1] + offset[1], label,
            fontsize=11, fontweight='bold', color=color, ha='center')


def draw_equal_marks(ax, p1, p2, num=1, color='blue', offset_factor=0.08):
    """Draw tick marks on a segment to indicate equal lengths."""
    mid = (p1 + p2) / 2
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = np.sqrt(dx**2 + dy**2)
    perp_x = -dy / length * offset_factor
    perp_y = dx / length * offset_factor
    along_x = dx / length * 0.04
    along_y = dy / length * 0.04
    
    for i in range(num):
        offset = (i - (num - 1) / 2) * 0.06
        cx = mid[0] + offset * along_x / 0.04
        cy = mid[1] + offset * along_y / 0.04
        ax.plot([cx - perp_x, cx + perp_x], [cy - perp_y, cy + perp_y],
                color=color, linewidth=2)


# ============================================================
# Calculate all 8 points
# ============================================================

# Points on line BC (y = 0, parametrized by x-coordinate t)
# Case 1: PA = PB (vertex P)
t1 = (a**2 - b**2) / (2 * a)
P_BC_1 = np.array([t1, 0])

# Case 2: PA = AB (vertex A)
# |t|^2 + b^2 = a^2 + b^2 -> t = ±a, exclude t=a (=B)
P_BC_2 = np.array([-a, 0])

# Case 3: PB = AB (vertex B)
# |t - a| = sqrt(a^2 + b^2) -> t = a ± AB
P_BC_3a = np.array([a + AB, 0])
P_BC_3b = np.array([a - AB, 0])

# Points on line AC (x = 0, parametrized by y-coordinate s)
# Case 4: PA = PB (vertex P)
s4 = (b**2 - a**2) / (2 * b)
P_AC_4 = np.array([0, s4])

# Case 5: PA = AB (vertex A)
# |s - b| = AB -> s = b ± AB
P_AC_5a = np.array([0, b + AB])
P_AC_5b = np.array([0, b - AB])

# Case 6: PB = AB (vertex B)
# a^2 + s^2 = a^2 + b^2 -> s = ±b, exclude s=b (=A)
P_AC_6 = np.array([0, -b])


# ============================================================
# Figure 1: Problem Setup
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')

draw_base_triangle(ax, extend_lines=True, line_extend=1.5)

# Annotations
ax.text(a/2, b/2 + 0.2, f'AB (hypotenuse)', fontsize=9, color='gray',
        rotation=-np.degrees(np.arctan2(b, -a)), ha='center')
ax.text(1.5, -0.5, 'line BC', fontsize=10, color='gray', style='italic')
ax.text(-0.5, b/2, 'line AC', fontsize=10, color='gray', style='italic', rotation=90)

# Angle labels
angle_arc_A = patches.Arc(A, 0.5, 0.5, angle=0, theta1=270, theta2=270+angle_A, color='red', linewidth=1.5)
ax.add_patch(angle_arc_A)
ax.text(A[0] + 0.2, A[1] - 0.35, f'{angle_A}°', fontsize=9, color='red')

angle_arc_B = patches.Arc(B, 0.5, 0.5, angle=0, theta1=180-angle_B, theta2=180, color='blue', linewidth=1.5)
ax.add_patch(angle_arc_B)
ax.text(B[0] - 0.45, B[1] + 0.15, f'{angle_B}°', fontsize=9, color='blue')

ax.set_xlim(-2, a + 2)
ax.set_ylim(-2, b + 2)
ax.axis('off')
ax.set_title('Step 1: Problem Setup\nRt Triangle ABC, angle C = 90°\nFind P on line BC or AC s.t. triangle PAB is isosceles',
             fontsize=11, pad=10)

plt.tight_layout()
plt.savefig('/home/rivli01/projects/homework/math/003_claude/step1_setup.png', dpi=150, bbox_inches='tight')
plt.close()


# ============================================================
# Figure 2: Points on line BC (PA=PB)
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(8, 6))
ax.set_aspect('equal')
draw_base_triangle(ax, extend_lines=True, line_extend=1.0)

# Draw perpendicular bisector of AB
mid_AB = (A + B) / 2
# Perpendicular bisector direction: perpendicular to AB
AB_dir = B - A
perp_dir = np.array([-AB_dir[1], AB_dir[0]])
perp_dir = perp_dir / np.linalg.norm(perp_dir)
pb_start = mid_AB - perp_dir * 2
pb_end = mid_AB + perp_dir * 2
ax.plot([pb_start[0], pb_end[0]], [pb_start[1], pb_end[1]], 'g--', linewidth=1, alpha=0.5)

# Mark point P1
mark_point(ax, P_BC_1, 'P₁', color='red', offset=(0.0, -0.3))

# Draw PA and PB
ax.plot([P_BC_1[0], A[0]], [P_BC_1[1], A[1]], 'r-', linewidth=1.5, alpha=0.6)
ax.plot([P_BC_1[0], B[0]], [P_BC_1[1], B[1]], 'r-', linewidth=1.5, alpha=0.6)
draw_equal_marks(ax, P_BC_1, A, num=1, color='red')
draw_equal_marks(ax, P_BC_1, B, num=1, color='red')

ax.set_xlim(-1.5, a + 1.5)
ax.set_ylim(-1.0, b + 0.5)
ax.axis('off')
ax.set_title('Step 2a: P on line BC, PA = PB\n(P on perpendicular bisector of AB) → 1 point',
             fontsize=11, pad=10)
plt.tight_layout()
plt.savefig('/home/rivli01/projects/homework/math/003_claude/step2a_BC_PA_eq_PB.png', dpi=150, bbox_inches='tight')
plt.close()


# ============================================================
# Figure 3: Points on line BC (PA=AB)
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(9, 6))
ax.set_aspect('equal')
draw_base_triangle(ax, extend_lines=True, line_extend=a + 0.5)

# Draw circle centered at A with radius AB
theta = np.linspace(0, 2*np.pi, 100)
circle_x = A[0] + AB * np.cos(theta)
circle_y = A[1] + AB * np.sin(theta)
ax.plot(circle_x, circle_y, 'b--', linewidth=1, alpha=0.4)

# Mark point P2
mark_point(ax, P_BC_2, 'P₂', color='green', offset=(0.0, -0.3))
ax.plot([P_BC_2[0], A[0]], [P_BC_2[1], A[1]], 'g-', linewidth=1.5, alpha=0.6)
ax.plot([A[0], B[0]], [A[1], B[1]], 'g-', linewidth=1.5, alpha=0.6)
draw_equal_marks(ax, P_BC_2, A, num=2, color='green')
draw_equal_marks(ax, A, B, num=2, color='green')

ax.text(A[0] + 0.6, A[1] - 0.8, 'Circle(A, AB)', fontsize=9, color='blue', style='italic')

ax.set_xlim(-a - 1, a + 1.5)
ax.set_ylim(-1.5, b + 1.5)
ax.axis('off')
ax.set_title('Step 2b: P on line BC, PA = AB\n(Circle centered A, radius AB) → 1 point (other is B)',
             fontsize=11, pad=10)
plt.tight_layout()
plt.savefig('/home/rivli01/projects/homework/math/003_claude/step2b_BC_PA_eq_AB.png', dpi=150, bbox_inches='tight')
plt.close()


# ============================================================
# Figure 4: Points on line BC (PB=AB)
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(10, 5))
ax.set_aspect('equal')
draw_base_triangle(ax, extend_lines=True, line_extend=AB + 0.5)

# Draw circle centered at B with radius AB
circle_x = B[0] + AB * np.cos(theta)
circle_y = B[1] + AB * np.sin(theta)
ax.plot(circle_x, circle_y, 'm--', linewidth=1, alpha=0.4)

# Mark points P3a and P3b
mark_point(ax, P_BC_3a, 'P₃', color='purple', offset=(0.0, 0.2))
mark_point(ax, P_BC_3b, 'P₄', color='purple', offset=(0.0, 0.2))
ax.plot([P_BC_3a[0], B[0]], [P_BC_3a[1], B[1]], 'm-', linewidth=1.5, alpha=0.6)
ax.plot([P_BC_3b[0], B[0]], [P_BC_3b[1], B[1]], 'm-', linewidth=1.5, alpha=0.6)
draw_equal_marks(ax, P_BC_3a, B, num=3, color='purple')
draw_equal_marks(ax, P_BC_3b, B, num=3, color='purple')
draw_equal_marks(ax, A, B, num=3, color='purple')

ax.text(B[0] + 0.8, B[1] + 1.5, 'Circle(B, AB)', fontsize=9, color='purple', style='italic')

ax.set_xlim(min(P_BC_3b[0], -a) - 0.5, P_BC_3a[0] + 0.5)
ax.set_ylim(-1.5, b + 1.5)
ax.axis('off')
ax.set_title('Step 2c: P on line BC, PB = AB\n(Circle centered B, radius AB) → 2 points',
             fontsize=11, pad=10)
plt.tight_layout()
plt.savefig('/home/rivli01/projects/homework/math/003_claude/step2c_BC_PB_eq_AB.png', dpi=150, bbox_inches='tight')
plt.close()


# ============================================================
# Figure 5: Points on line AC (PA=PB)
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')
draw_base_triangle(ax, extend_lines=True, line_extend=1.5)

# Draw perpendicular bisector of AB
ax.plot([pb_start[0], pb_end[0]], [pb_start[1], pb_end[1]], 'g--', linewidth=1, alpha=0.5)

# Mark point P5
mark_point(ax, P_AC_4, 'P₅', color='red', offset=(0.2, 0.0))
ax.plot([P_AC_4[0], A[0]], [P_AC_4[1], A[1]], 'r-', linewidth=1.5, alpha=0.6)
ax.plot([P_AC_4[0], B[0]], [P_AC_4[1], B[1]], 'r-', linewidth=1.5, alpha=0.6)
draw_equal_marks(ax, P_AC_4, A, num=1, color='red')
draw_equal_marks(ax, P_AC_4, B, num=1, color='red')

ax.set_xlim(-1.5, a + 1.5)
ax.set_ylim(-1.5, b + 1.5)
ax.axis('off')
ax.set_title('Step 3a: P on line AC, PA = PB\n(Perpendicular bisector of AB) → 1 point',
             fontsize=11, pad=10)
plt.tight_layout()
plt.savefig('/home/rivli01/projects/homework/math/003_claude/step3a_AC_PA_eq_PB.png', dpi=150, bbox_inches='tight')
plt.close()


# ============================================================
# Figure 6: Points on line AC (PA=AB)
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(7, 9))
ax.set_aspect('equal')

# Need larger y-range for this figure
draw_base_triangle(ax, extend_lines=True, line_extend=AB + 0.5)

# Draw circle centered at A with radius AB
circle_x = A[0] + AB * np.cos(theta)
circle_y = A[1] + AB * np.sin(theta)
ax.plot(circle_x, circle_y, 'b--', linewidth=1, alpha=0.4)

# Mark points P6a and P6b
mark_point(ax, P_AC_5a, 'P₆', color='blue', offset=(0.2, 0.1))
mark_point(ax, P_AC_5b, 'P₇', color='blue', offset=(0.2, 0.1))
ax.plot([P_AC_5a[0], A[0]], [P_AC_5a[1], A[1]], 'b-', linewidth=1.5, alpha=0.6)
ax.plot([P_AC_5b[0], A[0]], [P_AC_5b[1], A[1]], 'b-', linewidth=1.5, alpha=0.6)
draw_equal_marks(ax, P_AC_5a, A, num=2, color='blue')
draw_equal_marks(ax, P_AC_5b, A, num=2, color='blue')
draw_equal_marks(ax, A, B, num=2, color='blue')

ax.set_xlim(-2, a + 2)
ax.set_ylim(P_AC_5b[1] - 0.5, P_AC_5a[1] + 0.5)
ax.axis('off')
ax.set_title('Step 3b: P on line AC, PA = AB\n(Circle centered A, radius AB) → 2 points',
             fontsize=11, pad=10)
plt.tight_layout()
plt.savefig('/home/rivli01/projects/homework/math/003_claude/step3b_AC_PA_eq_AB.png', dpi=150, bbox_inches='tight')
plt.close()


# ============================================================
# Figure 7: Points on line AC (PB=AB)
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')
draw_base_triangle(ax, extend_lines=True, line_extend=b + 0.5)

# Draw circle centered at B with radius AB
circle_x = B[0] + AB * np.cos(theta)
circle_y = B[1] + AB * np.sin(theta)
ax.plot(circle_x, circle_y, 'm--', linewidth=1, alpha=0.4)

# Mark point P8
mark_point(ax, P_AC_6, 'P₈', color='orange', offset=(0.2, 0.0))
ax.plot([P_AC_6[0], B[0]], [P_AC_6[1], B[1]], color='orange', linewidth=1.5, alpha=0.6)
ax.plot([A[0], B[0]], [A[1], B[1]], color='orange', linewidth=1.5, alpha=0.6)
draw_equal_marks(ax, P_AC_6, B, num=3, color='orange')
draw_equal_marks(ax, A, B, num=3, color='orange')

ax.set_xlim(-1.5, a + 1.5)
ax.set_ylim(-b - 0.5, b + 1)
ax.axis('off')
ax.set_title('Step 3c: P on line AC, PB = AB\n(Circle centered B, radius AB) → 1 point (other is A)',
             fontsize=11, pad=10)
plt.tight_layout()
plt.savefig('/home/rivli01/projects/homework/math/003_claude/step3c_AC_PB_eq_AB.png', dpi=150, bbox_inches='tight')
plt.close()


# ============================================================
# Figure 8: Summary - All 8 points
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(11, 9))
ax.set_aspect('equal')

# Extended range
draw_base_triangle(ax, extend_lines=True, line_extend=AB + 1)

# Mark all 8 points with different colors
points_BC = [(P_BC_1, 'P₁', 'red'), (P_BC_2, 'P₂', 'green'),
             (P_BC_3a, 'P₃', 'purple'), (P_BC_3b, 'P₄', 'purple')]
points_AC = [(P_AC_4, 'P₅', 'red'), (P_AC_5a, 'P₆', 'blue'),
             (P_AC_5b, 'P₇', 'blue'), (P_AC_6, 'P₈', 'orange')]

for point, label, color in points_BC:
    mark_point(ax, point, label, color=color, offset=(0.0, -0.3))
    # Draw triangle PAB lightly
    tri = plt.Polygon([point, A, B], fill=False, edgecolor=color, linewidth=1, alpha=0.3)
    ax.add_patch(tri)

for point, label, color in points_AC:
    offset_x = 0.25
    if point[1] > b:
        offset_y = 0.15
    else:
        offset_y = -0.15
    mark_point(ax, point, label, color=color, offset=(offset_x, offset_y))
    tri = plt.Polygon([point, A, B], fill=False, edgecolor=color, linewidth=1, alpha=0.3)
    ax.add_patch(tri)

# Legend
legend_y = b + AB
ax.text(-a, legend_y, 'On line BC:', fontsize=10, fontweight='bold')
ax.text(-a, legend_y - 0.3, 'P₁: PA=PB | P₂: PA=AB | P₃,P₄: PB=AB', fontsize=9)
ax.text(-a, legend_y - 0.6, 'On line AC:', fontsize=10, fontweight='bold')
ax.text(-a, legend_y - 0.9, 'P₅: PA=PB | P₆,P₇: PA=AB | P₈: PB=AB', fontsize=9)

all_x = [p[0] for p, _, _ in points_BC + points_AC]
all_y = [p[1] for p, _, _ in points_BC + points_AC]
ax.set_xlim(min(all_x) - 1, max(all_x) + 1)
ax.set_ylim(min(all_y) - 1, max(all_y) + 1.5)
ax.axis('off')
ax.set_title('Step 4: Summary — All 8 Points\n(∠A = 55°, ∠B = 35° as illustration)',
             fontsize=12, fontweight='bold', pad=10)

plt.tight_layout()
plt.savefig('/home/rivli01/projects/homework/math/003_claude/step4_summary.png', dpi=150, bbox_inches='tight')
plt.close()

print("All figures for Problem 003 generated successfully!")
print(f"\nVerification (∠A = {angle_A}°):")
print(f"  a (BC) = {a:.3f}, b (AC) = {b:.3f}, AB = {AB:.3f}")
print(f"  P₁ on BC: ({P_BC_1[0]:.3f}, 0) — PA=PB={np.linalg.norm(P_BC_1-A):.3f}")
print(f"  P₂ on BC: ({P_BC_2[0]:.3f}, 0) — PA={np.linalg.norm(P_BC_2-A):.3f}, AB={AB:.3f}")
print(f"  P₃ on BC: ({P_BC_3a[0]:.3f}, 0) — PB={np.linalg.norm(P_BC_3a-B):.3f}, AB={AB:.3f}")
print(f"  P₄ on BC: ({P_BC_3b[0]:.3f}, 0) — PB={np.linalg.norm(P_BC_3b-B):.3f}, AB={AB:.3f}")
print(f"  P₅ on AC: (0, {P_AC_4[1]:.3f}) — PA=PB: {np.linalg.norm(P_AC_4-A):.3f}={np.linalg.norm(P_AC_4-B):.3f}")
print(f"  P₆ on AC: (0, {P_AC_5a[1]:.3f}) — PA={np.linalg.norm(P_AC_5a-A):.3f}, AB={AB:.3f}")
print(f"  P₇ on AC: (0, {P_AC_5b[1]:.3f}) — PA={np.linalg.norm(P_AC_5b-A):.3f}, AB={AB:.3f}")
print(f"  P₈ on AC: (0, {P_AC_6[1]:.3f}) — PB={np.linalg.norm(P_AC_6-B):.3f}, AB={AB:.3f}")
