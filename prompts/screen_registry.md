# Screening prompt: registry constants (Gemini / ChatGPT)

Paste into a fresh chat, one batch of about 8 constants per chat. Replace the batch label and the constant list. Attach a zip of registry pages and open-PR diffs if the model cannot browse.

```
You are screening open constants from Terence Tao's optimization-constants registry (github.com/teorth/optimizationproblems; pages at https://teorth.github.io/optimizationproblems/constants/<id>.html) for one purpose: find constants where a short computer run (≤10 min, 2 CPU cores, Python) could produce a NEW, EXACTLY-VERIFIED record bound.

Your batch is R01. Screen only these constants: <id>, <id>, ...

For EACH constant:
1. Live bar: best bound in each direction. Check, in order: the constant's registry page; EVERY open pull request touching constants/<id>.md (open each relevant PR, read its diff and latest comments); then 2025–2026 arXiv papers. Give values as strings with all published digits, source URL, date, and whether you OPENED the source or only saw a search snippet.
2. Certificate: is the record construction public (coordinates, file, explicit formula, code)? URL.
3. Checker: official/author verifier? Float or exact? Tolerance?
4. Lane fit (yes/no/unknown, one line of evidence each):
   - Lane 1, validity audit: float-scored record where an exact recheck could invalidate or tighten it?
   - Lane 2, exactification: record is a numerical solution of a polynomial/algebraic system that interval-Newton (Krawczyk) could certify? Unknowns, equations, symmetries.
   - Lane 3, local search: finite construction that polishing from the record could improve in 10 min? Tight (many constraints active) or loose?
5. Already reported: issues/PRs/comments saying someone already polished, verified, or tried to improve it.
6. Activity: how many groups posted improvements in the last 14 days (crowded = 2+).
7. Cost estimate to a verified attempt (minutes, cores, memory).
8. Recommend run or skip. Skip: pure proof problems, asymptotic exponents with no finite construction, >1 hr compute, no public construction, or crowded with an improvement in the last 7 days.

Rules: Never guess. Write "unknown" for anything not confirmed and list it under not_checked. Do not round values. A registry page is NOT the live bar until you have checked open PRs. If you cannot browse, say "BROWSING UNAVAILABLE" and stop.

Output ONLY one JSON code block, no prose, in exactly this shape:

{"batch": "R01", "screened_on": "YYYY-MM-DD", "problems": [{
  "id": "",
  "objective": "exact quantity, min or max, constraints",
  "live_record": {"upper": {"value": "", "source_url": "", "source_type": "paper|repo_pr|registry|repo_issue|notebook", "date": "", "how_confirmed": "opened source | search snippet only"},
                  "lower": {"value": "", "source_url": "", "source_type": "", "date": "", "how_confirmed": ""}},
  "open_prs_checked": ["#NNN: what it claims"],
  "certificate": {"public": true, "url": "", "format": "coordinates|construction file|formula|code|none"},
  "checker": {"official_url": "", "float_or_exact": "", "tolerance": ""},
  "lane1_validity_audit": {"fit": "yes|no|unknown", "evidence": ""},
  "lane2_exactification": {"fit": "yes|no|unknown", "unknowns": "", "equations": "", "symmetries_removed": "", "evidence": ""},
  "lane3_local_search": {"fit": "yes|no|unknown", "tight_or_loose": "", "evidence": ""},
  "already_reported": [{"url": "", "what": ""}],
  "activity_14d": "",
  "cost_estimate": "",
  "recommend": "run|skip",
  "not_checked": []
}], "ranking": ["ids, best first"]}
```
