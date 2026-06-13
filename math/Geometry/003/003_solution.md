# Geometry Problem 003 Solution

## Problem

In right triangle ABC, angle C = 90°, angle A ≠ 30°, angle A ≠ 45°. Point P is taken on line BC or line AC such that triangle PAB is isosceles. How many such points P exist?

---

## Solution

### Step 1: Understanding the Problem

Given:
- Right triangle ABC with angle C = 90°
- Point P lies on line BC or line AC (can be on extensions)
- Triangle PAB is isosceles

Triangle PAB being isosceles has three cases:
1. PA = PB (P lies on perpendicular bisector of AB)
2. PA = AB (P lies on circle centered at A with radius AB)
3. PB = AB (P lies on circle centered at B with radius AB)

![Step 1](step1_setup.png)

---

### Step 2: Case Analysis

#### Case 1: PA = PB (Perpendicular Bisector of AB)

The perpendicular bisector of AB intersects:
- Line AC at 1 point (on extension of AC)
- Line BC at 1 point (on extension of BC)

**Case 1 Total: 2 points**

#### Case 2: PA = AB (Circle centered at A with radius AB)

A circle centered at A with radius AB intersects:
- Line AC at 2 points (one above C, one below C)
- Line BC at 1 point (on extension of BC, excluding point B itself)

**Case 2 Total: 3 points**

#### Case 3: PB = AB (Circle centered at B with radius AB)

A circle centered at B with radius AB intersects:
- Line AC at 1 point (on extension of AC, excluding point A itself)
- Line BC at 2 points (one to the right of C, one to the left of C)

**Case 3 Total: 3 points**

![Step 2](step2_cases.png)

---

### Step 3: Verify No Overlaps

We need to check if any points from different cases coincide:
- If a point satisfies PA = PB = AB, then triangle PAB is equilateral

When triangle PAB is equilateral:
- If P is on AC, then angle A = 60°
- If P is on BC, then angle B = 60°, which means angle A = 30°

Given condition: angle A ≠ 30°, so the second case does not occur.

If angle A = 60°, there would be overlaps, but this is not excluded by the problem. In general cases (angle A ≠ 60°), all 8 points are distinct.

**Total: 2 + 3 + 3 = 8 points**

![Step 3](step3_solution.png)

---

## Final Answer

> **8 points**

---

## Key Concepts Summary

1. **Isosceles Triangle Criterion**: Two sides equal or two angles equal
2. **Perpendicular Bisector Property**: Points on perpendicular bisector are equidistant from segment endpoints
3. **Circle Definition**: Locus of points at fixed distance from a center
4. **Classification Discussion**: Enumerate all cases without omission or duplication
5. **Line-Circle Intersections**: At most 2 intersection points

---

## Complete Solution Process

1. **Establish Classification Criteria**: Triangle PAB isosceles has three cases (PA=PB, PA=AB, PB=AB)
2. **Case 1 Analysis**: P on perpendicular bisector of AB, intersects two lines at 2 points
3. **Case 2 Analysis**: Circle centered at A with radius AB, intersects AC at 2 points, BC at 1 point, total 3 points
4. **Case 3 Analysis**: Circle centered at B with radius AB, intersects AC at 1 point, BC at 2 points, total 3 points
5. **Verify Overlaps**: In general case (angle A ≠ 60°), all 8 points are distinct

---

## Problem Solving Techniques

- **See isosceles triangle** → Immediately consider three cases
- **See "line"** → Note that point can be on extension
- **Combine numbers and shapes** → Use circles and perpendicular bisectors to find points
- **Verify overlaps** → Consider if special angles cause point coincidences
