from __future__ import annotations

import json
import time
from dataclasses import dataclass
from itertools import count
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Literal, cast

from ..core.events import FillEvent, MarketEvent, OrderEvent, SignalEvent
from ..core.execution import ExecutionConfig, SimulatedExecutionHandler
from ..core.queue import EventQueue
from ..portfolio import PortfolioState
from ..strategy.base import Strategy
from ..strategy.context import StrategyContext
from ..strategy.indicators import IndicatorCache
from ..utils.logging import get_logger
from ..utils.random import DeterministicRandom
from .context import EngineContext
from .modes import EngineMode, EngineResult, EngineSegmentResult, SegmentPlan
from ..metrics.report import build_metrics_report
from .scheduler import RunScheduler


@dataclass(slots=True)
class BacktestSettings:
    run_id: str = "skeleton"
    output_dir: Path = Path("artifacts")
    deterministic_seed: int = 42
    initial_cash: float = 1_000_000.0
    mode: EngineMode = EngineMode.STANDARD
    walk_forward_window: int = 0
    grid_parameters: Sequence[Dict[str, float]] | None = None
    enable_progress: bool = True
    enable_checkpointing: bool = True


class BacktestRunner:
    def __init__(
        self,
        strategy: Strategy,
        settings: BacktestSettings | None = None,
        execution_handler: SimulatedExecutionHandler | None = None,
    ) -> None:
        self.strategy = strategy
        self.settings = settings or BacktestSettings()
        self.execution_handler = execution_handler or SimulatedExecutionHandler(ExecutionConfig())
        self.logger = get_logger(self.__class__.__name__)
        self._order_counter = count(1)
        self.portfolio: Optional[PortfolioState] = None
        self.last_snapshot: Optional[dict[str, float]] = None
        self.strategy_context: Optional[StrategyContext] = None
        self.output_dir = self.settings.output_dir / self.settings.run_id
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self, market_events: Iterable[MarketEvent]) -> EngineResult:
        context = EngineContext(
            portfolio=PortfolioState(base_currency="USD", starting_cash=self.settings.initial_cash),
            run_id=self.settings.run_id,
            output_dir=self.output_dir,
            randomizer=DeterministicRandom(seed=self.settings.deterministic_seed),
        )
        scheduler = RunScheduler(
            mode=self.settings.mode,
            walk_forward_window=self.settings.walk_forward_window,
            grid_parameters=self.settings.grid_parameters,
        )
        plans = scheduler.plan(market_events)
        if not plans:
            raise ValueError("No market events supplied to BacktestRunner.")

        metadata_path = self.output_dir / "metadata.json"
        segment_results: List[EngineSegmentResult] = []
        status = "completed"

        try:
            for idx, plan in enumerate(plans, 1):
                if self.settings.enable_progress:
                    self.logger.info("run %s segment %s (%d/%d)", self.settings.run_id, plan.segment_id, idx, len(plans))
                self._prepare_strategy_context(context.portfolio, plan)
                self._apply_parameters(plan.parameters)
                result = self._execute_segment(plan, context.portfolio)
                segment_results.append(result)
                if self.settings.enable_checkpointing:
                    self._write_metadata(metadata_path, segment_results, status="in_progress")
        except Exception as exc:  # pragma: no cover - crash path
            status = "crashed"
            self._write_metadata(metadata_path, segment_results, status=status, error=str(exc))
            raise

        self.last_snapshot = context.portfolio.snapshot()
        self.portfolio = context.portfolio
        self._write_metadata(metadata_path, segment_results, status=status)
        build_metrics_report(
            EngineResult(
                run_id=self.settings.run_id,
                mode=self.settings.mode,
                segments=segment_results,
                metadata_path=str(metadata_path),
                status=status,
            ),
            self.output_dir,
        )
        return EngineResult(
            run_id=self.settings.run_id,
            mode=self.settings.mode,
            segments=segment_results,
            metadata_path=str(metadata_path),
            status=status,
        )

    # --- internal helpers -------------------------------------------------
    def _execute_segment(self, plan: SegmentPlan, portfolio: PortfolioState) -> EngineSegmentResult:
        start = time.time()
        queue = EventQueue()
        fills: List[FillEvent] = []
        latest_market: dict[str, MarketEvent] = {}

        for market_event in plan.events:
            queue.put(market_event)

        while len(queue):
            qitem = queue.get()
            if qitem is None:
                continue
            if isinstance(qitem, MarketEvent):
                portfolio.mark_price(qitem.symbol, qitem.price)
                latest_market[qitem.symbol] = qitem
                for signal in self.strategy.on_market_data(qitem):
                    order = self._signal_to_order(signal)
                    queue.put(order)
            elif isinstance(qitem, OrderEvent):
                market_snapshot = latest_market.get(qitem.symbol)
                if market_snapshot is None:
                    continue
                fill_list = self.execution_handler.execute(qitem, market_snapshot)
                for fill in fill_list:
                    portfolio.apply_fill(fill)
                    fills.append(fill)

        snapshot = portfolio.snapshot()
        duration_ms = (time.time() - start) * 1000.0
        return EngineSegmentResult(
            segment_id=plan.segment_id,
            fills=fills,
            portfolio_snapshot=snapshot,
            parameters=plan.parameters,
            duration_ms=duration_ms,
        )

    def _signal_to_order(self, signal: SignalEvent) -> OrderEvent:
        direction_str = "BUY" if signal.direction.upper() == "LONG" else "SELL"
        direction = cast(Literal["BUY", "SELL"], direction_str)
        quantity = max(1, int(abs(signal.strength) * 100))
        order_id = f"ord-{next(self._order_counter)}"
        return OrderEvent(
            order_id=order_id,
            symbol=signal.symbol,
            quantity=quantity,
            direction=direction,
            order_type="MARKET",
            signal_id=signal.signal_id,
            timestamp=signal.timestamp,
        )

    def _write_metadata(
        self,
        path: Path,
        segments: List[EngineSegmentResult],
        status: str,
        error: Optional[str] = None,
    ) -> None:
        payload = {
            "run_id": self.settings.run_id,
            "mode": self.settings.mode.value,
            "status": status,
            "segments": [
                {
                    "segment_id": segment.segment_id,
                    "fill_count": segment.fill_count,
                    "duration_ms": segment.duration_ms,
                    "parameters": segment.parameters,
                    "portfolio": segment.portfolio_snapshot,
                }
                for segment in segments
            ],
            "timestamp": time.time(),
        }
        if error:
            payload["error"] = error
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _apply_parameters(self, parameters: Optional[Dict[str, float]]) -> None:
        if not parameters:
            return
        configure = getattr(self.strategy, "configure", None)
        if callable(configure):
            configure(parameters)
            return
        for key, value in parameters.items():
            setattr(self.strategy, key, value)

    def _prepare_strategy_context(self, portfolio: PortfolioState, plan: SegmentPlan) -> None:
        indicator_cache = IndicatorCache()
        metadata = {
            "run_id": self.settings.run_id,
            "segment_id": plan.segment_id,
            "mode": self.settings.mode.value,
        }
        if plan.metadata:
            metadata.update(plan.metadata)

        context = StrategyContext(
            name=getattr(self.strategy, "name", self.strategy.__class__.__name__),
            portfolio=portfolio,
            indicator_cache=indicator_cache,
            random_seed=self.settings.deterministic_seed,
            metadata=metadata,
        )
        setter = getattr(self.strategy, "set_context", None)
        if callable(setter):
            setter(context)
        initializer = getattr(self.strategy, "initialize_segment", None)
        if callable(initializer):
            initializer(plan.segment_id, metadata)
        self.strategy_context = context
