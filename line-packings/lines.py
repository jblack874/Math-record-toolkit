import numpy as np, sys, time
from scipy.optimize import minimize
from multiprocessing import Pool
SL = dict(l.split() for l in """20 32.7071
21 32.2161
22 31.8963
23 30.5062
24 30.1628
25 29.2486
26 28.7126
27 28.2495
28 27.8473
29 27.5244
30 26.9983
31 26.4987
32 25.9497
33 25.5748
34 25.2567
35 24.8702
36 24.5758
37 24.2859
38 24.0886
39 23.8433
40 23.3293
41 22.9915
42 22.7075
43 22.5383
44 22.2012
45 22.0481
46 21.8426
47 21.6609
48 21.4663
49 21.1610
50 20.8922
51 20.6903
52 20.4914
53 20.2685
54 20.1555
55 20.1034""".splitlines())
def angle(U):
    U = U / np.linalg.norm(U, axis=1)[:, None]; G = np.abs(U @ U.T); np.fill_diagonal(G, 0)
    return np.degrees(np.arccos(G.max()))
def run(N, budget=22.0, seed=0):
    rng = np.random.default_rng(seed); best = (0, None); t0 = time.time(); iu = np.triu_indices(N, 1)
    while time.time() - t0 < budget:
        U = rng.normal(size=(N, 3)); U /= np.linalg.norm(U, axis=1)[:, None]
        for _ in range(300):                                   # repulsion warm-up on lines
            G = U @ U.T; np.fill_diagonal(G, 0); F = (G / (1 - G**2 + 1e-9)**3) @ U
            U -= 0.002 * (F - (F * U).sum(1)[:, None] * U); U /= np.linalg.norm(U, axis=1)[:, None]
        x0 = np.r_[U.ravel(), (np.abs(U @ U.T)[iu]).max()**2]
        cons = [{'type': 'ineq', 'fun': lambda x: x[-1] - ((x[:-1].reshape(N, 3) @ x[:-1].reshape(N, 3).T)[iu])**2},
                {'type': 'eq', 'fun': lambda x: (x[:-1].reshape(N, 3)**2).sum(1) - 1}]
        r = minimize(lambda x: x[-1], x0, jac=lambda x: np.r_[np.zeros(3*N), 1], constraints=cons, method='SLSQP', options={'maxiter': 400, 'ftol': 1e-15})
        a = angle(r.x[:-1].reshape(N, 3))
        if a > best[0]: best = (a, r.x[:-1].reshape(N, 3))
    return N, best[0], best[1]
if __name__ == '__main__':
    Ns = list(range(20, 56))
    with Pool(2) as p: res = p.map(run, Ns)
    out = {}
    for N, a, U in res:
        d = a - float(SL[str(N)]); out[N] = U.tolist()
        print('N=%2d ours %.6f  Sloane %s  diff %+.5f %s' % (N, a, SL[str(N)], d, '<-- ABOVE' if d > 5e-5 else ''))
    import json; json.dump(out, open('best.json', 'w'))
