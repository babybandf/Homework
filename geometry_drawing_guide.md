# 几何图形绘制规范

> ⚠️ 本文档为**实现细节参考**。硬性约束以 [AGENT.MD](AGENT.MD) 为准。

## ⚠️ 本文档的 MUST 条款（其他为参考）

- **M1** MUST 使用 Python matplotlib 输出 PNG。MUST NOT 用 SVG / Mermaid / ASCII / 内联 HTML 绘图替代。
- **M2** 中文字体 MUST 通过 `font/STHeiti Medium.ttc` 以**绝对路径**加载（见下方"中文字体支持"章节）。
- **M3** 坐标范围 MUST 在所有关键点计算完成后再设置，并留 10–20% 边距。
- **M4** `draw_angle_arc` 调用 MUST 在上方加 `# ∠XXX at V` 注释标明实际几何角。
- **M5** 脚本末尾 MUST 输出 `print("All figures generated successfully!")` 用于自检。
- **M6** 备选方案（JSXGraph / Manim）仅当用户在本轮显式覆盖时启用。
- **M7** 点名、线段名、角标、直角符号 MUST 保持清晰可读；MUST NOT 与线段、辅助线、点标记或其他标签明显重叠。
- **M8** 关键辅助线（如角平分线、垂线、构造线）在交点附近 MUST 连续可见；若虚线节距导致视觉断裂，MUST 调整 dash pattern 或局部补短实线。
- **M9** 点标记、标签、直角符号、辅助线 MUST 显式考虑图层顺序（`zorder`）；关键线段 MUST NOT 被点标记或直角符号盖住。
- **M10** 所有可见图元（直角符号、角弧、等边 tick、标签偏移）MUST 按下方"绘图执行标准（G-标准）"以图幅 `L_ref` 归一，MUST NOT 直接写绝对坐标经验值。
- **M11** 每张图 MUST 在绘图前 `set_active_auditor(auditor)`、绘图后 `check()`（模板提供，自动登记+bbox 感知）；`check()` 返回非空即 FAIL，MUST 修复到空列表后再保存。MUST NOT 把违规当 warning 打印后照常保存。
- **M12** 每个 `step*.png` MUST 只显式高亮"该步骤新增/讨论"的几何对象；前置上下文（已在前一步建立的元素）MUST 用 `alpha ≤ 0.35` 淡显或省略。
- **M13** 说明框 / 公式框 MUST 放在空白区（用 `place_legend_auto`），MUST NOT 压住几何；高亮已有线段 MUST 改造原线（加粗/变色/平行偏移），MUST NOT 叠加穿过端点的双向箭头。

---

## 绘图执行标准（G-标准，MUST，量化可执行）

> 所有 G-标准都用图幅参考长度 `L_ref` 归一，避免在小图（短边=1）和大图（短边=10）上共用同一组绝对值。
> MUST 在 `set_xlim` / `set_ylim` 之后再放置任何视觉元素；MUST 用工具函数 `compute_visual_scale(ax)` 取得 `L_ref`。

```python
def compute_visual_scale(ax):
    """返回图幅参考长度 L_ref = min(xrange, yrange)。
    MUST 在所有图元尺寸计算前调用。"""
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    return min(abs(x1 - x0), abs(y1 - y0))
```

### G1 直角符号 size

- `size = 0.045 × L_ref`（推荐区间 `[0.03, 0.06] × L_ref`）。
- MUST NOT 超过其所在两条线段中较短者的 **15%**（既保证直角符号可辨识，又不过度侵占邻域）。
- `zorder` MUST ≤ 普通线段 zorder（即 ≤ 2），不得遮挡关键辅助线。

### G2 角弧半径

- 单角：`r ∈ [0.08, 0.14] × L_ref`，默认 `0.10 × L_ref`。
- 同顶点多角分层：相邻两弧半径差 `Δr ≥ 0.05 × L_ref`。
- 弧外标签距离弧的额外偏移：`0.045 × L_ref`。
- 大角（>120°）取下限，小角（<30°）取上限以避免标签贴线。

### G3 等边 tick

- 单 tick 长度：`tick_len = 0.040 × L_ref`，且 MUST ≤ 该线段长度的 12%。
- 多 tick（num_marks≥2）间距：`0.025 × L_ref`，单 tick 长度同步缩短为 `0.030 × L_ref` 以避免视觉过重。
- tick 颜色第一组红、第二组绿、第三组橙（与等边语义一致即可）。

### G4 点标记与点标签

