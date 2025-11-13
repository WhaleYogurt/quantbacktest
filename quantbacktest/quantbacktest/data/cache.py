from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import pandas as pd

@dataclass(slots=True)
class LocalDataCache:
    """
    Minimal cache implementation storing normalized JSON payloads on disk.

    Later steps will extend this to store parquet/feather data and perform
    schema checks. For the skeleton we focus on deterministic read/write and
    easy dependency injection for tests.
    """

    root: Path
    serializer: Callable[[Dict[str, Any]], str] = json.dumps
    deserializer: Callable[[str], Dict[str, Any]] = json.loads
    frame_suffix: str = "csv"
    frames_dir: Path = field(init=False)

    def __post_init__(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.frames_dir = self.root / "frames"
        self.frames_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, key: str) -> Path:
        if not key:
            raise ValueError("cache key must be non-empty")
        safe_key = key.replace("/", "_")
        return self.root / f"{safe_key}.json"

    def _frame_path_for(self, key: str) -> Path:
        safe_key = key.replace("/", "_")
        return self.frames_dir / f"{safe_key}.{self.frame_suffix}"

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Return cached data if present."""
        path = self._path_for(key)
        if not path.exists():
            return None
        return self.deserializer(path.read_text(encoding="utf-8"))

    def set(self, key: str, payload: Dict[str, Any]) -> None:
        """Persist normalized data to disk."""
        path = self._path_for(key)
        path.write_text(self.serializer(payload), encoding="utf-8")

    def clear(self) -> None:
        """Remove all cached items."""
        for child in self.root.glob("*.json"):
            child.unlink(missing_ok=True)
        for child in self.frames_dir.glob(f"*.{self.frame_suffix}"):
            child.unlink(missing_ok=True)

    # --- DataFrame helpers -------------------------------------------------
    def load_frame(self, key: str) -> Optional[pd.DataFrame]:
        path = self._frame_path_for(key)
        if not path.exists():
            return None
        return pd.read_csv(path, parse_dates=["timestamp"])

    def store_frame(self, key: str, frame: pd.DataFrame) -> None:
        path = self._frame_path_for(key)
        frame.to_csv(path, index=False)
