# Cross-System Evidence Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a reproducible, privacy-minimal inventory and fail-closed evidence contract for the ICARUS program without granting training, paper, or broker authority.

**Architecture:** Extend the existing independent evidence lab. Read-only scanners emit normalized source records; a separate provenance evaluator records only demonstrated states; a requirement ledger links user requests to exact source and verification records. Reports are deterministic snapshots written atomically outside the committed raw-data boundary. Existing ICARUS, NEXUS, AION/PARALLAX, DAEDALUS, ORACLE, ATHENA, ARGUS, and AEGIS implementations remain separate.

**Tech Stack:** Python >=3.10 standard library, `unittest`, PowerShell on Windows, Git. No new runtime dependency.

**Spec:** `docs/superpowers/specs/2026-09-23-cross-system-evidence-contract-design.md`

## Global Constraints

- Source repositories and the paper engine are read-only inputs to this subproject; preserve all dirty files.
- No Pulse rewrite, order change, candidate swap, broker connection, or execution permission.
- All research/shadow decisions remain blocked until independently verified source timing, protected holdouts, and real-fill parity.
- Raw owner CSV/XLSX/ZIP data and credentials remain outside Git; commit only minimal hashes, locators, counts, and verification findings.
- Keep chart representation, event time, first-known availability, revision, and executable-price status separate.
- Do not infer authenticated order flow from candles or market identity from filenames.
- A green unit suite or handoff manifest is evidence of only the checks it actually covers.

## Review Focus

1. Duplicate ZIP member names: preserve each central-directory ordinal and hash its own bytes, rather than reopening the first matching name. Task 2 pins this.
2. Untrusted source text or remote URLs containing secrets: reject arbitrary fields and strip URL credentials/query/fragment before a report is written. Tasks 1 and 3 pin this.
3. A revised macro/market row with only its historical event time: fail closed until its first authenticated release is known. Task 4 pins this.
4. A scan that fails midway or a source that disappears: record a bounded failure, never silently omit the locator or leave a torn report. Tasks 2, 3, and 6 pin this.
5. Contradictory or absent sibling handoff claims: preserve each claim and mark it unverified rather than treating the newest ZIP or green count as deployed. Task 5 pins this.

## File Map

| File | Responsibility |
| --- | --- |
| `src/csv_evidence/contracts.py` | Strict, minimal source/requirement/verification record schemas and deterministic IDs |
| `src/csv_evidence/archive_inventory.py` | Bounded, read-only ZIP-member identities and CSV logical-row counts |
| `src/csv_evidence/local_inventory.py` | Read-only Git checkout and Claude JSONL metadata; sanitized ChatGPT index intake |
| `src/csv_evidence/provenance.py` | Fail-closed state assessment, with no research or execution promotion |
| `src/csv_evidence/ledger.py` | Requirement coverage and source-claim reconciliation |
| `src/csv_evidence/reporting.py` | Atomic, canonical, privacy-minimal report writes |
| `src/csv_evidence/cli.py` | Add inventory, assess, and ledger commands to existing CLI |
| `tests/test_contracts.py` | Schema and secret-bearing extra-field rejection |
| `tests/test_archive_inventory.py` | Duplicate ZIP names, corruption, and resource budgets |
| `tests/test_local_inventory.py` | Git URL sanitization, dirty state, JSONL gaps |
| `tests/test_provenance.py` | Timing, representation, revision, and structural fail-closed rules |
| `tests/test_ledger.py` | Requirement coverage, conflicting claims, absent packages |
| `tests/test_reporting.py` | Deterministic output, atomic failure, end-to-end read-only behavior |
| `docs/PROGRAM_REQUIREMENTS.json` | Explicit named-system and capability matrix, no invented completion |
| `docs/PROGRAM_BASELINES.md` | Reproduced test commands/results with revision and dirty-tree context |
| `docs/PROGRAM_INVENTORY.md` | Sanitized source locator map and access gaps, not raw data |

All Python interfaces below are project-relative under `C:\Users\tripl\icarus-csv-evidence-lab`. Use `$env:PYTHONPATH=(Resolve-Path .\src).Path` before the listed test commands. Preserve the existing `audit.py`, `reconcile.py`, and their 15 passing tests.

---

### Task 1: Strict Evidence Records

**Files:**
- Create: `src/csv_evidence/contracts.py`
- Test: `tests/test_contracts.py`

**Interfaces:**
- Produces: `checked_source(raw: dict) -> dict`, `checked_requirement(raw: dict) -> dict`, `stable_id(kind: str, locator: str, digest: str | None) -> str`, `byte_identity(kind: str, digest: str) -> str`.
- Later tasks provide only allowlisted scalar facts; arbitrary payloads, transcript text, and credential fields never enter records.

- [ ] **Step 1: Write the failing tests**

```python
import unittest
from csv_evidence.contracts import checked_source, checked_requirement, stable_id, byte_identity

class ContractTests(unittest.TestCase):
    def test_source_rejects_secret_bearing_extra_key(self):
        source = {"kind":"zip", "locator":"C:/intake/a.zip", "digest":"a"*64,
                  "access":"observed", "facts":{"members":2}, "api_key":"secret"}
        with self.assertRaises(ValueError): checked_source(source)

    def test_requirement_requires_next_action_even_when_missing(self):
        with self.assertRaises(ValueError):
            checked_requirement({"id":"REQ-001", "system":"NEXUS", "statement":"Verify timing",
                                 "sources":[], "artifacts":[], "verification":"missing"})

    def test_stable_id_distinguishes_same_name_different_bytes(self):
        self.assertNotEqual(stable_id("zip_member", "a.zip#3:x.csv", "a"*64),
                            stable_id("zip_member", "a.zip#3:x.csv", "b"*64))

    def test_byte_identity_collapses_copies_but_not_locations(self):
        self.assertEqual(byte_identity("zip", "a"*64), byte_identity("zip", "a"*64))
        self.assertNotEqual(stable_id("zip", "C:/one.zip", "a"*64),
                            stable_id("zip", "C:/two.zip", "a"*64))
```

- [ ] **Step 2: Run the test and confirm import failure**

```powershell
py -3 -m unittest tests.test_contracts -v
```

Expected: `ModuleNotFoundError: No module named 'csv_evidence.contracts'`.

- [ ] **Step 3: Implement exact-key validation and canonical IDs**

