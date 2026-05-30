# 几何图形绘制规范

> 本文档定义了解题过程中生成几何图形的完整技术规范和最佳实践。
> 默认使用 Python matplotlib，备选方案（JSXGraph、Manim）需用户明确指定。

## 基本规范

- 使用Python matplotlib库绘制示意图
- 根据演示需要生成中间过程图片
- 图片命名规范：`step{序号}_{描述}.png`
- 保存路径：与题目图片同名的文件夹内
- **插图文字规范**：
  - 优先使用英文标签（避免字体兼容问题）
  - 如需中文，需配置中文字体支持（详见下方"中文字体支持"章节）
  - 几何元素标注：Apex（顶角）、Base（底角）、Line AC（直线AC）等
  - 标题使用英文：Step 1、Case 1、Final Answer等
  - 确保所有文字在英文环境下清晰可读
- **中文字体支持**：
  - 适用场景：解题说明、技巧总结等需要中文展示的插图
  - **优先使用项目目录中的字体文件**，确保跨环境兼容
  - 项目 `font/` 目录已放置字体文件：`STHeiti Medium.ttc`、`STHeiti Light.ttc`
  - 配置方法：通过 `font_manager.addfont()` 加载项目内字体
    ```python
    from matplotlib import font_manager
    font_manager.fontManager.addfont('font/STHeiti Medium.ttc')
    plt.rcParams['font.family'] = 'Heiti TC'
    plt.rcParams['axes.unicode_minus'] = False
    ```
  - 需确保运行时 **当前工作目录为项目根目录**，或使用绝对路径：
    ```python
    import os
    from matplotlib import font_manager
    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(base_dir, 'font', 'STHeiti Medium.ttc')
    font_manager.fontManager.addfont(font_path)
    plt.rcParams['font.family'] = 'Heiti TC'
    ```
  - 系统字体检测方法（备选，依赖系统安装的字体）：
    ```python
    import matplotlib.font_manager as fm
    fonts = [f.name for f in fm.fontManager.ttflist]
    chinese_fonts = [f for f in fonts if any(k in f for k in ['Ping', 'Heiti', 'Song', 'STHeiti'])]
    print(sorted(set(chinese_fonts)))
    ```
  - ⚠️ 注意事项：
    - `STHeiti` 字体缺少数学符号 `≅`（全等号），需用 `=` 或文字描述替代
    - 设置中文字体后，英文字母和数字仍可正常显示
    - 设置 `axes.unicode_minus = False` 可解决负号 `−` 显示为方块的问题
- **坐标范围设置规范（重要）**：
  - 必须先计算图形关键点的实际坐标，确保坐标范围足够大
  - 例如：等腰三角形顶点C的y坐标 = 底边长度/2 × tan(顶角)，需确保ylim上限大于此值
  - 设置`ax.set_ylim()`和`ax.set_xlim()`时，必须验证所有图形元素都在范围内
  - 使用`bbox_inches='tight'`时要特别注意：它会裁剪空白区域，可能误裁剪图形部分
  - 建议做法：先计算所有点的坐标范围，然后设置比实际范围大10-20%的显示区域

## Matplotlib 最佳实践（基于006/007实战验证）

### 脚本结构模板

每个 `geometry_figures.py` 遵循统一结构：

```python
"""
Problem XXX: [简要描述]
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# ========== 可复用工具函数 ==========
def draw_triangle(ax, A, B, C, labels=None, color='black', linewidth=1.5): ...
def draw_angle_arc(ax, center, p1, p2, radius=0.3, color='blue', label=None): ...
def mark_equal_sides(ax, p1, p2, num_marks=1, color='red'): ...

# ========== Figure 1: [描述] ==========
fig, ax = plt.subplots(1, 1, figsize=(7, 7))
ax.set_aspect('equal')
# ... 绘图代码 ...
plt.tight_layout()
plt.savefig('step1_xxx.png', dpi=150, bbox_inches='tight')
plt.close()

# ========== Figure 2: [描述] ==========
# ...

print("All figures generated successfully!")
```

