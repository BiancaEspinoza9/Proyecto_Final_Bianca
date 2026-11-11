"""Genera un historial SINTETICO de Yape para una bodega inventada.
Todos los nombres son ficticios. Uso: python data/make_synthetic.py
"""
import random
from datetime import date, timedelta
from pathlib import Path

rng = random.Random(2026)

CLIENTES = ["Rosa Quispe", "Carlos Mamani", "Lucia Torres", "Jorge Salas", "Ana Huaman",
            "Pedro Rojas", "Marta Vega", "Luis Cardenas", "Elena Paredes", "Raul Campos"]
FAMILIA = ["Teresa Diaz", "Mario Diaz", "Karen Diaz"]
PROVEEDORES = ["Distribuidora Andina", "Abarrotes El Sol", "Bebidas Norte"]
NOTAS_VENTA = ["pan", "gaseosa", "huevos", "arroz", "leche", "aceite", "", "", ""]


def main() -> None:
    lineas = ["# Historial sintetico - Bodega 'Don Lucho' (datos inventados)"]
    inicio = date(2026, 10, 12)
    for d in range(30):
        dia = inicio + timedelta(days=d)
        f = dia.strftime("%d/%m/%Y")
        for _ in range(rng.randint(3, 7)):  # ventas del negocio
            h, mi = rng.randint(7, 20), rng.choice([0, 10, 15, 25, 40, 55])
            lineas.append(f"{f} {h:02d}:{mi:02d} | recibido | {rng.choice(CLIENTES)} | S/ {rng.choice([2.5, 4, 6.5, 8, 12, 15, 22, 35]):.2f} | {rng.choice(NOTAS_VENTA)}")
        if rng.random() < 0.35:  # familia manda plata (personal)
            lineas.append(f"{f} 21:{rng.randint(0, 59):02d} | recibido | {rng.choice(FAMILIA)} | S/ {rng.choice([50, 100, 150]):.2f} | para el cine")
        if rng.random() < 0.3:  # gasto personal
            lineas.append(f"{f} 19:{rng.randint(0, 59):02d} | enviado | {rng.choice(FAMILIA)} | S/ {rng.choice([20, 40, 60]):.2f} | regalo cumple")
        if d % 5 == 0:  # compra de mercaderia
            lineas.append(f"{f} 06:30 | enviado | {rng.choice(PROVEEDORES)} | S/ {rng.choice([180, 250, 320]):.2f} | mercaderia")
        if rng.random() < 0.15:  # caso ambiguo sin nota
            lineas.append(f"{f} 17:{rng.randint(0, 59):02d} | recibido | Diego Alarcon | S/ {rng.choice([30, 45, 80]):.2f} |")
    salida = Path(__file__).parent / "sample_movimientos.txt"
    salida.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"{len(lineas) - 1} movimientos -> {salida}")


if __name__ == "__main__":
    main()
