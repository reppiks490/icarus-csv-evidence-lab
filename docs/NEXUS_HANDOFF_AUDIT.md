# NEXUS v0.3 Handoff Audit

Date: 2026-09-23. The owner supplied `NEXUS_ADAPTIVE_MARKET_FABRIC_v0.3_SOL_FOR_SOL_EXTRA_HIGH.zip` (SHA-256 `11bc19567b0e02c10a5508610e0218065513e70197ea2f766cdc7da048010cec`). The ZIP was path-checked before extraction. Its Git bundle was cloned separately; bundle head and tag both identify `6529eed7623e9a967bb053c9a78e4102d2c18d6d`. The release manifest names older code checkpoint `763497739c89f54d215e211e9be295363c84bc5b`, which is an ancestor, not the final bundle head.

## Independently verified

- Python 3.11 with `numpy`, `pandas`, and `pytest`: `117 passed` locally. `compileall -q src tests` passed.
- The manifest's listed file hashes match the extracted files except `artifacts/final_verification.v0.3.SOL.json`: listed `7a27e15e...`, actual `07cbaaf1...`. The bundle's last commit changed that verification artifact and the release manifest's embedded verification text without refreshing the file-hash entry. Treat the seal as inconsistent until regenerated and rechecked.
- Source code includes ZIP-native and extracted-file cataloging, positional duplicate-header records, raw/logical hashes, explicit representation review, replay and sibling routing contracts. These are engineering capabilities, not live or financial validation.

## Unresolved

- Handoff catalog: 238 usable streams / 1,970,753 rows. NEXUS's ZIP-native profiler was rerun locally on PARALLAX's nine recovered ZIPs: 626 usable members, 12,588,916 logical rows, 513 distinct byte hashes, and 157 duplicate-header members. The tenth index ZIP separately yielded 33 usable members, 1,199,340 rows, and 26 duplicate-header members. Combined: 659 members and 13,788,256 rows, exactly the current PARALLAX physical counts. The prior 12,588,290-row handoff was lower by 626, one per nine-ZIP member. The all-ten combined distinct-hash set still requires a NEXUS-emitted unified manifest comparison; PARALLAX reports 542. A complete source/clock/availability review remains required before owner-corpus or trading claims.
- The bundle's top-level `VALIDATION_STATUS.md` still describes v0.1 and 22 tests; `docs/VALIDATION_STATUS.md` describes v0.3. Documentation selection must be made unambiguous.
- No authenticated true trade/depth feed, live adapter, real-time availability attestation, broker authority, or proven predictive edge was established by this handoff. `pyarrow`/Parquet runtime parity was not in the local baseline.
- AION source is present in a private repository and its 21 tests passed locally. DAEDALUS source is present at current private `main` with a newer 59-test checkpoint, but its suite has not yet been independently rerun in this workspace. ATHENA and ARGUS local ZIPs contain blueprints, not implementation source; their 3/4-test handoff counts cannot be rerun here. Contract smoke tests do not certify deployed services.

## Admission rule

Keep NEXUS and every sibling in research/shadow status. Do not route its output into live execution or promote an ML candidate because a parser, unit test, or replay smoke passed. First reconcile source identity and representation clocks, then run as-of/availability and holdout leakage checks, then evaluate realistic fills and uncertainty independently.
