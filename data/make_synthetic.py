"""Genera un historial SINTETICO de Yape para una bodega inventada.
Todos los nombres son ficticios. Uso: python data/make_synthetic.py
"""
import random
from datetime import date, timedelta
from pathlib import Path

rng = random.Random(2026)

CLIENTES = ["Rosa Quispe", "Carlos Mamani", "Lucia Torres", "Jorge Salas", "Ana Huaman",
            "Pedro Rojas", "Marta Vega", "Luis Cardenas", "Elena Paredes", "Raul Campos",
            "Sofia Medina", "Hugo Valdez", "Nelly Ccori", "Berta Soto", "Walter Quiroz", "Irma Lazo"]
FAMILIA = ["Teresa Diaz", "Mario Diaz", "Karen Diaz"]
PROVEEDORES = ["Distribuidora Andina", "Abarrotes El Sol", "Bebidas Norte"]
NOTAS_VENTA = ["pan", "gaseosa", "huevos", "arroz", "leche", "aceite", "almuerzo", "menu", "pollo",
               "pedido", "cafe", "torta", "", "", ""]
NOTAS_FAMILIA_IN = ["para el cine", "para mama", "para la salida", "prestamo", "para el uber"]
NOTAS_FAMILIA_OUT = ["regalo cumple", "para mama", "cine", "salida con amigos", "uber"]
GASTOS_NEGOCIO = [("Bebidas Norte", "insumos"), ("Ferreteria Sur", "bolsas"), ("Gasera Lima", "gas"),
                  ("Don Teo", "alquiler local"), ("Electro Sur", "luz local")]


def main() -> None:
    lineas = ["# Historial sintetico - Bodega 'Don Lucho' (datos inventados)"]
    inicio = date(2026, 9, 12)
    for d in range(60):
        dia = inicio + timedelta(days=d)
        f = dia.strftime("%d/%m/%Y")
        for _ in range(rng.randint(3, 7)):  # ventas del negocio
            h, mi = rng.randint(7, 20), rng.choice([0, 10, 15, 25, 40, 55])
            lineas.append(f"{f} {h:02d}:{mi:02d} | recibido | {rng.choice(CLIENTES)} | S/ {rng.choice([2.5, 4, 6.5, 8, 12, 15, 22, 35]):.2f} | {rng.choice(NOTAS_VENTA)}")
        if rng.random() < 0.35:  # familia manda plata (personal)
            lineas.append(f"{f} 21:{rng.randint(0, 59):02d} | recibido | {rng.choice(FAMILIA)} | S/ {rng.choice([50, 100, 150]):.2f} | {rng.choice(NOTAS_FAMILIA_IN)}")
        if rng.random() < 0.3:  # gasto personal
            lineas.append(f"{f} 19:{rng.randint(0, 59):02d} | enviado | {rng.choice(FAMILIA)} | S/ {rng.choice([20, 40, 60]):.2f} | {rng.choice(NOTAS_FAMILIA_OUT)}")
        if d % 5 == 0:  # compra de mercaderia
            lineas.append(f"{f} 06:30 | enviado | {rng.choice(PROVEEDORES)} | S/ {rng.choice([180, 250, 320]):.2f} | mercaderia")
        if d % 9 == 3:  # gasto fijo / insumos
            prov, nota = rng.choice(GASTOS_NEGOCIO)
            lineas.append(f"{f} 08:{rng.randint(0, 59):02d} | enviado | {prov} | S/ {rng.choice([35, 60, 90, 450]):.2f} | {nota}")
        if rng.random() < 0.15:  # caso ambiguo sin nota
            lineas.append(f"{f} 17:{rng.randint(0, 59):02d} | recibido | Diego Alarcon | S/ {rng.choice([30, 45, 80]):.2f} |")
    salida = Path(__file__).parent / "sample_movimientos.txt"
    salida.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"{len(lineas) - 1} movimientos -> {salida}")


if __name__ == "__main__":
    main()
