# 模板文件目录

> 由 [AGENT.MD](../AGENT.MD) §R7 强制要求：所有解题产出必须从这里复制骨架后再填充。
> **禁止**从零编写 HTML / Markdown / 绘图脚本。

## 使用方法

对编号 `NNN` 的新题目：

```bash
mkdir -p math/NNN
cp templates/_template.html               math/NNN/NNN.html
cp templates/_template_solution.md        math/NNN/NNN_solution.md
cp templates/_template_geometry_figures.py math/NNN/geometry_figures.py
```

随后**只填充占位内容**（`{{...}}` 或 `TODO:` 标记处），骨架中已有的双语切换、进度条、键盘导航、提示问答框架、字体加载等结构 **MUST NOT 删除**。

## 文件清单

| 模板 | 用途 |
|---|---|
| `_template.html` | 交互式网页骨架（双语 + 步骤卡 + 进度条 + 键盘导航 + 提示问答） |
| `_template_solution.md` | Markdown 解题文档骨架 |
| `_template_geometry_figures.py` | matplotlib 绘图脚本骨架（含中文字体加载与工具函数） |

## 绘图模板使用建议

`_template_geometry_figures.py` 现在除了基础的 `draw_triangle`、`draw_angle_arc`、`mark_equal_sides` 之外，还内置了几类用于避免“图能生成，但标注不好读”的 helper。

### 推荐优先使用的 helper

- `label_point(...)`
	- 用于点和点名。
	- 自带白底文字框。
	- 可单独设置点标记和文字的图层（`marker_zorder` / `text_zorder`）。
	- 适合 `H` 这类落在关键辅助线上的点，避免点本身盖住辅助线。

- `place_segment_label(...)`
	- 用于 `BN`、`CD`、`CE` 这类线段名。
	- 标签会沿线段法向偏移，通常比“固定往上挪/往下挪”更稳。
	- 经验值：短线段用较小偏移（如 `0.12 ~ 0.18`），中长线段用 `0.22 ~ 0.30`。

- `draw_right_angle(...)`
	- 用于直角符号。
	- 默认放低图层，减少压住关键辅助线的风险。

- `draw_ao(...)`
	- 用于角平分线 / 关键虚线辅助线。
	- 会在关键点附近补一小段实线，避免虚线空档让线段在视觉上“断掉”。

### 推荐默认图层顺序

- 底层：填充区域、直角符号
- 中层：普通边、普通辅助线、点标记
- 上层：关键辅助线、高亮线段
- 最上层：文字标签

如果图里出现“明明画了但看不见”的情况，优先检查是不是 `zorder` 问题，而不是先怀疑坐标算错。

### 局部密集区域的处理原则

像 `D / H / O` 这类集中在垂足附近的标签，不要共用一套 `dx / dy` 偏移。应按功能分开：

- `D` 贴近点，但避开角平分线
- `H` 避开直角符号和过点直线
- `O` 沿辅助线再下移一段，不要和 `D / H` 扎堆

这类区域如果只做“统一微调 0.02”，通常效果不好。

### 每次改图后的最小复查清单

在 `python geometry_figures.py` 成功之后，至少要人工检查：

```text
[ ] 点名不压线
[ ] 线段名贴近目标线段
[ ] D/H/O 等密集区域已疏开
[ ] 直角符号不盖住关键辅助线
[ ] 虚线在关键点附近不出现视觉断裂
[ ] 调整后无跨图片回归
```

建议先看最拥挤的那张图，再抽查其他图，不要只看第一张题设图。
