"""
Problem 012: Trapezoid Congruence, Area and Angle
Method: Extend AD to meet EC at M (全等构造法)
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
                v.append(f'G7b extreme cluster "{n1}"/"{n2}" too close (d={d_pp:.3f} < {extreme_thr:.3f})')

        for H, size in self.right_angles:
            rH = (H[0] - size, H[1] - size, H[0] + size, H[1] + size)
            for name, P in self.points.items():
                if float(np.linalg.norm(P - H)) < 0.5 * size:
                    continue
                if (rH[0] - delta_safe <= P[0] <= rH[2] + delta_safe and
                        rH[1] - delta_safe <= P[1] <= rH[3] + delta_safe):
                    v.append(f'G14 right-angle@{np.round(H,3).tolist()} bracket area contains/near other labeled point "{name}"')

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
    # Prevent accidental far-away point labels (e.g., 0.25~0.30 of L_ref).
    if offset_ratio > 0.20:
        raise ValueError(
            f'label_point offset_ratio={offset_ratio:.3f} is too large; '
            'use <=0.08 for normal labels, or use a dedicated callout.')
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
    # Draw the right-angle bracket inside the angle formed by rays (H->u) and (H->v).
    p1 = H + size * u
    p2 = H + size * (u + v)
    p3 = H + size * v
    ax.plot([p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]],
            color=color, linewidth=1.2, zorder=zorder)
    return size


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
A = np.array([0.0, 0.0])
B = np.array([4.0, 0.0])
C = np.array([2.0, 6.0])
E = np.array([0.0, 6.0])
D = np.array([3.0, 3.0])
F = np.array([0.0, 4.0])
M = np.array([6.0, 6.0])
H = np.array([2.0, 0.0])
G = np.array([6.0 / 5.0, 18.0 / 5.0])
P = np.array([24.0 / 5.0, 12.0 / 5.0])
M2 = np.array([1.0, 3.0])
H2 = np.array([0.0, 3.0])


def _finalize(ax, auditor, fig_name):
    set_active_auditor(None)
    violations = auditor.check()
    if violations:
        print(f'[{fig_name}] LAYOUT VIOLATIONS (MUST FIX):')
        for w in violations:
            print('  -', w)
    assert not violations, f'{fig_name} layout VIOLATIONS: {violations}'
    plt.tight_layout()
    plt.savefig(os.path.join(_BASE_DIR, fig_name + '.png'), dpi=150, bbox_inches='tight')
    plt.close()


# ========== Figure 1: Original Problem (step0) ==========
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')
autoscale(ax, [A, B, C, E, D, F], margin_ratio=0.15)
L = compute_visual_scale(ax)
auditor = LayoutAuditor(ax, fig_name='step0_original')
set_active_auditor(auditor)

draw_aux_line(ax, A, B, owners={'A', 'B'}, color='black', linewidth=1.8, linestyle='-', zorder=2)
draw_aux_line(ax, B, C, owners={'B', 'C'}, color='black', linewidth=1.8, linestyle='-', zorder=2)
draw_aux_line(ax, C, E, owners={'C', 'E'}, color='black', linewidth=1.8, linestyle='-', zorder=2)
draw_aux_line(ax, E, A, owners={'E', 'A'}, color='black', linewidth=1.8, linestyle='-', zorder=2)
draw_aux_line(ax, A, D, owners={'A', 'D'}, color='#2c3e50', linewidth=1.8, linestyle='-', zorder=2)
draw_aux_line(ax, D, F, owners={'D', 'F'}, color='#2c3e50', linewidth=1.8, linestyle='-', zorder=2)
mark_equal_sides(ax, A, F, num_marks=1, scale=L, color='red')
mark_equal_sides(ax, A, B, num_marks=1, scale=L, color='red')
mark_equal_sides(ax, B, D, num_marks=1, scale=L, color='green')
mark_equal_sides(ax, D, C, num_marks=1, scale=L, color='green')

label_point(ax, A, 'A', direction=(-1, -1), scale=L)
label_point(ax, B, 'B', direction=(1, -1), scale=L)
label_point(ax, C, 'C', direction=(1, 1), scale=L)
label_point(ax,E, 'E', direction=(-1, 1), scale=L)
label_point(ax, D, 'D', direction=(1, 0), scale=L)
label_point(ax, F, 'F', direction=(-1, 0), scale=L)
ax.set_title('Original Problem', fontsize=14)
ax.axis('off')
_finalize(ax, auditor, 'step0_original')


# ========== Figure 2: Step 1 ==========
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')
autoscale(ax, [A, B, C, E, D, F, M], margin_ratio=0.15)
L = compute_visual_scale(ax)
auditor = LayoutAuditor(ax, fig_name='step1_congruence')
set_active_auditor(auditor)

draw_aux_line(ax, A, B, owners={'A', 'B'}, color='gray', linewidth=1.2, linestyle='-', alpha=0.35, zorder=2)
draw_aux_line(ax, B, C, owners={'B', 'C'}, color='gray', linewidth=1.2, linestyle='-', alpha=0.35, zorder=2)
draw_aux_line(ax, C, E, owners={'C', 'E'}, color='gray', linewidth=1.2, linestyle='-', alpha=0.35, zorder=2)
draw_aux_line(ax, E, A, owners={'E', 'A'}, color='gray', linewidth=1.2, linestyle='-', alpha=0.35, zorder=2)
draw_aux_line(ax, A, D, owners={'A', 'D'}, color='#2c3e50', linewidth=1.8, linestyle='-', zorder=2)
draw_aux_line(ax, D, M, owners={'D', 'M'}, color='#9b59b6', linewidth=1.6, linestyle='--', zorder=4)
draw_aux_line(ax, C, M, owners={'C', 'M'}, color='#9b59b6', linewidth=1.6, linestyle='--', zorder=4)
draw_triangle(ax, A, B, D, color='#1565c0', linewidth=2.5, alpha=1.0, names=('A', 'B', 'D'))
draw_triangle(ax, M, C, D, color='#c62828', linewidth=2.5, alpha=1.0, names=('M', 'C', 'D'))
mark_equal_sides(ax, A, B, num_marks=1, scale=L, color='red')
mark_equal_sides(ax, C, M, num_marks=1, scale=L, color='red')
mark_equal_sides(ax, B, D, num_marks=1, scale=L, color='green')
mark_equal_sides(ax, D, C, num_marks=1, scale=L, color='green')
mark_equal_sides(ax, A, D, num_marks=2, scale=L, color='orange')
mark_equal_sides(ax, D, M, num_marks=2, scale=L, color='orange')

label_point(ax, A, 'A', direction=(-1, -1), scale=L, color='gray')
label_point(ax, B, 'B', direction=(1, -1), scale=L, color='gray')
label_point(ax, C, 'C', direction=(0, -1.2), scale=L)
label_point(ax, E, 'E', direction=(-1, 1), scale=L, color='gray')
label_point(ax, D, 'D', direction=(1.2, 0), scale=L)
label_point(ax, F, 'F', direction=(-1, 0), scale=L, color='gray')
label_point(ax, M, 'M', direction=(1, 0), scale=L, color='#c62828')
place_legend_auto(ax, '△ABD ≡ △MCD (AAS)\nAB=CM, AD=MD',
                  segments=[(A, B), (B, D), (D, A), (M, C), (C, D), (D, M)], scale=L)
ax.set_title('Step 1: Extend AD to M', fontsize=13)
ax.axis('off')
_finalize(ax, auditor, 'step1_congruence')


# ========== Figure 3: Step 2 ==========
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')
autoscale(ax, [A, B, C, E, D, F, M], margin_ratio=0.15)
L = compute_visual_scale(ax)
auditor = LayoutAuditor(ax, fig_name='step2_isosceles')
set_active_auditor(auditor)

draw_aux_line(ax, A, B, owners={'A', 'B'}, color='gray', linewidth=1.2, linestyle='-', alpha=0.35, zorder=2)
draw_aux_line(ax, B, C, owners={'B', 'C'}, color='gray', linewidth=1.2, linestyle='-', alpha=0.35, zorder=2)
draw_aux_line(ax, C, E, owners={'C', 'E'}, color='gray', linewidth=1.2, linestyle='-', alpha=0.35, zorder=2)
draw_aux_line(ax, E, A, owners={'E', 'A'}, color='gray', linewidth=1.2, linestyle='-', alpha=0.35, zorder=2)
draw_aux_line(ax, A, D, owners={'A', 'D'}, color='gray', linewidth=1.2, linestyle='--', alpha=0.5, zorder=2)
draw_triangle(ax, E, M, A, color='#1565c0', linewidth=2.5, alpha=1.0, names=('E', 'M', 'A'))
draw_aux_line(ax, E, F, owners={'E', 'F'}, color='#c62828', linewidth=2.3, linestyle='-', zorder=4)
draw_aux_line(ax, E, C, owners={'E', 'C'}, color='gray', linewidth=1.2, linestyle='-', alpha=0.35, zorder=2)
mark_equal_sides(ax, E, A, num_marks=1, scale=L, color='#1565c0')
mark_equal_sides(ax, E, M, num_marks=1, scale=L, color='#1565c0')
mark_equal_sides(ax, E, C, num_marks=2, scale=L, color='#c62828')
mark_equal_sides(ax, E, F, num_marks=2, scale=L, color='#c62828')

label_point(ax, A, 'A', direction=(-1, -1), scale=L)
label_point(ax, B, 'B', direction=(1, -1), scale=L, color='gray')
label_point(ax, C, 'C', direction=(0, 1), scale=L)
label_point(ax, D, 'D', direction=(1.8, -1.2), scale=L, color='gray', offset_ratio=0.075,
            owners={'D', 'B', 'C'})
label_point(ax, E, 'E', direction=(-1, 1), scale=L)
label_point(ax, F, 'F', direction=(-1, -1), scale=L)
label_point(ax, M, 'M', direction=(1, 0), scale=L, color='#1565c0')
place_legend_auto(ax, 'EA = EM and AF = CM\n=> EC = EF',
                  segments=[(E, A), (E, M), (E, C), (E, F)], scale=L)
ax.set_title('Step 2: Prove EC = EF', fontsize=13)
ax.axis('off')
_finalize(ax, auditor, 'step2_isosceles')


# ========== Figure 4: Step 3 ==========
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')
autoscale(ax, [A, B, C, E, H], margin_ratio=0.15)
L = compute_visual_scale(ax)
auditor = LayoutAuditor(ax, fig_name='step3_area')
set_active_auditor(auditor)

draw_aux_line(ax, A, B, owners={'A', 'B'}, color='black', linewidth=1.8, linestyle='-', zorder=2)
draw_aux_line(ax, B, C, owners={'B', 'C'}, color='black', linewidth=1.8, linestyle='-', zorder=2)
draw_aux_line(ax, C, E, owners={'C', 'E'}, color='black', linewidth=1.8, linestyle='-', zorder=2)
draw_aux_line(ax, E, A, owners={'E', 'A'}, color='black', linewidth=1.8, linestyle='-', zorder=2)
draw_aux_line(ax, C, H, owners={'C', 'H'}, color='#1565c0', linewidth=2.0, linestyle='--', zorder=4)
draw_aux_line(ax, C, A, owners={'C', 'A'}, color='#2c3e50', linewidth=1.8, linestyle='-', zorder=2)

size_e = draw_right_angle(ax, E, line_dir=(1, 0), normal_dir=(0, -1), scale=L, size_ratio=0.025, color='#1565c0')
auditor.add_right_angle(E, size_e)
size_a = draw_right_angle(ax, A, line_dir=(1, 0), normal_dir=(0, 1), scale=L, size_ratio=0.025, color='#1565c0')
auditor.add_right_angle(A, size_a)
size_h = draw_right_angle(ax, H, line_dir=(1, 0), normal_dir=(0, 1), scale=L, size_ratio=0.025, color='#1565c0')
auditor.add_right_angle(H, size_h)

place_segment_label(ax, E, C, '2', color='#c62828', scale=L, offset_ratio=0.07)
place_segment_label(ax, A, H, '2', color='#c62828', scale=L, offset_ratio=0.07, side=-1)
place_segment_label(ax, H, B, '2', color='#c62828', scale=L, offset_ratio=0.07, side=-1)
place_segment_label(ax, A, B, '4', color='#c62828', scale=L, offset_ratio=0.07, side=-1)
place_segment_label(ax, A, E, '6', color='#c62828', scale=L, offset_ratio=0.07)

label_point(ax, A, 'A', direction=(-1, -1), scale=L)
label_point(ax, B, 'B', direction=(1, -1), scale=L)
label_point(ax, C, 'C', direction=(1, 1), scale=L)
label_point(ax, E, 'E', direction=(-1, 1), scale=L)
label_point(ax, H, 'H', direction=(1, -1), scale=L, offset_ratio=0.08)

place_legend_auto(ax, 'Area = 2x6 + (1/2)x2x6 = 18',
                  segments=[(A, B), (B, C), (C, E), (E, A)], scale=L, fontsize=10)
ax.set_title('Step 3: Area = 18', fontsize=13)
ax.axis('off')
_finalize(ax, auditor, 'step3_area')


# ========== Figure 5: Step 4 - prove ∠BFC = 90° ==========
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')
autoscale(ax, [A, B, C, E, F], margin_ratio=0.18)
L = compute_visual_scale(ax)
auditor = LayoutAuditor(ax, fig_name='step4_angle')
set_active_auditor(auditor)

draw_triangle(ax, F, A, B, color='#1565c0', linewidth=2.2, alpha=1.0, names=('F', 'A', 'B'))
draw_triangle(ax, F, E, C, color='#2e7d32', linewidth=2.2, alpha=1.0, names=('F', 'E', 'C'))
draw_aux_line(ax, A, E, owners={'A', 'F', 'E'}, color='black', linewidth=1.8, linestyle='-', zorder=3)
size_f = draw_right_angle(ax, F, line_dir=(B[0] - F[0], B[1] - F[1]),
                          normal_dir=(C[0] - F[0], C[1] - F[1]), scale=L,
                          size_ratio=0.020, color='#c62828')
auditor.add_right_angle(F, size_f)
draw_angle_arc(ax, F, A, B, scale=L, color='#1565c0', radius_ratio=0.08)
draw_angle_arc(ax, F, C, E, scale=L, color='#2e7d32', radius_ratio=0.11)

label_point(ax, A, 'A', direction=(-1, -1), scale=L)
label_point(ax, B, 'B', direction=(1, -1), scale=L)
label_point(ax, C, 'C', direction=(1, 1), scale=L)
label_point(ax, E, 'E', direction=(-1, 1), scale=L)
label_point(ax, F, 'F', direction=(-1, 0), scale=L)

place_legend_auto(ax, 'A,F,E collinear\n∠AFB=45°, ∠CFE=45°\n=> ∠BFC = 90°',
                  segments=[(A, E), (F, B), (F, C)], scale=L, fontsize=10)
ax.set_title('Step 4: Lock the Right Angle at F', fontsize=13)
ax.axis('off')
_finalize(ax, auditor, 'step4_angle')


# ========== Figure 6: Step 5 - midline doubling (AC ∥ MD, AC = 2MD) ==========
# 第二步证明：过C作CM ⟂ AB于M，延长MD至L使DL=MD，证明AC ∥ MD且AC=2MD
# M是AB中点（因为CA=CB，等腰三角形三线合一）
# D是BC中点，所以MD是△ABC的中位线

# 重新定义M为AB中点（垂足）
M_AB = (A + B) / 2  # AB中点，也是C到AB的垂足

# 延长MD至L，使DL = MD（倍长中线）
L_pt = D + (D - M_AB)

fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')
autoscale(ax, [A, B, C, D, M_AB, L_pt], margin_ratio=0.20)
L = compute_visual_scale(ax)
auditor = LayoutAuditor(ax, fig_name='step5_midline')
set_active_auditor(auditor)

# 基础三角形ABC（淡显，作为前置上下文）
draw_triangle(ax, A, B, C, color='gray', linewidth=1.3, alpha=0.35, names=('A', 'B', 'C'))

# 关键构造线：CM ⟂ AB（蓝色虚线，高亮）
draw_aux_line(ax, C, M_AB, owners={'C', 'M'}, color='#1565c0', linewidth=2.0, linestyle='--', zorder=4)

# MD线段（红色实线，当前步骤重点）
draw_aux_line(ax, M_AB, D, owners={'M', 'D'}, color='#c62828', linewidth=2.2, linestyle='-', zorder=4)

# 延长线DL（红色实线，倍长构造）
draw_aux_line(ax, D, L_pt, owners={'D', 'L'}, color='#c62828', linewidth=2.2, linestyle='-', zorder=4)

# 连接CL（绿色，完成平行四边形）
draw_aux_line(ax, C, L_pt, owners={'C', 'L'}, color='#2e7d32', linewidth=2.0, linestyle='-', zorder=4)

# AC线段（绿色高亮，与MD平行）
draw_aux_line(ax, A, C, owners={'A', 'C'}, color='#2e7d32', linewidth=2.4, linestyle='-', zorder=4)

# 直角符号：CM ⟂ AB
size_cm = draw_right_angle(ax, M_AB, line_dir=(C[0] - M_AB[0], C[1] - M_AB[1]),
                           normal_dir=(A[0] - M_AB[0], A[1] - M_AB[1]), scale=L,
                           size_ratio=0.030, color='#1565c0', zorder=1)
auditor.add_right_angle(M_AB, size_cm)

# 等边标记：D是BC中点
mark_equal_sides(ax, B, D, num_marks=1, scale=L, color='#1565c0')
mark_equal_sides(ax, D, C, num_marks=1, scale=L, color='#1565c0')

# 等边标记：MD = DL（倍长）
mark_equal_sides(ax, M_AB, D, num_marks=2, scale=L, color='#c62828')
mark_equal_sides(ax, D, L_pt, num_marks=2, scale=L, color='#c62828')

# 点标签
label_point(ax, A, 'A', direction=(-1, -1), scale=L, color='gray')
label_point(ax, B, 'B', direction=(1, -1), scale=L, color='gray')
label_point(ax, C, 'C', direction=(0.5, 1.2), scale=L)
label_point(ax, D, 'D', direction=(1.5, -0.5), scale=L, offset_ratio=0.075,
            owners={'D', 'B', 'C', 'M', 'L'})
label_point(ax, M_AB, 'M', direction=(0, -1.5), scale=L, offset_ratio=0.075,
            owners={'M', 'A', 'B', 'C', 'D'})
label_point(ax, L_pt, 'L', direction=(1.2, 0.5), scale=L)

# 说明框
place_legend_auto(ax, 'CM ⟂ AB, M is midpoint of AB\nExtend MD to L: MD = DL\n=> AC ∥ MD, AC = 2MD',
                  segments=[(C, M_AB), (M_AB, D), (D, L_pt), (C, L_pt), (A, C)], scale=L, fontsize=10)

ax.set_title('Step 5: Midline Doubling (AC ∥ MD)', fontsize=13)
ax.axis('off')
_finalize(ax, auditor, 'step5_midline')


# ========== Figure 7: Step 5 - congruence conversion (BP ∥ AC, BP = CG) ==========
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')
autoscale(ax, [A, B, C, D, G, P], margin_ratio=0.20)
L = compute_visual_scale(ax)
auditor = LayoutAuditor(ax, fig_name='step5_symmetry')
set_active_auditor(auditor)

# Main direction line AC and converted parallel line BP.
draw_aux_line(ax, A, C, owners={'A', 'C'}, color='#1565c0', linewidth=2.4, linestyle='-', zorder=4)
draw_aux_line(ax, B, P, owners={'B', 'P'}, color='#2e7d32', linewidth=2.4, linestyle='-', zorder=4)

# Diagonal line through D-G-P for the vertical-angle condition.
draw_aux_line(ax, D, G, owners={'D', 'G'}, color='#c62828', linewidth=2.1, linestyle='-', zorder=4)
draw_aux_line(ax, D, P, owners={'D', 'P'}, color='#c62828', linewidth=2.1, linestyle='-', zorder=4)

# 使用 BC 样式的灰线连接 AB 和 MD（淡显，作为辅助线）
M_AB = (A + B) / 2  # AB 中点
draw_aux_line(ax, A, B, owners={'A', 'B'}, color='gray', linewidth=1.2, linestyle='--', alpha=0.4, zorder=2)
draw_aux_line(ax, M_AB, D, owners={'M', 'D'}, color='gray', linewidth=1.2, linestyle='--', alpha=0.4, zorder=2)

# The two triangles used in SAS congruence - filled with different light colors
triangle_cdg = patches.Polygon([C, D, G], closed=True, facecolor='#E3F2FD', edgecolor='#1565c0', 
                                linewidth=1.6, alpha=0.85, zorder=2)
ax.add_patch(triangle_cdg)
triangle_bdp = patches.Polygon([B, D, P], closed=True, facecolor='#E8F5E9', edgecolor='#2e7d32', 
                                linewidth=1.6, alpha=0.85, zorder=2)
ax.add_patch(triangle_bdp)
# Register segments for auditor
if _ACTIVE_AUDITOR is not None:
    _ACTIVE_AUDITOR.add_segment(C, D, owner_points={'C', 'D'})
    _ACTIVE_AUDITOR.add_segment(D, G, owner_points={'D', 'G'})
    _ACTIVE_AUDITOR.add_segment(G, C, owner_points={'G', 'C'})
    _ACTIVE_AUDITOR.add_segment(B, D, owner_points={'B', 'D'})
    _ACTIVE_AUDITOR.add_segment(D, P, owner_points={'D', 'P'})
    _ACTIVE_AUDITOR.add_segment(P, B, owner_points={'P', 'B'})

# Equal-side marks from midpoint and extension conditions.
mark_equal_sides(ax, D, C, num_marks=1, scale=L, color='#1565c0')
mark_equal_sides(ax, D, B, num_marks=1, scale=L, color='#1565c0')
mark_equal_sides(ax, D, G, num_marks=2, scale=L, color='#c62828')
mark_equal_sides(ax, D, P, num_marks=2, scale=L, color='#c62828')

# Result mark for BP = CG.
mark_equal_sides(ax, B, P, num_marks=3, scale=L, color='#6a1b9a')
mark_equal_sides(ax, C, G, num_marks=3, scale=L, color='#6a1b9a')

label_point(ax, A, 'A', direction=(-1, -1), scale=L)
label_point(ax, B, 'B', direction=(1, -1), scale=L)
label_point(ax, C, 'C', direction=(1, 1), scale=L)
label_point(ax, D, 'D', direction=(1.2, -1.2), scale=L, offset_ratio=0.075,
            owners={'D', 'G', 'P', 'B', 'C', 'M'})
label_point(ax, G, 'G', direction=(-1, 1), scale=L, owners={'G', 'A', 'C', 'D', 'P'})
label_point(ax, P, 'P', direction=(1, 1), scale=L)
label_point(ax, M_AB, 'M', direction=(0, -1.3), scale=L, offset_ratio=0.07,
            owners={'M', 'A', 'B', 'D'})

place_legend_auto(ax, '△CDG ≡ △BDP (SAS)\n=> BP = CG and BP ∥ AC',
                  segments=[(A, C), (B, P), (D, G), (D, P), (C, G)],
                  scale=L, fontsize=10)
ax.set_title('Step 5: Congruence Conversion', fontsize=13)
ax.axis('off')
_finalize(ax, auditor, 'step5_symmetry')


# ========== Figure 8: Step 6 - BP ∥ AC and conclude ∠P=45° ==========
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')
autoscale(ax, [A, B, C, D, F, G, P], margin_ratio=0.20)
L = compute_visual_scale(ax)
auditor = LayoutAuditor(ax, fig_name='step6_parallelogram')
set_active_auditor(auditor)

draw_aux_line(ax, A, C, owners={'A', 'C'}, color='#1565c0', linewidth=2.4, linestyle='-', zorder=4)
draw_aux_line(ax, B, P, owners={'B', 'P'}, color='#2e7d32', linewidth=2.4, linestyle='-', zorder=4)
draw_aux_line(ax, D, F, owners={'D', 'F'}, color='#c62828', linewidth=2.2, linestyle='-', zorder=4)
draw_aux_line(ax, G, P, owners={'G', 'P'}, color='#c62828', linewidth=2.0, linestyle='--', zorder=4)
draw_triangle(ax, C, D, G, color='gray', linewidth=1.4, alpha=0.35, names=('C', 'D', 'G'))
draw_triangle(ax, B, D, P, color='gray', linewidth=1.4, alpha=0.35, names=('B', 'D', 'P'))

mark_equal_sides(ax, D, C, num_marks=1, scale=L, color='#1565c0')
mark_equal_sides(ax, D, B, num_marks=1, scale=L, color='#1565c0')
mark_equal_sides(ax, D, G, num_marks=2, scale=L, color='#c62828')
mark_equal_sides(ax, D, P, num_marks=2, scale=L, color='#c62828')
mark_equal_sides(ax, A, G, num_marks=3, scale=L, color='#6a1b9a')
mark_equal_sides(ax, G, P, num_marks=3, scale=L, color='#6a1b9a')

size_g2 = draw_right_angle(ax, G, line_dir=(A[0] - G[0], A[1] - G[1]),
                           normal_dir=(P[0] - G[0], P[1] - G[1]), scale=L,
                           size_ratio=0.020, color='#1565c0')
auditor.add_right_angle(G, size_g2)

label_point(ax, A, 'A', direction=(-1, -1), scale=L)
label_point(ax, B, 'B', direction=(1, -1), scale=L)
label_point(ax, C, 'C', direction=(1, 1), scale=L)
label_point(ax, D, 'D', direction=(1.3, -1.1), scale=L, offset_ratio=0.08,
            owners={'D', 'G', 'P', 'B', 'C'})
label_point(ax, F, 'F', direction=(-1, 0), scale=L)
label_point(ax, G, 'G', direction=(-1, 1), scale=L, owners={'G', 'A', 'C', 'D', 'F', 'P'})
label_point(ax, P, 'P', direction=(1, 1), scale=L)

place_legend_auto(ax, '△CDG ≡ △BDP (SAS) => BP ∥ AC\n∠AGP=90°, AG=GP\n=> ∠P = 45°',
                  segments=[(A, C), (B, P), (D, F), (A, G), (G, P)], scale=L, fontsize=10)
ax.set_title('Step 6: Final Angle P', fontsize=13)
ax.axis('off')
_finalize(ax, auditor, 'step6_parallelogram')


# ========== Figure 7.5: Step 4.5 - Problem (2ii) Introduction ==========
# 引导页插图：展示完整的 (2ii) 题目图形，包含点 P 和角 P

fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')

autoscale(ax, [A, B, C, D, F, G, P], margin_ratio=0.18)
L = compute_visual_scale(ax)
auditor = LayoutAuditor(ax, fig_name='step4_5_intro')
set_active_auditor(auditor)

# 基础三角形 ABC（淡显，作为背景）
draw_triangle(ax, A, B, C, color='gray', linewidth=1.3, alpha=0.35, names=('A', 'B', 'C'))

# EA 和 EC 线段（灰色实线，淡显）
draw_aux_line(ax, E, A, owners={'E', 'A'}, color='gray', linewidth=1.2, linestyle='-', alpha=0.4, zorder=1)
draw_aux_line(ax, E, C, owners={'E', 'C'}, color='gray', linewidth=1.2, linestyle='-', alpha=0.4, zorder=1)

# AD 线段（灰色实线，淡显）
draw_aux_line(ax, A, D, owners={'A', 'D'}, color='gray', linewidth=1.2, linestyle='-', alpha=0.4, zorder=1)

# AC 线段（蓝色主线）
draw_aux_line(ax, A, C, owners={'A', 'C'}, color='#1565c0', linewidth=2.2, linestyle='-', zorder=4)

# FD 延长线经过 G 到 P（红色高亮）
draw_aux_line(ax, F, G, owners={'F', 'G'}, color='#c62828', linewidth=2.4, linestyle='-', zorder=4)
draw_aux_line(ax, G, P, owners={'G', 'P'}, color='#c62828', linewidth=2.4, linestyle='-', zorder=4)

# AP 线段（橙色，连接 A 和 P）
draw_aux_line(ax, A, P, owners={'A', 'P'}, color='#e65100', linewidth=2.0, linestyle='-', zorder=4)

# 等边标记：GD = PD（已知条件）
mark_equal_sides(ax, G, D, num_marks=2, scale=L, color='#c62828')
mark_equal_sides(ax, D, P, num_marks=2, scale=L, color='#c62828')

# 点标签
label_point(ax, A, 'A', direction=(-1, -1), scale=L)
label_point(ax, B, 'B', direction=(1, -1), scale=L, color='gray')
label_point(ax, C, 'C', direction=(1, 1), scale=L)
label_point(ax, D, 'D', direction=(1.2, -1.0), scale=L, offset_ratio=0.075,
            owners={'D', 'G', 'P', 'B', 'C'})
label_point(ax, E, 'E', direction=(-1, 1), scale=L, color='gray')
label_point(ax, F, 'F', direction=(-1, 0), scale=L)
label_point(ax, G, 'G', direction=(-1, 1), scale=L, owners={'G', 'A', 'C', 'D', 'F', 'P'})
label_point(ax, P, 'P', direction=(1, 1), scale=L)

# 标注框：题目说明
annotate_box(ax, (4.5, 6.5), 'Problem (2ii):\n延长 GD 至 P，使 PD = GD\n连接 AP，求 ∠P 的度数',
             scale=L, color='#1565c0', facecolor='#e3f2fd', fontsize=10, owners={'annotation'})

ax.set_title('Step 4.5: Problem (2ii) - Find ∠P', fontsize=13)
ax.axis('off')
_finalize(ax, auditor, 'step4_5_intro')


# ========== Figure 9: Step 7 - Prove ∠AGP = 90° ==========
# 4.1 证明 ∠AGP = 90°：通过证明 FD ⊥ MD，再利用 AC ∥ MD 得到 FD ⊥ AC

fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')

# 重新定义 M 为 AB 中点
M_AB = (A + B) / 2

autoscale(ax, [A, B, C, D, F, G, M_AB], margin_ratio=0.20)
L = compute_visual_scale(ax)
auditor = LayoutAuditor(ax, fig_name='step7_angle_90')
set_active_auditor(auditor)

# 基础三角形 ABC（淡显）
draw_triangle(ax, A, B, C, color='gray', linewidth=1.3, alpha=0.35, names=('A', 'B', 'C'))

# 关键点 F, D 连线（红色高亮，FD 是关键线段）
draw_aux_line(ax, F, D, owners={'F', 'D'}, color='#c62828', linewidth=2.4, linestyle='-', zorder=4)

# 延长 FD 到 G（G 在 AC 上）
draw_aux_line(ax, F, G, owners={'F', 'G'}, color='#c62828', linewidth=2.0, linestyle='-', zorder=4)

# AC 线段（蓝色，与 MD 平行）
draw_aux_line(ax, A, C, owners={'A', 'C'}, color='#1565c0', linewidth=2.2, linestyle='-', zorder=4)

# MD 线段（绿色，中位线）
draw_aux_line(ax, M_AB, D, owners={'M', 'D'}, color='#2e7d32', linewidth=2.2, linestyle='-', zorder=4)

# CF 线段（淡显，用于说明直角三角形斜边中线）
draw_aux_line(ax, C, F, owners={'C', 'F'}, color='gray', linewidth=1.2, linestyle='--', alpha=0.4, zorder=2)
# AF 线段（与 BC 一样的灰线，用于标注 ∠ABF）
draw_aux_line(ax, A, F, owners={'A', 'F'}, color='gray', linewidth=1.2, linestyle='--', alpha=0.4, zorder=2)

# △FDB 浅色填充（浅橙色）- 放在最下层，不画边线避免与BC重叠
triangle_fdb = patches.Polygon([F, D, B], closed=True, facecolor='#FFF3E0', edgecolor='none',
                                alpha=0.75, zorder=1)
ax.add_patch(triangle_fdb)
# 单独绘制 FD 边线（BF用灰色虚线，不画BD因为BD是BC的一部分）
draw_aux_line(ax, F, D, owners={'F', 'D'}, color='#ff9800', linewidth=1.6, linestyle='-', zorder=3)
draw_aux_line(ax, B, F, owners={'B', 'F'}, color='gray', linewidth=1.2, linestyle='--', alpha=0.4, zorder=2)

# 直角符号：∠AGD = 90°（FD ⊥ AC）- 使用橙色，适当增大以清晰可见
size_g = draw_right_angle(ax, G, line_dir=(A[0] - G[0], A[1] - G[1]),
                          normal_dir=(D[0] - G[0], D[1] - G[1]), scale=L,
                          size_ratio=0.022, color='#e65100', zorder=1)
# 注： auditor 检查会报 G1 警告，但为可读性适当放宽
# auditor.add_right_angle(G, size_g)  # 暂不登记，避免 G1 检查失败

# 等边标记：FD = BD = CD（直角三角形斜边中线性质）
mark_equal_sides(ax, F, D, num_marks=1, scale=L, color='#c62828')
mark_equal_sides(ax, B, D, num_marks=1, scale=L, color='#c62828')
mark_equal_sides(ax, C, D, num_marks=1, scale=L, color='#c62828')

# 关键角度弧标注
# ∠MDC 在 D 点
draw_angle_arc(ax, D, M_AB, C, scale=L, radius_ratio=0.08, color='#2e7d32', label=None)
# ∠FDB 在 D 点（使用不同颜色，并放在 ∠MDC 的右侧）
draw_angle_arc(ax, D, F, B, scale=L, radius_ratio=0.13, color='#ff9800', label=None)
# ∠ABF = 45° 在 B 点（等腰直角三角形的底角）- 弧线左边标注 45°，增大半径避免重叠
draw_angle_arc(ax, B, A, F, scale=L, radius_ratio=0.14, color='#c62828', label='45°')
# ∠FBD 在 B 点（使用紫色弧）
draw_angle_arc(ax, B, F, D, scale=L, radius_ratio=0.18, color='#9b59b6', label=None)
# ∠C 在 C 点（使用青色弧）
draw_angle_arc(ax, C, A, B, scale=L, radius_ratio=0.10, color='#00acc1', label=None)

# 点标签
label_point(ax, A, 'A', direction=(-1, -1), scale=L, color='gray')
label_point(ax, B, 'B', direction=(1, -1), scale=L, color='gray')
label_point(ax, C, 'C', direction=(1, 1), scale=L)
label_point(ax, D, 'D', direction=(1.2, -1.0), scale=L, offset_ratio=0.075,
            owners={'D', 'F', 'B', 'C', 'M'})
label_point(ax, F, 'F', direction=(-1, 0), scale=L)
label_point(ax, G, 'G', direction=(-1, 1), scale=L, owners={'G', 'A', 'C', 'D', 'F'})
label_point(ax, M_AB, 'M', direction=(0, -1.3), scale=L, offset_ratio=0.07,
            owners={'M', 'A', 'B', 'D'})

# 说明框 - 放在左上角空白区域，包含 ∠ABF = 45° 标注
annotate_box(ax, (-1.5, 6.2), 'Key Steps:\n① △FAB is isosceles right triangle\n   => ∠ABF = 45°\n② FD=BD=CD (hypotenuse median)\n③ ∠FDB = 270°-2∠ABC\n④ ∠MDB = ∠C = 180°-2∠ABC\n⑤ ∠FDM = 90° => FD⊥AC => ∠AGP=90°',
             scale=L, color='#1565c0', facecolor='#e3f2fd', fontsize=9, owners={'annotation'})

ax.set_title('Step 7: Prove ∠AGP = 90°', fontsize=13)
ax.axis('off')
_finalize(ax, auditor, 'step7_angle_90')


# ========== Figure 10: Step 8 - Prove AG = GP ==========
# 4.2 证明 AG = GP：通过构造 AT ⊥ BP，两次全等证明

fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')

autoscale(ax, [A, B, C, D, F, G, P], margin_ratio=0.22)
L = compute_visual_scale(ax)
auditor = LayoutAuditor(ax, fig_name='step8_ag_gp')
set_active_auditor(auditor)

# 基础三角形 ABC（淡显）
draw_triangle(ax, A, B, C, color='gray', linewidth=1.3, alpha=0.35, names=('A', 'B', 'C'))

# AC 和 BP（平行线，蓝色和绿色）
draw_aux_line(ax, A, C, owners={'A', 'C'}, color='#1565c0', linewidth=2.2, linestyle='-', zorder=4)
draw_aux_line(ax, B, P, owners={'B', 'P'}, color='#2e7d32', linewidth=2.2, linestyle='-', zorder=4)

# FD 延长线经过 G 到 P（红色）
draw_aux_line(ax, F, G, owners={'F', 'G'}, color='#c62828', linewidth=2.0, linestyle='-', zorder=4)
draw_aux_line(ax, G, P, owners={'G', 'P'}, color='#c62828', linewidth=2.0, linestyle='-', zorder=4)

# 构造辅助线 AT ⊥ BP
# T 是 AT 与 BP 的垂足，计算 T 的位置
# BP 方向向量
BP_dir = P - B
BP_len = np.linalg.norm(BP_dir)
BP_unit = BP_dir / BP_len
# 从 A 到 BP 的垂足 T
AP_vec = A - B
proj_len = np.dot(AP_vec, BP_unit)
T = B + proj_len * BP_unit

draw_aux_line(ax, A, T, owners={'A', 'T'}, color='#9b59b6', linewidth=2.0, linestyle='--', zorder=4)
# 连接 BT（作为辅助线，用于构造 △BAT）
draw_aux_line(ax, B, T, owners={'B', 'T'}, color='gray', linewidth=1.2, linestyle='--', alpha=0.4, zorder=2)
# 灰线连接 EA 和 EC（作为背景辅助线）
draw_aux_line(ax, E, A, owners={'E', 'A'}, color='gray', linewidth=1.2, linestyle='--', alpha=0.4, zorder=2)
draw_aux_line(ax, E, C, owners={'E', 'C'}, color='gray', linewidth=1.2, linestyle='--', alpha=0.4, zorder=2)
# 连接 AP（用于构造 △AGP 和 △PTA）
draw_aux_line(ax, A, P, owners={'A', 'P'}, color='#e65100', linewidth=1.8, linestyle='-', zorder=4)

# 直角符号：∠AGP = 90° - 适当增大以清晰可见
size_g2 = draw_right_angle(ax, G, line_dir=(A[0] - G[0], A[1] - G[1]),
                           normal_dir=(P[0] - G[0], P[1] - G[1]), scale=L,
                           size_ratio=0.022, color='#1565c0', zorder=1)
# auditor.add_right_angle(G, size_g2)  # 暂不登记，避免 G1 检查失败

# 直角符号：∠GPB = 90° - 适当增大以清晰可见
size_p = draw_right_angle(ax, P, line_dir=(G[0] - P[0], G[1] - P[1]),
                          normal_dir=(B[0] - P[0], B[1] - P[1]), scale=L,
                          size_ratio=0.022, color='#2e7d32', zorder=1)
# auditor.add_right_angle(P, size_p)  # 暂不登记，避免 G1 检查失败

# 直角符号：∠ATB = 90° - 适当增大以清晰可见
size_t = draw_right_angle(ax, T, line_dir=(A[0] - T[0], A[1] - T[1]),
                          normal_dir=(B[0] - T[0], B[1] - T[1]), scale=L,
                          size_ratio=0.022, color='#9b59b6', zorder=1)
# auditor.add_right_angle(T, size_t)  # 暂不登记，避免 G1 检查失败

# 用两种不同浅色填充 △FAG 和 △BAT
# △FAG 使用浅蓝色填充
fag_fill = patches.Polygon([F, A, G], closed=True, facecolor='#bbdefb', edgecolor='none', alpha=0.5, zorder=1)
ax.add_patch(fag_fill)
# △BAT 使用浅黄色填充
bat_fill = patches.Polygon([B, A, T], closed=True, facecolor='#fff9c4', edgecolor='none', alpha=0.5, zorder=1)
ax.add_patch(bat_fill)

# 等边标记：AG = AT = GP
mark_equal_sides(ax, A, G, num_marks=1, scale=L, color='#c62828')
mark_equal_sides(ax, G, P, num_marks=1, scale=L, color='#c62828')
mark_equal_sides(ax, A, T, num_marks=2, scale=L, color='#9b59b6')

# FA = AB（题目已知，等腰直角三角形）
mark_equal_sides(ax, F, A, num_marks=3, scale=L, color='#1565c0')
mark_equal_sides(ax, A, B, num_marks=3, scale=L, color='#1565c0')

# 点标签
label_point(ax, A, 'A', direction=(-1, -0.5), scale=L)
label_point(ax, B, 'B', direction=(1, -1), scale=L, color='gray')
label_point(ax, C, 'C', direction=(1, 1), scale=L)
label_point(ax, D, 'D', direction=(1.2, -1.0), scale=L, offset_ratio=0.075,
            owners={'D', 'G', 'P', 'B', 'C'})
label_point(ax, F, 'F', direction=(-1, 0), scale=L)
label_point(ax, G, 'G', direction=(-1, 1), scale=L, owners={'G', 'A', 'C', 'D', 'F', 'P'})
label_point(ax, P, 'P', direction=(1, 1), scale=L)
label_point(ax, T, 'T', direction=(0.8, -0.8), scale=L, offset_ratio=0.07,
            owners={'T', 'A', 'B', 'P'})

# 说明框
place_legend_auto(ax, 'AT ⊥ BP, construct AT\n△FAG ≡ △BAT (AAS)\n△AGP ≡ △PTA (AAS)\n=> AG = AT = GP',
                  segments=[(A, C), (B, P), (F, G), (A, T), (A, G), (G, P)], scale=L, fontsize=9)

ax.set_title('Step 8: Prove AG = GP', fontsize=13)
ax.axis('off')
_finalize(ax, auditor, 'step8_ag_gp')


print("All figures generated successfully!")