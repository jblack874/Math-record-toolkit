import json
from mpmath import iv, mpf
iv.dps = 50
d = json.load(open('best.json'))
SL = {20: '0.291972234676310', 22: '0.279189472772918', 26: '0.230800083465611', 49: '0.130314072572911', 54: '0.118727643427711'}
for N, s in SL.items():
    P = [[iv.mpf(repr(x)) for x in v] for v in d[str(N)]]
    lo = None
    for i in range(N):
        for j in range(i + 1, N):
            u, v = P[i], P[j]
            c = (u[0]*v[0]+u[1]*v[1]+u[2]*v[2])**2 / ((u[0]**2+u[1]**2+u[2]**2)*(v[0]**2+v[1]**2+v[2]**2))
            s2 = 1 - c
            lo = s2.a if lo is None or s2.a < lo else lo
    print(N, 'interval lower bound', iv.nstr(lo, 17), 'beats' if lo > mpf(s) else 'NOT')
