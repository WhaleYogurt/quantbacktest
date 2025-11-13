# Metrics & Reporting

## Pipeline Overview

1. **Engine run** – Each `BacktestRunner` segment records `portfolio_snapshot` (cash, equity, exposures).
2. **Metadata** – After a run, `metadata.json` captures segment summaries.
3. **Analyzer** – Run `python -m quantbacktest.metrics.cli --metadata artifacts/<run_id>/metadata.json` to compute metrics and persist `metrics.json`.

## Metrics Reported

- `cumulative_return` – Final equity growth relative to starting capital.
- `average_return` & `annualized_return` – Mean return per period and extrapolated annual figure.
- `max_drawdown` – Maximum peak-to-trough decline across the cumulative curve.
- `sharpe` / `sortino` – Risk-adjusted ratios with zero risk-free rate assumption.
- `segments` – Number of segments in the run (useful for walk-forward/grid-search attribution).

## Extending Metrics

- Implement additional helpers in `quantbacktest.metrics` (e.g., Calmar, exposure attribution).
- Plug into `analyze_engine_result` or create bespoke scripts reading `metadata.json`.

## CI Integration

- `test.bat` already runs the metrics CLI on grid-search output and logs the summary in `report.txt`.
- For pipelines, archive `report.txt`, `profile.txt`, `artifacts/<run_id>/metadata.json`, and `metrics.json` as build artifacts to enable regression diffs.
