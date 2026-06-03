# 交互式网页生成规范

> ⚠️ 本文档为**实现细节参考**。硬性约束以 [AGENT.MD](AGENT.MD) 为准。

## ⚠️ 本文档的 MUST 条款（其他为参考）

- **M1** HTML MUST 从 `templates/_template.html` 复制后填充，MUST NOT 从零编写。
- **M2** Header MUST 含双语切换按钮（id=`langZh`、`langEn`）+ `setLang()` 函数 + 完整 `i18n = { zh, en }` 字典。
- **M3** 所有可见文本元素 MUST 带 `data-i18n="..."` 属性；新增键 MUST 同时在 `zh` 与 `en` 中填充。
- **M4** MUST 含步骤卡片系统（`.step-card` + `goToStep`）+ 进度指示器（`N/总数`）+ 键盘 ←/→ 导航。
- **M5** 每个解题关键步骤 MUST 提供 ≥ 2 个可展开提示问答。
- **M6** 末尾 MUST 含思路梳理 / 总结页（最终答案 + 解题流程 + 知识点 + 解题技巧）。
- **M7** MathJax / TailwindCSS / JSXGraph（如使用）MUST 通过 CDN 引入。

---


## 技术栈

- **TailwindCSS**：CDN引入，用于页面样式
- **MathJax 3**：CDN引入，用于数学公式渲染
- **JSXGraph 1.8.0**（可选）：CDN引入，用于交互式几何图形（替代静态PNG图片）

```html
<script src="https://cdn.tailwindcss.com"></script>
<script>
    MathJax = {
        tex: { inlineMath: [['$', '$'], ['\\(', '\\)']], displayMath: [['$$', '$$']] }
    };
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<!-- 如使用JSXGraph -->
<script src="https://cdn.jsdelivr.net/npm/jsxgraph@1.8.0/distrib/jsxgraphcore.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/jsxgraph@1.8.0/distrib/jsxgraph.css">
```

## 页面整体布局

```
┌──────────────────────────────────────────────┐
│ Header (sticky): 标题 | 语言切换 | 进度指示器  │
├──────────────────────────────────────────────┤
│                                              │
│   步骤卡片（一次显示一张，其余隐藏）            │
│   ┌────────────────────────────────────┐     │
│   │  步骤编号圆点 + 步骤标题             │     │
│   │  图形区域（JSXGraph 或 PNG图片）     │     │
│   │  文字说明（渐变高亮框/要点框）        │     │
│   │  交互式提示问答（可展开，2-3个）      │     │
│   │  导航按钮（← 上一步 | 下一步 →）     │     │
│   └────────────────────────────────────┘     │
│                                              │
└──────────────────────────────────────────────┘
```

## 步骤卡片系统

### 卡片结构

每个步骤为独立的 `.step-card` div，通过 `goToStep(n)` 切换：

```html
<div id="step0" class="step-card visible mb-8">
    <div class="bg-white rounded-2xl shadow-lg p-8">
        <!-- 标题行 -->
        <div class="flex items-center mb-4">
            <span class="bg-blue-500 text-white w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg mr-3">1</span>
            <h2 class="text-2xl font-bold text-gray-800" data-i18n="s1_title">步骤标题</h2>
        </div>
        <!-- 图形/图片 -->
        <!-- 文字说明 -->
        <!-- 提示问答 -->
        <!-- 导航按钮 -->
    </div>
</div>
```

### 切换显示规则

- 非活动步骤使用 `display: none` 完全隐藏
- 切换时页面自动滚动到顶部
- fadeIn 动画提升体验

```css
.step-card { display: none; }
.step-card.visible { display: block; animation: fadeIn 0.4s ease; }
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
}
```

```javascript
function goToStep(step) {
    document.querySelectorAll('.step-card').forEach(card => {
        card.classList.remove('visible');
        card.style.display = 'none';
    });
    const target = document.getElementById('step' + step);
    target.style.display = 'block';
    void target.offsetHeight; // 强制reflow触发动画
    target.classList.add('visible');
    currentStep = step;
    updateProgress();
    window.scrollTo(0, 0);
}
```

## Header 与导航

### Sticky Header（必需包含语言切换）

