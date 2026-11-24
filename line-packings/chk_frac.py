import json, sys
from fractions import Fraction as F
d = json.load(open('best.json'))
SL = {20: '0.291972234676310', 22: '0.279189472772918', 26: '0.230800083465611', 49: '0.130314072572911', 54: '0.118727643427711'}
for N, s in SL.items():
    P = [[F(x) for x in v] for v in d[str(N)]]   # exact binary floats as rationals
    m = None
    for i in range(N):
        for j in range(i + 1, N):
            u, v = P[i], P[j]
            dot = sum(a * b for a, b in zip(u, v)); nu = sum(a * a for a in u); nv = sum(b * b for b in v)
            s2 = 1 - dot * dot / (nu * nv)
            m = s2 if m is None or s2 < m else m
    print(N, float(m), 'beats Sloane' if m > F(s) else 'NOT', float(m - F(s)))
