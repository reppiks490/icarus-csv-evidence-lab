# Maintainer workspace

> [!CAUTION]
> **PROPRIETARY — ALL RIGHTS RESERVED**
>
> **No public license or personal-use license is granted.** Except where [LICENSE.md](LICENSE.md) preserves applicable law, GitHub platform rights, third-party terms, or prior valid permissions, written authorization is required to use, run, copy, modify, redistribute, or sell covered material. Do not remove ownership notices or claim this work as your own.
>
> Unauthorized infringement may lead to takedown requests and legal proceedings for available remedies. Public visibility is not permission to reuse.

This workspace is maintained for its owner and authorized collaborators. Permission requests and the full terms are in [LICENSE.md](LICENSE.md).

<details>
<summary>Maintainer documentation</summary>

# ICARUS CSV Evidence Lab

Private, research-only independent CSV validation and integration map for ICARUS, NEXUS, AION/PARALLAX, DAEDALUS, ARGUS, and ATHENA.

This repo does **not** contain owner market data. It does not train models, place orders, approve a feed, repair source files, or certify chart semantics. A successful structural scan means only that a file parsed and met the checks implemented here.

## What was extracted

- From [datablist/sample-csv-files](https://github.com/datablist/sample-csv-files): the **pattern** of named broken CSV fixtures, an expected-result manifest, and parser regression tests. We built new, synthetic trading-shaped fixtures. Its customer and company rows are not market data.
- From [watson/chart-csv](https://github.com/watson/chart-csv): the **idea** of fast numeric CSV inspection. Its implementation was not copied or adopted; the comma-split parser, integer conversion, and raw CSV embedding in a script are unsuitable for futures prices, quoted fields, or untrusted input.
- From the owner systems: the need to keep source bytes, duplicate header positions, hashes, chart identity, and decision-time availability distinct.

The [source decision record](docs/SOURCES.md), [system map](docs/SYSTEM_MAP.md), [NEXUS handoff audit](docs/NEXUS_HANDOFF_AUDIT.md), [provenance contract](docs/PROVENANCE_CONTRACT.md), and [roadmap](docs/ROADMAP.md) are the strategic handoff. NEXUS already has ZIP-native corpus cataloging; this repository is an independent structural check and a place to test cross-system admission boundaries, not a replacement for NEXUS.

## Run on Windows

From this repository in PowerShell:

```powershell
$env:PYTHONPATH = (Resolve-Path .\src).Path
py -3 -m unittest discover -s tests -v
py -3 -m csv_evidence.cli fixtures .\private-data\synthetic
py -3 -m csv_evidence.cli scan 'C:\path\to\an\export.csv' --output .\reports\local-audit.json
py -3 -m csv_evidence.cli reconcile 'C:\path\to\parallax-ten-archives.json' 'C:\path\to\nexus-catalog.json' --output .\reports\reconciliation.json
```

The scan is read-only. `reports/`, `private-data/`, CSV, ZIP, and XLSX files are ignored by Git. Do not commit account data, paid-feed exports, secrets, or raw market files here.

## ICARUS repository federation

The active ICARUS engine may consume this repository's **status/evidence receipts only** through the machine-readable contract at
`automation_intelligence/advanced_csv/icarus_consumer_contract.json`.

The consumer contract deliberately keeps these meanings separate:

- `heartbeat.RUN_STATUS=RUN_PERSISTED` proves a durable run receipt only.
- substantive evidence authority remains `evidence_state.EVIDENCE_STATUS`.
- raw owner market data is not transferred into ICARUS by this federation.
- no CSV artifact, model, strategy, paper order, live order, or execution authority is auto-promoted.
- ICARUS verifies the Git blob identity of every consumed receipt and exposes pointer disagreement instead of silently reconciling it.

This lets the actively running CSV evidence lane collaborate with ICARUS without collapsing durability, evidence, data admission, model qualification, and trading authority into one signal.

## Current evidence

The first local probe read three owner exports without modifying them: two NQ 20-minute files and one GC 20-minute file. All had five OHLC-like columns and parsed, but the NQ files differed by 11 rows and had different SHA-256 hashes. Chart type, roll mode, session, timezone, provider, and first-known availability remain unverified. This is not a parity or profitability result.

The next work is explicit in [docs/ROADMAP.md](docs/ROADMAP.md). Do not wire this scanner to auto-promote a file into live or model-training use.

## License and ownership

Copyright (c) 2026 reppiks490. **Proprietary — all rights reserved.**
Public visibility does not grant permission to reuse, redistribute, sell, or claim this work as your own. Written permission is required except where applicable law, existing grants, third-party terms, or GitHub's terms provide otherwise. See [LICENSE.md](LICENSE.md) for the full notice and permission requests.

</details>
