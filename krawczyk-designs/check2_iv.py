#!/usr/bin/env python3
"""Second, independent existence check (mpmath.iv interval arithmetic; shares no code with krawczyk_design.py).
Antipodal set of N points, t = 2k+1. Conditions: sum over the N/2 representatives of the monomials
x^c y^a z^b (c in {0,1}, c+a+b = m even, 2 <= m <= 2k) equals (N/2) * mean over S^2. (On S^2,
x^2 = 1 - y^2 - z^2 reduces every even polynomial of degree <= 2k to this basis plus 1, and the
reduced monomials are independent: p(y,z) + x q(y,z) = 0 on S^2 forces p = q = 0.)
Points: (sin th cos ph, sin th sin ph, cos th). Krawczyk: K(X) = m - Y F(m) + (I - Y F'(X))(X - m).
Usage: check2_iv.py designs.json name t"""
import json, sys, time
import numpy as np
import mpmath
from mpmath import mp, iv, mpf

name, t = sys.argv[2], int(sys.argv[3]); k = (t - 1) // 2
A = np.array(json.load(open(sys.argv[1]))[name], float); N = len(A); A /= np.linalg.norm(A, axis=1)[:, None]
T0 = time.time()
# representatives: of each antipodal pair keep the one with larger y (never ambiguous here)
taken = np.zeros(N, bool); reps = []
for i in range(N):
    if taken[i]: continue
    d = np.linalg.norm(A + A[i], axis=1); j = int(d.argmin()); assert d[j] < 1e-6 and j != i
    taken[i] = taken[j] = True; reps.append(A[i] if A[i, 1] >= A[j, 1] else A[j])
Rp = np.array(reps); h = len(Rp); P = 2 * h
basis = []
for m in range(2, 2 * k + 1, 2):
    for c in (0, 1):
        for a in range(m - c + 1):
            basis.append((c, a, m - c - a))   # x^c y^a z^b
E = len(basis)


def dfac(n):
    out = 1
    while n > 1: out *= n; n -= 2
    return out


def mean(c, a, b):
    if c or a % 2 or b % 2: return (0, 1)
    return (dfac(a - 1) * dfac(b - 1), dfac(a + b + 1))


MEAN = [mean(*q) for q in basis]
th0 = np.arccos(np.clip(Rp[:, 2], -1, 1)); ph0 = np.arctan2(Rp[:, 1], Rp[:, 0])
q0 = np.column_stack([th0, ph0]).ravel()


def FJ_float(q):
    th, ph = q[0::2], q[1::2]; st, ct, sp, cp = np.sin(th), np.cos(th), np.sin(ph), np.cos(ph)
    x, y, z = st * cp, st * sp, ct
    dx = (ct * cp, -st * sp); dy = (ct * sp, st * cp); dz = (-st, 0 * st)
    F = np.empty(E); J = np.zeros((E, P))
    for r, (c, a, b) in enumerate(basis):
        xc = x if c else 1.0
        v = xc * y ** a * z ** b
        F[r] = v.sum() - h * MEAN[r][0] / MEAN[r][1]
        for s in (0, 1):
            g = (c * y ** a * z ** b * dx[s]) + (a * xc * y ** max(a - 1, 0) * z ** b * dy[s] if a else 0) + (b * xc * y ** a * z ** max(b - 1, 0) * dz[s] if b else 0)
            J[r, s::2] = g
    return F, J


q = q0.copy()
for _ in range(25):
    F, J = FJ_float(q)
    if abs(F).max() < 5e-15: break
    q -= np.linalg.lstsq(J, F, rcond=None)[0]
F, J = FJ_float(q)
# gauge: choose the E solved parameters by greedy column selection on the SVD-rotated Jacobian
U, S, Vt = np.linalg.svd(J, full_matrices=True)
null = Vt[E:]                                    # directions not seen by F (tangent of the solution set)
order = np.argsort(-np.abs(null).sum(0))        # fix the parameters that move most along the null space
fixed = []
for j in order:
    trial = sorted(set(range(P)) - set(fixed) - {j})
    if len(fixed) < P - E and np.linalg.matrix_rank(J[:, [c for c in range(P) if c not in fixed + [j]]], tol=1e-9) == E:
        fixed.append(int(j))
    if len(fixed) == P - E: break
