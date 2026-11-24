#!/usr/bin/env python3
"""Computer-assisted existence proof of an antipodal spherical t-design on S^2 near a numerical one.

t = 2k+1 odd, N points closed under x -> -x. Such a set is a t-design iff for every even-degree
spherical polynomial p of degree <= 2k: sum_X p = N * mean_{S^2} p. On S^2 the restrictions of the
monomials x^a y^b z^c with c in {0,1}, a+b+c = m even, 2 <= m <= 2k, together with 1, form a basis
of the even polynomials of degree <= 2k (count 1 + sum (2m+1) = 1 + E), so the conditions are E
polynomial equations F_abc = 2 sum_{i<=N/2} x_i^a y_i^b z_i^c - N mu_abc = 0 in the N/2 representatives.
Points are parametrised stereographically: x = 2u/D, y = 2v/D, z = (u^2+v^2-1)/D, D = 1+u^2+v^2.
E of the N parameters are solved for; the other N-E are fixed at dyadic values (column-pivoted QR picks
them). Krawczyk: if K(X) = m - Y F(m) + (I - Y F'(X))(X - m) lies in the interior of the box X, the
square system has a unique zero in X (all arithmetic in Arb ball arithmetic, python-flint).
Usage: krawczyk_design.py designs.json name t [prec_bits] [radius_exp]"""
import json, sys, time
import numpy as np
from fractions import Fraction
import flint
from flint import arb, arb_mat

name, t = sys.argv[2], int(sys.argv[3])
prec = int(sys.argv[4]) if len(sys.argv) > 4 else 320
rexp = int(sys.argv[5]) if len(sys.argv) > 5 else -40
X0 = np.array(json.load(open(sys.argv[1]))[name], float)
N = len(X0); k = (t - 1) // 2; assert t % 2 == 1
X0 /= np.linalg.norm(X0, axis=1)[:, None]
T0 = time.time()

# ---- antipodal pairing, representatives in the lower hemisphere
used = np.zeros(N, bool); reps = []
for i in range(N):
    if used[i]: continue
    j = int(np.argmin(np.linalg.norm(X0 + X0[i], axis=1)))
    assert j != i and not used[j] and np.linalg.norm(X0[j] + X0[i]) < 1e-6, 'not antipodal'
    used[i] = used[j] = True
    reps.append(X0[i] if X0[i, 2] <= X0[j, 2] else X0[j])
R = np.array(reps); h = len(R); P = 2 * h
mons = [(a, m - c - a, c) for m in range(2, 2 * k + 1, 2) for c in (0, 1) for a in range(m - c + 1)]
E = len(mons)


def dfact(n):
    r = 1
    while n > 1: r *= n; n -= 2
    return r


def mu(a, b, c):  # mean over S^2 of x^a y^b z^c, c in {0,1}
    if c == 1 or a % 2 or b % 2: return Fraction(0)
    return Fraction(dfact(a - 1) * dfact(b - 1), dfact(a + b + 1))


MU = [mu(*q) for q in mons]
print(f'{name}: t={t} N={N} pairs={h} params={P} equations={E} (spare {P - E})', flush=True)

# ---- float stage: parameters, residual, Jacobian
uv0 = np.column_stack([R[:, 0] / (1 - R[:, 2]), R[:, 1] / (1 - R[:, 2])]).ravel()


def float_FJ(p, want_J=True):
    u, v = p[0::2], p[1::2]; s = u * u + v * v; D = 1 + s
    x, y, z = 2 * u / D, 2 * v / D, (s - 1) / D
    xu, xv = (2 * D - 4 * u * u) / D ** 2, -4 * u * v / D ** 2
    yu, yv = -4 * u * v / D ** 2, (2 * D - 4 * v * v) / D ** 2
    zu, zv = 4 * u / D ** 2, 4 * v / D ** 2
    F = np.empty(E); J = np.zeros((E, P)) if want_J else None
    xp = [np.ones(h)]; yp = [np.ones(h)]
    for _ in range(2 * k + 1): xp.append(xp[-1] * x); yp.append(yp[-1] * y)
    for r, (a, b, c) in enumerate(mons):
        zc = z if c else 1.0
        val = xp[a] * yp[b] * zc
        F[r] = 2 * val.sum() - N * float(MU[r])
        if want_J:
            dx = a * xp[a - 1] * yp[b] * zc if a else 0.0
            dy = b * xp[a] * yp[b - 1] * zc if b else 0.0
            dz = xp[a] * yp[b] if c else 0.0
            J[r, 0::2] = 2 * (dx * xu + dy * yu + dz * zu)
            J[r, 1::2] = 2 * (dx * xv + dy * yv + dz * zv)
    return F, J


p = uv0.copy()
F, J = float_FJ(p)
print(f'  published max|F| = {abs(F).max():.2e}', flush=True)
for it in range(20):  # min-norm Gauss-Newton
    F, J = float_FJ(p)
    if abs(F).max() < 1e-14: break
    p -= np.linalg.lstsq(J, F, rcond=None)[0]
F, J = float_FJ(p)
print(f'  float refine: max|F| = {abs(F).max():.2e}, moved {abs(p - uv0).max():.1e}', flush=True)
import scipy.linalg as sla
Qr, Rr, piv = sla.qr(J, pivoting=True, mode='economic')
solve_idx = np.sort(piv[:E]); fix_idx = np.sort(piv[E:])
sv = np.linalg.svd(J[:, solve_idx], compute_uv=False)
print(f'  square block: sigma_min {sv[-1]:.2e}, cond {sv[0] / sv[-1]:.2e}; fixed params {list(fix_idx)}', flush=True)

