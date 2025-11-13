# Strategy Development Guide

## Lifecycle

1. **Initialization** – Instantiate your strategy (subclass `BaseStrategy`) with parameters such as `warmup_bars`, `max_signal_strength`, and `min_signal_interval`.
2. **Context attachment** – The engine calls `set_context()` before each segment, providing `StrategyContext` with:
   - `portfolio`: read-only snapshot for exposure checks.
   - `indicator_cache`: per-strategy cache for deterministic indicator reuse.
   - `metadata`: segment IDs, run_id, mode, etc.
3. **Warm-up** – `on_warmup()` receives `MarketEvent`s until `warmup_bars` is satisfied. Compute indicators and seed state here.
4. **Signal generation** – Implement `generate_signals()` to yield `SignalEvent`s; `BaseStrategy.on_market_data()` handles throttling, clamping, and metadata.
5. **Segment reset** – Override `initialize_segment()` to clear state between walk-forward/grid-search segments.

## Best Practices

- **Determinism** – Avoid randomness; if necessary, use `StrategyContext.random_seed`.
- **Indicator cache** – Store expensive computations via `indicator_cache.set(name, key, value)` to guarantee reuse across ticks; helper functions such as `simple_moving_average`, `exponential_moving_average`, and `relative_strength_index` live in `strategy.indicators`.
- **Risk checks** – Consult `self.portfolio.snapshot()` before emitting signals to avoid breaches.
- **Throttling** – Use `min_signal_interval` to prevent over-trading on noisy data.
- **Subscriptions** – Call `self.subscribe("AAPL", "MSFT")` to ignore unrelated symbols.
- **Registry** – Register reusable strategies with `strategy.register_strategy("name", factory)` so CLI tools and plugins can instantiate them dynamically (`available_strategies()` lists everything).

## Example Skeleton

```python
from quantbacktest.strategy.base import BaseStrategy
from quantbacktest.core.events import MarketEvent, SignalEvent

class SimpleMomentum(BaseStrategy):
    def __init__(self, lookback: int = 10):
        super().__init__(name="momentum", warmup_bars=lookback)
        self.lookback = lookback
        self.history = {}

    def on_warmup(self, event: MarketEvent) -> None:
        self.history.setdefault(event.symbol, []).append(event.price)

    def generate_signals(self, event: MarketEvent):
        prices = self.history.setdefault(event.symbol, [])
        prices.append(event.price)
        if len(prices) < self.lookback:
            return []
        momentum = prices[-1] / prices[-self.lookback] - 1.0
        direction = "LONG" if momentum > 0 else "SHORT"
        yield self.create_signal(event.symbol, strength=abs(momentum), direction=direction, event=event)
```

For a contrarian template, see `MeanReversionStrategy`, which uses moving averages and standard deviations to emit SHORT signals when price trades far above its mean (and LONG when below).
