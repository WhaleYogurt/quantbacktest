# Quickstart

Welcome to **quantbacktest**. Follow these steps to get up and running in a reproducible way.

## 1. Environment Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
```

This installs the package in editable mode along with the development toolchain (pytest, coverage, mypy, ruff).

## 2. Run the Verification Harness

```bash
test.bat
```

`test.bat` executes:

1. `python -m pytest` – full unit test suite (data layer, engine, portfolio, strategy API, metrics).
2. Example scripts – quickstart, walk-forward, and grid-search demos that populate `examples/output/`.
3. Engine diagnostics – validates metadata checkpoints in `artifacts/` and runs the metrics analyzer CLI.
4. Profiler – records `profile.txt` and folds hotspots into `report.txt`.

Inspect `report.txt` and `profile.txt` before committing changes.

## 3. Explore the Examples

```bash
python examples/quickstart_example.py --test-mode --run-id demo
python examples/walk_forward_example.py --window 3 --bars 9 --run-id wf-demo
python examples/grid_search_example.py --weights 0.1 0.3 0.5 --run-id grid-demo
python examples/aapl_momentum_strategy.py --lookback 5 --threshold 0.01 --run-id aapl-demo
```

Each command emits JSON summaries into `examples/output/` and writes engine metadata under `artifacts/<run_id>/`.

The AAPL momentum script showcases `DataSettings`, which wires the cache + provider chain (local CSV fixtures first, Yahoo Finance as fallback). Reuse `DataSettings.defaults(cache_dir, data_dir)` in your own scripts for consistent data plumbing.

## 4. Analyze Metrics

After a grid search run, inspect metrics:

```bash
python -m quantbacktest.metrics.cli --metadata artifacts/grid-demo/metadata.json
```

This produces `metrics.json` alongside the metadata file with cumulative return, drawdown, Sharpe/Sortino, and segment counts.

## 5. Next Steps

- Read `docs/strategies.md` to design deterministic strategies.
- Consult `docs/data.md` for provider and cache configuration.
- Review `docs/metrics.md` to integrate metrics into CI or research notebooks.
- Use `docs/examples.md` as a cheat sheet for all example scripts and expected outputs.