```python
import hashlib
import json
import re
from urllib.parse import urlsplit

SOURCE_KEYS = {"kind", "locator", "digest", "access", "facts"}
REQUIREMENT_KEYS = {"id", "system", "statement", "sources", "artifacts", "verification", "next_action"}
KINDS = {"chat", "git", "local_tree", "zip", "zip_member", "csv", "handoff"}
FACT_KEYS = {
    "chat": {"thread_id", "turn_id", "timestamp", "session_id", "content_digest", "gap"},
    "git": {"branch", "commit", "dirty", "status_digest", "remote", "test_command", "test_result"},
    "local_tree": {"file_count", "status_digest"},
    "zip": {"members", "size_bytes", "error"},
    "zip_member": {"archive_id", "ordinal", "name", "size_bytes", "logical_rows",
                   "header_count", "duplicate_header_positions", "error"},
    "csv": {"rows", "columns", "role", "error"},
    "handoff": {"bundle_ref", "claim", "test_command", "test_result", "gap"},
}

def stable_id(kind: str, locator: str, digest: str | None) -> str:
    payload = json.dumps([kind, locator, digest], separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def byte_identity(kind: str, digest: str) -> str:
    return hashlib.sha256(f"{kind}:{digest}".encode("ascii")).hexdigest()

def checked_source(raw: dict) -> dict:
    if not isinstance(raw, dict) or set(raw) != SOURCE_KEYS or raw["kind"] not in KINDS:
        raise ValueError("invalid source record keys or kind")
    if not isinstance(raw["locator"], str) or not raw["locator"]:
        raise ValueError("source locator required")
    if len(raw["locator"]) > 1024:
        raise ValueError("source locator too long")
    if "://" in raw["locator"]:
        parts = urlsplit(raw["locator"])
        if parts.username or parts.password or parts.query or parts.fragment:
            raise ValueError("source locator contains URL credentials or query")
    if raw["digest"] is not None and not re.fullmatch(r"[0-9a-f]{64}", raw["digest"]):
        raise ValueError("invalid source digest")
    if raw["access"] not in {"observed", "unavailable", "failed"}:
        raise ValueError("invalid access state")
    facts = raw["facts"]
    if not isinstance(facts, dict) or set(facts) - FACT_KEYS[raw["kind"]]:
        raise ValueError("unapproved source facts")
    if any(not isinstance(v, (str, int, bool, type(None))) for v in facts.values()):
        raise ValueError("source facts must be scalars")
    if any(isinstance(v, str) and len(v) > 1024 for v in facts.values()):
        raise ValueError("source fact too long")
    return {**raw, "id": stable_id(raw["kind"], raw["locator"], raw["digest"])}

def checked_requirement(raw: dict) -> dict:
    if not isinstance(raw, dict) or set(raw) != REQUIREMENT_KEYS:
        raise ValueError("invalid requirement keys")
    if not re.fullmatch(r"REQ-[0-9]{3}", raw["id"]):
        raise ValueError("invalid requirement id")
    if not all(isinstance(raw[k], str) and raw[k] for k in ("system", "statement", "verification", "next_action")):
        raise ValueError("requirement text missing")
    if not all(isinstance(raw[k], list) and all(isinstance(x, str) for x in raw[k]) for k in ("sources", "artifacts")):
        raise ValueError("requirement references must be string lists")
    return raw
```

Add a test with `https://user:token@github.com/o/r?key=secret` in `locator` and assert rejection. Do not accept transcript or CSV content in `facts`; keep schema additions deliberate and versioned.

- [ ] **Step 4: Run focused and existing tests**

```powershell
py -3 -m unittest tests.test_contracts -v
py -3 -m unittest discover -s tests -v
```

Expected: new tests and all 15 existing tests pass.

- [ ] **Step 5: Commit this independently reviewable contract**

```powershell
git add src/csv_evidence/contracts.py tests/test_contracts.py
git commit -m "feat: add strict evidence record contracts"
```

### Task 2: Bounded Archive and Member Inventory

**Files:**
- Create: `src/csv_evidence/archive_inventory.py`
- Test: `tests/test_archive_inventory.py`

**Interfaces:**
- Consumes: `checked_source` and `stable_id` from Task 1.
- Produces: `scan_zip(path: Path, budget: ScanBudget) -> list[dict]`; first record is archive identity, following records are member identities or explicit failures.

- [ ] **Step 1: Write failing duplicate-name and budget tests**

```python
import tempfile, unittest, warnings, zipfile
from pathlib import Path
from csv_evidence.archive_inventory import ScanBudget, scan_zip

class ArchiveTests(unittest.TestCase):
    def test_duplicate_member_names_remain_distinct(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"a.zip"
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                with zipfile.ZipFile(p, "w") as z:
                    z.writestr("same.csv", "a,b\n1,2\n")
                    z.writestr("same.csv", "a,b\n3,4\n")
            records = [x for x in scan_zip(p, ScanBudget()) if x["kind"] == "zip_member"]
            self.assertEqual([x["facts"]["ordinal"] for x in records], [0, 1])
            self.assertNotEqual(records[0]["digest"], records[1]["digest"])

    def test_member_over_budget_is_a_recorded_failure(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"big.zip"
            with zipfile.ZipFile(p, "w") as z: z.writestr("x.csv", "a\n" + "1\n"*20)
            records = scan_zip(p, ScanBudget(max_member_bytes=8))
            self.assertEqual(records[1]["access"], "failed")
            self.assertEqual(records[1]["facts"]["error"], "member_size_limit")

    def test_duplicate_header_positions_are_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"header.zip"
            with zipfile.ZipFile(p,"w") as z: z.writestr("x.csv","time,close,close\n1,2,3\n")
            member=scan_zip(p,ScanBudget())[1]
            self.assertEqual(member["facts"]["header_count"],3)
            self.assertEqual(member["facts"]["duplicate_header_positions"],"2")
```

- [ ] **Step 2: Run the test and confirm import failure**

```powershell
py -3 -m unittest tests.test_archive_inventory -v
```

Expected: missing `archive_inventory` module.

- [ ] **Step 3: Implement streaming hashes and logical CSV counts**