# ---- Arb stage
flint.ctx.prec = prec
DY = 60  # fixed parameters rounded to multiples of 2^-60 (exact dyadics)
pfix = {int(j): Fraction(round(p[j] * 2 ** DY), 2 ** DY) for j in fix_idx}
MUa = [arb(int(q.numerator)) / int(q.denominator) for q in MU]


def arb_FJ(vals, want_J=True):
    """vals: list of P arb balls. Returns F (E arbs) and J restricted to solve_idx (E x E arbs)."""
    col = {int(j): c for c, j in enumerate(solve_idx)}
    F = [arb(0)] * E; Jl = [[arb(0)] * E for _ in range(E)] if want_J else None
    for i in range(h):
        u, v = vals[2 * i], vals[2 * i + 1]; s = u * u + v * v; D = 1 + s; D2 = D * D
        x, y, z = 2 * u / D, 2 * v / D, (s - 1) / D
        xu, xv = (2 * D - 4 * u * u) / D2, -4 * u * v / D2
        yu, yv = xv, (2 * D - 4 * v * v) / D2
        zu, zv = 4 * u / D2, 4 * v / D2
        xp = [arb(1)]; yp = [arb(1)]
        for _ in range(2 * k + 1): xp.append(xp[-1] * x); yp.append(yp[-1] * y)
        cu, cv = col.get(2 * i), col.get(2 * i + 1)
        for r, (a, b, c) in enumerate(mons):
            xy = xp[a] * yp[b]
            F[r] = F[r] + (xy * z if c else xy)
            if want_J and (cu is not None or cv is not None):
                zc = z if c else arb(1)
                dx = a * xp[a - 1] * yp[b] * zc if a else arb(0)
                dy = b * xp[a] * yp[b - 1] * zc if b else arb(0)
                dz = xy if c else arb(0)
                if cu is not None: Jl[r][cu] = Jl[r][cu] + 2 * (dx * xu + dy * yu + dz * zu)
                if cv is not None: Jl[r][cv] = Jl[r][cv] + 2 * (dx * xv + dy * yv + dz * zv)
    F = [2 * F[r] - N * MUa[r] for r in range(E)]
    return F, Jl


def assemble(sol):  # sol: dict solve-index -> arb
    return [sol[j] if j in sol else arb(int(pfix[j].numerator)) / int(pfix[j].denominator) for j in range(P)]


# high-precision Newton on the square system (midpoints only)
sol = {int(j): arb(float(p[j])) for j in solve_idx}
for it in range(8):
    Fa, Ja = arb_FJ(assemble(sol))
    res = max(float(abs(f).mid()) for f in Fa)
    print(f'  arb Newton {it}: max|F| = {res:.3e}  ({time.time() - T0:.0f}s)', flush=True)
    if res < 2.0 ** (-prec + 40): break
    step = arb_mat(Ja).solve(arb_mat([[f] for f in Fa]))
    for c, j in enumerate(solve_idx):
        sol[int(j)] = (sol[int(j)] - step[c, 0]).mid()
m = {j: v.mid() for j, v in sol.items()}

# Krawczyk test on the box m +- r
r = arb(2) ** rexp
Fm, Jm = arb_FJ(assemble(m))
Jmid = arb_mat([[e.mid() for e in row] for row in Jm])
Y = Jmid.inv()
Y = arb_mat([[Y[i, j].mid() for j in range(E)] for i in range(E)])  # any real matrix will do
box = {j: arb(m[j], r) for j in m}
Fb, JX = arb_FJ(assemble(box))
I_YJ = arb_mat.eye(E) if hasattr(arb_mat, 'eye') else arb_mat([[arb(1) if i == j else arb(0) for j in range(E)] for i in range(E)])
I_YJ = I_YJ - Y * arb_mat(JX)
dX = arb_mat([[arb(0, r)] for _ in range(E)])
YF = Y * arb_mat([[f] for f in Fm])
IdX = I_YJ * dX
ok = True; worst = 0.0
for c in range(E):
    d = -YF[c, 0] + IdX[c, 0]          # K_c - m_c
    inside = (abs(d) < r)               # certainly inside the open box
    w = float((abs(d).upper() / r).mid()) if hasattr(abs(d), 'upper') else float(((abs(d).mid() + abs(d).rad()) / r).mid())
    worst = max(worst, w)
    ok = ok and bool(inside)
nrm = max(float(sum((abs(I_YJ[i, j]).mid() + abs(I_YJ[i, j]).rad()) for j in range(E)).mid()) for i in range(E))
print(f'  Krawczyk: box radius 2^{rexp}, max |K-m|/r = {worst:.3e}, ||I - Y F\'(X)||_inf <= {nrm:.3e}', flush=True)
# separation of the N points (all distinct)
fl = np.array([float(assemble(m)[j].mid()) for j in range(P)])
u, v = fl[0::2], fl[1::2]; s = u * u + v * v; Pt = np.column_stack([2 * u, 2 * v, s - 1]) / (1 + s)[:, None]
All = np.vstack([Pt, -Pt]); dmin = min(np.linalg.norm(All[i] - All[j]) for i in range(len(All)) for j in range(i))
print(f'  min pairwise distance of the {len(All)} points ~ {dmin:.3e} (box radius 2^{rexp} on parameters)', flush=True)
print(f'  RESULT {name}: {"PROVED" if ok else "NOT PROVED"} ({time.time() - T0:.0f}s)', flush=True)
out = {'name': name, 't': t, 'N': N, 'proved': ok, 'prec_bits': prec, 'box_radius': f'2^{rexp}',
       'fixed_params_dyadic_2^-60': {str(j): str(q) for j, q in pfix.items()},
       'solve_params_mid': {str(j): m[j].str(40, radius=False) for j in m}, 'max_K_over_r': worst, 'norm_I_minus_YJ': nrm}
json.dump(out, open(f'proof_{name}.json', 'w'), indent=0)
