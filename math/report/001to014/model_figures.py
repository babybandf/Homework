"""
Generate illustrative figures for the 5 core geometry models
described in geometry_mastery_report.md.

Output: math/model_assets/model{1-5}_*.png
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ========== Chinese font support ==========
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_FONT_PATH = None
_search = _BASE_DIR
for _ in range(6):
    _candidate = os.path.join(_search, 'font', 'STHeiti Medium.ttc')
    if os.path.exists(_candidate):
        _FONT_PATH = _candidate
        break
    _search = os.path.dirname(_search)

if _FONT_PATH:
    font_manager.fontManager.addfont(_FONT_PATH)
    plt.rcParams['font.family'] = 'Heiti TC'
plt.rcParams['axes.unicode_minus'] = False

_TEXT_BOX = dict(facecolor='white', edgecolor='none', alpha=0.78, pad=0.12)
OUT_DIR = os.path.join(_BASE_DIR, 'model_assets')
os.makedirs(OUT_DIR, exist_ok=True)

def compute_visual_scale(ax):
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    return min(abs(x1 - x0), abs(y1 - y0))

def autoscale(ax, key_points, margin=0.25):
    pts = np.array(key_points)
    xmin, ymin = pts.min(axis=0)
    xmax, ymax = pts.max(axis=0)
    dx = xmax - xmin
    dy = ymax - ymin
    ax.set_xlim(xmin - margin * max(dx, dy), xmax + margin * max(dx, dy))
    ax.set_ylim(ymin - margin * max(dx, dy), ymax + margin * max(dx, dy))
    ax.set_aspect('equal')

def label_point(ax, P, name, direction, scale, offset_ratio=0.06,
                fontsize=14, color='black'):
    d = np.array(direction, dtype=float)
    d = d / (np.linalg.norm(d) + 1e-9) * (scale * offset_ratio)
    anchor = np.array([P[0] + d[0], P[1] + d[1]])
    ax.plot(P[0], P[1], 'o', color=color, markersize=5, zorder=10)
    ax.text(anchor[0], anchor[1], name, ha='center', va='center',
            fontsize=fontsize, fontweight='bold', color=color,
            bbox=_TEXT_BOX, zorder=12)

def draw_right_angle(ax, vertex, dir1, dir2, size, color='black', lw=1.5):
    d1 = np.asarray(dir1, dtype=float)
    d2 = np.asarray(dir2, dtype=float)
    d1 = d1 / (np.linalg.norm(d1) + 1e-9) * size
    d2 = d2 / (np.linalg.norm(d2) + 1e-9) * size
    p1 = vertex + d1
    p2 = vertex + d1 + d2
    p3 = vertex + d2
    ax.plot([p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]],
            color=color, linewidth=lw, zorder=6)

def draw_dashed(ax, p1, p2, color='#9b59b6', lw=1.8, alpha=1.0):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]],
            color=color, linewidth=lw, linestyle='--', zorder=4, alpha=alpha)

def draw_solid(ax, p1, p2, color='black', lw=2.0, alpha=1.0):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]],
            color=color, linewidth=lw, zorder=4, alpha=alpha)


# ================================================================
# Model 1: 手拉手模型 (Hand-in-Hand Model)
# Two equilateral triangles sharing vertex A
# ================================================================
def draw_model1():
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_axis_off()

    A = np.array([0.0, 3.0])
    B = np.array([-2.5, 0.0])
    C = np.array([2.5, 0.0])
    # △ADE — another equilateral, rotated ~30° from △ABC
    D = np.array([-0.5, 0.8])
    # E = A rotated by 60° around A from D? Actually △ADE equilateral
    # AD rotated 60° CW → AE
    angle = np.radians(60)
    AD = D - A
    rot = np.array([[np.cos(angle), -np.sin(angle)],
                     [np.sin(angle),  np.cos(angle)]])
    AE = rot @ AD
    E = A + AE  # (1.5, 1.5) approx

    pts = [A, B, C, D, E]
    autoscale(ax, pts, margin=0.30)
    L = compute_visual_scale(ax)

    # Draw △ABC (equilateral) — black
    draw_solid(ax, A, B, color='#333333', lw=2.2)
    draw_solid(ax, B, C, color='#333333', lw=2.2)
    draw_solid(ax, C, A, color='#333333', lw=2.2)

    # Draw △ADE (equilateral) — blue
    draw_solid(ax, A, D, color='#2563eb', lw=2.2)
    draw_solid(ax, D, E, color='#2563eb', lw=2.2)
    draw_solid(ax, E, A, color='#2563eb', lw=2.2)

    # Draw the "handshake" segments — BD and CE (the pair proved equal)
    draw_solid(ax, B, D, color='#dc2626', lw=2.8)
    draw_solid(ax, C, E, color='#dc2626', lw=2.8)

    # Angle arc at A for 60°
    from matplotlib import patches
    arc_r = 0.08 * L
    for (p1, p2, color) in [(B, C, '#333333'), (D, E, '#2563eb')]:
        a1 = np.degrees(np.arctan2(p1[1]-A[1], p1[0]-A[0]))
        a2 = np.degrees(np.arctan2(p2[1]-A[1], p2[0]-A[0]))
        if a2 < a1:
            a1, a2 = a2, a1
        arc = patches.Arc(A, 2*arc_r, 2*arc_r, angle=0,
                          theta1=a1, theta2=a2, color=color, lw=2, zorder=3)
        ax.add_patch(arc)
        mid = np.radians((a1+a2)/2)
        lx = A[0] + (arc_r + 0.04*L)*np.cos(mid)
        ly = A[1] + (arc_r + 0.04*L)*np.sin(mid)
        # Don't label angles here — keep it clean

    # Labels
    label_point(ax, A, 'A', (0, 1), L)
    label_point(ax, B, 'B', (-1, -1), L)
    label_point(ax, C, 'C', (1, -1), L)
    label_point(ax, D, 'D', (-1.2, -0.3), L)
    label_point(ax, E, 'E', (1.2, -0.3), L)

    # △ABC label
    centroid_abc = (A + B + C) / 3
    ax.text(centroid_abc[0], centroid_abc[1]-0.4, '△ABC\n(等边)',
            ha='center', va='center', fontsize=10, color='#555555',
            bbox=_TEXT_BOX, zorder=12)
    centroid_ade = (A + D + E) / 3
    ax.text(centroid_ade[0]+0.6, centroid_ade[1]+0.2, '△ADE\n(等边)',
            ha='center', va='center', fontsize=10, color='#2563eb',
            bbox=_TEXT_BOX, zorder=12)

    # Title
    ax.set_title('模型1：手拉手模型\n△ABD ≌ △ACE (SAS)', fontsize=16,
                 fontweight='bold', color='#1e293b', pad=15)

    # Legend
    ax.text(0.02, 0.02, 'BD = CE（红色）\n∠BAC = ∠DAE = 60°',
            transform=ax.transAxes, fontsize=10, color='#dc2626',
            va='bottom', bbox=dict(facecolor='#fef2f2', alpha=0.9, pad=6))

    plt.savefig(os.path.join(OUT_DIR, 'model1_hand_in_hand.png'),
                dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Model 1 done ✓")


# ================================================================
# Model 2: 角平分线 + 垂线 → 对称全等
# ================================================================
def draw_model2():
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_axis_off()

    A = np.array([0.0, 2.5])
    B = np.array([-3.0, -0.5])
    C = np.array([3.0, -0.5])
    # Angle bisector AO — goes to middle
    O = np.array([0.0, -1.5])  # D in original problems
    # l ⟂ AO at H
    H = np.array([0.0, 1.0])
    # Line l direction: perpendicular to AO (vertical), horizontal
    # l intersects AB at N, AC at E, BC at M
    N = np.array([-1.2, 1.0])
    E = np.array([1.2, 1.0])
    M = np.array([0.0, -1.0])

    pts = [A, B, C, O, N, E, M, H]
    autoscale(ax, pts, margin=0.30)
    L = compute_visual_scale(ax)

    # Triangle ABC
    draw_solid(ax, A, B, lw=1.8, color='#333333')
    draw_solid(ax, B, C, lw=1.8, color='#333333')
    draw_solid(ax, C, A, lw=1.8, color='#333333')

    # AO bisector (dashed)
    draw_dashed(ax, A, O, color='#9b59b6', lw=1.6)

    # l (perpendicular to AO) — bold red
    draw_solid(ax, N, E, color='#dc2626', lw=2.5)

    # Right angle at H
    # AO direction: O - A
    draw_right_angle(ax, H, N-H, A-H, size=0.04*L, color='#dc2626', lw=2)

    # Angle marks at A (equal angles from bisector)
    from matplotlib import patches as mpatches
    arc_r = 0.09 * L
    AO_dir = O - A
    AB_dir = B - A
    AC_dir = C - A

    a_ao = np.degrees(np.arctan2(AO_dir[1], AO_dir[0]))
    a_ab = np.degrees(np.arctan2(AB_dir[1], AB_dir[0]))
    a_ac = np.degrees(np.arctan2(AC_dir[1], AC_dir[0]))

    arc1 = mpatches.Arc(A, 2*arc_r, 2*arc_r, angle=0,
                        theta1=min(a_ab, a_ao), theta2=max(a_ab, a_ao),
                        color='#9b59b6', lw=1.5, zorder=3)
    ax.add_patch(arc1)
    arc_r2 = 0.12 * L
    arc2 = mpatches.Arc(A, 2*arc_r2, 2*arc_r2, angle=0,
                        theta1=min(a_ao, a_ac), theta2=max(a_ao, a_ac),
                        color='#9b59b6', lw=1.5, zorder=3)
    ax.add_patch(arc2)

    # Equal tick marks on AB and AC angles
    mid_ab = np.radians((a_ab + a_ao)/2)
    mid_ac = np.radians((a_ao + a_ac)/2)
    ax.text(A[0]+(arc_r+0.02*L)*np.cos(mid_ab), A[1]+(arc_r+0.02*L)*np.sin(mid_ab),
            '=', fontsize=9, color='#9b59b6', ha='center', va='center')

    # Labels
    label_point(ax, A, 'A', (0, 1), L)
    label_point(ax, B, 'B', (-1, -0.5), L)
    label_point(ax, C, 'C', (1, -0.5), L)
    label_point(ax, O, 'D', (1, -1), L)
    label_point(ax, N, 'N', (-1, 0.6), L)
    label_point(ax, E, 'E', (1, 0.6), L)
    label_point(ax, H, 'H', (-0.8, 0.3), L)
    label_point(ax, M, 'M', (0.8, -1), L)

    # AO label
    ax.text(-0.3, -0.1, 'AO (角平分线)', fontsize=9, color='#9b59b6',
            bbox=_TEXT_BOX, zorder=12)
    ax.text(1.8, 1.3, 'l (垂直 AO)', fontsize=10, color='#dc2626',
            fontweight='bold', bbox=_TEXT_BOX, zorder=12)

    ax.set_title('模型2：角平分线 + 垂线 → 对称全等\n△AHN ≌ △AHE (ASA) → AN = AE',
                 fontsize=16, fontweight='bold', color='#1e293b', pad=15)

    plt.savefig(os.path.join(OUT_DIR, 'model2_symmetry.png'),
                dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Model 2 done ✓")


# ================================================================
# Model 3: 截长补短 (∠C = 2∠B + angle bisector)
# ================================================================
def draw_model3():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    for ax in [ax1, ax2]:
        ax.set_axis_off()

    # Triangle with ∠C=2∠B, AD bisects ∠A
    # Let ∠B = 30°, ∠C = 60°, ∠A = 90° (simple example)
    A = np.array([0.0, 3.0])
    B = np.array([-2.0, 0.0])
    C = np.array([4.0, 0.0])
    # AD: angle bisector of A, intersects BC at D
    D = np.array([0.8, 0.0])

    pts = [A, B, C, D]
    autoscale(ax1, pts, margin=0.35)
    L1 = compute_visual_scale(ax1)
    autoscale(ax2, pts + [np.array([2.0, 0.0])], margin=0.35)
    L2 = compute_visual_scale(ax2)

    # ---- Left panel: BEFORE (original triangle) ----
    draw_solid(ax1, A, B, color='#333333', lw=2)
    draw_solid(ax1, B, C, color='#333333', lw=2)
    draw_solid(ax1, C, A, color='#333333', lw=2)
    draw_dashed(ax1, A, D, color='#9b59b6', lw=1.8)

    # Angle marks
    # ∠B (30°) and ∠C (60°) annotation
    ax1.text(B[0]+0.1, B[1]+0.2, '∠B=β', fontsize=10, color='#2563eb',
             bbox=_TEXT_BOX)
    ax1.text(C[0]-0.2, C[1]+0.2, '∠C=2β', fontsize=10, color='#dc2626',
             bbox=_TEXT_BOX)

    label_point(ax1, A, 'A', (0, 1), L1)
    label_point(ax1, B, 'B', (-1, -0.5), L1)
    label_point(ax1, C, 'C', (1, -0.5), L1)
    label_point(ax1, D, 'D', (0.6, -1), L1)

    # AD label
    ax1.text(-0.3, 1.2, 'AD 平分∠A', fontsize=10, color='#9b59b6',
             fontweight='bold', bbox=_TEXT_BOX)
    ax1.set_title('已知：∠C=2∠B，AD平分∠A', fontsize=13,
                  fontweight='bold', color='#1e293b')

    # ---- Right panel: AFTER (截长补短) ----
    # Draw same base
    draw_solid(ax2, A, B, color='#333333', lw=2)
    draw_solid(ax2, B, C, color='#333333', lw=2)
    draw_solid(ax2, C, A, color='#333333', lw=2)
    draw_dashed(ax2, A, D, color='#9b59b6', lw=1.8)

    # Cut: AF = AC on AB
    # AB direction: B-A = (-2, -3), length sqrt(13) ≈ 3.6
    # AC length = 5, so F is beyond B? Actually let's adjust angles
    # Better: use a triangle where AC < AB so F is on AB
    # My current triangle: AB=sqrt(13)≈3.6, AC=5. AC > AB so cut doesn't work.
    # Let me re-coordinate: swap to make AC < AB
    # Actually, let me just draw the concept clearly — set F at a reasonable position
    # For demo purposes, put F at ~midpoint of AB
    F = np.array([-0.9, 1.65])
    # F should be on AB. AB: from (-2,0) to (0,3). param t: F = B + t*(A-B) = (-2+2t, 0+3t)
    # For F=(-0.9, 1.65): 2t=1.1→t=0.55, 3t=1.65→t=0.55. OK, F is on AB.

    # Draw DF (connection after cut)
    draw_solid(ax2, D, F, color='#16a34a', lw=2.5)

    # Highlight AF and AC as equal (the "cut")
    draw_solid(ax2, A, F, color='#2563eb', lw=2.8, alpha=0.6)
    draw_solid(ax2, A, C, color='#2563eb', lw=2.8, alpha=0.6)

    # Equal ticks on AF and AC
    mid_AF = (A+F)/2
    mid_AC = (A+C)/2
    tick = 0.05 * L2
    for mid, seg in [(mid_AF, F-A), (mid_AC, C-A)]:
        perp = np.array([-seg[1], seg[0]]) / (np.linalg.norm(seg)+1e-9) * tick
        ax2.plot([mid[0]-perp[0], mid[0]+perp[0]],
                 [mid[1]-perp[1], mid[1]+perp[1]],
                 color='#2563eb', lw=2.5)

    # Equal ticks on DF and DC
    mid_DF = (D+F)/2
    perp_DF = np.array([-(F[1]-D[1]), F[0]-D[0]]) / (np.linalg.norm(F-D)+1e-9) * tick
    ax2.plot([mid_DF[0]-perp_DF[0], mid_DF[0]+perp_DF[0]],
             [mid_DF[1]-perp_DF[1], mid_DF[1]+perp_DF[1]],
             color='#16a34a', lw=2.5)

    # Highlight BF as the key (BF = CD = AB-AC)
    draw_solid(ax2, B, F, color='#dc2626', lw=2.8)

    label_point(ax2, A, 'A', (0, 1), L2)
    label_point(ax2, B, 'B', (-1, -0.5), L2)
    label_point(ax2, C, 'C', (1, -0.5), L2)
    label_point(ax2, D, 'D', (0.6, -1), L2)
    label_point(ax2, F, 'F', (-1, 0.8), L2)

    # Annotation boxes
    ax2.annotate('AF = AC\n(截长)', xy=F, xytext=(-3.0, 2.5),
                fontsize=10, color='#2563eb', fontweight='bold',
                bbox=dict(facecolor='#eff6ff', alpha=0.9, pad=6),
                arrowprops=dict(arrowstyle='->', color='#2563eb', lw=1.5))

    ax2.annotate('BF = DF = CD\n(等腰推导)', xy=(B+F)/2, xytext=(-0.5, 3.2),
                fontsize=10, color='#dc2626', fontweight='bold',
                bbox=dict(facecolor='#fef2f2', alpha=0.9, pad=6),
                arrowprops=dict(arrowstyle='->', color='#dc2626', lw=1.5))

    ax2.annotate('DF = DC\n(全等△AFD≌△ACD)', xy=(D+F)/2, xytext=(2.5, 1.8),
                fontsize=10, color='#16a34a', fontweight='bold',
                bbox=dict(facecolor='#f0fdf4', alpha=0.9, pad=6),
                arrowprops=dict(arrowstyle='->', color='#16a34a', lw=1.5))

    ax2.set_title('方法：截长补短 → CD = AB - AC', fontsize=13,
                  fontweight='bold', color='#1e293b')

    fig.suptitle('模型3：截长补短\n∠C=2∠B + AD平分∠A', fontsize=16,
                 fontweight='bold', color='#1e293b', y=1.02)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'model3_cut_and_fill.png'),
                dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Model 3 done ✓")


# ================================================================
# Model 4: 构造等边三角形 → 连锁全等 (Problem 004 style)
# ================================================================
def draw_model4():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    for ax in [ax1, ax2]:
        ax.set_axis_off()

    # Triangle with ∠A=44°, ∠C=44°, so ∠B=92°
    # A at top-left, B at bottom, C at bottom-right
    A = np.array([-1.0, 3.2])
    B = np.array([-2.5, 0.0])
    C = np.array([2.0, 0.0])
    # M: interior point with ∠MCA=30°, ∠MAC=16°
    M = np.array([-0.6, 1.5])

    # Equilateral triangle ACE on AC
    AC_vec = C - A
    angle60 = np.radians(-60)  # rotate AC by -60° to get AE
    rot = np.array([[np.cos(angle60), -np.sin(angle60)],
                     [np.sin(angle60),  np.cos(angle60)]])
    AE = rot @ AC_vec
    E = A + AE  # E is the third vertex of equilateral △ACE

    pts = [A, B, C, M, E]
    for ax_i in [ax1, ax2]:
        autoscale(ax_i, pts, margin=0.35)

    L_refs = [compute_visual_scale(ax1), compute_visual_scale(ax2)]

    # ---- Left panel: BEFORE construction ----
    draw_solid(ax1, A, B, color='#333333', lw=2)
    draw_solid(ax1, B, C, color='#333333', lw=2)
    draw_solid(ax1, C, A, color='#333333', lw=2)

    # M connections
    draw_solid(ax1, M, A, color='#9b59b6', lw=1.5)
    draw_solid(ax1, M, C, color='#9b59b6', lw=1.5)
    draw_solid(ax1, M, B, color='#999999', lw=1.2, alpha=0.5)

    L1 = L_refs[0]
    label_point(ax1, A, 'A', (-1, 1), L1)
    label_point(ax1, B, 'B', (-1, -1), L1)
    label_point(ax1, C, 'C', (1, -1), L1)
    label_point(ax1, M, 'M', (-1.2, -0.2), L1, color='#9b59b6')

    # Angle annotations
    ax1.text(A[0]-0.7, A[1]-0.5, '44°', fontsize=10, color='#333333', bbox=_TEXT_BOX)
    ax1.text(C[0]+0.2, C[1]-0.5, '44°', fontsize=10, color='#333333', bbox=_TEXT_BOX)
    ax1.text(M[0]+0.5, M[1]+0.1, '16°', fontsize=10, color='#9b59b6', bbox=_TEXT_BOX)
    ax1.text(M[0]+0.5, M[1]-0.4, '30°', fontsize=10, color='#9b59b6', bbox=_TEXT_BOX)

    ax1.set_title('已知：∠A = ∠C = 44°\n∠MAC = 16°, ∠MCA = 30°',
                  fontsize=12, fontweight='bold', color='#1e293b')

    # ---- Right panel: AFTER construction ----
    # Draw base triangle
    draw_solid(ax2, A, B, color='#999999', lw=1.5, alpha=0.4)
    draw_solid(ax2, B, C, color='#999999', lw=1.5, alpha=0.4)
    draw_solid(ax2, C, A, color='#999999', lw=1.5, alpha=0.4)

    # Equilateral triangle ACE — bold cyan
    draw_solid(ax2, A, C, color='#0891b2', lw=2.5)
    draw_solid(ax2, C, E, color='#0891b2', lw=2.5)
    draw_solid(ax2, E, A, color='#0891b2', lw=2.5)

    # Connections for proof
    draw_solid(ax2, B, E, color='#dc2626', lw=2.5)  # Key connection
    draw_solid(ax2, M, A, color='#9b59b6', lw=1.5)
    draw_solid(ax2, M, C, color='#9b59b6', lw=1.5)

    # Congruence highlight: ABE ≌ CBE
    L2 = L_refs[1]
    # Equal ticks on AB and CB
    mid_AB = (A+B)/2
    mid_CB = (C+B)/2
    tick = 0.04 * L2
    for mid, seg in [(mid_AB, B-A), (mid_CB, B-C)]:
        perp = np.array([-seg[1], seg[0]]) / (np.linalg.norm(seg)+1e-9) * tick
        ax2.plot([mid[0]-perp[0], mid[0]+perp[0]],
                 [mid[1]-perp[1], mid[1]+perp[1]],
                 color='#333333', lw=2)

    # Equal ticks on AE and CE
    mid_AE = (A+E)/2
    mid_CE = (C+E)/2
    for mid, seg in [(mid_AE, E-A), (mid_CE, E-C)]:
        perp = np.array([-seg[1], seg[0]]) / (np.linalg.norm(seg)+1e-9) * tick
        ax2.plot([mid[0]-perp[0], mid[0]+perp[0]],
                 [mid[1]-perp[1], mid[1]+perp[1]],
                 color='#0891b2', lw=2)

    label_point(ax2, A, 'A', (-1, 1), L2)
    label_point(ax2, B, 'B', (-1, -1), L2)
    label_point(ax2, C, 'C', (1, -1), L2)
    label_point(ax2, M, 'M', (-1.2, -0.2), L2, color='#9b59b6')
    label_point(ax2, E, 'E', (-0.5, 4.2), L2, color='#0891b2')

    # Key angle: ∠EAB = 16° = ∠MAC
    ax2.annotate('60°-44°=16°\n=∠MAC !',
                xy=A, xytext=(-3.5, 4.0),
                fontsize=11, color='#dc2626', fontweight='bold',
                bbox=dict(facecolor='#fef2f2', alpha=0.95, pad=6, edgecolor='#dc2626'),
                arrowprops=dict(arrowstyle='->', color='#dc2626', lw=2))

    ax2.annotate('△ACE\n等边',
                xy=(A+C)/2, xytext=(3.0, 2.5),
                fontsize=10, color='#0891b2', fontweight='bold',
                bbox=dict(facecolor='#ecfeff', alpha=0.95, pad=6),
                arrowprops=dict(arrowstyle='->', color='#0891b2', lw=1.5))

    ax2.set_title('构造：以AC为边作等边△ACE\n△ABE≌△CBE(SSS)→∠AEB=30°',
                  fontsize=12, fontweight='bold', color='#1e293b')

    fig.suptitle('模型4：特殊角 → 构造等边三角形 → 连锁全等',
                 fontsize=16, fontweight='bold', color='#1e293b', y=1.02)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'model4_equilateral_construction.png'),
                dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Model 4 done ✓")


# ================================================================
# Model 5: 分类讨论 — 等腰三角形分割
# ================================================================
def draw_model5():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    for ax in [ax1, ax2]:
        ax.set_axis_off()

    # Isosceles △ABC with AB=AC, ∠A unknown
    A = np.array([0.0, 3.0])
    B = np.array([-2.5, 0.0])
    C = np.array([2.5, 0.0])

    L1 = 6.0  # approximate visual scale
    L2 = 6.0

    # ---- Left: Case 1 (x = 180°/7 ≈ 25.7°) ----
    # AD=DC in △ACD, BD=BC in △BCD
    # D on AB such that these hold
    # For case 1: ∠A=x, ∠DCA=x, ∠ADC=180-2x, ∠BDC=∠BCD=2x
    # Let's compute D position
    # AB: from (-2.5,0) to (0,3). D splits AB. AD=DC means...
    # Actually let's just place D at a position that visually shows the concept
    D1 = np.array([-0.6, 2.1])  # roughly on AB, 1/3 from A

    for ax_i, D, title, case in [(ax1, D1, '情况一：AD = DC，BD = BC\n∠A = 180°/7 ≈ 25.7°', 'case1'),
                                 (ax2, np.array([-0.8, 1.8]), '情况二：AD = DC，DC = CB\n∠A = 36°', 'case2')]:
        autoscale(ax_i, [A, B, C, D], margin=0.35)
        L = compute_visual_scale(ax_i)

        # △ABC
        draw_solid(ax_i, A, B, color='#333333', lw=1.8)
        draw_solid(ax_i, B, C, color='#333333', lw=1.8)
        draw_solid(ax_i, C, A, color='#333333', lw=1.8)

        # Equal ticks on AB and AC (isosceles)
        mid_AB = (A+B)/2
        mid_AC = (A+C)/2
        tick = 0.04 * L
        for mid, seg in [(mid_AB, B-A), (mid_AC, C-A)]:
            perp = np.array([-seg[1], seg[0]]) / (np.linalg.norm(seg)+1e-9) * tick
            ax_i.plot([mid[0]-perp[0], mid[0]+perp[0]],
                     [mid[1]-perp[1], mid[1]+perp[1]],
                     color='#333333', lw=2)

        # Line CD (the split)
        draw_solid(ax_i, C, D, color='#dc2626', lw=2.5)

        # Highlight equal segments in split triangles
        if case == 'case1':
            # AD=DC: tick both
            mid_AD = (A+D)/2
            perp_AD = np.array([-(D[1]-A[1]), D[0]-A[0]]) / (np.linalg.norm(D-A)+1e-9) * tick
            ax_i.plot([mid_AD[0]-perp_AD[0], mid_AD[0]+perp_AD[0]],
                     [mid_AD[1]-perp_AD[1], mid_AD[1]+perp_AD[1]],
                     color='#2563eb', lw=2.5)
            mid_CD = (C+D)/2
            perp_CD = np.array([-(D[1]-C[1]), D[0]-C[0]]) / (np.linalg.norm(D-C)+1e-9) * tick
            ax_i.plot([mid_CD[0]-perp_CD[0], mid_CD[0]+perp_CD[0]],
                     [mid_CD[1]-perp_CD[1], mid_CD[1]+perp_CD[1]],
                     color='#2563eb', lw=2.5)
            # BD=BC: tick both
            mid_BD = (B+D)/2
            perp_BD = np.array([-(D[1]-B[1]), D[0]-B[0]]) / (np.linalg.norm(D-B)+1e-9) * tick
            ax_i.plot([mid_BD[0]-perp_BD[0], mid_BD[0]+perp_BD[0]],
                     [mid_BD[1]-perp_BD[1], mid_BD[1]+perp_BD[1]],
                     color='#16a34a', lw=2.5)
            mid_BC = (B+C)/2
            perp_BC = np.array([0, 1]) * tick
            ax_i.plot([mid_BC[0]-perp_BC[0], mid_BC[0]+perp_BC[0]],
                     [mid_BC[1]-perp_BC[1], mid_BC[1]+perp_BC[1]],
                     color='#16a34a', lw=2.5)
        else:
            # AD=DC: tick both
            mid_AD = (A+D)/2
            perp_AD = np.array([-(D[1]-A[1]), D[0]-A[0]]) / (np.linalg.norm(D-A)+1e-9) * tick
            ax_i.plot([mid_AD[0]-perp_AD[0], mid_AD[0]+perp_AD[0]],
                     [mid_AD[1]-perp_AD[1], mid_AD[1]+perp_AD[1]],
                     color='#2563eb', lw=2.5)
            mid_CD = (C+D)/2
            perp_CD = np.array([-(D[1]-C[1]), D[0]-C[0]]) / (np.linalg.norm(D-C)+1e-9) * tick
            ax_i.plot([mid_CD[0]-perp_CD[0], mid_CD[0]+perp_CD[0]],
                     [mid_CD[1]-perp_CD[1], mid_CD[1]+perp_CD[1]],
                     color='#2563eb', lw=2.5)
            # DC=CB: tick both
            mid_CB = (C+B)/2
            perp_CB = np.array([0, 1]) * tick
            ax_i.plot([mid_CB[0]-perp_CB[0], mid_CB[0]+perp_CB[0]],
                     [mid_CB[1]-perp_CB[1], mid_CB[1]+perp_CB[1]],
                     color='#16a34a', lw=2.5)

        label_point(ax_i, A, 'A', (0, 1), L)
        label_point(ax_i, B, 'B', (-1, -1), L)
        label_point(ax_i, C, 'C', (1, -1), L)
        label_point(ax_i, D, 'D', (-1, 0.8), L, color='#dc2626')

        ax_i.set_title(title, fontsize=12, fontweight='bold', color='#1e293b')

    # Legend for tick colors
    ax1.text(0.02, 0.02, '蓝色 = AD=DC\n绿色 = BD=BC',
             transform=ax1.transAxes, fontsize=9,
             va='bottom', bbox=dict(facecolor='white', alpha=0.9, pad=4))
    ax2.text(0.02, 0.02, '蓝色 = AD=DC\n绿色 = DC=CB',
             transform=ax2.transAxes, fontsize=9,
             va='bottom', bbox=dict(facecolor='white', alpha=0.9, pad=4))

    fig.suptitle('模型5：分类讨论——等腰三角形被分成两个等腰三角形\n过C作直线交AB于D',
                 fontsize=16, fontweight='bold', color='#1e293b', y=1.02)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'model5_classification.png'),
                dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Model 5 done ✓")


# ================================================================
# Bonus: 辅助线决策流程图
# ================================================================
def draw_decision_tree():
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_axis_off()
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)

    # Title
    ax.text(6, 7.6, '几何辅助线决策流程图', fontsize=18, fontweight='bold',
            ha='center', va='center', color='#1e293b')

    # Root node
    boxes = []

    def draw_box(x, y, w, h, text, color='#dbeafe', edge='#2563eb', fontsize=10):
        from matplotlib.patches import FancyBboxPatch
        box = FancyBboxPatch((x-w/2, y-h/2), w, h,
                             boxstyle="round,pad=0.1",
                             facecolor=color, edgecolor=edge, linewidth=2, zorder=5)
        ax.add_patch(box)
        ax.text(x, y, text, ha='center', va='center', fontsize=fontsize,
                fontweight='bold', color='#1e293b', zorder=6)
        return (x, y)

    def draw_arrow(x1, y1, x2, y2, label='', color='#64748b'):
        ax.annotate('', xy=(x2, y2-0.3), xytext=(x1, y1+0.3),
                   arrowprops=dict(arrowstyle='->', color=color, lw=1.8))
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx+0.2, my, label, fontsize=8, color=color, fontweight='bold',
                    bbox=dict(facecolor='white', alpha=0.8, pad=1))

    # Row 1: Root
    draw_box(6, 7.0, 7, 0.6, '看到什么信号？', '#fef3c7', '#d97706', 12)

    # Row 2: Signal branches
    y2 = 5.5
    signals = [
        (1.2, '角平分线\n+ 垂线', '#dbeafe'),
        (3.6, '∠C = 2∠B\n+ 角平分线', '#d1fae5'),
        (6.0, '非标准\n特殊角', '#fce7f3'),
        (8.4, '中点\n+ 孤立线段', '#e0e7ff'),
        (10.8, '两个等边△\n共顶点', '#fef3c7'),
    ]
    for x, text, color in signals:
        draw_box(x, y2, 2.0, 1.0, text, color, '#475569', 9)
        draw_arrow(6, 6.7, x, 6.0)

    # Row 3: Methods
    y3 = 3.8
    methods = [
        (1.2, '延长垂线\n→ 对称全等\n→ 中点/等腰', '#bfdbfe'),
        (3.6, '截长补短\nAF=AC\n→ CD=AB-AC', '#a7f3d0'),
        (6.0, '构造等边△\n造60°角\n差得关键角', '#fbcfe8'),
        (8.4, '倍长中线\n→ SAS全等\n→ 平行/等量', '#c7d2fe'),
        (10.8, '手拉手模型\nSAS全等\n→ 平行/共线', '#fde68a'),
    ]
    for x, text, color in methods:
        draw_box(x, y3, 2.2, 1.2, text, color, '#475569', 9)
        draw_arrow(x, 5.0, x, 4.4)

    # Row 4: Goal
    y4 = 2.4
    draw_box(6, y4, 10, 0.7,
             '目标：找到全等三角形 → 搬运等边/等角 → 得出结论',
             '#fee2e2', '#dc2626', 11)
    for x, _, _ in methods:
        draw_arrow(x, 3.2, 6, 2.75)

    # Bottom tip
    ax.text(6, 1.0, '核心原则：缺什么条件 → 就构造什么辅助线 → 补全条件 → 证明全等',
            fontsize=11, ha='center', va='center', color='#64748b',
            fontstyle='italic',
            bbox=dict(facecolor='#f8fafc', alpha=0.9, pad=8))

    plt.savefig(os.path.join(OUT_DIR, 'decision_tree.png'),
                dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Decision tree done ✓")


# ================================================================
if __name__ == '__main__':
    draw_model1()
    draw_model2()
    draw_model3()
    draw_model4()
    draw_model5()
    draw_decision_tree()
    print(f"\nAll figures saved to: {OUT_DIR}")