```python
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from zipfile import ZipFile, BadZipFile
import csv, hashlib, io
from .contracts import checked_source

@dataclass(frozen=True)
class ScanBudget:
    max_archive_bytes: int = 8 << 30
    max_member_bytes: int = 2 << 30
    max_total_uncompressed: int = 32 << 30
    max_members: int = 100_000
    max_ratio: int = 1_000
    max_rows_per_member: int = 20_000_000

def _digest(stream, limit: int) -> str:
    h = hashlib.sha256(); size = 0
    for chunk in iter(lambda: stream.read(1 << 20), b""):
        size += len(chunk)
        if size > limit: raise ValueError("member_size_limit")
        h.update(chunk)
    return h.hexdigest()

def _logical_rows(z: ZipFile, info, budget: ScanBudget) -> tuple[int,int,str]:
    with z.open(info) as raw:
        with io.TextIOWrapper(raw, encoding="utf-8-sig", newline="") as text:
            reader = csv.reader(text, strict=True)
            header=next(reader, [])
            seen=set(); duplicates=[]
            for position,name in enumerate(header):
                canonical=" ".join(name.strip().casefold().split())
                if canonical in seen: duplicates.append(position)
                seen.add(canonical)
            count = 0
            for _ in reader:
                count += 1
                if count > budget.max_rows_per_member: raise ValueError("row_limit")
            return count,len(header),",".join(map(str,duplicates))

def _failed_archive(path: Path, digest: str | None, error: str) -> list[dict]:
    return [checked_source({"kind":"zip", "locator":str(path), "digest":digest,
                            "access":"failed", "facts":{"error":error}})]

def scan_zip(path: Path, budget: ScanBudget = ScanBudget()) -> list[dict]:
    path = path.resolve()
    try:
        with path.open("rb") as source:
            archive_hash = _digest(source, budget.max_archive_bytes)
    except (OSError, ValueError) as exc:
        return _failed_archive(path, None, type(exc).__name__)
    records = [checked_source({"kind":"zip", "locator":str(path), "digest":archive_hash,
                               "access":"observed", "facts":{"size_bytes":path.stat().st_size}})]
    try:
      with ZipFile(path) as z:
        infos = z.infolist()
        if len(infos) > budget.max_members:
            return _failed_archive(path, archive_hash, "member_count_limit")
        total = 0
        for ordinal, info in enumerate(infos):
            if info.is_dir(): continue
            total += info.file_size
            locator = f"{path}#{ordinal}:{info.filename}"
            error = None
            parts = PurePosixPath(info.filename)
            if parts.is_absolute() or ".." in parts.parts or "\\" in info.filename:
                error = "unsafe_member_name"
            elif info.filename.lower().endswith(".zip"):
                error = "nested_archive_not_scanned"
            if info.file_size > budget.max_member_bytes or total > budget.max_total_uncompressed:
                error = "member_size_limit"
            elif info.file_size > budget.max_ratio * max(info.compress_size, 1):
                error = "compression_ratio_limit"
            elif info.flag_bits & 1:
                error = "encrypted_member"
            rows=header_count=duplicate_positions=None
            try:
                if error:
                    digest = None
                else:
                    with z.open(info) as member:
                        digest = _digest(member, budget.max_member_bytes)
                    if info.filename.lower().endswith(".csv"):
                        rows,header_count,duplicate_positions = _logical_rows(z, info, budget)
            except (BadZipFile, ValueError, OSError, UnicodeDecodeError, csv.Error) as exc:
                digest, error = None, type(exc).__name__
            facts = {"archive_id":records[0]["id"], "ordinal":ordinal, "name":info.filename,
                     "size_bytes":info.file_size, "logical_rows":None if error else rows,
                     "header_count":None if error else header_count,
                     "duplicate_header_positions":None if error else duplicate_positions,
                     "error":error}
            records.append(checked_source({"kind":"zip_member", "locator":locator,
                                          "digest":digest, "access":"failed" if error else "observed",
                                          "facts":facts}))
    except (BadZipFile, OSError) as exc:
        return _failed_archive(path, archive_hash, type(exc).__name__)
    return records
```

Add tests with `b"not-a-zip"` (failed archive locator survives), a quoted newline CSV (one logical row), `../unsafe.csv` (failed member), and `inner.zip` (recorded without recursion). Confirm a failure does not affect a subsequent valid scan. The implementation never extracts members or stores row values.

- [ ] **Step 4: Run focused tests and the full suite**

```powershell
py -3 -m unittest tests.test_archive_inventory -v
py -3 -m unittest discover -s tests -v
```

Expected: duplicate names stay distinct; no source file is modified; all tests pass.

- [ ] **Step 5: Commit**

```powershell
git add src/csv_evidence/archive_inventory.py tests/test_archive_inventory.py
git commit -m "feat: inventory archive members with bounded reads"
```

### Task 3: Repository and Chat Locator Inventory

**Files:**
- Create: `src/csv_evidence/local_inventory.py`
- Test: `tests/test_local_inventory.py`

**Interfaces:**
- Consumes: `checked_source` from Task 1.
- Produces: `scan_git(path: Path) -> dict`, `scan_claude_jsonl(path: Path, *, max_line_bytes: int = 8 << 20) -> list[dict]`, `check_chat_index(rows: list[dict]) -> list[dict]`.

- [ ] **Step 1: Write failing read-only and sanitization tests**

```python
import json, subprocess, tempfile, unittest
from pathlib import Path
from csv_evidence.local_inventory import scan_git, scan_claude_jsonl, check_chat_index

class LocalInventoryTests(unittest.TestCase):
    def test_git_does_not_expose_remote_credentials(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); subprocess.run(["git","init",str(p)], check=True, capture_output=True)
            subprocess.run(["git","-C",str(p),"-c","user.name=Test","-c","user.email=t@example.test",
                            "commit","--allow-empty","-m","seed"], check=True, capture_output=True)
            subprocess.run(["git","-C",str(p),"remote","add","origin",
                            "https://user:token@github.com/owner/repo?auth=secret"], check=True)
            row = scan_git(p)
            self.assertNotIn("token", json.dumps(row))
            self.assertNotIn("secret", json.dumps(row))

    def test_claude_event_hashes_without_transcript_text(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"session.jsonl"
            p.write_text(json.dumps({"type":"user","uuid":"u1","timestamp":"2026-09-23T10:00:00Z",
                                     "sessionId":"s1","message":{"content":"PRIVATE"}})+"\n", encoding="utf-8")
            row = scan_claude_jsonl(p)[0]
            self.assertEqual(row["facts"]["turn_id"], "u1")
            self.assertNotIn("PRIVATE", json.dumps(row))

    def test_chatgpt_missing_turn_is_an_explicit_gap(self):
        rows = check_chat_index([{"thread_id":"c1","turn_id":None,"timestamp":None,"content_digest":None}])
        self.assertEqual(rows[0]["access"], "unavailable")
```

- [ ] **Step 2: Run the test and confirm import failure**

```powershell
py -3 -m unittest tests.test_local_inventory -v
```

Expected: missing `local_inventory` module.

- [ ] **Step 3: Implement bounded metadata intake**

