"""Paso 3: reporte del negocio, sin lo personal ni lo dudoso."""
from __future__ import annotations

import pandas as pd


def a_dataframe(filas: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(filas)
    if df.empty:
        return df
    df["fecha_dt"] = pd.to_datetime(df["fecha"], format="%d/%m/%Y")
    return df


def resumen(df: pd.DataFrame) -> dict:
    if df.empty:
        return dict(ventas=0.0, gastos=0.0, utilidad=0.0, personal=0.0, dudosos=0, movimientos=0)
    ventas = df.loc[df.categoria == "venta", "monto"].sum()
    gastos = df.loc[df.categoria == "gasto_negocio", "monto"].sum()
    return dict(
        ventas=round(float(ventas), 2),
        gastos=round(float(gastos), 2),
        utilidad=round(float(ventas - gastos), 2),
        personal=round(float(df.loc[df.categoria == "personal", "monto"].sum()), 2),
        dudosos=int((df.categoria == "dudoso").sum()),
        movimientos=len(df),
    )


def por_dia(df: pd.DataFrame) -> pd.DataFrame:
    """Ventas y gastos del negocio por dia (para el grafico)."""
    if df.empty:
        return pd.DataFrame()
    neg = df[df.categoria.isin(["venta", "gasto_negocio"])]
    tabla = neg.pivot_table(index="fecha_dt", columns="categoria", values="monto", aggfunc="sum", fill_value=0)
    return tabla
