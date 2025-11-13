# Examples Overview

| Script | Description | Output |
|--------|-------------|--------|
| `quickstart_example.py` | Minimal backtest using the placeholder strategy (single segment). | `examples/output/quickstart.json` |
| `walk_forward_example.py` | Demonstrates `EngineMode.WALK_FORWARD` with configurable window size and bars. | `examples/output/walk_forward.json` + `artifacts/<run_id>/metadata.json` |
| `grid_search_example.py` | Runs a small parameter sweep via `EngineMode.GRID_SEARCH`. | `examples/output/grid_search.json` + `artifacts/<run_id>/metadata.json` |
| `aapl_momentum_strategy.py` | Executes the `AAPLMomentumStrategy` over offline AAPL data via the data manager. | `examples/output/aapl_momentum.json` + metrics in `artifacts/<run_id>/metrics.json` |
| `mean_reversion_strategy.py` | Runs the `MeanReversionStrategy` on synthetic MSFT data to show contrarian behavior. | `examples/output/mean_reversion.json` + `artifacts/<run_id>/metrics.json` |

Run them individually or via `test.bat`, which executes all three and records results in `report.txt`.
