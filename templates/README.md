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
