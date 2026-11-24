# math-record-toolkit

**Small, exact checkers and searches for attacking published mathematical records: certify, audit, polish.**

These are the scripts behind a run of record attempts on Terence Tao's [optimization-constants registry](https://github.com/teorth/optimizationproblems), the [AlphaEvolve problem repository](https://github.com/google-deepmind/alphaevolve_repository_of_problems), and Sloane's packing tables (Nov 2026). Each folder is self-contained, fast (seconds to minutes on 2 cores), and built around one rule: a number counts only after an exact or interval-arithmetic check passes.

## What it does

| Folder | Problem | What the scripts do | Outcome |
|---|---|---|---|
| `krawczyk-cylinders/` | Nine pairwise touching cylinders, unequal radii (AlphaEvolve 54) | Interval-Newton (Krawczyk) existence proof for a 52×52 polynomial system; two independent checkers (python-flint arb balls; mpmath.iv with forward-mode AD) | First rigorous proof that 9 touching cylinders exist ([issue #26](https://github.com/google-deepmind/alphaevolve_repository_of_problems/issues/26)) |
| `krawczyk-designs/` | Spherical t-designs (AlphaEvolve 32) | Krawczyk certification of numerical designs; gauge fixing plus column-pivoted QR for spare coordinates | N = 124, 198, 234 certified |
| `line-packings/` | Packing N lines in R³ (Grassmannian G(3,1)) | Repulsion warm start then SLSQP max-min search; exact rational checker and 50-digit interval checker | N = 20, 22, 26, 49, 54 beat Sloane's table (sent to Sloane 11/24) |
| `ramsey-k5-cayley/` | Ramsey multiplicity of K₅ (registry 89b) | Fast C evaluator for monochromatic-K₅ density of a Cayley step graphon on F₂⁸; KKT gradient, Hessian, single and pair flip searches | Showed the 0.001648970526* record is a strict local minimum in its class |
| `sunflower-49a/` | 3-sunflower-free capacity (registry 49a) | Incremental checker (re-checks only boxes touching a new set, ~10–15k candidates/s); half-level blocker screen; 1-for-2 exchange tester | 18.4M single sets and 90 exchanges: none fit ([#379 thread](https://github.com/teorth/optimizationproblems/pull/379)) |
| `limit-3e/` | Limit of the [M2026b] ⟨4,5⟩ construction (registry 3e) | Two independent evaluators: entropy-rate form and the certificate's finite formula at 60 digits | Found the listed limit was wrong ([issue #387](https://github.com/teorth/optimizationproblems/issues/387), fixed in PR #388) |
| `heilbronn-convex/` | Heilbronn, arbitrary convex box (AlphaEvolve 49) | LP first-order stationarity test plus SLSQP max-min polish | Records shown first-order stationary |

## How the runs are chosen

The work runs on a fixed consumer-plan compute and usage budget, so the expensive step (a timed search with exact verification) is spent only on problems that pass a cheap screen first.

1. **Delegated screening.** A second model (ChatGPT or Gemini) screens problems in batches of about 8 using a fixed prompt and a strict JSON schema ([`prompts/`](prompts/)). Every value must be tagged `opened source` or `search snippet only`, and anything unconfirmed is written `unknown`.
2. **Verify before run.** Every `run` recommendation is rechecked against the primary source (registry page, open pull requests, the record's own certificate) before any compute is spent. On 24 Nov 2026, 4 of 7 healthcare `run` calls survived the recheck; 3 were dropped (mature tables or algebraic records that local search cannot beat), and one problem marked `skip` was upgraded.
3. **Gates.** A problem runs only if the record's construction is public, an exact checker can be written, the live bar is confirmed in open PRs (registry pages lag by days), and the problem is not crowded (two or more groups improving it in the last 14 days).
4. **Sprint.** A 10-minute box on 2 cores: confirm the bar, build two independent exact checkers, reproduce the record, search from the record, verify. Every run ends with an 8-field writeup: objective, baseline, candidate, verification, record eligibility, novelty, search economics, decision.
5. **Post what holds, including negatives.** Corrections and negative results go back to the source thread, so the next person does not repeat the search.

### Status, 24 Nov 2026

| Problem | Venue | Result | Link |
|---|---|---|---|
| Nine touching cylinders | AlphaEvolve 54 | Existence proved (two Krawczyk checkers) | [issue #26](https://github.com/google-deepmind/alphaevolve_repository_of_problems/issues/26) |
| Line packings in R³, N = 20, 22, 26, 49, 54 | Sloane's Grassmannian table | Five improved packings, exact | sent to Sloane; `line-packings/` |
| 3e limiting ratio | teorth registry | Listed limit corrected (author confirmed) | [issue #387](https://github.com/teorth/optimizationproblems/issues/387), [PR #388](https://github.com/teorth/optimizationproblems/pull/388) |
| C_1a autocorrelation | teorth registry | 1.502664829454529727 | [PR #386](https://github.com/teorth/optimizationproblems/pull/386) |
| Heilbronn n = 11, circles n = 26/32 | AlphaEvolve 48, 36 | Exact-validity fixes to float-scored records | issues #24, #25 |
| Spherical designs t = 15, 19, 21 | AlphaEvolve 32 | Krawczyk certificates | [repo](https://github.com/jblack874/32---Spherical-designs) |
| 49a sunflower capacity | teorth registry | No: 18.4M single sets and 90 exchanges fail | [#379 comment](https://github.com/teorth/optimizationproblems/pull/379) |
| 89b Ramsey multiplicity K₅ | teorth registry | No: record is a strict local minimum in its class | `ramsey-k5-cayley/` |
| Heilbronn convex, C_1d, Erdős overlap, others | various | No gain; records tight or superseded | — |

Screened so far: 68 AlphaEvolve problems, 49 registry constants and 27 applied (healthcare) problems.

## Rules the scripts follow

- **Exact or interval only.** Floats find candidates; Fractions, arb balls or mpmath intervals decide them.
- **Two checkers that share no code** for any positive claim.
- **Reproduce the record first.** Every checker is run on the published certificate before it is trusted.
- **Start from the record, not from scratch**, and stop when the local structure says there is nothing to gain (KKT slack, positive-definite Hessian, exhausted flip neighborhoods).

## Honest limits

- Negative results are bounded by the classes searched; each folder's scripts state their class.
- `ramsey-k5-cayley/` gradient and Hessian use double-precision finite differences: enough for a "no descent" verdict, not a certificate.
- `sunflower-49a/` depends on Arhan Canli's checker ([quantavane-replays](https://github.com/arhancanli/quantavane-replays), commit `e53c299`), fetched by `fetch_and_patch.sh` rather than copied here. It is one checker, not an independent replay.
- Scripts are research code: short, direct, lightly commented.

## Run it

```bash
pip install numpy scipy mpmath python-flint

# line packings: verify the 5 improved packings exactly
cd line-packings && python3 chk_frac.py && python3 chk_mp.py

# nine touching cylinders: both Krawczyk checkers
cd krawczyk-cylinders && python3 kraw_arb.py && python3 check2_iv.py

# K5 Cayley graphon: reproduce Pinho's 0.0016489705256..., then KKT gradient
cd ramsey-k5-cayley && python3 make_q.py && gcc -O3 -fopenmp dens.c -o dens && ./dens q.txt && ./dens q.txt grad

# 49a: fetch Canli's checker, then screen exchanges
cd sunflower-49a && ./fetch_and_patch.sh && python3 exch.py canli 120 0 1

# 3e limit: both evaluators
cd limit-3e && python3 limit_entropy.py && python3 limit_finite.py
```

## How it works

| Piece | Where |
|---|---|
| Krawczyk operator with arb balls | `krawczyk-cylinders/kraw_arb.py`, `krawczyk-designs/krawczyk_design.py` |
| Independent interval checker (mpmath.iv + forward AD) | `*/check2_iv.py` |
| Max-min line packing search | `line-packings/lines.py` |
| Exact rational / interval packing check | `line-packings/chk_frac.py`, `chk_mp.py` |
| Cayley K₅ density with zero-pruning and weak-order multiplicities | `ramsey-k5-cayley/dens.c` |
| Hessian, single-flip and pair-flip neighborhoods | `ramsey-k5-cayley/hess2.c`, `flip.c`, `pair.c` |
| Incremental sunflower/containment check | `sunflower-49a/inc.py` |
| Half-level blocker screen and exchange tests | `sunflower-49a/exch.py`, `pairs.py` |
| Saddle-point limit evaluators | `limit-3e/` |
| LP stationarity test | `heilbronn-convex/h.py` |

## Sources and credit

- Records and certificates checked here belong to their authors: R. Pinho (89b round 4, [math-certificates](https://github.com/rpinho/math-certificates)), R. F. Tilley Jr. and A. Canli (49a), mizopl ([M2026b], 3e), N. J. A. Sloane and coauthors ([Grassmannian packings](https://neilsloane.com/grass/)), AlphaEvolve problem authors.
- Line-packing and cylinder certificates are in their folders; the cylinder proof repo is [jblack874/touching_cylinders_9_proof](https://github.com/jblack874/touching_cylinders_9_proof).

Joe Black ([@jblack874](https://github.com/jblack874)). Prepared with AI assistance (Claude, Anthropic).
