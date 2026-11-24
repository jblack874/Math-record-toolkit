"""Independent check of the 3e limit, written separately from limit.py.
Uses the certificate's own finite formula: n_d = floor(N x^kappa(d)/Z), L = sum n_d kappa(d),
log D_N = logGamma(N+1) - logGamma(n_0+1) - 2 sum logGamma(n_d+1), log S_N(y) = N log P_+(y) - 2L log y,
with y solving the saddle equation exactly (findroot), all in mpmath at 60 digits. Then optimizes x."""
from mpmath import mp, mpf, log, loggamma, floor, findroot, nstr
mp.dps = 60
def alphabet(B):
    H = sorted({4*i + 5*j for i in range(B//4 + 1) for j in range(B//5 + 1) if 4*i + 5*j <= B})
    Hs = set(H)
    kap = [min(2*b + d for b in H if b + d in Hs) for d in range(1, B + 1)]
    S = sorted({a + b for a in H for b in H})
    return kap, S
def ratio(N, B, x, y=None):
    kap, S = alphabet(B); x = mpf(x)
    w = [x**k for k in kap]; Z = 1 + 2*sum(w)
    n = [floor(N*wi/Z) for wi in w]; n0 = N - 2*sum(n); L = sum(ni*k for ni, k in zip(n, kap))
    logD = loggamma(N + 1) - loggamma(n0 + 1) - 2*sum(loggamma(ni + 1) for ni in n)
    if y is None:
        f = lambda yy: sum(s*yy**s for s in S)/sum(yy**s for s in S) - 2*L/N
        y = findroot(f, mpf('0.85'))
    y = mpf(y); logS = N*log(sum(y**s for s in S)) - 2*L*log(y)
    return logD/logS, logD, logS, y
# 1) reproduce the B=160 certificate's numbers at its own x, y, N
r, D, S_, _ = ratio(mpf(10)**15, 160, mpf(814897)/10**6, mpf(851418)/10**6)
print('cert reproduction: log D_N =', nstr(D, 22), '| log S_N =', nstr(S_, 22), '| ratio', nstr(r, 20))
# 2) optimize x (golden section) at very large N for B = 160 and 320
for B in (160, 320):
    for N in (mpf(10)**15, mpf(10)**30):
        a, b = mpf('0.80'), mpf('0.83'); g = (mpf(5).sqrt() - 1)/2
        F = lambda x: -ratio(N, B, x)[0]
        c, d = b - g*(b - a), a + g*(b - a); fc, fd = F(c), F(d)
        for _ in range(45):
            if fc < fd: b, d, fd = d, c, fc; c = b - g*(b - a); fc = F(c)
            else: a, c, fc = c, d, fd; d = a + g*(b - a); fd = F(d)
        x = (a + b)/2; print('B=%d N=1e%d: best x %s ratio %s' % (B, int(log(N, 10) + 0.5), nstr(x, 10), nstr(-F(x), 16)), flush=True)
