"""
Problem NNN: {{简要描述}}

模板使用指南：
- 复制为 `math/NNN/geometry_figures.py` 后填充。
- 中文字体加载逻辑、工具函数（draw_angle_arc / mark_equal_sides / label_vertices）
  以及末尾的 `print("All figures generated successfully!")` MUST NOT 删除。
- 运行验证：cd 到题目目录后 `python geometry_figures.py` 必须无报错。
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager

# ========== 中文字体加载（绝对路径，跨环境一致） ==========
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 项目根目录下的 font/，向上若干级查找直到命中
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
# 详见 geometry_drawing_guide.md "绘图执行标准（G-标准，MUST，量化可执行）"
# 所有视觉元素 MUST 按 L_ref 归一，不要写死绝对值。

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
    # 端点在矩形内 → 相交
    for p in (a, b):
        if xmin <= p[0] <= xmax and ymin <= p[1] <= ymax:
            return 0.0
    corners = [np.array([xmin, ymin]), np.array([xmax, ymin]),
               np.array([xmax, ymax]), np.array([xmin, ymax])]
    edges = [(corners[i], corners[(i + 1) % 4]) for i in range(4)]
    # 线段是否与任一矩形边相交
    def _ccw(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    def _intersect(p1, p2, p3, p4):
        d1 = _ccw(p3, p4, p1); d2 = _ccw(p3, p4, p2)
        d3 = _ccw(p1, p2, p3); d4 = _ccw(p1, p2, p4)
        return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))
    for e0, e1 in edges:
        if _intersect(a, b, e0, e1):
            return 0.0
    # 不相交：取线段端点到各边、各角点到线段的最小距离
    dmin = min(_seg_point_distance(c, a, b) for c in corners)
    for e0, e1 in edges:
        dmin = min(dmin, _seg_point_distance(a, e0, e1),
                   _seg_point_distance(b, e0, e1))
    return float(dmin)


class LayoutAuditor:
    """G-标准自检器（自动登记 + bbox 感知）。

    与旧版差异：
    - 文字标签由绘图函数 **自动登记**（通过 set_active_auditor），
      模型不再需要手动 add_point/add_segment 每个标签 → 杜绝"忘记登记→假 PASS"。
    - 标签避碰用 matplotlib renderer 取得的 **真实文字 bbox 矩形相交** 判断，
      不再用中心点距离（宽标签如 'C(M)'、'△AHC≡△AHN' 不会被低估）。

    用法（推荐）：
        auditor = LayoutAuditor(ax, 'step1')
        set_active_auditor(auditor)        # 之后所有 label_* 自动登记
        auditor.add_segment(A, B, owner_points=('A', 'B'))
        ... 绘图 ...
        set_active_auditor(None)
        violations = auditor.check()        # 空列表 = PASS
    """

    def __init__(self, ax, fig_name='figure'):
        self.ax = ax
        self.fig_name = fig_name
        self.scale = compute_visual_scale(ax)
        self.points = {}        # name -> anchor_xy（用于 G7 点群方向检查）
        self.segments = []      # list of (a, b, owners_set)
        self.right_angles = []  # list of (H, size)
        self.texts = []         # list of dict(kind,name,artist,anchor,owners,is_box)

    # ---- 几何对象登记 ----
    def add_segment(self, a, b, owner_points=()):
        self.segments.append((np.asarray(a, float),
                              np.asarray(b, float),
                              set(owner_points)))

    def add_right_angle(self, H, size):
        self.right_angles.append((np.asarray(H, float), float(size)))

    def add_point_anchor(self, name, xy):
        self.points[name] = np.asarray(xy, float)

    # ---- 文字登记（绘图函数自动调用）----
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

    # ---- bbox 计算 ----
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
        # 若 ax 上有文字 artist 但 self.texts 为空，说明 set_active_auditor 在
        # 绘图后才调用，自动登记完全失效（=> 后续所有 G6/G6b/G7b/G14 会假阳性 PASS）。
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

        # G4: 点标签到点心距离 ≤ 0.08·L_ref（G16 引线模式除外）
        max_pt_dist = 0.08 * L
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
                    f'd={d:.3f} > 0.08·L_ref={max_pt_dist:.3f}. '
                    f'Use direction="auto" (G15) or leader=(lx,ly) (G16).')

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

        # G12: 说明框 ↔ 任意几何线段（说明框必须落在空白区）
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
                # 取标签 anchor 方向
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
                # 仅当两个点都被标注（label_point 注册了 kind='point' 的文字）才报
                t1 = next((t for t in self.texts if t['kind'] == 'point' and t['name'] == n1), None)
                t2 = next((t for t in self.texts if t['kind'] == 'point' and t['name'] == n2), None)
                if t1 is None or t2 is None:
                    continue
                # 至少一个未在淡显（alpha < 0.5）则视为正常显示
                a1 = t1['artist'].get_alpha() or 1.0
                a2 = t2['artist'].get_alpha() or 1.0
                if a1 < 0.5 or a2 < 0.5:
                    continue
                v.append(f'G7b extreme cluster "{n1}"/"{n2}" too close (d={d_pp:.3f} < {extreme_thr:.3f}) — MUST hide one label this step or fade to alpha<=0.35')

        # G14: 直角符号方框 ↔ 其他已标注点的标记/标签
        # 直角符号占据从 H 出发约 size×size 的方形区域；不应套住别的标注点
        for H, size in self.right_angles:
            # 直角符号的近似 bbox：以 H 为中心、边长 2*size 的正方形（保守膨胀）
            rH = (H[0] - size, H[1] - size, H[0] + size, H[1] + size)
            for name, P in self.points.items():
                # 自身（垂足）允许；判定"自身"用距离 < 0.5*size
                if float(np.linalg.norm(P - H)) < 0.5 * size:
                    continue
                # 点位于直角符号 bbox 内或非常接近
                if (rH[0] - delta_safe <= P[0] <= rH[2] + delta_safe and
                        rH[1] - delta_safe <= P[1] <= rH[3] + delta_safe):
                    v.append(f'G14 right-angle@{np.round(H,3).tolist()} bracket area contains/near other labeled point "{name}"@{np.round(P,3).tolist()} — shrink size_ratio or rotate bracket')

        return v


# ---- 活动审计器（让绘图函数自动登记文字）----
_ACTIVE_AUDITOR = None


def set_active_auditor(auditor):
    """设为非 None 后，label_point / place_segment_label / draw_angle_arc(label) /
    annotate_box 会自动把文字登记到该 auditor。绘完一张图后 MUST 置回 None。"""
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


# ========== G15 自适应方向 + G16 引线标注 ==========
# 当点处在密集点群（如垂足、内心、交点）时，简单 direction 容易跟邻近点标签重叠
# 或与本地线段相撞。G15 让 label_point 自动在 8 个候选方向中选"远离线段且不与
# 邻近标签同向"的方向；G16 在 G15 全部失败时退化为引线标注。

_G15_CANDIDATES = [
    (0, 1), (0, -1), (1, 0), (-1, 0),
    (1, 1), (1, -1), (-1, 1), (-1, -1),
]
_G15_OFFSETS = (0.055, 0.07, 0.08)
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


# ========== 可复用工具函数（全部按 L_ref 归一） ==========
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
    """画一条辅助线/构造线（如 AO、l）并**自动登记为几何线段**。

    ⚠️ 几何线段 MUST 用本函数（或手动 add_segment），
    MUST NOT 直接用 ax.plot 画几何线——否则压在该线上的标签 auditor 查不到。
    owners: 该线的端点名集合（如 AO 传 {'A','D'}）。
    """
    p1, p2 = np.asarray(p1, float), np.asarray(p2, float)
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linewidth=linewidth,
            linestyle=linestyle, zorder=zorder, alpha=alpha)
    if _ACTIVE_AUDITOR is not None:
        _ACTIVE_AUDITOR.add_segment(p1, p2, owner_points=set(owners))


def label_point(ax, P, name, direction=(1.0, 1.0), scale=1.0,
                offset_ratio=0.055, fontsize=13, color='black',
                marker_zorder=5, text_zorder=6, owners=None):
    """绘制点和点名。文字自动登记到活动 auditor（G11）。

    direction: 标签相对点的方向向量（无需归一），自动按 scale*offset_ratio 归一。
               传 'auto' 走 G15 自适应方向（默认行为）；传 (dx, dy) 显式指定。
    leader: (lx, ly) 走 G16 引线模式：标签放在远端空白区，自动画引线连回 P。
            触发后 G4 距离上限不再适用，但 G6/G7b 仍生效。
    scale: L_ref（来自 compute_visual_scale）。
    密集区点群 MUST 显式给出互不平行的 direction，遵循 G7。
    owners: 该点归属的名集合（默认 {name}），用于避免误报“标签压自身关联边”。
    """
    # 保护阈值：防止误把点标签抛到远处空白区。
    if offset_ratio > 0.08 + 1e-9:
        raise ValueError(
            f'label_point offset_ratio={offset_ratio:.3f} > G4 max 0.08·L_ref. '
            f'Use direction="auto" (G15) or leader=(lx,ly) (G16) for far placements.')

    is_leader_mode = leader is not None
    if is_leader_mode:
        leader_pt = np.asarray(leader, dtype=float)
        # 画引线（虚线：callout 标准视觉，区别于几何实/虚线）
        ax.plot([P[0], leader_pt[0]], [P[1], leader_pt[1]],
                color='#666666', linewidth=0.6, linestyle=':', zorder=4)
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
                       is_leader=is_leader_mode)
    return anchor  # 返回标签 xy（兼容旧调用）


def place_segment_label(ax, p1, p2, text, color, scale=1.0,
                        offset_ratio=0.055, fontsize=12, side=None, owners=None):
    """沿线段法向放置标签。文字自动登记（G11）。

    scale: L_ref。
    offset_ratio: 默认 0.055，落在 G5 的 [0.04, 0.08] 区间内。
    side: None 取 y 分量为正的一侧；+1 / -1 显式指定。
    owners: 该标签归属的点集合（默认空），避免误报“压自身线段”。
    """
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
    """画一个说明框（ASA 框、公式框等）并登记为 is_box=True（G12）。

    说明框 MUST 放在空白区，不得与几何线段相交；推荐用 place_legend_auto 自动选位。
    """
    art = ax.text(xy[0], xy[1], text, ha='center', va='center',
                  fontsize=fontsize, fontweight='bold', color=color,
                  bbox=dict(facecolor=facecolor, edgecolor=color, alpha=0.9, pad=6),
                  zorder=7)
    _auto_register(art, kind='box', name=text.split('\n')[0][:16],
                   owners=(owners if owners is not None else set()), is_box=True)
    return art


def place_legend_auto(ax, text, segments, scale=1.0, color='#1565c0',
                      facecolor='#e3f2fd', fontsize=12):
    """在四个角中选择“离所有几何线段最远”的位置放说明框（G12）。

    segments: [(a, b), ...] 几何线段（用于评估空白度）。
    """
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
    """在 H 处画直角符号；size 按 G1 自适应。

    scale: L_ref。
    size_ratio: 默认 0.035，落在 G1 的 [0.025, 0.05] 区间内。
    """
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
    return size  # 供 auditor.add_right_angle 使用


def draw_ao(ax, A, D, H, ao_dir, scale=1.0,
            color='#9b59b6', linewidth=1.6,
            cap_ratio=0.075,
            dash_zorder=4, cap_zorder=5, owners=None):
    """画 AO 虚线，并在 H 附近补一小段实线，避免虚线空档造成视觉断裂。
    自动登记为几何线段（owners 默认 {'A','D'}）。

    cap_ratio: 实线段半长 / L_ref，默认 0.075。
    """
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
    """在 vertex 处标注角 ∠(p1 - vertex - p2)。G2/G3 自适应半径。

    参数顺序记忆：(顶点, 边1另一点, 边2另一点)。
    调用前 MUST 写注释 `# ∠XXX at V` 表明实际几何角。
    radius_ratio: 默认 0.10，落在 G2 的 [0.08, 0.14] 区间内；
                  同顶点多角调用时相邻 Δradius_ratio MUST ≥ 0.05。
    """
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
    """G3：tick 长度按 L_ref 归一；num_marks≥2 时单 tick 缩短。"""
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
    # G3 上限：tick 总宽度（含间距） ≤ 12% × seg_len
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


def label_vertices(ax, vertices, triangle_pts, scale=1.0,
                   offset_ratio=0.060, fontsize=14):
    """根据重心方向把顶点标签放在外侧。
    密集点群（G7）MUST 改用 label_point 显式给方向。
    """
    centroid = np.mean(np.array(triangle_pts), axis=0)
    for name, pt in vertices.items():
        d = np.array(pt) - centroid
        n = np.linalg.norm(d)
        if n > 0:
            d = d / n * (scale * offset_ratio)
        ax.text(pt[0] + d[0], pt[1] + d[1], name,
                ha='center', va='center',
                fontsize=fontsize, fontweight='bold',
                bbox=_TEXT_BOX, zorder=6)


def autoscale(ax, points, margin_ratio=0.12):
    """根据所有关键点自动设置 xlim/ylim，留 margin_ratio × 范围 边距。"""
    pts = np.array(points)
    xr = pts[:, 0].max() - pts[:, 0].min()
    yr = pts[:, 1].max() - pts[:, 1].min()
    mx = max(xr, yr) * margin_ratio
    ax.set_xlim(pts[:, 0].min() - mx, pts[:, 0].max() + mx)
    ax.set_ylim(pts[:, 1].min() - mx, pts[:, 1].max() + mx)


# ========== Figure 1: TODO 描述 ==========
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')

# TODO: 计算关键点坐标
# A = np.array([0, 0])
# B = np.array([4, 0])
# C = np.array([2, 3])

# Step A — 先 autoscale，再取 L_ref：所有视觉元素 MUST 用 scale=L 调用
# autoscale(ax, [A, B, C])
# L = compute_visual_scale(ax)

# Step B — 建 auditor 并设为活动（之后 label_* 自动登记文字，无需手动 add）
# auditor = LayoutAuditor(ax, fig_name='step1')
# set_active_auditor(auditor)              # ★ G11 关键：开启自动登记
# auditor.add_segment(A, B, owner_points=('A', 'B'))
# auditor.add_segment(B, C, owner_points=('B', 'C'))
# auditor.add_segment(C, A, owner_points=('C', 'A'))

# Step C — 绘制图形（所有文字自动登记到 auditor）
# draw_triangle(ax, A, B, C)
#
# 密集点群（G7：方向夹角 ≥ 90°）：
# label_point(ax, D, 'D', direction=(+1, -1), scale=L)
# label_point(ax, H, 'H', direction=(-1, +1), scale=L)
# label_point(ax, O, 'O', direction=(+1, +1), scale=L)
#
# 直角符号（G1：size 自适应，几何标记仍需手动登记）：
# size = draw_right_angle(ax, H, line_dir=(1,0), normal_dir=(0,1), scale=L)
# auditor.add_right_angle(H, size)
#
# 角弧（G2：同顶点多角 Δradius_ratio ≥ 0.05；label 自动登记）：
# # ∠BAC at A
# draw_angle_arc(ax, A, B, C, scale=L, radius_ratio=0.10, color='red', label='α')
# # ∠CAD at A（同顶点第二个角，半径加大）
# draw_angle_arc(ax, A, C, D, scale=L, radius_ratio=0.16, color='blue', label='β')
#
# 关键辅助线（G8 zorder=4，并在 H 附近补实线 cap）：
# ao_dir = (D - A) / np.linalg.norm(D - A)
# draw_ao(ax, A, D, H, ao_dir, scale=L)
#
# 说明框 / 公式框（G12：MUST 放空白区，禁止压几何）：
# place_legend_auto(ax, '△AHC ≡ △AHN (ASA)',
#                   segments=[(A,B),(B,C),(C,A),(A,H),(H,N)], scale=L)
#
# 高亮已有线段（G13）：MUST 改造原线（加粗/变色/平行偏移），
#   MUST NOT 叠加 annotate('', arrowprops=...) 让箭头穿过已标注点。

# Step D — 关闭自动登记 + 自检（G11：违规即 FAIL，必须修复到空列表）
# set_active_auditor(None)
# violations = auditor.check()
# if violations:
#     print('[step1] LAYOUT VIOLATIONS (MUST FIX):')
#     for w in violations:
#         print('  -', w)

# Step E — 步骤元素隔离（G10）
# 前置上下文（如本步不直接讨论的边、角）MUST 用 alpha<=0.35 淡显，或省略

ax.set_title('Step 1: TODO')
ax.axis('off')
plt.tight_layout()
plt.savefig(os.path.join(_BASE_DIR, 'step1_TODO.png'),
            dpi=150, bbox_inches='tight')
plt.close()


# ========== Figure 2: TODO 描述 ==========
# TODO: 复制上方结构，按解题步骤补充。


print("All figures generated successfully!")
