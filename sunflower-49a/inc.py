import sys, json, time, itertools
mode, cls, t_budget = sys.argv[1], sys.argv[2], float(sys.argv[3])
src = open('tilley_a.py').read().split('t0 = time.time()')[0]
import os
EXF = os.environ.get('EXF', 'extras.json')
sys.argv = ['tilley_a.py', 'sunflower_check.py', '--extra-left', EXF, '--extra-right', EXF]
g = {'__name__': 'tilley_prefix'}
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src, 'tilley_prefix', 'exec'), g)
L0, L1, R0, R1, TOP = g['L0'], g['L1'], g['R0'], g['R1'], g['TOP']
half_patterns, half_relations, HP, HR, HALF_FAMS = g['half_patterns'], g['half_relations'], g['HP'], g['HR'], g['HALF_FAMS']
PB, QB = g['PBIT'], g['QBIT']
BLset = set(g['BL'])
def purge(ids):
    for D in (HP, HR):
        for k in [k for k in D if any(i in ids for i in k)]: del D[k]
    for i in ids: HALF_FAMS.pop(i, None)
def check(S):
    sl, sr = S & ~QB, S & ~PB
    lq, rp = bool(S & QB), bool(S & PB)
    singles = []
    def one(v):
        f = [v]; singles.append(f); return f
    NEW = []
    if not lq: NEW.append(([sl], 'L0'))
    a, b = one(sl), one(sr)
    NEW = []
    if not lq: NEW.append((a, R1))
    if rp: NEW.append((L0, b))
    if (not lq) and rp: NEW.append((a, b))
    if lq: NEW.append((a, R0))
    if not rp: NEW.append((L1, b))
    if lq and not rp: NEW.append((a, b))
    allb = [(X, Y) for _, X, Y in TOP] + NEW
    n_old = len(TOP)
    ok = True
    for i in range(len(allb)):
        for j in range(len(allb)):
            if i < n_old and j < n_old: continue
            rl, rr = half_relations(allb[i][0], allb[j][0]), half_relations(allb[i][1], allb[j][1])
            if i == j and len(allb[i][0]) == 1 and len(allb[i][1]) == 1: continue
            if rl and rr and ((rl & 2) or (rr & 2)): ok = False; break
        if not ok: break
    if ok:
        for i, j, k in itertools.combinations_with_replacement(range(len(allb)), 3):
            if k < n_old: continue
            pl = half_patterns(allb[i][0], allb[j][0], allb[k][0]); pr = half_patterns(allb[i][1], allb[j][1], allb[k][1])
            if any((pl >> x & 1) and (pr >> y & 1) and (x | y) == 7 for x in range(8) for y in range(8)): ok = False; break
    purge({id(f) for f in singles})
    return ok
FULL = 1023
parts = [0, FULL] + [FULL & ~(1 << i) for i in range(10)] + [1 << i for i in range(10)]
if mode == 'selftest':
    X = json.load(open('extras.json'))
    # X1, X2 are already in the base: adding them again must be refused or treated as duplicates; use Pinho's 64768 (known refusal)
    print('selftest refuse 64768:', not check(64768), flush=True)
    if EXF != 'extras.json': print('selftest accept X1 261940 on X2-only base:', check(261940), '| accept X2 on X1-only base check needs other file', flush=True)
    sys.exit()
H = g['H_AVOID'] + g['H_CONT']
def gen(cls):
    if cls == 'canli':
        for core in range(256):
            for a in (0, FULL):
                for b in (0, FULL): yield core | a << 8 | b << 18
    elif cls in ('noport', 'port'):
        for core in range(256):
            if (cls == 'noport') == bool(core & 3): continue
            for a in parts:
                for b in parts:
                    if a in (0, FULL) and b in (0, FULL) and not core & 3: continue
                    yield core | a << 8 | b << 18
    elif cls == 'onepend':
        for core in range(256):
            for e in (0, FULL):
                for x in range(1024):
                    yield core | x << 8 | e << 18
                    yield core | e << 8 | x << 18
    elif cls == 'struct':
        sp = sorted(set([0, FULL] + [FULL & ~(1 << i) for i in range(10)] + [1 << i for i in range(10)] + H + [FULL & ~h for h in H]))
        lo, hi = int(os.environ.get('CLO', 0)), int(os.environ.get('CHI', 256))
        for core in range(lo, hi):
            for a in sp:
                for b in sp: yield core | a << 8 | b << 18
seen = set()
t0 = time.time(); passes = []; n = 0; last = None
for S in gen(cls):
    if S in BLset or S in seen: continue
    seen.add(S)
    if time.time() - t0 > t_budget: break
    n += 1; last = S
    if check(S): passes.append(S); print('PASS', S, flush=True)
print('class %s: checked %d in %.1f s, passes %d, last %s' % (cls, n, time.time() - t0, len(passes), last), flush=True)
json.dump(passes, open('inc_pass_%s_%s.json' % (cls, os.environ.get('CLO', '')), 'w'))
