"""Paso 2: separar lo del negocio de lo personal.

Categorias: venta | gasto_negocio | personal | dudoso
Regla de oro: si no estamos seguros, marcamos "dudoso" y se lo preguntamos al
comerciante. El sistema recuerda su respuesta por contraparte.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict

from .parser import SIN_NOMBRE, Movimiento


def clave_label(m: Movimiento) -> tuple[str, str]:
    """Con que clave se recuerda la respuesta del usuario.
    Por persona; pero si no hay nombre, solo para ese movimiento (no mezclar a desconocidos)."""
    if m.contraparte == SIN_NOMBRE:
        return (m.tipo, f"{SIN_NOMBRE} {m.fecha} {m.hora}")
    return (m.tipo, m.contraparte.lower())


KW_VENTA = ("pan", "almuerzo", "menu", "menú", "gaseosa", "pollo", "pedido", "venta", "pago",
            "huevos", "arroz", "aceite", "leche", "cafe", "café", "torta", "delivery")
KW_GASTO = ("proveedor", "mercaderia", "mercadería", "distribuidora", "alquiler local",
            "luz local", "agua local", "insumos", "bolsas", "gas")
KW_PERSONAL = ("mama", "mamá", "papa", "papá", "hermano", "hermana", "regalo", "cine",
               "uber", "cumple", "prestamo", "préstamo", "salida", "chifa personal")

CATEGORIAS = ["venta", "gasto_negocio", "personal"]


def _tiene(nota: str, palabras: tuple[str, ...]) -> bool:
    n = nota.lower()
    return any(p in n for p in palabras)


def clasificar(movs: list[Movimiento], labels: dict | None = None,
              familia: set[str] | None = None) -> list[dict]:
    """labels: {(tipo, contraparte_en_minusculas): categoria} que el usuario ya confirmo.
    familia: nombres (en minusculas) que el usuario dijo que NO son del negocio."""
    labels = labels or {}
    familia = familia or set()
    recibidos = Counter(m.contraparte.lower() for m in movs
                        if m.tipo == "recibido" and m.contraparte != SIN_NOMBRE)
    filas: list[dict] = []
    for m in movs:
        clave = clave_label(m)
        if clave in labels:
            cat, motivo = labels[clave], "confirmado por ti antes"
        elif m.contraparte.lower() in familia:
            cat, motivo = "personal", "esta en tu lista de familia"
        elif _tiene(m.nota, KW_PERSONAL):
            cat, motivo = "personal", f"la nota '{m.nota}' parece personal"
        elif m.tipo == "enviado" and _tiene(m.nota, KW_GASTO):
            cat, motivo = "gasto_negocio", f"la nota '{m.nota}' parece un gasto del negocio"
        elif m.tipo == "recibido" and _tiene(m.nota, KW_VENTA):
            cat, motivo = "venta", f"la nota '{m.nota}' parece una venta"
        elif (m.tipo == "recibido" and m.contraparte != SIN_NOMBRE
              and recibidos[m.contraparte.lower()] >= 3 and m.monto <= 60):
            cat, motivo = "venta", "paga seguido montos chicos: parece cliente"
        else:
            cat, motivo = "dudoso", "sin pistas suficientes"
        fila = asdict(m)
        fila.update(categoria=cat, motivo=motivo)
        filas.append(fila)
    return filas
