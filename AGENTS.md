# ICARUS federation instructions for AI units

Every AI unit working in this repository must treat Advanced CSV as part of the shared ICARUS evidence fabric.

Before making claims about data availability, source coverage, freshness, provider access, research status, or blockers, read the canonical federation state in `reppiks490/Icarus-engine`:

- `config/data_ingestion_manifest.json`
- `docs/agent-handoffs/FEDERATED_DATA_COLLECTION.md`
- `docs/agent-handoffs/DATA_GAP_LEDGER.md`
- `automation_intelligence/sentinel/data_health.json`
- `automation_intelligence/manifest.json`

This repository contributes the persisted Advanced CSV evidence lane under `automation_intelligence/advanced_csv/**`, including latest state, heartbeat/finalization state, history, and restored-five liveness/durability receipts. Those artifacts are shared research evidence for the federation; they are not private to one AI account.

The restored-five watchdog/liveness workflows protect persistence and freshness. They do not themselves create new third-party API entitlements. Do not copy plaintext provider credentials here or infer access from another AI account. Use the GitHub-native provider/data plane in Icarus-engine for source-qualified external evidence.

Preserve immutable evidence history and fail-closed watchdog behavior. If an AI unit discovers stale, missing, inconsistent, or unconsumed evidence, it must repair the ICARUS-owned gap or publish the exact external blocker and evidence path.
