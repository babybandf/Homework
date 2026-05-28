import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.patches import Arc, Circle
import os

# 设置字体
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

def draw_step1_setup():
    """Step 1: Problem setup"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
    # Draw right triangle ABC
    C = np.array([0, 0])
    A = np.array([0, 6])
    B = np.array([4, 0])
    
    triangle = plt.Polygon([A, B, C], fill=True, facecolor='lightblue', 
                          edgecolor='black', linewidth=2, alpha=0.3)
    ax.add_patch(triangle)
    
    # Draw right angle mark
    ax.plot([0, 0.5], [0, 0], 'k-', linewidth=1)
    ax.plot([0, 0], [0, 0.5], 'k-', linewidth=1)
    
    # Label vertices
    ax.text(A[0]-0.5, A[1]+0.3, 'A', fontsize=16, ha='center', fontweight='bold')
    ax.text(B[0]+0.3, B[1]-0.5, 'B', fontsize=16, ha='center', fontweight='bold')
    ax.text(C[0]-0.5, C[1]-0.5, 'C', fontsize=16, ha='center', fontweight='bold')
    
    # Mark right angle
    ax.text(0.3, 0.3, '90°', fontsize=12, ha='center')
    
    # Extend lines AC and BC
    ax.plot([0, 0], [6, 8], 'g--', alpha=0.5, linewidth=1)
    ax.plot([0, 0], [0, -3], 'g--', alpha=0.5, linewidth=1)
    ax.plot([4, 7], [0, 0], 'g--', alpha=0.5, linewidth=1)
    ax.plot([0, -3], [0, 0], 'g--', alpha=0.5, linewidth=1)
    
    # Label lines
    ax.text(-0.5, 7.5, 'Line AC', fontsize=11, color='green', rotation=90)
    ax.text(7, -0.5, 'Line BC', fontsize=11, color='green')
    
    ax.set_aspect('equal')
    ax.set_xlim(-4, 9)
    ax.set_ylim(-4, 9)
    ax.axis('off')
    ax.set_title('Step 1: Right Triangle ABC', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/rivli01/projects/homework/math/003/step1_setup.png', dpi=150,
                bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print("Step 1 completed")

def draw_step2_cases():
    """Step 2: Three cases of isosceles triangle"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    C = np.array([0, 0])
    A = np.array([0, 5])
    B = np.array([4, 0])
    
    # Case 1: PA = PB
    ax1 = axes[0]
    triangle1 = plt.Polygon([A, B, C], fill=True, facecolor='lightblue', 
                           edgecolor='black', linewidth=1.5, alpha=0.2)
    ax1.add_patch(triangle1)
    
    # Draw perpendicular bisector of AB
    mid_AB = (A + B) / 2
    slope_AB = (B[1] - A[1]) / (B[0] - A[0])
    perp_slope = -1 / slope_AB
    
    # Draw perpendicular bisector line
    t = np.linspace(-3, 3, 100)
    perp_x = mid_AB[0] + t
    perp_y = mid_AB[1] + perp_slope * t
    ax1.plot(perp_x, perp_y, 'r-', linewidth=2, label='Perpendicular bisector')
    
    # Mark intersection points
    ax1.plot(0, 2.5, 'ro', markersize=10)  # Intersection with AC
    ax1.plot(2, 0, 'ro', markersize=10)    # Intersection with BC
    
    ax1.text(A[0]-0.5, A[1]+0.3, 'A', fontsize=12, ha='center')
    ax1.text(B[0]+0.3, B[1]-0.5, 'B', fontsize=12, ha='center')
    ax1.text(C[0]-0.5, C[1]-0.5, 'C', fontsize=12, ha='center')
    
    ax1.set_aspect('equal')
    ax1.set_xlim(-3, 7)
    ax1.set_ylim(-3, 7)
    ax1.axis('off')
    ax1.set_title('Case 1: PA = PB\n(2 points)', fontsize=12, fontweight='bold')
    
    # Case 2: PA = AB
    ax2 = axes[1]
    triangle2 = plt.Polygon([A, B, C], fill=True, facecolor='lightblue', 
                           edgecolor='black', linewidth=1.5, alpha=0.2)
    ax2.add_patch(triangle2)
    
    # Draw circle centered at A with radius AB
    AB_len = np.linalg.norm(B - A)
    circle2 = Circle(A, AB_len, fill=False, edgecolor='red', linewidth=2)
    ax2.add_patch(circle2)
    
    # Mark intersection points
    ax2.plot(0, 5+AB_len, 'ro', markersize=8)
    ax2.plot(0, 5-AB_len, 'ro', markersize=8)
    ax2.plot(-3, 0, 'ro', markersize=8)
    
    ax2.text(A[0]-0.5, A[1]+0.3, 'A', fontsize=12, ha='center')
    ax2.text(B[0]+0.3, B[1]-0.5, 'B', fontsize=12, ha='center')
    ax2.text(C[0]-0.5, C[1]-0.5, 'C', fontsize=12, ha='center')
    
    ax2.set_aspect('equal')
    ax2.set_xlim(-5, 8)
    ax2.set_ylim(-3, 10)
    ax2.axis('off')
    ax2.set_title('Case 2: PA = AB\n(3 points)', fontsize=12, fontweight='bold')
    
    # Case 3: PB = AB
    ax3 = axes[2]
    triangle3 = plt.Polygon([A, B, C], fill=True, facecolor='lightblue', 
                           edgecolor='black', linewidth=1.5, alpha=0.2)
    ax3.add_patch(triangle3)
    
    # Draw circle centered at B with radius AB
    circle3 = Circle(B, AB_len, fill=False, edgecolor='red', linewidth=2)
    ax3.add_patch(circle3)
    
    # Mark intersection points
    ax3.plot(0, -3, 'ro', markersize=8)
    ax3.plot(4+AB_len, 0, 'ro', markersize=8)
    ax3.plot(4-AB_len, 0, 'ro', markersize=8)
    
    ax3.text(A[0]-0.5, A[1]+0.3, 'A', fontsize=12, ha='center')
    ax3.text(B[0]+0.3, B[1]-0.5, 'B', fontsize=12, ha='center')
    ax3.text(C[0]-0.5, C[1]-0.5, 'C', fontsize=12, ha='center')
    
    ax3.set_aspect('equal')
    ax3.set_xlim(-5, 10)
    ax3.set_ylim(-5, 7)
    ax3.axis('off')
    ax3.set_title('Case 3: PB = AB\n(3 points)', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/rivli01/projects/homework/math/003/step2_cases.png', dpi=150,
                bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print("Step 2 completed")

def draw_step3_solution():
    """Step 3: Final answer"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
    C = np.array([0, 0])
    A = np.array([0, 5])
    B = np.array([4, 0])
    
    # Draw triangle
    triangle = plt.Polygon([A, B, C], fill=True, facecolor='lightblue', 
                          edgecolor='black', linewidth=2, alpha=0.3)
    ax.add_patch(triangle)
    
    # Draw all 8 points
    points = [
        (0, 2.5),      # PA=PB on AC
        (2, 0),        # PA=PB on BC
        (0, 9),        # PA=AB on AC extended
        (0, 1),        # PA=AB on CA extended
        (-3, 0),       # PA=AB on BC extended
        (0, -3),       # PB=AB on AC extended
        (8, 0),        # PB=AB on BC extended
        (-2, 0),       # PB=AB on CB extended
    ]
    
    for i, (x, y) in enumerate(points):
        color = 'red' if i < 2 else ('green' if i < 5 else 'blue')
        ax.plot(x, y, 'o', color=color, markersize=10)
        ax.text(x+0.3, y+0.3, f'P{i+1}', fontsize=10, fontweight='bold')
    
    ax.text(A[0]-0.5, A[1]+0.3, 'A', fontsize=14, ha='center', fontweight='bold')
    ax.text(B[0]+0.3, B[1]-0.5, 'B', fontsize=14, ha='center', fontweight='bold')
    ax.text(C[0]-0.5, C[1]-0.5, 'C', fontsize=14, ha='center', fontweight='bold')
    
    # Legend
    ax.plot([], [], 'ro', markersize=8, label='PA=PB (2 points)')
    ax.plot([], [], 'go', markersize=8, label='PA=AB (3 points)')
    ax.plot([], [], 'bo', markersize=8, label='PB=AB (3 points)')
    ax.legend(loc='upper right', fontsize=10)
    
    # Answer box
    answer_text = 'Total: 8 points'
    ax.text(5, 7, answer_text, fontsize=20, ha='center', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', 
                     edgecolor='darkgreen', linewidth=3))
    
    ax.set_aspect('equal')
    ax.set_xlim(-5, 10)
    ax.set_ylim(-5, 9)
    ax.axis('off')
    ax.set_title('Step 3: All 8 Points P', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/rivli01/projects/homework/math/003/step3_solution.png', dpi=150,
                bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print("Step 3 completed")

# Generate all figures
if __name__ == '__main__':
    print("Generating geometric figures for problem 003...")
    
    draw_step1_setup()
    draw_step2_cases()
    draw_step3_solution()
    
    print("\nAll figures generated successfully!")
