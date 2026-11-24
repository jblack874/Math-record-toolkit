#!/bin/sh
# Fetch Canli's checker (not ours; MIT terms per his repo) and build tilley_x.py with a --drop option.
git clone -q https://github.com/arhancanli/quantavane-replays qv && (cd qv && git checkout -q e53c299c6f56fe11adfd0d65b6e1305a276b4972)
cp qv/improvements/c49/tilley_a.py qv/improvements/c49/extras.json qv/c49/sunflower_check.py .
sed 's/^BL = B + \[m for m in EXL if m not in set(B)\]/DROP = set(load_list("--drop")); BL = [m for m in B + [m for m in EXL if m not in set(B)] if m not in DROP]/; s/^BR = B + \[m for m in EXR if m not in set(B)\]/BR = [m for m in B + [m for m in EXR if m not in set(B)] if m not in DROP]/' tilley_a.py > tilley_x.py
