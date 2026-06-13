# AGENT 硬性约束（MUST）

> 本文件是所有大模型执行解题任务时**必须首先并完整阅读**的硬性约束。
> 任一 MUST 条款被省略或重新解释，本次任务即视为**未完成**。
> 实现细节参考：[problem_solve_steps.md](problem_solve_steps.md)、[geometry_drawing_guide.md](geometry_drawing_guide.md)、[webpage_guide.md](webpage_guide.md)。
> 这些参考文档**不能**覆盖本文件的 MUST 条款，只能在本文件未规定的细节上提供做法。

---

## 关键词约定

- **MUST / 必须** — 不允许省略、变通或自行解释为"建议"。
- **MUST NOT / 禁止** — 出现即判 FAIL。
- **OPTIONAL / 可选** — 仅此词代表真正可选；"建议""推荐""默认"在本规范中**等同于 MUST**。
- **本轮显式覆盖** — 仅指用户在当前对话中明确以自然语言写出"用 X 替代 Y"。模型不得自行推断为"显式覆盖"。

---

## R1 知识范围（MUST）

- 解题方法 MUST 限制在**七年级**范围内。
- 涉及高中或竞赛知识时，MUST 在解答中明确指出，并改写为七年级可理解的等价方法；不得直接使用。
- 不能使用三角函数、勾股定理，优先使用几何方法，例如使用相似三角形、等边三角形、倍长中线、构造全等三角形，截长补短、三线合一等。

## R2 默认技术栈（MUST，除非用户在本轮显式覆盖）

- 几何绘图：**Python matplotlib**，输出 PNG。
  - MUST NOT 用 SVG / Mermaid / ASCII art / 手绘文字示意 替代 PNG。
  - MUST NOT 把绘图代码内联在 HTML 里替代 `geometry_figures.py`。
  - 生成的 PNG 中，点名/线段名/角标/直角符号 MUST 清晰可读；MUST NOT 与线段、虚线辅助线、点标记或其他标签发生明显遮挡或重叠。关键辅助线（如角平分线、垂线）在交点附近 MUST 连续可见，不得因虚线空档或图层顺序看似“断掉”。
  - **MUST 遵循 [geometry_drawing_guide.md](geometry_drawing_guide.md) 的"绘图执行标准（G-标准）"**，所有视觉元素（直角符号尺寸、角弧半径、等边 tick、点/线标签偏移）MUST 按图幅参考长度 `L_ref` 归一；MUST NOT 直接写绝对坐标经验值（如 `size=0.18`、`offset=0.24`）。
  - 每张图 MUST 在绘图前 `set_active_auditor(auditor)`、绘图后 `LayoutAuditor.check()`（自动登记全部文字 + 真实 bbox 相交判定）；`check()` 返回非空即 FAIL，MUST 修复到空列表后再保存，MUST NOT 把违规当 warning 打印后照常保存。**构造顺序 MUST 是**：`autoscale → compute_visual_scale → LayoutAuditor(...) → set_active_auditor(auditor) → 绘几何/标签 → set_active_auditor(None) → check()`，把 auditor 创建/激活放在绘图后会被新增 G0 自检立即判 FAIL（`auditor.texts` 为空但 ax 已有文字）。
  - 说明框 / 公式框 MUST 用 `place_legend_auto` 放在空白区，MUST NOT 压住几何对象（G12）；高亮已有线段 MUST 改造原线（加粗/变色/平行偏移），MUST NOT 叠加穿过端点的双向箭头（G13）。
  - 所有几何线段（含辅助线/构造线 AO、垂线 l 等）MUST 登记到 auditor：三边用 `draw_triangle(..., names=('A','B','C'))`，辅助线用 `draw_aux_line(ax,p1,p2,owners=...)` 或 `draw_ao(...)`；MUST NOT 用裸 `ax.plot` 画几何线（否则压在该线上的标签 auditor 查不到）。线段标签 MUST 贴近其主线段（距离 ≤ 0.12·`L_ref`），不得为躲避碰撞而把标签甩到远处（G5b）。
  - 每个 `step*.png` MUST 只显式高亮当前步骤新增/讨论的几何对象；前置上下文 MUST 用 `alpha ≤ 0.35` 淡显或省略。
  - **原题重绘，禁止直接引用原图照片**：若原题包含插图，MUST 用 matplotlib 重新绘制该图形（通常作为 `step0_original.png`），MUST NOT 以任何形式直接引用或嵌入原始题图的扫描/截屏/照片文件作为解题配图。重绘图形的整体朝向与线段位置关系 MUST 与原图一致（见下一款）。
  - **原图一致性**：所有新绘制的几何图形 MUST 与原图的**整体朝向**（图形在画布中的摆放角度、顶点方位）和**线段位置关系**（线段之间的相对位置、交叠次序、包围关系）保持一致。MUST NOT 擅自旋转、镜像翻转、平移重组或以其他方式改变原图的空间拓扑关系。允许为了添加辅助线或分步演示而做非破坏性扩展（不改变已有元素位置）。