- 点标记 `markersize ≤ 5`（约 `0.006 × L_ref` 视觉半径）。
- 点标签到点心距离 `d_label ∈ [0.04, 0.08] × L_ref`，默认 `0.055 × L_ref`。
- **点标签距离上限 `0.08 × L_ref` MUST 由 `LayoutAuditor.check()` 强制**——超出即报 `G4`。
  唯一例外是 G16 引线模式（标签放在远端空白、用引线连回点）。
- 点标签 MUST 带白底 bbox（`facecolor='white', alpha=0.78`）。
- 点标签方向选择 MUST 满足 G6 的避碰约束，禁止整张图共用一组 `dx, dy`。
- **点标签 MUST 通过 `label_point` helper 放置**（除非 G16 引线模式手动指定引线终点）。
  禁止用裸 `ax.text` 标注点字母，因为会绕过 G15 自适应方向与 G16 引线机制。
- 当点处在 2+ 条线交点附近（垂足、内心、外接圆心等），本地就近方向全部冲突时，
  MUST 走 G15（自适应方向搜索）或 G16（引线标注），不得人为把标签甩到 0.08·`L_ref` 之外。

### G15 自适应点标签方向（MUST）

- `label_point(...)` 支持 `direction='auto'`（默认）。未指定 `direction` 时，**默认走 auto**。
- 候选方向：8 个等分向量 `(±1,0) / (0,±1) / (±1,±1)/√2`。
- 对每个候选，offset 默认从 `0.055·L_ref` 起，依次尝试 `0.055, 0.07, 0.08`：
  1. 估算 label bbox（数据坐标系：`width ≈ 0.06·L_ref`, `height ≈ 0.04·L_ref`，以 anchor 为中心）；
  2. 计算该 bbox 到所有已登记线段的最小距离 `min_d`；
  3. 若 `min_d ≥ δ_safe`（= `0.025·L_ref`），该候选合格。
- 在合格候选中选 `min_d` 最大者；并列时偏向"远离附近点群质心"的方向。
- 8 个候选在 3 个 offset 档位下均不合格 → 返回 `None`，调用方走 G16 引线。
- **不**考虑 G6b（文字 ↔ 文字）冲突——这部分由 auditor 在 `check()` 时统一收口，
  若报 `G6b`，开发者调整 `direction` 或减小 `offset_ratio` 即可。

### G16 引线标注（callout，MUST，硬性场景）

- 触发条件：G15 全部候选方向仍冲突；或点本地 `0.08·L_ref` 范围内**所有** 8 方向都至少与 1 条非自身线段相交。
  典型场景：垂足（G3 在 AC ∩ DG 交点处）、内心、外接圆心、三角形中心等。
- 做法：
  1. 调用 `label_point(ax, P, name, leader=(lx, ly), scale=L, ...)`；
  2. 标签放置在 `(lx, ly)`，可以远离 `0.08·L_ref` 范围（不再受 G4 距离上限约束）；
  3. 从 `P` 到 `(lx, ly)` 画一条细引线（`linewidth=0.6, color='#666', zorder=4`，与原图风格一致）；
  4. 引线作为**已登记线段**添加到 auditor：`add_segment(P, (lx, ly), owner_points={name})`，
     该 owner 集合让 G6 不会判定"标签压在引线上"是冲突；
  5. `(lx, ly)` 选取规则：落在 `place_legend_auto` 同款的"四象限离所有线段最远"评分位置，
     或开发者手动指定并已在脚本中验证为空白的角。
- 引线标签的 `register_text` MUST 传 `is_leader=True`，
  `LayoutAuditor.check()` 的 G4 检查会跳过这类标签。
- 引线本身画完后 MUST `set_active_auditor` 仍在激活窗口内（即 auditor 已捕获该引线段）。

> 真实反例（013 step7_case3_proof 之前版本）：G 标签用裸 `ax.text` 放到 `G3[1] - 0.14·L`，
> 偏移 1.54 个单位（远超 G4 上限 0.88），穿过 BC 边落在三角形外。
> 修复后应走 G15：`label_point(ax, G3, 'G', direction='auto', scale=L)`，
> auto 选 (0, 1)，label 落在 `(1.5, 2.11)`，与 AC / DG 边均无 G6 冲突。

### G5 线段标签

- 沿法向偏移 `offset ∈ [0.04, 0.08] × L_ref`，默认 `0.055 × L_ref`。
- 偏移方向 MUST 取"远离其他线段"的一侧；若两侧都贴线，MUST 减小 offset 而不是改方向到两线之间。
- 线段标签 MUST 带白底 bbox。

