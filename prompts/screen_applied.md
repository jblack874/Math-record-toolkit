# Screening prompt: applied problems with record tables (healthcare batch)

For problems whose records live in tables or papers rather than a registry (sequence design, packings, designs, codes). One batch of about 8 per chat.

```
You are screening open math problems that have healthcare applications. The goal is to find problems where a short computer run (≤10 min, 2 CPU cores, Python) could produce a NEW, EXACTLY-VERIFIED record: a better construction than the best published one, checked in exact or interval arithmetic.

Your batch is HC1. Screen only these problems: <id> <name> (<application>), ...

For EACH problem:
1. Define the exact scored quantity: what is maximized or minimized, and under which constraints. If the problem is a conjecture or a proof problem with no scored construction, say so. Then name the finite sub-question a computer could answer, if one exists.
2. Live record: the maintained record table (repository, database or website), or the newest paper. Give its URL and last-update date. List the 3 entries that look softest: oldest, found by weakest method, or with the largest gap to the known bound. Give each value as a string with all digits, its source, and whether you OPENED the source or only saw a search snippet. Search 2024–2026 arXiv and GitHub for newer values the table missed.
3. Certificate: are record constructions downloadable? URL and format.
4. Checker: is there an official verifier? Is it float or exact? Could an exact checker be written in under 50 lines?
5. Lane fit (yes/no/unknown, one line of evidence each): Lane 1 validity audit; Lane 2 exactification (Krawczyk); Lane 3 local search from the record (tight or loose?).
6. Already reported: recent issues, papers or posts claiming improvements, or saying the table is exhausted at small sizes.
7. Cost estimate to a verified attempt (minutes, cores, memory).
8. Recommend run or skip. Skip pure proof problems, anything needing >1 hr compute, problems with no public record table, and tables where every entry is proven optimal.

Rules: Never guess. Write "unknown" for anything not confirmed and list it under not_checked. Do not round values. A table's "last updated" date isn't proof it's current; search for newer papers.

Output ONLY one JSON code block, no prose, in exactly this shape:

{"batch": "HC1", "screened_on": "YYYY-MM-DD", "problems": [{
  "id": "",
  "objective": "",
  "record_table": {"url": "", "last_updated": "", "how_confirmed": "opened source | search snippet only"},
  "soft_entries": [{"instance": "", "value": "", "source_url": "", "date": "", "method": "", "known_bound": "", "how_confirmed": ""}],
  "newer_than_table": [{"url": "", "value": "", "date": ""}],
  "certificate": {"public": true, "url": "", "format": "sequence|matrix|coordinates|design blocks|none"},
  "checker": {"official_url": "", "float_or_exact": "", "exact_checker_easy": "yes|no"},
  "lane1_validity_audit": {"fit": "yes|no|unknown", "evidence": ""},
  "lane2_exactification": {"fit": "yes|no|unknown", "unknowns": "", "equations": "", "symmetries_removed": "", "evidence": ""},
  "lane3_local_search": {"fit": "yes|no|unknown", "tight_or_loose": "", "evidence": ""},
  "already_reported": [{"url": "", "what": ""}],
  "cost_estimate": "",
  "recommend": "run|skip",
  "not_checked": []
}], "ranking": ["ids, best first"]}
```