assert len(fixed) == P - E
solv = [c for c in range(P) if c not in fixed]
print(f'{name}: t={t} N={N} E={E} P={P}; float max|F| {abs(F).max():.1e}; fixed {sorted(fixed)}; cond {np.linalg.cond(J[:, solv]):.1e}', flush=True)

mp.prec = 200; iv.prec = 200
fixv = {j: mpf(float(q[j])) for j in fixed}            # exact binary64 values
sv = {j: mpf(float(q[j])) for j in solv}


def evalF(vals, ar, want_J):
    """ar: mp or iv context. vals: P numbers of that context."""
    F = [ar.mpf(0)] * E; J = [[ar.mpf(0)] * E for _ in range(E)] if want_J else None
    col = {j: c for c, j in enumerate(solv)}
    for i in range(h):
        th, ph = vals[2 * i], vals[2 * i + 1]
        st, ct, sp, cp = ar.sin(th), ar.cos(th), ar.sin(ph), ar.cos(ph)
        x, y, z = st * cp, st * sp, ct
        D = {0: (ct * cp, ct * sp, -st), 1: (-st * sp, st * cp, ar.mpf(0))}
        yp = [ar.mpf(1)]; zp = [ar.mpf(1)]
        for _ in range(2 * k + 1): yp.append(yp[-1] * y); zp.append(zp[-1] * z)
        for r, (c, a, b) in enumerate(basis):
            yz = yp[a] * zp[b]
            F[r] += x * yz if c else yz
            if want_J:
                for s in (0, 1):
                    cc = col.get(2 * i + s)
                    if cc is None: continue
                    dxs, dys, dzs = D[s]; xc = x if c else ar.mpf(1)
                    g = (yz * dxs if c else 0) + (a * xc * yp[a - 1] * zp[b] * dys if a else 0) + (b * xc * yp[a] * zp[b - 1] * dzs if b else 0)
                    J[r][cc] += g
    F = [F[r] - ar.mpf(h * MEAN[r][0]) / MEAN[r][1] for r in range(E)]
    return F, J


def full(d, ar):
    return [d[j] if j in d else ar.mpf(fixv[j]) for j in range(P)]


for it in range(6):   # Newton in mp on the square system
    Fm, Jm = evalF(full(sv, mp), mp, True)
    res = max(abs(f) for f in Fm)
    print(f'  mp Newton {it}: max|F| = {mpmath.nstr(res, 3)} ({time.time() - T0:.0f}s)', flush=True)
    if res < mpf(2) ** -170: break
    step = mp.lu_solve(mp.matrix(Jm), mp.matrix(Fm))
    for c, j in enumerate(solv): sv[j] = sv[j] - step[c]
# Krawczyk with interval arithmetic
r = mpf(2) ** -60
mid = {j: sv[j] for j in solv}
Fm_iv, _ = evalF(full({j: iv.mpf(mid[j]) for j in solv}, iv), iv, False)
_, Jm_f = evalF(full(mid, mp), mp, True)
Y = np.linalg.inv(np.array([[float(e) for e in row] for row in Jm_f]))          # any real matrix
box = {j: iv.mpf([mid[j] - r, mid[j] + r]) for j in solv}
_, JX = evalF(full(box, iv), iv, True)
print(f'  interval Jacobian over the box done ({time.time() - T0:.0f}s)', flush=True)
Yiv = [[iv.mpf(float(Y[i, j])) for j in range(E)] for i in range(E)]
ok = True; worst = mpf(0)
for i in range(E):
    YF = iv.mpf(0); mag = mpf(0)
    for j in range(E): YF += Yiv[i][j] * Fm_iv[j]
    for j in range(E):
        cij = (iv.mpf(1) if i == j else iv.mpf(0)) - sum((Yiv[i][l] * JX[l][j] for l in range(E)), iv.mpf(0))
        mag += max(abs(cij.a), abs(cij.b))
    d = -YF + iv.mpf([-r, r]) * mag
    bound = max(abs(d.a), abs(d.b))
    worst = max(worst, bound / r)
    if not bound < r: ok = False
print(f'  Krawczyk (iv): box radius 2^-60, max |K-m|/r <= {mpmath.nstr(worst, 4)} -> {"PROVED" if ok else "NOT PROVED"} ({time.time() - T0:.0f}s)', flush=True)