```html
<header class="bg-white shadow-md sticky top-0 z-50">
    <div class="max-w-4xl mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
            <h1 class="text-xl font-bold text-gray-800" data-i18n="title">📐 标题</h1>
            <div class="flex items-center space-x-4">
                <!-- 语言切换（必需组件） -->
                <div class="flex items-center bg-gray-100 rounded-full p-0.5">
                    <button onclick="setLang('zh')" class="lang-btn active px-3 py-1 rounded-full text-xs font-medium" id="langZh">中文</button>
                    <button onclick="setLang('en')" class="lang-btn px-3 py-1 rounded-full text-xs font-medium text-gray-600" id="langEn">EN</button>
                </div>
                <!-- 进度指示器 -->
                <div class="flex items-center space-x-2">
                    <span class="text-sm text-gray-600" data-i18n="progress">进度:</span>
                    <div class="flex space-x-1" id="progressDots"></div>
                    <span id="progressText" class="text-sm font-medium text-gray-700 ml-2">1/7</span>
                </div>
            </div>
        </div>
    </div>
</header>
```

> ⚠️ **注意**：语言切换按钮为**必需组件**，默认提供中英双语（中文/EN）。即使当前只实现中文，也需预留 `data-i18n` 属性和 `setLang()` 函数结构，便于后续扩展。

### 进度指示器（两种方案）

**方案A：圆点式**（适合步骤较少，≤7步）

```html
<div class="flex space-x-1" id="progressDots"></div>
<span id="progressText" class="text-sm font-medium text-gray-700 ml-2">1/7</span>
```

**方案B：进度条式**（适合步骤较多，或需要线性进度感）

```html
<div class="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
    <div id="progressBar" class="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500" style="width: 0%"></div>
</div>
<span id="progressText" class="text-sm font-medium text-gray-700">0/7</span>
```

### 导航按钮

每张卡片底部：

```html
<div class="flex justify-between mt-6">
    <button onclick="goToStep(n-1)" class="nav-btn bg-gray-200 text-gray-700 px-6 py-2 rounded-full font-medium" data-i18n="prev">← 上一步</button>
    <button onclick="goToStep(n+1)" class="nav-btn bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-2 rounded-full font-medium" data-i18n="next">下一步 →</button>
</div>
```

```css
.nav-btn { transition: all 0.3s ease; }
.nav-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
```

键盘导航：

```javascript
document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') goToStep(currentStep + 1);
    if (e.key === 'ArrowLeft') goToStep(currentStep - 1);
});
```

## 内容展示组件

### 渐变高亮框（用于题目、重要结论）

```html
<div class="bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl p-6 text-lg leading-relaxed">
    <p>题目文字或重要结论</p>
</div>
```

### 公式/答案框

```html
<div class="bg-gradient-to-r from-red-500 to-pink-600 text-white rounded-xl p-8 text-center">
    <p class="text-lg mb-4">在△BMC中，由三角形内角和：</p>
    <p class="text-3xl font-bold mt-4 py-2 border-t border-white/30">∠BMC = 150°</p>
</div>
```

### 要点框（蓝色左边框）

```html
<div class="bg-blue-50 border-l-4 border-blue-500 rounded-r-lg p-4">
    <strong>🔑 关键发现：</strong><br>
    重要内容说明...
</div>
```

### 数据网格（用于展示多个条件）

```html
<div class="grid grid-cols-3 gap-4 mb-6">
    <div class="bg-blue-50 rounded-lg p-4 text-center">
        <p class="text-blue-600 font-bold text-xl">AB = 12</p>
    </div>
    <div class="bg-green-50 rounded-lg p-4 text-center">
        <p class="text-green-600 font-bold text-xl">AC = 9</p>
    </div>
    <div class="bg-purple-50 rounded-lg p-4 text-center">
        <p class="text-purple-600 font-bold text-xl">BC = 13</p>
    </div>
</div>
```

### 推导过程框（带背景色区分）

```html
<div class="bg-orange-50 rounded-xl p-5 mt-6">
    <p class="font-semibold text-gray-800 mb-3" data-i18n="s4_subtitle">比较△ABE和△AMC：</p>
    <ul class="space-y-2 text-gray-700">
        <li data-i18n="s4_l1">① 条件1 ✓</li>
        <li data-i18n="s4_l2">② 条件2 ✓</li>
    </ul>
    <p class="mt-4 font-bold text-orange-700" data-i18n="s4_conc">∴ 结论</p>
</div>
```