```python
import hashlib, json, subprocess
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from .contracts import checked_source

def _git(path: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(path), *args], check=True,
                          capture_output=True, text=True, timeout=15).stdout.strip()

def _safe_remote(raw: str) -> str:
    if raw.startswith("git@github.com:"):
        return "https://github.com/" + raw.split(":", 1)[1]
    p = urlsplit(raw)
    return urlunsplit((p.scheme, p.hostname or "", p.path, "", ""))

def scan_git(path: Path) -> dict:
    path = path.resolve()
    commit = _git(path, "rev-parse", "HEAD")
    branch = _git(path, "branch", "--show-current")
    status = _git(path, "status", "--porcelain=v1", "-z")
    try: remote = _safe_remote(_git(path, "remote", "get-url", "origin"))
    except subprocess.CalledProcessError: remote = ""
    digest=hashlib.sha256(commit.encode("ascii")).hexdigest()
    return checked_source({"kind":"git", "locator":str(path), "digest":digest,
                           "access":"observed", "facts":{"branch":branch,"commit":commit,
                           "dirty":bool(status),"status_digest":hashlib.sha256(status.encode()).hexdigest(),
                           "remote":remote}})

def scan_claude_jsonl(path: Path, *, max_line_bytes: int = 8 << 20) -> list[dict]:
    rows = []
    with path.open("rb") as source:
        for ordinal, line in enumerate(source):
            digest = hashlib.sha256(line).hexdigest()
            locator = f"{path.resolve()}#{ordinal}"
            try:
                if len(line) > max_line_bytes: raise ValueError("line_size_limit")
                item = json.loads(line)
                facts = {"thread_id":item.get("sessionId"), "turn_id":item.get("uuid"),
                         "timestamp":item.get("timestamp"), "content_digest":digest}
                access = "observed"
            except (ValueError, UnicodeDecodeError):
                facts, access = {"content_digest":digest, "gap":"invalid_or_oversize_jsonl"}, "failed"
            rows.append(checked_source({"kind":"chat", "locator":locator,"digest":digest,
                                        "access":access,"facts":facts}))
    return rows

def check_chat_index(rows: list[dict]) -> list[dict]:
    normalized = []
    for row in rows:
        if set(row) != {"thread_id", "turn_id", "timestamp", "content_digest"}:
            raise ValueError("chat index must contain IDs, timestamp, and digest only")
        thread_id = row["thread_id"]
        if not isinstance(thread_id, str) or not thread_id:
            raise ValueError("chat thread id required")
        turn_id = row["turn_id"]
        access = "observed" if turn_id and row["content_digest"] else "unavailable"
        normalized.append(checked_source({
            "kind":"chat", "locator":f"chatgpt://{thread_id}/{turn_id or 'missing-turn'}",
            "digest":row["content_digest"], "access":access,
            "facts":{"thread_id":thread_id, "turn_id":turn_id,
                     "timestamp":row["timestamp"], "content_digest":row["content_digest"],
                     "gap":None if access == "observed" else "turn_or_digest_missing"}}))
    return normalized
```

Treat titles, summaries, and chat messages as untrusted data and do not commit them. Empty `uuid`/timestamp in Claude metadata events are valid recorded gaps, not fabricated turn IDs. Add tests for malformed JSONL and a Git worktree with no remote; its sanitized remote field is empty, not invented.

- [ ] **Step 4: Run focused and full tests**

```powershell
py -3 -m unittest tests.test_local_inventory -v
py -3 -m unittest discover -s tests -v
```

Expected: no transcript text or URL credential in normalized records; all tests pass.

- [ ] **Step 5: Commit**

```powershell
git add src/csv_evidence/local_inventory.py tests/test_local_inventory.py
git commit -m "feat: inventory git and chat metadata without content leakage"
```

### Task 4: Fail-Closed Provenance Assessment

**Files:**
- Create: `src/csv_evidence/provenance.py`
- Test: `tests/test_provenance.py`
- Modify: `docs/PROVENANCE_CONTRACT.md`

**Interfaces:**
- Consumes: `audit_file`'s findings and a source record tied to the same SHA-256.
- Produces: `assess_source(scan: dict, source: dict, attestations: list[dict], *, reviewed_evidence: set[str] | None = None) -> dict` with `state`, `reasons`, `execution_authorized=False`. The reviewed hash set is an explicit, separate human-review input; the lab never produces `research_eligible` or `execution_eligible`.

- [ ] **Step 1: Write failing timing and representation tests**

```python
import unittest
from csv_evidence.provenance import assess_source, resolve_local_time

SCAN = {"sha256":"a"*64, "parse_complete":True, "finding_counts":{}}
SOURCE = {"digest":"a"*64}
IDENTITY = {"kind":"identity", "source_sha256":"a"*64, "reviewer":"owner",
            "evidence_sha256":"b"*64, "provider":"TradingView", "symbol":"NQ1!",
            "representation":"heikin_ashi", "session":"RTH", "timezone":"America/Chicago",
            "bar_stamp":"open", "roll_rule":"volume", "license":"private_research"}

class ProvenanceTests(unittest.TestCase):
    def test_unknown_availability_never_promotes(self):
        result = assess_source(SCAN, SOURCE, [IDENTITY], reviewed_evidence={"b"*64})
        self.assertEqual(result["state"], "identity_verified")
        self.assertFalse(result["execution_authorized"])

    def test_unreviewed_identity_claim_cannot_certify_itself(self):
        result = assess_source(SCAN, SOURCE, [IDENTITY])
        self.assertEqual(result["state"], "structurally_checked")
        self.assertIn("identity_evidence_unreviewed", result["reasons"])

    def test_revised_row_without_first_release_fails_closed(self):
        result = assess_source(SCAN, SOURCE, [IDENTITY,
            {"kind":"availability", "source_sha256":"a"*64, "reviewer":"data_auditor",
             "evidence_sha256":"c"*64, "event_ns":100, "revision":2}],
            reviewed_evidence={"b"*64, "c"*64})
        self.assertEqual(result["state"], "identity_verified")
        self.assertIn("first_release_missing", result["reasons"])

    def test_malformed_ohlc_cannot_promote(self):
        bad = {**SCAN, "finding_counts":{"ohlc_inconsistent":1}}
        self.assertEqual(assess_source(bad, SOURCE, [IDENTITY])["state"], "quarantined")

    def test_mixed_chart_mode_cannot_be_identity_verified(self):
        mixed = {**IDENTITY, "representation":"mixed"}
        self.assertEqual(assess_source(SCAN, SOURCE, [mixed],
                         reviewed_evidence={"b"*64})["state"], "structurally_checked")

    def test_dst_fall_back_requires_offset_or_fold(self):
        with self.assertRaises(ValueError):
            resolve_local_time("2026-11-01T01:30:00", "America/New_York")
```

- [ ] **Step 2: Run test and confirm import failure**

```powershell
py -3 -m unittest tests.test_provenance -v
```

Expected: missing `provenance` module.

- [ ] **Step 3: Implement explicit state progression**