### G5b 线段标签 MUST 贴近其主线段（防漂离）

- 线段标签 bbox 到**其所标注的那条线段**的距离 MUST `≤ 0.12 × L_ref`。
  超出即视为"漂离"——读者无法判断它标的是哪条线（auditor 报 `G5b`）。
- 因此 `offset_ratio` 不得无脑放大来躲避碰撞；若标签既要躲开别的线（G6）又要贴近主线（G5b）发生冲突，
  MUST 改用更短的引线/换标签位置，而不是把标签甩到远处。
- `place_segment_label(...)` 会自动登记 `owner_seg`，auditor 据此判定 G5b，无需手动。

### G6 几何避碰阈值（核心）

定义"安全距离" `δ_safe = 0.025 × L_ref`。MUST 满足（auditor 用**真实 bbox 矩形**判定，非中心点）：

| 对 | 距离要求 |
|---|---|
| 标签 bbox ↔ 任意非自身相关线段 | 矩形到线段距离 `≥ δ_safe` |
| 标签 bbox ↔ 任意其他标签 bbox（G6b） | 矩形 MUST NOT 相交（含 `0.3·δ_safe` 外扩） |
| 直角符号外缘 ↔ 任意非垂足相关线段 | `≥ 0.5·δ_safe` |
| 角弧 ↔ 邻近角弧（同顶点） | 半径差 `Δr ≥ 0.05 × L_ref`（见 G2） |
| 说明框 bbox ↔ 任意几何线段（G12） | 矩形到线段距离 `≥ δ_safe` |

### G7 点群密集规则

若任意两个被标注点 `P, Q` 满足 `|P − Q| < 0.15 × L_ref`：
- 二者点标签方向（`dx, dy` 单位向量）夹角 MUST ≥ 90°；
- 二者 MUST NOT 同时使用同一颜色文字框。
- 推荐：先在脚本里写出 `cluster = {'D': (+1,-1), 'H': (-1,+1), 'O': (+1,+1)}`，再传给 `label_point`。

### G7b 极密点群（< 5%·L_ref）禁止双标（MUST）

- 若两个**几何上需要的**点 `P, Q` 在当前图坐标中 `|P − Q| < 0.05 × L_ref`（如 010 中 D 与 H2 仅相距 ~3.5%·L_ref）：
  即便方向夹角 ≥ 90°，标签 bbox + 点标记仍会不可避免地视觉粘连，G7 不再够。
- MUST 选其一：
  1. 当前 step 只标注其中一个点（另一个不调用 `label_point`），或
  2. 把另一个点 `alpha ≤ 0.35` 淡显（包括其点标记和标签），或
  3. 用引线 callout 把其中一个标签拉到远处空白区。
- auditor 已实现 G7b 自动检查；触发时 `check()` 会列出 `G7b extreme cluster ...`。

### G8 zorder 分层（默认值，禁止跳层）

| 层级 | 元素 |
|---|---|
| 1 | 区域填充、直角符号 |
| 2 | 普通边、普通辅助线 |
| 3 | 等边 tick、角弧 |
| 4 | 关键辅助线虚线主体（如 `AO`） |
| 5 | 关键辅助线"补缺"实线段、点标记 |
| 6 | 文字标签（点名、线段名、角标） |

### G9 字号约束

- 顶点名：12–14。
- 线段名 / 角标：10–12。
- 标题：13–15。
- 字号上限：`fontsize ≤ 28 × (L_ref / 总图幅短边像素长 inch)`，不要在小图上用 16+ 字号。

### G10 步骤元素隔离

- 每个 `step*.png` MUST 只**强调**当前步骤新增或讨论的几何对象。
- 前置上下文（前一步已建立、当前步骤不直接讨论的元素）MUST 满足以下其一：
  - `alpha ≤ 0.35` 淡显，或
  - 直接省略（仅保留必要的形状骨架）。
- 反例（010 step1）：同时画了 ∠A/∠B/∠C/AO/l/D/M/H/N/E 全部，导致 H/D/M 三点拥挤。

### G11 自检（每张图必须执行，自动登记 + bbox 感知）

> ⚠️ **教训（010 deepseek 重写）**：旧版 `LayoutAuditor` 是"手动登记制"——模型只 `add_point` 了点，
> 没登记自由文字框 / 段标签 / 角标，于是 `check()` 报 0 违规却放过了真实重叠（假 PASS）。
> 新版改为**自动登记 + 真实 bbox 矩形相交**，从源头消除"忘记登记"。

