# Source Decision Record

Observed 2026-09-23. Source repositories are cited at immutable commits so later changes do not silently alter this review.

| Source | Revision | Useful idea | Excluded implementation/data |
| --- | --- | --- | --- |
| [watson/chart-csv](https://github.com/watson/chart-csv) | [`90d4157`](https://github.com/watson/chart-csv/tree/90d41573426f6cdd8b5ea96f10ed824bb34f7185) | Quick, browser-visible numeric CSV preview after trusted parsing. | `templates/head.html` uses `split('\n')`, `split(',')`, and `parseInt`; it loses decimal ticks, cannot handle quoted commas/newlines, ignores a time axis, and injects CSV into inline JavaScript. `index.js` simply streams source bytes into that HTML. Do not use it to render owner exports. |
| [datablist/sample-csv-files](https://github.com/datablist/sample-csv-files) | [`f97f6cf`](https://github.com/datablist/sample-csv-files/tree/f97f6cfdf0aede55f2730225a5de17ddac11a443) | `src/broken_csv.py` records deliberately malformed fixtures, expected outcomes, and a manifest; `tests/test_broken_csv.py` asserts parser behavior. Useful as a test-design pattern. | `src/schemas.py` and `src/generators.py` build synthetic CRM/customer/product records. They carry no market labels or order-flow truth. Do not mix their rows with the owner corpus. |

No code or data from either repository is vendored. The lab uses an independent Python standard-library implementation. A chart preview would require a separate, escaped visualization implementation and its own review.

## Owner-source observations

Local Icarus source in `C:\Users\tripl\Icarus-ml-d9d4db8`:

- `icarus_plant/drop.py::ingest_file` parses OHLC-like CSV and merges it into canonical history based largely on filename and detected granularity. It does not independently verify chart type, continuous-contract roll, session, or provider before merge.
- `icarus_engine/feeds/bars.py::parse_ohlcv_csv` builds a dictionary by timestamp, so later duplicate timestamps win; it also tolerates dropped unparsable rows. The new lab must remain an independent **pre-ingest** gate, not a claim that the existing parser is wrong in every use.
- `icarus_engine/csv_access.py` lists available files but does not certify them.

The owner's two sampled `CME_MINI_DL_NQ1!, 20.csv` files have the same five-column schema but 20,194 versus 20,183 logical rows and different SHA-256 hashes. Neither filename nor headers establish which chart representation produced them. No raw owner CSV was copied into this repo.
