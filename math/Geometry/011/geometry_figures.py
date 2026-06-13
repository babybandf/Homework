"""
Problem 011: In triangle ABC with angle ACB = 2*angle B, AO bisects angle BAC
meeting BC at D. H is on AO; line l through H perpendicular to AO meets lines
AB, AC, BC at N, E, M respectively.

Three figures support: setup, (1) l through C, (2) M is midpoint, (3) general,
plus two proof-helper figures.
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager

# ========== 中文字体加载（绝对路径） ==========
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


# ========== 工具函数 ==========
def line_intersection(P1, d1, P2, d2):
    A = np.array([[d1[0], -d2[0]], [d1[1], -d2[1]]])
    b = P2 - P1
    t, _ = np.linalg.solve(A, b)
    return P1 + t * d1


_TEXT_BOX = dict(facecolor='white', edgecolor='none', alpha=0.78, pad=0.12)


def label_pt(ax, P, name, dx=0.0, dy=0.18, fontsize=13, color='black',
             marker_zorder=5, text_zorder=6):
    ax.plot(P[0], P[1], 'o', color=color, markersize=4, zorder=marker_zorder)
    ax.text(P[0] + dx, P[1] + dy, name, ha='center', va='center',
                        fontsize=fontsize, fontweight='bold', color=color,
            bbox=_TEXT_BOX, zorder=text_zorder)


def draw_angle_arc(ax, vertex, p1, p2, radius=0.35, color='blue', label=None,
                   label_offset=0.18):
    a1 = np.degrees(np.arctan2(p1[1] - vertex[1], p1[0] - vertex[0]))
    a2 = np.degrees(np.arctan2(p2[1] - vertex[1], p2[0] - vertex[0]))
    if a2 < a1:
        a1, a2 = a2, a1
    if a2 - a1 > 180:
        a1, a2 = a2, a1 + 360
    arc = patches.Arc(vertex, 2 * radius, 2 * radius,
                      angle=0, theta1=a1, theta2=a2,
                      color=color, linewidth=1.5)
    ax.add_patch(arc)
    if label:
        mid = np.radians((a1 + a2) / 2)
        r = radius + label_offset
        ax.text(vertex[0] + r * np.cos(mid),
                vertex[1] + r * np.sin(mid),
                label, ha='center', va='center',
                fontsize=10, color=color)


def tick_eq(ax, P1, P2, color='#e74c3c', size=0.10):
    mid = (P1 + P2) / 2
    d = P2 - P1
    L = np.linalg.norm(d)
    perp = np.array([-d[1], d[0]]) / L * size
    ax.plot([mid[0] - perp[0], mid[0] + perp[0]],
            [mid[1] - perp[1], mid[1] + perp[1]],
            color=color, linewidth=2)


def draw_ao(ax, A, D, H, color='#9b59b6'):
    AO_end = A + 1.05 * (D - A)
    ax.plot([A[0], AO_end[0]], [A[1], AO_end[1]],
            color=color, linewidth=1.6, linestyle='--', zorder=4)
    # Keep AO visibly connected at H even if the dash pattern hits a gap there.
    cap = 0.22
    p_start = H - cap * AO_dir
    p_end = H + cap * AO_dir
    ax.plot([p_start[0], p_end[0]], [p_start[1], p_end[1]],
            color=color, linewidth=1.8, zorder=5)


# ========== 几何参数 ==========
BETA_DEG = 40.0
BETA = np.radians(BETA_DEG)

B = np.array([0.0, 0.0])
C = np.array([6.0, 0.0])

R2 = 6.0 / np.sin(np.radians(180 - 3 * BETA_DEG))
c_len = R2 * np.sin(np.radians(2 * BETA_DEG))   # |AB|
b_len = R2 * np.sin(BETA)                       # |AC|
A = B + c_len * np.array([np.cos(BETA), np.sin(BETA)])

BDx = 6.0 * c_len / (b_len + c_len)
D = B + BDx * (C - B) / 6.0

AO_dir = D - A
AO_dir = AO_dir / np.linalg.norm(AO_dir)
l_dir = np.array([-AO_dir[1], AO_dir[0]])


def figure_for(M, savename, title_zh, with_NEM_labels=True,
               highlight_segments=None, special_C_label=None):
    fig, ax = plt.subplots(figsize=(8.6, 7.0))
    ax.set_aspect('equal')

    H = line_intersection(A, AO_dir, M, l_dir)
    N = line_intersection(B, A - B, M, l_dir)
    E = line_intersection(A, C - A, M, l_dir)

    extend = 0.6
    pts_on_l = [N, E, M]
    ts = [(p - H) @ l_dir for p in pts_on_l]
    L_start = H + (min(ts) - extend) * l_dir
    L_end = H + (max(ts) + extend) * l_dir

    ax.add_patch(plt.Polygon([A, B, C], closed=True, fill=False,
                             edgecolor='#222222', linewidth=2.0))
    ax.plot([L_start[0], L_end[0]], [L_start[1], L_end[1]],
            color='#1565c0', linewidth=1.6, zorder=2)
    draw_ao(ax, A, D, H)

    rsize = 0.18
    p1 = H - rsize * AO_dir
    p2 = p1 + rsize * l_dir
    p3 = H + rsize * l_dir
    ax.plot([p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]],
            color='#1565c0', linewidth=1.2, zorder=1)

    if highlight_segments:
        for P1, P2, col, lab in highlight_segments:
            ax.plot([P1[0], P2[0]], [P1[1], P2[1]],
                    color=col, linewidth=4.0, alpha=0.85)
            mid = (P1 + P2) / 2
            d = P2 - P1
            L = np.linalg.norm(d)
            perp = np.array([-d[1], d[0]]) / (L + 1e-9)
            if perp[1] < 0:
                perp = -perp
            off_scale = 0.14 if lab == 'BN' else 0.28
            off = off_scale * perp
            ax.text(mid[0] + off[0], mid[1] + off[1], lab, color=col,
                    fontsize=12, fontweight='bold', ha='center',
                    bbox=_TEXT_BOX)

    label_pt(ax, A, 'A', dy=0.28)
    label_pt(ax, B, 'B', dx=-0.22, dy=-0.05)
    if special_C_label:
        label_pt(ax, C, special_C_label, dx=0.65, dy=-0.05)
    else:
        label_pt(ax, C, 'C', dx=0.25, dy=-0.05)

        label_pt(ax, D, 'D', dx=0.14, dy=-0.12, color='#7d3c98')
        label_pt(ax, H, 'H', dx=-0.28, dy=-0.34, color='#1565c0', marker_zorder=3)
    if with_NEM_labels:
        label_pt(ax, N, 'N', dx=-0.30, dy=0.28, color='#1565c0')
        label_pt(ax, E, 'E', dx=0.32, dy=0.10, color='#1565c0')
        label_pt(ax, M, 'M', dx=0.00, dy=-0.40, color='#1565c0')

    O_marker = D + 1.10 * AO_dir / np.linalg.norm(AO_dir)
    ax.text(O_marker[0] - 0.02, O_marker[1] - 0.10, 'O',
            fontsize=12, color='#9b59b6', bbox=_TEXT_BOX)

    ax.set_title(title_zh, fontsize=14)
    all_pts = np.array([A, B, C, D, H, N, E, M, L_start, L_end])
    margin = 0.7
    ax.set_xlim(all_pts[:, 0].min() - margin, all_pts[:, 0].max() + margin)
    ax.set_ylim(all_pts[:, 1].min() - margin, all_pts[:, 1].max() + margin)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(_BASE_DIR, savename),
                dpi=150, bbox_inches='tight')
    plt.close()


# ========== Figure 1: 题目原图（M 在 BC 延长线 C 之外，与原题图1一致） ==========
figure_for(
    np.array([7.2, 0.0]),
    'step1_setup.png',
    title_zh='图1：l ⊥ AO 于 H，交直线 AB、AC、BC 于 N、E、M',
)

# ========== Figure 2: (1) l 过 C ==========
figure_for(
    C.copy(),
    'step2_part1_throughC.png',
    title_zh='图2（第1问）：l 过 C，此时 E、M 与 C 重合',
    special_C_label='C (=M=E)',
)

# ========== Figure 3: (1) 证明辅助 — △ANC 等腰 ==========
fig, ax = plt.subplots(figsize=(8.4, 6.8))
ax.set_aspect('equal')
M5 = C.copy()
H5 = line_intersection(A, AO_dir, M5, l_dir)
N5 = line_intersection(B, A - B, M5, l_dir)

ax.add_patch(plt.Polygon([A, B, C], closed=True, fill=False,
                         edgecolor='#222', linewidth=2))
ax.add_patch(plt.Polygon([A, N5, C], closed=True,
                         facecolor='#bbdefb', alpha=0.35,
                         edgecolor='#1565c0', linewidth=2))

draw_ao(ax, A, D, H5)

extend = 0.6
ts = [(p - H5) @ l_dir for p in [N5, C]]
L_start = H5 + (min(ts) - extend) * l_dir
L_end = H5 + (max(ts) + extend) * l_dir
ax.plot([L_start[0], L_end[0]], [L_start[1], L_end[1]],
        color='#1565c0', linewidth=1.6)

rsize = 0.18
p1 = H5 - rsize * AO_dir; p2 = p1 + rsize * l_dir; p3 = H5 + rsize * l_dir
ax.plot([p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]],
        color='#1565c0', linewidth=1.2, zorder=1)

tick_eq(ax, A, N5)
tick_eq(ax, A, C)

# ∠NAH at A (between rays AN and AH)
draw_angle_arc(ax, A, N5, H5, radius=0.55, color='#9b59b6')
# ∠HAC at A
draw_angle_arc(ax, A, H5, C, radius=0.75, color='#9b59b6')

label_pt(ax, A, 'A', dy=0.28)
label_pt(ax, B, 'B', dx=-0.22, dy=-0.05)
label_pt(ax, C, 'C (=M=E)', dx=0.65, dy=-0.05)
label_pt(ax, N5, 'N', dx=-0.30, dy=0.28, color='#1565c0')
label_pt(ax, H5, 'H', dx=-0.28, dy=-0.34, color='#1565c0', marker_zorder=3)

ax.set_title('AN = AC（AO 是 ∠NAC 的角平分线且 AO ⊥ NC）', fontsize=13)
all_pts = np.array([A, B, C, H5, N5, L_start, L_end])
margin = 0.7
ax.set_xlim(all_pts[:, 0].min() - margin, all_pts[:, 0].max() + margin)
ax.set_ylim(all_pts[:, 1].min() - margin, all_pts[:, 1].max() + margin)
ax.axis('off')
plt.tight_layout()
plt.savefig(os.path.join(_BASE_DIR, 'step2b_part1_proof.png'),
            dpi=150, bbox_inches='tight')
plt.close()


# ========== Figure 4: (2) M 是 BC 中点 ==========
M_mid = (B + C) / 2
H_mid = line_intersection(A, AO_dir, M_mid, l_dir)
N_mid = line_intersection(B, A - B, M_mid, l_dir)
E_mid = line_intersection(A, C - A, M_mid, l_dir)
figure_for(
    M_mid,
    'step3_part2_midpoint.png',
    title_zh='图3（第2问）：M 为 BC 中点，CD = 2·CE',
    highlight_segments=[
        (C, D, '#e74c3c', 'CD'),
        (C, E_mid, '#27ae60', 'CE'),
    ],
)

# ========== Figure 5: (2) 倍长中线辅助图 ==========
fig, ax = plt.subplots(figsize=(8.6, 7.0))
ax.set_aspect('equal')
G_aux = 2 * M_mid - N_mid

ax.add_patch(plt.Polygon([A, B, C], closed=True, fill=False,
                         edgecolor='#222', linewidth=2))
# AO
draw_ao(ax, A, D, H_mid)
# l (extended through G as well)
extend = 0.6
ts = [(p - H_mid) @ l_dir for p in [N_mid, E_mid, M_mid, G_aux]]
L_start = H_mid + (min(ts) - extend) * l_dir
L_end = H_mid + (max(ts) + extend) * l_dir
ax.plot([L_start[0], L_end[0]], [L_start[1], L_end[1]],
        color='#1565c0', linewidth=1.4)

# CG segment
ax.plot([C[0], G_aux[0]], [C[1], G_aux[1]],
        color='#27ae60', linewidth=2.0)
# BN
ax.plot([B[0], N_mid[0]], [B[1], N_mid[1]],
        color='#1565c0', linewidth=2.6)
# tick BN = CG
tick_eq(ax, B, N_mid, color='#1565c0')
tick_eq(ax, C, G_aux, color='#1565c0')
# tick BM = MC
tick_eq(ax, B, M_mid, color='#9b59b6')
tick_eq(ax, M_mid, C, color='#9b59b6')
# tick NM = MG
tick_eq(ax, N_mid, M_mid, color='#e67e22')
tick_eq(ax, M_mid, G_aux, color='#e67e22')

label_pt(ax, A, 'A', dy=0.28)
label_pt(ax, B, 'B', dx=-0.22, dy=-0.05)
label_pt(ax, C, 'C', dx=0.25, dy=-0.05)
label_pt(ax, D, 'D', dx=0.14, dy=-0.12, color='#7d3c98')
label_pt(ax, H_mid, 'H', dx=-0.28, dy=-0.34, color='#1565c0', marker_zorder=3)
label_pt(ax, N_mid, 'N', dx=-0.30, dy=0.28, color='#1565c0')
label_pt(ax, E_mid, 'E', dx=0.32, dy=0.10, color='#1565c0')
label_pt(ax, M_mid, 'M', dx=0.00, dy=-0.40, color='#1565c0')
label_pt(ax, G_aux, 'G', dx=0.25, dy=-0.10, color='#27ae60')

ax.set_title('倍长中线：延长 NM 到 G 使 MG = MN，△BNM ≌ △CGM',
             fontsize=13)
all_pts = np.array([A, B, C, D, H_mid, N_mid, E_mid, M_mid, G_aux,
                    L_start, L_end])
margin = 0.7
ax.set_xlim(all_pts[:, 0].min() - margin, all_pts[:, 0].max() + margin)
ax.set_ylim(all_pts[:, 1].min() - margin, all_pts[:, 1].max() + margin)
ax.axis('off')
plt.tight_layout()
plt.savefig(os.path.join(_BASE_DIR, 'step3b_part2_double_median.png'),
            dpi=150, bbox_inches='tight')
plt.close()


# ========== Figure 6: (3) 一般情形 BN + CE = CD ==========
M4 = np.array([2.0, 0.0])
H4 = line_intersection(A, AO_dir, M4, l_dir)
N4 = line_intersection(B, A - B, M4, l_dir)
E4 = line_intersection(A, C - A, M4, l_dir)
figure_for(
    M4,
    'step4_part3_general.png',
    title_zh='图4（第3问）：一般情形 BN + CE = CD',
    highlight_segments=[
        (B, N4, '#1565c0', 'BN'),
        (C, E4, '#27ae60', 'CE'),
        (C, D, '#e74c3c', 'CD'),
    ],
)


# ========== Figure 6b: 第3问证明图（在 AB 上截取 AF = AC） ==========
fig, ax = plt.subplots(figsize=(8.6, 7.0))
ax.set_aspect('equal')

H4b = line_intersection(A, AO_dir, M4, l_dir)
N4b = line_intersection(B, A - B, M4, l_dir)
E4b = line_intersection(A, C - A, M4, l_dir)
F4 = A + b_len * (B - A) / c_len  # AF = AC = b_len, on segment AB

# 三角形
ax.add_patch(plt.Polygon([A, B, C], closed=True, fill=False,
                         edgecolor='#222', linewidth=2))
# l 直线
extend = 0.6
ts = [(p - H4b) @ l_dir for p in [N4b, E4b, M4]]
L_start = H4b + (min(ts) - extend) * l_dir
L_end = H4b + (max(ts) + extend) * l_dir
ax.plot([L_start[0], L_end[0]], [L_start[1], L_end[1]],
        color='#1565c0', linewidth=1.4)
# AO
draw_ao(ax, A, D, H4b)
# 辅助线 DF
ax.plot([D[0], F4[0]], [D[1], F4[1]], color='#27ae60',
        linewidth=1.5, linestyle=':')

# 高亮线段
# BN（粗蓝）
ax.plot([B[0], N4b[0]], [B[1], N4b[1]],
        color='#1565c0', linewidth=4.0, alpha=0.85)
# NF（橙）= CE
ax.plot([N4b[0], F4[0]], [N4b[1], F4[1]],
        color='#e67e22', linewidth=4.0, alpha=0.85)
# CE（绿）
ax.plot([C[0], E4b[0]], [C[1], E4b[1]],
        color='#e67e22', linewidth=4.0, alpha=0.85)
# CD（红）
ax.plot([C[0], D[0]], [C[1], D[1]],
        color='#e74c3c', linewidth=4.0, alpha=0.85)

# tick: AF = AC
tick_eq(ax, A, F4, color='#e74c3c')
tick_eq(ax, A, C, color='#e74c3c')
# tick: BF = CD（用蓝色十字）
tick_eq(ax, F4, B, color='#1565c0')
tick_eq(ax, C, D, color='#1565c0')
# tick: NF = CE（用橙色）
tick_eq(ax, N4b, F4, color='#e67e22')
tick_eq(ax, C, E4b, color='#e67e22')

label_pt(ax, A, 'A', dy=0.28)
label_pt(ax, B, 'B', dx=-0.22, dy=-0.05)
label_pt(ax, C, 'C', dx=0.25, dy=-0.05)
label_pt(ax, D, 'D', dx=0.14, dy=-0.12, color='#7d3c98')
label_pt(ax, H4b, 'H', dx=-0.28, dy=-0.34, color='#1565c0', marker_zorder=3)
label_pt(ax, N4b, 'N', dx=-0.30, dy=0.28, color='#1565c0')
label_pt(ax, E4b, 'E', dx=0.32, dy=0.10, color='#1565c0')
label_pt(ax, M4, 'M', dx=0.00, dy=-0.40, color='#1565c0')
label_pt(ax, F4, 'F', dx=0.30, dy=0.05, color='#27ae60')

# 文字标签
mid_bn = (B + N4b) / 2
d_bn = N4b - B
perp_bn = np.array([-d_bn[1], d_bn[0]]) / (np.linalg.norm(d_bn) + 1e-9)
if perp_bn[1] < 0:
    perp_bn = -perp_bn
ax.text(mid_bn[0] + 0.14 * perp_bn[0], mid_bn[1] + 0.14 * perp_bn[1], 'BN',
        color='#1565c0', fontsize=12, fontweight='bold', ha='center',
        bbox=_TEXT_BOX)

mid_nf = (N4b + F4) / 2
d_nf = F4 - N4b
perp_nf = np.array([-d_nf[1], d_nf[0]]) / (np.linalg.norm(d_nf) + 1e-9)
if perp_nf[1] < 0:
    perp_nf = -perp_nf
ax.text(mid_nf[0] + 0.30 * perp_nf[0], mid_nf[1] + 0.30 * perp_nf[1], 'NF=CE',
        color='#e67e22', fontsize=11, fontweight='bold', ha='center',
        bbox=_TEXT_BOX)

mid_ce = (C + E4b) / 2
d_ce = E4b - C
perp_ce = np.array([-d_ce[1], d_ce[0]]) / (np.linalg.norm(d_ce) + 1e-9)
if perp_ce[1] < 0:
    perp_ce = -perp_ce
ax.text(mid_ce[0] + 0.26 * perp_ce[0], mid_ce[1] + 0.26 * perp_ce[1], 'CE',
        color='#e67e22', fontsize=12, fontweight='bold', ha='left',
        bbox=_TEXT_BOX)
ax.text((C[0]+D[0])/2, D[1] - 0.32, 'CD',
        color='#e74c3c', fontsize=12, fontweight='bold', ha='center',
        bbox=_TEXT_BOX)

ax.set_title('第3问证明：AB 上截 AF = AC，则 BF = CD，且 NF = CE',
             fontsize=13)
all_pts = np.array([A, B, C, D, H4b, N4b, E4b, M4, F4, L_start, L_end])
margin = 0.7
ax.set_xlim(all_pts[:, 0].min() - margin, all_pts[:, 0].max() + margin)
ax.set_ylim(all_pts[:, 1].min() - margin, all_pts[:, 1].max() + margin)
ax.axis('off')
plt.tight_layout()
plt.savefig(os.path.join(_BASE_DIR, 'step4c_part3_proof.png'),
            dpi=150, bbox_inches='tight')
plt.close()


# ========== Figure 7: 引理 AB = AC + CD ==========
fig, ax = plt.subplots(figsize=(8.4, 6.8))
ax.set_aspect('equal')
ax.add_patch(plt.Polygon([A, B, C], closed=True, fill=False,
                         edgecolor='#222', linewidth=2))
F = A + b_len * (B - A) / c_len
ax.plot([D[0], F[0]], [D[1], F[1]], color='#27ae60', linewidth=1.6)

# AF = AC (red)
tick_eq(ax, A, F, color='#e74c3c')
tick_eq(ax, A, C, color='#e74c3c')
# FB = DC = DF (blue)
tick_eq(ax, F, B, color='#1565c0')
tick_eq(ax, D, C, color='#1565c0')
tick_eq(ax, D, F, color='#1565c0')

draw_ao(ax, A, D, D + 0.55 * AO_dir)

label_pt(ax, A, 'A', dy=0.28)
label_pt(ax, B, 'B', dx=-0.22, dy=-0.05)
label_pt(ax, C, 'C', dx=0.25, dy=-0.05)
label_pt(ax, D, 'D', dx=0.14, dy=-0.12, color='#7d3c98')
label_pt(ax, F, 'F', dx=-0.30, dy=0.0, color='#27ae60')

ax.set_title('引理：AB = AC + CD（AB 上截 AF = AC，连 DF）',
             fontsize=13)
all_pts = np.array([A, B, C, D, F])
margin = 0.7
ax.set_xlim(all_pts[:, 0].min() - margin, all_pts[:, 0].max() + margin)
ax.set_ylim(all_pts[:, 1].min() - margin, all_pts[:, 1].max() + margin)
ax.axis('off')
plt.tight_layout()
plt.savefig(os.path.join(_BASE_DIR, 'step4b_lemma_AB_AC_CD.png'),
            dpi=150, bbox_inches='tight')
plt.close()


print("All figures generated successfully!")