> ⚠️ **教训补充（010 第二轮）**：DS 把 `LayoutAuditor` 创建在**绘图之后**，
> 导致 `set_active_auditor(auditor)` 调用时所有 `label_point` / `place_segment_label`
> / `annotate_box` 已经画完，自动登记从未触发，`auditor.texts` 永远是空——
> `check()` 仍假 PASS。新增 **G0** 检查会立刻判 FAIL。

- **G0 MUST 严格遵守的构造顺序**：

  ```text
  fig, ax = plt.subplots(...)
  autoscale(ax, key_points)                # 先固定坐标范围
  L = compute_visual_scale(ax)             # 再算 L_ref
  auditor = LayoutAuditor(ax, name)        # ① 创建 auditor
  set_active_auditor(auditor)              # ② 开启自动登记
  draw_triangle / draw_aux_line / draw_ao  # ③ 在激活窗口内绘几何
  draw_right_angle(...)                    #    （记住把返回 size 给 add_right_angle）
  label_point / place_segment_label / draw_angle_arc(label=) / place_legend_auto
  auditor.add_segment(... owner_points=...)# ④ 几何线段 / 直角符号手动登记
  set_active_auditor(None)                 # ⑤ 关闭自动登记
  violations = auditor.check()             # ⑥ 自检
  assert not violations, violations
  fig.savefig(...)                         # ⑦ 保存
  ```

  把 ① ② 放在 ③ 之后是常见错误——auditor 看不到任何文字，所有 G6/G6b/G7b/G14
  会"假 PASS"。auditor 的 `check()` 已能识别"ax 上有文字 artist 但 auditor.texts 为空"
  这种异常并报 G0。

- 开启活动 auditor 后，`label_point` / `place_segment_label` / `draw_angle_arc(label=...)` / `annotate_box` 的文字**自动登记**，模型 MUST NOT 依赖手动登记每个标签。
- 几何标记（线段 `add_segment`、直角符号 `add_right_angle`）仍 MUST 手动登记，因为它们不产生文字。
- `check()` 用 matplotlib renderer 取得每段文字的**真实包围盒**，按矩形相交判断重叠（取代旧的中心点距离）。
- **`check()` 返回非空即判 FAIL**：MUST 修复到返回空列表后再 `savefig`；MUST NOT 把违规当 warning 打印后照常保存。

```python
fig, ax = plt.subplots(...); autoscale(ax, key_points)
L = compute_visual_scale(ax)
auditor = LayoutAuditor(ax, 'step1')
set_active_auditor(auditor)             # ★ 必须在所有 draw_*/label_* 之前
draw_triangle(ax, A, B, C, names=('A','B','C'))
sz = draw_right_angle(ax, H, (1,0), (0,1), scale=L)
auditor.add_right_angle(H, sz)
label_point(ax, A, 'A', direction=(-1, -1), scale=L)   # 文字自动登记
# ... 其他绘图 ...
set_active_auditor(None)
violations = auditor.check()
assert not violations, f'step1 layout VIOLATIONS: {violations}'
```

### G14 直角符号方框 ↔ 其他已标注点（MUST）

- `draw_right_angle` 在 H 处占据约 `size × size` 的方形区域。
- 该方形 MUST NOT 套住或贴近**另一个**已 `label_point` 的点（除 H 自身/重合垂足外）。
- 命中即为 G14 违规，处理：减小 `size_ratio`（最低 0.03），或把另一点淡显，或选 G7b 的方案 1。

### G6b 文字 ↔ 文字（bbox 矩形相交，MUST）

- 任意两段文字的**真实包围盒** MUST NOT 相交（含 `0.3·δ_safe` 外扩）。
- 这条专治"中心点不近但宽标签实际压住"的情况，如 `C(M)`、`△AHC≡△AHN`、`BN+CE=CD`。
- auditor 已自动覆盖；模型只需保证 `check()` 无 G6b 项。

### G12 说明框 / 公式框置于空白区（MUST）

- 大注解框（全等结论框、公式框、图例）MUST NOT 与任何几何线段相交。
- MUST 用 `place_legend_auto(ax, text, segments=[...], scale=L)` 自动在四角中选"离所有线段最远"的位置；或手动放在已验证为空白的区域。
- MUST NOT 随手丢在图正中（010 step2 的 `△AHC≡△AHN` 框压住三角形/角弧/H 点即为反例）。
- auditor 对 `is_box=True` 的文字做专门的 G12 检查。

