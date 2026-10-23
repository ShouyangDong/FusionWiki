#!/usr/bin/env python3
"""Regenerate the derived lessons/ view from the raw entries/ shards.

entries/ is the single source of truth; this script is the only writer of
lessons/. The read and derivation logic is imported from InferArch so this
repository never carries a second, drifting implementation:

    python tools/rebuild.py [--wiki /path/to/FusionWiki]

Requires an importable inferarch package (e.g. run from an InferArch source
checkout). Only the torch-free inferarch.planning.fusion_wiki module is used.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

WIKI_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--wiki", type=Path, default=WIKI_ROOT, help="FusionWiki repository root"
    )
    args = parser.parse_args()

    from inferarch.planning.fusion_wiki import derive_aggregates, read_sharded_entries

    entries = read_sharded_entries(args.wiki)
    print(f"read {len(entries)} entries from {args.wiki / 'entries'}")

    by_environment: dict[str, list[dict]] = {}
    for entry in entries:
        scope = json.dumps(entry.get("environment") or {}, sort_keys=True, default=str)
        by_environment.setdefault(scope, []).append(entry)

    for scope, scoped in by_environment.items():
        environment = json.loads(scope)
        aggregates = derive_aggregates(scoped, environment)
        written = 0
        for lesson_key, lesson in sorted(aggregates["lessons"].items()):
            path = args.wiki / "lessons" / "lessons" / f"{lesson_key.replace(':', '_')}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(lesson, indent=2, ensure_ascii=False) + "\n")
            written += 1
        for lesson_key, winners in sorted(aggregates["winning_boundaries"].items()):
            if not winners:
                continue
            path = args.wiki / "lessons" / "winning_boundaries" / f"{lesson_key.replace(':', '_')}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(winners, indent=2, ensure_ascii=False) + "\n")
            written += 1
        print(f"environment {scope}: wrote {written} aggregate files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
