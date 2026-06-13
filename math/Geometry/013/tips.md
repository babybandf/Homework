---
mathjax: true
---

# 几何证明题

## 题目

在等腰直角三角形 $\triangle ABC$ 中，$\angle BAC = 90^\circ$，$MN \parallel BC$。点 $D$ 在 $MN$ 上，点 $P$ 在直线 $AC$ 上，且 $\angle BDE = 90^\circ$。

**求证：** $BD = DP$

---

## 证明

### (1) 点 $P$ 在 $AC$ 边上（图1）

如图1，过点 $D$ 作 $DF \perp AB$ 于点 $F$，$DG \perp AC$ 于点 $G$。

因为 $MN \parallel BC$，且 $\triangle ABC$ 是等腰直角三角形，$\angle BAC = 90^\circ$，所以：

$$
\angle BAM = \angle ABC = 45^\circ, \quad \angle CAN = \angle ACB = 45^\circ
$$

即 $MN$ 是 $\angle BAC$ 的外角平分线。因此，点 $D$ 到 $AB$ 和 $AC$ 的距离相等，即 $DF = DG$。

又因为 $DF \perp AB$，$DG \perp AC$，且 $AB \perp AC$，所以四边形 $AFDG$ 是矩形。结合 $DF = DG$ 得 $AFDG$ 是正方形。从而：

$$
DF = DG, \quad \angle FDG = 90^\circ
$$

由 $\angle BDE = 90^\circ$，得：

$$
\angle BDF + \angle FDP = \angle PDG + \angle FDP = 90^\circ
$$

所以 $\angle BDF = \angle PDG$。

又 $\angle BFD = \angle PGD = 90^\circ$，且 $DF = DG$，故：

$$
\triangle BDF \cong \triangle PDG \quad (\text{ASA})
$$

因此 $BD = DP$。

---

### (2) 点 $P$ 在 $CA$ 的延长线上（图2）

在图2中，点 $P$ 在 $CA$ 的延长线上，同样过 $D$ 作 $DF \perp AB$ 于 $F$，$DG \perp AC$ 于 $G$。

同理可证：
- $DF = DG$
- 四边形 $AFDG$ 为正方形
- $\angle FDG = 90^\circ$

由 $\angle BDE = 90^\circ$ 得 $\angle BDF = \angle PDG$，结合 $\angle BFD = \angle PGD = 90^\circ$ 及 $DF = DG$，得：

$$
\triangle BDF \cong \triangle PDG
$$

所以 $BD = DP$。结论成立。

---

### (3) 点 $P$ 在 $AC$ 的延长线上（图3）

在图3中，点 $P$ 在 $AC$ 的延长线上，同样作垂线。

同理可证 $BD = DP$。结论成立。

---

## 结论

综上所述，在所有三种情形下，均有：

$$
\boxed{BD = DP}
$$