### G13 高亮已有线段：改造原线，不叠加箭头（MUST）

- 高亮一条**已经画出**的线段（如 `CD`、`CE`、`BN`）时，MUST 通过以下手段之一：
  - 加粗 / 改高亮色重画该线段；
  - 或沿法向**平行偏移**一条高亮线，不覆盖原线。
- MUST NOT 用 `ax.annotate('', xytext=..., arrowprops=dict(arrowstyle='<->'))` 在原线正上方叠加双向箭头——箭头会穿过端点（如 `D`、`H`）和其它标注，等于再加一层遮挡。
- 反例（010 step3/step5）：CD/CE/BN 全用双向箭头叠加，箭头穿过 D/H 点。

### G9 字号约束

- 顶点名：12–14。
- 线段名 / 角标：10–12。
- 标题：13–15。
- 字号上限：`fontsize ≤ 28 × (L_ref / 总图幅短边像素长 inch)`，不要在小图上用 16+ 字号。

> 模板 `_template_geometry_figures.py` 已提供 `LayoutAuditor`（自动登记+bbox）、`compute_visual_scale`、
> `set_active_auditor`、`annotate_box`、`place_legend_auto`。
> 其他工具函数（`draw_right_angle` / `mark_equal_sides` / `place_segment_label` / `label_point` / `draw_angle_arc`）
> MUST 通过 `scale=L_ref` 参数调用，不再接受写死的 0.18 / 0.08 类绝对值。

---


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

### 标注与图层避碰（011实践，后续默认遵循）

这部分是 011 题里真实踩坑后总结出来的规则，默认适用于所有 `geometry_figures.py`。

**问题类型清单**：

- 点名压在线段上，例如 `N`、`H` 与蓝色直线重叠。
- 线段名离目标线段太远，例如 `BN` 虽不重叠，但阅读时不容易判断归属。
- 局部区域标签过密，例如 `D/H/O` 全部堆在垂足附近。
- 直角符号盖住辅助线末端，导致 `AH` 或 `AO` 在交点附近看似断裂。
- 虚线节距刚好落在关键点附近，造成“其实没被遮挡，但视觉上断掉”的错觉。

**原则一：标签优先沿法向偏移，而不是固定只往上/下挪**

线段名应沿线段法向偏移，这样既贴近对象，又不容易压线：

```python
def place_segment_label(ax, p1, p2, text, color, offset=0.24):
    mid = (p1 + p2) / 2
    d = p2 - p1
    L = np.linalg.norm(d)
    perp = np.array([-d[1], d[0]]) / (L + 1e-9)
    if perp[1] < 0:
        perp = -perp
    ax.text(mid[0] + offset * perp[0], mid[1] + offset * perp[1], text,
            color=color, ha='center', va='center', fontsize=12,
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.78, pad=0.12))
```

**经验值**：

- 短线段标签（如 `BN`）偏移宜小，通常 `0.12 ~ 0.18`。
- 中长线段标签（如 `CD`、`CE`）偏移可用 `0.22 ~ 0.30`。
- 如果标签虽不重叠但“离得太远”，优先减小法向偏移，而不是改成别的方向。

**原则二：点名与点本体分开处理，必要时单独指定偏移**

不要指望一个统一的 `dx/dy` 适用于所有点。像 `D/H/O` 这种局部密集区，必须单独摆位。

推荐做法：

- `D`：优先放在点的右下或右侧，避开角平分线。
- `H`：优先放在点的左下，避开直角符号和过点直线。
- `O`：若只是表示在线 `AO` 上，不必紧贴 `D`；可沿 `AO` 再下移一段，避免与 `D/H` 扎堆。

**011 的直接教训**：`D/H/O` 都靠近垂足区域时，不要只做“微调 0.03”；应先把三者职责分开，再决定谁靠近点、谁沿辅助线远离。

**原则三：文字必须有白底容错层**

对于点名、线段名、关键角标，默认使用浅白底文字框：

```python
TEXT_BOX = dict(facecolor='white', edgecolor='none', alpha=0.78, pad=0.12)
ax.text(x, y, 'D', bbox=TEXT_BOX)
```

这不是美观问题，而是容错问题。示意图里线多、色多、交点密时，没有白底就很容易出现“明明没重合，但看不清”。

**原则四：图层顺序必须显式写出，不要依赖 matplotlib 默认顺序**

推荐图层：

