# Yape Contable

> Estado: en construcción (sprint del proyecto final, UP 2026-II). Las secciones marcadas **PENDIENTE** se llenan con evidencia real; no se rellenan con supuestos.

## 1. One-liner
Ayudamos a comerciantes pequeños que cobran por Yape a separar lo del negocio de lo personal, mediante IA que lee su historial, clasifica cada movimiento y pregunta solo lo dudoso.

## 2. Founder
**Bianca Espinoza** — estudiante de Economía, Universidad del Pacífico. PENDIENTE: foto y una línea de por qué soy la persona indicada; cómo cubro producto, ingeniería, diseño y ventas con agentes de IA.

## 3. Problema
- **Quién lo sufre:** dueños de negocios pequeños que cobran buena parte de sus ventas por Yape/Plin y usan la **misma cuenta** para lo personal y el negocio (en las 3 conversaciones: una bodega, un emprendimiento de postres por Instagram y un negocio con clientes que "casi todos pagan por Yape").
- **Cuánto les cuesta:** entre **2 y 5 horas al mes** ordenando sus movimientos (promedio ~3.5 h), y errores: "a veces se me pasan algunas" ventas, o no saben a qué pedido corresponde un pago.
- **Cómo lo resuelven hoy:** cuaderno, Excel, revisar el Yape a mano, pedir capturas al cliente o buscar su nombre en los chats.
- **Evidencia:** 3 conversaciones por WhatsApp en [`docs/research/`](docs/research/) ([resumen](docs/research/resumen.md)). Es una muestra pequeña de conocidos: confirma que el problema existe, no mide el mercado.

## 4. Solución e insight
Flujo único: historial de Yape → movimientos estructurados → clasificación **venta / gasto del negocio / personal / dudoso** → el comerciante confirma solo lo dudoso (el sistema recuerda su respuesta por persona) → reporte de ventas, gastos y utilidad.

Insight (hipótesis a validar): el problema no es leer el historial, sino que está mezclado con la vida personal. La herramienta no pretende acertar el 100 %: **pregunta cuando no sabe**.

## 5. Why now
PENDIENTE de redactar con cuidado. Idea base: los LLM ya ordenan texto desordenado en JSON verificable, algo que antes exigía reglas rígidas por cada formato.

## 6. Demo
- **URL pública:** PENDIENTE (despliegue previsto en Streamlit Community Cloud).
- **Correr en local:**
  ```bash
  pip install -r requirements.txt
  python data/make_synthetic.py      # genera datos de ejemplo (ya incluidos)
  streamlit run app/streamlit_app.py
  ```
- **Capturas y diagrama:** PENDIENTE en `docs/`.
- **Datos:** 100 % sintéticos (nombres inventados). No se usan datos de personas reales.
- **Modelos/APIs:** reglas propias para el formato conocido; LLM de Anthropic (`claude-haiku-5-5`) con salida estructurada solo para líneas que las reglas no entienden, y con verificación literal de lo que devuelve.

```
historial (texto) ──► parser (reglas → LLM si hace falta) ──► verificación literal
                                   │
                                   ▼
                     clasificador (venta / gasto / personal / dudoso)
                                   │  confirmación del usuario (se recuerda)
                                   ▼
                      reporte + gráfico por día (Streamlit)
```

## 7. Modelo de negocio
- **Quién paga:** el dueño del negocio.
- **Precio (hipótesis):** **S/ 15 al mes**. En las entrevistas dijeron S/ 5 a 10 (tras probar), ~S/ 15 y hasta S/ 25 (si además separa gastos y calcula ganancia). Son 3 respuestas habladas, no pagos reales: el precio hay que validarlo con uso real.
- **Costo por usuario:** PENDIENTE de medir. El clasificador por reglas casi no tiene costo; el LLM solo se usa en las líneas que las reglas no entienden.

## 8. Herramientas del curso
| Herramienta | Dónde |
|---|---|
| LLM con salidas estructuradas (sesión 08) | [`ai/parser.py`](ai/parser.py) |
| Dashboard (sesión 05) | [`app/streamlit_app.py`](app/streamlit_app.py), [`ai/report.py`](ai/report.py) |
| Document AI / OCR (sesión 10) | PENDIENTE: lectura de capturas de pantalla |

## 9. Qué hizo el agente
Claude Code generó el esqueleto inicial: parser, clasificador, reporte, app Streamlit, datos sintéticos, pruebas y esta plantilla de README. Las reglas de clasificación son una primera propuesta que debo revisar y ajustar con lo que digan los usuarios. PENDIENTE: ir actualizando esta sección con lo que cambie.

## Limitaciones conocidas
- El formato del historial es el de los datos sintéticos; hay que adaptarlo al formato real de Yape/Plin.
- La clasificación por reglas es una primera versión: por eso existe la bandeja de "dudosos".
- El modo LLM no se ha probado aún contra la API real.
