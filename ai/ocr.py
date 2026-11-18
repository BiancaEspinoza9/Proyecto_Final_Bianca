"""Paso 0: de una CAPTURA de la pantalla "Movimientos" de Yape a movimientos.

Document AI / OCR (sesion 10). Corre 100 % en el computador (RapidOCR, ONNX):
la captura no sale de ahi, no hay clave de API ni costo.

Como es la pantalla real: cada fila tiene el nombre arriba a la izquierda, la fecha
y hora abajo (a veces con una nota), y el monto a la derecha. Rojo con "-" = enviaste.
El OCR a veces pierde los espacios ("Ayer1:52pm"), por eso las regex son tolerantes.
"""
from __future__ import annotations

import re
from datetime import date, timedelta

from .parser import SIN_NOMBRE, Movimiento

MESES = {"ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6, "jul": 7,
         "ago": 8, "set": 9, "sep": 9, "oct": 10, "nov": 11, "dic": 12}

MONTO = re.compile(r"^([-–—−])?\s*S\s*/\s*([\d.,]+)$")
FECHA_REL = re.compile(r"^(ayer|hoy)\s*(\d{1,2}):(\d{2})\s*([ap])\.?\s*m\.?\s*-?\s*(.*)$", re.I)
FECHA_ABS = re.compile(
    r"^(\d{1,2})\s*([a-z]{3,4})\.?\s*(\d{4})\s*-?\s*(\d{1,2}):(\d{2})\s*([ap])\.?\s*m\.?\s*-?\s*(.*)$", re.I)

_motor = None


def _hora24(h: str, m: str, ap: str) -> str:
    h_ = int(h)
    if ap.lower() == "p" and h_ < 12:
        h_ += 12
    if ap.lower() == "a" and h_ == 12:
        h_ = 0
    return f"{h_:02d}:{m}"


def _fecha(texto: str, hoy: date):
    """Devuelve (fecha 'DD/MM/AAAA', hora 'HH:MM', nota) o None si no es una linea de fecha."""
    t = texto.strip()
    m = FECHA_REL.match(t)
    if m:
        palabra, h, mi, ap, nota = m.groups()
        dia = hoy - timedelta(days=1) if palabra.lower() == "ayer" else hoy
        return dia.strftime("%d/%m/%Y"), _hora24(h, mi, ap), nota.strip()
    m = FECHA_ABS.match(t)
    if m:
        d, mes, anio, h, mi, ap, nota = m.groups()
        n_mes = MESES.get(mes.lower())
        if n_mes:
            return f"{int(d):02d}/{n_mes:02d}/{anio}", _hora24(h, mi, ap), nota.strip()
    return None


def parsear_items(items: list[tuple[float, float, str]], hoy: date | None = None
                  ) -> tuple[list[Movimiento], list[str]]:
    """items = [(x, y, texto)] tal como los entrega el OCR. Agrupa por filas."""
    hoy = hoy or date.today()
    if not items:
        return [], []
    corte_x = 0.5 * max(x for x, _, _ in items)  # montos a la derecha, nombres/fechas a la izquierda
    montos = sorted(((x, y, t) for x, y, t in items if x >= corte_x and MONTO.match(t.strip())),
                    key=lambda i: i[1])
    izquierda = [(x, y, t) for x, y, t in items if x < corte_x]

    movs: list[Movimiento] = []
    no_leidas: list[str] = []
    for _, ay, atexto in montos:
        signo, num = MONTO.match(atexto.strip()).groups()
        # la fecha esta justo debajo del monto (mas o menos 22 px)
        candidatas = [(abs(y - (ay + 22)), t) for _, y, t in izquierda
                      if ay - 10 <= y <= ay + 60 and _fecha(t, hoy)]
        if not candidatas:
            no_leidas.append(atexto)
            continue
        ftxt = min(candidatas)[1]
        fecha, hora, nota = _fecha(ftxt, hoy)
        nombre = " ".join(t.strip() for _, y, t in izquierda
                          if ay - 70 <= y <= ay + 5 and not _fecha(t, hoy)).strip() or SIN_NOMBRE
        movs.append(Movimiento(fecha, hora, "enviado" if signo else "recibido", nombre,
                               float(num.replace(",", "")), nota))
    return movs, no_leidas


def leer_captura(imagen: bytes | str) -> list[tuple[float, float, str]]:
    """Corre el OCR local. La primera vez tarda unos segundos en cargar el modelo."""
    global _motor
    if _motor is None:
        from rapidocr_onnxruntime import RapidOCR  # import perezoso: la app funciona sin OCR
        _motor = RapidOCR()
    resultado, _ = _motor(imagen)
    items = []
    for caja, texto, conf in resultado or []:
        if float(conf) < 0.4:
            continue
        xs = [p[0] for p in caja]
        ys = [p[1] for p in caja]
        items.append((min(xs), sum(ys) / len(ys), texto))
    return items


def parse_captura(imagen: bytes | str, hoy: date | None = None) -> tuple[list[Movimiento], list[str]]:
    return parsear_items(leer_captura(imagen), hoy)
