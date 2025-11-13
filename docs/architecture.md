# Architecture Overview

## Guiding Principles

1. **Determinism before speed** – every module must expose seed control and deterministic behaviors before adding optimizations.
2. **Strict layering** – strategies never pull data directly; everything flows through the data providers and validation layer.
3. **Extensibility** – each package offers clear extension points (e.g., new providers, portfolio models, or metrics).

## Package Responsibilities

| Package        | Responsibility                                                |
| `data`         | Cache-first data retrieval (`DataManager`), provider orchestration, validation |
| `core`         | Event definitions, event queues, and execution handlers        |
| `portfolio`    | Positions, cash, exposure summaries, trade ledger              |
| `strategy`     | Base classes and helper strategies                             |
| `engine`       | Backtest runners, modes, walk-forward, simulations             |
| `metrics`      | Rolling and aggregate performance analytics                    |
| `utils`        | Logging, profiling, configuration, determinism                 |

## Run Lifecycle (Step 1 Skeleton)

1. Data modules (currently offline fixtures) supply normalized market events.
2. `core` events travel through the placeholder `BacktestRunner`.
3. Strategies emit signals captured for diagnostics.
4. Metrics compute lightweight aggregates for smoke validation.

Later steps will flesh out order routing, fills, slippage, multi-provider fallbacks, walk-forward automation, and Monte Carlo tooling.

## Events & Execution (Step 3)

- `core/events.py` now tracks unique identifiers and metadata for signals, orders, and fills so downstream modules can attribute performance correctly.
- `core/execution.py` introduces `ExecutionConfig` and `SimulatedExecutionHandler`, providing deterministic slippage, spread, and commission modeling for both market and limit orders.
- The placeholder `BacktestRunner` consumes `SignalEvent` objects, creates `OrderEvent` instances, and routes them through the execution handler to produce `FillEvent`s—laying the groundwork for the full event loop in later steps.

## Portfolio & Accounting (Step 4)

- `portfolio/state.py` now tracks multi-currency cash balances, margin reserves, realized/unrealized PnL, leverage/exposure summaries, and persists trade logs for auditability.
- Every `FillEvent` now flows through `PortfolioState.apply_fill`, ensuring commissions, cost basis, and trade logs stay in sync with the execution layer.
- The engine continuously marks positions to market using the latest `MarketEvent` prices so snapshots capture deterministic equity curves for later metrics work.

## Strategy API (Step 5)

- `strategy/base.py` defines `BaseStrategy`, adding warm-up enforcement, monotonic timestamp guards, signal clamping, and emission throttling.
- Each strategy receives a `StrategyContext` (portfolio snapshot + `IndicatorCache`) so indicator computations can be shared deterministically across ticks.
- New pytest coverage (`tests/test_strategy_api.py`) exercises warm-up logic, throttling, and indicator caching helpers to keep strategy regressions visible.

## Engine Core (Step 6)

- `engine/base.py` now orchestrates multi-segment runs, writing checkpoint metadata and supporting standard, walk-forward, and grid-search modes.
- `RunScheduler` (`engine/scheduler.py`) deterministically chunks market data into segments, while `EngineMode` (`engine/modes.py`) captures runtime intent.
- Each segment produces an `EngineSegmentResult` persisted via `metadata.json`, enabling crash-safe resumes and future multi-run analytics.

## Documentation & Examples (Step 8)

- `docs/quickstart.md` provides end-to-end setup instructions, including how to interpret `test.bat` artifacts.
- `docs/data.md`, `docs/strategies.md`, and `docs/metrics.md` dive deeper into the respective subsystems so contributors have a single source of truth.
- Examples now include quickstart, walk-forward, and grid-search scripts under `examples/` with JSON outputs in `examples/output/`, making it easy to showcase new features in CI or tutorials.
