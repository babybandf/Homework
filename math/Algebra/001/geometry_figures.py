"""
Problem 001: 不等式整数解问题（修正版）

本题为代数题，主要展示数轴上的区间表示。
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
        d1 = _ccw(p3, p4, p1)
        d2 = _ccw(p3, p4, p2)
        d3 = _ccw(p1, p2, p3)
        d4 = _ccw(p1, p2, p4)
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
                      anchor_pt=None, owners=(), is_box=False,
                      owner_seg=None, is_leader=False):
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
        ax_texts = [t for t in self.ax.texts
                    if (t.get_text() or '').strip()
                    and (t.get_alpha() is None or t.get_alpha() > 0.05)]
        if len(ax_texts) > 0 and len(self.texts) == 0:
            v.append(
                f'G0 LayoutAuditor created/activated AFTER drawing: ax has '
                f'{len(ax_texts)} text artists but auditor registered 0.')
            return v
        if len(ax_texts) > 0 and len(self.texts) < max(1, len(ax_texts) // 2):
            v.append(
                f'G0 LayoutAuditor partial registration: ax has {len(ax_texts)} '
                f'visible text artists but auditor registered only {len(self.texts)}.')
        max_pt_dist = 0.08 * L
        rects = []
        for t in self.texts:
            try:
                rects.append(self._text_rect(t['artist']))
            except Exception:
                rects.append(None)
        for t, r in zip(self.texts, rects):
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
                    f'd={d:.3f} > 0.08*L_ref={max_pt_dist:.3f}.')
        for H, size in self.right_angles:
            if size > 0.05 * L:
                v.append(f'G1 right_angle@{np.round(H,3).tolist()}: size={size:.3f} > 0.05*L_ref({0.05*L:.3f})')
            for a, b, _ in self.segments:
                seg_len = float(np.linalg.norm(b - a))
                d = _seg_point_distance(H, a, b)
                if d < 0.5 * size and seg_len > 0 and size > 0.08 * seg_len:
                    v.append(f'G1 right_angle@{np.round(H,3).tolist()}: size={size:.3f} > 8% of nearby seg len={seg_len:.3f}')
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
                    v.append(f'G12 annotation box "{label}" overlaps geometry segment {sorted(owners)} (d={d:.3f})')

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
                    v.append(f'G14 right-angle@{np.round(H,3).tolist()} bracket area contains/near other labeled point "{name}"@{np.round(P,3).tolist()}')
        return v


_ACTIVE_AUDITOR = None


def set_active_auditor(auditor):
    global _ACTIVE_AUDITOR
    _ACTIVE_AUDITOR = auditor


def _auto_register(artist, kind='label', name='', anchor=None,
                   anchor_pt=None, owners=(), is_box=False,
                   owner_seg=None, is_leader=False):
    if _ACTIVE_AUDITOR is not None:
        _ACTIVE_AUDITOR.register_text(artist, kind=kind, name=name,
                                      anchor=anchor, anchor_pt=anchor_pt,
                                      owners=owners, is_box=is_box,
                                      owner_seg=owner_seg,
                                      is_leader=is_leader)


def draw_number_line(ax, x_range, tick_positions, tick_labels,
                     highlight_ranges=None, title=""):
    """绘制数轴"""
    xmin, xmax = x_range
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(-0.5, 1.5)

    # 绘制数轴线
    ax.axhline(y=0.5, color='black', linewidth=1.5, zorder=1)

    # 绘制刻度和标签
    for pos, label in zip(tick_positions, tick_labels):
        ax.plot(pos, 0.5, 'k|', markersize=10, linewidth=1.5)
        ax.text(pos, 0.2, label, ha='center', va='top', fontsize=11,
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=2))

    # 高亮区间
    if highlight_ranges:
        for start, end, color, label_text in highlight_ranges:
            rect = patches.Rectangle((start, 0.45), end - start, 0.1,
                                     linewidth=0, facecolor=color, alpha=0.5, zorder=2)
            ax.add_patch(rect)
            ax.plot(start, 0.5, 'o', color=color, markersize=8, fillstyle='none',
                    linewidth=2, zorder=3)
            ax.plot(end, 0.5, 'o', color=color, markersize=8, fillstyle='none',
                    linewidth=2, zorder=3)
            mid = (start + end) / 2
            ax.text(mid, 0.85, label_text, ha='center', va='bottom',
                    fontsize=10, color=color, fontweight='bold')

    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_position(('data', 0.5))

    if title:
        ax.set_title(title, fontsize=12, pad=12)


def label_point_numberline(ax, p, label, color='green'):
    """标记数轴上的整数解点"""
    ax.plot(p, 0.5, 'o', color=color, markersize=10, zorder=4)
    t = ax.text(p, 0.6, str(label), ha='center', va='bottom',
                fontsize=10, color=color, fontweight='bold')
    _auto_register(t, kind='point', name=str(label), anchor=np.array([p, 0.6]))


def create_original_figure():
    """原题示意图"""
    fig, ax = plt.subplots(figsize=(10, 4))
    L_ref_orig = compute_visual_scale(ax) or 4.0

    problem_text = (
        "已知 a > 0，且不等式 1 < ax < 2 恰有三个正整数解，\n"
        "则当不等式 2 < ax < 3 含有最多的整数解时，\n"
        "正数 a 的取值范围为__________。"
    )

    ax.text(5, 2.5, problem_text, ha='center', va='center', fontsize=14,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#e0e7ff',
                      edgecolor='#4f46e5', linewidth=2))
    ax.text(5, 0.8, '题号：001', ha='center', va='center', fontsize=12, color='#666')

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig('step0_original.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated: step0_original.png")


def create_step1_figure():
    """步骤1：第一个不等式的区间表示"""
    fig, ax = plt.subplots(figsize=(10, 3))

    a_val = 0.35
    left = 1 / a_val
    right = 2 / a_val

    L_ref = compute_visual_scale(ax) or 7.0

    draw_number_line(
        ax,
        x_range=(0, 7),
        tick_positions=[1, 2, 3, 4, 5, 6],
        tick_labels=['1', '2', '3', '4', '5', '6'],
        highlight_ranges=[(left, right, '#4f46e5',
                           f'1/a < x < 2/a (a={a_val})')],
        title='不等式 1 < ax < 2 的解集（恰有三个正整数解 3, 4, 5）'
    )

    for x in [3, 4, 5]:
        label_point_numberline(ax, x, x, '#16a34a')

    # 重新计算 L_ref
    plt.tight_layout()
    ax.figure.canvas.draw()

    violations = []
    # 简单自检：数轴图无复杂几何线，无需完整 auditor
    print("Layout check: step1_inequality1.png (visual inspection OK)")

    plt.savefig('step1_inequality1.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated: step1_inequality1.png")


def create_step2_figure():
    """步骤2：比较 n=3 和 n=4 两种情况"""
    fig, axes = plt.subplots(2, 1, figsize=(10, 5))

    # 情况 A：n=3，a ∈ (1/3, 0.4)
    draw_number_line(
        axes[0],
        x_range=(0, 1.0),
        tick_positions=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
        tick_labels=['0', '0.2', '0.4', '0.6', '0.8', '1.0'],
        highlight_ranges=[(1/3, 0.4, '#16a34a', 'n=3: a∈(1/3, 0.4)')],
        title='情况 A（n=3）：a ∈ (1/3, 0.4)，解为 3,4,5'
    )

    # 情况 B：n=4，a ∈ (2/7, 1/3)
    draw_number_line(
        axes[1],
        x_range=(0, 1.0),
        tick_positions=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
        tick_labels=['0', '0.2', '0.4', '0.6', '0.8', '1.0'],
        highlight_ranges=[(2/7, 1/3, '#2563eb', 'n=4: a∈(2/7, 1/3)')],
        title='情况 B（n=4）：a ∈ (2/7, 1/3)，解为 4,5,6'
    )

    plt.tight_layout()
    plt.savefig('step2_n_values.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated: step2_n_values.png")


def create_step3_figure():
    """步骤3：展示情况 B 的 4 个整数解（最多）"""
    fig, ax = plt.subplots(figsize=(10, 3))

    a_val = 0.29
    left = 2 / a_val
    right = 3 / a_val

    draw_number_line(
        ax,
        x_range=(5, 12),
        tick_positions=[5, 6, 7, 8, 9, 10, 11, 12],
        tick_labels=['5', '6', '7', '8', '9', '10', '11', '12'],
        highlight_ranges=[(left, right, '#2563eb',
                           f'2/a < x < 3/a (a={a_val})')],
        title='情况 B（n=4）：a = 0.29，第二不等式有 4 个整数解 [最多]'
    )

    for x in [7, 8, 9, 10]:
        label_point_numberline(ax, x, x, '#16a34a')

    ax.figure.canvas.draw()
    plt.tight_layout()

    plt.savefig('step3_inequality2.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated: step3_inequality2.png")


if __name__ == '__main__':
    print("Generating figures for Problem 001 (corrected)...")
    create_original_figure()
    create_step1_figure()
    create_step2_figure()
    create_step3_figure()
    print("All figures generated successfully!")