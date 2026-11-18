"""Datos FICTICIOS para completar el demo.

Una captura de Yape trae pocos dias; con estos datos inventados (bodega 'Don Lucho',
12/10 al 10/11 de 2026) el reporte y el grafico se ven completos. Cada movimiento queda
marcado con origen="ficticio" para que la app avise que no son reales.
"""
from __future__ import annotations

from pathlib import Path

from .parser import Movimiento, parse_rules

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample_movimientos.txt"


def historial_ficticio() -> list[Movimiento]:
    if not SAMPLE.exists():
        return []
    movs, _ = parse_rules(SAMPLE.read_text(encoding="utf-8"))
    for m in movs:
        m.origen = "ficticio"
    return movs


def completar(movs: list[Movimiento]) -> list[Movimiento]:
    """Pone el historial ficticio antes de los movimientos reales."""
    return historial_ficticio() + movs
