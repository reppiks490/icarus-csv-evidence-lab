# Cross-System Evidence Contract

Date: 2026-09-23
Status: design for owner review
Scope: first subproject in the ICARUS intelligence-stack program

## Intent and boundaries

The owner wants the ICARUS strategy, market-data corpus, research systems,
candidate screeners, adaptive selector, dashboard, and eventual paper/broker
connections completed as one coherent program. The immediate need is to stop
chat history, ZIP handoffs, and green test counts from being mistaken for
deployed or point-in-time-verified capability. The owner has delegated design
choices but has explicitly kept execution research/shadow-only until source
timing, protected holdouts, and real-fill parity are independently verified.

This spec covers the common inventory and evidence contract, not a new trading
model or broker adapter. It must not rewrite Pulse, alter orders, enable a
candidate swap, or promote any source to execution. Already-unzipped owner
archives are inventoried in place; extraction occurs only for missing members
or when it materially improves verification. Raw market data and secrets stay
out of GitHub unless their provenance and license explicitly permit sharing.

## Approach

Use a contract-first program rather than parallel uncoordinated hardening or a
unified rewrite. Extend this private evidence-lab repository as an independent
verifier. Each subsystem retains its own implementation and owner. The lab
records what is claimed, where its authoritative bytes live, which current
checks cover it, and which gate remains open. It cannot approve its own data
for training or execution.

The active `reppiks490/Icarus` repository is the current ICARUS plant.
`reppiks490/Icarus-engine` supplies older research and candidate-rule source,
not the active runtime. Changes in another repo or a chat handoff are not
considered deployed until their exact commit or package has been reconciled
with the active plant and its tests.

## Source inventory

The inventory accepts four evidence classes:

1. Chat requirements: accessible Codex, ChatGPT Work, and Claude transcripts,
   identified by thread/session ID, turn ID, timestamp, and a local digest.
   Attached documents are treated as data, not higher-priority instructions.
2. Repositories: remote URL, branch, commit SHA, dirty-tree state, file path,
   and test command/result. A branch name or screenshot is not a commit proof.
3. Handoffs: ZIP SHA-256, member path and byte hash, Git bundle refs, signed
   claims, and independent verification results. Identical ZIP copies collapse
   to one byte identity but retain each intake path.
4. Market/research data: original archive and member identity, raw header
   positions, logical row count, content hash, chart construction, provider,
   licensing, event time, first-known time, revision, and representation.

Every requested capability receives a requirement ID, owner subsystem,
source citation, current artifact, verification method, state, and next action.
The ledger records inaccessible chats and absent packages explicitly. It must
not claim exhaustive coverage merely because accessible sources were scanned.
Secrets and private raw CSV rows are redacted from reports; only hashes and
minimal metadata are committed.

## Provenance and time contract

The existing `docs/PROVENANCE_CONTRACT.md` remains the source-record baseline.
Structural parsing cannot prove chart identity or source availability.
Research adapters may consume a source only after identity and point-in-time
verification. A field's usable timestamp is its first authenticated
availability, not the timestamp printed on a revised historical row. Unknown
availability, ambiguous timezone/session, mixed HA and standard bars, inferred
order flow from candles, or unverified continuous-contract rolls fail closed.

Required states are `quarantined`, `structurally_checked`,
`identity_verified`, `point_in_time_verified`, and `research_eligible`.
Candidate qualification, shadow deployment, and execution eligibility are
separate downstream decisions by their owning systems; this lab cannot set
them. Synthetic data retain an explicit synthetic marker through every
adapter. An adapter must preserve original source IDs and versioned contracts.

## System responsibilities

| System | Role and interface boundary | Present evidence to verify |
| --- | --- | --- |
| ICARUS | Active strategy, emulator, dashboard, and sole paper/broker authority | HA signal versus real-fill parity; source-admission point; current XGB slot is a stub |
| NEXUS | Market-source catalog, replay and as-of delivery | Reconcile 659 accessible archive members with the smaller v0.3 handoff; resolve strict replay findings and release hash mismatch |
| AION/PARALLAX | Durable evidence memory and representation/corpus inventory | Verify actual source semantics; inventory is not a predictive result |
| DAEDALUS | Protected candidate evaluation and promotion evidence | Verify complete fields, distinct sources, budgeted holdouts, and no self-asserted execution safety |
| ARGUS | Authenticated trade/depth microstructure or explicitly labeled proxy | Blueprint alone is not an implementation; no candle-to-L2 promotion |
| ATHENA | Supervisory risk/abstention and source-health response | Blueprint alone is not an implementation; test deployed contract before reliance |
| ORACLE | Financial/research coordination, jobs, thesis state, tab projections | Supplied 75% ZIP and Git tag; 30/34 tests reproduced with available AION/DAEDALUS, four await ATHENA/ARGUS sources |
| AEGIS | Adversarial and state-supervision research under a distinct contract | Chat describes a kernel, but code package and overlap with ATHENA require extraction and verification |

