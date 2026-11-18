"""Paso 1: del texto del historial de Yape a movimientos estructurados.

Dos caminos:
- reglas (regex): rapido, gratis y predecible, para el formato conocido.
- LLM con salida estructurada (sesion 08): para lineas que las reglas no entienden.

Verificacion literal: lo que devuelve el LLM solo se acepta si la contraparte
aparece textualmente en la linea de origen (el LLM no puede inventar personas).
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass

LINE = re.compile(
    r"^\s*(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})\s*\|\s*(recibido|enviado)\s*\|\s*(.+?)\s*"
    r"\|\s*S/\s*([\d.,]+)\s*(?:\|\s*(.*?))?\s*$",
    re.IGNORECASE,
)

LLM_MODEL = "claude-haiku-5-5"

# Cuando el nombre no es legible (o fue tapado por privacidad en la captura)
SIN_NOMBRE = "(sin nombre)"

TOOL = {
    "name": "registrar_movimientos",
    "description": "Registra los movimientos de Yape/Plin encontrados en el texto.",
    "input_schema": {
        "type": "object",
        "properties": {
            "movimientos": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "fecha": {"type": "string", "description": "DD/MM/AAAA"},
                        "hora": {"type": "string", "description": "HH:MM"},
                        "tipo": {"type": "string", "enum": ["recibido", "enviado"]},
                        "contraparte": {"type": "string"},
                        "monto": {"type": "number", "description": "Soles, positivo"},
                        "nota": {"type": "string"},
                    },
                    "required": ["fecha", "hora", "tipo", "contraparte", "monto"],
                },
            }
        },
        "required": ["movimientos"],
    },
}


@dataclass
class Movimiento:
    fecha: str
    hora: str
    tipo: str  # "recibido" | "enviado"
    contraparte: str
    monto: float
    nota: str = ""


def _monto(texto: str) -> float:
    return float(texto.replace(",", ""))


def parse_rules(text: str) -> tuple[list[Movimiento], list[str]]:
    """Devuelve (movimientos leidos, lineas que las reglas no entendieron)."""
    movs: list[Movimiento] = []
    pendientes: list[str] = []
    for linea in text.splitlines():
        if not linea.strip() or linea.lstrip().startswith("#"):
            continue
        m = LINE.match(linea)
        if not m:
            pendientes.append(linea)
            continue
        fecha, hora, tipo, contra, monto, nota = m.groups()
        movs.append(Movimiento(fecha, hora, tipo.lower(), contra.strip(), _monto(monto), (nota or "").strip()))
    return movs, pendientes


def parse_llm(lineas: list[str]) -> list[Movimiento]:
    """Usa un LLM con salida estructurada y verifica cada resultado contra el texto."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or not lineas:
        return []
    import anthropic  # import perezoso: la app funciona sin esta libreria

    client = anthropic.Anthropic(api_key=api_key)
    texto = "\n".join(lineas)
    resp = client.messages.create(
        model=LLM_MODEL,
        max_tokens=2000,
        tools=[TOOL],
        tool_choice={"type": "tool", "name": "registrar_movimientos"},
        messages=[{
            "role": "user",
            "content": "Extrae SOLO los movimientos que aparecen en este historial. "
                       "No inventes nombres ni montos.\n\n" + texto,
        }],
    )
    salida: list[Movimiento] = []
    for bloque in resp.content:
        if bloque.type != "tool_use":
            continue
        for d in bloque.input.get("movimientos", []):
            if d["contraparte"].lower() not in texto.lower():  # verificacion literal
                continue
            salida.append(Movimiento(d["fecha"], d["hora"], d["tipo"], d["contraparte"],
                                     float(d["monto"]), d.get("nota", "")))
    return salida


def parse(text: str, use_llm: bool = False) -> tuple[list[Movimiento], list[str]]:
    """Reglas primero; el LLM solo toma lo que las reglas no entendieron."""
    movs, pendientes = parse_rules(text)
    if use_llm and pendientes:
        extra = parse_llm(pendientes)
        movs.extend(extra)
        pendientes = [] if extra else pendientes
    return movs, pendientes
