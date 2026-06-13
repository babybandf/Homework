# 初中数学习题解析助手

> 帮助孩子更好地理解解题过程，通过可视化插图、流程梳理和思路引导，让数学学习更轻松。

## 项目简介

利用大模型辅助生成：

- **可视化插图** — Python matplotlib 绘制几何/函数图形，直观展示题目和解题过程
- **分步解析** — 将复杂题目拆分为简单步骤，逐步引导理解
- **思路梳理** — 总结解题技巧和关键知识点，培养数学思维
- **交互式网页** — 可交互的 HTML 页面，支持逐步浏览和提示探索
- **复习报告** — 跨题目总结解题规律、梳理知识体系、诊断薄弱环节

## 项目结构

```
Homework/
├── CLAUDE.md                         # Claude Code 项目指南
├── AGENT.MD                          # 任务执行硬性约束（知识范围、技术栈、必出文件）
├── checker.md                        # 解题成果自检清单 + 报告模板
├── problem_solve_steps.md            # 详细解题步骤执行规范
├── geometry_drawing_guide.md         # 几何图形绘制规范（G-标准 + LayoutAuditor）
├── webpage_guide.md                  # 交互式网页生成规范
│
├── math/
│   ├── Geometry/                     # 几何题
│   │   ├── 001/ ... 014/             # 已完成的14道几何题
│   │   └── report/
│   │       └── 001to014/             # 几何题全面复习报告
│   │           ├── geometry_mastery_report.md   # 复习报告（含5大模型配图）
│   │           ├── model_figures.py             # 模型配图绘制脚本
│   │           └── model_assets/                # 配图PNG文件
│   │
│   └── Algebra/                      # 代数题（规划中）
│       └── 001/                      # 已完成的第1道代数题
│
├── templates/                        # 文件骨架（MUST从骨架复制后填充）
│   ├── _template.html                # 交互式网页骨架
│   ├── _template_solution.md         # Markdown 解题文档骨架
│   └── _template_geometry_figures.py # matplotlib 绘图脚本骨架
│
└── font/                             # 中文字体（matplotlib 渲染用）
    ├── STHeiti Medium.ttc
    └── STHeiti Light.ttc
```

## 几何题概况

目前已覆盖 **001-014** 共14道七年级几何题，涵盖：

| 核心模型 | 题目 | 关键技巧 |
|:---|:---|:---|
| 手拉手模型（双等边共顶点） | 008, 014 | SAS 全等 → 旋转视角 |
| 角平分线 + 垂线 → 对称 | 001, 010, 011, 013 | ASA 全等 → 等腰/中点 |
| ∠C=2∠B + 角平分线 → 截长补短 | 010, 011 | SAS 全等 → 等量代换 |
| 特殊角 → 构造等边三角形 | 004, 005 | 造 60° → 连锁全等 |
| 分类讨论（等腰/位置） | 003, 006, 007, 009, 013 | 穷举 + 验证 |

> 详细复习报告见 [`math/Geometry/report/001to014/geometry_mastery_report.md`](math/Geometry/report/001to014/geometry_mastery_report.md)

## 使用方法

### 查看交互式网页

```bash
cd math/Geometry/001
python3 -m http.server 8080
# 浏览器打开 http://localhost:8080/001.html
```

### 重新生成几何配图

```bash
cd math/Geometry/001
python3 geometry_figures.py
# 输出 "All figures generated successfully!" 即成功
```

### 查看 Markdown 解题文档

直接用任意 Markdown 预览器打开 `001_solution.md` 等文件。

## 新题初始化流程

```bash
NNN="015"
mkdir -p math/Geometry/$NNN
cp templates/_template.html               math/Geometry/$NNN/$NNN.html
cp templates/_template_solution.md        math/Geometry/$NNN/$NNN_solution.md
cp templates/_template_geometry_figures.py math/Geometry/$NNN/geometry_figures.py
# 然后填充 {{...}} / TODO: 占位内容
```

## 公式显示规范

| 类型 | 示例 | 说明 |
|------|------|------|
| 角度 | `∠ABC = 60°` | 直接使用 Unicode |
| 分数 | `(1/2)` | 避免 LaTeX 分数 |
| 面积比 | `S△AMN / S△ABC` | 纯文本表示 |
| 平方 | `(1/2)²` | 使用上标符号 |
| 重要公式 | `**加粗**` 或 `>` 引用 | 突出显示 |

## 任务完成标准

- 解题方法不超七年级范围（不涉及三角函数、勾股定理）
- 四类必出文件齐全（`*_solution.md`, `*.html`, `geometry_figures.py`, `step*.png`）
- `LayoutAuditor.check()` 返回空列表（标签无重叠、直角符号合规等）
- 逐项填写 [`checker.md`](checker.md) 自检报告，全部 PASS
- Markdown 公式使用纯文本，HTML 引入 MathJax 渲染

## 适用对象

- 七年级学生
- 需要几何/代数解题辅导的初中生
- 希望培养数学思维的学生
