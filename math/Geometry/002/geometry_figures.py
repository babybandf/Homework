import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.patches import Arc
import os

# 设置中文字体 - 尝试使用系统可用字体
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'SimHei', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

def draw_step1_problem():
    """Step 1: Problem illustration - Isosceles triangles"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Left: Acute isosceles triangle
    ax1 = axes[0]
    apex1 = np.array([5, 4])
    base1_left = np.array([2, 0])
    base1_right = np.array([8, 0])
    
    triangle1 = plt.Polygon([apex1, base1_left, base1_right], 
                            fill=True, facecolor='lightblue', edgecolor='black', linewidth=2)
    ax1.add_patch(triangle1)
    
    ax1.text(5, 4.3, 'Apex', fontsize=12, ha='center')
    ax1.text(1.5, 0.3, 'Base', fontsize=12, ha='center')
    ax1.text(8.5, 0.3, 'Base', fontsize=12, ha='center')
    
    ax1.set_aspect('equal')
    ax1.set_xlim(0, 10)
    ax1.set_ylim(-1, 6)
    ax1.axis('off')
    ax1.set_title('Acute Isosceles\n(Apex < 90°)', fontsize=12, fontweight='bold')
    
    # Middle: Right isosceles triangle
    ax2 = axes[1]
    apex2 = np.array([5, 5])
    base2_left = np.array([2, 2])
    base2_right = np.array([8, 2])
    
    triangle2 = plt.Polygon([apex2, base2_left, base2_right], 
                            fill=True, facecolor='lightyellow', edgecolor='black', linewidth=2)
    ax2.add_patch(triangle2)
    
    # Right angle mark
    ax2.plot([5, 5], [5, 4.2], 'k-', linewidth=1.5)
    ax2.plot([5, 5.8], [5, 5], 'k-', linewidth=1.5)
    
    ax2.text(5, 5.5, '90°', fontsize=14, ha='center', fontweight='bold')
    ax2.text(1.5, 2.3, '45°', fontsize=12, ha='center')
    ax2.text(8.2, 2.3, '45°', fontsize=12, ha='center')
    
    ax2.set_aspect('equal')
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 7)
    ax2.axis('off')
    ax2.set_title('Right Isosceles\n(Apex = 90°)', fontsize=12, fontweight='bold')
    
    # Right: Obtuse isosceles triangle
    ax3 = axes[2]
    apex3 = np.array([5, 2])
    base3_left = np.array([1, 5])
    base3_right = np.array([9, 5])
    
    triangle3 = plt.Polygon([apex3, base3_left, base3_right], 
                            fill=True, facecolor='lightcoral', edgecolor='black', linewidth=2)
    ax3.add_patch(triangle3)
    
    ax3.text(5, 1.2, 'Apex > 90°', fontsize=12, ha='center', color='red', fontweight='bold')
    ax3.text(0.5, 5.5, 'Base', fontsize=12, ha='center')
    ax3.text(9.3, 5.5, 'Base', fontsize=12, ha='center')
    
    ax3.set_aspect('equal')
    ax3.set_xlim(-1, 11)
    ax3.set_ylim(0, 7)
    ax3.axis('off')
    ax3.set_title('Obtuse Isosceles\n(Apex > 90°)', fontsize=12, fontweight='bold', color='red')
    
    plt.tight_layout()
    plt.savefig('/home/rivli01/projects/homework/math/002/step1_problem.png', dpi=150, 
                bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print("Step 1 completed: Problem illustration")

def draw_step2_analysis():
    """Step 2: Angle analysis"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
    # Draw isosceles triangle with angle labels
    apex = np.array([5, 6])
    base_left = np.array([1, 1])
    base_right = np.array([9, 1])
    
    triangle = plt.Polygon([apex, base_left, base_right], 
                          fill=True, facecolor='lightgreen', edgecolor='black', 
                          linewidth=2.5, alpha=0.3)
    ax.add_patch(triangle)
    
    # Draw angle marks
    # Apex angle
    arc_top = Arc((5, 6), 1.5, 1.5, angle=0, theta1=250, theta2=290, color='red', linewidth=2)
    ax.add_patch(arc_top)
    
    # Base angles
    arc_left = Arc((1, 1), 1.5, 1.5, angle=0, theta1=30, theta2=70, color='blue', linewidth=2)
    ax.add_patch(arc_left)
    
    arc_right = Arc((9, 1), 1.5, 1.5, angle=0, theta1=110, theta2=150, color='blue', linewidth=2)
    ax.add_patch(arc_right)
    
    # Label angles
    ax.text(5, 6.8, 'Apex = b', fontsize=14, ha='center', fontweight='bold', color='red')
    ax.text(0.2, 1.8, 'Base = a', fontsize=14, ha='center', fontweight='bold', color='blue')
    ax.text(9.8, 1.8, 'Base = a', fontsize=14, ha='center', fontweight='bold', color='blue')
    
    # Add formula
    ax.text(5, 4, '2a + b = 180°', fontsize=16, ha='center', 
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
    ax.text(5, 3, 'a < b (given)', fontsize=14, ha='center', 
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    ax.set_aspect('equal')
    ax.set_xlim(-1, 11)
    ax.set_ylim(0, 9)
    ax.axis('off')
    ax.set_title('Step 2: Angle Relationship Analysis', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/rivli01/projects/homework/math/002/step2_analysis.png', dpi=150,
                bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print("Step 2 completed: Angle analysis")

def draw_step3_critical_point():
    """Step 3: Critical point analysis"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left: Right angle case (critical)
    ax1 = axes[0]
    apex1 = np.array([5, 5])
    base1_left = np.array([0, 0])
    base1_right = np.array([10, 0])
    
    triangle1 = plt.Polygon([apex1, base1_left, base1_right], 
                            fill=True, facecolor='lightyellow', edgecolor='black', linewidth=2)
    ax1.add_patch(triangle1)
    
    # Mark right angle
    ax1.plot([5, 5], [5, 4.2], 'k-', linewidth=1.5)
    ax1.plot([5, 5.8], [5, 5], 'k-', linewidth=1.5)
    
    ax1.text(5, 5.5, '90°', fontsize=14, ha='center', fontweight='bold')
    ax1.text(-0.5, 0.5, '45°', fontsize=12, ha='center')
    ax1.text(10.5, 0.5, '45°', fontsize=12, ha='center')
    
    ax1.text(5, 2.5, 'Critical: b = 90°, a = 45°\nb/a = 2', fontsize=12, ha='center',
            bbox=dict(boxstyle='round', facecolor='orange', alpha=0.7))
    
    ax1.set_aspect('equal')
    ax1.set_xlim(-2, 12)
    ax1.set_ylim(-1, 7)
    ax1.axis('off')
    ax1.set_title('Critical Case: Right Isosceles', fontsize=12, fontweight='bold')
    
    # Right: Obtuse case
    ax2 = axes[1]
    apex2 = np.array([5, 2])
    base2_left = np.array([0, 6])
    base2_right = np.array([10, 6])
    
    triangle2 = plt.Polygon([apex2, base2_left, base2_right], 
                            fill=True, facecolor='lightcoral', edgecolor='black', linewidth=2)
    ax2.add_patch(triangle2)
    
    # Mark obtuse angle
    arc = Arc((5, 2), 2, 2, angle=0, theta1=45, theta2=135, color='red', linewidth=3)
    ax2.add_patch(arc)
    
    ax2.text(5, 0.8, 'b > 90°', fontsize=14, ha='center', fontweight='bold', color='red')
    ax2.text(-0.8, 6.5, 'a < 45°', fontsize=12, ha='center', color='blue')
    ax2.text(10.5, 6.5, 'a < 45°', fontsize=12, ha='center', color='blue')
    
    ax2.text(5, 4, 'Obtuse: b > 90°, a < 45°\nb/a > 2', fontsize=12, ha='center',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
    
    ax2.set_aspect('equal')
    ax2.set_xlim(-2, 12)
    ax2.set_ylim(-1, 8)
    ax2.axis('off')
    ax2.set_title('Target Case: Obtuse Isosceles', fontsize=12, fontweight='bold', color='red')
    
    plt.tight_layout()
    plt.savefig('/home/rivli01/projects/homework/math/002/step3_critical.png', dpi=150,
                bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print("Step 3 completed: Critical point analysis")

def draw_step4_solution():
    """Step 4: Final solution"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Draw number line
    ax.axhline(y=5, color='black', linewidth=2)
    
    # Mark critical point
    ax.plot(2, 5, 'ro', markersize=15)
    ax.text(2, 4.3, '2\n(Critical)', fontsize=14, ha='center', fontweight='bold')
    
    # Draw solution interval
    ax.plot([2, 10], [5, 5], 'g-', linewidth=8, alpha=0.5, label='Solution: b/a > 2')
    
    # Arrow for infinity
    ax.annotate('', xy=(10, 5), xytext=(9.5, 5),
                arrowprops=dict(arrowstyle='->', color='green', lw=3))
    
    # Label region
    ax.text(6, 5.8, 'b/a > 2', fontsize=18, ha='center', fontweight='bold', color='green')
    ax.text(6, 6.5, 'Solution Interval', fontsize=14, ha='center', color='green')
    
    # Left infeasible region
    ax.plot([0, 2], [5, 5], 'r--', linewidth=4, alpha=0.5)
    ax.text(1, 4.3, 'Acute/Right\n(Invalid)', fontsize=10, ha='center', color='red')
    
    ax.set_xlim(0, 11)
    ax.set_ylim(3, 8)
    ax.axis('off')
    ax.set_title('Step 4: Range of b/a', fontsize=16, fontweight='bold')
    
    # Answer box
    answer_text = 'Answer: b/a > 2\nOr (2, +∞)'
    ax.text(5.5, 2, answer_text, fontsize=20, ha='center', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', 
                     edgecolor='darkgreen', linewidth=3))
    
    plt.tight_layout()
    plt.savefig('/home/rivli01/projects/homework/math/002/step4_solution.png', dpi=150,
                bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print("Step 4 completed: Final solution")

# Generate all figures
if __name__ == '__main__':
    print("Generating geometric figures for problem 002...")
    
    draw_step1_problem()
    draw_step2_analysis()
    draw_step3_critical_point()
    draw_step4_solution()
    
    print("\nAll figures generated successfully!")
