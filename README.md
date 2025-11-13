# quantbacktest

quantbacktest is a production-oriented Python research stack for designing and validating quantitative trading strategies. The project emphasizes reproducibility, multi-provider data access, overfitting safeguards, and extensible architecture so institutional workflows can evolve without rewriting the foundation.

## Vision & Capabilities

- **Deterministic research** – centralized configuration, seed control, and metadata logging for every run.
- **Modular engine** – event-driven core with clean separation of data, strategies, portfolio, metrics, and reporting layers.
- **Multi-provider data** – cache-first fetchers with Yahoo Finance fallback (additional providers coming in later steps).
- **Safety rails** – walk-forward harness, Monte Carlo stress, and diagnostics to highlight over-optimization.
- **Tooling first** – `test.bat` orchestrates tests, smoke examples, profiling, and produces a human-readable report.

## Repository Layout

```
quantbacktest/
├─ quantbacktest/          # Python package
│  ├─ data/                # Providers, caches, validation
│  ├─ core/                # Events, queues, execution glue
│  ├─ portfolio/           # Accounting, exposures, risk
│  ├─ strategy/            # Strategy interfaces and helpers
│  ├─ engine/              # Backtest runners, modes, simulations
│  ├─ metrics/             # Performance analytics
│  └─ utils/               # Logging, profiling, paths, determinism
├─ tests/                  # Pytest suite + offline fixtures
├─ docs/                   # Architecture notes and tutorials
├─ examples/               # Ready-to-run research snippets
├─ bloat/                  # Parking area for deprecated assets
└─ test.bat                # Unified verification + profiling harness
```

## Development Workflow

1. Run `test.bat` before and after every change. Inspect the generated `report.txt` to confirm profiling and warnings.
2. Keep all data interactions inside the `data` module and respect cache-first, provider-second semantics.
3. Never delete files; move unused artifacts into `bloat/` with an explanatory note.
4. Document new modules in `docs/` and keep the README synchronized with current capabilities.
5. Generate synthetic fixtures via `python scripts/generate_synthetic_data.py` if `tests/data/` is empty.
6. Before publishing/pushing, remove generated artifacts (`artifacts/`, `cache/`, `.pytest_cache/`, `examples/output/`, `profile.txt`, `report.txt`) or run `git clean -fdX` to ensure the repo tree is clean.

## Getting Started (preview)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
test.bat
```

The roadmap in the user instructions drives development through nine gated steps. We are currently implementing **Step 1 — Project Skeleton**; later steps will layer in the full data stack, portfolio engine, metrics, documentation, and example strategies.
