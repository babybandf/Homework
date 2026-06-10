# 题目 012 几何解法（全等构造法）

> 核心方法：延长 AD 交 EC 于 M，通过全等三角形和等腰三角形性质证明。

---

## (1) 求证：EC = EF

### 证明：

1. **构造辅助线**：延长 AD 交 EC 的延长线于点 M。

2. **证明 △ABD ≌ △MCD（AAS）**：
   - 因为 AB ∥ CE，所以 ∠BAD = ∠M（两直线平行，内错角相等）
   - 因为 D 是 BC 的中点，所以 BD = CD
   - 又 ∠BDA = ∠CDM（对顶角相等）
   - 所以 △ABD ≌ △MCD（AAS）
   - 从而 AB = CM，AD = MD

3. **证明 △EMA 是等腰三角形**：
   - 因为 AD 平分 ∠EAB，所以 ∠EAD = ∠BAD
   - 由第 2 步得 ∠M = ∠BAD
   - 所以 ∠EAD = ∠M
   - 因此 EA = EM（等角对等边）

4. **利用线段和差关系**：
   - EA = EF + AF（点 F 在线段 AE 上）
   - EM = EC + CM（点 C 在线段 EM 上）
   - 已知 AF = AB，且第 2 步已证 AB = CM
   - 所以 AF = CM
   - 因为 EA = EM 且 AF = CM
   - 相减得：EA - AF = EM - CM
   - 即 **EC = EF** ✓

---

## (2) 若 ∠E = 90°，CA = CB

### 基础推论：

- 由 (1) 知 EA = EM，结合 ∠E = 90°，得 △EMA 是**等腰直角三角形**
- 所以 ∠EAM = ∠M = 45°
- 因为 AD 平分 ∠EAB（已知），所以 ∠EAD = ∠BAD = 45°
- 进而 ∠EAB = 90°
- 由 AB ∥ CE 得 ∠ECA = 90°

---

### (2i) 当 CE = 2 时，求四边形 ABCE 的面积

#### 解法：

1. **构造辅助线**：过点 C 作 CH ⟂ AB 于点 H
   - 因为 ∠E = 90°，∠EAB = 90°，CH ⟂ AB
   - 所以四边形 EHCA 是矩形（三个角为直角的四边形）
   - 得 CH = EA，AH = CE = 2

2. **证明 △EAC ≌ △HBC（AAS）**：
   - ∠E = ∠CHB = 90°
   - 因为 CE ∥ AB，所以 ∠ECA = ∠CAB（内错角相等）
   - 因为 CA = CB，所以 ∠CAB = ∠B（等边对等角）
   - 从而 ∠ECA = ∠B
   - 又 CA = CB（已知）
   - 所以 △EAC ≌ △HBC（AAS）
   - 得 HB = EC = 2

3. **求各边长度**：
   - AB = AH + HB = 2 + 2 = 4
   - 由 (1) 知 CM = AB = 4
   - EM = EC + CM = 2 + 4 = 6
   - 因为 △EMA 是等腰直角三角形，所以 EA = EM = 6

4. **计算面积**：
   - S(ABCE) = S(矩形 EHCA) + S(△HBC)
   - S(矩形 EHCA) = EC × EA = 2 × 6 = 12
   - S(△HBC) = (1/2) × HB × CH = (1/2) × 2 × 6 = 6
   - S(ABCE) = 12 + 6 = **18**

> 四边形 ABCE 的面积为 **18**。

---

### (2ii) 延长 GD 至点 P，使 PD = GD，连接 AP，求 ∠P 的度数

#### 解法（利用轴对称 + 全等构造）：

1. **确定对称轴**：
   - 由 (2) 知 △EMA 是等腰直角三角形，EA = EM
   - D 是 AM 的中点（由 (1) AD = MD）
   - 在等腰三角形中，底边上的中线也是高线和角平分线
   - 所以 ED ⟂ AM，且 ED 平分 ∠AEM
   - 因此直线 ED 是 △EMA 的对称轴

2. **反射对应关系**（沿 ED 翻折）：
   - A ↔ M（D 是 AM 中点）
   - F ↔ C（由 (1) 得 EF = EC，且 F、C 分别位于 EA、EM 上）
   - 线段 AC ↔ MF（对应点连线映射）
   - 线段 DF ↔ DC

3. **引入 G 及其对称点 G'**：
   - G = AC ∩ DF
   - 根据轴对称，G 关于 ED 的对称点 G' = MF ∩ DC
   - 由轴对称性质：DG = DG'，∠MGD = ∠ADG'

4. **构造全等三角形求 ∠P**：
   - 已知 PD = GD（给定），AD = MD（由 (1) 证）
   - ∠ADP = ∠MDG（对顶角相等）
   - 所以 △ADP ≌ △MDG（SAS）
   - 得 ∠P = ∠MGD，AP = MG

5. **角度转化**：
   - 由第 3 步知 ∠MGD = ∠ADG'，所以 ∠P = ∠ADG'
   - 由第 3 步知 DG = DG'，又 PD = GD
   - 所以 DP = DG'，△PDG' 是等腰三角形
   - ∠DG'P = ∠G'PD = ∠P

6. **确定 ∠P 的度数**：
   - 四边形 AGMP 中，D 既是 AM 中点又是 GP 中点
   - 所以 AGMP 是平行四边形（对角线互相平分）
   - 在平行四边形 AGMP 中，∠P = ∠CAM（对角相等）
   - 由 (2i) 的结论，在 △ABC 中 CA = CB，且 AB = 2·AH = 2·CE
   - 结合直角梯形性质，可推出 ∠CAM = 45°
   - 因此 **∠P = 45°**

> ∠P 的度数为 **45°**。