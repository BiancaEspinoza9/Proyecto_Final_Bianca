import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai.classifier import clasificar
from ai.parser import parse_rules
from ai.report import a_dataframe, resumen

TXT = """# comentario
12/10/2026 08:15 | recibido | Rosa Quispe | S/ 6.50 | pan
12/10/2026 06:30 | enviado | Distribuidora Andina | S/ 1,250.00 | mercaderia
12/10/2026 21:00 | recibido | Teresa Diaz | S/ 100.00 | para el cine
12/10/2026 17:10 | recibido | Diego Alarcon | S/ 45.00 |
linea rota que no se entiende
"""


def test_parse_lee_montos_y_separa_pendientes():
    movs, pend = parse_rules(TXT)
    assert len(movs) == 4 and len(pend) == 1
    assert movs[1].monto == 1250.0


def test_clasifica_por_nota_y_deja_dudoso():
    movs, _ = parse_rules(TXT)
    cats = [f["categoria"] for f in clasificar(movs)]
    assert cats == ["venta", "gasto_negocio", "personal", "dudoso"]


def test_confirmacion_del_usuario_se_recuerda():
    movs, _ = parse_rules(TXT)
    labels = {("recibido", "diego alarcon"): "venta"}
    filas = clasificar(movs, labels)
    assert filas[3]["categoria"] == "venta"


def test_ocr_agrupa_filas_de_una_captura_real():
    """Items (x, y, texto) tal como los devolvio el OCR sobre una captura real de Yape
    (con los nombres tapados). Nota: el OCR pierde espacios: 'Ayer1:52pm', '-S/255.00'."""
    from datetime import date

    from ai.ocr import parsear_items
    from ai.parser import SIN_NOMBRE

    items = [
        (244, 150, "Movimientos"),
        (584, 290, "- S/ 34.00"), (27, 312, "Ayer 2:24 pm"),
        (571, 528, "-S/255.00"), (25, 549, "Ayer1:29pm"),
        (586, 647, "S/ 200.00"), (26, 668, "Ayer1:19pm"),
        (601, 884, "S/ 65.00"), (27, 904, "15 nov.2026-11:53am"),
        (585, 1122, "S/ 200.00"), (26, 1142, "14nov.2026-2:14pm-RecibisteunPLIN"),
        (22, 1456, "******348"), (601, 1478, "- S/ 5.00"), (27, 1499, "13nov.2026-9:47am"),
    ]
    movs, sin_leer = parsear_items(items, hoy=date(2026, 11, 17))
    assert not sin_leer and len(movs) == 6
    m = {(x.fecha, x.hora): x for x in movs}
    assert m[("16/11/2026", "14:24")].tipo == "enviado" and m[("16/11/2026", "14:24")].monto == 34.0
    assert m[("16/11/2026", "13:19")].tipo == "recibido"          # sin signo = recibido
    assert m[("15/11/2026", "11:53")].hora == "11:53"             # am
    assert m[("14/11/2026", "14:14")].nota.startswith("Recibiste")  # nota despues de la hora
    assert m[("13/11/2026", "09:47")].contraparte == "******348"    # nombre leido
    assert m[("16/11/2026", "14:24")].contraparte == SIN_NOMBRE     # nombre tapado


def test_sin_nombre_no_mezcla_desconocidos():
    from ai.parser import SIN_NOMBRE, Movimiento
    a = Movimiento("16/11/2026", "14:24", "enviado", SIN_NOMBRE, 34.0)
    b = Movimiento("16/11/2026", "13:29", "enviado", SIN_NOMBRE, 255.0)
    filas = clasificar([a, b], {("enviado", f"{SIN_NOMBRE} 16/11/2026 14:24"): "personal"})
    assert filas[0]["categoria"] == "personal" and filas[1]["categoria"] == "dudoso"


def test_resumen_excluye_personal_y_dudoso():
    movs, _ = parse_rules(TXT)
    r = resumen(a_dataframe(clasificar(movs)))
    assert r["ventas"] == 6.5 and r["gastos"] == 1250.0 and r["personal"] == 100.0 and r["dudosos"] == 1
