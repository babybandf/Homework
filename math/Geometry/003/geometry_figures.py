"""
Problem 003: Count points P on lines BC or AC such that triangle PAB is isosceles
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.patches import Arc, Circle

# Set font
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False


def draw_triangle(ax, A, B, C, labels=None, color='black', linewidth=2, fill_color='lightblue', alpha=0.2):
    """Draw a triangle given three vertices."""
    triangle = plt.Polygon([A, B, C], fill=True, facecolor=fill_color, 
                          edgecolor=color, linewidth=linewidth, alpha=alpha)
    ax.add_patch(triangle)
    if labels:
        centroid = np.array([(A[0]+B[0]+C[0])/3, (A[1]+B[1]+C[1])/3])
        offset = 0.3
        for point, label in zip([A, B, C], labels):
            direction = np.array(point) - centroid
            direction = direction / np.linalg.norm(direction) * offset
            ax.text(point[0] + direction[0], point[1] + direction[1], label,
                    ha='center', va='center', fontsize=14, fontweight='bold')


def draw_right_angle_mark(ax, vertex, size=0.4):
    """Draw right angle mark at vertex."""
    x, y = vertex
    ax.plot([x, x+size], [y, y], 'k-', linewidth=1.5)
    ax.plot([x, x], [y, y+size], 'k-', linewidth=1.5)


def draw_angle_arc(ax, center, p1, p2, radius=0.5, color='red', label=None):
    """Draw an angle arc between two rays from center."""
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
                label, ha='center', va='center', fontsize=11, color=color, fontweight='bold')


def draw_step1_setup():
    """Step 1: Problem setup - Right triangle ABC"""
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    ax.set_aspect('equal')
    
    # Define right triangle ABC with C at origin
    C = np.array([0, 0])
    A = np.array([0, 6])  # On y-axis
    B = np.array([4, 0])  # On x-axis
    
    # Draw triangle
    draw_triangle(ax, A, B, C, labels=['A', 'B', 'C'], fill_color='lightcyan', alpha=0.3)
    
    # Draw right angle mark at C
    draw_right_angle_mark(ax, C, size=0.4)
    
    # Draw angle arc for angle C
    draw_angle_arc(ax, C, A, B, radius=0.6, color='red', label='90°')
    
    # Extend lines AC and BC (showing they are lines, not just segments)
    ax.plot([0, 0], [6, 8.5], 'g--', alpha=0.6, linewidth=1.5)
    ax.plot([0, 0], [0, -3], 'g--', alpha=0.6, linewidth=1.5)
    ax.plot([4, 7.5], [0, 0], 'g--', alpha=0.6, linewidth=1.5)
    ax.plot([0, -3], [0, 0], 'g--', alpha=0.6, linewidth=1.5)
    
    # Label lines
    ax.text(-0.6, 8, 'Line AC', fontsize=11, color='green', rotation=90, va='bottom')
    ax.text(7.5, -0.6, 'Line BC', fontsize=11, color='green', ha='right')
    
    # Set limits with margin
    ax.set_xlim(-4, 9)
    ax.set_ylim(-4, 10)
    ax.axis('off')
    ax.set_title('Step 1: Right Triangle ABC', fontsize=14, fontweight='bold', pad=15)
    
    plt.tight_layout()
    plt.savefig('/home/rivli01/projects/homework/math/003/step1_setup.png', dpi=150,
                bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print("Step 1 completed")


def draw_step2_cases():
    """Step 2: Three cases of isosceles triangle PAB"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Common triangle setup
    C = np.array([0, 0])
    A = np.array([0, 5])
    B = np.array([4, 0])
    AB_len = np.linalg.norm(B - A)
    
    # Case 1: PA = PB (P on perpendicular bisector of AB)
    ax1 = axes[0]
    ax1.set_aspect('equal')
    draw_triangle(ax1, A, B, C, labels=['A', 'B', 'C'], fill_color='lightcyan', alpha=0.2)
    draw_right_angle_mark(ax1, C, size=0.3)
    
    # Calculate perpendicular bisector
    mid_AB = (A + B) / 2
    slope_AB = (B[1] - A[1]) / (B[0] - A[0])
    perp_slope = -1 / slope_AB
    
    # Draw perpendicular bisector line
    t = np.linspace(-4, 4, 100)
    perp_x = mid_AB[0] + t
    perp_y = mid_AB[1] + perp_slope * t
    ax1.plot(perp_x, perp_y, 'r-', linewidth=2.5, label='Perpendicular bisector')
    
    # Mark intersection points with lines AC and BC
    # Intersection with AC (x=0): mid_AB[1] + perp_slope * t = 0 -> solve for t
    t_ac = -mid_AB[0]
    p_ac_y = mid_AB[1] + perp_slope * t_ac
    ax1.plot(0, p_ac_y, 'ro', markersize=12, zorder=5)
    ax1.text(0.4, p_ac_y, 'P1', fontsize=12, fontweight='bold', color='red')
    
    # Intersection with BC (y=0): mid_AB[1] + perp_slope * t = 0
    t_bc = -mid_AB[1] / perp_slope if perp_slope != 0 else 0
    p_bc_x = mid_AB[0] + t_bc
    ax1.plot(p_bc_x, 0, 'ro', markersize=12, zorder=5)
    ax1.text(p_bc_x, 0.4, 'P2', fontsize=12, fontweight='bold', color='red')
    
    ax1.set_xlim(-3, 7)
    ax1.set_ylim(-3, 7)
    ax1.axis('off')
    ax1.set_title('Case 1: PA = PB\n(2 points)', fontsize=12, fontweight='bold')
    
    # Case 2: PA = AB (Circle centered at A)
    ax2 = axes[1]
    ax2.set_aspect('equal')
    draw_triangle(ax2, A, B, C, labels=['A', 'B', 'C'], fill_color='lightcyan', alpha=0.2)
    draw_right_angle_mark(ax2, C, size=0.3)
    
    # Draw circle centered at A with radius AB
    circle2 = Circle(A, AB_len, fill=False, edgecolor='blue', linewidth=2.5, linestyle='-')
    ax2.add_patch(circle2)
    
    # Mark intersection points
    # On line AC (x=0): A[1] +/- AB_len
    ax2.plot(0, A[1] + AB_len, 'bo', markersize=10, zorder=5)
    ax2.text(0.4, A[1] + AB_len, 'P3', fontsize=11, fontweight='bold', color='blue')
    ax2.plot(0, A[1] - AB_len, 'bo', markersize=10, zorder=5)
    ax2.text(0.4, A[1] - AB_len, 'P4', fontsize=11, fontweight='bold', color='blue')
    
    # On line BC (y=0): solve for x
    # (x-0)^2 + (0-5)^2 = AB_len^2
    # x^2 + 25 = AB_len^2
    # x = +/- sqrt(AB_len^2 - 25)
    x_val = np.sqrt(AB_len**2 - 25)
    ax2.plot(-x_val, 0, 'bo', markersize=10, zorder=5)
    ax2.text(-x_val, 0.4, 'P5', fontsize=11, fontweight='bold', color='blue')
    
    ax2.set_xlim(-5, 8)
    ax2.set_ylim(-3, 10)
    ax2.axis('off')
    ax2.set_title('Case 2: PA = AB\n(3 points)', fontsize=12, fontweight='bold')
    
    # Case 3: PB = AB (Circle centered at B)
    ax3 = axes[2]
    ax3.set_aspect('equal')
    draw_triangle(ax3, A, B, C, labels=['A', 'B', 'C'], fill_color='lightcyan', alpha=0.2)
    draw_right_angle_mark(ax3, C, size=0.3)
    
    # Draw circle centered at B with radius AB
    circle3 = Circle(B, AB_len, fill=False, edgecolor='green', linewidth=2.5, linestyle='-')
    ax3.add_patch(circle3)
    
    # Mark intersection points
    # On line AC (x=0): (0-4)^2 + (y-0)^2 = AB_len^2
    # 16 + y^2 = AB_len^2
    # y = -sqrt(AB_len^2 - 16) (negative because A is at y=5)
    y_val = -np.sqrt(AB_len**2 - 16)
    ax3.plot(0, y_val, 'go', markersize=10, zorder=5)
    ax3.text(0.4, y_val, 'P6', fontsize=11, fontweight='bold', color='green')
    
    # On line BC (y=0): (x-4)^2 + 0 = AB_len^2
    # x = 4 +/- AB_len
    ax3.plot(4 + AB_len, 0, 'go', markersize=10, zorder=5)
    ax3.text(4 + AB_len, 0.4, 'P7', fontsize=11, fontweight='bold', color='green')
    ax3.plot(4 - AB_len, 0, 'go', markersize=10, zorder=5)
    ax3.text(4 - AB_len, 0.4, 'P8', fontsize=11, fontweight='bold', color='green')
    
    ax3.set_xlim(-5, 10)
    ax3.set_ylim(-5, 7)
    ax3.axis('off')
    ax3.set_title('Case 3: PB = AB\n(3 points)', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/rivli01/projects/homework/math/003/step2_cases.png', dpi=150,
                bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print("Step 2 completed")


def draw_step3_case1():
    """Step 3 Case 1: PA = PB (Perpendicular Bisector)"""
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    ax.set_aspect('equal')
    
    C = np.array([0, 0])
    A = np.array([0, 5])
    B = np.array([4, 0])
    
    # Draw extended lines AC and BC (dashed)
    ax.plot([0, 0], [5, 7], 'g--', alpha=0.6, linewidth=1.5)
    ax.plot([0, 0], [0, -3], 'g--', alpha=0.6, linewidth=1.5)
    ax.plot([4, 6], [0, 0], 'g--', alpha=0.6, linewidth=1.5)
    ax.plot([0, -2], [0, 0], 'g--', alpha=0.6, linewidth=1.5)
    
    draw_triangle(ax, A, B, C, labels=['A', 'B', 'C'], fill_color='lightcyan', alpha=0.2)
    draw_right_angle_mark(ax, C, size=0.4)
    
    # Calculate perpendicular bisector
    mid_AB = (A + B) / 2
    slope_AB = (B[1] - A[1]) / (B[0] - A[0])
    perp_slope = -1 / slope_AB
    
    # Draw perpendicular bisector line
    t = np.linspace(-4, 4, 100)
    perp_x = mid_AB[0] + t
    perp_y = mid_AB[1] + perp_slope * t
    ax.plot(perp_x, perp_y, 'r-', linewidth=2.5, label='Perpendicular bisector')
    
    # Mark intersection points
    t_ac = -mid_AB[0]
    p_ac_y = mid_AB[1] + perp_slope * t_ac
    ax.plot(0, p_ac_y, 'ro', markersize=14, zorder=5)
    ax.text(0.4, p_ac_y, 'P1', fontsize=12, fontweight='bold', color='red')
    
    t_bc = -mid_AB[1] / perp_slope
    p_bc_x = mid_AB[0] + t_bc
    ax.plot(p_bc_x, 0, 'ro', markersize=14, zorder=5)
    ax.text(p_bc_x, 0.4, 'P2', fontsize=12, fontweight='bold', color='red')
    
    ax.set_xlim(-3, 7)
    ax.set_ylim(-3, 7)
    ax.axis('off')
    ax.set_title('Case 1: PA = PB (2 points)', fontsize=14, fontweight='bold', pad=15)
    
    plt.tight_layout()
    plt.savefig('/home/rivli01/projects/homework/math/003/step3_case1.png', dpi=150,
                bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print("Step 3 Case 1 completed")


def draw_step3_case2():
    """Step 3 Case 2: PA = AB (Circle at A)"""
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    ax.set_aspect('equal')
    
    C = np.array([0, 0])
    A = np.array([0, 5])
    B = np.array([4, 0])
    AB_len = np.linalg.norm(B - A)
    
    # Draw extended lines AC and BC (dashed)
    ax.plot([0, 0], [5, 10], 'g--', alpha=0.6, linewidth=1.5)
    ax.plot([0, 0], [0, -4], 'g--', alpha=0.6, linewidth=1.5)
    ax.plot([4, 8], [0, 0], 'g--', alpha=0.6, linewidth=1.5)
    ax.plot([0, -4], [0, 0], 'g--', alpha=0.6, linewidth=1.5)
    
    draw_triangle(ax, A, B, C, labels=['A', 'B', 'C'], fill_color='lightcyan', alpha=0.2)
    draw_right_angle_mark(ax, C, size=0.4)
    
    # Draw circle centered at A with radius AB
    circle = Circle(A, AB_len, fill=False, edgecolor='blue', linewidth=2.5, linestyle='-')
    ax.add_patch(circle)
    
    # Mark intersection points
    ax.plot(0, A[1] + AB_len, 'bo', markersize=12, zorder=5)
    ax.text(0.4, A[1] + AB_len, 'P3', fontsize=11, fontweight='bold', color='blue')
    ax.plot(0, A[1] - AB_len, 'bo', markersize=12, zorder=5)
    ax.text(0.4, A[1] - AB_len, 'P4', fontsize=11, fontweight='bold', color='blue')
    
    x_val = np.sqrt(AB_len**2 - 25)
    ax.plot(-x_val, 0, 'bo', markersize=12, zorder=5)
    ax.text(-x_val, 0.4, 'P5', fontsize=11, fontweight='bold', color='blue')
    
    ax.set_xlim(-5, 8)
    ax.set_ylim(-4, 10)
    ax.axis('off')
    ax.set_title('Case 2: PA = AB (3 points)', fontsize=14, fontweight='bold', pad=15)
    
    plt.tight_layout()
    plt.savefig('/home/rivli01/projects/homework/math/003/step3_case2.png', dpi=150,
                bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print("Step 3 Case 2 completed")


def draw_step3_case3():
    """Step 3 Case 3: PB = AB (Circle at B)"""
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    ax.set_aspect('equal')
    
    C = np.array([0, 0])
    A = np.array([0, 5])
    B = np.array([4, 0])
    AB_len = np.linalg.norm(B - A)
    
    # Draw extended lines AC and BC (dashed)
    ax.plot([0, 0], [5, 8], 'g--', alpha=0.6, linewidth=1.5)
    ax.plot([0, 0], [0, -6], 'g--', alpha=0.6, linewidth=1.5)
    ax.plot([4, 10], [0, 0], 'g--', alpha=0.6, linewidth=1.5)
    ax.plot([0, -4], [0, 0], 'g--', alpha=0.6, linewidth=1.5)
    
    draw_triangle(ax, A, B, C, labels=['A', 'B', 'C'], fill_color='lightcyan', alpha=0.2)
    draw_right_angle_mark(ax, C, size=0.4)
    
    # Draw circle centered at B with radius AB
    circle = Circle(B, AB_len, fill=False, edgecolor='green', linewidth=2.5, linestyle='-')
    ax.add_patch(circle)
    
    # Mark intersection points
    y_val = -np.sqrt(AB_len**2 - 16)
    ax.plot(0, y_val, 'go', markersize=12, zorder=5)
    ax.text(0.4, y_val, 'P6', fontsize=11, fontweight='bold', color='green')
    
    ax.plot(4 + AB_len, 0, 'go', markersize=12, zorder=5)
    ax.text(4 + AB_len, 0.4, 'P7', fontsize=11, fontweight='bold', color='green')
    ax.plot(4 - AB_len, 0, 'go', markersize=12, zorder=5)
    ax.text(4 - AB_len, 0.4, 'P8', fontsize=11, fontweight='bold', color='green')
    
    ax.set_xlim(-5, 11)
    ax.set_ylim(-6, 8)
    ax.axis('off')
    ax.set_title('Case 3: PB = AB (3 points)', fontsize=14, fontweight='bold', pad=15)
    
    plt.tight_layout()
    plt.savefig('/home/rivli01/projects/homework/math/003/step3_case3.png', dpi=150,
                bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print("Step 3 Case 3 completed")


def draw_step3_solution():
    """Step 3: Final answer - All 8 points"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    ax.set_aspect('equal')
    
    # Triangle setup
    C = np.array([0, 0])
    A = np.array([0, 5])
    B = np.array([4, 0])
    AB_len = np.linalg.norm(B - A)
    
    # Draw extended lines AC and BC (dashed)
    ax.plot([0, 0], [5, 9], 'g--', alpha=0.6, linewidth=1.5)
    ax.plot([0, 0], [0, -5], 'g--', alpha=0.6, linewidth=1.5)
    ax.plot([4, 10], [0, 0], 'g--', alpha=0.6, linewidth=1.5)
    ax.plot([0, -4], [0, 0], 'g--', alpha=0.6, linewidth=1.5)
    
    # Draw triangle
    draw_triangle(ax, A, B, C, labels=['A', 'B', 'C'], fill_color='lightcyan', alpha=0.2)
    draw_right_angle_mark(ax, C, size=0.4)
    draw_angle_arc(ax, C, A, B, radius=0.6, color='red', label='90°')
    
    # Calculate all 8 points
    # Case 1: PA = PB (perpendicular bisector)
    mid_AB = (A + B) / 2
    slope_AB = (B[1] - A[1]) / (B[0] - A[0])
    perp_slope = -1 / slope_AB
    
    t_ac = -mid_AB[0]
    p1 = np.array([0, mid_AB[1] + perp_slope * t_ac])  # On AC
    
    t_bc = -mid_AB[1] / perp_slope
    p2 = np.array([mid_AB[0] + t_bc, 0])  # On BC
    
    # Case 2: PA = AB (circle at A)
    p3 = np.array([0, A[1] + AB_len])  # On AC extended up
    p4 = np.array([0, A[1] - AB_len])  # On AC extended down
    x_val = np.sqrt(AB_len**2 - 25)
    p5 = np.array([-x_val, 0])  # On BC extended left
    
    # Case 3: PB = AB (circle at B)
    y_val = -np.sqrt(AB_len**2 - 16)
    p6 = np.array([0, y_val])  # On AC extended down
    p7 = np.array([4 + AB_len, 0])  # On BC extended right
    p8 = np.array([4 - AB_len, 0])  # On BC extended left
    
    # Draw all points with different colors by case
    points_case1 = [p1, p2]
    points_case2 = [p3, p4, p5]
    points_case3 = [p6, p7, p8]
    
    # Draw Case 1 points (red)
    for i, p in enumerate(points_case1, 1):
        ax.plot(p[0], p[1], 'ro', markersize=14, zorder=5)
        offset = 0.4
        ax.text(p[0]+offset, p[1]+offset, f'P{i}', fontsize=12, fontweight='bold', color='red')
    
    # Draw Case 2 points (blue)
    for i, p in enumerate(points_case2, 3):
        ax.plot(p[0], p[1], 'bo', markersize=12, zorder=5)
        offset = 0.4
        ax.text(p[0]+offset, p[1]+offset, f'P{i}', fontsize=11, fontweight='bold', color='blue')
    
    # Draw Case 3 points (green)
    for i, p in enumerate(points_case3, 6):
        ax.plot(p[0], p[1], 'go', markersize=12, zorder=5)
        offset = 0.4
        ax.text(p[0]+offset, p[1]+offset, f'P{i}', fontsize=11, fontweight='bold', color='green')
    
    # Add legend
    ax.plot([], [], 'ro', markersize=10, label='PA = PB (2 points)')
    ax.plot([], [], 'bo', markersize=10, label='PA = AB (3 points)')
    ax.plot([], [], 'go', markersize=10, label='PB = AB (3 points)')
    ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
    
    # Answer box
    answer_text = 'Total: 8 points'
    ax.text(6, 8, answer_text, fontsize=18, ha='center', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='yellow', 
                     edgecolor='darkorange', linewidth=3))
    
    # Set limits
    ax.set_xlim(-5, 11)
    ax.set_ylim(-5, 11)
    ax.axis('off')
    ax.set_title('Step 3: All 8 Points P', fontsize=14, fontweight='bold', pad=15)
    
    plt.tight_layout()
    plt.savefig('/home/rivli01/projects/homework/math/003/step3_solution.png', dpi=150,
                bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print("Step 3 completed")


if __name__ == '__main__':
    draw_step1_setup()
    draw_step2_cases()
    draw_step3_case1()
    draw_step3_case2()
    draw_step3_case3()
    draw_step3_solution()
    print("All figures generated successfully!")
