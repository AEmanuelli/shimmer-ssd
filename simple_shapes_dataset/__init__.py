import os
from pathlib import Path

import simple_shapes_dataset.cli as cli
import simple_shapes_dataset.text as text
from simple_shapes_dataset.dataset.dataset import SimpleShapesDataset
from simple_shapes_dataset.dataset.domain import (
    AVAILABLE_DOMAINS,
    Attribute,
    RawText,
    SimpleShapesAttributes,
    SimpleShapesImages,
    SimpleShapesRawText,
    SimpleShapesText,
    Text,
)
from simple_shapes_dataset.dataset.domain_alignment import get_aligned_datasets

from .version import __version__

PROJECT_DIR = Path(__file__).resolve().parent.parent
DEBUG_MODE = bool(int(os.getenv("DEBUG", "0")))

__all__ = [
    "cli",
    "text",
    "__version__",
    "SimpleShapesImages",
    "SimpleShapesAttributes",
    "SimpleShapesText",
    "SimpleShapesRawText",
    "SimpleShapesDataset",
    "Attribute",
    "RawText",
    "Text",
    "AVAILABLE_DOMAINS",
    "get_aligned_datasets",
    "PROJECT_DIR",
]
