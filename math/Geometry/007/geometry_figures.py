"""
Problem 007: Geometry Figures
A triangle is divided into two isosceles triangles.
If one angle of the original triangle is 36°, find all possible combinations for the other two angles.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


def draw_triangle_with_cevian(ax, angles, cevian_from, title, case_label):
    """
    Draw a triangle with given angles and a cevian that divides it into two isosceles triangles.
    angles: tuple of three angles (A, B, C) in degrees
    cevian_from: which vertex the cevian goes from ('A', 'B', or 'C')
    """
    A_angle, B_angle, C_angle = angles
    
    # Place triangle with base BC horizontal
    # Using sine rule to find side lengths (set BC = 1 for convenience)
    BC = 3.0
    # By sine rule: BC/sin(A) = AC/sin(B) = AB/sin(C)
    AC = BC * np.sin(np.radians(B_angle)) / np.sin(np.radians(A_angle))
    AB = BC * np.sin(np.radians(C_angle)) / np.sin(np.radians(A_angle))
    
    # Place B at origin, C on x-axis
    B = np.array([0, 0])
    C = np.array([BC, 0])
    # A is at angle B_angle from BC direction
    A = np.array([AB * np.cos(np.radians(B_angle)), AB * np.sin(np.radians(B_angle))])
    
    vertices = {'A': A, 'B': B, 'C': C}
    
    # Draw the main triangle
    triangle = plt.Polygon([A, B, C], fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(triangle)
    
    # Label vertices
    for name, point in vertices.items():
        centroid = (A + B + C) / 3
        direction = point - centroid
        direction = direction / np.linalg.norm(direction) * 0.25
        ax.text(point[0] + direction[0], point[1] + direction[1], name,
                ha='center', va='center', fontsize=13, fontweight='bold')
    
    # Draw cevian
    # Determine the cevian endpoint based on which vertex it goes from
    if cevian_from == 'A':
        # Cevian from A to point D on BC
        # Need to find D such that both triangles are isosceles
        # For the specific cases we know the answer
        start = A
        # D divides BC
        opposite_side_start = B
        opposite_side_end = C
    elif cevian_from == 'B':
        start = B
        opposite_side_start = A
        opposite_side_end = C
    elif cevian_from == 'C':
        start = C
        opposite_side_start = A
        opposite_side_end = B
    
    # Calculate D position using angle constraints
    # This is a simplified placement - use the midpoint-ish for visualization
    # Actually, let me calculate properly based on the specific cases
    D = find_cevian_point(A, B, C, A_angle, B_angle, C_angle, cevian_from)
    
    if D is not None:
        ax.plot([start[0], D[0]], [start[1], D[1]], 'b-', linewidth=1.5, linestyle='--')
        # Label D
        centroid = (A + B + C) / 3
        direction = D - centroid
        if np.linalg.norm(direction) > 0:
            direction = direction / np.linalg.norm(direction) * 0.2
        ax.text(D[0] + direction[0], D[1] + direction[1], 'D',
                ha='center', va='center', fontsize=11, fontweight='bold', color='blue')
        
        # Fill the two sub-triangles
        if cevian_from == 'A':
            tri1 = plt.Polygon([A, B, D], alpha=0.15, facecolor='lightblue', edgecolor='none')
            tri2 = plt.Polygon([A, D, C], alpha=0.15, facecolor='lightyellow', edgecolor='none')
        elif cevian_from == 'B':
            tri1 = plt.Polygon([B, A, D], alpha=0.15, facecolor='lightblue', edgecolor='none')
            tri2 = plt.Polygon([B, D, C], alpha=0.15, facecolor='lightyellow', edgecolor='none')
        elif cevian_from == 'C':
            tri1 = plt.Polygon([C, A, D], alpha=0.15, facecolor='lightblue', edgecolor='none')
            tri2 = plt.Polygon([C, D, B], alpha=0.15, facecolor='lightyellow', edgecolor='none')
        ax.add_patch(tri1)
        ax.add_patch(tri2)
    
    # Add angle labels
    angle_labels = [f'{A_angle:.0f}°' if A_angle == int(A_angle) else f'{A_angle:.1f}°',
                    f'{B_angle:.0f}°' if B_angle == int(B_angle) else f'{B_angle:.1f}°',
                    f'{C_angle:.0f}°' if C_angle == int(C_angle) else f'{C_angle:.1f}°']
    
    for point, angle_str, other1, other2 in [(A, angle_labels[0], B, C),
                                              (B, angle_labels[1], A, C),
                                              (C, angle_labels[2], A, B)]:
        # Place angle label near the vertex, inside the triangle
        mid_direction = ((other1 + other2) / 2 - point)
        if np.linalg.norm(mid_direction) > 0:
            mid_direction = mid_direction / np.linalg.norm(mid_direction) * 0.45
        ax.text(point[0] + mid_direction[0], point[1] + mid_direction[1],
                angle_str, ha='center', va='center', fontsize=9, color='red')
    
    ax.set_aspect('equal')
    all_points = np.array([A, B, C])
    margin = 0.5
    ax.set_xlim(all_points[:, 0].min() - margin, all_points[:, 0].max() + margin)
    ax.set_ylim(all_points[:, 1].min() - margin, all_points[:, 1].max() + margin)
    ax.axis('off')
    ax.set_title(f'{case_label}\n{title}', fontsize=11, fontweight='bold', pad=8)


def find_cevian_point(A, B, C, A_angle, B_angle, C_angle, cevian_from):
    """Find the cevian point D on the opposite side."""
    if cevian_from == 'A':
        # D on BC, cevian AD
        # Use specific known solutions
        if abs(A_angle - 36) < 0.1 and abs(B_angle - 132) < 0.1:
            # Cevian from A: angle BAD = 24, angle CAD = 12
            # D on BC such that AD divides into ABD and ACD
            # In triangle ABD: angle A=24, angle B=132, angle ADB=24 -> AB=BD
            # t = BD/BC
            BD = np.linalg.norm(A - B)  # AB = BD
            BC_len = np.linalg.norm(C - B)
            t = min(BD / BC_len, 0.95)
            return B + t * (C - B)
        elif abs(A_angle - 36) < 0.1 and abs(B_angle - 108) < 0.1:
            # angle BAD = some value
            # Triangle ABD: angle A_part, B=108, angle ADB
            # Let's use: from vertex B cevian to AC
            # Actually for this case, cevian from B works better
            # Use approximate position
            return B + 0.618 * (C - B)
        else:
            return B + 0.5 * (C - B)
    elif cevian_from == 'B':
        # D on AC
        if abs(A_angle - 36) < 0.1 and abs(B_angle - 108) < 0.1:
            # Triangle: 36-108-36. Cevian from B to AC.
            # angle ABD = 72, angle DBC = 36
            # In triangle ABD: angle A=36, angle ABD=72, angle ADB=72 -> AB=AD
            AD = np.linalg.norm(A - B)  # AB
            AC_len = np.linalg.norm(C - A)
            t = min(AD / AC_len, 0.95)
            return A + t * (C - A)
        elif abs(A_angle - 36) < 0.1 and abs(B_angle - 72) < 0.1:
            # 36-72-72: cevian from B
            # angle ABD=36, DBC=36
            # triangle ABD: A=36, ABD=36, ADB=108 -> AD=BD
            # triangle BCD: C=72, DBC=36, BDC=72 -> BC=BD
            # So AD = BD = BC
            BC_len = np.linalg.norm(C - B)
            # AD = BC, find t on AC
            AC_len = np.linalg.norm(C - A)
            t = min(BC_len / AC_len, 0.95)
            return A + t * (C - A)
        elif abs(A_angle - 36) < 0.1 and abs(B_angle - 126) < 0.1:
            # 36-126-18: cevian from B (or A)
            # Actually let me use angle ABD = 108
            AB = np.linalg.norm(A - B)
            AC_len = np.linalg.norm(C - A)
            # In triangle ABD: A=36, ABD=108, ADB=36 -> AB=AD... wait no AB=BD
            # angle A=36, angle ADB = 36, so AB = BD (since they're opposite equal angles... no)
            # sides opposite equal angles are equal: angle A = angle ADB = 36 -> BD = AB
            BD = AB
            # Now find D on AC using law of cosines in triangle ABD
            # Actually use: AD / sin(ABD) = AB / sin(ADB)
            # AD / sin(108) = AB / sin(36)
            AD = AB * np.sin(np.radians(108)) / np.sin(np.radians(36))
            t = min(AD / AC_len, 0.95)
            return A + t * (C - A)
        elif abs(A_angle - 36) < 0.1 and abs(B_angle - 90) < 0.1:
            # 36-90-54: need to find appropriate cevian
            # Cevian from B: angle ABD = 36, DBC = 54
            # triangle ABD: A=36, ABD=36, ADB=108 -> AD=BD
            # triangle BCD: C=54, DBC=54, BDC=72 -> BD=CD
            BC_len = np.linalg.norm(C - B)
            AB = np.linalg.norm(A - B)
            AC_len = np.linalg.norm(C - A)
            # AD = BD (from triangle ABD with equal base angles)
            # In triangle ABD: angle A=36, ABD=36, ADB=108
            # AD/sin(ABD) = AB/sin(ADB) -> AD/sin36 = AB/sin108
            AD = AB * np.sin(np.radians(36)) / np.sin(np.radians(108))
            t = min(AD / AC_len, 0.95)
            return A + t * (C - A)
        else:
            return A + 0.5 * (C - A)
    elif cevian_from == 'C':
        # D on AB
        if abs(A_angle - 36) < 0.1 and abs(C_angle - 132) < 0.1:
            # angle ACD, angle BCD
            return A + 0.5 * (B - A)
        else:
            AB_len = np.linalg.norm(B - A)
            return A + 0.5 * (B - A)
    return None


# ============================================================
# Figure 1: Problem Overview
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(7, 5))
ax.set_aspect('equal')

# Draw a generic triangle with one angle = 36
A_angle, B_angle, C_angle = 36, 72, 72
BC = 3.0
AB = BC * np.sin(np.radians(C_angle)) / np.sin(np.radians(A_angle))
B = np.array([0, 0])
C = np.array([BC, 0])
A = np.array([AB * np.cos(np.radians(B_angle)), AB * np.sin(np.radians(B_angle))])

triangle = plt.Polygon([A, B, C], fill=False, edgecolor='black', linewidth=2.5)
ax.add_patch(triangle)

# Label
for name, point in [('A', A), ('B', B), ('C', C)]:
    centroid = (A + B + C) / 3
    direction = point - centroid
    direction = direction / np.linalg.norm(direction) * 0.3
    ax.text(point[0] + direction[0], point[1] + direction[1], name,
            ha='center', va='center', fontsize=15, fontweight='bold')

# Mark the 36 degree angle
mid = (B + C) / 2 - A
mid = mid / np.linalg.norm(mid) * 0.5
ax.text(A[0] + mid[0], A[1] + mid[1], '36°', ha='center', va='center',
        fontsize=12, color='red', fontweight='bold')

# Question mark for other angles
mid_b = (A + C) / 2 - B
mid_b = mid_b / np.linalg.norm(mid_b) * 0.5
ax.text(B[0] + mid_b[0], B[1] + mid_b[1], '?', ha='center', va='center',
        fontsize=16, color='blue', fontweight='bold')
mid_c = (A + B) / 2 - C
mid_c = mid_c / np.linalg.norm(mid_c) * 0.5
ax.text(C[0] + mid_c[0], C[1] + mid_c[1], '?', ha='center', va='center',
        fontsize=16, color='blue', fontweight='bold')

# Dashed cevian to suggest division
D = B + 0.618 * (C - B)
ax.plot([A[0], D[0]], [A[1], D[1]], 'b--', linewidth=1.5, alpha=0.5)

all_points = np.array([A, B, C])
margin = 0.6
ax.set_xlim(all_points[:, 0].min() - margin, all_points[:, 0].max() + margin)
ax.set_ylim(all_points[:, 1].min() - margin, all_points[:, 1].max() + margin)
ax.axis('off')
ax.set_title('Problem 007: One angle is 36°\nFind all possible cases for the other two angles', fontsize=13, pad=10)

plt.tight_layout()
plt.savefig('/home/rivli01/projects/homework/math/007/step1_setup.png', dpi=150, bbox_inches='tight')
plt.close()


# ============================================================
# Figure 2: All 5 solutions
# ============================================================
cases = [
    ((36, 72, 72), 'B', '36° - 72° - 72°', 'Case 1'),
    ((36, 108, 36), 'B', '36° - 108° - 36°', 'Case 2'),
    ((36, 132, 12), 'A', '36° - 132° - 12°', 'Case 3'),
    ((36, 126, 18), 'B', '36° - 126° - 18°', 'Case 4'),
    ((36, 90, 54), 'B', '36° - 90° - 54°', 'Case 5'),
]

fig, axes = plt.subplots(2, 3, figsize=(14, 10))
axes_flat = axes.flatten()

for idx, (angles, cevian_from, title, label) in enumerate(cases):
    draw_triangle_with_cevian(axes_flat[idx], angles, cevian_from, title, label)

# Hide the last empty subplot
axes_flat[5].axis('off')
axes_flat[5].text(0.5, 0.5, 'Total: 5 Cases', ha='center', va='center',
                  fontsize=18, fontweight='bold', color='#667eea',
                  transform=axes_flat[5].transAxes)

plt.suptitle('Problem 007: All Possible Triangles', fontsize=15, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig('/home/rivli01/projects/homework/math/007/step2_all_solutions.png', dpi=150, bbox_inches='tight')
plt.close()


# ============================================================
# Figure 3: Detailed verification for each case
# ============================================================
# Case 1: 36-72-72 (isosceles, cevian from B)
fig, ax = plt.subplots(1, 1, figsize=(7, 6))
angles = (36, 72, 72)
A_angle, B_angle, C_angle = angles
BC = 3.0
AB = BC * np.sin(np.radians(C_angle)) / np.sin(np.radians(A_angle))
B = np.array([0, 0])
C = np.array([BC, 0])
A = np.array([AB * np.cos(np.radians(B_angle)), AB * np.sin(np.radians(B_angle))])

# Cevian from B to D on AC
# angle ABD = 36, angle DBC = 36
# triangle ABD: A=36, ABD=36, ADB=108
# AD/sin(36) = AB/sin(108), AD = AB*sin36/sin108
AD = AB * np.sin(np.radians(36)) / np.sin(np.radians(108))
AC_len = np.linalg.norm(C - A)
t = AD / AC_len
D = A + t * (C - A)

# Draw
tri1 = plt.Polygon([A, B, D], alpha=0.2, facecolor='lightblue', edgecolor='blue', linewidth=1.5)
tri2 = plt.Polygon([B, D, C], alpha=0.2, facecolor='lightyellow', edgecolor='orange', linewidth=1.5)
ax.add_patch(tri1)
ax.add_patch(tri2)
triangle = plt.Polygon([A, B, C], fill=False, edgecolor='black', linewidth=2.5)
ax.add_patch(triangle)
ax.plot([B[0], D[0]], [B[1], D[1]], 'b-', linewidth=2)

for name, point in [('A', A), ('B', B), ('C', C), ('D', D)]:
    centroid = (A + B + C) / 3
    direction = point - centroid
    direction = direction / np.linalg.norm(direction) * 0.3
    ax.text(point[0] + direction[0], point[1] + direction[1], name,
            ha='center', va='center', fontsize=14, fontweight='bold')

# Angle labels inside triangles
centroid1 = (A + B + D) / 3
ax.text(centroid1[0], centroid1[1], 'ABD\n36°-36°-108°\nAD=BD',
        ha='center', va='center', fontsize=9, color='blue')
centroid2 = (B + D + C) / 3
ax.text(centroid2[0], centroid2[1], 'BDC\n36°-72°-72°\nBC=BD',
        ha='center', va='center', fontsize=9, color='darkorange')

ax.set_aspect('equal')
all_points = np.array([A, B, C, D])
margin = 0.6
ax.set_xlim(all_points[:, 0].min() - margin, all_points[:, 0].max() + margin)
ax.set_ylim(all_points[:, 1].min() - margin, all_points[:, 1].max() + margin)
ax.axis('off')
ax.set_title('Case 1: 36° - 72° - 72° (Isosceles Triangle)\nCevian from B to AC', fontsize=12, pad=10)

plt.tight_layout()
plt.savefig('/home/rivli01/projects/homework/math/007/step3_case1.png', dpi=150, bbox_inches='tight')
plt.close()


# ============================================================
# Figure 4: Case 2 - 36-108-36
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(7, 6))
angles = (36, 108, 36)
A_angle, B_angle, C_angle = angles
BC = 3.0
AB = BC * np.sin(np.radians(C_angle)) / np.sin(np.radians(A_angle))
B = np.array([0, 0])
C = np.array([BC, 0])
A = np.array([AB * np.cos(np.radians(B_angle)), AB * np.sin(np.radians(B_angle))])

# Cevian from B to D on AC
# angle ABD = 72, angle DBC = 36
# triangle ABD: A=36, ABD=72, ADB=72 -> AB=AD
AD = np.linalg.norm(A - B)  # AB = AD
AC_len = np.linalg.norm(C - A)
t = AD / AC_len
D = A + t * (C - A)

tri1 = plt.Polygon([A, B, D], alpha=0.2, facecolor='lightblue', edgecolor='blue', linewidth=1.5)
tri2 = plt.Polygon([B, D, C], alpha=0.2, facecolor='lightyellow', edgecolor='orange', linewidth=1.5)
ax.add_patch(tri1)
ax.add_patch(tri2)
triangle = plt.Polygon([A, B, C], fill=False, edgecolor='black', linewidth=2.5)
ax.add_patch(triangle)
ax.plot([B[0], D[0]], [B[1], D[1]], 'b-', linewidth=2)

for name, point in [('A', A), ('B', B), ('C', C), ('D', D)]:
    centroid = (A + B + C) / 3
    direction = point - centroid
    direction = direction / np.linalg.norm(direction) * 0.3
    ax.text(point[0] + direction[0], point[1] + direction[1], name,
            ha='center', va='center', fontsize=14, fontweight='bold')

centroid1 = (A + B + D) / 3
ax.text(centroid1[0], centroid1[1], 'ABD\n36°-72°-72°\nAB=AD',
        ha='center', va='center', fontsize=9, color='blue')
centroid2 = (B + D + C) / 3
ax.text(centroid2[0], centroid2[1], 'BDC\n36°-36°-108°\nBD=CD',
        ha='center', va='center', fontsize=9, color='darkorange')

ax.set_aspect('equal')
all_points = np.array([A, B, C, D])
margin = 0.6
ax.set_xlim(all_points[:, 0].min() - margin, all_points[:, 0].max() + margin)
ax.set_ylim(all_points[:, 1].min() - margin, all_points[:, 1].max() + margin)
ax.axis('off')
ax.set_title('Case 2: 36° - 108° - 36° (Isosceles Triangle)\nCevian from B to AC', fontsize=12, pad=10)

plt.tight_layout()
plt.savefig('/home/rivli01/projects/homework/math/007/step4_case2.png', dpi=150, bbox_inches='tight')
plt.close()


# ============================================================
# Figure 5: Case 3 - 36-132-12
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(7, 6))
angles = (36, 132, 12)
A_angle, B_angle, C_angle = angles
BC = 3.0
AB = BC * np.sin(np.radians(C_angle)) / np.sin(np.radians(A_angle))
B = np.array([0, 0])
C = np.array([BC, 0])
A = np.array([AB * np.cos(np.radians(B_angle)), AB * np.sin(np.radians(B_angle))])

# Cevian from A to D on BC
# angle BAD = 24, angle CAD = 12
# triangle ABD: A_part=24, B=132, ADB=24 -> AB=BD
BD = np.linalg.norm(A - B)
BC_len = np.linalg.norm(C - B)
t = BD / BC_len
D = B + t * (C - B)

tri1 = plt.Polygon([A, B, D], alpha=0.2, facecolor='lightblue', edgecolor='blue', linewidth=1.5)
tri2 = plt.Polygon([A, D, C], alpha=0.2, facecolor='lightyellow', edgecolor='orange', linewidth=1.5)
ax.add_patch(tri1)
ax.add_patch(tri2)
triangle = plt.Polygon([A, B, C], fill=False, edgecolor='black', linewidth=2.5)
ax.add_patch(triangle)
ax.plot([A[0], D[0]], [A[1], D[1]], 'b-', linewidth=2)

for name, point in [('A', A), ('B', B), ('C', C), ('D', D)]:
    centroid = (A + B + C) / 3
    direction = point - centroid
    if np.linalg.norm(direction) > 0:
        direction = direction / np.linalg.norm(direction) * 0.3
    ax.text(point[0] + direction[0], point[1] + direction[1], name,
            ha='center', va='center', fontsize=14, fontweight='bold')

centroid1 = (A + B + D) / 3
ax.text(centroid1[0], centroid1[1], 'ABD\n24°-132°-24°\nAB=BD',
        ha='center', va='center', fontsize=9, color='blue')
centroid2 = (A + D + C) / 3
ax.text(centroid2[0], centroid2[1], 'ACD\n12°-12°-156°\nAD=CD',
        ha='center', va='center', fontsize=9, color='darkorange')

ax.set_aspect('equal')
all_points = np.array([A, B, C, D])
margin = 0.6
ax.set_xlim(all_points[:, 0].min() - margin, all_points[:, 0].max() + margin)
ax.set_ylim(all_points[:, 1].min() - margin, all_points[:, 1].max() + margin)
ax.axis('off')
ax.set_title('Case 3: 36° - 132° - 12°\nCevian from A to BC', fontsize=12, pad=10)

plt.tight_layout()
plt.savefig('/home/rivli01/projects/homework/math/007/step5_case3.png', dpi=150, bbox_inches='tight')
plt.close()


# ============================================================
# Figure 6: Case 4 - 36-126-18
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(7, 6))
angles = (36, 126, 18)
A_angle, B_angle, C_angle = angles
BC = 3.0
AB = BC * np.sin(np.radians(C_angle)) / np.sin(np.radians(A_angle))
B = np.array([0, 0])
C = np.array([BC, 0])
A = np.array([AB * np.cos(np.radians(B_angle)), AB * np.sin(np.radians(B_angle))])

# Cevian from B to D on AC
# angle ABD = 108, angle DBC = 18
# triangle ABD: A=36, ABD=108, ADB=36 -> AB=BD (sides opp equal angles)
# In triangle BDC: C=18, DBC=18, BDC=144 -> BD=CD
AD = AB * np.sin(np.radians(108)) / np.sin(np.radians(36))
AC_len = np.linalg.norm(C - A)
t = min(AD / AC_len, 0.95)
D = A + t * (C - A)

tri1 = plt.Polygon([A, B, D], alpha=0.2, facecolor='lightblue', edgecolor='blue', linewidth=1.5)
tri2 = plt.Polygon([B, D, C], alpha=0.2, facecolor='lightyellow', edgecolor='orange', linewidth=1.5)
ax.add_patch(tri1)
ax.add_patch(tri2)
triangle = plt.Polygon([A, B, C], fill=False, edgecolor='black', linewidth=2.5)
ax.add_patch(triangle)
ax.plot([B[0], D[0]], [B[1], D[1]], 'b-', linewidth=2)

for name, point in [('A', A), ('B', B), ('C', C), ('D', D)]:
    centroid = (A + B + C) / 3
    direction = point - centroid
    if np.linalg.norm(direction) > 0:
        direction = direction / np.linalg.norm(direction) * 0.3
    ax.text(point[0] + direction[0], point[1] + direction[1], name,
            ha='center', va='center', fontsize=14, fontweight='bold')

centroid1 = (A + B + D) / 3
ax.text(centroid1[0], centroid1[1], 'ABD\n36°-108°-36°\nAB=BD',
        ha='center', va='center', fontsize=9, color='blue')
centroid2 = (B + D + C) / 3
ax.text(centroid2[0], centroid2[1], 'BDC\n18°-18°-144°\nBD=CD',
        ha='center', va='center', fontsize=9, color='darkorange')

ax.set_aspect('equal')
all_points = np.array([A, B, C, D])
margin = 0.6
ax.set_xlim(all_points[:, 0].min() - margin, all_points[:, 0].max() + margin)
ax.set_ylim(all_points[:, 1].min() - margin, all_points[:, 1].max() + margin)
ax.axis('off')
ax.set_title('Case 4: 36° - 126° - 18°\nCevian from B to AC', fontsize=12, pad=10)

plt.tight_layout()
plt.savefig('/home/rivli01/projects/homework/math/007/step6_case4.png', dpi=150, bbox_inches='tight')
plt.close()


# ============================================================
# Figure 7: Case 5 - 36-90-54
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(7, 6))
angles = (36, 90, 54)
A_angle, B_angle, C_angle = angles
BC = 3.0
AB = BC * np.sin(np.radians(C_angle)) / np.sin(np.radians(A_angle))
B = np.array([0, 0])
C = np.array([BC, 0])
A = np.array([AB * np.cos(np.radians(B_angle)), AB * np.sin(np.radians(B_angle))])

# Cevian from B to D on AC
# angle ABD = 36, angle DBC = 54
# triangle ABD: A=36, ABD=36, ADB=108 -> AD=BD
# triangle BDC: C=54, DBC=54, BDC=72 -> BD=CD
AD = AB * np.sin(np.radians(36)) / np.sin(np.radians(108))
AC_len = np.linalg.norm(C - A)
t = AD / AC_len
D = A + t * (C - A)

tri1 = plt.Polygon([A, B, D], alpha=0.2, facecolor='lightblue', edgecolor='blue', linewidth=1.5)
tri2 = plt.Polygon([B, D, C], alpha=0.2, facecolor='lightyellow', edgecolor='orange', linewidth=1.5)
ax.add_patch(tri1)
ax.add_patch(tri2)
triangle = plt.Polygon([A, B, C], fill=False, edgecolor='black', linewidth=2.5)
ax.add_patch(triangle)
ax.plot([B[0], D[0]], [B[1], D[1]], 'b-', linewidth=2)

for name, point in [('A', A), ('B', B), ('C', C), ('D', D)]:
    centroid = (A + B + C) / 3
    direction = point - centroid
    if np.linalg.norm(direction) > 0:
        direction = direction / np.linalg.norm(direction) * 0.3
    ax.text(point[0] + direction[0], point[1] + direction[1], name,
            ha='center', va='center', fontsize=14, fontweight='bold')

centroid1 = (A + B + D) / 3
ax.text(centroid1[0], centroid1[1], 'ABD\n36°-36°-108°\nAD=BD',
        ha='center', va='center', fontsize=9, color='blue')
centroid2 = (B + D + C) / 3
ax.text(centroid2[0], centroid2[1], 'BDC\n54°-54°-72°\nBD=CD',
        ha='center', va='center', fontsize=9, color='darkorange')

ax.set_aspect('equal')
all_points = np.array([A, B, C, D])
margin = 0.6
ax.set_xlim(all_points[:, 0].min() - margin, all_points[:, 0].max() + margin)
ax.set_ylim(all_points[:, 1].min() - margin, all_points[:, 1].max() + margin)
ax.axis('off')
ax.set_title('Case 5: 36° - 90° - 54°\nCevian from B to AC', fontsize=12, pad=10)

plt.tight_layout()
plt.savefig('/home/rivli01/projects/homework/math/007/step7_case5.png', dpi=150, bbox_inches='tight')
plt.close()

print("All figures for Problem 007 generated successfully!")
