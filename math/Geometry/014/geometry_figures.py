"""
Problem 014: 等边三角形中的全等证明与平行证明

题目：如图(1)，等边△ABC中，D是AB边上的动点，以CD为一边，向上作等边△EDC，连接AE。

(1) △DBC和△EAC会全等吗？请说说你的理由；
(2) 试说明 AE∥BC 的理由；
(3) 如图(2)，将(1)动点D运动到边BA的延长线上，所作仍为等边三角形，请问是否仍有 AE∥BC？证明你的猜想。
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager

# ========== 中文字体加载（绝对路径，跨环境一致） ==========
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


# ========== G-标准核心：参考长度 + 自检器 ==========
def compute_visual_scale(ax):
    """L_ref = min(xrange, yrange)。MUST 在 set_xlim/set_ylim 之后调用。"""
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    return min(abs(x1 - x0), abs(y1 - y0))


def _seg_point_distance(p, a, b):
    """点 p 到线段 ab 的距离。"""
    p, a, b = np.asarray(p), np.asarray(a), np.asarray(b)
    ab = b - a
    L2 = float(ab @ ab)
    if L2 < 1e-12:
        return float(np.linalg.norm(p - a))
    t = float((p - a) @ ab) / L2
    t = max(0.0, min(1.0, t))
    foot = a + t * ab
    return float(np.linalg.norm(p - foot))


def _rects_overlap(r1, r2, pad=0.0):
    """两个轴对齐矩形 (xmin,ymin,xmax,ymax) 是否相交（含 pad 外扩）。"""
    return not (r1[2] + pad < r2[0] or r2[2] + pad < r1[0] or
                r1[3] + pad < r2[1] or r2[3] + pad < r1[1])


def _seg_rect_distance(a, b, rect):
    """线段 ab 到轴对齐矩形 rect 的最小距离；相交返回 0。"""
    a, b = np.asarray(a, float), np.asarray(b, float)
    xmin, ymin, xmax, ymax = rect
    for p in (a, b):
        if xmin <= p[0] <= xmax and ymin <= p[1] <= ymax:
            return 0.0
    corners = [np.array([xmin, ymin]), np.array([xmax, ymin]),
               np.array([xmax, ymax]), np.array([xmin, ymax])]
    edges = [(corners[i], corners[(i + 1) % 4]) for i in range(4)]
    def _ccw(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    def _intersect(p1, p2, p3, p4):
        d1 = _ccw(p3, p4, p1); d2 = _ccw(p3, p4, p2)
        d3 = _ccw(p1, p2, p3); d4 = _ccw(p1, p2, p4)
        return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))
    for e0, e1 in edges:
        if _intersect(a, b, e0, e1):
            return 0.0
    dmin = min(_seg_point_distance(c, a, b) for c in corners)
    for e0, e1 in edges:
        dmin = min(dmin, _seg_point_distance(a, e0, e1),
                   _seg_point_distance(b, e0, e1))
    return float(dmin)


class LayoutAuditor:
    """G-标准自检器（自动登记 + bbox 感知）。"""

    def __init__(self, ax, fig_name='figure'):
        self.ax = ax
        self.fig_name = fig_name
        self.scale = compute_visual_scale(ax)
        self.points = {}
        self.segments = []
        self.right_angles = []
        self.texts = []

    def add_segment(self, a, b, owner_points=()):
        self.segments.append((np.asarray(a, float),
                              np.asarray(b, float),
                              set(owner_points)))

    def add_right_angle(self, H, size):
        self.right_angles.append((np.asarray(H, float), float(size)))

    def add_point_anchor(self, name, xy):
        self.points[name] = np.asarray(xy, float)

    def register_text(self, artist, kind='label', name='', anchor=None,
                      owners=(), is_box=False, owner_seg=None):
        self.texts.append(dict(
            kind=kind, name=name, artist=artist,
            anchor=None if anchor is None else np.asarray(anchor, float),
            owners=set(owners), is_box=is_box,
            owner_seg=None if owner_seg is None
            else (np.asarray(owner_seg[0], float), np.asarray(owner_seg[1], float))))

    def _text_rect(self, artist):
        fig = self.ax.figure
        try:
            renderer = fig.canvas.get_renderer()
        except AttributeError:
            fig.canvas.draw()
            renderer = fig.canvas.get_renderer()
        bb = artist.get_window_extent(renderer=renderer)
        inv = self.ax.transData.inverted()
        (x0, y0) = inv.transform((bb.x0, bb.y0))
        (x1, y1) = inv.transform((bb.x1, bb.y1))
        return (min(x0, x1), min(y0, y1), max(x0, x1), max(y1, y1))

    def check(self):
        """返回违规列表（空 = PASS）。MUST 修复至空再保存。"""
        L = self.scale
        delta_safe = 0.025 * L
        v = []
        self.ax.figure.canvas.draw()

        ax_texts = [t for t in self.ax.texts
                    if (t.get_text() or '').strip()
                    and (t.get_alpha() is None or t.get_alpha() > 0.05)]
        if len(ax_texts) > 0 and len(self.texts) == 0:
            v.append(
                f'G0 LayoutAuditor created/activated AFTER drawing: ax has '
                f'{len(ax_texts)} text artists but auditor registered 0. ')
            return v

        for H, size in self.right_angles:
            if size > 0.05 * L:
                v.append(f'G1 right_angle@{np.round(H,3).tolist()}: size={size:.3f} > 0.05*L_ref')
            for a, b, _ in self.segments:
                seg_len = float(np.linalg.norm(b - a))
                d = _seg_point_distance(H, a, b)
                if d < 0.5 * size and seg_len > 0 and size > 0.08 * seg_len:
                    v.append(f'G1 right_angle@{np.round(H,3).tolist()}: size={size:.3f} > 8% of nearby seg')

        rects = []
        for t in self.texts:
            try:
                rects.append(self._text_rect(t['artist']))
            except Exception:
                rects.append(None)

        for t, r in zip(self.texts, rects):
            if r is None:
                continue
            for a, b, owners in self.segments:
                if t['owners'] & owners:
                    continue
                d = _seg_rect_distance(a, b, r)
                if d < delta_safe:
                    label = t['name'] or t['kind']
                    v.append(f'G6 text "{label}" overlaps/near segment {sorted(owners)}: d={d:.3f} < {delta_safe:.3f}')

        max_own = 0.12 * L
        for t, r in zip(self.texts, rects):
            if r is None or t.get('owner_seg') is None:
                continue
            a, b = t['owner_seg']
            d = _seg_rect_distance(a, b, r)
            if d > max_own:
                label = t['name'] or t['kind']
                v.append(f'G5b text "{label}" too far from its own segment: d={d:.3f} > {max_own:.3f}')

        for i in range(len(self.texts)):
            for j in range(i + 1, len(self.texts)):
                ri, rj = rects[i], rects[j]
                if ri is None or rj is None:
                    continue
                if _rects_overlap(ri, rj, pad=0.3 * delta_safe):
                    ni = self.texts[i]['name'] or self.texts[i]['kind']
                    nj = self.texts[j]['name'] or self.texts[j]['kind']
                    v.append(f'G6b text "{ni}" and "{nj}" bbox overlap')

        for t, r in zip(self.texts, rects):
            if r is None or not t['is_box']:
                continue
            for a, b, owners in self.segments:
                d = _seg_rect_distance(a, b, r)
                if d < delta_safe:
                    label = t['name'] or 'annotation-box'
                    v.append(f'G12 annotation box "{label}" overlaps geometry segment {sorted(owners)}')

        names = list(self.points.keys())
        threshold = 0.15 * L
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                n1, n2 = names[i], names[j]
                p1, p2 = self.points[n1], self.points[n2]
                if float(np.linalg.norm(p1 - p2)) >= threshold:
                    continue
                t1 = next((t for t in self.texts if t['kind'] == 'point' and t['name'] == n1), None)
                t2 = next((t for t in self.texts if t['kind'] == 'point' and t['name'] == n2), None)
                if not t1 or not t2 or t1['anchor'] is None or t2['anchor'] is None:
                    continue
                d1 = t1['anchor'] - p1
                d2 = t2['anchor'] - p2
                n1m, n2m = np.linalg.norm(d1), np.linalg.norm(d2)
                if n1m < 1e-9 or n2m < 1e-9:
                    continue
                cos_a = max(-1.0, min(1.0, float((d1 @ d2) / (n1m * n2m))))
                if cos_a > 1e-3:
                    v.append(f'G7 cluster "{n1}"/"{n2}" close but label dirs not split')

        extreme_thr = 0.05 * L
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                n1, n2 = names[i], names[j]
                p1, p2 = self.points[n1], self.points[n2]
                d_pp = float(np.linalg.norm(p1 - p2))
                if d_pp >= extreme_thr:
                    continue
                t1 = next((t for t in self.texts if t['kind'] == 'point' and t['name'] == n1), None)
                t2 = next((t for t in self.texts if t['kind'] == 'point' and t['name'] == n2), None)
                if t1 is None or t2 is None:
                    continue
                a1 = t1['artist'].get_alpha() or 1.0
                a2 = t2['artist'].get_alpha() or 1.0
                if a1 < 0.5 or a2 < 0.5:
                    continue
                v.append(f'G7b extreme cluster "{n1}"/"{n2}" too close')

        for H, size in self.right_angles:
            rH = (H[0] - size, H[1] - size, H[0] + size, H[1] + size)
            for name, P in self.points.items():
                if float(np.linalg.norm(P - H)) < 0.5 * size:
                    continue
                if (rH[0] - delta_safe <= P[0] <= rH[2] + delta_safe and
                        rH[1] - delta_safe <= P[1] <= rH[3] + delta_safe):
                    v.append(f'G14 right-angle@{np.round(H,3).tolist()} bracket area contains other point "{name}"')

        return v


_ACTIVE_AUDITOR = None


def set_active_auditor(auditor):
    global _ACTIVE_AUDITOR
    _ACTIVE_AUDITOR = auditor


def _auto_register(artist, kind='label', name='', anchor=None, owners=(), is_box=False, owner_seg=None):
    if _ACTIVE_AUDITOR is not None:
        _ACTIVE_AUDITOR.register_text(artist, kind=kind, name=name,
                                      anchor=anchor, owners=owners, is_box=is_box,
                                      owner_seg=owner_seg)


def draw_triangle(ax, A, B, C, color='black', linewidth=1.8, alpha=1.0, names=None):
    pts = np.array([A, B, C, A])
    ax.plot(pts[:, 0], pts[:, 1], color=color, linewidth=linewidth,
            alpha=alpha, zorder=2)
    if names is not None and _ACTIVE_AUDITOR is not None:
        nA, nB, nC = names
        _ACTIVE_AUDITOR.add_segment(A, B, owner_points={nA, nB})
        _ACTIVE_AUDITOR.add_segment(B, C, owner_points={nB, nC})
        _ACTIVE_AUDITOR.add_segment(C, A, owner_points={nC, nA})


def draw_aux_line(ax, p1, p2, owners=(), color='#9b59b6', linewidth=1.6,
                  linestyle='--', zorder=4, alpha=1.0):
    p1, p2 = np.asarray(p1, float), np.asarray(p2, float)
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linewidth=linewidth,
            linestyle=linestyle, zorder=zorder, alpha=alpha)
    if _ACTIVE_AUDITOR is not None:
        _ACTIVE_AUDITOR.add_segment(p1, p2, owner_points=set(owners))


def label_point(ax, P, name, direction=(1.0, 1.0), scale=1.0,
                offset_ratio=0.055, fontsize=13, color='black',
                marker_zorder=5, text_zorder=6, owners=None):
    if offset_ratio > 0.20:
        raise ValueError(f'label_point offset_ratio={offset_ratio:.3f} is too large')
    d = np.array(direction, dtype=float)
    n = np.linalg.norm(d)
    if n < 1e-9:
        d = np.array([0.0, 1.0])
        n = 1.0
    d = d / n * (scale * offset_ratio)
    anchor = np.array([P[0] + d[0], P[1] + d[1]])
    ax.plot(P[0], P[1], 'o', color=color, markersize=4, zorder=marker_zorder)
    art = ax.text(anchor[0], anchor[1], name,
                  ha='center', va='center',
                  fontsize=fontsize, fontweight='bold', color=color,
                  bbox=_TEXT_BOX, zorder=text_zorder)
    if _ACTIVE_AUDITOR is not None:
        _ACTIVE_AUDITOR.add_point_anchor(name, P)
        _auto_register(art, kind='point', name=name, anchor=anchor,
                       owners=(owners if owners is not None else {name}))
    return anchor


def place_segment_label(ax, p1, p2, text, color, scale=1.0,
                        offset_ratio=0.055, fontsize=12, side=None, owners=None):
    p1, p2 = np.asarray(p1, float), np.asarray(p2, float)
    mid = (p1 + p2) / 2
    d = p2 - p1
    L = np.linalg.norm(d)
    perp = np.array([-d[1], d[0]]) / (L + 1e-9)
    if side is None:
        if perp[1] < 0:
            perp = -perp
    else:
        if (perp[1] > 0 and side < 0) or (perp[1] < 0 and side > 0):
            perp = -perp
    off = scale * offset_ratio
    art = ax.text(mid[0] + off * perp[0], mid[1] + off * perp[1], text,
                  color=color, ha='center', va='center', fontsize=fontsize,
                  fontweight='bold', bbox=_TEXT_BOX, zorder=6)
    _auto_register(art, kind='seglabel', name=text,
                   owners=(owners if owners is not None else set()),
                   owner_seg=(p1, p2))
    return art


def annotate_box(ax, xy, text, scale=1.0, color='#1565c0',
                 facecolor='#e3f2fd', fontsize=12, owners=None):
    art = ax.text(xy[0], xy[1], text, ha='center', va='center',
                  fontsize=fontsize, fontweight='bold', color=color,
                  bbox=dict(facecolor=facecolor, edgecolor=color, alpha=0.9, pad=6),
                  zorder=7)
    _auto_register(art, kind='box', name=text.split('\n')[0][:16],
                   owners=(owners if owners is not None else set()), is_box=True)
    return art


def place_legend_auto(ax, text, segments, scale=1.0, color='#1565c0',
                      facecolor='#e3f2fd', fontsize=12):
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    pad = 0.14 * scale
    candidates = {
        'TL': (x0 + pad, y1 - pad), 'TR': (x1 - pad, y1 - pad),
        'BL': (x0 + pad, y0 + pad), 'BR': (x1 - pad, y0 + pad),
    }
    best, best_d = None, -1.0
    for _, xy in candidates.items():
        xy = np.asarray(xy, float)
        dmin = min((_seg_point_distance(xy, np.asarray(a, float), np.asarray(b, float))
                    for a, b in segments), default=1e9)
        if dmin > best_d:
            best_d, best = dmin, xy
    return annotate_box(ax, best, text, scale=scale, color=color,
                        facecolor=facecolor, fontsize=fontsize)


def draw_angle_arc(ax, vertex, p1, p2, scale=1.0,
                   radius_ratio=0.10, color='blue', label=None,
                   label_pad_ratio=0.045):
    radius = scale * radius_ratio
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
        r = radius + scale * label_pad_ratio
        art = ax.text(vertex[0] + r * np.cos(mid),
                      vertex[1] + r * np.sin(mid),
                      label, ha='center', va='center',
                      fontsize=10, color=color, bbox=_TEXT_BOX, zorder=6)
        _auto_register(art, kind='anglelabel', name=label)


def mark_equal_sides(ax, p1, p2, num_marks=1, scale=1.0,
                     tick_ratio=0.040, gap_ratio=0.025, color='red'):
    p1, p2 = np.asarray(p1, float), np.asarray(p2, float)
    mid = (p1 + p2) / 2
    d = p2 - p1
    L = np.hypot(*d)
    if L < 1e-9:
        return
    seg_len = L
    base_tick = scale * tick_ratio
    if num_marks >= 2:
        base_tick = scale * 0.030
    tick = min(base_tick, 0.12 * seg_len / 2)
    gap = scale * gap_ratio
    along = d / L
    perp = np.array([-d[1], d[0]]) / L
    for i in range(num_marks):
        offset = (i - (num_marks - 1) / 2) * gap
        c = mid + offset * along
        ax.plot([c[0] - tick * perp[0], c[0] + tick * perp[0]],
                [c[1] - tick * perp[1], c[1] + tick * perp[1]],
                color=color, linewidth=2, zorder=3)


def autoscale(ax, points, margin_ratio=0.12):
    pts = np.array(points)
    xr = pts[:, 0].max() - pts[:, 0].min()
    yr = pts[:, 1].max() - pts[:, 1].min()
    mx = max(xr, yr) * margin_ratio
    ax.set_xlim(pts[:, 0].min() - mx, pts[:, 0].max() + mx)
    ax.set_ylim(pts[:, 1].min() - mx, pts[:, 1].max() + mx)


# ========== 014题几何图形 ==========
# 等边三角形ABC
# 设BC水平，A在上方

# 基础坐标设定
side_len = 4
B = np.array([0, 0])
C = np.array([side_len, 0])
A = np.array([side_len / 2, side_len * np.sqrt(3) / 2])

# ========== Figure 1: 情况1 - D在AB上 ==========
fig, ax = plt.subplots(1, 1, figsize=(8, 8))
ax.set_aspect('equal')

# D点在AB上（靠近A的位置）
D1 = A + 0.4 * (B - A)  # D在AB上，距离A 40%

# 等边三角形EDC，以CD为边向上作（向上作意为E在上方，需要顺时针旋转-60°）
CD_vec = D1 - C
CD_len = np.linalg.norm(CD_vec)
CD_unit = CD_vec / CD_len

# 将CD顺时针旋转60°（即逆时针旋转-60°）得到CE方向，使E点向上
angle_60 = np.radians(-60)
rotation_matrix = np.array([[np.cos(angle_60), -np.sin(angle_60)],
                            [np.sin(angle_60), np.cos(angle_60)]])
CE_vec = rotation_matrix @ CD_vec
E1 = C + CE_vec

all_points_1 = [A, B, C, D1, E1]
autoscale(ax, all_points_1, margin_ratio=0.18)
L = compute_visual_scale(ax)

auditor = LayoutAuditor(ax, fig_name='step1_case1')
set_active_auditor(auditor)

# 绘制等边三角形ABC
auditor.add_segment(A, B, owner_points={'A', 'B'})
auditor.add_segment(B, C, owner_points={'B', 'C'})
auditor.add_segment(C, A, owner_points={'C', 'A'})
draw_triangle(ax, A, B, C, names=('A', 'B', 'C'))

# 绘制等边三角形EDC
auditor.add_segment(E1, D1, owner_points={'E', 'D'})
auditor.add_segment(D1, C, owner_points={'D', 'C'})
auditor.add_segment(C, E1, owner_points={'C', 'E'})
ax.plot([E1[0], D1[0]], [E1[1], D1[1]], 'purple', linewidth=2, zorder=3)
ax.plot([D1[0], C[0]], [D1[1], C[1]], 'purple', linewidth=2, zorder=3)
ax.plot([C[0], E1[0]], [C[1], E1[1]], 'purple', linewidth=2, zorder=3)

# 绘制AE
ax.plot([A[0], E1[0]], [A[1], E1[1]], 'green', linewidth=2.5, zorder=4)

# 绘制CD（高亮）
ax.plot([C[0], D1[0]], [C[1], D1[1]], 'orange', linewidth=2.5, linestyle='--', zorder=3)

# 标注点
label_point(ax, A, 'A', direction=(0, 1), scale=L, offset_ratio=0.07)
label_point(ax, B, 'B', direction=(-1, -0.3), scale=L, offset_ratio=0.06)
label_point(ax, C, 'C', direction=(1, -0.3), scale=L, offset_ratio=0.06)
label_point(ax, D1, 'D', direction=(-0.5, 0.8), scale=L, offset_ratio=0.06)
label_point(ax, E1, 'E', direction=(0.8, 0.6), scale=L, offset_ratio=0.07)

# 等边标记
mark_equal_sides(ax, A, B, num_marks=1, scale=L, color='red')
mark_equal_sides(ax, B, C, num_marks=1, scale=L, color='red')
mark_equal_sides(ax, C, A, num_marks=1, scale=L, color='red')
mark_equal_sides(ax, E1, D1, num_marks=1, scale=L, color='blue')
mark_equal_sides(ax, D1, C, num_marks=1, scale=L, color='blue')
mark_equal_sides(ax, C, E1, num_marks=1, scale=L, color='blue')

place_legend_auto(ax, '图1: D在AB上\n△DBC ≌ △EAC (SAS)',
                  segments=[(A,B),(B,C),(C,A),(E1,D1),(D1,C),(C,E1)], scale=L)

set_active_auditor(None)
violations = auditor.check()
if violations:
    print('[step1_case1] VIOLATIONS:')
    for w in violations:
        print('  -', w)

ax.set_title('014题 - 情况1', fontsize=14)
ax.axis('off')
plt.tight_layout()
plt.savefig(os.path.join(_BASE_DIR, 'step1_case1.png'), dpi=150, bbox_inches='tight')
plt.close()


# ========== Figure 2: 情况1 证明AE∥BC ==========
fig, ax = plt.subplots(1, 1, figsize=(8, 8))
ax.set_aspect('equal')

all_points_2 = [A, B, C, D1, E1]
autoscale(ax, all_points_2, margin_ratio=0.18)
L = compute_visual_scale(ax)

auditor = LayoutAuditor(ax, fig_name='step2_parallel')
set_active_auditor(auditor)

# 绘制等边三角形ABC（淡显）
ax.plot([A[0], B[0]], [A[1], B[1]], 'gray', linewidth=1.5, alpha=0.4, zorder=2)
ax.plot([B[0], C[0]], [B[1], C[1]], 'gray', linewidth=1.5, alpha=0.4, zorder=2)
ax.plot([C[0], A[0]], [C[1], A[1]], 'gray', linewidth=1.5, alpha=0.4, zorder=2)

# 绘制等边三角形EDC（淡显）
ax.plot([E1[0], D1[0]], [E1[1], D1[1]], 'gray', linewidth=1.5, alpha=0.4, zorder=2)
ax.plot([D1[0], C[0]], [D1[1], C[1]], 'gray', linewidth=1.5, alpha=0.4, zorder=2)
ax.plot([C[0], E1[0]], [C[1], E1[1]], 'gray', linewidth=1.5, alpha=0.4, zorder=2)

# 高亮AE
auditor.add_segment(A, E1, owner_points={'A', 'E'})
ax.plot([A[0], E1[0]], [A[1], E1[1]], 'green', linewidth=3, zorder=5)

# 高亮BC
auditor.add_segment(B, C, owner_points={'B', 'C'})
ax.plot([B[0], C[0]], [B[1], C[1]], 'blue', linewidth=3, zorder=5)

# 标注点
label_point(ax, A, 'A', direction=(0, 1), scale=L, offset_ratio=0.07)
label_point(ax, B, 'B', direction=(-1, -0.3), scale=L, offset_ratio=0.06)
label_point(ax, C, 'C', direction=(1, -0.3), scale=L, offset_ratio=0.06)
label_point(ax, D1, 'D', direction=(-0.5, 0.8), scale=L, offset_ratio=0.06)
label_point(ax, E1, 'E', direction=(0.8, 0.6), scale=L, offset_ratio=0.07)

# 角度标记 - ∠EAC
# ∠EAC = ∠EAB + ∠BAC，但更简单的是用平行线判定
draw_angle_arc(ax, A, E1, C, scale=L, radius_ratio=0.12, color='red', label='60°')

place_legend_auto(ax, 'AE ∥ BC 的证明\n∠EAC = ∠ACB = 60° (内错角)',
                  segments=[(A,E1),(B,C)], scale=L)

set_active_auditor(None)
violations = auditor.check()
if violations:
    print('[step2_parallel] VIOLATIONS:')
    for w in violations:
        print('  -', w)

ax.set_title('014题 - AE∥BC证明', fontsize=14)
ax.axis('off')
plt.tight_layout()
plt.savefig(os.path.join(_BASE_DIR, 'step2_parallel.png'), dpi=150, bbox_inches='tight')
plt.close()


# ========== Figure 3: 情况2 - D在BA延长线上 ==========
fig, ax = plt.subplots(1, 1, figsize=(8, 8))
ax.set_aspect('equal')

# D点在BA延长线上（A的上方）
D2 = A + 0.6 * (A - B)  # D在BA延长线上，距离A 60%

# 等边三角形EDC，以CD为边向上作（使用同样的顺时针旋转-60°）
CD2_vec = D2 - C
CE2_vec = rotation_matrix @ CD2_vec
E2 = C + CE2_vec

all_points_3 = [A, B, C, D2, E2]
autoscale(ax, all_points_3, margin_ratio=0.18)
L = compute_visual_scale(ax)

auditor = LayoutAuditor(ax, fig_name='step3_case2')
set_active_auditor(auditor)

# 绘制等边三角形ABC
auditor.add_segment(A, B, owner_points={'A', 'B'})
auditor.add_segment(B, C, owner_points={'B', 'C'})
auditor.add_segment(C, A, owner_points={'C', 'A'})
draw_triangle(ax, A, B, C, names=('A', 'B', 'C'))

# 绘制延长线BA
BA_ext = A + 1.5 * (A - B)
draw_aux_line(ax, B, BA_ext, owners={'B', 'A'}, color='gray', linestyle=':', alpha=0.5)

# 绘制等边三角形EDC
auditor.add_segment(E2, D2, owner_points={'E', 'D'})
auditor.add_segment(D2, C, owner_points={'D', 'C'})
auditor.add_segment(C, E2, owner_points={'C', 'E'})
ax.plot([E2[0], D2[0]], [E2[1], D2[1]], 'purple', linewidth=2, zorder=3)
ax.plot([D2[0], C[0]], [D2[1], C[1]], 'purple', linewidth=2, zorder=3)
ax.plot([C[0], E2[0]], [C[1], E2[1]], 'purple', linewidth=2, zorder=3)

# 绘制AE
ax.plot([A[0], E2[0]], [A[1], E2[1]], 'green', linewidth=2.5, zorder=4)

# 标注点
label_point(ax, A, 'A', direction=(0.5, 0.8), scale=L, offset_ratio=0.06)
label_point(ax, B, 'B', direction=(-1, -0.3), scale=L, offset_ratio=0.06)
label_point(ax, C, 'C', direction=(1, -0.3), scale=L, offset_ratio=0.06)
label_point(ax, D2, 'D', direction=(-0.3, 1), scale=L, offset_ratio=0.07)
label_point(ax, E2, 'E', direction=(1, 0.5), scale=L, offset_ratio=0.07)

# 等边标记
mark_equal_sides(ax, A, B, num_marks=1, scale=L, color='red')
mark_equal_sides(ax, B, C, num_marks=1, scale=L, color='red')
mark_equal_sides(ax, C, A, num_marks=1, scale=L, color='red')
mark_equal_sides(ax, E2, D2, num_marks=1, scale=L, color='blue')
mark_equal_sides(ax, D2, C, num_marks=1, scale=L, color='blue')
mark_equal_sides(ax, C, E2, num_marks=1, scale=L, color='blue')

place_legend_auto(ax, '图2: D在BA延长线上\n结论: AE ∥ BC 仍然成立',
                  segments=[(A,B),(B,C),(C,A),(E2,D2),(D2,C),(C,E2)], scale=L)

set_active_auditor(None)
violations = auditor.check()
if violations:
    print('[step3_case2] VIOLATIONS:')
    for w in violations:
        print('  -', w)

ax.set_title('014题 - 情况2', fontsize=14)
ax.axis('off')
plt.tight_layout()
plt.savefig(os.path.join(_BASE_DIR, 'step3_case2.png'), dpi=150, bbox_inches='tight')
plt.close()


# ========== Figure 4: 全等证明详解 ==========
fig, ax = plt.subplots(1, 1, figsize=(8, 8))
ax.set_aspect('equal')

all_points_4 = [A, B, C, D1, E1]
autoscale(ax, all_points_4, margin_ratio=0.18)
L = compute_visual_scale(ax)

auditor = LayoutAuditor(ax, fig_name='step4_congruent')
set_active_auditor(auditor)

# 绘制等边三角形ABC（淡显）
ax.plot([A[0], B[0]], [A[1], B[1]], 'gray', linewidth=1.5, alpha=0.4, zorder=2)
ax.plot([B[0], C[0]], [B[1], C[1]], 'gray', linewidth=1.5, alpha=0.4, zorder=2)
ax.plot([C[0], A[0]], [C[1], A[1]], 'gray', linewidth=1.5, alpha=0.4, zorder=2)

# 绘制等边三角形EDC（淡显）
ax.plot([E1[0], D1[0]], [E1[1], D1[1]], 'gray', linewidth=1.5, alpha=0.4, zorder=2)
ax.plot([D1[0], C[0]], [D1[1], C[1]], 'gray', linewidth=1.5, alpha=0.4, zorder=2)
ax.plot([C[0], E1[0]], [C[1], E1[1]], 'gray', linewidth=1.5, alpha=0.4, zorder=2)

# 高亮△DBC
auditor.add_segment(D1, B, owner_points={'D', 'B'})
auditor.add_segment(B, C, owner_points={'B', 'C'})
auditor.add_segment(C, D1, owner_points={'C', 'D'})
ax.plot([D1[0], B[0]], [D1[1], B[1]], 'red', linewidth=2.5, zorder=4)
ax.plot([B[0], C[0]], [B[1], C[1]], 'red', linewidth=2.5, zorder=4)
ax.plot([C[0], D1[0]], [C[1], D1[1]], 'red', linewidth=2.5, zorder=4)

# 高亮△EAC
auditor.add_segment(E1, A, owner_points={'E', 'A'})
auditor.add_segment(A, C, owner_points={'A', 'C'})
auditor.add_segment(C, E1, owner_points={'C', 'E'})
ax.plot([E1[0], A[0]], [E1[1], A[1]], 'blue', linewidth=2.5, zorder=4)
ax.plot([A[0], C[0]], [A[1], C[1]], 'blue', linewidth=2.5, zorder=4)
ax.plot([C[0], E1[0]], [C[1], E1[1]], 'blue', linewidth=2.5, zorder=4)

# 标注点
label_point(ax, A, 'A', direction=(0, 1), scale=L, offset_ratio=0.07)
label_point(ax, B, 'B', direction=(-1, -0.3), scale=L, offset_ratio=0.06)
label_point(ax, C, 'C', direction=(1, -0.3), scale=L, offset_ratio=0.06)
label_point(ax, D1, 'D', direction=(-0.5, 0.8), scale=L, offset_ratio=0.06)
label_point(ax, E1, 'E', direction=(0.8, 0.6), scale=L, offset_ratio=0.07)

place_legend_auto(ax, '△DBC ≌ △EAC (SAS)\nBC=AC, CD=CE, ∠BCD=∠ACE',
                  segments=[(D1,B),(B,C),(C,D1),(E1,A),(A,C),(C,E1)], scale=L)

set_active_auditor(None)
violations = auditor.check()
if violations:
    print('[step4_congruent] VIOLATIONS:')
    for w in violations:
        print('  -', w)

ax.set_title('014题 - 全等证明', fontsize=14)
ax.axis('off')
plt.tight_layout()
plt.savefig(os.path.join(_BASE_DIR, 'step4_congruent.png'), dpi=150, bbox_inches='tight')
plt.close()


print("All figures generated successfully!")
