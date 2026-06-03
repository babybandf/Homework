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

## R2 默认技术栈（MUST，除非用户在本轮显式覆盖）

- 几何绘图：**Python matplotlib**，输出 PNG。
  - MUST NOT 用 SVG / Mermaid / ASCII art / 手绘文字示意 替代 PNG。
  - MUST NOT 把绘图代码内联在 HTML 里替代 `geometry_figures.py`。
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
- ❌ 网页只有中文，没有 `setLang` / `data-i18n` / `langZh` / `langEn`
- ❌ HTML 内嵌 LaTeX 公式但未引入 MathJax
- ❌ Markdown 中 `![](stepX.png)` 引用了未生成的图片文件
- ❌ 自检报告缺失，或只写"全部通过"未逐项列出
- ❌ 创建 `NNN_<modelname>/` 之类的并列变体目录
- ❌ 把"建议/默认"理解为"可选"
- ❌ 解题方法超出七年级（如直接用三角函数、向量、解析几何高级技巧）