- 网页：**TailwindCSS + MathJax 3 + JSXGraph 1.8.0**，全部通过 CDN 引入。
- 中文字体：MUST 通过项目内 `font/STHeiti Medium.ttc` 以**绝对路径**加载（参见 [geometry_drawing_guide.md](geometry_drawing_guide.md) 字体章节）。
- Markdown 公式：MUST 使用纯文本格式（如 `(1/2)`、`S△ABC`、`²`），MUST NOT 使用 `$...$` / `$$...$$`（HTML 内 MathJax 除外）。

## R3 必出文件（MUST，缺一即 FAIL）

对编号 `NNN` 的题目，MUST 在 `math/NNN/` 目录下产出以下文件：

| 文件 | 说明 |
|---|---|
| `NNN_solution.md` | Markdown 解题文档 |
| `NNN.html` | 交互式网页 |
| `geometry_figures.py` | 绘图脚本，`python geometry_figures.py` 必须无报错 |
| `step*.png` | 至少覆盖每个解题关键步骤；分类讨论每种情况 MUST 有独立图或对比图 |

- MUST NOT 创建并列的同题号变体目录（如 `003/`）；同一题号只允许一个目录。
- 文件命名 MUST 严格遵循 [problem_solve_steps.md](problem_solve_steps.md) 附表。

## R4 网页必含组件（MUST，缺一即 FAIL）

HTML 文件 MUST 包含以下全部组件：

1. 顶部**中英双语切换**按钮（id=`langZh`, `langEn`）+ 完整 `i18n = { zh:{...}, en:{...} }` 字典 + `setLang()` 函数。
   - 即使英文未实际翻译，结构和键 MUST 完整存在。
   - **每个**可见文本元素 MUST 带 `data-i18n="..."` 属性。
2. 步骤卡片系统（`.step-card` + `goToStep(n)`）。
3. 进度指示器（圆点或进度条）+ `1/N` 文本。
4. 键盘导航（`ArrowLeft` / `ArrowRight` 切换步骤）。
5. 每个解题关键步骤 MUST 提供 ≥ 2 个可展开提示问答（`hint-btn` + `hint-content`）。
6. 末尾**思路梳理 / 总结**页：包含最终答案、解题流程、知识点标签、解题技巧。
7. CDN：MUST 引入 TailwindCSS、MathJax 3；如使用交互几何 MUST 引入 JSXGraph 1.8.0。

> 实现起点 MUST 是 `templates/_template.html`（见 R7），禁止从零编写 HTML。

## R5 一致性（MUST）

- Markdown 与 HTML 的**题目原文、解题步骤、公式、最终答案** MUST 逐字对应。
- 所有 `![](...)` / `<img src=...>` 引用的图片文件 MUST 真实存在于同目录。
- HTML 中所有 `data-i18n` 键 MUST 在 `i18n.zh` 中有对应条目。

## R6 完成门槛（MUST）

