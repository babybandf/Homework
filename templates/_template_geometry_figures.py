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


# ========== 可复用工具函数 ==========
def draw_triangle(ax, A, B, C, color='black', linewidth=1.8):
    """绘制三角形 ABC 的三条边。"""
    pts = np.array([A, B, C, A])
    ax.plot(pts[:, 0], pts[:, 1], color=color, linewidth=linewidth)


def draw_angle_arc(ax, vertex, p1, p2, radius=0.4, color='blue', label=None):
    """在 vertex 处标注角 ∠(p1 - vertex - p2)。

    参数顺序记忆：(顶点, 边1另一点, 边2另一点)。
    调用前 MUST 写注释 `# ∠XXX at V` 表明实际几何角。
    """
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
        r = radius + 0.18
        ax.text(vertex[0] + r * np.cos(mid),
                vertex[1] + r * np.sin(mid),
                label, ha='center', va='center',
                fontsize=10, color=color)


def mark_equal_sides(ax, p1, p2, num_marks=1, color='red'):
    """在线段中点画垂直短线表示等边。"""
    mid = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    L = np.hypot(dx, dy)
    px, py = -dy / L * 0.08, dx / L * 0.08
    ax_, ay_ = dx / L * 0.05, dy / L * 0.05
    for i in range(num_marks):
        offset = (i - (num_marks - 1) / 2)
        cx = mid[0] + offset * ax_
        cy = mid[1] + offset * ay_
        ax.plot([cx - px, cx + px], [cy - py, cy + py],
                color=color, linewidth=2)


def label_vertices(ax, vertices, triangle_pts, offset=0.25, fontsize=14):
    """根据重心方向把顶点标签放在外侧。

    vertices: dict[name -> (x, y)]
    triangle_pts: (A, B, C) 用于计算重心
    """
    centroid = np.mean(np.array(triangle_pts), axis=0)
    for name, pt in vertices.items():
        d = np.array(pt) - centroid
        n = np.linalg.norm(d)
        if n > 0:
            d = d / n * offset
        ax.text(pt[0] + d[0], pt[1] + d[1], name,
                ha='center', va='center',
                fontsize=fontsize, fontweight='bold')


def autoscale(ax, points, margin=0.6):
    """根据所有关键点自动设置 xlim/ylim 留边距。"""
    pts = np.array(points)
    ax.set_xlim(pts[:, 0].min() - margin, pts[:, 0].max() + margin)
    ax.set_ylim(pts[:, 1].min() - margin, pts[:, 1].max() + margin)


# ========== Figure 1: TODO 描述 ==========
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')

# TODO: 计算关键点坐标
# A = np.array([0, 0])
# B = np.array([4, 0])
# C = np.array([2, 3])

# TODO: 绘制图形
# draw_triangle(ax, A, B, C)
# label_vertices(ax, {'A': A, 'B': B, 'C': C}, (A, B, C))
# autoscale(ax, [A, B, C])

ax.set_title('Step 1: TODO')
ax.axis('off')
plt.tight_layout()
plt.savefig(os.path.join(_BASE_DIR, 'step1_TODO.png'),
            dpi=150, bbox_inches='tight')
plt.close()


# ========== Figure 2: TODO 描述 ==========
# TODO: 复制上方结构，按解题步骤补充。


print("All figures generated successfully!")