### 角度标注精确化

使用 `patches.Arc` 结合三角函数，处理角度方向翻转：

```python
def draw_angle_arc(ax, center, p1, p2, radius=0.3, color='blue', label=None):
    """Draw an angle arc between two rays from center."""
    angle1 = np.degrees(np.arctan2(p1[1]-center[1], p1[0]-center[0]))
    angle2 = np.degrees(np.arctan2(p2[1]-center[1], p2[0]-center[0]))
    # 关键：确保弧线画在较小角一侧
    if angle2 < angle1:
        angle1, angle2 = angle2, angle1
    if angle2 - angle1 > 180:
        angle1, angle2 = angle2, angle1 + 360
    arc = patches.Arc(center, 2*radius, 2*radius, angle=0,
                      theta1=angle1, theta2=angle2, color=color, linewidth=1.5)
    ax.add_patch(arc)
    if label:
        mid_angle = np.radians((angle1 + angle2) / 2)
        label_r = radius + 0.15
        ax.text(center[0] + label_r * np.cos(mid_angle),
                center[1] + label_r * np.sin(mid_angle),
                label, ha='center', va='center', fontsize=10, color=color)
```

**参数几何含义**：

| 参数 | 几何含义 | 示例 |
|------|----------|------|
| `center` | **角的顶点** | 标 ∠ABC 时传入 `B` |
| `p1` | 角的一条边上的另一点（非顶点） | 标 ∠ABC 时传入 `A`（代表边BA） |
| `p2` | 角的另一条边上的另一点（非顶点） | 标 ∠ABC 时传入 `C`（代表边BC） |

> ⚠️ **调用规律**：`draw_angle_arc(ax, vertex, point_on_side1, point_on_side2, ...)` 对应几何角 ∠(point_on_side1 - vertex - point_on_side2)。中间参数永远是**角的顶点**。
>
> **常见错误**：容易把 p1、p2 误当作弧的两个端点。例如 `draw_angle_arc(ax, A, B, C)` 画出的是 **∠BAC**（顶点A，边AB和AC），而不是从B到C的弧。

### 顶点标签智能定位

基于三角形重心计算偏移方向，确保标签始终在外部：

```python
def label_vertices(ax, vertices_dict, triangle_points, offset=0.25):
    """为多个顶点自动计算标签位置，向外偏移。"""
    A, B, C = triangle_points
    centroid = (A + B + C) / 3
    for name, point in vertices_dict.items():
        direction = point - centroid
        if np.linalg.norm(direction) > 0:
            direction = direction / np.linalg.norm(direction) * offset
        ax.text(point[0] + direction[0], point[1] + direction[1], name,
                ha='center', va='center', fontsize=14, fontweight='bold')
```

### 等边标记专业化

绘制垂直于边的短线段标记相等边长：

```python
def mark_equal_sides(ax, p1, p2, num_marks=1, color='red'):
    """在线段中点处绘制垂直短线标记相等边。"""
    mid = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2)
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = np.sqrt(dx**2 + dy**2)
    perp_x = -dy / length * 0.08
    perp_y = dx / length * 0.08
    along_x = dx / length * 0.05
    along_y = dy / length * 0.05
    for i in range(num_marks):
        offset = (i - (num_marks-1)/2) * 0.06
        cx = mid[0] + offset * along_x / 0.05
        cy = mid[1] + offset * along_y / 0.05
        ax.plot([cx - perp_x, cx + perp_x], [cy - perp_y, cy + perp_y],
                color=color, linewidth=2)
```

### 多角度标注策略（006实践，核心最佳实践）

当同一顶点或相邻顶点有多个角度需标注时，需通过**半径分层 + 颜色区分**避免视觉混乱：

**原则零（首要原则）：先写注释再写代码**

