"""
Problem 010: Angle bisector and perpendicular line in triangle

G-标准合规重写：
- 所有视觉元素按 L_ref 归一（G1–G5）
- 每图调用 LayoutAuditor.check()（G11）
- 步骤元素隔离：只强调当前步骤对象，前置上下文 alpha ≤ 0.35（G10）
- 密集点群标签方向夹角 ≥ 90°（G7）
- zorder 分层遵循 G8
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

_TEXT_BOX = dict(facecolor='white', edgecolor='none', alpha=0.78, pad=0.12)


# ========== G-标准核心工具 ==========
def compute_visual_scale(ax):
    """L_ref = min(xrange, yrange)。"""
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
    """G-标准自检器（自动登记 + bbox 感知）。

    用法：
        auditor = LayoutAuditor(ax, 'step1')
        set_active_auditor(auditor)
        auditor.add_segment(A, B, owner_points=('A', 'B'))
        auditor.add_right_angle(...)
        # label_point / place_segment_label / annotate_box 自动登记文字
        set_active_auditor(None)
        violations = auditor.check()   # 空 = PASS
    """

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
        self.texts.append(dict(kind=kind, name=name, artist=artist,
                               anchor=None if anchor is None else np.asarray(anchor, float),
                               owners=set(owners), is_box=is_box,
                               owner_seg=owner_seg))

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
        """返回违规列表（空 = PASS）。MUST 修复至空再保存。"""
        L = self.scale
        delta_safe = 0.025 * L
        v = []
        # 确保 renderer 就绪
        self.ax.figure.canvas.draw()

        # G0: auditor 构造时机 / 激活窗口正确性 —— MUST 在绘图**之前**创建并 set_active
        ax_texts = [t for t in self.ax.texts
                    if (t.get_text() or '').strip()
                    and (t.get_alpha() is None or t.get_alpha() > 0.05)]
        if len(ax_texts) > 0 and len(self.texts) == 0:
            v.append(
                f'G0 LayoutAuditor created/activated AFTER drawing: ax has '
                f'{len(ax_texts)} text artists but auditor registered 0. '
                f'Pattern MUST be: create auditor -> set_active_auditor(auditor) '
                f'-> autoscale + draw_* + label_* -> set_active_auditor(None) -> check().')
            return v  # 早退：其它检查已不可信
        if len(ax_texts) > 0 and len(self.texts) < max(1, len(ax_texts) // 2):
            v.append(
                f'G0 LayoutAuditor partial registration: ax has {len(ax_texts)} '
                f'visible text artists but auditor registered only {len(self.texts)}. '
                f'set_active_auditor(auditor) MUST wrap ALL drawing calls.')

        # G1: 直角符号尺寸
        for H, size in self.right_angles:
            if size > 0.05 * L:
                v.append(f'G1 right_angle@{np.round(H,3).tolist()}: size={size:.3f} > 0.05*L_ref({0.05*L:.3f})')
            for a, b, _ in self.segments:
                seg_len = float(np.linalg.norm(b - a))
                d = _seg_point_distance(H, a, b)
                if d < 0.5 * size and seg_len > 0 and size > 0.08 * seg_len:
                    v.append(f'G1 right_angle@{np.round(H,3).tolist()}: size={size:.3f} > 8% of nearby seg len={seg_len:.3f}')

        # 预计算所有文字矩形
        rects = []
        for t in self.texts:
            try:
                rects.append(self._text_rect(t['artist']))
            except Exception:
                rects.append(None)

        # G6: 文字 ↔ 非自身关联线段（bbox vs segment）
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

        # G5b: 段标签 MUST 贴近其主线段（避免漂离、归属不清）
        max_own = 0.12 * L
        for t, r in zip(self.texts, rects):
            if r is None or t.get('owner_seg') is None:
                continue
            a, b = t['owner_seg']
            d = _seg_rect_distance(a, b, r)
            if d > max_own:
                label = t['name'] or t['kind']
                v.append(f'G5b text "{label}" too far from its own segment: d={d:.3f} > {max_own:.3f} (ambiguous which segment it labels)')

        # G6b: 文字 ↔ 文字（bbox 矩形相交）
        for i in range(len(self.texts)):
            for j in range(i + 1, len(self.texts)):
                ri, rj = rects[i], rects[j]
                if ri is None or rj is None:
                    continue
                if _rects_overlap(ri, rj, pad=0.3 * delta_safe):
                    ni = self.texts[i]['name'] or self.texts[i]['kind']
                    nj = self.texts[j]['name'] or self.texts[j]['kind']
                    v.append(f'G6b text "{ni}" and "{nj}" bbox overlap')

        # G12: 说明框 ↔ 任意几何线段
        for t, r in zip(self.texts, rects):
            if r is None or not t['is_box']:
                continue
            for a, b, owners in self.segments:
                d = _seg_rect_distance(a, b, r)
                if d < delta_safe:
                    label = t['name'] or 'annotation-box'
                    v.append(f'G12 annotation box "{label}" overlaps geometry segment {sorted(owners)} (d={d:.3f}); move to empty area')

        # G7: 点群密集时标签方向夹角 ≥ 90°
        names = list(self.points.keys())
        anchor_of = {t['name']: t['anchor'] for t in self.texts
                     if t['kind'] == 'point' and t['anchor'] is not None}
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

        # G7b: 极密点群（< 5%·L_ref）—— 即便方向分散也无法清晰双标
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

        # G14: 直角符号方框 ↔ 其他已标注点的标记/标签
        for H, size in self.right_angles:
            rH = (H[0] - size, H[1] - size, H[0] + size, H[1] + size)
            for name, P in self.points.items():
                if float(np.linalg.norm(P - H)) < 0.5 * size:
                    continue  # 自身垂足点
                t = next((t for t in self.texts if t['kind'] == 'point' and t['name'] == name), None)
                if t is None:
                    continue
                try:
                    rP = self._text_rect(t['artist'])
                except Exception:
                    continue
                if _rects_overlap(rH, rP, pad=0.5 * size):
                    v.append(f'G14 right_angle at H={np.round(H,2).tolist()} overlaps labeled point "{name}" at {np.round(P,2).tolist()}')
                # 还检查直角符号方框是否套住点标记（dot marker）
                if rH[0] < P[0] < rH[2] and rH[1] < P[1] < rH[3]:
                    v.append(f'G14 right_angle bbox at H={np.round(H,2).tolist()} encloses point "{name}" at {np.round(P,2).tolist()}')

        return v


# ---- 活动审计器 ----
_ACTIVE_AUDITOR = None


def set_active_auditor(auditor):
    global _ACTIVE_AUDITOR
    _ACTIVE_AUDITOR = auditor


def _auto_register(artist, kind='label', name='', anchor=None, owners=(), is_box=False, owner_seg=None):
    if _ACTIVE_AUDITOR is not None:
        _ACTIVE_AUDITOR.register_text(artist, kind=kind, name=name,
                                      anchor=anchor, owners=owners, is_box=is_box,
                                      owner_seg=owner_seg)


# ========== 绘图工具函数（全部按 L_ref 归一） ==========
def draw_triangle(ax, A, B, C, color='black', linewidth=1.8, alpha=1.0,
                  names=None):
    """绘制三角形 ABC 的三条边。

    names: 若传入 ('A','B','C') 且有活动 auditor，会自动登记三条边
           （owner_points 正确），免去手动 add_segment。
    """
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
    """辅助线（AO、垂线 l 等）并自动登记为几何线段（原则六补充）。"""
    p1, p2 = np.asarray(p1, float), np.asarray(p2, float)
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linewidth=linewidth,
            linestyle=linestyle, zorder=zorder, alpha=alpha)
    if _ACTIVE_AUDITOR is not None:
        _ACTIVE_AUDITOR.add_segment(p1, p2, owner_points=set(owners))


def label_point(ax, P, name, direction=(1.0, 1.0), scale=1.0,
                offset_ratio=0.055, fontsize=13, color='black',
                marker_zorder=5, text_zorder=6, alpha=1.0, fontweight='bold',
                owners=None):
    """绘制点和点名。文字自动登记到活动 auditor（G11）。

    owners: 该点归属的名集合（默认 {name}），用于避免误报"标签压自身关联边"。
    """
    d = np.array(direction, dtype=float)
    n = np.linalg.norm(d)
    if n < 1e-9:
        d = np.array([0.0, 1.0])
        n = 1.0
    d = d / n * (scale * offset_ratio)
    anchor = np.array([P[0] + d[0], P[1] + d[1]])
    ax.plot(P[0], P[1], 'o', color=color, markersize=4,
            zorder=marker_zorder, alpha=alpha)
    art = ax.text(anchor[0], anchor[1], name,
                  ha='center', va='center',
                  fontsize=fontsize, fontweight=fontweight, color=color,
                  bbox=_TEXT_BOX, zorder=text_zorder, alpha=alpha)
    if _ACTIVE_AUDITOR is not None:
        _ACTIVE_AUDITOR.add_point_anchor(name, P)
        _auto_register(art, kind='point', name=name, anchor=anchor,
                       owners=(owners if owners is not None else {name}))
    return anchor


def place_segment_label(ax, p1, p2, text, color, scale=1.0,
                        offset_ratio=0.055, fontsize=12, side=None,
                        owners=None):
    """沿线段法向放置标签，带 owner_seg 供 G5b 检查。"""
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
                  fontweight='bold', bbox=_TEXT_BOX, zorder=6, alpha=1.0)
    _auto_register(art, kind='seglabel', name=text,
                   owners=(owners if owners is not None else set()),
                   owner_seg=(p1, p2))
    return art


def draw_right_angle(ax, H, line_dir, normal_dir, scale=1.0,
                     size_ratio=0.035, color='#1565c0', zorder=1, alpha=1.0):
    size = scale * size_ratio
    u = np.asarray(line_dir, float)
    u = u / (np.linalg.norm(u) + 1e-9)
    v = np.asarray(normal_dir, float)
    v = v / (np.linalg.norm(v) + 1e-9)
    p1 = H - size * v
    p2 = p1 + size * u
    p3 = H + size * u
    ax.plot([p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]],
            color=color, linewidth=1.2, zorder=zorder, alpha=alpha)
    return size


def draw_ao(ax, A, D, H, ao_dir, scale=1.0,
            color='#9b59b6', linewidth=1.6,
            cap_ratio=0.075, dash_zorder=4, cap_zorder=5, alpha=1.0,
            owners=None):
    """画 AO 虚线，并在 H 附近补一小段实线，避免虚线空档造成视觉断裂。
    自动登记为几何线段（owners 默认 {'A','D'}）。
    """
    AO_end = A + 1.05 * (D - A)
    ax.plot([A[0], AO_end[0]], [A[1], AO_end[1]],
            color=color, linewidth=linewidth, linestyle='--',
            zorder=dash_zorder, alpha=alpha)
    cap = scale * cap_ratio
    p_start = H - cap * ao_dir
    p_end = H + cap * ao_dir
    ax.plot([p_start[0], p_end[0]], [p_start[1], p_end[1]],
            color=color, linewidth=linewidth + 0.2,
            zorder=cap_zorder, alpha=min(alpha + 0.15, 1.0))
    if _ACTIVE_AUDITOR is not None:
        _ACTIVE_AUDITOR.add_segment(A, AO_end,
                                    owner_points=(owners if owners is not None else {'A', 'D'}))


def draw_angle_arc(ax, vertex, p1, p2, scale=1.0,
                   radius_ratio=0.10, color='blue', label=None,
                   label_pad_ratio=0.045, alpha=1.0):
    radius = scale * radius_ratio
    a1 = np.degrees(np.arctan2(p1[1] - vertex[1], p1[0] - vertex[0]))
    a2 = np.degrees(np.arctan2(p2[1] - vertex[1], p2[0] - vertex[0]))
    if a2 < a1:
        a1, a2 = a2, a1
    if a2 - a1 > 180:
        a1, a2 = a2, a1 + 360
    arc = patches.Arc(vertex, 2 * radius, 2 * radius,
                      angle=0, theta1=a1, theta2=a2,
                      color=color, linewidth=1.5, alpha=alpha)
    ax.add_patch(arc)
    if label:
        mid = np.radians((a1 + a2) / 2)
        r = radius + scale * label_pad_ratio
        art = ax.text(vertex[0] + r * np.cos(mid),
                      vertex[1] + r * np.sin(mid),
                      label, ha='center', va='center',
                      fontsize=10, color=color, bbox=_TEXT_BOX, zorder=6, alpha=alpha)
        _auto_register(art, kind='anglelabel', name=label)


def mark_equal_sides(ax, p1, p2, num_marks=1, scale=1.0,
                     tick_ratio=0.040, gap_ratio=0.025, color='red', alpha=1.0):
    p1, p2 = np.asarray(p1, float), np.asarray(p2, float)
    mid = (p1 + p2) / 2
    d = p2 - p1
    L = np.hypot(*d)
    if L < 1e-9:
        return
    base_tick = scale * tick_ratio
    if num_marks >= 2:
        base_tick = scale * 0.030
    tick = min(base_tick, 0.12 * L / 2)
    gap = scale * gap_ratio
    along = d / L
    perp = np.array([-d[1], d[0]]) / L
    for i in range(num_marks):
        offset = (i - (num_marks - 1) / 2) * gap
        c = mid + offset * along
        ax.plot([c[0] - tick * perp[0], c[0] + tick * perp[0]],
                [c[1] - tick * perp[1], c[1] + tick * perp[1]],
                color=color, linewidth=2, zorder=3, alpha=alpha)


def autoscale(ax, points, margin_ratio=0.12):
    pts = np.array(points)
    xr = pts[:, 0].max() - pts[:, 0].min()
    yr = pts[:, 1].max() - pts[:, 1].min()
    mx = max(xr, yr) * margin_ratio
    ax.set_xlim(pts[:, 0].min() - mx, pts[:, 0].max() + mx)
    ax.set_ylim(pts[:, 1].min() - mx, pts[:, 1].max() + mx)


def annotate_box(ax, xy, text, scale=1.0, color='#1565c0',
                 facecolor='#e3f2fd', fontsize=12, owners=None):
    """画一个说明框（ASA 框、公式框等）并登记为 is_box=True（G12）。"""
    art = ax.text(xy[0], xy[1], text, ha='center', va='center',
                  fontsize=fontsize, fontweight='bold', color=color,
                  bbox=dict(facecolor=facecolor, edgecolor=color, alpha=0.9, pad=6),
                  zorder=7)
    _auto_register(art, kind='box', name=text.split('\n')[0][:16],
                   owners=(owners if owners is not None else set()), is_box=True)
    return art


def place_legend_auto(ax, text, segments, scale=1.0, color='#1565c0',
                      facecolor='#e3f2fd', fontsize=12):
    """在四个角中选择"离所有几何线段最远"的位置放说明框（G12）。"""
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


# ========== 几何计算 ==========
# 三角形 ABC: ∠B=β=30°, ∠C=2β=60°, ∠A=90°
# A=(0,0), B=(√3,0), C=(0,1)
s3 = np.sqrt(3)
A = np.array([0.0, 0.0])
B = np.array([s3, 0.0])
C = np.array([0.0, 1.0])

# AO 方向（角平分线，y=x）
ao_dir = np.array([1.0, 1.0]) / np.sqrt(2)

# D = AO ∩ BC
tD = s3 / (1 + s3)
D = np.array([s3 * (1 - tD), tD])

# Part 1: l 经过 C
H1 = np.array([0.5, 0.5])
N1 = np.array([1.0, 0.0])

# Part 2: M 为 BC 中点
M2 = np.array([s3 / 2, 0.5])
h2x = s3 / 4 + 0.25
H2 = np.array([h2x, h2x])
n2x = s3 / 2 + 0.5
N2 = np.array([n2x, 0.0])
E2 = np.array([0.0, n2x])

# 辅助延长线
ao_end = A + 1.25 * (D - A)
l1_start = N1 - 0.5 * (C - N1)
l1_end = C + 0.3 * (C - N1)
l2_dir_n = E2 - N2
l2_start = N2 - 0.25 * l2_dir_n
l2_end = E2 + 0.25 * l2_dir_n

# 构造点 P: AP = AC
P = np.array([1.0, 0.0])

# B' 和 C'（B 和 C 在 AO 上的投影）
# AO 方向单位向量 u = (1/√2, 1/√2)
# B 投影到 AO: t = B·u = s3/√2, B' = t*u = (s3/2, s3/2)
# C 投影到 AO: t = C·u = 1/√2, C' = (1/2, 1/2)
Bp = np.array([s3 / 2, s3 / 2])
Cp = np.array([0.5, 0.5])


def _save(fig, ax, name, auditor=None):
    """统一保存流程：自检（FAIL 则中断）+ savefig。"""
    if auditor is not None:
        violations = auditor.check()
        if violations:
            msg = '\n'.join(f'  - {v}' for v in violations)
            raise AssertionError(f'[{name}] LayoutAuditor violations (MUST fix before save):\n{msg}')
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(_BASE_DIR, name), dpi=150, bbox_inches='tight')
    plt.close()


# ================================================================
# Figure 0: 原题图（三角形 + AO + D + 角标记）
# G10: 只显示本题信息，不出现 l / H / N / E / M
# ================================================================
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')

autoscale(ax, [A, B, C, ao_end], margin_ratio=0.18)
L = compute_visual_scale(ax)

auditor = LayoutAuditor(ax, 'step0_problem_original')
set_active_auditor(auditor)

draw_triangle(ax, A, B, C, linewidth=2.0, names=('A','B','C'))
# AO 虚线（draw_aux_line 自动登记）
draw_aux_line(ax, A, ao_end, owners=('A', 'D'), color='#9b59b6',
              linewidth=1.6, linestyle='--', zorder=4)

lr_beta = 0.12  # G2 默认
lr_2beta = 0.18  # 同顶点 C 的两个角，半径差 ≥ 0.05
# ∠A = ? at A（手动放标签远离 AO 虚线）
draw_angle_arc(ax, A, B, C, scale=L, radius_ratio=0.10,
               color='#2196f3')
# 手动放置 ? 标签远离 AO 方向（45° 即 AO 线），偏移到弧外侧偏下
mid_rad = np.radians(45)
r_label = L * (0.10 + 0.060)
art_q = ax.text(A[0] + r_label * np.cos(mid_rad - 0.3),
                A[1] + r_label * np.sin(mid_rad - 0.3),
                u'?', ha='center', va='center',
                fontsize=11, color='#2196f3', bbox=_TEXT_BOX, zorder=6)
_auto_register(art_q, kind='anglelabel', name='?')
# ∠ACB = 2β at C
draw_angle_arc(ax, C, B, A, scale=L, radius_ratio=lr_2beta,
               color='#e67e22', label=u'2\u03b2')
# ∠B = β at B（用大半径避免标签压 AB/BC）
draw_angle_arc(ax, B, A, C, scale=L, radius_ratio=0.20,
               color='#4caf50', label=u'\u03b2')

# 顶点标签（label_point 自动登记文字）
centroid = (A + B + C) / 3
lf_A = label_point(ax, A, 'A', direction=(A - centroid), scale=L, offset_ratio=0.065, fontsize=14)
lf_B = label_point(ax, B, 'B', direction=(B - centroid), scale=L, offset_ratio=0.065, fontsize=14)
lf_C = label_point(ax, C, 'C', direction=(C - centroid), scale=L, offset_ratio=0.065, fontsize=14)

# D 点标注（D 在 BC 上，owners 包含 B,C 避免 G6 误报）
lf_D = label_point(ax, D, 'D', direction=(+1.5, -0.2), scale=L, fontsize=13,
                   owners={'D', 'B', 'C'})

# 注释框（G12: 自动放到空白区）
place_legend_auto(ax, 'AO bisects \u2220A     \u2220ACB = 2\u2220B',
                  segments=[(A, B), (B, C), (C, A)],
                  scale=L, color='#555', facecolor='#f0f0f0', fontsize=11)

# BC 额外登记 D 为 owner（D 在线 BC 上，避免误报）
auditor.add_segment(B, C, owner_points={'B', 'C', 'D'})

set_active_auditor(None)
ax.set_title('Fig 1: Original Configuration', fontsize=14)

_save(fig, ax, 'step0_problem_original.png', auditor)


# ================================================================
# Figure 1: 基本配置（三角形 + AO + l + 所有点 + 角标记）
# ================================================================
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')

autoscale(ax, [A, B, C, N2, E2, M2, ao_end, l2_end], margin_ratio=0.15)
L = compute_visual_scale(ax)

auditor = LayoutAuditor(ax, 'step1_basic')
set_active_auditor(auditor)

draw_triangle(ax, A, B, C, names=('A','B','C'))
# AO
draw_aux_line(ax, A, ao_end, owners=('A', 'D'), color='#9b59b6',
              linewidth=1.6, linestyle='--', zorder=4)
# l 线（用 part2 的通用情况）
draw_aux_line(ax, l2_start, l2_end, owners=('N', 'E'), color='#e74c3c',
              linewidth=1.6, linestyle='-', zorder=3)

# 直角符号 at H2
sz = draw_right_angle(ax, H2, (1, 1), (-1, 1), scale=L, size_ratio=0.025)

# 所有点标签（密集点群：方向夹角 ≥ 90°）
lf_A = label_point(ax, A, 'A', direction=(-0.5, -1.0), scale=L, fontsize=13)
lf_B = label_point(ax, B, 'B', direction=(+1.0, -0.5), scale=L, fontsize=13)
lf_C = label_point(ax, C, 'C', direction=(-0.8, +1.0), scale=L, fontsize=13)
# D 与 H 距离过近（<0.05·L_ref），不标注 D 避免 G7b/G14
lf_H = label_point(ax, H2, 'H', direction=(-2.0, +2.0), scale=L, fontsize=12,
                   owners={'H', 'N', 'E', 'B', 'C'})
lf_N = label_point(ax, N2, 'N', direction=(+0.5, -1.0), scale=L, fontsize=12)
lf_E = label_point(ax, E2, 'E', direction=(-1.0, -0.2), scale=L, fontsize=12)
lf_M = label_point(ax, M2, 'M', direction=(+0.0, -1.0), scale=L, fontsize=12,
                   owners={'M', 'B', 'C', 'N', 'E'})

# 角弧
draw_angle_arc(ax, A, B, C, scale=L, radius_ratio=0.10,
               color='#2196f3')
# 手动放置 ? 标签远离 AO 方向（45° 即 AO 线）
mid_rad = np.radians(45)
r_q = L * (0.10 + 0.060)
art_q2 = ax.text(A[0] + r_q * np.cos(mid_rad - 0.3),
                 A[1] + r_q * np.sin(mid_rad - 0.3),
                 u'?', ha='center', va='center',
                 fontsize=11, color='#2196f3', bbox=_TEXT_BOX, zorder=6)
_auto_register(art_q2, kind='anglelabel', name='?')
draw_angle_arc(ax, C, B, A, scale=L, radius_ratio=0.18,
               color='#e67e22', label=u'2\u03b2')
draw_angle_arc(ax, B, A, C, scale=L, radius_ratio=0.30,
               color='#4caf50', label=u'\u03b2')

auditor.add_segment(B, C, owner_points={'B', 'C', 'D'})
auditor.add_right_angle(H2, sz)

set_active_auditor(None)
ax.set_title('Step 1: Lines and Points (Basic Configuration)', fontsize=14)

_save(fig, ax, 'step1_lines_and_points.png', auditor)


# ================================================================
# Figure 2: Part (1) — l 经过 C
# G10: 强调 l 过 C（M=C），淡出 E
# ================================================================
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')

autoscale(ax, [A, B, C, N1, H1, ao_end, l1_end], margin_ratio=0.15)
L = compute_visual_scale(ax)

auditor = LayoutAuditor(ax, 'step1_part1')
set_active_auditor(auditor)

draw_triangle(ax, A, B, C, names=('A','B','C'))
# AO
draw_aux_line(ax, A, ao_end, owners=('A', 'D'), color='#9b59b6',
              linewidth=1.6, linestyle='--', zorder=4)
# l（经过 C）
draw_aux_line(ax, l1_start, l1_end, owners=('N', 'C'), color='#e74c3c',
              linewidth=2.0, linestyle='-', zorder=3)

sz = draw_right_angle(ax, H1, (1, 1), (-1, 1), scale=L, size_ratio=0.035)

# 全 alpha：相关点
lf_A = label_point(ax, A, 'A', direction=(-0.5, -1.0), scale=L, fontsize=13)
lf_B = label_point(ax, B, 'B', direction=(+1.0, -0.5), scale=L, fontsize=13)
lf_C = label_point(ax, C, 'C(M)', direction=(-0.8, +1.2), scale=L, fontsize=12,
                   owners={'C', 'A', 'B'})
lf_H = label_point(ax, H1, 'H', direction=(+1.2, -1.0), scale=L, fontsize=12,
                   owners={'H', 'C', 'N'})
lf_N = label_point(ax, N1, 'N', direction=(0.0, -1.0), scale=L, fontsize=12)

# 等边标记 AN = AC
mark_equal_sides(ax, A, C, num_marks=1, scale=L, color='red')
mark_equal_sides(ax, A, N1, num_marks=1, scale=L, color='red')

# 角弧
draw_angle_arc(ax, B, A, C, scale=L, radius_ratio=0.14,
               color='#4caf50', label=u'\u03b2')
draw_angle_arc(ax, C, B, A, scale=L, radius_ratio=0.20,
               color='#e67e22', label=u'2\u03b2')
# ∠NMB = ∠NCB at C (CN=CH1 direction vs CB) — 手动放置标签避免落在 AO 线上
draw_angle_arc(ax, C, H1, B, scale=L, radius_ratio=0.28,
               color='#f44336')
# 手动放置 β/2 标签，偏移避开 AO 线（mid angle -37.5°，偏移 +0.35 rad）
mid_b2 = np.radians(-37.5)
r_b2 = L * (0.28 + 0.060)
art_b2 = ax.text(C[0] + r_b2 * np.cos(mid_b2 + 0.35),
                 C[1] + r_b2 * np.sin(mid_b2 + 0.35),
                 u'\u03b2/2', ha='center', va='center',
                 fontsize=10, color='#f44336', bbox=_TEXT_BOX, zorder=6)
_auto_register(art_b2, kind='anglelabel', name=u'\u03b2/2')

auditor.add_segment(B, C, owner_points={'B', 'C', 'D'})
auditor.add_right_angle(H1, sz)

set_active_auditor(None)
ax.set_title('Step 2: l passes through C (Part 1)', fontsize=14)

_save(fig, ax, 'step1_part1_l_through_C.png', auditor)


# ================================================================
# Figure 3: Part (1) — 全等三角形 ASA 证明
# G10: 强调 △AHC 和 △AHN，淡出 B, C
# ================================================================
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')

autoscale(ax, [A, B, C, N1, H1, ao_end, l1_end], margin_ratio=0.15)
L = compute_visual_scale(ax)

auditor = LayoutAuditor(ax, 'step2_part1_congruent')
set_active_auditor(auditor)

# 背景三角形淡显（无 names = 不登记线段）
draw_triangle(ax, A, B, C, alpha=0.30)

# AO 淡显
draw_aux_line(ax, A, ao_end, owners=('A', 'D'), color='#9b59b6',
              linewidth=1.2, linestyle='--', zorder=4, alpha=0.30)

# l 过 C
draw_aux_line(ax, l1_start, l1_end, owners=('N', 'C'), color='#e74c3c',
              linewidth=1.8, linestyle='-', zorder=3, alpha=1.0)

sz = draw_right_angle(ax, H1, (1, 1), (-1, 1), scale=L, size_ratio=0.025)
tri_AHC = np.array([A, H1, C])
tri_AHN = np.array([A, H1, N1])
ax.fill(tri_AHC[:, 0], tri_AHC[:, 1], color='#3498db', alpha=0.15, zorder=1)
ax.fill(tri_AHN[:, 0], tri_AHN[:, 1], color='#2ecc71', alpha=0.12, zorder=1)

# G13: 全等三角形的粗边（draw_aux_line 自动登记）
for seg, c, owners in [((A, H1), '#3498db', {'A', 'H'}), ((A, C), '#3498db', {'A', 'C'}),
                        ((H1, C), '#3498db', {'H', 'C'}), ((A, N1), '#2ecc71', {'A', 'N'}),
                        ((H1, N1), '#2ecc71', {'H', 'N'})]:
    draw_aux_line(ax, seg[0], seg[1], owners=owners, color=c,
                  linewidth=2.5, linestyle='-', zorder=4)

# 顶点标签
lf_A = label_point(ax, A, 'A', direction=(-0.5, -1.0), scale=L, fontsize=13)
lf_B_fade = label_point(ax, B, 'B', direction=(+1.0, -0.5), scale=L, fontsize=12, alpha=0.35)
lf_C = label_point(ax, C, 'C(M)', direction=(+0.8, +0.6), scale=L, fontsize=12,
                   owners={'C', 'A', 'H', 'N'})
lf_H = label_point(ax, H1, 'H', direction=(+1.0, -0.5), scale=L, fontsize=12,
                   owners={'H', 'C', 'N'})
lf_N = label_point(ax, N1, 'N', direction=(0.0, -1.0), scale=L, fontsize=12)

# 等边标记
mark_equal_sides(ax, A, C, num_marks=1, scale=L, color='red')
mark_equal_sides(ax, A, N1, num_marks=1, scale=L, color='red')

# 角弧标注全等条件
draw_angle_arc(ax, A, C, H1, scale=L, radius_ratio=0.14,
               color='#1565c0', label=u'\u03b1')
draw_angle_arc(ax, A, H1, N1, scale=L, radius_ratio=0.22,
               color='#1565c0', label=u'\u03b1')

# 注解（G12：自动放到空白区）
place_legend_auto(ax, '\u25b3AHC \u2261 \u25b3AHN (ASA)',
                  segments=[(A, H1), (A, C), (H1, C), (A, N1), (H1, N1)],
                  scale=L)

auditor.add_right_angle(H1, sz)

set_active_auditor(None)
ax.set_title('Step 3: \u25b3AHC \u2261 \u25b3AHN (ASA)', fontsize=14)

_save(fig, ax, 'step2_part1_congruent.png', auditor)


# ================================================================
# Figure 4: Part (2) — M 为 BC 中点，AN=AE 对称性
# G10: 全面展示中点情况，没有需要淡出的元素
# ================================================================
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')

autoscale(ax, [A, B, C, N2, E2, M2, ao_end, l2_end], margin_ratio=0.15)
L = compute_visual_scale(ax)

auditor = LayoutAuditor(ax, 'step3_midpoint')
set_active_auditor(auditor)

draw_triangle(ax, A, B, C, names=('A','B','C'))
draw_aux_line(ax, A, ao_end, owners=('A', 'D'), color='#9b59b6',
              linewidth=1.6, linestyle='--', zorder=4)
draw_aux_line(ax, l2_start, l2_end, owners=('N', 'E'), color='#e74c3c',
              linewidth=1.8, linestyle='-', zorder=3)

sz = draw_right_angle(ax, H2, (1, 1), (-1, 1), scale=L, size_ratio=0.025)

lf_A = label_point(ax, A, 'A', direction=(-0.5, -1.0), scale=L, fontsize=13)
lf_B = label_point(ax, B, 'B', direction=(+1.0, -0.5), scale=L, fontsize=13)
lf_C = label_point(ax, C, 'C', direction=(-1.5, +1.2), scale=L, fontsize=13,
                   owners={'C', 'A'})
# D 与 H 过近，隐藏 D 避免 G7b/G14
lf_H = label_point(ax, H2, 'H', direction=(-1.0, +0.6), scale=L, fontsize=12,
                   owners={'H', 'N', 'E', 'B', 'C', 'D', 'M'})
lf_N = label_point(ax, N2, 'N', direction=(+0.5, -1.0), scale=L, fontsize=12)
lf_E = label_point(ax, E2, 'E', direction=(-1.0, -0.2), scale=L, fontsize=12)
lf_M = label_point(ax, M2, 'M', direction=(+0.0, -1.0), scale=L, fontsize=12,
                   owners={'M', 'B', 'C', 'N', 'E'})

# 等边标记 BM = CM
mark_equal_sides(ax, B, M2, num_marks=1, scale=L, color='#e67e22')
mark_equal_sides(ax, M2, C, num_marks=1, scale=L, color='#e67e22')

# 等边标记 AN = AE
mark_equal_sides(ax, A, N2, num_marks=2, scale=L, color='#e91e63')
mark_equal_sides(ax, A, E2, num_marks=2, scale=L, color='#e91e63')

# G13: 高亮 CE / CD 用加粗线（draw_aux_line 自动登记）
draw_aux_line(ax, C, E2, owners=('C', 'E'), color='#e74c3c',
              linewidth=2.8, linestyle='-', zorder=4)
draw_aux_line(ax, C, D, owners=('C', 'D'), color='#e74c3c',
              linewidth=2.8, linestyle='-', zorder=4)

auditor.add_segment(B, C, owner_points={'B', 'C', 'D'})
auditor.add_segment(B, M2, owner_points={'B', 'M'})
auditor.add_segment(M2, C, owner_points={'M', 'C'})
auditor.add_segment(A, N2, owner_points={'A', 'N'})
auditor.add_segment(A, E2, owner_points={'A', 'E'})
auditor.add_right_angle(H2, sz)

set_active_auditor(None)
ax.set_title('Step 4: Midpoint M + AN = AE Symmetry', fontsize=14)

_save(fig, ax, 'step3_midpoint.png', auditor)


# ================================================================
# Figure 5: CD = AB - AC（构造 P）
# G10: 只显示三角形、AO、D、P。淡出 l、H、N、E、M
# ================================================================
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')

autoscale(ax, [A, B, C, D, P, ao_end], margin_ratio=0.15)
L = compute_visual_scale(ax)

auditor = LayoutAuditor(ax, 'step4_prove_CD')
set_active_auditor(auditor)

draw_triangle(ax, A, B, C, names=('A','B','C'))
draw_aux_line(ax, A, ao_end, owners=('A', 'D'), color='#9b59b6',
              linewidth=1.6, linestyle='--', zorder=4)

# PD 连线
draw_aux_line(ax, P, D, owners=('P', 'D'), color='#e74c3c',
              linewidth=2.0, linestyle='-', zorder=3)

# 三角形填充
ax.fill([A[0], P[0], D[0]], [A[1], P[1], D[1]],
        color='#3498db', alpha=0.10, zorder=1)
ax.fill([A[0], C[0], D[0]], [A[1], C[1], D[1]],
        color='#2ecc71', alpha=0.10, zorder=1)

lf_A = label_point(ax, A, 'A', direction=(-0.5, -1.0), scale=L, fontsize=13)
lf_B = label_point(ax, B, 'B', direction=(+1.0, -0.5), scale=L, fontsize=13)
lf_C = label_point(ax, C, 'C', direction=(-1.0, +0.8), scale=L, fontsize=13)
lf_D = label_point(ax, D, 'D', direction=(+1.5, -0.1), scale=L, fontsize=12,
                   owners={'D', 'B', 'C'})
lf_P = label_point(ax, P, 'P', direction=(0.0, -1.0), scale=L, fontsize=12)

# 等边标记
mark_equal_sides(ax, A, P, num_marks=1, scale=L, color='red')
mark_equal_sides(ax, A, C, num_marks=1, scale=L, color='red')
mark_equal_sides(ax, P, D, num_marks=2, scale=L, color='#e67e22')
mark_equal_sides(ax, C, D, num_marks=2, scale=L, color='#e67e22')

# 角弧
draw_angle_arc(ax, B, A, P, scale=L, radius_ratio=0.22,
               color='#4caf50')
# 手动放置 β 标签于 ∠BAP 的平分线，登记 owners 避免 G6 误报
r_beta = L * (0.22 + 0.060)
mid_ba = np.radians((0 + 60) / 2)  # AB=0°, AP=60°
art_beta = ax.text(A[0] + r_beta * np.cos(mid_ba),
                   A[1] + r_beta * np.sin(mid_ba),
                   u'\u03b2', ha='center', va='center',
                   fontsize=10, color='#4caf50', bbox=_TEXT_BOX, zorder=6)
_auto_register(art_beta, kind='anglelabel', name=u'\u03b2',
               owners={'A', 'B', 'P'})
draw_angle_arc(ax, D, P, B, scale=L, radius_ratio=0.18,
               color='#4caf50', label=u'\u03b2')

auditor.add_segment(B, C, owner_points={'B', 'C', 'D'})
auditor.add_segment(A, P, owner_points={'A', 'P'})
auditor.add_segment(C, D, owner_points={'C', 'D'})

set_active_auditor(None)
ax.set_title('Step 5: CD = AB \u2212 AC (Construct P)', fontsize=14)

_save(fig, ax, 'step4_prove_CD_AB_minus_AC.png', auditor)


# ================================================================
# Figure 6: BN + CE = CD 关系图
# G10: 展示全部元素但强调 BN、CE、CD 线段。淡出 H、M
# ================================================================
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')

autoscale(ax, [A, B, C, N2, E2, ao_end, l2_end], margin_ratio=0.18)
L = compute_visual_scale(ax)

auditor = LayoutAuditor(ax, 'step5_relation')
set_active_auditor(auditor)

draw_triangle(ax, A, B, C, names=('A','B','C'))
draw_aux_line(ax, A, ao_end, owners=('A', 'D'), color='#9b59b6',
              linewidth=1.6, linestyle='--', zorder=4)

# l 线（alpha=0.35 淡显）
draw_aux_line(ax, l2_start, l2_end, owners=('N', 'E'), color='#e74c3c',
              linewidth=1.8, linestyle='-', zorder=3, alpha=0.35)
sz = draw_right_angle(ax, H2, (1, 1), (-1, 1), scale=L, size_ratio=0.035, alpha=0.35)

# 点标签 — 淡出 H，M
lf_A = label_point(ax, A, 'A', direction=(-0.5, -1.0), scale=L, fontsize=13)
lf_B = label_point(ax, B, 'B', direction=(+1.0, +0.0), scale=L, fontsize=13)
lf_C = label_point(ax, C, 'C', direction=(-1.0, +0.0), scale=L, fontsize=13)
lf_D = label_point(ax, D, 'D', direction=(+1.0, -0.0), scale=L, fontsize=12,
                   owners={'D', 'B', 'C', 'N', 'E'})
lf_H = label_point(ax, H2, 'H', direction=(-1.0, +0.6), scale=L, fontsize=12, alpha=0.35,
                   owners={'H', 'B', 'C', 'N', 'E', 'D'})
lf_N = label_point(ax, N2, 'N', direction=(+0.0, -1.0), scale=L, fontsize=12)
lf_E = label_point(ax, E2, 'E', direction=(+0.0, -1.0), scale=L, fontsize=12)
lf_M = label_point(ax, M2, 'M', direction=(+0.0, -1.0), scale=L, fontsize=12, alpha=0.35,
                   owners={'M', 'B', 'C', 'N', 'E'})

# G13: 高亮 BN、CE、CD 用加粗线（draw_aux_line 自动登记）
draw_aux_line(ax, B, N2, owners=('B', 'N'), color='#2980b9',
              linewidth=2.8, linestyle='-', zorder=4)
draw_aux_line(ax, C, E2, owners=('C', 'E'), color='#27ae60',
              linewidth=2.8, linestyle='-', zorder=4)
draw_aux_line(ax, C, D, owners=('C', 'D'), color='#e74c3c',
              linewidth=2.8, linestyle='-', zorder=4)

place_segment_label(ax, B, N2, 'BN', '#2980b9', scale=L, offset_ratio=0.065,
                    owners={'B', 'N'})
place_segment_label(ax, C, E2, 'CE', '#27ae60', scale=L, offset_ratio=0.065,
                    owners={'C', 'E'})
place_segment_label(ax, C, D, 'CD', '#e74c3c', scale=L, offset_ratio=0.065,
                    owners={'C', 'D', 'E', 'N'})

# 公式框（G12: 自动放到空白区）
place_legend_auto(ax, 'BN + CE = CD',
                  segments=[(A, B), (B, C), (C, A), (B, N2), (C, E2), (C, D)],
                  scale=L, color='#8e44ad', facecolor='#f3e5f5', fontsize=16)

auditor.add_segment(B, C, owner_points={'B', 'C', 'D'})

set_active_auditor(None)
ax.set_title('Step 6: BN + CE = CD', fontsize=14)

_save(fig, ax, 'step5_relation.png', auditor)


print("All figures generated successfully!")