```python
STATES = ("quarantined", "structurally_checked", "identity_verified",
          "point_in_time_verified", "research_eligible")
IDENTITY_FIELDS = ("provider", "symbol", "representation", "session", "timezone",
                   "bar_stamp", "roll_rule", "license")
REPRESENTATIONS = {"standard_ohlc", "heikin_ashi", "renko", "footprint", "tpo", "session_profile"}

def _valid_zone(value: str) -> bool:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
    try:
        ZoneInfo(value)
        return True
    except (ZoneInfoNotFoundError, TypeError, ValueError):
        return False

def resolve_local_time(value: str, timezone: str, fold: int | None = None):
    from datetime import datetime
    from zoneinfo import ZoneInfo
    local = datetime.fromisoformat(value)
    zone = ZoneInfo(timezone)
    if local.tzinfo is not None:
        return local.astimezone(zone)
    a = local.replace(tzinfo=zone, fold=0)
    b = local.replace(tzinfo=zone, fold=1)
    if a.utcoffset() != b.utcoffset() and fold is None:
        raise ValueError("ambiguous local timestamp requires fold or offset")
    return local.replace(tzinfo=zone, fold=fold or 0)

def assess_source(scan: dict, source: dict, attestations: list[dict], *,
                  reviewed_evidence: set[str] | None = None) -> dict:
    reasons = []
    reviewed_evidence = reviewed_evidence or set()
    if scan.get("sha256") != source.get("digest") or not scan.get("parse_complete") or scan.get("finding_counts"):
        return {"state":"quarantined", "reasons":["structural_or_digest_failure"],
                "execution_authorized":False}
    state = "structurally_checked"
    identity = next((a for a in attestations if a.get("kind") == "identity"), None)
    if identity is None or identity.get("source_sha256") != source["digest"]:
        reasons.append("identity_missing")
    elif any(not identity.get(k) or identity[k] == "unknown" for k in IDENTITY_FIELDS):
        reasons.append("identity_incomplete")
    elif identity["representation"] not in REPRESENTATIONS:
        reasons.append("representation_unreviewed")
    elif not _valid_zone(identity["timezone"]):
        reasons.append("timezone_unverified")
    elif not identity.get("reviewer") or not identity.get("evidence_sha256"):
        reasons.append("identity_evidence_missing")
    elif identity["evidence_sha256"] not in reviewed_evidence:
        reasons.append("identity_evidence_unreviewed")
    else:
        state = "identity_verified"
        release = next((a for a in attestations if a.get("kind") == "availability"
                        and a.get("source_sha256") == source["digest"]), None)
        if release is None or release.get("first_release_ns") is None:
            reasons.append("first_release_missing")
        elif isinstance(release["first_release_ns"], bool) or not isinstance(release["first_release_ns"], int):
            reasons.append("first_release_invalid")
        elif isinstance(release.get("event_ns"), bool) or not isinstance(release.get("event_ns"), int):
            reasons.append("event_time_invalid")
        elif release["first_release_ns"] < release.get("event_ns", 0):
            reasons.append("release_before_event")
        elif release.get("revision", 0) and release.get("first_release_basis") not in {"publisher_log", "observed_receipt"}:
            reasons.append("revision_release_basis_missing")
        elif not release.get("reviewer") or not release.get("evidence_sha256"):
            reasons.append("availability_evidence_missing")
        elif release["evidence_sha256"] not in reviewed_evidence:
            reasons.append("availability_evidence_unreviewed")
        else:
            state = "point_in_time_verified"
    return {"state":state, "reasons":reasons, "execution_authorized":False}
```

Add a test with `revision=2`, `first_release_ns=120`, and no `first_release_basis`; expect `identity_verified` with `revision_release_basis_missing`. A mixed HA/standard file is represented as `mixed`, which is not in `REPRESENTATIONS`; a continuous contract with unknown roll is rejected by `identity_incomplete`. Document that the externally reviewed hash set records a human review, not a cryptographic signature or training approval; the default empty set never promotes a claim.

- [ ] **Step 4: Run tests**

```powershell
py -3 -m unittest tests.test_provenance -v
py -3 -m unittest discover -s tests -v
```

Expected: no malformed source or unknown availability reaches `point_in_time_verified`; all tests pass.

- [ ] **Step 5: Commit**

```powershell
git add src/csv_evidence/provenance.py tests/test_provenance.py docs/PROVENANCE_CONTRACT.md
git commit -m "feat: assess source provenance without granting authority"
```

### Task 5: Requirement Ledger and Conflicting Claims

**Files:**
- Create: `src/csv_evidence/ledger.py`
- Create: `docs/PROGRAM_REQUIREMENTS.json`
- Test: `tests/test_ledger.py`

**Interfaces:**
- Consumes: `checked_source`, `checked_requirement` from Task 1.
- Produces: `build_ledger(sources: list[dict], requirements: list[dict], *, reviewed_artifacts: set[str] | None = None) -> dict` with deterministic linked records and explicit missing references. A requirement cannot certify itself by setting `verification` text.

- [ ] **Step 1: Write failing completeness and contradiction tests**

```python
import unittest
from csv_evidence.ledger import build_ledger, REQUIRED_SYSTEMS

class LedgerTests(unittest.TestCase):
    def test_all_named_systems_are_required(self):
        self.assertEqual(REQUIRED_SYSTEMS,
            {"ICARUS","NEXUS","AION/PARALLAX","DAEDALUS","ARGUS","ATHENA","ORACLE","AEGIS"})

    def test_two_conflicting_claims_are_not_collapsed(self):
        sources = [
            {"id":"a"*64, "kind":"handoff", "locator":"zip#a", "digest":"a"*64,
             "access":"observed", "facts":{"claim":"117 passed"}},
            {"id":"b"*64, "kind":"handoff", "locator":"worktree#b", "digest":"b"*64,
             "access":"observed", "facts":{"claim":"115 passed, 2 failed"}}]
        req = [{"id":"REQ-001", "system":"NEXUS", "statement":"Verify strict replay",
                "sources":["a"*64,"b"*64], "artifacts":[], "verification":"conflicting",
                "next_action":"reproduce against a clean commit and resolve two tests"}]
        result = build_ledger(sources, req)
        self.assertEqual(len(result["requirements"][0]["claims"]), 2)
        self.assertFalse(result["requirements"][0]["verified"])

    def test_missing_package_is_reported(self):
        req = [{"id":"REQ-002", "system":"ARGUS", "statement":"Verify implementation",
                "sources":["a"*64], "artifacts":[], "verification":"missing",
                "next_action":"obtain source package"}]
        self.assertEqual(build_ledger([], req)["missing_source_ids"], ["a"*64])

    def test_same_zip_bytes_have_one_byte_identity_and_two_locators(self):
        from csv_evidence.contracts import checked_source
        a=checked_source({"kind":"zip","locator":"C:/one.zip","digest":"a"*64,
                          "access":"observed","facts":{"members":1}})
        b=checked_source({"kind":"zip","locator":"C:/two.zip","digest":"a"*64,
                          "access":"observed","facts":{"members":1}})
        groups=build_ledger([a,b],[])["byte_groups"]
        self.assertEqual(len(groups),1)
        self.assertEqual(len(next(iter(groups.values()))),2)

    def test_committed_matrix_has_all_program_items(self):
        import json
        from pathlib import Path
        p=Path(__file__).resolve().parents[1]/"docs/PROGRAM_REQUIREMENTS.json"
        rows=json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual({r["id"] for r in rows}, {f"REQ-{i:03d}" for i in range(1,26)})
        self.assertTrue(all(r["sources"] for r in rows))
        self.assertTrue(all(r["next_action"] for r in rows))
```

- [ ] **Step 2: Run test and confirm import failure**

```powershell
py -3 -m unittest tests.test_ledger -v
```

Expected: missing `ledger` module.

- [ ] **Step 3: Implement deterministic linking and the full requirement matrix**

