import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.patches import Arc, FancyArrowPatch
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def calculate_triangle_coordinates():
    """计算三角形ABC的坐标"""
    # 已知三边：AB=12, AC=9, BC=13
    # 将B放在原点，C放在x轴上
    B = np.array([0, 0])
    C = np.array([13, 0])
    
    # 用余弦定理求角B
    cos_B = (12**2 + 13**2 - 9**2) / (2 * 12 * 13)
    sin_B = np.sqrt(1 - cos_B**2)
    
    # A点坐标
    A = np.array([12 * cos_B, 12 * sin_B])
    
    return A, B, C

def calculate_angle_bisector_point(A, B, C, vertex):
    """计算角平分线上的点"""
    if vertex == 'B':
        BA = A - B
        BC = C - B
        BA_unit = BA / np.linalg.norm(BA)
        BC_unit = BC / np.linalg.norm(BC)
        bisector_dir = BA_unit + BC_unit
        return B, bisector_dir
    elif vertex == 'C':
        CA = A - C
        CB = B - C
        CA_unit = CA / np.linalg.norm(CA)
        CB_unit = CB / np.linalg.norm(CB)
        bisector_dir = CA_unit + CB_unit
        return C, bisector_dir

def foot_of_perpendicular(P, line_point, line_dir):
    """计算点P到直线的垂足"""
    t0 = np.dot(P - line_point, line_dir) / np.dot(line_dir, line_dir)
    return line_point + t0 * line_dir

def extend_to_intersection(A, M, C):
    """延长AM交BC于P"""
    AM_dir = M - A
    if abs(AM_dir[1]) < 1e-10:
        return None
    t = -A[1] / AM_dir[1]
    P = A + t * AM_dir
    return P