- 底层：填充区域、直角符号
- 中层：普通边、普通辅助线、点标记
- 上层：关键辅助线（如 `AO`）、高亮线段
- 最上层：文字标签

可直接按这个顺序控制：

```python
ax.plot(..., zorder=1)   # 直角符号
ax.plot(..., zorder=2)   # 普通线
ax.plot(..., zorder=4)   # 关键辅助线 AO
ax.text(..., zorder=6)   # 标签
```

**011 的直接教训**：

- 把 `AO` 提高图层仍不一定够，因为点标记本身也可能盖住 `AO`。
- `H` 这种落在关键辅助线上的点，点标记层级应低于关键辅助线，文字层级再高于线。

**原则五：虚线辅助线要额外检查“视觉断裂”**

虚线有一个特有风险：

- 实际上线没问题；
- 但 dash gap 正好落在关键交点附近；
- 用户会感觉“末端没画出来”。

推荐做法二选一：

1. 调整 `linestyle` / dash pattern，让空档不要落在关键点附近。
2. 在关键点附近沿同方向补一小段实线。

011 最稳定的方案是第 2 种：整条 `AO` 保持虚线，但在 `H` 附近补一小段实线，保证 `AH` 末端连续可见。

```python
def draw_ao(ax, A, D, H, ao_dir, color='#9b59b6'):
    AO_end = A + 1.05 * (D - A)
    ax.plot([A[0], AO_end[0]], [A[1], AO_end[1]],
            color=color, linewidth=1.6, linestyle='--', zorder=4)
    cap = 0.22
    p_start = H - cap * ao_dir
    p_end = H + cap * ao_dir
    ax.plot([p_start[0], p_end[0]], [p_start[1], p_end[1]],
            color=color, linewidth=1.8, zorder=5)
```

**原则六：直角符号不要压住关键辅助线**

直角符号是“说明性标记”，不是主角。默认应满足：

- 直角符号层级低于关键辅助线；
- 直角符号大小只够表达垂直关系，不要大到侵占邻域；
- 若直角符号与点名冲突，先保留点名和关键辅助线，再缩小或下沉直角符号。

**原则六补充：所有几何线段 MUST 登记到 auditor（含辅助线/构造线）**

> 这是和"忘记登记文字"同类的隐患：auditor 只能检查它知道的线段。

- 三角形三边：用 `draw_triangle(ax, A, B, C, names=('A','B','C'))`，会自动登记三条边。
- 关键辅助线 `AO`：用 `draw_ao(...)`（已自动登记），或显式传 `owners`。
- 其它构造线/辅助线（如垂线 `l`、中线、延长线）：**MUST NOT 直接 `ax.plot` 画几何线**，
  改用 `draw_aux_line(ax, p1, p2, owners={...})`，它在绘制的同时把线段登记给 auditor。
- 反例：DeepSeek 在 010 用裸 `ax.plot` 画 `AO`/`l`，导致 `?` 角标恰好压在 `AO` 上而 auditor 报 0 违规。
  根因不是"模型不小心"，而是"画几何线的入口没有强制登记"——已用 `draw_aux_line`/`draw_ao` 堵住。

```python
# ✅ 自动登记：
draw_triangle(ax, A, B, C, names=('A', 'B', 'C'))   # 三边
draw_ao(ax, A, D, H, ao_dir, scale=L)               # AO（默认 owners={'A','D'}）
draw_aux_line(ax, B, foot, owners={'B', 'F'},        # 垂线 l 等
              color='#e74c3c', linestyle='-')
# ❌ 禁止：ax.plot([A[0],D[0]],[A[1],D[1]], '--')  # 几何线未登记，避碰检查失效
```

**原则七：每次改图后必须做“局部可读性复查”**

不要只检查“图生成成功”。至少要人工复查以下项目：

- `N/H/D/O` 是否压线。
- 线段名是否明显对应到正确线段。
- `AO`、垂线、构造线在关键点附近是否连续可见。
- 改动一处后，是否在其他图引入回归（例如全局偏移影响 step1 但 step4 更差）。

建议顺序：先看最拥挤的图（通常是 general proof figure / midpoint figure），再抽查其余图。

**一个可复用的检查清单**：

```text
[ ] 点名不压线
[ ] 线段名贴近目标线段
[ ] D/H/O 等密集区域已疏开
[ ] 直角符号不盖住关键辅助线
[ ] 虚线在关键点附近不出现视觉断裂
[ ] 调整后无跨图片回归
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
