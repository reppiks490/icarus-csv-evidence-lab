"""Read-only CSV triage with explicit limits on what can be inferred."""

from __future__ import annotations

import csv
import hashlib
import io
import tempfile
from collections import Counter
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable


def _snapshot(source: Path, target) -> tuple[str, int]:
    digest, size = hashlib.sha256(), 0
    with source.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            target.write(chunk)
            digest.update(chunk)
            size += len(chunk)
    target.flush()
    target.seek(0)
    return digest.hexdigest(), size


def _number(value: str) -> Decimal | None:
    try:
        parsed = Decimal(value.strip())
    except (InvalidOperation, AttributeError):
        return None
    return parsed if parsed.is_finite() else None


def _canonical(name: str) -> str:
    return " ".join(name.strip().casefold().split())


def _dialect(sample_bytes: bytes, delimiter: str | None) -> tuple[str, str]:
    if delimiter is not None:
        if delimiter not in (",", ";", "\t"):
            raise ValueError("delimiter must be comma, semicolon, or tab")
        return delimiter, "explicit"
    sample = sample_bytes.decode("utf-8-sig", errors="ignore")
    try:
        sniffed = csv.Sniffer().sniff(sample, delimiters=",;\t")
        return sniffed.delimiter, "inferred_unverified"
    except csv.Error:
        return ",", "fallback_unverified"


def _timestamp(raw: str) -> tuple[str, Decimal | datetime] | None:
    value = raw.strip()
    if not value:
        return None
    numeric = _number(value)
    if numeric is not None:
        return "numeric", numeric
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return ("aware" if parsed.tzinfo else "naive"), parsed


def audit_file(path: str | Path, *, delimiter: str | None = None, finding_limit: int = 25) -> dict:
    """Inspect structure only; never auto-repair, label, or approve a source."""
    source = Path(path).resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if finding_limit < 1:
        raise ValueError("finding_limit must be positive")

    findings: list[dict] = []
    finding_counts: Counter[str] = Counter()

    def note(code: str, severity: str, line: int | None = None) -> None:
        finding_counts[code] += 1
        if len(findings) < finding_limit:
            findings.append({"code": code, "severity": severity, "line": line})

    result = {
        "path": str(source),
        "size_bytes": None,
        "sha256": None,
        "rows": 0,
        "columns": 0,
        "header": [],
        "delimiter": None,
        "delimiter_basis": None,
        "structural_role": "unknown",
        "findings": findings,
        "finding_counts": {},
        "parse_complete": False,
        "provenance": {
            "provider": "unverified",
            "symbol_contract": "unverified",
            "chart_type": "unverified",
            "session_timezone_roll": "unverified",
            "available_at": "unverified",
            "license": "unverified",
        },
        "eligibility": "quarantined_pending_source_verification",
    }
    before = source.stat()
    with tempfile.TemporaryFile(mode="w+b") as snapshot:
        digest, size = _snapshot(source, snapshot)
        result["sha256"], result["size_bytes"] = digest, size
        try:
            snapshot.seek(0)
            sep, basis = _dialect(snapshot.read(65536), delimiter)
            result["delimiter"], result["delimiter_basis"] = sep, basis
            if basis != "explicit":
                note("delimiter_not_confirmed", "warning")
            snapshot.seek(0)
            stream = io.TextIOWrapper(snapshot, encoding="utf-8-sig", newline="")
            reader = csv.reader(stream, delimiter=sep, strict=True)
            try:
                header = next(reader)
            except StopIteration:
                note("empty_file", "error")
                result["finding_counts"] = dict(finding_counts)
                return result
            names = [_canonical(h) for h in header]
            result["header"] = header
            result["columns"] = len(header)
            if any(not name for name in names):
                note("empty_header", "error", reader.line_num)
            for name, count in Counter(names).items():
                if name and count > 1:
                    note("duplicate_header", "error", reader.line_num)
            if any(h != h.strip() for h in header):
                note("header_whitespace", "warning", reader.line_num)

            index = {name: i for i, name in enumerate(names)}
            ohlc = all(name in index for name in ("open", "high", "low", "close"))
            result["structural_role"] = "ohlc_like" if ohlc else "other_csv"
            volume_index = index.get("volume") if names.count("volume") == 1 else None
            time_columns = [index[name] for name in ("time", "timestamp", "datetime", "date", "ts") if name in index]
            if ohlc and len(time_columns) != 1:
                note("missing_or_ambiguous_timestamp_column", "error", reader.line_num)
            time_index = time_columns[0] if len(time_columns) == 1 else None
            previous_time: tuple[str, Decimal | datetime] | None = None
            for row in reader:
                result["rows"] += 1
                line = reader.line_num
                if len(row) != len(header):
                    note("ragged_row", "error", line)
                    continue
                if not ohlc:
                    continue
                if time_index is not None:
                    current_time = _timestamp(row[time_index])
                    if current_time is None:
                        note("invalid_timestamp", "error", line)
                    elif previous_time is not None:
                        if current_time[0] != previous_time[0]:
                            note("mixed_timestamp_semantics", "error", line)
                        elif current_time[1] == previous_time[1]:
                            note("duplicate_timestamp", "error", line)
                        elif current_time[1] < previous_time[1]:
                            note("timestamp_out_of_order", "error", line)
                    if current_time is not None:
                        previous_time = current_time
                prices = {name: _number(row[index[name]]) for name in ("open", "high", "low", "close")}
                if any(value is None for value in prices.values()):
                    note("invalid_ohlc_number", "error", line)
                    continue
                if prices["low"] > prices["high"] or not all(
                    prices["low"] <= prices[name] <= prices["high"] for name in ("open", "close")
                ):
                    note("ohlc_inconsistent", "error", line)
                if volume_index is not None:
                    volume = _number(row[volume_index])
                    if volume is None or volume < 0:
                        note("invalid_volume", "error", line)
            if result["rows"] == 0:
                note("no_data_rows", "error")
            result["parse_complete"] = True
        except UnicodeDecodeError:
            note("not_utf8", "error")
        except csv.Error:
            note("malformed_csv", "error")
        finally:
            # TextIOWrapper owns the underlying temporary file once constructed.
            if "stream" in locals():
                stream.detach()
    after = source.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        note("source_path_changed_during_audit", "warning")
    result["finding_counts"] = dict(finding_counts)
    return result


def audit_paths(paths: Iterable[str | Path], *, delimiter: str | None = None) -> dict:
    files: list[Path] = []
    for item in paths:
        path = Path(item).resolve()
        if path.is_file() and path.suffix.lower() == ".csv":
            files.append(path)
        elif path.is_dir():
            files.extend(path.rglob("*.csv"))
        else:
            raise FileNotFoundError(path)
    unique = sorted(set(files), key=lambda p: str(p).casefold())
    reports = [audit_file(path, delimiter=delimiter) for path in unique]
    by_hash: dict[str, list[str]] = {}
    for report in reports:
        by_hash.setdefault(report["sha256"], []).append(report["path"])
    duplicates = [members for members in by_hash.values() if len(members) > 1]
    return {
        "schema_version": 1,
        "purpose": "structure_and_identity_only_not_market_validation",
        "file_count": len(reports),
        "files": reports,
        "identical_content_groups": duplicates,
    }
