# Data Layer Guide

## Provider Chain

1. `DataManager` orchestrates cache-first lookups before falling back to providers.
2. Providers currently include:
   - `LocalCSVProvider` for deterministic fixtures (`tests/data/`).
   - `YahooFinanceProvider` for live data via `yfinance` (with retries/backoff).
3. Use `DataSettings` to assemble provider chains without scattering instantiation logic. `DataSettings.defaults(cache_dir, data_dir)` wires local CSV + Yahoo; override `provider_chain` to add/remove providers or adjust parameters.
4. Implement additional providers by subclassing `DataProvider` and passing them via `DataSettings`.

## Cache Semantics

- `LocalDataCache` stores JSON metadata and CSV frames under `cache/`.
- Keys are derived from `DataRequest.cache_key()` to guarantee reproducibility (symbol, interval, date range, adjusted flag).
- Use `cache.clear()` sparingly; prefer targeted deletion to keep offline datasets available.

## Validation Rules

`DataValidator` enforces:

- Required columns: `timestamp`, `open`, `high`, `low`, `close`, `volume`.
- Monotonic, duplicate-free timestamps (converted to UTC).
- No NaNs in required columns.
- Bounds: data must stay within `[request.start, request.end]` to avoid lookahead.

Failed validations raise `DataValidationError`, while provider issues raise `DataProviderError`.

## Offline Testing

- Use `scripts/generate_synthetic_data.py` to populate `tests/data/` with reproducible fixtures (e.g., `synthetic_aapl.csv`). The script runs automatically in CI and is safe to run before `pytest`.
## Tips

- Always request adjusted data when comparing across providers.
- Batch repeated requests to leverage the cache.
- Capture metadata (provider name, interval) in logs for auditability.
- Centralize configuration through `DataSettings` so CLI tools, notebooks, and production jobs share the same provider order and cache paths.