### 图片容器（使用静态PNG时）

```html
<div class="overflow-hidden rounded-xl shadow-lg mb-6">
    <img src="step1_basic.png" alt="描述" class="w-full max-w-2xl mx-auto transition-transform hover:scale-[1.02]">
</div>
```

### JSXGraph 容器（使用交互式图形时）

```html
<div id="board1" class="jxgbox mx-auto rounded-xl overflow-hidden shadow-lg" style="width:500px; height:420px;"></div>
```

## 交互式提示设计

### 提示结构

每个关键步骤提供 2-3 个可展开提示：

```html
<div class="bg-gray-100 rounded-xl p-4 mb-6">
    <p class="font-semibold text-gray-700 mb-3">💭 思考问题</p>

    <div class="space-y-2">
        <!-- 提示按钮 -->
        <div class="hint-btn bg-white rounded-lg p-3 shadow-sm" onclick="toggleHint('h1_1')">
            <span class="inline-block w-5 h-5 rounded-full bg-indigo-400 text-white text-center text-xs leading-5 mr-2">?</span>
            <span class="text-gray-700" data-i18n="h1_1_q">提示问题</span>
        </div>
        <!-- 提示内容（默认隐藏） -->
        <div id="h1_1" class="hint-content hint-correct">
            <span class="text-green-700" data-i18n="h1_1_a">✓ 正确思路的答案内容</span>
        </div>
    </div>
</div>
```

### 提示类型与样式

| 类型 | 图标 | 边框样式 | 用途 |
|------|------|----------|------|
| 正确 | ✓ | `bg-green-50 border-l-4 border-green-500` | 正确思路引导 |
| 错误 | ✗ | `bg-red-50 border-l-4 border-red-500` | 常见错误分析 |
| 中性 | ? | `bg-blue-50 border-l-4 border-blue-500` | 启发性问题、补充说明 |

### 提示CSS

```css
.hint-btn { transition: all 0.3s ease; cursor: pointer; }
.hint-btn:hover { transform: translateX(4px); box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.hint-content { max-height: 0; overflow: hidden; transition: max-height 0.4s ease, padding 0.4s ease; }
.hint-content.show { max-height: 300px; padding: 12px 16px; margin-top: 8px; }
```

## 中英双语切换

### UI组件

```html
<div class="flex items-center bg-gray-100 rounded-full p-0.5">
    <button onclick="setLang('zh')" class="lang-btn active px-3 py-1 rounded-full text-xs font-medium" id="langZh">中文</button>
    <button onclick="setLang('en')" class="lang-btn px-3 py-1 rounded-full text-xs font-medium text-gray-600" id="langEn">EN</button>
</div>
```

```css
.lang-btn { cursor: pointer; transition: all 0.2s; }
.lang-btn:hover { transform: scale(1.05); }
.lang-btn.active { background-color: #4f46e5; color: white; }
```

### 实现方式

1. 所有可翻译文本元素添加 `data-i18n="key"` 属性
2. JS中维护翻译字典 `i18n = { zh: {...}, en: {...} }`
3. `setLang(lang)` 遍历所有 `[data-i18n]` 元素，用 `innerHTML` 替换

```javascript
let currentLang = 'zh';
const i18n = { zh: { /* ... */ }, en: { /* ... */ } };

function setLang(lang) {
    currentLang = lang;
    document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';
    document.getElementById('langZh').classList.toggle('active', lang === 'zh');
    document.getElementById('langEn').classList.toggle('active', lang === 'en');
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (i18n[lang][key] !== undefined) {
            el.innerHTML = i18n[lang][key];
        }
    });
}
```

### 翻译规则

- **需要翻译**：标题、步骤说明、提示问答、按钮文字、知识点标签、解题技巧
- **不需要翻译**：数学符号（∠、△、°）、数字、JSXGraph标注、MathJax公式
- 翻译文本支持内嵌HTML（`<strong>`、`<span>`），用 `innerHTML` 赋值

