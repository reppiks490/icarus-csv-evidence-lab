# Advanced CSV automation persistence

This path is the metadata-only durable sink for the scheduled Advanced CSV Data Collector.

- Raw owner market CSV/ZIP/XLSX data, paid-feed exports, secrets, credentials, and personal data MUST NOT be committed here.
- One logical scheduled run produces exactly one immutable `history/<RUN_ID>.json` record.
- `heartbeat.json` is the only in-progress marker.
- `latest.json` must always be the most recent fully persisted run and is updated only after history verification.
- `state.json` and `manifest.json` are updated after `latest.json`, with fresh-SHA conflict checks and post-write verification.
- A run is not `RUN_PERSISTED` until history/latest/state/manifest agree on the same RUN_ID and returned GitHub commit/blob evidence has been re-read.
- Missing historical runs are never invented; recover only from verifiable artifacts.
