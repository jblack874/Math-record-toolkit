import numpy as np, itertools, sys, time
from mpmath import mp, mpf, log, findroot
def setup(M, B):
    M = sorted(m for m in M if m <= B); Ms = set(M)
    kap = {}
    for d in range(1, B + 1):
        c = [2 * b + d for b in M if b + d in Ms]
        if c: kap[d] = min(c)
    S = sorted({a + b for a in M for b in M})
    return np.array(list(kap.values()), float), np.array(S, float), len(kap) == B
def ratio(kap, S, x):
    w = x ** kap; Z = 1 + 2 * w.sum(); p = w / Z; ell = (p * kap).sum()
    H = np.log(Z) - 2 * ell * np.log(x)
    lo, hi = 1e-9, 1 - 1e-12                     # solve mean_S(y) = 2*ell (mean increases with y)
    for _ in range(80):
        y = (lo + hi) / 2; v = y ** S; m = (S * v).sum() / v.sum()
        if m < 2 * ell: lo = y
        else: hi = y
    y = (lo + hi) / 2
    den = np.log((y ** S).sum()) - 2 * ell * np.log(y)
    return H / den, y, H, den
def best(kap, S):
    a, b = 0.3, 0.99; f = lambda x: -ratio(kap, S, x)[0]
    g = (5 ** .5 - 1) / 2
    c, d = b - g * (b - a), a + g * (b - a); fc, fd = f(c), f(d)
    for _ in range(70):
        if fc < fd: b, d, fd = d, c, fc; c = b - g * (b - a); fc = f(c)
        else: a, c, fc = c, d, fd; d = a + g * (b - a); fd = f(d)
    x = (a + b) / 2; r, y, H, den = ratio(kap, S, x); return r, x, y, H, den
if __name__ == '__main__':
    B = 400
    sg = lambda gens: {sum(c * g for c, g in zip(cs, gens)) for cs in itertools.product(range(B + 1), repeat=len(gens)) if sum(c * g for c, g in zip(cs, gens)) <= B} if len(gens) <= 2 else None
    k, S, ok = setup(range(B + 1), B); print('gapless (HRY 1.2715533031636):', best(k, S)[:3])
    k, S, ok = setup(sg([4, 5]), B); print('<4,5> (registry limit 1.2725580515):', best(k, S)[:3])
    k, S, ok = setup(sg([4, 5]), 160); print('<4,5> B=160 at cert x,y:', ratio(k, S, 0.814897)[0], 'H', ratio(k, S, 0.814897)[2])
