# Provenance Contract

The `scan` output is a structural evidence record, not an import approval. It includes byte size, SHA-256, original header positions, logical CSV row count, parser findings, a rough OHLC-like role, and explicit `unverified` provenance fields. Identical hashes identify identical bytes, **not** equivalent market meaning; different hashes may still represent overlapping dates or a later export.

Before a source can influence a backtest, candidate selection, or live decision, a separate signed-off source record must identify:

1. Exact provider, exchange, symbol, contract or continuous-contract convention, and license/redistribution scope.
2. Chart representation (standard OHLC, Heikin Ashi, Renko, footprint, TPO, session profile, etc.), construction parameters, and whether prices are executable.
3. Interval and timestamp meaning (bar open/close, source timezone), RTH/ETH calendar, holiday handling, adjustment and roll rules.
4. Original file SHA-256, export time, publisher/version, parent archive/member, and immutable source URI or local intake ID.
5. First-known availability for **each feature or event** used in a decision. Historical bar timestamps alone do not prove what a live trader could have known. Revised data require revision/receipt history or must be excluded from point-in-time tests.
6. Whether this is raw observed market data, derived chart data, or clearly synthetic fixture data. A derived candle is not an authenticated trade tape or level-2 order book.

Approval states should be `quarantined`, `structurally_checked`, `identity_verified`, `point_in_time_verified`, and only then a separately authorized `research_eligible` or `execution_eligible`. A parser result may advance at most to `structurally_checked`; this CLI intentionally leaves every file quarantined.

**Owner involvement:** most hashes, schemas, and duplicate groups can be generated automatically. Only chart/account facts that are not embedded in the file need confirmation from TradingView export settings, provider documentation, or a trusted collection log. Do not ask the owner to hand-label hundreds of files. Cluster by schema, name, and export batch, then ask about ambiguous groups. Account keys must never be put in a source record.
