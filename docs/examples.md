# Examples & Tutorials

## Quickstart

```
python examples/quickstart_example.py --test-mode --run-id demo
```

Generates `examples/output/quickstart.json` and metadata in `artifacts/demo/`.

## Walk-Forward

```
python examples/walk_forward_example.py --window 3 --bars 9 --run-id wf-demo
```

Produces `examples/output/walk_forward.json` and `artifacts/wf-demo/metadata.json`. The metadata contains per-segment summaries which feed the metrics analyzer (`python -m quantbacktest.metrics.cli --metadata artifacts/wf-demo/metadata.json`).

## Grid Search

```
python examples/grid_search_example.py --weights 0.1 0.3 0.5 --run-id grid-demo
```

Writes `examples/output/grid_search.json` and `artifacts/grid-demo/metrics.json`.

## AAPL Momentum Strategy

```
python examples/aapl_momentum_strategy.py --lookback 5 --threshold 0.01 --run-id aapl-demo
```

Uses `DataSettings.defaults()` to combine local CSV fixtures with Yahoo Finance fallback, then runs `AAPLMomentumStrategy`. Outputs: `examples/output/aapl_momentum.json` and metrics under `artifacts/aapl-demo/`.

## Mean Reversion Strategy

```
python examples/mean_reversion_strategy.py --lookback 8 --threshold 0.5 --run-id meanrev-demo
```

Demonstrates `MeanReversionStrategy` (contrarian signals). Outputs `examples/output/mean_reversion.json`.

All of the above scripts run automatically via `test.bat`, which also validates metadata and metrics to ensure the examples stay healthy.

## Additional Resources

- `docs/quickstart.md` – overall setup instructions.
- `docs/strategies.md` – how to build custom strategies (see references to momentum/mean-reversion templates).
- `docs/data.md` – details on configuring `DataSettings`.
- `docs/metrics.md` – analyzer usage and report schema.
