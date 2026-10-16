# ICARUS federation instructions for AI units

Every AI unit working in this repository must treat Advanced CSV as part of the shared ICARUS evidence fabric.

## Central work coordination is mandatory

Before substantial work, use the canonical model-neutral coordination bus in `reppiks490/icarus-owner-actions`: read `coordination/START_HERE.md`, `coordination/ACTIVE.md`, `coordination/collisions.json`, `coordination/owner_status.json`, and applicable directives. Create/resume a unique central session and publish a PLAN/CLAIM event with narrow repo-qualified targets before mutation. Re-read the compiled collision state immediately before changing a reserved path. No task is reserved merely because a particular model or chat historically worked it; overlapping target work requires explicit mutual cooperation. Publish WAITING/UPDATE/BLOCKED/HANDOFF/RELEASE/COMPLETE events as state changes, and continue useful non-conflicting work while dependencies run.

Before making claims about data availability, source coverage, freshness, provider access, research status, or blockers, read the canonical federation state in `reppiks490/Icarus-engine`:

- `config/data_ingestion_manifest.json`
- `docs/agent-handoffs/FEDERATED_DATA_COLLECTION.md`
- `docs/agent-handoffs/DATA_GAP_LEDGER.md`
- `automation_intelligence/sentinel/data_health.json`
- `automation_intelligence/manifest.json`

This repository contributes the persisted Advanced CSV evidence lane under `automation_intelligence/advanced_csv/**`, including latest state, heartbeat/finalization state, history, and restored-five liveness/durability receipts. Those artifacts are shared research evidence for the federation; they are not private to one AI account.

The restored-five watchdog/liveness workflows protect persistence and freshness. They do not themselves create new third-party API entitlements. Do not copy plaintext provider credentials here or infer access from another AI account. Use the GitHub-native provider/data plane in Icarus-engine for source-qualified external evidence.

Preserve immutable evidence history and fail-closed watchdog behavior. If an AI unit discovers stale, missing, inconsistent, or unconsumed evidence, it must repair the ICARUS-owned gap or publish the exact external blocker and evidence path. Live broker arming follows the central owner status and is currently disabled.
