from dataclasses import dataclass, field
from pathlib import Path

from omegaconf import MISSING


@dataclass
class ExploreVAE:
    checkpoint: Path = MISSING
    num_samples: int = 5
    range_start: int = -3
    range_end: int = 3
    wandb_name: str | None = None


@dataclass
class Visualization:
    explore_vae: ExploreVAE = field(default_factory=ExploreVAE)
