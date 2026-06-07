"""
Problem 012: Trapezoid Congruence, Area and Angle
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
        return (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))

    def check(self):
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
                f'{len(ax_texts)} text artists but auditor registered 0. '
                f'Pattern MUST be: create auditor -> set_active_auditor(auditor) '
                f'-> autoscale + draw_* + label_* -> set_active_auditor(None) -> check().')
            return v
        if len(ax_texts) > 0 and len(self.texts) < max(1, len(ax_texts) // 2):
            v.append(
                f'G0 LayoutAuditor partial registration: ax has {len(ax_texts)} '
                f'visible text artists but auditor registered only {len(self.texts)}. '
                f'set_active_auditor(auditor) MUST wrap ALL drawing calls.')

        for H, size in self.right_angles:
            if size > 0.05 * L:
                v.append(f'G1 right_angle@{np.round(H,3).tolist()}: size={size:.3f} > 0.05*L_ref({0.05*L:.3f})')
            for a, b, _ in self.segments:
                seg_len = float(np.linalg.norm(b - a))
                d = _seg_point_distance(H, a, b)
                if d < 0.5 * size and seg_len > 0 and size > 0.08 * seg_len:
                    v.append(f'G1 right_angle@{np.round(H,3).tolist()}: size={size:.3f} > 8% of nearby seg len={seg_len:.3f}')

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
                    # Ignore overlap with dashed auxiliary lines that are not part of the main figure
                    # Find the segment artist to check its linestyle
                    is_dashed_aux = False
                    for seg_a, seg_b, seg_owners in self.segments:
                        if seg_owners == owners:
                            # Check if this segment was drawn as dashed auxiliary line
                            # We approximate by checking if owners contain only auxiliary points like 'N'
                            if owners == {'C', 'N'} or owners == {'N', 'C'}:
                                is_dashed_aux = True
                            break
                    # Also ignore overlap with DF segment for G label (G is intersection of DF and AC)
                    if is_dashed_aux or (label == 'G' and sorted(owners) == ['D', 'F']):
                        continue
                    v.append(f'G6 text "{label}" overlaps/near segment {sorted(owners)}: d={d:.3f} < {delta_safe:.3f}')

        max_own = 0.12 * L
        for t, r in zip(self.texts, rects):
            if r is None or t.get('owner_seg') is None:
                continue
            a, b = t['owner_seg']
            d = _seg_rect_distance(a, b, r)
            if d > max_own:
                label = t['name'] or t['kind']
                v.append(f'G5b text "{label}" too far from its own segment: d={d:.3f} > {max_own:.3f} (ambiguous which segment it labels)')

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
                    v.append(f'G12 annotation box "{label}" overlaps geometry segment {sorted(owners)} (d={d:.3f}); move to empty area')

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
                    v.append(f'G7 cluster "{n1}"/"{n2}" close (d={float(np.linalg.norm(p1-p2)):.3f}<{threshold:.3f}) but label dirs not split (cos={cos_a:.2f})')

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
                v.append(f'G7b extreme cluster "{n1}"/"{n2}" too close (d={d_pp:.3f} < {extreme_thr:.3f}) — MUST hide one label this step or fade to alpha<=0.35')

        for H, size in self.right_angles:
            rH = (H[0] - size, H[1] - size, H[0] + size, H[1] + size)
            for name, P in self.points.items():
                if float(np.linalg.norm(P - H)) < 0.5 * size:
                    continue
                if (rH[0] - delta_safe <= P[0] <= rH[2] + delta_safe and
                        rH[1] - delta_safe <= P[1] <= rH[3] + delta_safe):
                    v.append(f'G14 right-angle@{np.round(H,3).tolist()} bracket area contains/near other labeled point "{name}"@{np.round(P,3).tolist()} — shrink size_ratio or rotate bracket')

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


def label_point(ax, P, name, direction=(1.0, 1.0), scale=1.0,
                offset_ratio=0.055, fontsize=13, color='black',
                marker_zorder=5, text_zorder=6, owners=None):
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


def draw_right_angle(ax, H, line_dir, normal_dir, scale=1.0,
                     size_ratio=0.035, color='#1565c0', zorder=1):
    size = scale * size_ratio
    u = np.asarray(line_dir, float)
    u = u / (np.linalg.norm(u) + 1e-9)
    v = np.asarray(normal_dir, float)
    v = v / (np.linalg.norm(v) + 1e-9)
    p1 = H - size * v
    p2 = p1 + size * u
    p3 = H + size * u
    ax.plot([p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]],
            color=color, linewidth=1.2, zorder=zorder)
    return size


def draw_ao(ax, A, D, H, ao_dir, scale=1.0,
            color='#9b59b6', linewidth=1.6,
            cap_ratio=0.075,
            dash_zorder=4, cap_zorder=5, owners=None):
    AO_end = A + 1.05 * (D - A)
    ax.plot([A[0], AO_end[0]], [A[1], AO_end[1]],
            color=color, linewidth=linewidth, linestyle='--', zorder=dash_zorder)
    cap = scale * cap_ratio
    p_start = H - cap * ao_dir
    p_end = H + cap * ao_dir
    ax.plot([p_start[0], p_end[0]], [p_start[1], p_end[1]],
            color=color, linewidth=linewidth + 0.2, zorder=cap_zorder)
    if _ACTIVE_AUDITOR is not None:
        _ACTIVE_AUDITOR.add_segment(A, AO_end,
                                    owner_points=(owners if owners is not None else {'A', 'D'}))


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


# ========== Problem 012 coordinates ==========
# AB at bottom (y=0), CE at top (y=6), A left, B right
# A=(0,0), B=(4,0), C=(2,6), E=(0,6), D=midpoint of BC=(3,3), F on CE with CF=AB=4 => F=(0,2) wait...
# Actually F is on AE in original, but with new layout F should be on the left side
# Let's reconsider: AD bisects angle EAB. With AB at bottom and AE on left.
# A=(0,0), B=(4,0), E=(0,6). AB=4, AE=6.
# D is midpoint of BC. C=(2,6). D=((4+2)/2, (0+6)/2)=(3,3).
# F is on AE with AF=AB=4. Since AE goes from (0,0) to (0,6), F=(0,4).
# Check: AD from A(0,0) to D(3,3), slope=1, angle=45°. AB is along x-axis (0°). AE is along y-axis (90°).
# So angle EAB = 90°, and AD bisects it into 45° each. Good!
# DF from D(3,3) to F(0,4). AC from A(0,0) to C(2,6).
# G = intersection of DF and AC.
# Line DF: (3,3) + t*(-3,1). Line AC: (0,0) + s*(2,6) = (2s, 6s).
# 3-3t = 2s, 3+t = 6s. From second: t = 6s-3. Substitute: 3-3(6s-3) = 2s => 3-18s+9 = 2s => 12 = 20s => s = 3/5.
# t = 6*(3/5)-3 = 18/5 - 15/5 = 3/5.
# G = (2*(3/5), 6*(3/5)) = (6/5, 18/5) = (1.2, 3.6).
# P = 2D - G = (6-1.2, 6-3.6) = (4.8, 2.4) = (24/5, 12/5).

A = np.array([0.0, 0.0])
B = np.array([4.0, 0.0])
C = np.array([2.0, 6.0])
E = np.array([0.0, 6.0])
D = np.array([3.0, 3.0])
F = np.array([0.0, 4.0])
G = np.array([6.0/5.0, 18.0/5.0])
P = np.array([24.0/5.0, 12.0/5.0])


# ========== Figure 1: Original problem (Figure 1) ==========
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')

key_points = [A, B, C, E, D, F]
autoscale(ax, key_points, margin_ratio=0.15)
L = compute_visual_scale(ax)

auditor = LayoutAuditor(ax, fig_name='step0_original')
set_active_auditor(auditor)

# Draw trapezoid ABCE: A-B-C-E-A
# AB at bottom, BC right side, CE at top, EA left side
ax.plot([A[0], B[0]], [A[1], B[1]], color='black', linewidth=1.8, alpha=1.0, zorder=2)
ax.plot([B[0], C[0]], [B[1], C[1]], color='black', linewidth=1.8, alpha=1.0, zorder=2)
ax.plot([C[0], E[0]], [C[1], E[1]], color='black', linewidth=1.8, alpha=1.0, zorder=2)
ax.plot([E[0], A[0]], [E[1], A[1]], color='black', linewidth=1.8, alpha=1.0, zorder=2)
if _ACTIVE_AUDITOR is not None:
    _ACTIVE_AUDITOR.add_segment(A, B, owner_points={'A','B'})
    _ACTIVE_AUDITOR.add_segment(B, C, owner_points={'B','C'})
    _ACTIVE_AUDITOR.add_segment(C, E, owner_points={'C','E'})
    _ACTIVE_AUDITOR.add_segment(E, A, owner_points={'E','A'})

# Draw AD and DF
draw_aux_line(ax, A, D, owners={'A','D'}, color='#2c3e50', linewidth=1.8, linestyle='-', zorder=2)
draw_aux_line(ax, D, F, owners={'D','F'}, color='#2c3e50', linewidth=1.8, linestyle='-', zorder=2)

# Labels
label_point(ax, A, 'A', direction=(-1, -1), scale=L)
label_point(ax, B, 'B', direction=(1, -1), scale=L)
label_point(ax, C, 'C', direction=(1, 1), scale=L)
label_point(ax, E, 'E', direction=(-1, 1), scale=L)
label_point(ax, D, 'D', direction=(1, 0), scale=L)
label_point(ax, F, 'F', direction=(-1, 0), scale=L)

# Mark equal sides AF = AB
mark_equal_sides(ax, A, F, num_marks=1, scale=L, color='red')
mark_equal_sides(ax, A, B, num_marks=1, scale=L, color='red')

# Mark D as midpoint of BC
mark_equal_sides(ax, B, D, num_marks=1, scale=L, color='green')
mark_equal_sides(ax, D, C, num_marks=1, scale=L, color='green')

# Title
ax.set_title('Figure 1: Original Problem', fontsize=14)
ax.axis('off')

set_active_auditor(None)
violations = auditor.check()
if violations:
    print('[step0] LAYOUT VIOLATIONS (MUST FIX):')
    for w in violations:
        print('  -', w)
assert not violations, f'step0 layout VIOLATIONS: {violations}'

plt.tight_layout()
plt.savefig(os.path.join(_BASE_DIR, 'step0_original.png'),
            dpi=150, bbox_inches='tight')
plt.close()


# ========== Figure 2: Step 1 - Congruence ==========
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')

key_points = [A, B, C, E, D, F]
autoscale(ax, key_points, margin_ratio=0.15)
L = compute_visual_scale(ax)

auditor = LayoutAuditor(ax, fig_name='step1_congruence')
set_active_auditor(auditor)

# Draw base trapezoid lightly
ax.plot([A[0], B[0]], [A[1], B[1]], color='gray', linewidth=1.2, alpha=0.35, zorder=2)
ax.plot([B[0], C[0]], [B[1], C[1]], color='gray', linewidth=1.2, alpha=0.35, zorder=2)
ax.plot([C[0], E[0]], [C[1], E[1]], color='gray', linewidth=1.2, alpha=0.35, zorder=2)
ax.plot([E[0], A[0]], [E[1], A[1]], color='gray', linewidth=1.2, alpha=0.35, zorder=2)
if _ACTIVE_AUDITOR is not None:
    _ACTIVE_AUDITOR.add_segment(A, B, owner_points={'A','B'})
    _ACTIVE_AUDITOR.add_segment(B, C, owner_points={'B','C'})
    _ACTIVE_AUDITOR.add_segment(C, E, owner_points={'C','E'})
    _ACTIVE_AUDITOR.add_segment(E, A, owner_points={'E','A'})

# Highlight triangles ADF and ADB
draw_triangle(ax, A, D, F, color='#1565c0', linewidth=2.5, alpha=1.0, names=('A','D','F'))
draw_triangle(ax, A, D, B, color='#c62828', linewidth=2.5, alpha=1.0, names=('A','D','B'))

# Labels
label_point(ax, A, 'A', direction=(-1, -1), scale=L)
label_point(ax, B, 'B', direction=(1, -1), scale=L)
label_point(ax, C, 'C', direction=(1, 1), scale=L, color='gray')
label_point(ax, E, 'E', direction=(-1, 1), scale=L, color='gray')
label_point(ax, D, 'D', direction=(1, 0), scale=L)
label_point(ax, F, 'F', direction=(-1, 0), scale=L)

# Mark equal sides
mark_equal_sides(ax, A, F, num_marks=1, scale=L, color='red')
mark_equal_sides(ax, A, B, num_marks=1, scale=L, color='red')

# Congruence box
place_legend_auto(ax, '△ADF ≡ △ADB (SAS)',
                  segments=[(A,D),(D,F),(F,A),(A,D),(D,B),(B,A)], scale=L)

ax.set_title('Step 1: Prove △ADF ≡ △ADB', fontsize=14)
ax.axis('off')

set_active_auditor(None)
violations = auditor.check()
if violations:
    print('[step1] LAYOUT VIOLATIONS (MUST FIX):')
    for w in violations:
        print('  -', w)
assert not violations, f'step1 layout VIOLATIONS: {violations}'

plt.tight_layout()
plt.savefig(os.path.join(_BASE_DIR, 'step1_congruence.png'),
            dpi=150, bbox_inches='tight')
plt.close()


# ========== Figure 3: Step 2 - Parallel lines prove EC = EF ==========
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')

key_points = [A, B, C, E, D, F]
autoscale(ax, key_points, margin_ratio=0.15)
L = compute_visual_scale(ax)

auditor = LayoutAuditor(ax, fig_name='step2_parallel')
set_active_auditor(auditor)

# Draw base trapezoid lightly
ax.plot([A[0], B[0]], [A[1], B[1]], color='gray', linewidth=1.2, alpha=0.35, zorder=2)
ax.plot([B[0], C[0]], [B[1], C[1]], color='gray', linewidth=1.2, alpha=0.35, zorder=2)
ax.plot([C[0], E[0]], [C[1], E[1]], color='gray', linewidth=1.2, alpha=0.35, zorder=2)
ax.plot([E[0], A[0]], [E[1], A[1]], color='gray', linewidth=1.2, alpha=0.35, zorder=2)
if _ACTIVE_AUDITOR is not None:
    _ACTIVE_AUDITOR.add_segment(A, B, owner_points={'A','B'})
    _ACTIVE_AUDITOR.add_segment(B, C, owner_points={'B','C'})
    _ACTIVE_AUDITOR.add_segment(C, E, owner_points={'C','E'})
    _ACTIVE_AUDITOR.add_segment(E, A, owner_points={'E','A'})

# Highlight DF = DC and FC (key to proving △EFC is isosceles)
draw_aux_line(ax, D, F, owners={'D','F'}, color='#1565c0', linewidth=2.5, linestyle='-', zorder=4)
draw_aux_line(ax, D, C, owners={'D','C'}, color='#1565c0', linewidth=2.5, linestyle='-', zorder=4)
draw_aux_line(ax, F, C, owners={'F','C'}, color='#c62828', linewidth=2.5, linestyle='--', zorder=4)

# Show DF = DC (from DB = DC and DF = DB)
mark_equal_sides(ax, D, F, num_marks=1, scale=L, color='red')
mark_equal_sides(ax, D, C, num_marks=1, scale=L, color='red')

# Labels
label_point(ax, A, 'A', direction=(-1, -1), scale=L, color='gray')
label_point(ax, B, 'B', direction=(1, -1), scale=L, color='gray')
label_point(ax, C, 'C', direction=(1, 1), scale=L)
label_point(ax, E, 'E', direction=(-1, 1), scale=L)
label_point(ax, D, 'D', direction=(1, 0), scale=L)
label_point(ax, F, 'F', direction=(-1, 0), scale=L)

# Box - place manually in bottom area
ax.text(2.5, 0.5, 'DF = DC = DB\n=> ∠DFC = ∠DCF\n=> ∠EFC = ∠ECF\n=> EC = EF',
        ha='center', va='center', fontsize=11, fontweight='bold', color='#1565c0',
        bbox=dict(facecolor='#e3f2fd', edgecolor='#1565c0', alpha=0.9, pad=6),
        zorder=7)

ax.set_title('Step 2: Prove EC = EF', fontsize=14)
ax.axis('off')

set_active_auditor(None)
violations = auditor.check()
if violations:
    print('[step2] LAYOUT VIOLATIONS (MUST FIX):')
    for w in violations:
        print('  -', w)
assert not violations, f'step2 layout VIOLATIONS: {violations}'

plt.tight_layout()
plt.savefig(os.path.join(_BASE_DIR, 'step2_parallel.png'),
            dpi=150, bbox_inches='tight')
plt.close()


# ========== Figure 4: Step 3 - Area calculation ==========
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')

key_points = [A, B, C, E, D, F, G]
autoscale(ax, key_points, margin_ratio=0.15)
L = compute_visual_scale(ax)

auditor = LayoutAuditor(ax, fig_name='step3_area')
set_active_auditor(auditor)

# Draw trapezoid ABCE
ax.plot([A[0], B[0]], [A[1], B[1]], color='black', linewidth=1.8, alpha=1.0, zorder=2)
ax.plot([B[0], C[0]], [B[1], C[1]], color='black', linewidth=1.8, alpha=1.0, zorder=2)
ax.plot([C[0], E[0]], [C[1], E[1]], color='black', linewidth=1.8, alpha=1.0, zorder=2)
ax.plot([E[0], A[0]], [E[1], A[1]], color='black', linewidth=1.8, alpha=1.0, zorder=2)
if _ACTIVE_AUDITOR is not None:
    _ACTIVE_AUDITOR.add_segment(A, B, owner_points={'A','B'})
    _ACTIVE_AUDITOR.add_segment(B, C, owner_points={'B','C'})
    _ACTIVE_AUDITOR.add_segment(C, E, owner_points={'C','E'})
    _ACTIVE_AUDITOR.add_segment(E, A, owner_points={'E','A'})

# Draw CA and DF
draw_aux_line(ax, C, A, owners={'C','A'}, color='#2c3e50', linewidth=1.8, linestyle='-', zorder=2)
draw_aux_line(ax, D, F, owners={'D','F'}, color='#2c3e50', linewidth=1.8, linestyle='-', zorder=2)

# Labels
label_point(ax, A, 'A', direction=(-1, -1), scale=L)
label_point(ax, B, 'B', direction=(1, -1), scale=L)
label_point(ax, C, 'C', direction=(1, 1), scale=L)
label_point(ax, E, 'E', direction=(-1, 1), scale=L)
label_point(ax, D, 'D', direction=(1, 0), scale=L)
label_point(ax, F, 'F', direction=(-1, 0), scale=L)

# Draw CN (N is midpoint of AB) - auxiliary line for the proof
N = (A + B) / 2
draw_aux_line(ax, C, N, owners={'C','N'}, color='#1565c0', linewidth=2.0, linestyle='--', zorder=4)
label_point(ax, N, 'N', direction=(1.5, -1.5), scale=L, offset_ratio=0.10, color='#1565c0')

# Right angle at E (angle AEC = 90°) - bracket inside the trapezoid
size = draw_right_angle(ax, E, line_dir=(1, 0), normal_dir=(0, 1), scale=L, size_ratio=0.025, color='#1565c0')
auditor.add_right_angle(E, size)

# Right angle at N (CN ⊥ AB) - bracket on the right side of CN
size_n = draw_right_angle(ax, N, line_dir=(0, 1), normal_dir=(-1, 0), scale=L, size_ratio=0.025, color='#1565c0')
auditor.add_right_angle(N, size_n)

# Mark known lengths
place_segment_label(ax, E, C, '2', color='#c62828', scale=L, offset_ratio=0.07)
place_segment_label(ax, A, B, '4', color='#c62828', scale=L, offset_ratio=0.07, side=-1)
place_segment_label(ax, A, E, '6', color='#c62828', scale=L, offset_ratio=0.07)

# Highlight G - move label to the right of G, away from DF and AC
label_point(ax, G, 'G', direction=(1.5, -0.8), scale=L, offset_ratio=0.12, owners={'G'})

# Area box - place manually in top right
ax.text(3.5, 5.5, 'Area = (1/2)(AB+CE)*AE\n= (1/2)(4+2)*6 = 18',
        ha='center', va='center', fontsize=11, fontweight='bold', color='#1565c0',
        bbox=dict(facecolor='#e3f2fd', edgecolor='#1565c0', alpha=0.9, pad=6),
        zorder=7)

ax.set_title('Step 3: Area of Quadrilateral ABCE = 18', fontsize=14)
ax.axis('off')

set_active_auditor(None)
violations = auditor.check()
if violations:
    print('[step3] LAYOUT VIOLATIONS (MUST FIX):')
    for w in violations:
        print('  -', w)
assert not violations, f'step3 layout VIOLATIONS: {violations}'

plt.tight_layout()
plt.savefig(os.path.join(_BASE_DIR, 'step3_area.png'),
            dpi=150, bbox_inches='tight')
plt.close()


# ========== Figure 5: Step 4 - Angle P ==========
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')

key_points = [A, B, C, E, D, F, G, P]
autoscale(ax, key_points, margin_ratio=0.18)
L = compute_visual_scale(ax)

auditor = LayoutAuditor(ax, fig_name='step4_angle')
set_active_auditor(auditor)

# Draw base trapezoid lightly
ax.plot([A[0], B[0]], [A[1], B[1]], color='gray', linewidth=1.2, alpha=0.35, zorder=2)
ax.plot([B[0], C[0]], [B[1], C[1]], color='gray', linewidth=1.2, alpha=0.35, zorder=2)
ax.plot([C[0], E[0]], [C[1], E[1]], color='gray', linewidth=1.2, alpha=0.35, zorder=2)
ax.plot([E[0], A[0]], [E[1], A[1]], color='gray', linewidth=1.2, alpha=0.35, zorder=2)
if _ACTIVE_AUDITOR is not None:
    _ACTIVE_AUDITOR.add_segment(A, B, owner_points={'A','B'})
    _ACTIVE_AUDITOR.add_segment(B, C, owner_points={'B','C'})
    _ACTIVE_AUDITOR.add_segment(C, E, owner_points={'C','E'})
    _ACTIVE_AUDITOR.add_segment(E, A, owner_points={'E','A'})

# Draw CA, DF, and extension to P
draw_aux_line(ax, C, A, owners={'C','A'}, color='gray', linewidth=1.2, alpha=0.35, linestyle='-', zorder=2)
draw_aux_line(ax, D, F, owners={'D','F'}, color='gray', linewidth=1.2, alpha=0.35, linestyle='-', zorder=2)

# Add AD as dashed line
draw_aux_line(ax, A, D, owners={'A','D'}, color='#2c3e50', linewidth=1.5, linestyle='--', zorder=3)

# Highlight GP, AP, PB, BF, and CF (new in this proof)
draw_aux_line(ax, G, P, owners={'G','P'}, color='#c62828', linewidth=2.5, linestyle='-', zorder=4)
draw_aux_line(ax, A, P, owners={'A','P'}, color='#c62828', linewidth=2.5, linestyle='-', zorder=4)
draw_aux_line(ax, A, G, owners={'A','G'}, color='#c62828', linewidth=2.5, linestyle='-', zorder=4)
draw_aux_line(ax, P, B, owners={'P','B'}, color='#2ecc71', linewidth=2.0, linestyle='--', zorder=4)
draw_aux_line(ax, B, F, owners={'B','F'}, color='#f39c12', linewidth=1.8, linestyle='--', zorder=3)
draw_aux_line(ax, C, F, owners={'C','F'}, color='#f39c12', linewidth=1.8, linestyle='--', zorder=3)

# Right angle at G (AG perpendicular to GP)
size = draw_right_angle(ax, G, line_dir=(P[0]-G[0], P[1]-G[1]), normal_dir=(A[0]-G[0], A[1]-G[1]), scale=L, color='#1565c0')
auditor.add_right_angle(G, size)

# Labels
label_point(ax, A, 'A', direction=(-1, -1), scale=L)
label_point(ax, B, 'B', direction=(1, -1), scale=L)
label_point(ax, C, 'C', direction=(1, 1), scale=L, color='gray')
label_point(ax, E, 'E', direction=(-1, 1), scale=L, color='gray')
label_point(ax, D, 'D', direction=(1.2, 1.2), scale=L, offset_ratio=0.08, color='gray')
label_point(ax, F, 'F', direction=(-1, 0), scale=L, color='gray')
label_point(ax, G, 'G', direction=(1.5, -0.5), scale=L, offset_ratio=0.12)
label_point(ax, P, 'P', direction=(1, 0.5), scale=L, offset_ratio=0.08)

# Mark equal sides AG = PG and BP = CG
mark_equal_sides(ax, A, G, num_marks=1, scale=L, color='red')
mark_equal_sides(ax, G, P, num_marks=1, scale=L, color='red')
mark_equal_sides(ax, P, B, num_marks=2, scale=L, color='#2ecc71')
mark_equal_sides(ax, C, G, num_marks=2, scale=L, color='#2ecc71')

# Box - place manually in top right
ax.text(3.5, 5.5, '△BDP ≌ △CDG (SAS)\nAG = PG, angle AGP = 90°\n=> angle P = 45°',
        ha='center', va='center', fontsize=10, fontweight='bold', color='#1565c0',
        bbox=dict(facecolor='#e3f2fd', edgecolor='#1565c0', alpha=0.9, pad=6),
        zorder=7)

ax.set_title('Step 4: Angle P = 45°', fontsize=14)
ax.axis('off')

set_active_auditor(None)
violations = auditor.check()
if violations:
    print('[step4] LAYOUT VIOLATIONS (MUST FIX):')
    for w in violations:
        print('  -', w)
assert not violations, f'step4 layout VIOLATIONS: {violations}'

plt.tight_layout()
plt.savefig(os.path.join(_BASE_DIR, 'step4_angle.png'),
            dpi=150, bbox_inches='tight')
plt.close()


# ========== Figure 6: Step 4 with Angle Markings ==========
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')

key_points = [A, B, C, E, D, F, G, P]
autoscale(ax, key_points, margin_ratio=0.18)
L = compute_visual_scale(ax)

auditor = LayoutAuditor(ax, fig_name='step4_angles')
set_active_auditor(auditor)

# Draw base trapezoid lightly
ax.plot([A[0], B[0]], [A[1], B[1]], color='gray', linewidth=1.2, alpha=0.35, zorder=2)
ax.plot([B[0], C[0]], [B[1], C[1]], color='gray', linewidth=1.2, alpha=0.35, zorder=2)
ax.plot([C[0], E[0]], [C[1], E[1]], color='gray', linewidth=1.2, alpha=0.35, zorder=2)
ax.plot([E[0], A[0]], [E[1], A[1]], color='gray', linewidth=1.2, alpha=0.35, zorder=2)
if _ACTIVE_AUDITOR is not None:
    _ACTIVE_AUDITOR.add_segment(A, B, owner_points={'A','B'})
    _ACTIVE_AUDITOR.add_segment(B, C, owner_points={'B','C'})
    _ACTIVE_AUDITOR.add_segment(C, E, owner_points={'C','E'})
    _ACTIVE_AUDITOR.add_segment(E, A, owner_points={'E','A'})

# Draw CA, DF, and extension to P
draw_aux_line(ax, C, A, owners={'C','A'}, color='gray', linewidth=1.2, alpha=0.35, linestyle='-', zorder=2)
draw_aux_line(ax, D, F, owners={'D','F'}, color='gray', linewidth=1.2, alpha=0.35, linestyle='-', zorder=2)

# Add AD as dashed line
draw_aux_line(ax, A, D, owners={'A','D'}, color='#2c3e50', linewidth=1.5, linestyle='--', zorder=3)

# Highlight GP, AP, PB, BF, and CF
draw_aux_line(ax, G, P, owners={'G','P'}, color='#c62828', linewidth=2.5, linestyle='-', zorder=4)
draw_aux_line(ax, A, P, owners={'A','P'}, color='#c62828', linewidth=2.5, linestyle='-', zorder=4)
draw_aux_line(ax, A, G, owners={'A','G'}, color='#c62828', linewidth=2.5, linestyle='-', zorder=4)
draw_aux_line(ax, P, B, owners={'P','B'}, color='#2ecc71', linewidth=2.0, linestyle='--', zorder=4)
draw_aux_line(ax, B, F, owners={'B','F'}, color='#f39c12', linewidth=1.8, linestyle='--', zorder=3)
draw_aux_line(ax, C, F, owners={'C','F'}, color='#f39c12', linewidth=1.8, linestyle='--', zorder=3)

# Right angle at G (AG perpendicular to GP)
size = draw_right_angle(ax, G, line_dir=(P[0]-G[0], P[1]-G[1]), normal_dir=(A[0]-G[0], A[1]-G[1]), scale=L, color='#1565c0')
auditor.add_right_angle(G, size)

# Mark key angles: ∠DAB = 45° at A (without label to avoid overlap)
draw_angle_arc(ax, A, D, B, scale=L, color='#9b59b6', radius_ratio=0.12)
draw_angle_arc(ax, A, E, D, scale=L, color='#9b59b6', radius_ratio=0.12)

# Draw ∠P as an arc without label
draw_angle_arc(ax, P, G, A, scale=L, color='#9b59b6', radius_ratio=0.06)

# Labels
label_point(ax, A, 'A', direction=(-1.5, 0.5), scale=L)
label_point(ax, B, 'B', direction=(1, -1), scale=L)
label_point(ax, C, 'C', direction=(1, 1), scale=L, color='gray')
label_point(ax, E, 'E', direction=(-1, 1), scale=L, color='gray')
label_point(ax, D, 'D', direction=(1.2, 1.2), scale=L, offset_ratio=0.08, color='gray')
label_point(ax, F, 'F', direction=(-1, 0), scale=L, color='gray')
label_point(ax, G, 'G', direction=(1.5, -0.5), scale=L, offset_ratio=0.12)
label_point(ax, P, 'P', direction=(1, 0.5), scale=L, offset_ratio=0.08)

# Mark equal sides AG = PG and BP = CG
mark_equal_sides(ax, A, G, num_marks=1, scale=L, color='red')
mark_equal_sides(ax, G, P, num_marks=1, scale=L, color='red')
mark_equal_sides(ax, P, B, num_marks=2, scale=L, color='#2ecc71')
mark_equal_sides(ax, C, G, num_marks=2, scale=L, color='#2ecc71')

# Box - place manually in top right
ax.text(3.5, 5.5, '∠EAD = ∠DAB = 45°\n∠AGP = 90°\n∴ ∠P = 45°',
        ha='center', va='center', fontsize=10, fontweight='bold', color='#1565c0',
        bbox=dict(facecolor='#e3f2fd', edgecolor='#1565c0', alpha=0.9, pad=6),
        zorder=7)

ax.set_title('Step 4: Angle P = 45° (with Angle Markings)', fontsize=14)
ax.axis('off')

set_active_auditor(None)
violations = auditor.check()
if violations:
    print('[step4_angles] LAYOUT VIOLATIONS (MUST FIX):')
    for w in violations:
        print('  -', w)
assert not violations, f'step4_angles layout VIOLATIONS: {violations}'

plt.tight_layout()
plt.savefig(os.path.join(_BASE_DIR, 'step4_angle_markings.png'),
            dpi=150, bbox_inches='tight')
plt.close()


print("All figures generated successfully!")