def draw_step1_basic_triangle():
    """步骤1：绘制基本三角形ABC"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
    A, B, C = calculate_triangle_coordinates()
    
    # 绘制三角形ABC
    triangle = plt.Polygon([A, B, C], fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(triangle)
    
    # 标记顶点
    ax.text(A[0], A[1] + 0.5, 'A', fontsize=16, ha='center', fontweight='bold')
    ax.text(B[0] - 0.5, B[1] - 0.5, 'B', fontsize=16, ha='center', fontweight='bold')
    ax.text(C[0] + 0.5, C[1] - 0.5, 'C', fontsize=16, ha='center', fontweight='bold')
    
    # 标记边长
    mid_AB = (A + B) / 2
    mid_AC = (A + C) / 2
    mid_BC = (B + C) / 2
    
    ax.text(mid_AB[0] - 0.8, mid_AB[1] + 0.3, '12', fontsize=12, color='blue')
    ax.text(mid_AC[0] + 0.5, mid_AC[1] + 0.3, '9', fontsize=12, color='blue')
    ax.text(mid_BC[0], mid_BC[1] - 0.8, '13', fontsize=12, color='blue')
    
    ax.set_aspect('equal')
    ax.set_xlim(-2, 15)
    ax.set_ylim(-2, 10)
    ax.axis('off')
    ax.set_title('Step 1: Triangle ABC', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/rivli01/projects/homework/math/001/step1_basic.png', dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    return A, B, C

def draw_step2_with_extensions(A, B, C):
    """步骤2：绘制垂线及延长线AM->P, AN->Q"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # 计算角平分线
    _, bisector_B_dir = calculate_angle_bisector_point(A, B, C, 'B')
    _, bisector_C_dir = calculate_angle_bisector_point(A, B, C, 'C')
    
    # 计算垂足
    N = foot_of_perpendicular(A, B, bisector_B_dir)
    M = foot_of_perpendicular(A, C, bisector_C_dir)
    
    # 计算延长线与BC的交点
    P = extend_to_intersection(A, M, C)  # 延长AM交BC于P
    Q = extend_to_intersection(A, N, B)  # 延长AN交BC于Q
    
    # 绘制三角形ABC
    triangle = plt.Polygon([A, B, C], fill=False, edgecolor='black', linewidth=2.5)
    ax.add_patch(triangle)
    
    # 绘制角平分线（虚线）
    t_vals = np.linspace(-2, 12, 100)
    bisector_B_points = np.array([B + t * bisector_B_dir for t in t_vals])
    ax.plot(bisector_B_points[:, 0], bisector_B_points[:, 1], 'g--', alpha=0.4, linewidth=1.5, label='Angle bisector of B')
    
    bisector_C_points = np.array([C + t * bisector_C_dir for t in t_vals])
    ax.plot(bisector_C_points[:, 0], bisector_C_points[:, 1], 'g--', alpha=0.4, linewidth=1.5, label='Angle bisector of C')
    
    # 绘制垂线AM和AN（红色）
    ax.plot([A[0], M[0]], [A[1], M[1]], 'r-', linewidth=2.5, label='AM ⊥ bisector of C')
    ax.plot([A[0], N[0]], [A[1], N[1]], 'r-', linewidth=2.5, label='AN ⊥ bisector of B')
    
    # 绘制延长线到BC（不同颜色）
    # 延长AM到P（紫色）
    ax.plot([M[0], P[0]], [M[1], P[1]], 'm-', linewidth=2.5, alpha=0.8, label='Extend AM to P')
    ax.plot([A[0], P[0]], [A[1], P[1]], 'm--', linewidth=1.5, alpha=0.5)
    
    # 延长AN到Q（橙色）
    ax.plot([N[0], Q[0]], [N[1], Q[1]], 'orange', linewidth=2.5, alpha=0.8, label='Extend AN to Q')
    ax.plot([A[0], Q[0]], [A[1], Q[1]], 'orange', linestyle='--', linewidth=1.5, alpha=0.5)
    
    # 绘制所有点
    ax.plot(A[0], A[1], 'ko', markersize=10)
    ax.plot(B[0], B[1], 'ko', markersize=10)
    ax.plot(C[0], C[1], 'ko', markersize=10)
    ax.plot(M[0], M[1], 'ro', markersize=9)
    ax.plot(N[0], N[1], 'ro', markersize=9)
    ax.plot(P[0], P[1], 'bs', markersize=10)
    ax.plot(Q[0], Q[1], 's', color='darkorange', markersize=10)
    
    # 标记点
    ax.text(A[0], A[1] + 0.6, 'A', fontsize=16, ha='center', fontweight='bold')
    ax.text(B[0] - 0.6, B[1] - 0.6, 'B', fontsize=16, ha='center', fontweight='bold')
    ax.text(C[0] + 0.6, C[1] - 0.6, 'C', fontsize=16, ha='center', fontweight='bold')
    ax.text(M[0] + 0.6, M[1] + 0.5, 'M', fontsize=14, ha='center', color='red', fontweight='bold')
    ax.text(N[0] - 0.6, N[1] + 0.5, 'N', fontsize=14, ha='center', color='red', fontweight='bold')
    ax.text(P[0], P[1] - 0.8, 'P', fontsize=14, ha='center', color='blue', fontweight='bold')
    ax.text(Q[0], Q[1] - 0.8, 'Q', fontsize=14, ha='center', color='darkorange', fontweight='bold')
    
    # 添加图例说明
    ax.text(0.02, 0.98, 'Extend AM → P (Purple)\nExtend AN → Q (Orange)', 
            transform=ax.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    ax.set_aspect('equal')
    ax.set_xlim(-3, 17)
    ax.set_ylim(-4, 12)
    ax.axis('off')
    ax.set_title('Step 2: Perpendiculars and Extensions to BC', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/rivli01/projects/homework/math/001/step2_perpendiculars.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    
    return M, N, P, Q

def draw_step3_with_bisectors(A, B, C, M, N, P, Q):
    """步骤3：保留角B、角C平分线，显示PQ长度"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # 计算角平分线
    _, bisector_B_dir = calculate_angle_bisector_point(A, B, C, 'B')
    _, bisector_C_dir = calculate_angle_bisector_point(A, B, C, 'C')
    
    # 绘制三角形ABC
    triangle = plt.Polygon([A, B, C], fill=False, edgecolor='black', linewidth=2.5)
    ax.add_patch(triangle)
    
    # 绘制角平分线（绿色实线，更明显）
    t_vals = np.linspace(-2, 12, 100)
    bisector_B_points = np.array([B + t * bisector_B_dir for t in t_vals])
    ax.plot(bisector_B_points[:, 0], bisector_B_points[:, 1], 'g-', alpha=0.6, linewidth=2, label='Bisector of ∠B')
    
    bisector_C_points = np.array([C + t * bisector_C_dir for t in t_vals])
    ax.plot(bisector_C_points[:, 0], bisector_C_points[:, 1], 'g-', alpha=0.6, linewidth=2, label='Bisector of ∠C')
    
    # 绘制延长线AP和AQ
    ax.plot([A[0], P[0]], [A[1], P[1]], 'm-', linewidth=2, alpha=0.7)
    ax.plot([A[0], Q[0]], [A[1], Q[1]], 'orange', linewidth=2, alpha=0.7)
    
    # 绘制MN
    ax.plot([M[0], N[0]], [M[1], N[1]], 'red', linewidth=2.5, linestyle='-')
    
    # 高亮显示PQ段
    ax.plot([P[0], Q[0]], [P[1], Q[1]], 'purple', linewidth=4, alpha=0.6)
    
    # 绘制所有点
    ax.plot(A[0], A[1], 'ko', markersize=10)
    ax.plot(B[0], B[1], 'ko', markersize=10)
    ax.plot(C[0], C[1], 'ko', markersize=10)
    ax.plot(N[0], N[1], 'ro', markersize=8)
    ax.plot(M[0], M[1], 'ro', markersize=8)
    ax.plot(P[0], P[1], 'bs', markersize=9)
    ax.plot(Q[0], Q[1], 's', color='darkorange', markersize=9)
    
    # 标记点
    ax.text(A[0], A[1] + 0.6, 'A', fontsize=16, ha='center', fontweight='bold')
    ax.text(B[0] - 0.6, B[1] - 0.6, 'B', fontsize=16, ha='center', fontweight='bold')
    ax.text(C[0] + 0.6, C[1] - 0.6, 'C', fontsize=16, ha='center', fontweight='bold')
    ax.text(N[0] - 0.6, N[1] + 0.6, 'N', fontsize=14, ha='center', color='red', fontweight='bold')
    ax.text(M[0] + 0.6, M[1] + 0.6, 'M', fontsize=14, ha='center', color='red', fontweight='bold')
    ax.text(P[0], P[1] - 0.9, 'P', fontsize=14, ha='center', color='blue', fontweight='bold')
    ax.text(Q[0], Q[1] - 0.9, 'Q', fontsize=14, ha='center', color='darkorange', fontweight='bold')
    
    # 标记MN
    mid_MN = (M + N) / 2
    ax.text(mid_MN[0], mid_MN[1] + 0.5, 'MN', fontsize=12, color='red', fontweight='bold')
    
    # 标记距离（带背景框）
    ax.text((B[0] + Q[0])/2, B[1] - 1.0, 'QB=12', fontsize=11, color='green', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
    ax.text((C[0] + P[0])/2, C[1] - 1.0, 'PC=9', fontsize=11, color='green', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
    ax.text((P[0] + Q[0])/2, P[1] - 1.5, 'PQ=8', fontsize=13, color='purple', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='plum', alpha=0.8))
    
    # 添加说明
    ax.text(0.02, 0.98, 'Green lines: Angle bisectors of B and C', 
            transform=ax.transAxes, fontsize=10, verticalalignment='top', color='green',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))
    
    ax.set_aspect('equal')
    ax.set_xlim(-3, 17)
    ax.set_ylim(-4, 12)
    ax.axis('off')
    ax.set_title('Step 3: Angle Bisectors and PQ = 8', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/rivli01/projects/homework/math/001/step3_extension.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

def draw_step4_midsegment(A, B, C, M, N, P, Q):
    """步骤4：中位线定理配图"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # 绘制三角形ABC（浅色背景）
    triangle_ABC = plt.Polygon([A, B, C], fill=True, facecolor='lightblue', edgecolor='black', 
                               linewidth=2, alpha=0.2)
    ax.add_patch(triangle_ABC)
    
    # 绘制三角形APQ（中等亮度）
    triangle_APQ = plt.Polygon([A, P, Q], fill=True, facecolor='lightyellow', edgecolor='orange', 
                               linewidth=2, alpha=0.5)
    ax.add_patch(triangle_APQ)
    
    # 绘制AP和AQ线
    ax.plot([A[0], P[0]], [A[1], P[1]], 'orange', linewidth=2, alpha=0.6)
    ax.plot([A[0], Q[0]], [A[1], Q[1]], 'orange', linewidth=2, alpha=0.6)
    
    # 绘制PQ线
    ax.plot([P[0], Q[0]], [P[1], Q[1]], 'purple', linewidth=3, alpha=0.7)
    
    # 绘制MN（红色粗线，高亮中位线）
    ax.plot([M[0], N[0]], [M[1], N[1]], 'red', linewidth=4)
    
    # 标记中点
    ax.plot(M[0], M[1], 'ro', markersize=12)
    ax.plot(N[0], N[1], 'ro', markersize=12)
    
    # 绘制所有点
    ax.plot(A[0], A[1], 'ko', markersize=10)
    ax.plot(B[0], B[1], 'ko', markersize=8, alpha=0.5)
    ax.plot(C[0], C[1], 'ko', markersize=8, alpha=0.5)
    ax.plot(P[0], P[1], 'bs', markersize=9)
    ax.plot(Q[0], Q[1], 's', color='darkorange', markersize=9)
    
    # 标记点
    ax.text(A[0], A[1] + 0.6, 'A', fontsize=16, ha='center', fontweight='bold')
    ax.text(B[0] - 0.5, B[1] - 0.5, 'B', fontsize=12, ha='center', alpha=0.6)
    ax.text(C[0] + 0.5, C[1] - 0.5, 'C', fontsize=12, ha='center', alpha=0.6)
    ax.text(P[0], P[1] - 0.9, 'P', fontsize=14, ha='center', color='blue', fontweight='bold')
    ax.text(Q[0], Q[1] - 0.9, 'Q', fontsize=14, ha='center', color='darkorange', fontweight='bold')
    ax.text(M[0] + 0.7, M[1] + 0.4, 'M\n(midpoint)', fontsize=11, ha='center', color='red', fontweight='bold')
    ax.text(N[0] - 0.7, N[1] + 0.4, 'N\n(midpoint)', fontsize=11, ha='center', color='red', fontweight='bold')
    
    # 标记MN和PQ
    mid_MN = (M + N) / 2
    ax.text(mid_MN[0] - 1.0, mid_MN[1] + 0.6, 'MN', fontsize=14, color='red', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
    
    mid_PQ = (P + Q) / 2
    ax.text(mid_PQ[0], mid_PQ[1] - 1.2, 'PQ = 8', fontsize=13, color='purple', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='plum', alpha=0.7))
    
    # 添加中位线定理说明
    ax.text(0.5, 0.95, 'Midsegment Theorem: MN = ½PQ = 4', 
            transform=ax.transAxes, fontsize=14, ha='center', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9, edgecolor='orange', linewidth=2))
    
    # 添加相似比说明
    ax.text(0.5, 0.05, '△AMN ~ △APQ with ratio 1:2', 
            transform=ax.transAxes, fontsize=12, ha='center', style='italic',
            bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8))
    
    ax.set_aspect('equal')
    ax.set_xlim(-3, 17)
    ax.set_ylim(-4, 12)
    ax.axis('off')
    ax.set_title('Step 4: Midsegment Theorem - MN is parallel to PQ and MN = ½PQ', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/rivli01/projects/homework/math/001/step4_midsegment.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

def draw_step5_area_ratio(A, B, C, M, N, P, Q):
    """步骤5：面积比计算配图"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # 绘制三角形ABC（浅色背景）
    triangle_ABC = plt.Polygon([A, B, C], fill=True, facecolor='lightblue', edgecolor='blue', 
                               linewidth=2.5, alpha=0.25)
    ax.add_patch(triangle_ABC)
    
    # 绘制三角形APQ（中等亮度）
    triangle_APQ = plt.Polygon([A, P, Q], fill=True, facecolor='lightyellow', edgecolor='orange', 
                               linewidth=2, alpha=0.5)
    ax.add_patch(triangle_APQ)
    
    # 绘制三角形AMN（高亮）
    triangle_AMN = plt.Polygon([A, M, N], fill=True, facecolor='lightgreen', edgecolor='green', 
                               linewidth=2.5, alpha=0.7)
    ax.add_patch(triangle_AMN)
    
    # 绘制各边
    ax.plot([A[0], P[0]], [A[1], P[1]], 'orange', linewidth=1.5, alpha=0.5)
    ax.plot([A[0], Q[0]], [A[1], Q[1]], 'orange', linewidth=1.5, alpha=0.5)
    ax.plot([P[0], Q[0]], [P[1], Q[1]], 'purple', linewidth=2, alpha=0.6)
    ax.plot([M[0], N[0]], [M[1], N[1]], 'green', linewidth=3)
    
    # 绘制所有点
    ax.plot(A[0], A[1], 'ko', markersize=11)
    ax.plot(B[0], B[1], 'ko', markersize=7, alpha=0.5)
    ax.plot(C[0], C[1], 'ko', markersize=7, alpha=0.5)
    ax.plot(P[0], P[1], 'bs', markersize=8, alpha=0.6)
    ax.plot(Q[0], Q[1], 's', color='darkorange', markersize=8, alpha=0.6)
    ax.plot(M[0], M[1], 'go', markersize=10)
    ax.plot(N[0], N[1], 'go', markersize=10)
    
    # 标记点
    ax.text(A[0], A[1] + 0.6, 'A', fontsize=16, ha='center', fontweight='bold')
    ax.text(B[0] - 0.5, B[1] - 0.5, 'B', fontsize=11, ha='center', alpha=0.5)
    ax.text(C[0] + 0.5, C[1] - 0.5, 'C', fontsize=11, ha='center', alpha=0.5)
    ax.text(M[0] + 0.6, M[1] + 0.4, 'M', fontsize=12, ha='center', color='green', fontweight='bold')
    ax.text(N[0] - 0.6, N[1] + 0.4, 'N', fontsize=12, ha='center', color='green', fontweight='bold')
    
    # 添加面积比公式框
    formula_text = r'$\frac{S_{\triangle AMN}}{S_{\triangle APQ}} = \frac{1}{4}$' + '\n' + \
                   r'$\frac{S_{\triangle APQ}}{S_{\triangle ABC}} = \frac{8}{13}$' + '\n' + \
                   r'$\frac{S_{\triangle AMN}}{S_{\triangle ABC}} = \frac{1}{4} \times \frac{8}{13} = \frac{2}{13}$'
    
    ax.text(0.98, 0.98, formula_text, 
            transform=ax.transAxes, fontsize=13, verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.95, edgecolor='darkgreen', linewidth=2))
    
    # 添加图例说明各三角形
    legend_elements = [
        patches.Patch(facecolor='lightgreen', edgecolor='green', alpha=0.7, label='△AMN (Target)'),
        patches.Patch(facecolor='lightyellow', edgecolor='orange', alpha=0.5, label='△APQ'),
        patches.Patch(facecolor='lightblue', edgecolor='blue', alpha=0.25, label='△ABC')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=11)
    
    ax.set_aspect('equal')
    ax.set_xlim(-3, 17)
    ax.set_ylim(-4, 12)
    ax.axis('off')
    ax.set_title('Step 5: Area Ratio Calculation', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/rivli01/projects/homework/math/001/step5_area_ratio.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

def draw_step6_final(A, B, C, M, N, P, Q):
    """步骤6：最终答案配图"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # 绘制三角形ABC（浅色）
    triangle_ABC = plt.Polygon([A, B, C], fill=True, facecolor='lightblue', edgecolor='black', 
                               linewidth=2, alpha=0.25)
    ax.add_patch(triangle_ABC)
    
    # 绘制三角形AMN（高亮）
    triangle_AMN = plt.Polygon([A, M, N], fill=True, facecolor='lightgreen', edgecolor='darkgreen', 
                               linewidth=3, alpha=0.8)
    ax.add_patch(triangle_AMN)
    
    # 绘制MN
    ax.plot([M[0], N[0]], [M[1], N[1]], 'darkgreen', linewidth=3.5)
    
    # 绘制延长线（虚线）
    ax.plot([A[0], P[0]], [A[1], P[1]], 'm--', linewidth=1, alpha=0.4)
    ax.plot([A[0], Q[0]], [A[1], Q[1]], 'orange', linestyle='--', linewidth=1, alpha=0.4)
    
    # 绘制所有点
    ax.plot(A[0], A[1], 'ko', markersize=12)
    ax.plot(B[0], B[1], 'ko', markersize=7, alpha=0.5)
    ax.plot(C[0], C[1], 'ko', markersize=7, alpha=0.5)
    ax.plot(N[0], N[1], 'go', markersize=10)
    ax.plot(M[0], M[1], 'go', markersize=10)
    ax.plot(P[0], P[1], 'bs', markersize=6, alpha=0.5)
    ax.plot(Q[0], Q[1], 's', color='darkorange', markersize=6, alpha=0.5)
    
    # 标记点
    ax.text(A[0], A[1] + 0.7, 'A', fontsize=16, ha='center', fontweight='bold')
    ax.text(B[0] - 0.5, B[1] - 0.5, 'B', fontsize=11, ha='center', alpha=0.5)
    ax.text(C[0] + 0.5, C[1] - 0.5, 'C', fontsize=11, ha='center', alpha=0.5)
    ax.text(N[0] - 0.6, N[1] + 0.5, 'N', fontsize=12, ha='center', color='green', fontweight='bold')
    ax.text(M[0] + 0.6, M[1] + 0.5, 'M', fontsize=12, ha='center', color='green', fontweight='bold')
    
    # 添加最终答案框
    answer_text = r'$\frac{S_{\triangle AMN}}{S_{\triangle ABC}} = \frac{2}{13}$'
    ax.text(0.5, 0.5, answer_text, 
            transform=ax.transAxes, fontsize=36, ha='center', va='center', fontweight='bold', color='darkgreen',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.9, edgecolor='darkgreen', linewidth=3))
    
    ax.set_aspect('equal')
    ax.set_xlim(-3, 17)
    ax.set_ylim(-4, 12)
    ax.axis('off')
    ax.set_title('Final Answer', fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/rivli01/projects/homework/math/001/step6_final.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

# 生成所有图形
if __name__ == '__main__':
    print("Generating geometric figures...")
    
    # 步骤1：基本三角形
    A, B, C = draw_step1_basic_triangle()
    print("Step 1 completed: Basic triangle")
    
    # 步骤2：垂线及延长线
    M, N, P, Q = draw_step2_with_extensions(A, B, C)
    print("Step 2 completed: Perpendiculars with extensions")
    
    # 步骤3：保留角平分线
    draw_step3_with_bisectors(A, B, C, M, N, P, Q)
    print("Step 3 completed: With angle bisectors")
    
    # 步骤4：中位线定理
    draw_step4_midsegment(A, B, C, M, N, P, Q)
    print("Step 4 completed: Midsegment theorem")
    
    # 步骤5：面积比
    draw_step5_area_ratio(A, B, C, M, N, P, Q)
    print("Step 5 completed: Area ratio")
    
    # 步骤6：最终答案
    draw_step6_final(A, B, C, M, N, P, Q)
    print("Step 6 completed: Final answer")
    
    print("\nAll figures generated successfully!")
