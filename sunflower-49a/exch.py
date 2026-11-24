import numpy as np, time, json, sys, os
from exch_prefix import load
cls, budget = sys.argv[1], float(sys.argv[2]); part, nparts = int(sys.argv[3]), int(sys.argv[4])
g = load(); BLl = g['BL']; BL = np.array(BLl, dtype=np.int64); BS = set(BLl)
FULL = 1023
def blockers(Y):
    """Half-level obstruction to adding Y: return set of member indices hitting every conflict, or None if no single member does (or no half-level conflict -> 'join')."""
    W = BL & Y
    cand = None
    c = np.nonzero((W == BL) | (W == Y))[0]
    for i in c:
        s = {int(i)}; cand = s if cand is None else cand & s
        if cand is not None and not cand: return None
    O = BL & ~Y
    ok = O != 0
    idx = np.nonzero(ok)[0]
    idx = idx[np.lexsort((O[idx], W[idx]))]
    Ws = W[idx]
    u, st, cnt = np.unique(Ws, return_index=True, return_counts=True)
    for k in np.nonzero(cnt > 1)[0]:
        ii = idx[st[k]:st[k]+cnt[k]]; o = O[ii]
        M = (o[:, None] & o[None, :]) == 0
        a, b = np.nonzero(np.triu(M, 1))
        if len(a) == 0: continue
        if cand is None:
            # intersection of all pairs {a,b}
            ca = set(ii[a].tolist()); cb = set(ii[b].tolist())
            pairs_mem = None
            for x, y in zip(ii[a][:50].tolist(), ii[b][:50].tolist()):
                pairs_mem = {x, y} if pairs_mem is None else pairs_mem & {x, y}
                if not pairs_mem: return None
            # verify on all pairs
            for m in list(pairs_mem):
                if not np.all((ii[a] == m) | (ii[b] == m)): pairs_mem.discard(m)
            cand = pairs_mem
        else:
            for m in list(cand):
                if not np.all((ii[a] == m) | (ii[b] == m)): cand.discard(m)
        if not cand: return None
    return 'join' if cand is None else cand
parts = [0, FULL] + [FULL & ~(1 << i) for i in range(10)] + [1 << i for i in range(10)]
def gen():
    if cls == 'canli':
        for core in range(256):
            for a in (0, FULL):
                for b in (0, FULL): yield core | a << 8 | b << 18
    elif cls == 'parts':
        for core in range(256):
            for a in parts:
                for b in parts: yield core | a << 8 | b << 18
t0 = time.time(); n = 0; single = {}; nj = 0; nm = 0
for k, Y in enumerate(gen()):
    if k % nparts != part or Y in BS: continue
    if time.time() - t0 > budget: break
    n += 1
    r = blockers(Y)
    if r is None: nm += 1
    elif r == 'join': nj += 1
    else:
        for s in r: single.setdefault(BLl[s], []).append(Y)
json.dump(single, open('exch_%s_%d.json' % (cls, part), 'w'))
print('cls %s part %d: %d Y in %.0f s; multi-blocked %d, no half conflict %d, single-blocker Y %d over %d members'
      % (cls, part, n, time.time()-t0, nm, nj, sum(len(v) for v in single.values()), len(single)), flush=True)
