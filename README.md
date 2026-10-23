# FusionWiki

A shared, cross-model knowledge base of **measured** search experience,
populated by [InferArch](https://github.com/ShouyangDong/InferArch) during
execution-plan search and fusion evolution.

Search experience is written here whenever a candidate is measured: which
fusion boundaries, region assignments, provider and variant choices actually
made code faster — and by how much — on a given runtime environment. Entries
are keyed by *semantic signatures* (op kinds, dtypes, ranks, environment
fingerprint), never by model-specific node names, so a lesson learned on one
model transfers to the next.

## Trust rules

This repository stores **priors, not decisions**.

- Every suggestion read back from the wiki must be re-measured on the current
  model and pass InferArch's admission gates before it is used.
- Entries recorded under a different runtime-environment fingerprint (torch
  version, device, backend, ...) are excluded from derived lessons entirely.
  Stale experience never silently transfers.
- Writers only append. History is never rewritten in place; corrections are
  new entries, and curation happens by removing whole shard files.

## Layout

```text
entries/<yyyy-mm>/env-<hash8>/<lesson_key[:2]>/<lesson_key>.jsonl   # raw entries
lessons/                                                           # derived aggregates
tools/rebuild.py                                                   # regenerate lessons/
```

- `entries/` is the single source of truth: one append-only JSONL file per
  lesson bucket, month, and environment. Independent machines appending
  concurrently never touch the same file, so `git pull` stays conflict-free.
- `lessons/` is a derived, regenerable view for humans and tooling. Do not
  edit by hand; run `python tools/rebuild.py` after pulling.
- Lock and corruption-quarantine files (`*.lock`, `*.corrupt_*`) are never
  committed (see `.gitignore`).

See [schema.md](schema.md) for the entry format, the lesson-key computation,
and the experience domains.

## Using it with InferArch

In a source checkout of InferArch, this repository lives at
`3rdparty/FusionWiki` and is picked up automatically; no configuration is
needed. To point at another location (or a shared checkout across machines):

```python
from inferarch.deployment import InferArchLoopConfig

config = InferArchLoopConfig(fusion_wiki_path="/shared/FusionWiki")
```

A **directory** enables the sharded append-only store described above; a
plain file path uses the legacy single-JSON store.

## Contributing

Entries are machine-written by InferArch. To contribute:

1. Run InferArch on your model with the wiki enabled.
2. Commit the new `entries/` shards and push.

No manual entry editing, no secrets (environment fingerprints contain
versions, not keys), and no benchmark numbers that did not come from a
measured admission round.
