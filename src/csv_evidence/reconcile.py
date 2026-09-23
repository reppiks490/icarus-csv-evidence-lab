"""Compare source inventories by raw content identity, never filename."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


def _read(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return data


def _hashes(members: list, field: str) -> tuple[Counter[str], dict[str, list[int]]]:
    counts: Counter[str] = Counter()
    rows: dict[str, list[int]] = {}
    for member in members:
        if not isinstance(member, dict):
            raise ValueError("manifest members must be objects")
        digest = member.get(field)
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest.lower()):
            raise ValueError(f"invalid {field} in manifest")
        digest = digest.lower()
        counts[digest] += 1
        row_count = member.get("data_rows" if field == "member_sha256" else "row_count")
        if isinstance(row_count, bool) or not isinstance(row_count, int) or row_count < 0:
            raise ValueError("invalid row count in manifest")
        rows.setdefault(digest, []).append(row_count)
    return counts, rows


def reconcile(aion_path: str | Path, nexus_path: str | Path) -> dict:
    """Return a privacy-minimal physical inventory delta, without promoting sources."""
    aion = _read(aion_path)
    nexus = _read(nexus_path)
    aion_members = aion.get("members")
    nexus_streams = nexus.get("streams")
    if not isinstance(aion_members, list) or not isinstance(nexus_streams, list):
        raise ValueError("expected AION members and NEXUS streams arrays")
    if any(not isinstance(member, dict) for member in aion_members + nexus_streams):
        raise ValueError("manifest members must be objects")
    parsed = [m for m in aion_members if m.get("status") == "parsed"]
    usable = []
    for stream in nexus_streams:
        identity = stream.get("identity")
        if not isinstance(identity, dict):
            raise ValueError("NEXUS stream has no identity")
        count = stream.get("row_count")
        flags = stream.get("quality_flags")
        if isinstance(count, bool) or not isinstance(count, int) or count < 0 or not isinstance(flags, list):
            raise ValueError("invalid NEXUS stream count or flags")
        if count and "appledouble" not in flags:
            usable.append({**stream, "_comparison_sha256": identity.get("raw_sha256")})
    left, left_rows = _hashes(parsed, "member_sha256")
    right, right_rows = _hashes(usable, "_comparison_sha256")
    aion_only = sorted(left.keys() - right.keys())
    nexus_only = sorted(right.keys() - left.keys())
    multiplicity = sorted(h for h in left.keys() & right.keys() if left[h] != right[h])
    row_differences = sorted(
        h for h in left.keys() & right.keys() if sorted(left_rows[h]) != sorted(right_rows[h])
    )
    inventory_equivalent = bool(parsed) and not (aion_only or nexus_only or multiplicity or row_differences)
    return {
        "schema_version": 1,
        "purpose": "hash_and_row_reconciliation_only_not_source_validation",
        "aion_entries": len(parsed),
        "nexus_entries": len(usable),
        "aion_distinct_hashes": len(left),
        "nexus_distinct_hashes": len(right),
        "common_hashes": len(left.keys() & right.keys()),
        "aion_only_hashes": aion_only,
        "nexus_only_hashes": nexus_only,
        "multiplicity_difference_hashes": multiplicity,
        "row_count_difference_hashes": row_differences,
        "row_count_note": "AION counts logical records; NEXUS may count only timestamp-parseable rows. Differences require member-level review.",
        "inventory_equivalent": inventory_equivalent,
        "coverage_claim_allowed": False,
        "coverage_note": "Matching inventories alone cannot establish full owner coverage, chart semantics, availability, or execution safety.",
    }