```python
REQUIRED_SYSTEMS = {"ICARUS","NEXUS","AION/PARALLAX","DAEDALUS",
                    "ARGUS","ATHENA","ORACLE","AEGIS"}
from .contracts import byte_identity

def build_ledger(sources: list[dict], requirements: list[dict], *,
                 reviewed_artifacts: set[str] | None = None) -> dict:
    reviewed_artifacts = reviewed_artifacts or set()
    by_id = {s["id"]: s for s in sources}
    if len(by_id) != len(sources): raise ValueError("duplicate source id")
    if len({r["id"] for r in requirements}) != len(requirements):
        raise ValueError("duplicate requirement id")
    missing = sorted({sid for r in requirements for sid in r["sources"] if sid not in by_id})
    groups = {}
    for source in sources:
        if source["digest"] is not None:
            key=byte_identity(source["kind"],source["digest"])
            groups.setdefault(key,[]).append(source["locator"])
    groups={key:sorted(paths) for key,paths in sorted(groups.items())}
    linked = []
    for r in sorted(requirements, key=lambda x:x["id"]):
        claims = [by_id[sid]["facts"]["claim"] for sid in r["sources"]
                  if sid in by_id and by_id[sid]["kind"] == "handoff"
                  and "claim" in by_id[sid]["facts"]]
        linked.append({**r, "claims":claims,
                       "verified":r["verification"] == "independently_verified"
                                  and bool(r["artifacts"])
                                  and all(aid in reviewed_artifacts for aid in r["artifacts"])
                                  and all(sid in by_id for sid in r["sources"])})
    return {"schema_version":1, "requirements":linked,
            "missing_source_ids":missing, "byte_groups":groups}
```

Use these exact IDs and statements in `docs/PROGRAM_REQUIREMENTS.json` (one object matching `checked_requirement` per line of the table). `sources` contains IDs from the generated inventory, never a guessed path; when a chat or package cannot be read, include its explicit `access="unavailable"` source record. `artifacts` contains the independently checked artifact digest only when one exists. Set `verification` to `missing`, `claimed`, `conflicting`, or `independently_verified`, and give each item a concrete next action from its current state.

| ID | System | Statement |
| --- | --- | --- |
| REQ-001 | PROGRAM | Index all accessible Codex, ChatGPT Work, and Claude chat turns with exact IDs and access gaps |
| REQ-002 | PROGRAM | Index each relevant Git checkout, remote, commit, dirty state, and ZIP handoff member |
| REQ-003 | PROGRAM | Reconcile all ten owner archives and preserve duplicate-byte versus overlapping-export distinctions |
| REQ-004 | PROGRAM | Require representation, session, timezone, roll, revision, license, and first-known availability before research admission |
| REQ-005 | ICARUS | Verify 20-minute Heikin Ashi signals against standard-price executable fills and the owner export |
| REQ-006 | ICARUS | Keep the active plant shadow-only and preserve Pulse as the fixed baseline |
| REQ-007 | NEXUS | Reconcile 659 accessible streams with the 238-stream v0.3 handoff and release hashes |
| REQ-008 | NEXUS | Fix and independently verify strict as-of replay without accepting unknown availability |
| REQ-009 | AION/PARALLAX | Verify durable evidence memory and representation-aware source inventory |
| REQ-010 | DAEDALUS | Verify complete candidate fields and distinct, budgeted protected holdouts |
| REQ-011 | ARGUS | Build and verify authenticated microstructure intake without candle-to-L2 promotion |
| REQ-012 | ATHENA | Build and verify independent supervisory risk and abstention authority |
| REQ-013 | ORACLE | Complete financial/research coordination and actual sibling adapters from the 75% checkpoint |
| REQ-014 | AEGIS | Obtain and verify the adversarial/state-supervision source package and its boundary with ATHENA |
| REQ-015 | ICARUS | Recover the exact Opus qualification floor and close missing-tune/missing-field loopholes |
| REQ-016 | ICARUS | Create an exceptional-candidates repo for fully cited candidates exceeding the fixed baseline |
| REQ-017 | ICARUS | Replace the XGBoost stub and file-existence gate with trained, versioned, held-out artifacts |
| REQ-018 | PROGRAM | Build per-asset/timeframe/representation ML with point-in-time macro, news, and financial features |
| REQ-019 | PROGRAM | Select champion/challenger candidates per asset/timeframe/regime in shadow mode only |
| REQ-020 | PROGRAM | Analyze settled losing trades without retroactively altering earlier decisions |
| REQ-021 | ICARUS | Replace the ten-minute delayed Yahoo path only with verified real-time data entitlement or chart data |
| REQ-022 | ICARUS | Deliver the private realistic backtester, multi-asset views, and configurable dashboard |
| REQ-023 | PROGRAM | Maintain owner-actions for exports, paid feeds, licenses, API keys, and eventual broker/prop decisions |
| REQ-024 | ICARUS | Defer themes, strategy-reactive animations, and lawful Dreambound playback until research/parity work |
| REQ-025 | PROGRAM | Require source timing, protected holdout, and real-fill parity gates before any execution discussion |

Update the source index when a new AEGIS package or ORACLE checkpoint arrives; do not replace older claims silently. Tests load this committed matrix and assert all 25 IDs, exact system names, source-or-gap links, and no unresolved `verified=True` flag.

- [ ] **Step 4: Run tests and inspect the human-readable ledger**

```powershell
py -3 -m unittest tests.test_ledger -v
py -3 -m unittest discover -s tests -v
```

Expected: the matrix includes every named system and no unresolved row is marked verified.

- [ ] **Step 5: Commit**

```powershell
git add src/csv_evidence/ledger.py tests/test_ledger.py docs/PROGRAM_REQUIREMENTS.json
git commit -m "feat: link program requirements to source evidence"
```

### Task 6: Canonical Reports and CLI

**Files:**
- Create: `src/csv_evidence/reporting.py`
- Modify: `src/csv_evidence/cli.py`
- Test: `tests/test_reporting.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: Tasks 2-5 records.
- Produces: `write_report(path: Path, report: dict) -> str` returning canonical SHA-256; CLI subcommands `inventory-zip`, `inventory-git`, `inventory-chat`, `assess-source`, `ledger`.

- [ ] **Step 1: Write failing atomicity and determinism tests**

```python
import json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from csv_evidence.reporting import write_report