### data-i18n 命名约定

| 前缀 | 含义 | 示例 |
|------|------|------|
| `title` | 页面标题 | `title` |
| `s{n}_title` | 第n步标题 | `s1_title`, `s2_title` |
| `s{n}_l{m}` | 第n步第m条列表项 | `s1_l1`, `s1_l2` |
| `h{n}_{m}_q` | 第n步第m个提示问题 | `h1_1_q`, `h2_3_q` |
| `h{n}_{m}_a` | 第n步第m个提示答案 | `h1_1_a`, `h2_3_a` |
| `s6_f{n}` | 总结页第n条流程 | `s6_f1`, `s6_f2` |
| `tag{n}` | 知识点标签 | `tag1`, `tag2` |
| `prev/next/restart` | 导航按钮（全局复用） | — |

## JSXGraph 几何图形规范

> 当使用JSXGraph代替静态PNG时适用。

### 每步独立 board

```javascript
(function() {
    const board = JXG.JSXGraph.initBoard('board2', {
        boundingbox: [-1.5, 6.8, 7.5, -1.2],
        keepaspectratio: true,
        showNavigation: false,
        showCopyright: false
    });
    // ... 绘制图形
})();
```

### 坐标预计算

在 `<script>` 顶部统一计算所有关键点：

```javascript
const Ax = 0, Ay = 0;
const Cx = 6, Cy = 0;
const Bx = 3, By = 3 * Math.tan(44 * Math.PI / 180);
// 射线交点等复杂坐标也在此统一计算
```

### boundingbox 设置

- 确保所有点在可视范围内，留 1-1.5 单位边距
- 辅助点（如等边三角形顶点）需扩大范围
- `keepaspectratio: true` 保持等比

### 颜色语义

| 元素 | 颜色 | 用途 |
|------|------|------|
| 原三角形边 | `#2c3e50` | 主体结构 |
| 辅助构造线 | `#9b59b6`（紫色） | 等边三角形等 |
| 关键点 | `#e74c3c`（红色） | 目标点（如M） |
| 全等三角形1 | `#1565c0` + `#bbdefb` | 蓝色系填充 |
| 全等三角形2 | `#f57f17` + `#fff9c4` | 黄色系填充 |
| 结论高亮 | `#c62828` + `#ffcdd2` | 红色系填充 |

## 总结页面

最后一个步骤卡片为总结页，包含：

### 最终答案

```html
<div class="bg-emerald-50 border border-emerald-200 rounded-xl p-6 mb-6">
    <h3 class="font-bold text-emerald-800 mb-3" data-i18n="s6_answer_label">🎯 最终答案</h3>
    <p class="text-2xl font-bold text-center text-emerald-700">∠BMC = 150°</p>
</div>
```

### 解题流程（编号纵向排列）

```html
<div class="flex flex-col space-y-3">
    <div class="flex items-center">
        <div class="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold shrink-0">1</div>
        <div class="ml-3 text-gray-700" data-i18n="s6_f1">步骤描述</div>
    </div>
    <div class="w-0.5 h-4 bg-blue-300 ml-4"></div>
    <!-- 更多步骤... -->
</div>
```

### 知识点标签

```html
<div class="flex flex-wrap gap-2">
    <span class="bg-yellow-200 text-yellow-800 px-3 py-1 rounded-full text-sm" data-i18n="tag1">知识点名称</span>
</div>
```

### 解题技巧列表

```html
<ul class="space-y-2 text-gray-700">
    <li data-i18n="s6_tip1">• <strong>技巧名称</strong>：技巧描述</li>
</ul>
```

## MathJax 渲染注意事项

当使用 `goToStep()` 切换步骤后，如有新显示的 MathJax 公式需重新排版：

```javascript
function goToStep(step) {
    // ... 切换逻辑 ...
    // 重新渲染当前步骤的MathJax
    if (window.MathJax && window.MathJax.typesetPromise) {
        MathJax.typesetPromise([document.getElementById('step' + step)]);
    }
}
```