在写 `draw_angle_arc` 之前，先列出所有要标注的角的参数对应关系：

```
∠BMC → draw_angle_arc(ax, M, B, C, ...)  # 顶点M，边MB和MC，角∠BMC
∠ABM → draw_angle_arc(ax, B, A, M, ...)  # 顶点B，边BA和BM，角∠ABM
∠MBC → draw_angle_arc(ax, B, M, C, ...)  # 顶点B，边BM和BC，角∠MBC
```

**规律**：三个参数就是几何角的三个点，中间是顶点 — `(顶点, 边1上另一点, 边2上另一点)`。

**每条 `draw_angle_arc` 调用必须加注释标明实际的几何角**，格式为 `# ∠XXX at V`（V是顶点）。

错误的注释还不如不写，例如 `# 角ACD` 就很有误导性，因为它没说明谁是顶点。
正确的注释 `# ∠ACD at C` 清楚表明顶点是C。

**原则一：同一顶点多角度用不同半径分层**

```python
# 顶点C被cevian分成两个角，用不同半径区分
draw_angle_arc(ax, C, A, D, radius=0.4, color='blue', label='36°')    # ∠ACD at C
draw_angle_arc(ax, C, D, B, radius=0.55, color='purple', label='36°')  # ∠DCB at C
```

**原则二：每个角度赋予独立颜色，表达归属关系**

```python
# 不同颜色对应不同子三角形的角，每条调用都标明几何角
draw_angle_arc(ax, A, B, C, radius=0.5, color='red', label='36°')      # ∠BAC at A（顶角A）
draw_angle_arc(ax, C, A, D, radius=0.4, color='blue', label='36°')     # ∠ACD at C（属于△ACD）
draw_angle_arc(ax, C, D, B, radius=0.55, color='purple', label='36°')  # ∠DCB at C（属于△BCD）
draw_angle_arc(ax, B, C, A, radius=0.4, color='orange', label='72°')   # ∠CBA at C（底角C）
```

**原则三：半径选择策略**

| 场景 | 推荐半径 | 说明 |
|------|----------|------|
| 主角/特征角 | 0.5 | 视觉突出 |
| 普通标注 | 0.4 | 基准大小 |
| 同顶点第二个角 | 0.55~0.6 | 与第一个角拉开层次 |
| 小角度（<30°） | 0.5~0.6 | 较大半径避免标签重叠 |
| 大角度（>90°） | 0.3~0.4 | 较小半径保持紧凑 |

**原则四：颜色与几何元素一致性映射**

- 主角/顶角：红色 — 最醒目，突出核心条件
- 属于子三角形1的角：蓝色 — 与该子三角形填充色系一致
- 属于子三角形2的角：紫色或橙色 — 与另一子三角形填充色系一致
- 底角：橙色 — 与侧边/底边相关

**完整示例（006核心模式）**：

```python
# 主三角形ABC中，cevian CD将其分为△ACD和△BCD
# 角度标注按归属和层次组织
draw_angle_arc(ax, A, B, C, radius=0.5, color='red', label='36°')       # 顶角A - 题目核心
draw_angle_arc(ax, C, A, D, radius=0.4, color='blue', label='36°')      # △ACD中C的角
draw_angle_arc(ax, C, D, B, radius=0.55, color='purple', label='36°')   # △BCD中C的角（同顶点，大半径）
draw_angle_arc(ax, B, C, A, radius=0.4, color='orange', label='72°')    # 底角B
```

### 颜色语义统一化

- 角度标注（单角场景）：红色 (`color='red'`)
- 角度标注（多角场景）：按归属分色（见上节）
- 等边标记第一组：红色 (`color='red'`)
- 等边标记第二组：绿色 (`color='green'`)
- 辅助线/cevian：蓝色 (`'b-'` 或 `'b--'`)
- 子三角形填充：lightblue + lightyellow（alpha=0.15~0.2）
- 辅助线/构造线：紫色或橙色

