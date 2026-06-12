"""Limpieza operativa best-effort de objetos sensibles."""

from __future__ import annotations

import gc
import logging
from typing import Iterable

import numpy as np

logger = logging.getLogger(__name__)


def wipe_numpy_arrays(arrays: Iterable[np.ndarray | None]) -> None:
    """Sobrescribe arreglos NumPy mutables cuando es posible."""
    for array in arrays:
        if array is None:
            continue
        try:
            if isinstance(array, np.ndarray) and array.flags.writeable:
                array.fill(0)
        except Exception as exc:  # noqa: BLE001
            logger.debug("No fue posible sobrescribir un arreglo NumPy: %s", exc)


def collect_garbage() -> None:
    """Solicita recolección de basura como medida complementaria."""
    collected = gc.collect()
    logger.debug("Garbage Collector ejecutado. Objetos recolectados: %s", collected)
