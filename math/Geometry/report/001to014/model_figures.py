"""
Generate illustrative figures for the 5 core geometry models
described in geometry_mastery_report.md.

Output: model_assets/model{1-5}_*.png, decision_tree.png
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager, patches as mpatches
from matplotlib.patches import FancyBboxPatch

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

_TEXT_BOX = dict(facecolor='white', edgecolor='none', alpha=0.85, pad=0.15)
OUT_DIR = os.path.join(_BASE_DIR, 'model_assets')
os.makedirs(OUT_DIR, exist_ok=True)


def compute_visual_scale(ax):
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    return min(abs(x1 - x0), abs(y1 - y0))


def autoscale(ax, key_points, margin=0.28):
    pts = np.array(key_points)
    xmin, ymin = pts.min(axis=0)
    xmax, ymax = pts.max(axis=0)
    dx = xmax - xmin
    dy = ymax - ymin
    ax.set_xlim(xmin - margin * max(dx, dy), xmax + margin * max(dx, dy))
    ax.set_ylim(ymin - margin * max(dx, dy), ymax + margin * max(dx, dy))
    ax.set_aspect('equal')


def label_point(ax, P, name, direction, scale, offset_ratio=0.065,
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


def draw_equal_tick(ax, mid, seg_dir, tick_len, color='black', lw=2.0):
    perp = np.array([-seg_dir[1], seg_dir[0]]) / (np.linalg.norm(seg_dir) + 1e-9) * tick_len
    ax.plot([mid[0] - perp[0], mid[0] + perp[0]],
            [mid[1] - perp[1], mid[1] + perp[1]],
            color=color, linewidth=lw, zorder=7)


def rotate_vec(v, angle_deg):
    """Rotate vector v by angle_deg degrees (CCW positive)."""
    ang = np.radians(angle_deg)
    c, s = np.cos(ang), np.sin(ang)
    rot = np.array([[c, -s], [s, c]])
    return rot @ np.asarray(v, dtype=float)


# ================================================================
# Model 1: 手拉手模型 (Hand-in-Hand Model)
# Two equilateral triangles sharing vertex A
# ================================================================
def draw_model1():
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_axis_off()

    # △ABC equilateral, A at top
    A = np.array([0.0, 3.0])
    side = 2 * np.sqrt(3)  # ~3.464
    B = np.array([-side / 2, 0.0])   # (-1.732, 0)
    C = np.array([side / 2, 0.0])    # (1.732, 0)

    # △ADE equilateral, sharing A, rotated so D is left-down, E is right-down
    # D-A direction: 240° (60° left of straight down)
    ad_len = 1.7
    D = A + ad_len * np.array([np.cos(np.radians(240)), np.sin(np.radians(240))])
    # E = A + rotate(D-A, 60° CCW)
    E = A + rotate_vec(D - A, 60)

    pts = [A, B, C, D, E]
    autoscale(ax, pts, margin=0.32)
    L = compute_visual_scale(ax)

    # Draw △ABC — black solid
    draw_solid(ax, A, B, color='#1e293b', lw=2.4)
    draw_solid(ax, B, C, color='#1e293b', lw=2.4)
    draw_solid(ax, C, A, color='#1e293b', lw=2.4)

    # Draw △ADE — blue solid
    draw_solid(ax, A, D, color='#2563eb', lw=2.4)
    draw_solid(ax, D, E, color='#2563eb', lw=2.4)
    draw_solid(ax, E, A, color='#2563eb', lw=2.4)

    # Handshake segments BD and CE — red bold
    draw_solid(ax, B, D, color='#dc2626', lw=3.0)
    draw_solid(ax, C, E, color='#dc2626', lw=3.0)

    # Equal tick marks on AB=AC, AD=AE
    tick = 0.035 * L
    draw_equal_tick(ax, (A + B) / 2, B - A, tick, color='#1e293b')
    draw_equal_tick(ax, (A + C) / 2, C - A, tick, color='#1e293b')
    draw_equal_tick(ax, (A + D) / 2, D - A, tick, color='#2563eb')
    draw_equal_tick(ax, (A + E) / 2, E - A, tick, color='#2563eb')

    # Arc marks for 60° at A
    arc_r = 0.09 * L
    for p1, p2, color in [(B, C, '#1e293b'), (D, E, '#2563eb')]:
        a1 = np.degrees(np.arctan2(p1[1] - A[1], p1[0] - A[0]))
        a2 = np.degrees(np.arctan2(p2[1] - A[1], p2[0] - A[0]))
        if a2 < a1:
            a1, a2 = a2, a1
        arc = mpatches.Arc(A, 2 * arc_r, 2 * arc_r, angle=0,
                           theta1=a1, theta2=a2, color=color, lw=2, zorder=3)
        ax.add_patch(arc)

    # Labels
    label_point(ax, A, 'A', (0, 1.1), L)
    label_point(ax, B, 'B', (-1, -0.9), L)
    label_point(ax, C, 'C', (1, -0.9), L)
    label_point(ax, D, 'D', (-1.2, -0.2), L)
    label_point(ax, E, 'E', (1.2, -0.2), L)

    # Triangle labels
    ax.text(-0.6, 1.0, '△ABC\n(等边)', ha='center', va='center',
            fontsize=10, color='#334155', fontweight='bold',
            bbox=dict(facecolor='white', alpha=0.9, pad=5))
    ax.text(1.3, 1.5, '△ADE\n(等边)', ha='center', va='center',
            fontsize=10, color='#2563eb', fontweight='bold',
            bbox=dict(facecolor='#eff6ff', alpha=0.9, pad=5))

    ax.set_title('模型1：手拉手模型 — 共顶点等边三角形的 SAS 全等',
                 fontsize=16, fontweight='bold', color='#1e293b', pad=15)

    ax.text(0.02, 0.02, '结论：△ABD ≌ △ACE (SAS)\n→ BD = CE  且  ∠ABD = ∠ACE',
            transform=ax.transAxes, fontsize=11, color='#dc2626',
            va='bottom', fontweight='bold',
            bbox=dict(facecolor='#fef2f2', alpha=0.95, pad=8, edgecolor='#dc2626', linewidth=1.5))

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

    A = np.array([0.0, 3.0])
    B = np.array([-3.0, 0.0])
    C = np.array([3.0, 0.0])
    # AO bisector (vertical downward)
    O = np.array([0.0, -1.0])
    # H on AO, l perpendicular to AO at H (horizontal line)
    H = np.array([0.0, 1.5])
    N = np.array([-1.5, 1.5])   # on AB
    E = np.array([1.5, 1.5])    # on AC

    pts = [A, B, C, O, N, E, H]
    autoscale(ax, pts, margin=0.30)
    L = compute_visual_scale(ax)

    # Triangle ABC
    draw_solid(ax, A, B, lw=2.0, color='#1e293b')
    draw_solid(ax, B, C, lw=2.0, color='#1e293b')
    draw_solid(ax, C, A, lw=2.0, color='#1e293b')

    # AO bisector (dashed purple)
    draw_dashed(ax, A, O, color='#9333ea', lw=1.8)

    # l (perpendicular to AO) — bold red
    draw_solid(ax, N, E, color='#dc2626', lw=2.8)

    # Right angle at H
    draw_right_angle(ax, H, N - H, A - H, size=0.04 * L, color='#dc2626', lw=2)

    # Angle marks at A (equal angles from bisector)
    arc_r = 0.10 * L
    AO_dir = O - A
    AB_dir = B - A
    AC_dir = C - A

    a_ao = np.degrees(np.arctan2(AO_dir[1], AO_dir[0]))
    a_ab = np.degrees(np.arctan2(AB_dir[1], AB_dir[0]))
    a_ac = np.degrees(np.arctan2(AC_dir[1], AC_dir[0]))

    arc1 = mpatches.Arc(A, 2 * arc_r, 2 * arc_r, angle=0,
                        theta1=min(a_ab, a_ao), theta2=max(a_ab, a_ao),
                        color='#9333ea', lw=2, zorder=3)
    ax.add_patch(arc1)
    arc_r2 = 0.14 * L
    arc2 = mpatches.Arc(A, 2 * arc_r2, 2 * arc_r2, angle=0,
                        theta1=min(a_ao, a_ac), theta2=max(a_ao, a_ac),
                        color='#9333ea', lw=2, zorder=3)
    ax.add_patch(arc2)

    # Equal tick inside angle arcs
    mid_ab = np.radians((a_ab + a_ao) / 2)
    ax.text(A[0] + (arc_r + 0.03 * L) * np.cos(mid_ab),
            A[1] + (arc_r + 0.03 * L) * np.sin(mid_ab),
            '1', fontsize=8, color='#9333ea', ha='center', va='center', fontweight='bold')
    mid_ac = np.radians((a_ao + a_ac) / 2)
    ax.text(A[0] + (arc_r2 + 0.03 * L) * np.cos(mid_ac),
            A[1] + (arc_r2 + 0.03 * L) * np.sin(mid_ac),
            '1', fontsize=8, color='#9333ea', ha='center', va='center', fontweight='bold')

    # Labels
    label_point(ax, A, 'A', (0, 1.1), L)
    label_point(ax, B, 'B', (-1, -0.8), L)
    label_point(ax, C, 'C', (1, -0.8), L)
    label_point(ax, O, 'O', (0.9, -0.8), L)
    label_point(ax, N, 'N', (-1.2, 0.5), L)
    label_point(ax, E, 'E', (1.2, 0.5), L)
    label_point(ax, H, 'H', (-0.9, 0.3), L)

    # Annotations
    ax.text(0.5, -0.5, 'AO\n(角平分线)', fontsize=10, color='#9333ea',
            fontweight='bold', bbox=dict(facecolor='#faf5ff', alpha=0.95, pad=5))
    ax.text(2.2, 1.8, 'l ⊥ AO', fontsize=11, color='#dc2626',
            fontweight='bold', bbox=dict(facecolor='#fef2f2', alpha=0.95, pad=5))
    ax.text(-2.8, 2.0, 'AN = AE\n(ASA 全等)', fontsize=10, color='#dc2626',
            fontweight='bold', bbox=dict(facecolor='#fef2f2', alpha=0.95, pad=5))

    ax.set_title('模型2：角平分线 + 垂线 → 对称全等 (AN = AE)',
                 fontsize=16, fontweight='bold', color='#1e293b', pad=15)

    ax.text(0.5, 0.02, '结论：△AHN ≌ △AHE (ASA) → AN = AE  且  HN = HE',
            transform=ax.transAxes, fontsize=11, color='#1e293b',
            ha='center', va='bottom', fontweight='bold',
            bbox=dict(facecolor='#fef9c3', alpha=0.95, pad=8, edgecolor='#eab308', linewidth=1.5))

    plt.savefig(os.path.join(OUT_DIR, 'model2_symmetry.png'),
                dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Model 2 done ✓")


# ================================================================
# Model 3: 截长补短 (∠C = 2∠B + angle bisector)
# ================================================================
def draw_model3():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.5))
    for ax in [ax1, ax2]:
        ax.set_axis_off()

    # Accurate triangle: ∠B=35°, ∠C=70°, ∠A=75°
    B = np.array([0.0, 0.0])
    C = np.array([4.0, 0.0])
    AB_len = 4.0 * np.sin(np.radians(70)) / np.sin(np.radians(75))
    A = np.array([AB_len * np.cos(np.radians(35)), AB_len * np.sin(np.radians(35))])
    # D on BC by angle-bisector theorem: BD / DC = AB / AC
    AC_len = 4.0 * np.sin(np.radians(35)) / np.sin(np.radians(75))
    BD_len = 4.0 * AB_len / (AB_len + AC_len)
    D = np.array([BD_len, 0.0])
    # F on AB with AF = AC
    AF_len = AC_len
    F = A + (AF_len / AB_len) * (B - A)

    pts = [A, B, C, D, F]
    autoscale(ax1, pts, margin=0.35)
    L1 = compute_visual_scale(ax1)
    autoscale(ax2, pts, margin=0.35)
    L2 = compute_visual_scale(ax2)

    # ---- Left panel: BEFORE ----
    draw_solid(ax1, A, B, color='#1e293b', lw=2.2)
    draw_solid(ax1, B, C, color='#1e293b', lw=2.2)
    draw_solid(ax1, C, A, color='#1e293b', lw=2.2)
    draw_dashed(ax1, A, D, color='#9333ea', lw=2.0)

    # Angle annotations
    ax1.annotate('∠B = β', xy=B, xytext=(-1.0, 0.6),
                fontsize=11, color='#2563eb', fontweight='bold',
                bbox=dict(facecolor='#eff6ff', alpha=0.95, pad=5),
                arrowprops=dict(arrowstyle='->', color='#2563eb', lw=1.5))
    ax1.annotate('∠C = 2β', xy=C, xytext=(3.0, 0.6),
                fontsize=11, color='#dc2626', fontweight='bold',
                bbox=dict(facecolor='#fef2f2', alpha=0.95, pad=5),
                arrowprops=dict(arrowstyle='->', color='#dc2626', lw=1.5))
    ax1.annotate('AD 平分∠A', xy=(A + D) / 2, xytext=(0.3, 2.5),
                fontsize=10, color='#9333ea', fontweight='bold',
                bbox=dict(facecolor='#faf5ff', alpha=0.95, pad=5),
                arrowprops=dict(arrowstyle='->', color='#9333ea', lw=1.5))

    label_point(ax1, A, 'A', (0.3, 1.0), L1)
    label_point(ax1, B, 'B', (-1, -0.7), L1)
    label_point(ax1, C, 'C', (1, -0.7), L1)
    label_point(ax1, D, 'D', (0.5, -1.0), L1)

    ax1.set_title('原图：∠C = 2∠B，AD 平分∠A', fontsize=13,
                  fontweight='bold', color='#1e293b')

    # ---- Right panel: AFTER (截长) ----
    draw_solid(ax2, A, B, color='#1e293b', lw=2.2)
    draw_solid(ax2, B, C, color='#1e293b', lw=2.2)
    draw_solid(ax2, C, A, color='#1e293b', lw=2.2)
    draw_dashed(ax2, A, D, color='#9333ea', lw=2.0)
    draw_solid(ax2, D, F, color='#16a34a', lw=2.5)

    tick = 0.04 * L2
    # Highlight AF = AC
    draw_solid(ax2, A, F, color='#2563eb', lw=2.8, alpha=0.5)
    draw_solid(ax2, A, C, color='#2563eb', lw=2.8, alpha=0.5)
    draw_equal_tick(ax2, (A + F) / 2, F - A, tick, color='#2563eb')
    draw_equal_tick(ax2, (A + C) / 2, C - A, tick, color='#2563eb')

    # Highlight DF = DC
    draw_equal_tick(ax2, (D + F) / 2, F - D, tick, color='#16a34a')
    draw_equal_tick(ax2, (D + C) / 2, C - D, tick, color='#16a34a')

    # Highlight BF (the remainder)
    draw_solid(ax2, B, F, color='#dc2626', lw=2.8, alpha=0.7)

    label_point(ax2, A, 'A', (0.3, 1.0), L2)
    label_point(ax2, B, 'B', (-1, -0.7), L2)
    label_point(ax2, C, 'C', (1, -0.7), L2)
    label_point(ax2, D, 'D', (0.5, -1.0), L2)
    label_point(ax2, F, 'F', (-0.8, 0.6), L2)

    ax2.annotate('AF = AC\n(截长)', xy=F, xytext=(-1.5, 2.8),
                fontsize=10, color='#2563eb', fontweight='bold',
                bbox=dict(facecolor='#eff6ff', alpha=0.95, pad=6),
                arrowprops=dict(arrowstyle='->', color='#2563eb', lw=1.5))
    ax2.annotate('DF = DC\n(△AFD ≌ △ACD)', xy=(D + F) / 2, xytext=(2.5, 1.8),
                fontsize=10, color='#16a34a', fontweight='bold',
                bbox=dict(facecolor='#f0fdf4', alpha=0.95, pad=6),
                arrowprops=dict(arrowstyle='->', color='#16a34a', lw=1.5))
    ax2.annotate('BF = DF = DC\n(△BDF 等腰)', xy=(B + F) / 2, xytext=(0.5, 2.5),
                fontsize=10, color='#dc2626', fontweight='bold',
                bbox=dict(facecolor='#fef2f2', alpha=0.95, pad=6),
                arrowprops=dict(arrowstyle='->', color='#dc2626', lw=1.5))

    ax2.set_title('截长法构造：CD = AB − AC', fontsize=13,
                  fontweight='bold', color='#1e293b')

    fig.suptitle('模型3：截长补短 — ∠C = 2∠B + 角平分线', fontsize=16,
                 fontweight='bold', color='#1e293b', y=1.02)

    ax2.text(0.5, -0.05, '证明思路：截 AF = AC → △AFD ≌ △ACD → DF = DC → BF = DF = DC → CD = AB − AC',
             transform=ax2.transAxes, fontsize=10, color='#1e293b',
             ha='center', va='top', fontweight='bold',
             bbox=dict(facecolor='#fef9c3', alpha=0.95, pad=6, edgecolor='#eab308', linewidth=1.5))

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'model3_cut_and_fill.png'),
                dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Model 3 done ✓")


# ================================================================
# Model 4: 构造等边三角形 → 连锁全等 (Problem 004 style)
# ================================================================
def draw_model4():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.5))
    for ax in [ax1, ax2]:
        ax.set_axis_off()

    # △ABC with ∠A = ∠C = 44°, ∠B = 92°, AB = BC
    B = np.array([0.0, 0.0])
    BC_len = 3.5
    C = np.array([BC_len, 0.0])
    AB_len = BC_len
    A = np.array([AB_len * np.cos(np.radians(92)), AB_len * np.sin(np.radians(92))])
    # M interior, ∠MAC = 16°, ∠MCA = 30°
    AC_vec = C - A
    AC_len = np.linalg.norm(AC_vec)
    AM_len = AC_len * np.sin(np.radians(30)) / np.sin(np.radians(134))
    # Direction of AC
    ac_angle = np.degrees(np.arctan2(AC_vec[1], AC_vec[0]))
    am_angle = ac_angle - 16   # toward AB side
    M = A + AM_len * np.array([np.cos(np.radians(am_angle)), np.sin(np.radians(am_angle))])

    # Equilateral △ACE on AC (same side as B)
    # B is on one side of AC; we rotate AC by -60° (CW) to get AE
    AE_vec = rotate_vec(AC_vec, -60)
    E = A + AE_vec

    pts = [A, B, C, M, E]
    for ax_i in [ax1, ax2]:
        autoscale(ax_i, pts, margin=0.32)

    L1 = compute_visual_scale(ax1)
    L2 = compute_visual_scale(ax2)

    # ---- Left panel: BEFORE ----
    draw_solid(ax1, A, B, color='#1e293b', lw=2.2)
    draw_solid(ax1, B, C, color='#1e293b', lw=2.2)
    draw_solid(ax1, C, A, color='#1e293b', lw=2.2)
    draw_solid(ax1, M, A, color='#9333ea', lw=1.8)
    draw_solid(ax1, M, C, color='#9333ea', lw=1.8)

    label_point(ax1, A, 'A', (-0.8, 1.0), L1)
    label_point(ax1, B, 'B', (-1, -0.8), L1)
    label_point(ax1, C, 'C', (1, -0.8), L1)
    label_point(ax1, M, 'M', (0.8, 0.4), L1, color='#9333ea')

    # Angle annotations
    ax1.annotate('44°', xy=A, xytext=(-1.2, 2.8),
                fontsize=10, color='#1e293b', fontweight='bold',
                bbox=dict(facecolor='white', alpha=0.95, pad=4),
                arrowprops=dict(arrowstyle='->', color='#1e293b', lw=1.2))
    ax1.annotate('44°', xy=C, xytext=(3.5, -1.5),
                fontsize=10, color='#1e293b', fontweight='bold',
                bbox=dict(facecolor='white', alpha=0.95, pad=4),
                arrowprops=dict(arrowstyle='->', color='#1e293b', lw=1.2))
    ax1.annotate('16°', xy=(A + M) / 2, xytext=(-0.8, 1.8),
                fontsize=9, color='#9333ea', fontweight='bold',
                bbox=dict(facecolor='#faf5ff', alpha=0.95, pad=3),
                arrowprops=dict(arrowstyle='->', color='#9333ea', lw=1.2))
    ax1.annotate('30°', xy=(C + M) / 2, xytext=(2.2, 0.3),
                fontsize=9, color='#9333ea', fontweight='bold',
                bbox=dict(facecolor='#faf5ff', alpha=0.95, pad=3),
                arrowprops=dict(arrowstyle='->', color='#9333ea', lw=1.2))

    ax1.set_title('原题：∠A = ∠C = 44°\n∠MAC = 16°，∠MCA = 30°',
                  fontsize=12, fontweight='bold', color='#1e293b')

    # ---- Right panel: AFTER ----
    # Base triangle (faded)
    draw_solid(ax2, A, B, color='#94a3b8', lw=1.5, alpha=0.4)
    draw_solid(ax2, B, C, color='#94a3b8', lw=1.5, alpha=0.4)
    draw_solid(ax2, C, A, color='#94a3b8', lw=1.5, alpha=0.4)

    # Equilateral △ACE — bold cyan
    draw_solid(ax2, A, C, color='#0891b2', lw=2.8)
    draw_solid(ax2, C, E, color='#0891b2', lw=2.8)
    draw_solid(ax2, E, A, color='#0891b2', lw=2.8)

    # Key proof lines
    draw_solid(ax2, B, E, color='#dc2626', lw=2.5)
    draw_solid(ax2, M, A, color='#9333ea', lw=1.8)
    draw_solid(ax2, M, C, color='#9333ea', lw=1.8)

    tick = 0.035 * L2
    # Equal ticks: AB = BC
    draw_equal_tick(ax2, (A + B) / 2, B - A, tick, color='#64748b')
    draw_equal_tick(ax2, (B + C) / 2, C - B, tick, color='#64748b')
    # Equal ticks: AE = CE = AC
    draw_equal_tick(ax2, (A + E) / 2, E - A, tick, color='#0891b2')
    draw_equal_tick(ax2, (C + E) / 2, E - C, tick, color='#0891b2')
    draw_equal_tick(ax2, (A + C) / 2, C - A, tick, color='#0891b2')

    label_point(ax2, A, 'A', (-0.8, 1.0), L2)
    label_point(ax2, B, 'B', (-1, -0.8), L2)
    label_point(ax2, C, 'C', (1, -0.8), L2)
    label_point(ax2, M, 'M', (0.8, 0.4), L2, color='#9333ea')
    label_point(ax2, E, 'E', (-0.3, -1.2), L2, color='#0891b2')

    # Key insight annotation
    ax2.annotate('∠EAC = 60°\n∠EAB = 60°−44° = 16°\n= ∠MAC （关键！）',
                xy=A, xytext=(-4.0, 4.0),
                fontsize=10, color='#dc2626', fontweight='bold',
                bbox=dict(facecolor='#fef2f2', alpha=0.95, pad=6, edgecolor='#dc2626'),
                arrowprops=dict(arrowstyle='->', color='#dc2626', lw=1.8))

    ax2.annotate('△ACE 等边', xy=(A + C) / 2, xytext=(3.0, 1.5),
                fontsize=10, color='#0891b2', fontweight='bold',
                bbox=dict(facecolor='#ecfeff', alpha=0.95, pad=6),
                arrowprops=dict(arrowstyle='->', color='#0891b2', lw=1.5))

    ax2.text(0.5, 0.5, '△ABE ≌ △AMC\n(ASA)', fontsize=10, color='#dc2626',
             fontweight='bold', ha='center', va='center',
             bbox=dict(facecolor='#fef2f2', alpha=0.95, pad=6))

    ax2.set_title('构造：以 AC 为边作等边△ACE\n△ABE ≌ △AMC (ASA)',
                  fontsize=12, fontweight='bold', color='#1e293b')

    fig.suptitle('模型4：特殊角 → 构造等边三角形 → 连锁全等',
                 fontsize=16, fontweight='bold', color='#1e293b', y=1.02)

    ax2.text(0.5, -0.05, '关键：造 60°，与 ∠A=44° 做差得 16°，恰好等于 ∠MAC → ASA 全等',
             transform=ax2.transAxes, fontsize=10, color='#1e293b',
             ha='center', va='top', fontweight='bold',
             bbox=dict(facecolor='#fef9c3', alpha=0.95, pad=6, edgecolor='#eab308', linewidth=1.5))

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'model4_equilateral_construction.png'),
                dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Model 4 done ✓")


# ================================================================
# Model 5: 分类讨论 — 等腰三角形分割
# ================================================================
def draw_model5():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.5))
    for ax in [ax1, ax2]:
        ax.set_axis_off()

    # ---- Case 1: ∠A = 180°/7 ≈ 25.714°, base = 77.143° ----
    A1 = np.array([0.0, 4.0])
    h1 = 4.0
    w1 = h1 * np.tan(np.radians(180 / 7 / 2))  # tan(12.857°)
    B1 = np.array([-w1, 0.0])
    C1 = np.array([w1, 0.0])
    AB1 = np.linalg.norm(A1 - B1)
    # D on AB with AD = DC; by sine law in △ACD
    AD1 = AB1 * np.sin(np.radians(180 / 7)) / np.sin(np.radians(180 - 2 * 180 / 7))
    D1 = A1 + (AD1 / AB1) * (B1 - A1)

    # ---- Case 2: ∠A = 36°, base = 72° ----
    A2 = np.array([0.0, 4.0])
    h2 = 4.0
    w2 = h2 * np.tan(np.radians(18))
    B2 = np.array([-w2, 0.0])
    C2 = np.array([w2, 0.0])
    AB2 = np.linalg.norm(A2 - B2)
    AD2 = AB2 * np.sin(np.radians(36)) / np.sin(np.radians(108))
    D2 = A2 + (AD2 / AB2) * (B2 - A2)

    for idx, (ax_i, A, B, C, D, title, case_name, legend_text) in enumerate([
        (ax1, A1, B1, C1, D1,
         '情况一：AD = DC，BD = BC\n∠A = 180°/7 ≈ 25.7°', 'case1',
         '蓝色 = AD = DC\n绿色 = BD = BC'),
        (ax2, A2, B2, C2, D2,
         '情况二：AD = DC，DC = CB\n∠A = 36°', 'case2',
         '蓝色 = AD = DC\n绿色 = DC = CB')
    ]):
        autoscale(ax_i, [A, B, C, D], margin=0.35)
        L = compute_visual_scale(ax_i)

        # △ABC
        draw_solid(ax_i, A, B, color='#1e293b', lw=2.0)
        draw_solid(ax_i, B, C, color='#1e293b', lw=2.0)
        draw_solid(ax_i, C, A, color='#1e293b', lw=2.0)

        # Equal ticks on AB and AC (isosceles)
        tick = 0.04 * L
        draw_equal_tick(ax_i, (A + B) / 2, B - A, tick, color='#1e293b')
        draw_equal_tick(ax_i, (A + C) / 2, C - A, tick, color='#1e293b')

        # Split line CD
        draw_solid(ax_i, C, D, color='#dc2626', lw=2.5)

        if case_name == 'case1':
            # AD = DC (blue)
            draw_equal_tick(ax_i, (A + D) / 2, D - A, tick, color='#2563eb')
            draw_equal_tick(ax_i, (C + D) / 2, D - C, tick, color='#2563eb')
            # BD = BC (green)
            draw_equal_tick(ax_i, (B + D) / 2, D - B, tick, color='#16a34a')
            draw_equal_tick(ax_i, (B + C) / 2, C - B, tick, color='#16a34a')
        else:
            # AD = DC (blue)
            draw_equal_tick(ax_i, (A + D) / 2, D - A, tick, color='#2563eb')
            draw_equal_tick(ax_i, (C + D) / 2, D - C, tick, color='#2563eb')
            # DC = CB (green)
            draw_equal_tick(ax_i, (C + D) / 2, D - C, tick, color='#16a34a')
            draw_equal_tick(ax_i, (B + C) / 2, C - B, tick, color='#16a34a')

        label_point(ax_i, A, 'A', (0, 1.1), L)
        label_point(ax_i, B, 'B', (-1, -0.8), L)
        label_point(ax_i, C, 'C', (1, -0.8), L)
        label_point(ax_i, D, 'D', (-1, 0.8), L, color='#dc2626')

        ax_i.set_title(title, fontsize=12, fontweight='bold', color='#1e293b')
        ax_i.text(0.02, 0.02, legend_text,
                  transform=ax_i.transAxes, fontsize=9,
                  va='bottom', bbox=dict(facecolor='white', alpha=0.9, pad=5))

    fig.suptitle('模型5：分类讨论 — 等腰三角形被分成两个等腰三角形\n过 C 作直线交 AB 于 D',
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

    def draw_box(x, y, w, h, text, color='#dbeafe', edge='#2563eb', fontsize=10):
        box = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                             boxstyle="round,pad=0.1",
                             facecolor=color, edgecolor=edge, linewidth=2, zorder=5)
        ax.add_patch(box)
        ax.text(x, y, text, ha='center', va='center', fontsize=fontsize,
                fontweight='bold', color='#1e293b', zorder=6)
        return (x, y)

    def draw_arrow(x1, y1, x2, y2, color='#64748b'):
        ax.annotate('', xy=(x2, y2 - 0.3), xytext=(x1, y1 + 0.3),
                   arrowprops=dict(arrowstyle='->', color=color, lw=1.8))

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
        (3.6, '截长补短\nAF = AC\n→ CD = AB−AC', '#a7f3d0'),
        (6.0, '构造等边△\n造 60° 角\n差得关键角', '#fbcfe8'),
        (8.4, '倍长中线\n→ SAS 全等\n→ 平行/等量', '#c7d2fe'),
        (10.8, '手拉手模型\nSAS 全等\n→ 平行/共线', '#fde68a'),
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