### 区域填充区分

使用半透明填充区分不同子三角形：

```python
tri1 = plt.Polygon([A, B, D], alpha=0.2, facecolor='lightblue', edgecolor='blue', linewidth=1.5)
tri2 = plt.Polygon([B, D, C], alpha=0.2, facecolor='lightyellow', edgecolor='orange', linewidth=1.5)
ax.add_patch(tri1)
ax.add_patch(tri2)
# 注意：填充层放在主三角形描边之前添加，确保边界线在上层
```

### 坐标计算数学严谨性

使用正弦定理精确计算顶点坐标：

```python
# 方法1：正弦定理计算边长，再用极坐标定位顶点
BC = 3.0  # 设定基准边长
AB = BC * np.sin(np.radians(C_angle)) / np.sin(np.radians(A_angle))
AC = BC * np.sin(np.radians(B_angle)) / np.sin(np.radians(A_angle))
# B在原点，C在x轴正方向，A通过B点角度定位
B = np.array([0, 0])
C = np.array([BC, 0])
A = np.array([AB * np.cos(np.radians(B_angle)), AB * np.sin(np.radians(B_angle))])

# 方法2：等腰三角形以顶角为中心对称放置
A = np.array([0, AB * np.cos(np.radians(angle_A/2))])  # 顶点在上
B = np.array([-AB * np.sin(np.radians(angle_A/2)), 0])  # 左底
C = np.array([AB * np.sin(np.radians(angle_A/2)), 0])   # 右底
```

### Cevian（角分线/内部分割线）端点精确计算

```python
# 已知分割后三角形的角度，用正弦定理求分割点位置
# 例如：cevian从B到AC上的D点，已知角ABD和角ADB
# 在△ABD中：AD / sin(ABD) = AB / sin(ADB)
AD = AB * np.sin(np.radians(angle_ABD)) / np.sin(np.radians(angle_ADB))
AC_len = np.linalg.norm(C - A)
t = AD / AC_len  # 参数化比例
D = A + t * (C - A)  # D在AC上的坐标
```

### 动态坐标范围设置（关键，避免图形被裁剪）

```python
# 收集所有关键点，自动计算范围
all_points = np.array([A, B, C, D])  # 包含所有点
margin = 0.6  # 边距，根据图形密度调整
ax.set_xlim(all_points[:, 0].min() - margin, all_points[:, 0].max() + margin)
ax.set_ylim(all_points[:, 1].min() - margin, all_points[:, 1].max() + margin)
```

### 角度标签放置于三角形内部（007实践）

替代arc标注的简洁方案：

```python
# 在顶点向对边中点方向偏移放置角度文字
mid_direction = ((other1 + other2) / 2 - vertex)
if np.linalg.norm(mid_direction) > 0:
    mid_direction = mid_direction / np.linalg.norm(mid_direction) * 0.45
ax.text(vertex[0] + mid_direction[0], vertex[1] + mid_direction[1],
        f'{angle:.0f}°', ha='center', va='center', fontsize=9, color='red')
```

### 子三角形内部标注信息（007实践）

在重心处标注角度和等边信息：

```python
centroid1 = (A + B + D) / 3
ax.text(centroid1[0], centroid1[1], 'ABD\n36°-36°-108°\nAD=BD',
        ha='center', va='center', fontsize=9, color='blue')
```

### 多图并排对比（006/007 Summary图）

```python
fig, axes = plt.subplots(2, 3, figsize=(14, 10))
axes_flat = axes.flatten()
for idx, case_data in enumerate(cases):
    draw_case(axes_flat[idx], case_data)
# 隐藏多余subplot
for i in range(len(cases), len(axes_flat)):
    axes_flat[i].axis('off')
plt.suptitle('Problem XXX: All Solutions', fontsize=15, fontweight='bold', y=0.98)
plt.tight_layout()
```

### 可复用函数清单