class ReportingTests(unittest.TestCase):
    def test_repeat_write_has_same_digest(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"out.json"; data={"schema_version":1,"sources":[],"requirements":[],"errors":[]}
            self.assertEqual(write_report(p,data), write_report(p,data))
            self.assertEqual(json.loads(p.read_text()), data)

    def test_unapproved_payload_cannot_be_written(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                write_report(Path(d)/"bad.json", {"schema_version":1,"raw_csv_row":"SECRET"})

    def test_failed_replace_preserves_previous_report(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"out.json"; p.write_text("OLD", encoding="utf-8")
            with patch("csv_evidence.reporting.os.replace", side_effect=OSError("injected")):
                with self.assertRaises(OSError): write_report(p,{"schema_version":1})
            self.assertEqual(p.read_text(encoding="utf-8"), "OLD")
```

- [ ] **Step 2: Run test and confirm import failure**

```powershell
py -3 -m unittest tests.test_reporting -v
```

Expected: missing `reporting` module.

- [ ] **Step 3: Implement canonical output and commands**

```python
import hashlib, json, os, re, tempfile
from pathlib import Path
from .contracts import SOURCE_KEYS, REQUIREMENT_KEYS, checked_source, checked_requirement

REPORT_KEYS={"schema_version","sources","requirements","errors","missing_source_ids","byte_groups","assessment"}

def _validate_report(report: dict) -> None:
    if not isinstance(report,dict) or report.get("schema_version") != 1 or set(report)-REPORT_KEYS:
        raise ValueError("unapproved report fields")
    for source in report.get("sources",[]):
        if set(source) != SOURCE_KEYS | {"id"}:
            raise ValueError("unapproved source fields")
        base={k:source[k] for k in SOURCE_KEYS}
        if checked_source(base)["id"] != source["id"]:
            raise ValueError("source identity mismatch")
    for req in report.get("requirements",[]):
        if set(req)-REQUIREMENT_KEYS-{"claims","verified"}:
            raise ValueError("unapproved requirement fields")
        checked_requirement({k:req[k] for k in REQUIREMENT_KEYS})
    for error in report.get("errors",[]):
        if set(error) != {"locator","code"}:
            raise ValueError("error records carry locator and code only")
    for key,paths in report.get("byte_groups",{}).items():
        if not re.fullmatch(r"[0-9a-f]{64}",key) or not isinstance(paths,list) or not all(isinstance(p,str) and len(p)<=1024 for p in paths):
            raise ValueError("invalid byte group")
    if not all(isinstance(x,str) and re.fullmatch(r"[0-9a-f]{64}",x) for x in report.get("missing_source_ids",[])):
        raise ValueError("invalid missing source id")
    if "assessment" in report:
        assessment=report["assessment"]
        if set(assessment) != {"state","reasons","execution_authorized"} or assessment["execution_authorized"] is not False:
            raise ValueError("assessment cannot authorize execution")
        if not isinstance(assessment["reasons"],list) or not all(isinstance(x,str) and len(x)<=80 for x in assessment["reasons"]):
            raise ValueError("assessment reasons must be short codes")

def write_report(path: Path, report: dict) -> str:
    _validate_report(report)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload=(json.dumps(report, sort_keys=True, separators=(",",":"),
                        ensure_ascii=False, allow_nan=False)+"\n").encode("utf-8")
    digest=hashlib.sha256(payload).hexdigest()
    name=None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=path.parent, prefix=".report-",
                                         suffix=".tmp", delete=False) as out:
            name=out.name; out.write(payload); out.flush(); os.fsync(out.fileno())
        os.replace(name,path)
    finally:
        if name is not None and os.path.exists(name): os.unlink(name)
    return digest
```

Add these branches in `cli.py`; preserve its existing `scan`, `fixtures`, and `reconcile` behavior:

```python
from .archive_inventory import scan_zip, ScanBudget
from .local_inventory import scan_git, scan_claude_jsonl, check_chat_index
from .provenance import assess_source
from .ledger import build_ledger
from .reporting import write_report

# During argparse setup:
for name in ("inventory-zip","inventory-git","inventory-chat","assess-source","ledger"):
    sub=commands.add_parser(name)
    sub.add_argument("input", type=Path)
    sub.add_argument("--output", type=Path, required=True)
    if name == "inventory-chat": sub.add_argument("--claude-jsonl", type=Path)
    if name == "assess-source": sub.add_argument("--reviewed-evidence", type=Path)

# After parse_args, before the existing branches:
if args.command == "inventory-zip":
    report={"schema_version":1,"sources":scan_zip(args.input, ScanBudget())}
elif args.command == "inventory-git":
    report={"schema_version":1,"sources":[scan_git(args.input)]}
elif args.command == "inventory-chat":
    index=json.loads(args.input.read_text(encoding="utf-8"))
    sources=check_chat_index(index)
    if args.claude_jsonl:
        sources.extend(scan_claude_jsonl(args.claude_jsonl))
    report={"schema_version":1,"sources":sources}
elif args.command == "assess-source":
    payload=json.loads(args.input.read_text(encoding="utf-8"))
    reviewed=set(json.loads(args.reviewed_evidence.read_text(encoding="utf-8"))) if args.reviewed_evidence else set()
    result=assess_source(payload["scan"],payload["source"],payload["attestations"],
                         reviewed_evidence=reviewed)
    report={"schema_version":1,"assessment":result}
elif args.command == "ledger":
    payload=json.loads(args.input.read_text(encoding="utf-8"))
    report=build_ledger(payload["sources"],payload["requirements"])
else:
    report=None
if report is not None:
    write_report(args.output,report)
    return 0
```

The `--reviewed-evidence` file is a local list of previously human-reviewed SHA-256 hashes; absent it, `assess-source` cannot promote beyond structural status. The `inventory-chat` index carries ChatGPT/Codex thread IDs and digests only. Do not scrape browser cookies. Add a CLI regression test that compares two reports from unchanged synthetic inputs byte-for-byte and one that shows an unavailable source as a recorded failure.

- [ ] **Step 4: Run focused and full tests**

```powershell
py -3 -m unittest tests.test_reporting -v
py -3 -m unittest discover -s tests -v
```

Expected: deterministic output and preserved old report after an injected replace failure.

- [ ] **Step 5: Commit**

```powershell
git add src/csv_evidence/reporting.py src/csv_evidence/cli.py tests/test_reporting.py README.md
git commit -m "feat: write deterministic evidence reports atomically"
```

### Task 7: Reproduce Baselines and Freeze a Sanitized Inventory

**Files:**
- Create: `docs/PROGRAM_BASELINES.md`
- Create: `docs/PROGRAM_INVENTORY.md`
- Modify: `docs/NEXUS_HANDOFF_AUDIT.md`
- Test: `tests/test_program_docs.py`

**Interfaces:**
- Consumes: exact scanner outputs from Tasks 2-6 and current checkout/package bytes.
- Produces: committed locator/evidence map; does not modify any source repository.

- [ ] **Step 1: Write a failing documentation contract test**

```python
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
class ProgramDocsTests(unittest.TestCase):
    def test_required_baselines_are_explicit(self):
        text=(ROOT/"docs/PROGRAM_BASELINES.md").read_text(encoding="utf-8")
        for name in ("ICARUS","NEXUS","AION/PARALLAX","DAEDALUS","ORACLE"):
            with self.subTest(name=name): self.assertIn(name,text)
        self.assertIn("command",text.lower())
        self.assertIn("dirty",text.lower())

    def test_unverified_packages_are_named(self):
        text=(ROOT/"docs/PROGRAM_INVENTORY.md").read_text(encoding="utf-8")
        for name in ("ATHENA","ARGUS","AEGIS"):
            with self.subTest(name=name): self.assertIn(name,text)
        self.assertIn("unverified",text.lower())
```

- [ ] **Step 2: Run test and confirm missing files fail**

```powershell
py -3 -m unittest tests.test_program_docs -v
```

Expected: `FileNotFoundError` for the two new docs.

- [ ] **Step 3: Reproduce each current baseline and record the actual result**

```powershell
# From C:\Users\tripl\icarus-csv-evidence-lab
$env:PYTHONPATH=(Resolve-Path .\src).Path
py -3 -m unittest discover -s tests -v
# From C:\Users\tripl\Icarus
py -3 -m pytest tests_engine -q -p no:cacheprovider
# From C:\Users\tripl\nexus-review-20260923\bundle-checkout
$env:PYTHONPATH=(Resolve-Path .\src).Path
uv run --no-project --python 3.11 --with pytest --with numpy --with pandas python -m pytest -q -p no:cacheprovider
# From C:\Users\tripl\aion-review-20260923\icarus-aion
uv run --no-project --python 3.11 --with pytest python -m pytest -q -p no:cacheprovider
# From C:\Users\tripl\daedalus-intake-20260923\daedalus-research-os
$env:PYTHONPATH=(Resolve-Path .\src).Path
uv run --no-project --python 3.11 --with pytest --with numpy --with pandas --with scipy --with scikit-learn --with joblib python -m pytest -q -p no:cacheprovider
# From C:\Users\tripl\oracle-review-20260923\ICARUS_ORACLE_CHECKPOINT_C_75_SOL_FOR_SOL_EXTRA_HIGH\icarus-oracle
$env:PYTHONPATH=(Resolve-Path .\src).Path
uv run --no-project --python 3.11 --with pytest python -m pytest -q -p no:cacheprovider
$env:PYTHONPATH="$(Resolve-Path .\src);C:\Users\tripl\aion-review-20260923\icarus-aion;C:\Users\tripl\daedalus-intake-20260923\daedalus-research-os\src"
uv run --no-project --python 3.11 --with pytest python -m pytest -q -p no:cacheprovider
```

Run each block from the named directory, then record path, SHA/commit, dirty-tree status, dependency/environment command, exit code, pass/fail counts, and missing siblings. Re-run ORACLE with and without available AION/DAEDALUS siblings; the known earlier observation was 28/34 and 30/34, but the document must report its new actual run. Update `docs/NEXUS_HANDOFF_AUDIT.md` so its clean-bundle 117-pass claim is not confused with the dirty-tree 115-pass/2-fail strict replay result. Never edit or reset those source trees merely to obtain a green count.

Write `docs/PROGRAM_INVENTORY.md` from exact Git commits, ZIP SHA-256/member ordinals, local Claude session IDs, accessible app thread/turn IDs, and archive manifests. Query `mcp__codex_app__list_threads` at its largest supported limit, page `list_archived_threads`, and use `read_thread` cursors for relevant chats; preserve the exact thread/turn locator when accessible and record inaccessible older turns as gaps. Mark absent ATHENA/ARGUS implementation packages and any AEGIS sandbox artifact not present locally as unverified. List the 10 owner archives, the 659 accessible member count and 238-member NEXUS handoff claim as separate observations, not equal coverage. Do not paste raw CSV rows, secrets, or full chat messages.

- [ ] **Step 4: Run documentation and full tests; inspect staged diff for sensitive data**

```powershell
py -3 -m unittest tests.test_program_docs -v
py -3 -m unittest discover -s tests -v
git diff --check
git diff --cached --stat
```

Expected: docs identify all five reproduced baselines plus ATHENA/ARGUS/AEGIS gaps; no raw owner data staged.

- [ ] **Step 5: Commit the verified inventory**

```powershell
git add docs/PROGRAM_BASELINES.md docs/PROGRAM_INVENTORY.md docs/NEXUS_HANDOFF_AUDIT.md tests/test_program_docs.py
git commit -m "docs: record reproducible program baselines and gaps"
```

### Task 8: Independent Acceptance and Handoff

**Files:**
- Modify: `README.md`
- Modify: `docs/ROADMAP.md`
- Test: all `tests/*.py`

**Interfaces:**
- Produces: a reviewed first-subproject baseline and explicit blockers for the next NEXUS timing-repair spec.

- [ ] **Step 1: Add an end-to-end synthetic acceptance test**

```python
def test_no_structural_scan_grants_training_authority(self):
    from csv_evidence.provenance import assess_source
    scan={"sha256":"a"*64,"parse_complete":True,"finding_counts":{}}
    result=assess_source(scan,{"digest":"a"*64},[])
    self.assertEqual(result["state"],"structurally_checked")
    self.assertFalse(result["execution_authorized"])
    self.assertNotEqual(result["state"],"research_eligible")
```

Place the test in `tests/test_reporting.py`; also assert no CLI operation writes to any owner source path by hashing synthetic inputs before and after commands.

- [ ] **Step 2: Run the entire suite and two identical scans**

```powershell
$env:PYTHONPATH=(Resolve-Path .\src).Path
py -3 -m unittest discover -s tests -v
py -3 -m csv_evidence.cli fixtures .\private-data\acceptance
py -3 -m csv_evidence.cli scan .\private-data\acceptance --output .\reports\acceptance-a.json
py -3 -m csv_evidence.cli scan .\private-data\acceptance --output .\reports\acceptance-b.json
Get-FileHash .\reports\acceptance-a.json, .\reports\acceptance-b.json -Algorithm SHA256
```

Expected: identical report hashes for unchanged input, all tests passing, no source changes. If `private-data/acceptance` already exists, use a new named test directory rather than overwrite it.

- [ ] **Step 3: Document limits, then request independent review**

```markdown
## Authority boundary

Inventory equivalence is not chart identity. A source remains unavailable to
training or execution until a separately reviewed, point-in-time source record
and downstream system gates approve it. The evidence lab never emits orders.
```

Update `README.md` and `docs/ROADMAP.md` with this boundary, the exact next NEXUS timing work, and the remaining full-program stages from the spec. Have a fresh reviewer compare the committed inventory against original source paths and challenge the five Review Focus cases; do not use the authoring context to approve itself.

- [ ] **Step 4: Commit only after the review findings are resolved**

```powershell
git diff --check
git status --short
git add README.md docs/ROADMAP.md tests/test_reporting.py
git commit -m "docs: hand off verified evidence contract"
```

## Plan Self-Review

- Spec coverage: source inventory (Tasks 1-3, 7), provenance/time (Task 4), system claims and requirement matrix (Task 5), atomic/private reports (Task 6), reproduced baselines and independent review (Tasks 7-8).
- The broader ML pipeline, candidate search, live data path, interface, and broker work remain separate architectural subprojects. This plan records them; it does not falsely implement them.
- No task edits or enables the paper engine, source repos, candidate promotion, or broker routing.
