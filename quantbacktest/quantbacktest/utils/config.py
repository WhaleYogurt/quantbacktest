from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class ProjectPaths:
    root: Path
    cache_dir: Path = field(init=False)
    artifacts_dir: Path = field(init=False)

    def __post_init__(self) -> None:
        self.cache_dir = self.root / "cache"
        self.artifacts_dir = self.root / "artifacts"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)


@dataclass(slots=True)
class Settings:
    """
    Global configuration object.

    Intended to hold file-system layout references and deterministic seeds.
    """

    project_paths: ProjectPaths
    seed: int = 42

    @classmethod
    def from_root(cls, root: Path, seed: int = 42) -> "Settings":
        return cls(project_paths=ProjectPaths(root=root), seed=seed)