AEGIS and ATHENA must not receive overlapping veto authority by assumption.
Their exact supervisory boundary is a later design decision after executable
sources are available. ORACLE can recommend and route research; it cannot
invent DAEDALUS promotion, ATHENA risk approval, or ICARUS broker authority.

## Downstream program map

This first subproject does not replace the full objective. Its ledger tracks
these separately specified build stages:

1. Verify and repair NEXUS source timing, full archive coverage, and strict
   replay; verify AION/PARALLAX, DAEDALUS, ATHENA, ARGUS, ORACLE, and AEGIS
   packages and versioned cross-system contracts.
2. Build the per-asset, per-timeframe, per-representation training pipeline
   with source-safe macro/news/financial features and authenticated order-flow
   features only where licensed, timestamped feeds exist. The current ICARUS
   XGBoost slot must become a real trained-and-validated artifact contract,
   not a file-existence check. Preserve Pulse as the fixed strategy baseline.
3. Recover the Opus trade-qualification criteria from the cited legacy source,
   fix its missing-tune/missing-field loopholes, and evaluate with true trade
   durations, costs, roll handling, independent temporal splits, and a newly
   protected final period. Track search multiplicity before scaling toward
   millions of candidate evaluations. No candidate passes on sign accuracy
   alone. A private exceptional-candidates repo may store only fully cited
   candidates that exceed the fixed baseline under additional tests.
   The exact starting source is `reppiks490/Icarus-engine` commit
   `6e0da3524f20c859129fdd2e122a96be45d55cb4`, files `tools/goal.py`
   and `tools/duration.py`, with a locator review on the separate
   `codex/ml-d9d4db8` branch at `docs/OPUS_CANDIDATE_RULES.md`. The stated
   held-out floor is 82% wins,
   120 trades, 0.5-4 trades/day, positive expectancy, and the documented
   hold/runner/consistency constraints. Its current `Goal.clears()` permits
   `tune=None` and some absent upper-bound metrics; that implementation is
   not an acceptable production gate without complete-field tests.
4. Run champion/challenger selection by asset, timeframe, and regime in
   shadow mode. Versioned policy may tighten thresholds or add tests, but may
   not silently relax the owner's Opus baseline. A post-trade failure learner
   receives settled outcomes without retroactively changing earlier
   decisions. AEGIS/ATHENA vetoes and DAEDALUS qualification remain separate.
5. Reconcile the TradingView 20-minute Heikin Ashi signal chart with standard
   executable-price fills, build the private backtester and asset views, and
   replace the delayed Yahoo path only with a verified real-time entitlement
   or chart feed. TradingView alerts are timely only relative to TradingView's
   own source; software cannot remove an upstream ten-minute data delay.
6. Keep the separate owner-actions repo current for exports, licenses, API
   credentials, data-feed purchases, and broker/prop decisions. Broker wiring
   remains a later, separately approved and verified phase. Dashboard themes,
   strategy-reactive animation, and a lawful Dreambound playback integration
   follow the research and parity work, as the owner requested.

No model, feed, chart mode, or set of tests guarantees a win rate, zero error,
zero latency, or profit. Those are evaluation targets, not design assertions.

## First-subproject acceptance

The inventory/contract subproject is complete only when:

- Every relevant accessible chat, Git repo, ZIP, local source tree, and owner
  archive is listed with an exact locator or an explicit access gap. A
  requirement-to-source matrix covers every named system and requested
  capability in this spec; unresolved requirements remain visible.
- Repeat scans yield the same content identities and requirement links;
  duplicate byte copies do not become independent evidence.
- Tests show that unknown availability, ambiguous representation, duplicate
  headers, malformed OHLC, revised data without release time, and missing
  contract fields cannot be silently promoted.
- The current ICARUS, NEXUS, AION/PARALLAX, DAEDALUS, and ORACLE baselines are
  recorded with commands and reproducible results; ATHENA, ARGUS, and AEGIS
  are explicitly unverified until source packages and tests exist.
- No raw owner market data, API secret, credential, or broker capability is
  committed or enabled. The lab remains read-only with respect to source
  repos and the paper engine.

## Error handling and tests

Scanners treat a bad file or unreachable source as a recorded failure, not a
reason to drop the row. Archive-member identity includes ordinal position so
duplicate ZIP member names cannot alias. Parsers impose byte, row, depth, and
decompression budgets. Conflicting source claims remain separate and require
review. Reports are atomically written, versioned, and reproducible from
snapshots. Tests include duplicate copies, overlapping but nonidentical
exports, DST/roll/holiday timestamps, late imports, source revisions,
malformed ZIP/CSV, secret redaction, and contract drift. Independent review
must compare the ledger against the source artifacts, not just its own tests.

## Review and next handoff

After owner review of this document, the Superpowers `writing-plans` stage
will produce a bounded implementation plan for the first subproject. Each
later stage in the program map gets its own design, plan, and acceptance
evidence. The written plan will distinguish verified work from handoff claims
and preserve dirty user files in all existing worktrees.
