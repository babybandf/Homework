import numpy as np

def rotate(center, p, deg):
    rad = np.radians(deg)
    c, s = np.cos(rad), np.sin(rad)
    dx, dy = p[0]-center[0], p[1]-center[1]
    return np.array([center[0]+dx*c-dy*s, center[1]+dx*s+dy*c])

base = 3.5
half = base / 2
CA = base * np.sin(np.radians(72)) / np.sin(np.radians(36))
h = np.sqrt(CA**2 - half**2)
print(f"CA=CB={CA:.4f}, height={h:.4f}")

B = np.array([0.0, 0.0])
A = np.array([base, 0.0])
C = np.array([half, h])
D = A + 0.55 * (C - A)
E = np.array([5.5, 0.0])
F = rotate(D, E, 36)
G = rotate(D, A, 36)

print(f"B = ({B[0]:.4f}, {B[1]:.4f})")
print(f"A = ({A[0]:.4f}, {A[1]:.4f})")
print(f"C = ({C[0]:.4f}, {C[1]:.4f})")
print(f"D = ({D[0]:.4f}, {D[1]:.4f})")
print(f"E = ({E[0]:.4f}, {E[1]:.4f})")
print(f"F = ({F[0]:.4f}, {F[1]:.4f})")
print(f"G = ({G[0]:.4f}, {G[1]:.4f})")

# Verify angles
def angle_between(p1, center, p2):
    v1 = p1 - center
    v2 = p2 - center
    cos_a = np.dot(v1, v2) / (np.linalg.norm(v1)*np.linalg.norm(v2))
    return np.degrees(np.arccos(np.clip(cos_a, -1, 1)))

print(f"angle ACB = {angle_between(A, C, B):.1f}")
print(f"angle EDF = {angle_between(E, D, F):.1f}")
print(f"angle FGE = {angle_between(F, G, E):.1f}")
print(f"angle DAE = {angle_between(D, A, E):.1f}")
print(f"angle ADG = {angle_between(A, D, G):.1f}")