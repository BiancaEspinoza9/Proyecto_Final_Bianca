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


def test_resumen_excluye_personal_y_dudoso():
    movs, _ = parse_rules(TXT)
    r = resumen(a_dataframe(clasificar(movs)))
    assert r["ventas"] == 6.5 and r["gastos"] == 1250.0 and r["personal"] == 100.0 and r["dudosos"] == 1