- 任务的**最终回复** MUST 原样贴出 [checker.md](checker.md) §"自检报告模板" 中的报告，并对每一项填写 PASS / FAIL。
- 任一项 FAIL → 任务未完成，MUST 修复后重新自检并重新贴报告。
- MUST NOT 使用"全部通过""已检查"等概括语代替逐项报告。

## R7 模板优先（MUST）

- HTML、Markdown、Python 绘图脚本 MUST 从 `templates/` 目录下的骨架复制后再填充：
  - `templates/_template.html`
  - `templates/_template_solution.md`
  - `templates/_template_geometry_figures.py`
- 骨架中已存在的双语切换、进度条、键盘导航、字体加载、工具函数 MUST NOT 删除。

---

## 常见违规（出现即 FAIL）

- ❌ 用 SVG / Mermaid / ASCII / Markdown 表格 替代 matplotlib PNG
- ❌ 直接引用/嵌入原始题图的扫描、截屏或照片文件作为解题配图，未用 matplotlib 重绘
- ❌ 图片中标签与线段、虚线、直角符号、点标记明显重叠，或关键辅助线在交点附近看似断裂
- ❌ 直角符号尺寸 > 图幅参考长度 `L_ref` 的 5%，或 > 最近邻线段长度的 8%（违反 G1）
- ❌ 视觉元素用绝对坐标经验值（如 `size=0.18`、`offset=0.24`），未按 `L_ref` 归一（违反 G-标准前置规则）
- ❌ 同一 `step*.png` 同时显示当前步骤无关的几何对象，且未做 `alpha ≤ 0.35` 淡显（违反 G10）
- ❌ 局部点群（两点距离 < 0.15·`L_ref`）的标签方向夹角 < 90°（违反 G7）
- ❌ 极密点群（< 0.05·`L_ref`）仍同时全 alpha 标注两个点，标签和点标记视觉粘连（违反 G7b）——MUST 只标一个 / 另一个淡显 / 用引线 callout
- ❌ 直角符号方框套住或贴近另一个已标注点（违反 G14）——缩小 size_ratio 或淡显另一点
- ❌ 说明框 / 公式框压住几何对象，未用 `place_legend_auto` 放到空白区（违反 G12）
- ❌ 用双向箭头叠加在已有线段上做高亮，箭头穿过已标注点（违反 G13）
- ❌ 几何辅助线/构造线（AO、垂线 l）用裸 `ax.plot` 绘制未登记，导致标签压在该线上但 auditor 未报警（违反原则六补充）
- ❌ 线段标签漂离其主线段（距离 > 0.12·`L_ref`），读者无法判断它标的是哪条线（违反 G5b）
- ❌ **点标签到点心距离 > 0.08·`L_ref`**（违反 G4 上限；G16 引线模式除外）
- ❌ 点的字母标使用裸 `ax.text` 绕过 `label_point`（失去 direction='auto' / leader 机制；违反 G15/G16）
- ❌ 点处在 2+ 直线交点附近（如垂足、内心），本地无空位放标签却未用 G16 引线（违反 G16）
- ❌ 几何图脚本未 `set_active_auditor` 自动登记，或 `check()` 返回非空仍直接保存（违反 G11）
- ❌ `LayoutAuditor` 创建/激活在绘图**之后**调用，导致 `auditor.texts` 为空、所有 bbox 检查假 PASS（违反 G0；正确顺序：autoscale → 创建 auditor → set_active → 绘图 → set_active(None) → check）
- ❌ 网页只有中文，没有 `setLang` / `data-i18n` / `langZh` / `langEn`
- ❌ HTML 内嵌 LaTeX 公式但未引入 MathJax
- ❌ Markdown 中 `![](stepX.png)` 引用了未生成的图片文件
- ❌ 自检报告缺失，或只写"全部通过"未逐项列出
- ❌ 创建 `NNN_<modelname>/` 之类的并列变体目录
- ❌ 把"建议/默认"理解为"可选"
- ❌ 解题方法超出七年级（如直接用三角函数、向量、解析几何高级技巧）
- ❌ 原题有插图，但新绘图形整体朝向、线段相对位置关系明显偏离原图（旋转、镜像、重新排布等）
