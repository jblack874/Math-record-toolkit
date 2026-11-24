import json, subprocess, itertools, sys, time
d = {}
for f in ['exch_parts_0.json','exch_parts_1.json','exch_canli_0.json','exch_canli_1.json']:
    for s, v in json.load(open(f)).items(): d.setdefault(int(s), set()).update(v)
part, budget = int(sys.argv[1]), float(sys.argv[2])
X = [268173364, 261940]
jobs = []
for s, ys in sorted(d.items()):
    ys = sorted(ys)
    for a, b in itertools.combinations(ys, 2):
        if (a & b) in (a, b): continue
        jobs.append((s, a, b))
print('pairs', len(jobs), flush=True)
t0 = time.time(); res = []
for k, (s, a, b) in enumerate(jobs):
    if k % 2 != part: continue
    if time.time() - t0 > budget: print('budget hit at', k); break
    ex = [x for x in X if x != s] + [a, b]
    json.dump(ex, open('ex_%d.json' % part, 'w')); json.dump([s], open('dr_%d.json' % part, 'w'))
    out = subprocess.run(['python3', 'tilley_x.py', 'sunflower_check.py', '--extra-left', 'ex_%d.json' % part, '--extra-right', 'ex_%d.json' % part, '--drop', 'dr_%d.json' % part], capture_output=True, text=True).stdout
    v = 'RESULT PASS' in out
    r = [l for l in out.splitlines() if l.startswith('RATE20')]
    res.append((s, a, b, v, r[0] if r else ''))
    if v: print('PASS', s, a, b, r, flush=True)
json.dump(res, open('pairs_res_%d.json' % part, 'w'))
print('part', part, 'done', len(res), 'in %.0f s' % (time.time() - t0), 'passes', sum(r[3] for r in res), flush=True)
