"""
Problem 004: Coordinate calculations for JSXGraph figures
In △ABC, ∠BAC = ∠BCA = 44°, M is inside, ∠MCA = 30°, ∠MAC = 16°.
Find ∠BMC.

This script verifies the coordinates used in the JSXGraph HTML and
validates the answer ∠BMC = 150°.
"""

import numpy as np

# Triangle ABC
# A at origin, C on x-axis, B at top
Ax, Ay = 0, 0
Cx, Cy = 6, 0
# B: from A at angle 44° upward, from C at angle (180-44)° upward
# AB and BC are equal (isosceles), angle at B = 92°
# B_x = 3 (midpoint of AC by symmetry), B_y = 3*tan(44°)
Bx = 3
By = 3 * np.tan(np.radians(44))
print(f"B = ({Bx:.4f}, {By:.4f})")

# Point M: intersection of:
#   Ray from A at angle 16° (∠MAC = 16°)
#   Ray from C at angle 150° from +x axis (∠MCA = 30°, M above AC)
# Ray from A: (t*cos16, t*sin16)
# Ray from C: (6 + s*cos150, s*sin150) = (6 - s*√3/2, s/2)
# Equating y: t*sin16 = s/2 → s = 2t*sin16
# Equating x: t*cos16 = 6 - s*√3/2 = 6 - t*sin16*√3
# t*(cos16 + √3*sin16) = 6
t_M = 6 / (np.cos(np.radians(16)) + np.sqrt(3)*np.sin(np.radians(16)))
Mx = t_M * np.cos(np.radians(16))
My = t_M * np.sin(np.radians(16))
print(f"M = ({Mx:.4f}, {My:.4f})")

# Equilateral triangle Q (below AC)
Qx = 3
Qy = -6 * np.sin(np.radians(60))
print(f"Q = ({Qx:.4f}, {Qy:.4f})")

# Verification
print("\n=== Angle Verification ===")

def angle_at_vertex(V, P1, P2):
    """Calculate angle at vertex V between rays VP1 and VP2 (in degrees)."""
    v1 = np.array(P1) - np.array(V)
    v2 = np.array(P2) - np.array(V)
    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    cos_angle = np.clip(cos_angle, -1, 1)
    return np.degrees(np.arccos(cos_angle))

A = (Ax, Ay)
B = (Bx, By)
C = (Cx, Cy)
M = (Mx, My)
Q = (Qx, Qy)

print(f"∠BAC = {angle_at_vertex(A, B, C):.2f}° (should be 44°)")
print(f"∠BCA = {angle_at_vertex(C, B, A):.2f}° (should be 44°)")
print(f"∠ABC = {angle_at_vertex(B, A, C):.2f}° (should be 92°)")
print(f"∠MAC = {angle_at_vertex(A, M, C):.2f}° (should be 16°)")
print(f"∠MCA = {angle_at_vertex(C, M, A):.2f}° (should be 30°)")
print(f"∠BAM = {angle_at_vertex(A, B, M):.2f}° (should be 28°)")
print(f"∠BCM = {angle_at_vertex(C, B, M):.2f}° (should be 14°)")
print(f"∠AMC = {angle_at_vertex(M, A, C):.2f}° (should be 134°)")

# Key result
angle_BMC = angle_at_vertex(M, B, C)
angle_MBC = angle_at_vertex(B, M, C)
angle_MCB = angle_at_vertex(C, M, B)
print(f"\n∠BMC = {angle_BMC:.2f}° (should be 150°)")
print(f"∠MBC = {angle_MBC:.2f}° (should be 16°)")
print(f"∠MCB = {angle_at_vertex(C, M, B):.2f}°")

# Actually let me recompute correctly
print("\n=== Correct angle computations ===")
print(f"∠MBC (at B, between M and C) = {angle_at_vertex(B, M, C):.2f}° (should be 16°)")
print(f"∠MCB (at C, between M and B) = {angle_at_vertex(C, M, B):.2f}° (should be 14°)")
print(f"∠BMC (at M, between B and C) = {angle_at_vertex(M, B, C):.2f}° (should be 150°)")

# Ceva's theorem verification
print("\n=== Trigonometric Ceva Verification ===")
# sin(∠BAM)/sin(∠MAC) × sin(∠ACM)/sin(∠MCB) × sin(∠CBM)/sin(∠MBA) = 1
ceva = (np.sin(np.radians(28)) / np.sin(np.radians(16)) *
        np.sin(np.radians(30)) / np.sin(np.radians(14)) *
        np.sin(np.radians(16)) / np.sin(np.radians(76)))
print(f"Ceva product = {ceva:.6f} (should be 1.0)")

# Equilateral triangle verification
print(f"\n=== Equilateral Triangle Verification ===")
AQ = np.linalg.norm(np.array(Q) - np.array(A))
CQ = np.linalg.norm(np.array(Q) - np.array(C))
AC = np.linalg.norm(np.array(C) - np.array(A))
print(f"AQ = {AQ:.4f}, CQ = {CQ:.4f}, AC = {AC:.4f} (should all be equal)")
print(f"∠QAC = {angle_at_vertex(A, Q, C):.2f}° (should be 60°)")
print(f"∠QCA = {angle_at_vertex(C, Q, A):.2f}° (should be 60°)")

# Congruent triangles verification
AB = np.linalg.norm(np.array(B) - np.array(A))
CB = np.linalg.norm(np.array(B) - np.array(C))
BQ = np.linalg.norm(np.array(Q) - np.array(B))
print(f"\nAB = {AB:.4f}, CB = {CB:.4f} (should be equal)")
print(f"BQ = {BQ:.4f}")
print(f"∠ABQ = {angle_at_vertex(B, A, Q):.2f}° (should be 46°)")
print(f"∠CBQ = {angle_at_vertex(B, C, Q):.2f}° (should be 46°)")
