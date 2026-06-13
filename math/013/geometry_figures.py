"""
Problem 013: 等腰直角三角形中BD=DP的证明

原图朝向：A在上方（直角顶点），B左下，C右下，
MN水平过A且平行于BC，D在MN左侧，P在AC边上。
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager

# ========== 中文字体加载（绝对路径）==========
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
    """L_ref = min(xrange, yrange)。"""
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    return min(abs(x1 - x0), abs(y1 - y0))


def _seg_point_distance(p, a, b):
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
    return not (r1[2] + pad < r2[0] or r2[2] + pad < r1[0] or
                r1[3] + pad < r2[1] or r2[3] + pad < r1[1])


def _seg_rect_distance(a, b, rect):
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
                      anchor_pt=None, owners=(), is_box=False, owner_seg=None,
                      is_leader=False):
        self.texts.append(dict(
            kind=kind, name=name, artist=artist,
            anchor=None if anchor is None else np.asarray(anchor, float),
            anchor_pt=None if anchor_pt is None else np.asarray(anchor_pt, float),
            owners=set(owners), is_box=is_box, is_leader=is_leader,
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
        return (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))

    def check(self):
        L = self.scale
        delta_safe = 0.025 * L
        v = []
        self.ax.figure.canvas.draw()

        # G0
        ax_texts = [t for t in self.ax.texts
                    if (t.get_text() or '').strip()
                    and (t.get_alpha() is None or t.get_alpha() > 0.05)]
        if len(ax_texts) > 0 and len(self.texts) == 0:
            v.append(
                f'G0 LayoutAuditor created AFTER drawing: ax has '
                f'{len(ax_texts)} text artists but auditor registered 0.')
            return v
        if len(ax_texts) > 0 and len(self.texts) < max(1, len(ax_texts) // 2):
            v.append(
                f'G0 partial registration: {len(ax_texts)} texts vs {len(self.texts)} registered.')

        # G1
        for H, size in self.right_angles:
            if size > 0.06 * L:
                v.append(f'G1 right_angle size={size:.3f} > 0.06*L_ref')
            for a, b, _ in self.segments:
                seg_len = float(np.linalg.norm(b - a))
                d = _seg_point_distance(H, a, b)
                if d < 0.5 * size and seg_len > 0 and size > 0.15 * seg_len:
                    v.append(f'G1 right_angle size={size:.3f} > 15% of seg len={seg_len:.3f}')

        rects = []
        for t in self.texts:
            try:
                rects.append(self._text_rect(t['artist']))
            except Exception:
                rects.append(None)

        # G6
        for t, r in zip(self.texts, rects):
            if r is None:
                continue
            for a, b, owners in self.segments:
                if t['owners'] & owners:
                    continue
                d = _seg_rect_distance(a, b, r)
                if d < delta_safe:
                    label = t['name'] or t['kind']
                    v.append(f'G6 text "{label}" overlaps segment {sorted(owners)}: d={d:.3f}')

        # G5b
        max_own = 0.12 * L
        for t, r in zip(self.texts, rects):
            if r is None or t.get('owner_seg') is None:
                continue
            a, b = t['owner_seg']
            d = _seg_rect_distance(a, b, r)
            if d > max_own:
                label = t['name'] or t['kind']
                v.append(f'G5b text "{label}" too far from its segment: d={d:.3f}')

        # G6b
        for i in range(len(self.texts)):
            for j in range(i + 1, len(self.texts)):
                ri, rj = rects[i], rects[j]
                if ri is None or rj is None:
                    continue
                if _rects_overlap(ri, rj, pad=0.3 * delta_safe):
                    ni = self.texts[i]['name'] or self.texts[i]['kind']
                    nj = self.texts[j]['name'] or self.texts[j]['kind']
                    v.append(f'G6b text "{ni}" and "{nj}" overlap')

        # G12
        for t, r in zip(self.texts, rects):
            if r is None or not t['is_box']:
                continue
            for a, b, owners in self.segments:
                d = _seg_rect_distance(a, b, r)
                if d < delta_safe:
                    label = t['name'] or 'box'
                    v.append(f'G12 box "{label}" overlaps geometry')

        # G7
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
                    v.append(f'G7 cluster "{n1}"/"{n2}" dirs not split cos={cos_a:.2f}')

        # G7b
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
                v.append(f'G7b extreme cluster "{n1}"/"{n2}" d={d_pp:.3f}')

        # G14
        for H, size in self.right_angles:
            rH = (H[0] - size, H[1] - size, H[0] + size, H[1] + size)
            for name, P in self.points.items():
                if float(np.linalg.norm(P - H)) < 0.5 * size:
                    continue
                if (rH[0] - delta_safe <= P[0] <= rH[2] + delta_safe and
                        rH[1] - delta_safe <= P[1] <= rH[3] + delta_safe):
                    v.append(f'G14 right-angle@{H.tolist()} near point "{name}"')

        # G4: 点标签到点心距离 ≤ 0.08·L_ref（G16 引线模式除外）
        max_pt_dist = 0.08 * L
        for t in self.texts:
            if t['kind'] != 'point':
                continue
            if t.get('is_leader'):
                continue
            if t.get('anchor_pt') is None or t.get('anchor') is None:
                continue
            d = float(np.linalg.norm(t['anchor'] - t['anchor_pt']))
            if d > max_pt_dist:
                label = t['name'] or 'point-label'
                v.append(
                    f'G4 point label "{label}" too far from its point: '
                    f'd={d:.3f} > 0.08·L_ref={max_pt_dist:.3f}. '
                    f'Use direction="auto" (G15) or leader=(lx,ly) (G16).')
        return v


_ACTIVE_AUDITOR = None


def set_active_auditor(auditor):
    global _ACTIVE_AUDITOR
    _ACTIVE_AUDITOR = auditor


def _auto_register(artist, kind='label', name='', anchor=None, anchor_pt=None,
                   owners=(), is_box=False, owner_seg=None, is_leader=False):
    if _ACTIVE_AUDITOR is not None:
        _ACTIVE_AUDITOR.register_text(artist, kind=kind, name=name,
                                      anchor=anchor, anchor_pt=anchor_pt,
                                      owners=owners, is_box=is_box,
                                      owner_seg=owner_seg, is_leader=is_leader)


# ========== G15 自适应方向选择 ==========
_G15_CANDIDATES = [(1, 0), (-1, 0), (0, 1), (0, -1),
                   (1, 1), (-1, 1), (1, -1), (-1, -1)]
_G15_OFFSETS = [0.055, 0.07, 0.08]
_G15_LABEL_W_RATIO = 0.06   # 估算 label 宽度 ≈ 0.06·L_ref
_G15_LABEL_H_RATIO = 0.04   # 估算 label 高度 ≈ 0.04·L_ref


def _auto_pick_direction(auditor, P, scale, owner_names=()):
    """G15：在 8 个候选方向中挑一个"远离已登记线段"且"不与邻近点标签同向"的方向。

    返回 (dx_unit, dy_unit, offset_ratio) 或 None（无合格候选，需走 G16 引线）。
    owner_names：当前点/标签关联的 owner，跳过这些线段再做 G6 判定。
    """
    P = np.asarray(P, float)
    delta_safe = 0.025 * scale
    cluster_thr = 0.15 * scale
    half_w = _G15_LABEL_W_RATIO * scale / 2
    half_h = _G15_LABEL_H_RATIO * scale / 2
    owners = set(owner_names)
    segs = auditor.segments if auditor is not None else []

    # 收集邻近点 (< 0.15·L_ref) 的标签方向，用于 G7 分散约束
    nearby_dirs = []
    if auditor is not None:
        for name, Pt in auditor.points.items():
            d_pp = float(np.linalg.norm(P - Pt))
            if d_pp >= cluster_thr or d_pp < 1e-9:
                continue
            t = next((tt for tt in auditor.texts
                      if tt['kind'] == 'point' and tt['name'] == name
                      and tt.get('anchor') is not None), None)
            if t is None:
                continue
            anchor_dir = t['anchor'] - Pt
            n = float(np.linalg.norm(anchor_dir))
            if n > 1e-9:
                nearby_dirs.append(anchor_dir / n)

    for offset in _G15_OFFSETS:
        best = None
        best_min_d = -1.0
        for dx, dy in _G15_CANDIDATES:
            d_unit = np.array([dx, dy], dtype=float)
            d_unit = d_unit / (np.linalg.norm(d_unit) + 1e-9)
            anchor = P + d_unit * (scale * offset)
            rect = (anchor[0] - half_w, anchor[1] - half_h,
                    anchor[0] + half_w, anchor[1] + half_h)
            # G6：到非自身线段最小距离
            min_d = float('inf')
            for a, b, seg_owners in segs:
                if seg_owners & owners:
                    continue
                d_seg = _seg_rect_distance(a, b, rect)
                if d_seg < min_d:
                    min_d = d_seg
            if min_d < delta_safe:
                continue
            # G7：与所有邻近点标签方向夹角必须 ≥ 90°
            g7_ok = True
            for nd in nearby_dirs:
                cos_a = float(d_unit @ nd)
                if cos_a > 1e-3:
                    g7_ok = False
                    break
            if not g7_ok:
                continue
            if min_d > best_min_d:
                best_min_d = min_d
                best = (float(d_unit[0]), float(d_unit[1]), offset)
        if best is not None:
            return best
    return None


# ========== 可复用工具函数 ==========
def draw_triangle(ax, A, B, C, color='black', linewidth=1.8, alpha=1.0,
                  names=None):
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


def label_point(ax, P, name, direction='auto', scale=1.0,
                offset_ratio=0.055, fontsize=13, color='black',
                marker_zorder=5, text_zorder=6, owners=None, leader=None):
    """G15/G16 入口：点标签放置。

    - direction='auto'（默认）：走 G15 自适应方向搜索
    - direction=(dx, dy)：手动指定方向（dx, dy 会被归一化）
    - leader=(lx, ly)：走 G16 引线模式，标签放在 (lx, ly)，从 P 画引线连回
    """
    if offset_ratio > 0.08 + 1e-9:
        raise ValueError(
            f'offset_ratio={offset_ratio:.3f} > G4 max 0.08·L_ref. '
            f'Use direction="auto" (G15) or leader=(lx,ly) (G16).')
    P = np.asarray(P, float)
    is_leader = leader is not None
    if is_leader:
        leader_pt = np.asarray(leader, float)
        # 画引线 P → leader_pt（虚线：callout 标准视觉）
        ax.plot([P[0], leader_pt[0]], [P[1], leader_pt[1]],
                color='#666666', linewidth=0.6, linestyle=':', zorder=4, alpha=0.7)
        if _ACTIVE_AUDITOR is not None:
            _ACTIVE_AUDITOR.add_segment(P, leader_pt, owner_points={name})
        anchor = leader_pt
        offset_ratio = 1.0  # G16 模式不再受 G4 距离上限约束
    else:
        if isinstance(direction, str) and direction == 'auto':
            result = _auto_pick_direction(_ACTIVE_AUDITOR, P, scale,
                                          owner_names=owners or {name})
            if result is not None:
                dx, dy, offset_ratio = result
                direction = (dx, dy)
            else:
                # G15 全失败：回退 (0, 1)，由 auditor 报 G4/G6 让 dev 改用 G16
                direction = (0.0, 1.0)
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
                       anchor_pt=P,
                       owners=(owners if owners is not None else {name}),
                       is_leader=is_leader)
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
                      facecolor='#e3f2fd', fontsize=11):
    candidates = [
        ('top-left', lambda xr, yr: (xr[0] + 0.08 * scale, yr[1] - 0.10 * scale)),
        ('top-right', lambda xr, yr: (xr[1] - 0.08 * scale, yr[1] - 0.10 * scale)),
        ('bottom-left', lambda xr, yr: (xr[0] + 0.08 * scale, yr[0] + 0.08 * scale)),
        ('bottom-right', lambda xr, yr: (xr[1] - 0.08 * scale, yr[0] + 0.08 * scale)),
    ]
    xr = (ax.get_xlim()[0], ax.get_xlim()[1])
    yr = (ax.get_ylim()[0], ax.get_ylim()[1])
    best_pos = None
    best_min_d = -1
    for _, fn in candidates:
        pos = fn(xr, yr)
        min_d = float('inf')
        for seg in segments:
            d = _seg_rect_distance(seg[0], seg[1],
                                   (pos[0] - 0.15 * scale, pos[1] - 0.06 * scale,
                                    pos[0] + 0.15 * scale, pos[1] + 0.06 * scale))
            min_d = min(min_d, d)
        if min_d > best_min_d:
            best_min_d = min_d
            best_pos = pos
    return annotate_box(ax, best_pos, text, scale=scale, color=color,
                        facecolor=facecolor, fontsize=fontsize)


def draw_right_angle(ax, vertex, dir1, dir2, scale=1.0,
                     size_ratio=0.045, color='black', linewidth=1.0):
    size = size_ratio * scale
    d1 = np.asarray(dir1, dtype=float)
    d2 = np.asarray(dir2, dtype=float)
    d1 = d1 / (np.linalg.norm(d1) + 1e-9) * size
    d2 = d2 / (np.linalg.norm(d2) + 1e-9) * size
    p1 = np.array([vertex[0] + d1[0], vertex[1] + d1[1]])
    p2 = np.array([vertex[0] + d1[0] + d2[0], vertex[1] + d1[1] + d2[1]])
    p3 = np.array([vertex[0] + d2[0], vertex[1] + d2[1]])
    ax.plot([p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]],
            color=color, linewidth=linewidth, zorder=3)
    if _ACTIVE_AUDITOR is not None:
        _ACTIVE_AUDITOR.add_right_angle(vertex, size)
    return size


def draw_angle_arc(ax, center, p1, p2, radius, color='red',
                   label=None, fontsize=10):
    angle1 = np.degrees(np.arctan2(p1[1] - center[1], p1[0] - center[0]))
    angle2 = np.degrees(np.arctan2(p2[1] - center[1], p2[0] - center[0]))
    if angle2 < angle1:
        angle1, angle2 = angle2, angle1
    if angle2 - angle1 > 180:
        angle1, angle2 = angle2, angle1 + 360
    arc = patches.Arc(center, 2 * radius, 2 * radius, angle=0,
                      theta1=angle1, theta2=angle2, color=color,
                      linewidth=1.5, zorder=3)
    ax.add_patch(arc)
    if label:
        mid_rad = np.radians((angle1 + angle2) / 2)
        lx = center[0] + (radius + 0.045 * compute_visual_scale(ax)) * np.cos(mid_rad)
        ly = center[1] + (radius + 0.045 * compute_visual_scale(ax)) * np.sin(mid_rad)
        art = ax.text(lx, ly, label, ha='center', va='center',
                      fontsize=fontsize, fontweight='bold', color=color,
                      bbox=_TEXT_BOX, zorder=6)
        _auto_register(art, kind='angle_label', name=label)
    return arc


# ========== 坐标定义（匹配原图图1朝向）==========
# A 在上方（直角顶点），B 左下，C 右下
A = np.array([0.0, 3.0])
B = np.array([-3.0, 0.0])
C = np.array([3.0, 0.0])
# MN 水平过 A，平行于 BC；D 在 MN 上 A 的左侧
D = np.array([-1.5, 3.0])
# MN 左右端点（用于画线）
M = np.array([-3.0, 3.0])
N = np.array([3.5, 3.0])

# P = DE 与 AC 的交点（DE 垂直于 DB）
# DB 向量 = B - D = (-1.5, -3)，垂直方向为 (2, -1) 或归一化
# 直线 DE: D + t*(2, -1)；直线 AC: A + s*(3, -3) 即 (3s, 3-3s)
# 解得 s=0.5, t=1.5
P = np.array([1.5, 1.5])

# E 在 DE 延长线上（取 t=3 使 E 靠近 BC 右侧）
E = np.array([4.5, 0.0])

# 辅助点：F 为 D 到 AB 的垂足，G 为 D 到 AC 的垂足
# AB: y = x + 3；AC: y = -x + 3
F = np.array([-0.75, 2.25])   # DF 垂足于 AB
G = np.array([-0.75, 3.75])   # DG 垂足于 AC 延长线


# ========== 辅助函数：自动设置坐标范围 ==========
def autoscale(ax, key_points, margin=0.22):
    pts = np.array(key_points)
    xmin, ymin = pts.min(axis=0)
    xmax, ymax = pts.max(axis=0)
    dx = xmax - xmin
    dy = ymax - ymin
    ax.set_xlim(xmin - margin * dx, xmax + margin * dy)
    ax.set_ylim(ymin - margin * dy, ymax + margin * dy)
    ax.set_aspect('equal')


# ============================================================
# Step 0: 重绘原题示意图（图1）
# ============================================================
fig, ax = plt.subplots(figsize=(8, 7))
ax.set_axis_off()

key_pts_0 = [A, B, C, D, M, N, P, E]
autoscale(ax, key_pts_0, margin=0.20)
L = compute_visual_scale(ax)
auditor = LayoutAuditor(ax, 'step0')
set_active_auditor(auditor)

# 三角形 ABC
draw_triangle(ax, A, B, C, names=('A', 'B', 'C'))

# MN 直线（平行于 BC，过 A），A、D 在 MN 上
draw_aux_line(ax, M, N, owners=('M', 'N', 'A', 'D'), color='#555555', linewidth=1.2, linestyle='-')

# 线段 BD、DE、DP
draw_aux_line(ax, B, D, owners=('B', 'D'), color='#2563eb', linewidth=2.0, linestyle='-')
draw_aux_line(ax, D, E, owners=('D', 'E', 'P'), color='#2563eb', linewidth=2.0, linestyle='-')
# P 在 AC 上且在 DE 上
draw_aux_line(ax, D, P, owners=('D', 'P'), color='#dc2626', linewidth=2.0, linestyle='-')

# 直角符号 ∠BAC = 90°
draw_right_angle(ax, A, B - A, C - A, scale=L, size_ratio=0.032, color='black')

# 直角符号 ∠BDE = 90°
dir_DB = (B - D) / np.linalg.norm(B - D)
dir_DE = (E - D) / np.linalg.norm(E - D)
draw_right_angle(ax, D, dir_DB, dir_DE, scale=L, size_ratio=0.032, color='#2563eb')

# 标注所有点
label_point(ax, A, 'A', direction=(0, 1), scale=L, offset_ratio=0.055)
label_point(ax, B, 'B', direction=(-1, -1), scale=L, offset_ratio=0.055)
label_point(ax, C, 'C', direction=(1, -1), scale=L, offset_ratio=0.055)
label_point(ax, D, 'D', direction=(-1, 0.8), scale=L, offset_ratio=0.06)
label_point(ax, M, 'M', direction=(-1, 0.5), scale=L, offset_ratio=0.04)
label_point(ax, N, 'N', direction=(1, 0.5), scale=L, offset_ratio=0.04)
# P 在 AC 上，标签方向避开 AC 和 DE
label_point(ax, P, 'P', direction=(1, 1), scale=L, offset_ratio=0.06,
            owners={'P', 'A', 'C'})
label_point(ax, E, 'E', direction=(1, -0.8), scale=L, offset_ratio=0.055)

# 平行标记 MN // BC（放在上方空白区）
art_mn = ax.text(0.3, 4.2, 'MN', color='#555555', ha='center', va='center',
                 fontsize=11, fontweight='bold', bbox=_TEXT_BOX, zorder=6)
_auto_register(art_mn, kind='seglabel', name='MN',
               owners={'M', 'N', 'A', 'D'})

set_active_auditor(None)
violations = auditor.check()
assert not violations, f'step0 layout VIOLATIONS: {violations}'
plt.savefig(os.path.join(_BASE_DIR, 'step0_original.png'), dpi=150, bbox_inches='tight', facecolor='white')
plt.close()


# ============================================================
# Step 1: 作辅助线 DF⊥AB, DG⊥AC，证明 AFDG 是正方形
# ============================================================
fig, ax = plt.subplots(figsize=(8, 7))
ax.set_axis_off()

key_pts_1 = [A, B, C, D, M, N, P, E, F, G]
autoscale(ax, key_pts_1, margin=0.22)
L = compute_visual_scale(ax)
auditor = LayoutAuditor(ax, 'step1')
set_active_auditor(auditor)

# 基础图形淡显
draw_triangle(ax, A, B, C, color='#999999', linewidth=1.2, alpha=0.35, names=('A','B','C'))
draw_aux_line(ax, M, N, owners=('M','N','A','D'), color='#999999', linewidth=1.0, linestyle='-', alpha=0.35)
draw_aux_line(ax, B, D, owners=('B','D'), color='#999999', linewidth=1.2, alpha=0.35)
draw_aux_line(ax, D, E, owners=('D','E','P'), color='#999999', linewidth=1.2, alpha=0.35)
draw_aux_line(ax, D, P, owners=('D','P'), color='#999999', linewidth=1.2, alpha=0.35)

# 高亮辅助线 DF 和 DG（DG 用不同颜色区分）
draw_aux_line(ax, D, F, owners=('D', 'F'), color='#e11d48', linewidth=2.2, linestyle='-')
draw_aux_line(ax, D, G, owners=('D', 'G'), color='#2563eb', linewidth=2.2, linestyle='-')

# 正方形 AFDG 边框（高亮，DG 边用蓝色）
ax.plot([A[0], F[0], D[0]], [A[1], F[1], D[1]],
        color='#e11d48', linewidth=1.5, linestyle='--', zorder=3, alpha=0.7)
ax.plot([D[0], G[0], A[0]], [D[1], G[1], A[1]],
        color='#2563eb', linewidth=1.5, linestyle='--', zorder=3, alpha=0.7)
if _ACTIVE_AUDITOR:
    _ACTIVE_AUDITOR.add_segment(A, F, owner_points={'A', 'F'})
    _ACTIVE_AUDITOR.add_segment(F, D, owner_points={'F', 'D'})
    _ACTIVE_AUDITOR.add_segment(D, G, owner_points={'D', 'G'})
    _ACTIVE_AUDITOR.add_segment(G, A, owner_points={'G', 'A'})

# 直角符号：DF⊥AB（缩短的直角边约1.06，size受15%约束）
dir_FD = (D - F) / np.linalg.norm(D - F)
dir_FB = (B - F) / np.linalg.norm(B - F)
draw_right_angle(ax, F, dir_FD, dir_FB, scale=L, size_ratio=0.028, color='#e11d48', linewidth=2.0)

# 直角符号：DG⊥AC
dir_GD = (D - G) / np.linalg.norm(D - G)
dir_GC = (C - G) / np.linalg.norm(C - G)
draw_right_angle(ax, G, dir_GD, dir_GC, scale=L, size_ratio=0.028, color='#2563eb', linewidth=2.0)

# 标注关键点（当前步骤相关的高亮）
label_point(ax, A, 'A', direction=(0, 1), scale=L, offset_ratio=0.055)
label_point(ax, D, 'D', direction=(-1, 0.8), scale=L, offset_ratio=0.06)
label_point(ax, F, 'F', direction=(-1, -0.8), scale=L, offset_ratio=0.06,
            owners={'F', 'A', 'B'})
label_point(ax, G, 'G', direction=(-1, 1), scale=L, offset_ratio=0.06)

# 淡显其他点
label_point(ax, B, 'B', direction=(-1, -1), scale=L, offset_ratio=0.05, color='#888888')
label_point(ax, C, 'C', direction=(1, -1), scale=L, offset_ratio=0.05, color='#888888')
label_point(ax, P, 'P', direction=(1, 1), scale=L, offset_ratio=0.06,
            color='#888888', owners={'P', 'A', 'C'})
label_point(ax, E, 'E', direction=(1, -0.8), scale=L, offset_ratio=0.05, color='#888888')
label_point(ax, M, 'M', direction=(-1, 0.5), scale=L, offset_ratio=0.04, color='#888888')
label_point(ax, N, 'N', direction=(1, 0.5), scale=L, offset_ratio=0.04, color='#888888')

# 说明框：正方形性质
segments_for_legend = [(A, B), (B, C), (C, A), (M, N), (D, F), (D, G),
                       (A, F), (F, D), (D, G), (G, A), (B, D), (D, E), (D, P)]
place_legend_auto(ax, '因为 MN//BC，所以 D 到 AB 和 AC 距离相等\n即 DF = DG\n又 AFDG 有三个直角，故为正方形',
                 segments_for_legend, scale=L, color='#be185d', facecolor='#fce7f3', fontsize=11)

set_active_auditor(None)
violations = auditor.check()
assert not violations, f'step1 layout VIOLATIONS: {violations}'
plt.savefig(os.path.join(_BASE_DIR, 'step1_auxiliary.png'), dpi=150, bbox_inches='tight', facecolor='white')
plt.close()


# ============================================================
# Step 2: 角度关系与全等三角形
# ============================================================
fig, ax = plt.subplots(figsize=(8, 7))
ax.set_axis_off()

key_pts_2 = [A, B, C, D, M, N, P, E, F, G]
autoscale(ax, key_pts_2, margin=0.22)
L = compute_visual_scale(ax)
auditor = LayoutAuditor(ax, 'step2')
set_active_auditor(auditor)

# 基础图形淡显
draw_triangle(ax, A, B, C, color='#999999', linewidth=1.2, alpha=0.35, names=('A','B','C'))
draw_aux_line(ax, M, N, owners=('M','N','A','D'), color='#999999', linewidth=1.0, linestyle='-', alpha=0.35)
draw_aux_line(ax, D, E, owners=('D','E','P'), color='#999999', linewidth=1.2, alpha=0.35)

# 高亮两个全等三角形的边
# ΔBDF
draw_aux_line(ax, B, D, owners=('B','D'), color='#2563eb', linewidth=2.2, linestyle='-')
draw_aux_line(ax, B, F, owners=('B','F'), color='#2563eb', linewidth=2.2, linestyle='-')
draw_aux_line(ax, D, F, owners=('D','F'), color='#2563eb', linewidth=2.2, linestyle='-')

# ΔPDG
draw_aux_line(ax, P, D, owners=('P','D'), color='#16a34a', linewidth=2.2, linestyle='-')
draw_aux_line(ax, P, G, owners=('P','G'), color='#16a34a', linewidth=2.2, linestyle='-')
draw_aux_line(ax, D, G, owners=('D','G'), color='#16a34a', linewidth=2.2, linestyle='-')

# 直角符号（缩小尺寸）
dir_FD = (D - F) / np.linalg.norm(D - F)
dir_FB = (B - F) / np.linalg.norm(B - F)
draw_right_angle(ax, F, dir_FD, dir_FB, scale=L, size_ratio=0.028, color='#2563eb')

dir_GD = (D - G) / np.linalg.norm(D - G)
dir_GP = (P - G) / np.linalg.norm(P - G)
draw_right_angle(ax, G, dir_GD, dir_GP, scale=L, size_ratio=0.028, color='#16a34a')

# 标注关键点
label_point(ax, B, 'B', direction=(-1, -1), scale=L, offset_ratio=0.055)
label_point(ax, D, 'D', direction=(-1, 0.8), scale=L, offset_ratio=0.06)
label_point(ax, F, 'F', direction=(-1, -0.8), scale=L, offset_ratio=0.06,
            owners={'F', 'A', 'B'})
label_point(ax, P, 'P', direction=(1, 1), scale=L, offset_ratio=0.06,
            owners={'P', 'A', 'C'})
label_point(ax, G, 'G', direction=(-1, 1), scale=L, offset_ratio=0.06)

# 淡显其他点
label_point(ax, A, 'A', direction=(0, 1), scale=L, offset_ratio=0.055,
            color='#888888', owners={'A', 'G', 'P'})
label_point(ax, C, 'C', direction=(1, -1), scale=L, offset_ratio=0.05, color='#888888')
label_point(ax, E, 'E', direction=(1, -0.8), scale=L, offset_ratio=0.05, color='#888888')
label_point(ax, M, 'M', direction=(-1, 0.5), scale=L, offset_ratio=0.04, color='#888888')
label_point(ax, N, 'N', direction=(1, 0.5), scale=L, offset_ratio=0.04, color='#888888')

# 角弧：∠BDF = ∠PDG
arc_r1 = 0.10 * L
# ∠BDF: 顶点 D，边 DB 和 DF
draw_angle_arc(ax, D, B, F, arc_r1, color='#2563eb')
# ∠PDG: 顶点 D，边 DP 和 DG
draw_angle_arc(ax, D, P, G, arc_r1 + 0.05 * L, color='#16a34a')

# 说明框
segments_for_legend2 = [(A,B),(B,C),(C,A),(M,N),(B,D),(D,E),(D,P),
                         (B,F),(D,F),(P,D),(P,G),(D,G)]
place_legend_auto(ax, '由 ∠BDE=90° 且 ∠FDG=90°\n得 ∠BDF = ∠PDG\n'
                 '又 ∠BFD = ∠PGD = 90°，DF = DG\n故 △BDF ≌ △PDG (ASA)',
                 segments_for_legend2, scale=L, color='#1d4ed8', facecolor='#dbeafe', fontsize=11)

set_active_auditor(None)
violations = auditor.check()
assert not violations, f'step2 layout VIOLATIONS: {violations}'
plt.savefig(os.path.join(_BASE_DIR, 'step2_congruence.png'), dpi=150, bbox_inches='tight', facecolor='white')
plt.close()


# ============================================================
# Step 3: 结论 —— BD = DP
# ============================================================
fig, ax = plt.subplots(figsize=(8, 7))
ax.set_axis_off()

key_pts_3 = [A, B, C, D, M, N, P, E, F, G]
autoscale(ax, key_pts_3, margin=0.20)
L = compute_visual_scale(ax)
auditor = LayoutAuditor(ax, 'step3')
set_active_auditor(auditor)

# 完整图形
draw_triangle(ax, A, B, C, names=('A', 'B', 'C'))
draw_aux_line(ax, M, N, owners=('M', 'N', 'A', 'D'), color='#555555', linewidth=1.2, linestyle='-')

# 高亮 BD 和 DP（结论中的等长线段）
draw_aux_line(ax, B, D, owners=('B', 'D'), color='#dc2626', linewidth=3.0, linestyle='-')
draw_aux_line(ax, D, P, owners=('D', 'P'), color='#dc2626', linewidth=3.0, linestyle='-')

# 其余线条淡显
draw_aux_line(ax, D, E, owners=('D', 'E', 'P'), color='#999999', linewidth=1.2, alpha=0.35)

# 直角符号
dir_DB = (B - D) / np.linalg.norm(B - D)
dir_DE = (E - D) / np.linalg.norm(E - D)
draw_right_angle(ax, D, dir_DB, dir_DE, scale=L, size_ratio=0.03, color='#666666')
draw_right_angle(ax, A, B - A, C - A, scale=L, size_ratio=0.03, color='#666666')

# 等长 tick 标记
tick_len = 0.040 * L
mid_BD = (B + D) / 2
dir_BD = D - B
dir_BD_perp = np.array([-dir_BD[1], dir_BD[0]]) / np.linalg.norm(dir_BD)
tick1_p1 = mid_BD - dir_BD_perp * tick_len / 2
tick1_p2 = mid_BD + dir_BD_perp * tick_len / 2
ax.plot([tick1_p1[0], tick1_p2[0]], [tick1_p1[1], tick1_p2[1]],
        color='#dc2626', linewidth=2.5, zorder=5)

mid_DP = (D + P) / 2
dir_DP = P - D
dir_DP_perp = np.array([-dir_DP[1], dir_DP[0]]) / np.linalg.norm(dir_DP)
tick2_p1 = mid_DP - dir_DP_perp * tick_len / 2
tick2_p2 = mid_DP + dir_DP_perp * tick_len / 2
ax.plot([tick2_p1[0], tick2_p2[0]], [tick2_p1[1], tick2_p2[1]],
        color='#dc2626', linewidth=2.5, zorder=5)

# 三角形 △BDF 和 △PDG 的剩余边（BD、DP 已高亮，补画 DF、BF、DG、PG）
draw_aux_line(ax, D, F, owners=('D', 'F'), color='#2563eb', linewidth=1.5, linestyle='--', alpha=0.8)
draw_aux_line(ax, B, F, owners=('B', 'F'), color='#2563eb', linewidth=1.5, linestyle='--', alpha=0.8)
draw_aux_line(ax, D, G, owners=('D', 'G'), color='#16a34a', linewidth=1.5, linestyle='--', alpha=0.8)
draw_aux_line(ax, P, G, owners=('P', 'G', 'A'), color='#16a34a', linewidth=1.5, linestyle='--', alpha=0.8)

# 三角形名称标签
centroid_BDF = (B + D + F) / 3
art_bdf = ax.text(centroid_BDF[0], centroid_BDF[1], '△BDF',
                  ha='center', va='center', fontsize=11, fontweight='bold',
                  color='#2563eb', bbox=_TEXT_BOX, zorder=6)
_auto_register(art_bdf, kind='seglabel', name='△BDF',
               owners={'B', 'D', 'F'})

centroid_PDG = (P + D + G) / 3
# △PDG 标签放在三角形 ABC 内部偏右区域，避让 AB、AC
art_pdg = ax.text(1.5, 2.2, '△PDG',
                  ha='center', va='center', fontsize=11, fontweight='bold',
                  color='#16a34a', bbox=_TEXT_BOX, zorder=6)
_auto_register(art_pdg, kind='seglabel', name='△PDG',
               owners={'P', 'D', 'G'})

# 标注所有点
label_point(ax, A, 'A', direction=(0, 1), scale=L, offset_ratio=0.055)
label_point(ax, B, 'B', direction=(-1, -1), scale=L, offset_ratio=0.055)
label_point(ax, C, 'C', direction=(1, -1), scale=L, offset_ratio=0.055)
label_point(ax, D, 'D', direction=(-1, 0.8), scale=L, offset_ratio=0.06)
label_point(ax, M, 'M', direction=(-1, 0.5), scale=L, offset_ratio=0.04)
label_point(ax, N, 'N', direction=(1, 0.8), scale=L, offset_ratio=0.05)
label_point(ax, P, 'P', direction=(1, 1), scale=L, offset_ratio=0.06,
            owners={'P', 'A', 'C'})
label_point(ax, E, 'E', direction=(1, -0.8), scale=L, offset_ratio=0.05,
            color='#888888')
# F 标签：走 G15 自适应方向（裸 ax.text 改写为 label_point）
label_point(ax, F, 'F', direction='auto', scale=L, offset_ratio=0.06,
            color='#2563eb', owners={'B', 'F', 'D'})
# G 标签：走 G15 自适应方向
label_point(ax, G, 'G', direction='auto', scale=L, offset_ratio=0.06,
            color='#16a34a', owners={'D', 'G'})

# 最终答案框（手动放在右下空白区，避开 MN 和所有几何对象）
annotate_box(ax, (3.5, -1.5), '由 △BDF ≌ △PDG (ASA)\n得对应边相等：BD = DP',
             scale=L, color='#dc2626', facecolor='#fee2e2', fontsize=12)

set_active_auditor(None)
violations = auditor.check()
assert not violations, f'step3 layout VIOLATIONS: {violations}'
plt.savefig(os.path.join(_BASE_DIR, 'step3_result.png'), dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

# ============================================================
# Case 2: 点 P 在 CA 的延长线上（图2）
# D 在 MN 上 A 的左侧，P 在 CA 延长线上（A 的上方）
# D = (-3,3) 使得 DB 竖直，△BDF 与 △PDG 完美全等（镜像对称）
# ============================================================
D2 = np.array([-3.0, 3.0])
# P2 = DB 与 AC 的交点（在 CA 延长线上）
# DB 为竖直线 x=-3, AC: y=-x+3 → P = (-3, 6)
P2 = np.array([-3.0, 6.0])
# E2 在 DE 上，DE ⟂ DB；DB 竖直故 DE 水平
E2 = np.array([3.0, 3.0])
# 辅助点 F2 (D 到 AB 垂足), G2 (D 到 AC 垂足)
F2 = np.array([-1.5, 1.5])
G2 = np.array([-1.5, 4.5])
# Case 2 专用的 MN 左端点（在 D2 左侧，避免标签与 D2 重叠）
M2 = np.array([-4.5, 3.0])


# ============================================================
# Step 4: Case 2 原题图（P 在 CA 延长线上）
# ============================================================
fig, ax = plt.subplots(figsize=(8, 7))
ax.set_axis_off()

key_pts_c2 = [A, B, C, D2, M2, N, P2, E2]
autoscale(ax, key_pts_c2, margin=0.22)
L = compute_visual_scale(ax)
auditor = LayoutAuditor(ax, 'step4_case2')
set_active_auditor(auditor)

draw_triangle(ax, A, B, C, names=('A', 'B', 'C'))
draw_aux_line(ax, M2, N, owners=('M', 'N', 'A', 'D'), color='#555555', linewidth=1.2, linestyle='-')

# DB, DE, DP
draw_aux_line(ax, B, D2, owners=('B', 'D'), color='#2563eb', linewidth=2.0, linestyle='-')
draw_aux_line(ax, D2, E2, owners=('D', 'E', 'P'), color='#2563eb', linewidth=2.0, linestyle='-')
draw_aux_line(ax, D2, P2, owners=('D', 'P'), color='#dc2626', linewidth=2.0, linestyle='-')

# 直角符号
draw_right_angle(ax, A, B - A, C - A, scale=L, size_ratio=0.032, color='black')
dir_DB2 = (B - D2) / np.linalg.norm(B - D2)
dir_DE2 = (E2 - D2) / np.linalg.norm(E2 - D2)
draw_right_angle(ax, D2, dir_DB2, dir_DE2, scale=L, size_ratio=0.032, color='#2563eb')

# 标注
label_point(ax, A, 'A', direction=(0, 1), scale=L, offset_ratio=0.055)
label_point(ax, B, 'B', direction=(-1, -1), scale=L, offset_ratio=0.055)
label_point(ax, C, 'C', direction=(1, -1), scale=L, offset_ratio=0.055)
label_point(ax, D2, 'D', direction=(-1, 0.8), scale=L, offset_ratio=0.06)
label_point(ax, M2, 'M', direction=(-1, -0.5), scale=L, offset_ratio=0.04)
label_point(ax, N, 'N', direction=(0.5, 1), scale=L, offset_ratio=0.04)
label_point(ax, P2, 'P', direction=(-1, 1), scale=L, offset_ratio=0.06)
label_point(ax, E2, 'E', direction=(1, -1), scale=L, offset_ratio=0.07)

# 标注虚线延长
ax.plot([A[0], P2[0]], [A[1], P2[1]], color='#999999', linewidth=1.0, linestyle='--', zorder=2)
if _ACTIVE_AUDITOR:
    _ACTIVE_AUDITOR.add_segment(A, P2, owner_points={'A', 'P'})

# 说明框（放在右上空白区）
annotate_box(ax, (3.5, 5.5), '情形2: P 在 CA 延长线上',
             scale=L, color='#7c3aed', facecolor='#ede9fe', fontsize=12)

set_active_auditor(None)
violations = auditor.check()
assert not violations, f'step4_case2 layout VIOLATIONS: {violations}'
plt.savefig(os.path.join(_BASE_DIR, 'step4_case2_config.png'), dpi=150, bbox_inches='tight', facecolor='white')
plt.close()


# ============================================================
# Step 5: Case 2 证明（作辅助线，全等三角形）
# ============================================================
fig, ax = plt.subplots(figsize=(8, 7))
ax.set_axis_off()

key_pts_c2p = [A, B, C, D2, M2, N, P2, E2, F2, G2]
autoscale(ax, key_pts_c2p, margin=0.22)
L = compute_visual_scale(ax)
auditor = LayoutAuditor(ax, 'step5_case2_proof')
set_active_auditor(auditor)

# 基础图形淡显
draw_triangle(ax, A, B, C, color='#999999', linewidth=1.2, alpha=0.30, names=('A','B','C'))
draw_aux_line(ax, M2, N, owners=('M','N','A','D'), color='#999999', linewidth=1.0, linestyle='-', alpha=0.30)
draw_aux_line(ax, D2, E2, owners=('D','E','P'), color='#999999', linewidth=1.2, alpha=0.30)
# 灰色虚线连接 AG（显示 D 到 AC 垂足 G 与 A 的关系）
draw_aux_line(ax, A, G2, owners=('A','G','D'), color='#999999', linewidth=1.2, linestyle='--', alpha=0.50)

# 高亮 △BDF 与 △PDG
# △BDF
draw_aux_line(ax, B, D2, owners=('B','D'), color='#2563eb', linewidth=2.2, linestyle='-')
draw_aux_line(ax, B, F2, owners=('B','F'), color='#2563eb', linewidth=2.2, linestyle='-')
draw_aux_line(ax, D2, F2, owners=('D','F'), color='#2563eb', linewidth=2.2, linestyle='-')

# △PDG
draw_aux_line(ax, P2, D2, owners=('P','D'), color='#16a34a', linewidth=2.2, linestyle='-')
draw_aux_line(ax, P2, G2, owners=('P','G'), color='#16a34a', linewidth=2.2, linestyle='-')
draw_aux_line(ax, D2, G2, owners=('D','G'), color='#16a34a', linewidth=2.2, linestyle='-')

# 直角符号
dir_F2D = (D2 - F2) / np.linalg.norm(D2 - F2)
dir_F2B = (B - F2) / np.linalg.norm(B - F2)
draw_right_angle(ax, F2, dir_F2D, dir_F2B, scale=L, size_ratio=0.016, color='#2563eb')

dir_G2D = (D2 - G2) / np.linalg.norm(D2 - G2)
dir_G2P = (P2 - G2) / np.linalg.norm(P2 - G2)
draw_right_angle(ax, G2, dir_G2D, dir_G2P, scale=L, size_ratio=0.016, color='#16a34a')

# 标注
label_point(ax, A, 'A', direction=(0, 1), scale=L, offset_ratio=0.07)
label_point(ax, B, 'B', direction=(-1, -1), scale=L, offset_ratio=0.055)
label_point(ax, D2, 'D', direction=(-1, 0.8), scale=L, offset_ratio=0.06)
label_point(ax, F2, 'F', direction=(-1, 1), scale=L, offset_ratio=0.06,
            owners={'F', 'A', 'B'})
label_point(ax, P2, 'P', direction=(-1.2, 0.5), scale=L, offset_ratio=0.06)
label_point(ax, G2, 'G', direction=(0.5, 1.2), scale=L, offset_ratio=0.06)

# 淡显其他点
label_point(ax, C, 'C', direction=(1, -1), scale=L, offset_ratio=0.05, color='#888888')
label_point(ax, E2, 'E', direction=(1, -1), scale=L, offset_ratio=0.07, color='#888888')
label_point(ax, M2, 'M', direction=(-1, -0.5), scale=L, offset_ratio=0.04, color='#888888')
label_point(ax, N, 'N', direction=(0.5, 1), scale=L, offset_ratio=0.04, color='#888888')

# 角弧
arc_r = 0.10 * L
draw_angle_arc(ax, D2, B, F2, arc_r, color='#2563eb')
draw_angle_arc(ax, D2, P2, G2, arc_r + 0.05 * L, color='#16a34a')

# 说明框
segments_c2 = [(A,B),(B,C),(C,A),(M2,N),(B,D2),(D2,E2),(D2,P2),
               (B,F2),(D2,F2),(P2,D2),(P2,G2),(D2,G2),(A,G2)]
place_legend_auto(ax, '同情形1：DF=DG, ∠FDG=90°\n∠BDF = ∠PDG (同角余角)\n△BDF ≌ △PDG (ASA)\n∴ BD = DP',
                 segments_c2, scale=L, color='#7c3aed', facecolor='#ede9fe', fontsize=11)

set_active_auditor(None)
violations = auditor.check()
assert not violations, f'step5_case2 layout VIOLATIONS: {violations}'
plt.savefig(os.path.join(_BASE_DIR, 'step5_case2_proof.png'), dpi=150, bbox_inches='tight', facecolor='white')
plt.close()


# ============================================================
# Case 3: 点 P 在 AC 的延长线上（图3）
# D 在 MN 上 A 的右侧，P 在 AC 延长线上（C 的右下方）
# D = (3,3)，则 DB 方向 (-6,-3)，垂向 (3,-6)=(1,-2)
# DE: (3+t, 3-2t)，与 AC (y=-x+3) 交点 P = (6, -3)
# BD = sqrt(45), DP = sqrt(45) → BD = DP
# ============================================================
D3 = np.array([3.0, 3.0])
# P3 = DE 与 AC 的交点（在 AC 延长线上，C 的右下方）
P3 = np.array([6.0, -3.0])
# E3 在 DE 上，DE ⟂ DB
# DB = (6,-3)，垂向 = (1,-2)
# DE 过 D(3,3) 方向 (1,-2)，取 t=5：E3 = (8, -7)
E3 = np.array([8.0, -7.0])
# 辅助点 F3 (D 到 AB 垂足), G3 (D 到 AC 垂足)
# AB: y=x+3，垂线通过 D(3,3)：x+y=6 → F=(1.5,4.5)
# AC: y=-x+3，垂线通过 D(3,3)：x-y=0 → G=(1.5,1.5)
F3 = np.array([1.5, 4.5])
G3 = np.array([1.5, 1.5])
# Case 3 专用的 MN 右端点（在 D3 右侧）
N3 = np.array([5.0, 3.0])


# ============================================================
# Step 6: Case 3 原题图（P 在 AC 延长线上）
# ============================================================
fig, ax = plt.subplots(figsize=(10, 7))
ax.set_axis_off()

key_pts_c3 = [A, B, C, D3, M, N3, P3, E3]
autoscale(ax, key_pts_c3, margin=0.22)
L = compute_visual_scale(ax)
auditor = LayoutAuditor(ax, 'step6_case3')
set_active_auditor(auditor)

draw_triangle(ax, A, B, C, names=('A', 'B', 'C'))
draw_aux_line(ax, M, N3, owners=('M', 'N', 'A', 'D'), color='#555555', linewidth=1.2, linestyle='-')

# DB, DE, DP
draw_aux_line(ax, B, D3, owners=('B', 'D'), color='#2563eb', linewidth=2.0, linestyle='-')
draw_aux_line(ax, D3, E3, owners=('D', 'E', 'P'), color='#2563eb', linewidth=2.0, linestyle='-')
draw_aux_line(ax, D3, P3, owners=('D', 'P', 'B'), color='#dc2626', linewidth=2.0, linestyle='-')

# AC 延长线（虚线）
ax.plot([C[0], P3[0]], [C[1], P3[1]], color='#999999', linewidth=1.0, linestyle='--', zorder=2)
if _ACTIVE_AUDITOR:
    _ACTIVE_AUDITOR.add_segment(C, P3, owner_points={'C', 'P'})

# 直角符号
draw_right_angle(ax, A, B - A, C - A, scale=L, size_ratio=0.018, color='black')
dir_DB3 = (B - D3) / np.linalg.norm(B - D3)
dir_DE3 = (E3 - D3) / np.linalg.norm(E3 - D3)
draw_right_angle(ax, D3, dir_DB3, dir_DE3, scale=L, size_ratio=0.018, color='#2563eb')

# 标注
label_point(ax, A, 'A', direction=(0, 1), scale=L, offset_ratio=0.055)
label_point(ax, B, 'B', direction=(-1, -0.5), scale=L, offset_ratio=0.055)
label_point(ax, C, 'C', direction=(0.5, -1), scale=L, offset_ratio=0.055)
label_point(ax, D3, 'D', direction=(0, 1), scale=L, offset_ratio=0.06)
label_point(ax, M, 'M', direction=(-1, 0.5), scale=L, offset_ratio=0.04)
label_point(ax, N3, 'N', direction=(1, 0), scale=L, offset_ratio=0.04)
label_point(ax, P3, 'P', direction=(1, -1), scale=L, offset_ratio=0.06)
label_point(ax, E3, 'E', direction=(0, -1), scale=L, offset_ratio=0.055)

# 说明框
annotate_box(ax, (-4.0, 4.5), '情形3: P 在 AC 延长线上',
             scale=L, color='#059669', facecolor='#d1fae5', fontsize=12)

set_active_auditor(None)
violations = auditor.check()
assert not violations, f'step6_case3 layout VIOLATIONS: {violations}'
plt.savefig(os.path.join(_BASE_DIR, 'step6_case3_config.png'), dpi=150, bbox_inches='tight', facecolor='white')
plt.close()


# ============================================================
# Step 7: Case 3 证明（作辅助线，全等三角形）
# ============================================================
fig, ax = plt.subplots(figsize=(10, 7))
ax.set_axis_off()

key_pts_c3p = [A, B, C, D3, M, N3, P3, E3, F3, G3]
autoscale(ax, key_pts_c3p, margin=0.22)
L = compute_visual_scale(ax)
auditor = LayoutAuditor(ax, 'step7_case3_proof')
set_active_auditor(auditor)

# 基础图形淡显
draw_triangle(ax, A, B, C, color='#999999', linewidth=1.2, alpha=0.30, names=('A','B','C'))
draw_aux_line(ax, M, N3, owners=('M','N','A','D'), color='#999999', linewidth=1.0, linestyle='-', alpha=0.30)
draw_aux_line(ax, D3, E3, owners=('D','E','P','G'), color='#999999', linewidth=1.2, alpha=0.30)
# 灰色虚线连接 AG、BF（显示 D 到两腰的垂足）
draw_aux_line(ax, A, G3, owners=('A','G','D'), color='#999999', linewidth=1.2, linestyle='--', alpha=0.50)
draw_aux_line(ax, B, F3, owners=('B','F','D'), color='#999999', linewidth=1.2, linestyle='--', alpha=0.50)

# 高亮 △BDF 与 △PDG
# △BDF
draw_aux_line(ax, B, D3, owners=('B','D'), color='#2563eb', linewidth=2.2, linestyle='-')
draw_aux_line(ax, B, F3, owners=('B','F'), color='#2563eb', linewidth=2.2, linestyle='-')
draw_aux_line(ax, D3, F3, owners=('D','F'), color='#2563eb', linewidth=2.2, linestyle='--')

# △PDG
draw_aux_line(ax, P3, D3, owners=('P','D','B'), color='#16a34a', linewidth=2.2, linestyle='-')
draw_aux_line(ax, P3, G3, owners=('P','G','C','A'), color='#16a34a', linewidth=2.2, linestyle='-')
draw_aux_line(ax, D3, G3, owners=('D','G'), color='#16a34a', linewidth=2.2, linestyle='--')

# 直角符号
dir_F3D = (D3 - F3) / np.linalg.norm(D3 - F3)
dir_F3B = (B - F3) / np.linalg.norm(B - F3)
draw_right_angle(ax, F3, dir_F3D, dir_F3B, scale=L, size_ratio=0.012, color='#2563eb')

dir_G3D = (D3 - G3) / np.linalg.norm(D3 - G3)
dir_G3P = (P3 - G3) / np.linalg.norm(P3 - G3)
draw_right_angle(ax, G3, dir_G3D, dir_G3P, scale=L, size_ratio=0.012, color='#16a34a')

# 标注
label_point(ax, A, 'A', direction=(0, 1), scale=L, offset_ratio=0.08)
label_point(ax, B, 'B', direction=(-1, -0.5), scale=L, offset_ratio=0.06)
label_point(ax, D3, 'D', direction=(0, 1), scale=L, offset_ratio=0.06)
# F/G 标签：走 G15 自适应方向（避免 0.14·L 偏移漂离点本体）
label_point(ax, F3, 'F', direction='auto', scale=L, offset_ratio=0.06,
            color='#2563eb', owners={'B', 'F', 'D'})
label_point(ax, P3, 'P', direction=(1, -1), scale=L, offset_ratio=0.055)
# G 标签：5 个邻近点 (A, B, D, F, P) 占据了不同方向，G15 无可用候选，走 G16 引线
label_point(ax, G3, 'G', leader=(0.5, -0.8), scale=L,
            color='#16a34a', owners={'D', 'G'})

# 淡显其他点
label_point(ax, C, 'C', direction=(0, 1), scale=L, offset_ratio=0.05, color='#888888')
label_point(ax, E3, 'E', direction=(-1, 1), scale=L, offset_ratio=0.07, color='#888888')
label_point(ax, M, 'M', direction=(-0.5, -1), scale=L, offset_ratio=0.04, color='#888888')
label_point(ax, N3, 'N', direction=(1, 0), scale=L, offset_ratio=0.04, color='#888888')

# 角弧（两角相等，用相同半径）
arc_r3 = 0.10 * L
draw_angle_arc(ax, D3, B, F3, arc_r3, color='#2563eb')
draw_angle_arc(ax, D3, P3, G3, arc_r3, color='#16a34a')

# 说明框
segments_c3 = [(A,B),(B,C),(C,A),(M,N3),(B,D3),(D3,E3),(D3,P3),
               (B,F3),(D3,F3),(P3,D3),(P3,G3),(D3,G3),(A,G3),(B,F3)]
place_legend_auto(ax, '同情形1：DF=DG, ∠FDG=90°\n∠BDF = ∠PDG (同角余角)\n△BDF ≌ △PDG (ASA)\n∴ BD = DP',
                 segments_c3, scale=L, color='#059669', facecolor='#d1fae5', fontsize=11)

set_active_auditor(None)
violations = auditor.check()
assert not violations, f'step7_case3 layout VIOLATIONS: {violations}'
plt.savefig(os.path.join(_BASE_DIR, 'step7_case3_proof.png'), dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

print("All figures generated successfully!")