## 完整 HTML 模板结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>题号 - 题目简述</title>
    <!-- CDN资源 -->
    <style>
        body { font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif; }
        .step-card { display: none; }
        .step-card.visible { display: block; animation: fadeIn 0.4s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
        .hint-btn { transition: all 0.3s ease; cursor: pointer; }
        .hint-btn:hover { transform: translateX(4px); }
        .hint-content { max-height: 0; overflow: hidden; transition: max-height 0.4s ease, padding 0.4s ease; }
        .hint-content.show { max-height: 300px; padding: 12px 16px; margin-top: 8px; }
        .nav-btn { transition: all 0.3s ease; }
        .nav-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        /* 语言切换按钮样式（必需） */
        .lang-btn { cursor: pointer; transition: all 0.2s; }
        .lang-btn:hover { transform: scale(1.05); }
        .lang-btn.active { background-color: #4f46e5; color: white; }
        .jxgbox { margin: 0 auto; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <header class="bg-white shadow-md sticky top-0 z-50">
        <!-- 标题 + 语言切换 + 进度 -->
    </header>
    <main class="max-w-4xl mx-auto px-4 py-8">
        <div id="step0" class="step-card visible mb-8"><!-- 题目 --></div>
        <div id="step1" class="step-card mb-8"><!-- 步骤1 --></div>
        <!-- ... 更多步骤 ... -->
        <div id="stepN" class="step-card mb-8"><!-- 总结 --></div>
    </main>
    <script>
        // ======== i18n System（必需，即使只实现中文） ========
        let currentLang = 'zh';
        const i18n = {
            zh: {
                title: '题号 - 题目简述',
                progress: '进度:',
                prev: '← 上一步',
                next: '下一步 →',
                restart: '重新开始 ↻',
                // 添加更多翻译键...
            },
            en: {
                title: 'Problem Title',
                progress: 'Progress:',
                prev: '← Prev',
                next: 'Next →',
                restart: 'Restart ↻',
                // 添加更多翻译键...
            }
        };

        function setLang(lang) {
            currentLang = lang;
            document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';
            document.getElementById('langZh').classList.toggle('active', lang === 'zh');
            document.getElementById('langZh').classList.toggle('text-gray-600', lang !== 'zh');
            document.getElementById('langEn').classList.toggle('active', lang === 'en');
            document.getElementById('langEn').classList.toggle('text-gray-600', lang !== 'en');
            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                if (i18n[lang][key] !== undefined) {
                    el.innerHTML = i18n[lang][key];
                }
            });
        }

        // ======== Navigation ========
        // goToStep(), updateProgress(), toggleHint() 等函数...

        // ======== 键盘导航 ========
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight') goToStep(currentStep + 1);
            if (e.key === 'ArrowLeft') goToStep(currentStep - 1);
        });

        // ======== 初始化 ========
        updateProgress();
    </script>
</body>
</html>
```

---

## 功能检查清单

生成HTML后，逐项确认以下功能是否完整实现：

### 必需组件
- [ ] **Header 包含语言切换按钮**（中文/EN两个按钮，有 `.lang-btn` 样式）
- [ ] **所有文本元素有 `data-i18n` 属性**（标题、步骤说明、提示问答、按钮文字）
- [ ] **i18n 字典包含 `zh` 和 `en` 两个key**（即使英文内容为空，结构必须存在）
- [ ] **`setLang()` 函数正确实现**（能切换按钮高亮状态，更新所有文本）
- [ ] **`.lang-btn` 样式已添加**（包含 `cursor`, `transition`, `hover`, `active` 状态）

### 导航功能
- [ ] **步骤切换正常**（`goToStep()` 能正确显示/隐藏步骤卡片）
- [ ] **进度指示器更新**（圆点或进度条随步骤变化）
- [ ] **提示展开/收起正常**（`toggleHint()` 能展开/收起提示内容）
- [ ] **键盘导航正常**（左右箭头键可切换步骤）

### 内容完整性
- [ ] **所有步骤内容已填充**（题目页 + 解题步骤 + 总结页）
- [ ] **图片路径正确**（`step1_init.png` 等图片能正常显示）
- [ ] **数学公式渲染**（如使用 MathJax，公式能正确显示）

> 💡 **提示**：建议先用中文完成全部内容，确认功能正常后再补充英文翻译。语言切换框架必须在**第一步**就搭建好，而不是后期添加。
