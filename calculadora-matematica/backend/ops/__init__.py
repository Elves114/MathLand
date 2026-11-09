"""Pacote de operações matemáticas do MathLab."""

from ops import (  # noqa: F401  — importar regista as operações no registry
    algebra,
    arithmetic,
    elliptic,
    finance,
    fractions_ops,
    geometry,
    logarithms,
    matrices,
    numbers,
    percent,
    probability,
    ratio,
    sequences,
    stats,
    trigonometry,
    units,
)
from ops.registry import CATEGORIES, OPERATIONS, sorted_operations  # noqa: F401

__all__ = ["CATEGORIES", "OPERATIONS", "sorted_operations"]
