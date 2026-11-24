# Follow-up prompt: restate a free-form screen as strict JSON

Use after a model has answered in prose. Every value comes back as a string with its source and how it was confirmed, so the next model can recompute instead of retyping.

```
Now convert your results into a single JSON code block for handoff to another model. No prose outside the block. Use exactly this shape, one object per problem, and write "unknown" for anything you did not confirm (never guess):

{"batch": "NN", "screened_on": "YYYY-MM-DD", "problems": [{
  "id": 0,
  "objective": "exact quantity, min or max, constraints",
  "live_record": {"value": "as published, all digits, as a string", "source_url": "", "source_type": "paper|repo_issue|repo_pr|arena|registry|notebook", "date": "", "how_confirmed": "opened source | search snippet only"},
  "certificate": {"public": true, "url": "", "format": "coordinates|construction file|none"},
  "checker": {"official_url": "", "float_or_exact": "", "tolerance": ""},
  "lane1_validity_audit": {"fit": "yes|no|unknown", "evidence": ""},
  "lane2_exactification": {"fit": "yes|no|unknown", "unknowns": "", "equations": "", "symmetries_removed": "", "evidence": ""},
  "lane3_local_search": {"fit": "yes|no|unknown", "tight_or_loose": "", "evidence": ""},
  "already_reported": [{"url": "", "what": ""}],
  "cost_estimate": "",
  "recommend": "run|skip",
  "not_checked": ["list what you could not open or verify"]
}], "ranking": [ids, best first]}
```