- `draw_triangle(ax, A, B, C, labels, color, linewidth)`
- `draw_angle_arc(ax, center, p1, p2, radius, color, label)`
- `mark_equal_sides(ax, p1, p2, num_marks, color)`
- `label_vertices(ax, vertices_dict, triangle_points, offset)`
- `draw_triangle_with_cevian(ax, angles, cevian_from, title, case_label)` — 007模式，完整绘制带分割线的三角形

---

## 备选方案：JSXGraph交互式绘图

> 需用户在任务中明确指定

- 适用场景：需要交互式拖拽、动态演示的几何图形
- CDN引入：`<script src="https://cdn.jsdelivr.net/npm/jsxgraph@1.8.0/distrib/jsxgraphcore.js"></script>`
- CSS引入：`<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/jsxgraph@1.8.0/distrib/jsxgraph.css">`
- 使用JSXGraph时，图形直接嵌入HTML中，无需生成PNG图片
- geometry_figures.py 改为坐标计算与验证脚本（不生成图片）
- 基本用法示例：
  ```javascript
  var board = JXG.JSXGraph.initBoard('boardId', {
      boundingbox: [-1, 6, 7, -1], axis: false, showNavigation: false
  });
  var A = board.create('point', [0, 0], {name: 'A', fixed: true});
  var B = board.create('point', [6, 0], {name: 'B', fixed: true});
  var C = board.create('point', [3, 4], {name: 'C', fixed: true});
  board.create('polygon', [A, B, C], {
      borders: {strokeColor: 'black', strokeWidth: 2},
      fillColor: 'transparent'
  });
  board.create('angle', [B, A, C], {radius: 0.5, name: '\\alpha'});
  ```
- 优势：用户可交互操作（缩放、拖拽）、动态显示解题步骤、无字体兼容问题
- 注意事项：
  - 每个步骤使用独立的 `board`，通过步骤切换控制显示/隐藏
  - 坐标需预先精确计算（可用Python脚本验证）
  - 配合MathJax渲染公式文本

---

## 备选方案：Manim动画绘图

> 需用户在任务中明确指定

- 适用场景：需要生成高质量动画演示、逐步构造过程的几何证明
- 安装：`pip install manim`（社区版 ManimCE）
- 使用Manim时，生成MP4/GIF动画或高清PNG帧图
- 基本用法示例：
  ```python
  from manim import *

  class TriangleConstruction(Scene):
      def construct(self):
          # Create triangle
          A = np.array([-2, -1, 0])
          B = np.array([2, -1, 0])
          C = np.array([0, 2, 0])
          triangle = Polygon(A, B, C, color=WHITE)

          # Labels
          label_A = MathTex("A").next_to(A, DOWN)
          label_B = MathTex("B").next_to(B, DOWN)
          label_C = MathTex("C").next_to(C, UP)

          # Animate step by step
          self.play(Create(triangle))
          self.play(Write(label_A), Write(label_B), Write(label_C))

          # Add angle arc
          angle = Angle.from_three_points(B, A, C, radius=0.4, color=RED)
          angle_label = MathTex(r"\alpha", color=RED).next_to(angle, RIGHT, buff=0.1)
          self.play(Create(angle), Write(angle_label))
  ```
- 渲染命令：
  - 高清PNG：`manim -s -qh geometry_figures.py TriangleConstruction`
  - GIF动画：`manim --format=gif -qm geometry_figures.py TriangleConstruction`
  - MP4视频：`manim -qm geometry_figures.py TriangleConstruction`
- 优势：动画效果直观展示构造过程、渲染质量高、原生支持LaTeX公式、无字体问题
- 注意事项：
  - 渲染速度较慢，适合最终展示而非快速迭代
  - 输出文件较大，需考虑网页加载性能
  - 静态图使用 `-s` 参数仅渲染最后一帧
  - HTML中嵌入视频使用 `<video>` 标签或转为GIF用 `<img>` 标签
