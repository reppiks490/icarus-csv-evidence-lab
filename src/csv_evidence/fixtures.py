"""Small, explicitly synthetic edge cases for importer regression tests."""

from __future__ import annotations

import json
from pathlib import Path


CASES = {
    "clean_ohlc": ("time,open,high,low,close,volume\n2026-01-01T10:00:00Z,100.25,101,100,100.75,12\n", None),
    "quoted_comma": ('time,open,high,low,close,note\n"2026-01-01,10:00",100,101,99,100.5,"label,with,commas"\n', None),
    "duplicate_volume": ("time,open,high,low,close,Volume,Volume\n2026-01-01T10:00:00Z,100,101,99,100,4,5\n", "duplicate_header"),
    "ragged_row": ("time,open,high,low,close\n2026-01-01T10:00:00Z,100,101,99\n", "ragged_row"),
    "impossible_ohlc": ("time,open,high,low,close\n2026-01-01T10:00:00Z,100,99,101,100\n", "ohlc_inconsistent"),
    "nonfinite_price": ("time,open,high,low,close\n2026-01-01T10:00:00Z,100,NaN,99,100\n", "invalid_ohlc_number"),
    "semicolon": ("time;open;high;low;close\n2026-01-01T10:00:00Z;100;101;99;100\n", None),
    "bom": ("\ufefftime,open,high,low,close\n2026-01-01T10:00:00Z,100,101,99,100\n", None),
    "broken_quote": ('time,open,high,low,close\n"2026-01-01T10:00:00Z,100,101,99,100\n', "malformed_csv"),
}


def write_fixtures(output_dir: str | Path, *, overwrite: bool = False) -> Path:
    target = Path(output_dir).resolve()
    if target.is_dir() and any(target.iterdir()) and not overwrite:
        raise FileExistsError(f"fixture destination is not empty: {target}")
    target.mkdir(parents=True, exist_ok=True)
    manifest = []
    for name, (body, expected) in CASES.items():
        path = target / f"SYNTHETIC_{name}.csv"
        path.write_text(body, encoding="utf-8", newline="")
        manifest.append({
            "file": path.name,
            "synthetic": True,
            "market_evidence": False,
            "expected_finding": expected,
        })
    legacy = target / "SYNTHETIC_windows_1252.csv"
    legacy.write_bytes("time,open,high,low,close,note\n2026-01-01,100,101,99,100,caf\u00e9\n".encode("cp1252"))
    manifest.append({
        "file": legacy.name,
        "synthetic": True,
        "market_evidence": False,
        "expected_finding": "not_utf8",
    })
    manifest_path = target / "synthetic_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path
