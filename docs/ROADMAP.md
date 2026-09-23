# Strategic Next Steps

## P0: preserve and classify

1. Reconcile all accessible owner archives against NEXUS v0.3's 238-stream handoff and PARALLAX's ten-archive, 659-entry checkpoint. Compare archive/member/hash identity and logical row counts, not filenames alone. Keep reports private; do not upload raw CSVs to this repo.
2. Run this lab's read-only structural scan on discrepant members and adversarial fixtures. Its result is an independent diagnostic, not a second source of truth or an automatic admission vote.
3. Cluster by exact hash, apparent symbol/interval, schema, and overlapping timestamps. Treat each cluster as a question, not proof of equivalent chart type. Resolve NEXUS's release-manifest hash mismatch before publishing a sealed release.
4. Obtain verified export/settings evidence per distinct chart configuration, including Heikin Ashi vs standard, RTH/ETH, timezone, continuous-roll policy and indicator overlays. Review NEXUS's representation queue; never infer timestamp meaning from cadence alone.
5. Add authenticated receipt/first-availability logs for feeds and macro/news revisions before point-in-time model evaluation.

## P1: guarded adapters

6. NEXUS: make the reconciled catalog and reviewed representation registry the source-fabric input. Prove strict as-of replay, archive parser failure visibility, and exact sibling contract drift checks before any model promotion.
7. ICARUS: place a NEXUS-backed identity/admission check before the automatic `history/drop` merge and require verified chart identity for canonical price history. Regression-test existing bars and preserve a rollback copy. No live broker actions in this phase.
8. AION/PARALLAX: join findings to archive-member hashes; keep source confidence separate from predictive confidence. Reject synthetic demo rows from any performance claim.
9. DAEDALUS: replace line-based counts with logical CSV record counts, retain duplicate header positions, and disallow self-asserted `execution_safe` promotion.
10. ARGUS: enforce a hard `proxy` versus `authenticated trades/depth` type boundary. Create an explicit capability-based mapping from ARGUS `E0`-`E4` to AION's differently numbered `EvidenceTier`; never pass tier integers through. Test that candles cannot satisfy L2 requirements.
11. ATHENA: ingest NEXUS health/quality as advisory evidence with explicit unknown states; verify the deployed sibling contract and reject stale or unreviewed source promotion.

## P2: analysis and display

12. Build a new safe numeric preview with a real CSV parser, decimal precision, escaped labels, explicit time axis, and provenance/latency badges. Do not embed source CSV in an inline script.
13. Add large-file load tests and late-import/duplicate/revision tests. Performance improvements must preserve exact bytes and audit lineage.
14. After adapters are implemented, run independent verification on real owner samples, synthetic edge cases, and negative tests. A clean structural scan is never a profitability or parity result.

No action here should connect to a live broker or promote a strategy candidate automatically.
