#!/usr/bin/env python3
"""Checks doc<->schema consistency for the Gauge Entity Canon.

- canon/entities.schema.json must be valid JSON
- every known_deviations cg_id appears in canon/entities.md
- the deviation index in matrix/parity.md lists exactly the schema cg_ids
- checker warning counts in README.md and matrix/parity.md agree

Exit 0 = consistent, 1 = inconsistency found.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    schema_path = ROOT / "canon" / "entities.schema.json"
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {schema_path}: {exc}")
        return 1

    cg_ids = {d["cg_id"]
              for deviations in schema.get("known_deviations", {}).values()
              for d in deviations if "cg_id" in d}

    entities = (ROOT / "canon" / "entities.md").read_text(encoding="utf-8")
    parity = (ROOT / "matrix" / "parity.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    errors = []
    for cid in sorted(cg_ids):
        if cid not in entities:
            errors.append(f"cg_id {cid} missing in canon/entities.md")

    index_ids = set(re.findall(r"^\| (CG-[A-Z0-9]+) \|", parity, re.M))
    missing = cg_ids - index_ids
    unknown = index_ids - cg_ids
    if missing:
        errors.append(f"deviation index missing: {sorted(missing)}")
    if unknown:
        errors.append(f"deviation index lists unknown IDs: {sorted(unknown)}")

    counts = set()
    for text in (readme, parity):
        counts.update(re.findall(r"(\d+) registrierte Warnungen", text))
    if len(counts) > 1:
        errors.append(f"checker warning counts disagree: {sorted(counts)}")

    for err in errors:
        print(f"ERROR: {err}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
