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
Flujo único: **captura de la pantalla "Movimientos" de Yape** → OCR local → movimientos estructurados (persona, monto, fecha, enviado/recibido) → clasificación **venta / gasto del negocio / personal / dudoso** → el comerciante confirma lo dudoso (el sistema recuerda su respuesta por persona; puede indicar su lista de familia y usar sugerencias) → reporte de ventas, gastos y utilidad.

Insight (hipótesis a validar): el problema no es leer el historial, sino que está mezclado con la vida personal (3 de 3 entrevistados usan la misma cuenta para todo). La herramienta **no adivina quién es cliente y quién es familia**, porque eso solo lo sabe el dueño: propone, recuerda lo que el dueño responde y pregunta cuando no sabe.

## 5. Why now
*Borrador, a revisar por la founder.* Hace pocos años, leer una captura exigía un servicio de pago en la nube o entrenar un modelo propio. Hoy hay OCR abierto que corre en la laptop (sin enviar la captura a ningún servidor) y LLM pequeños que ordenan texto desordenado en JSON. Además, casi todo el cobro de estos negocios ya pasa por Yape/Plin (entrevistas: 40 % a 90 % de sus ventas), así que el historial digital ya contiene la información, solo que mezclada.

## 6. Demo
- **URL pública:** https://yape-contable.streamlit.app (Streamlit Community Cloud). Puede tardar unos segundos en despertar si nadie la ha abierto.
- **Correr en local:**
  ```bash
  pip install -r requirements.txt
  python data/make_synthetic.py      # genera datos de ejemplo (ya incluidos)
  python -m streamlit run app/streamlit_app.py
  ```
  En la app: *Origen → Subir captura de Yape* (o *Datos de ejemplo*).
- **Capturas y diagrama:** PENDIENTE en `docs/`.
- **Datos:** el origen "Datos de ejemplo" es 100 % sintético (nombres inventados). La lectura de capturas se probó con **una captura real propia** (11 de 11 movimientos leídos correctamente), con los nombres tapados; esa captura no se sube al repo. No se usan datos de terceros.
- **Modelos y por qué:**
  - **RapidOCR (ONNX), sin API externa:** corre dentro de la propia app, sin clave ni costo. Si la app se ejecuta en la laptop, la captura no sale de ella (importante porque el historial es información financiera). En la URL pública se procesa en el servidor de Streamlit, por eso allí solo deben subirse capturas de ejemplo o con nombres tapados.
  - **Reglas propias** para clasificar: son predecibles y se pueden explicar ("lo clasifiqué así porque...").
  - **LLM de Anthropic (`claude-haiku-5-5`)**, opcional, con salida estructurada para líneas que las reglas no entienden, y con verificación literal de lo que devuelve. No se ha probado contra la API real.

```
captura de Yape ──► OCR local (ai/ocr.py) ──► movimientos
historial en texto ──► parser (reglas → LLM opcional, ai/parser.py) ──┘
                                   │
                                   ▼
        clasificador (venta / gasto / personal / dudoso, ai/classifier.py)
                                   │  confirmación del usuario (se recuerda por persona)
                                   ▼
               reporte + gráfico por día (Streamlit, ai/report.py)
```

## 7. Modelo de negocio
- **Quién paga:** el dueño del negocio.
- **Precio (hipótesis):** **S/ 15 al mes**. En las entrevistas dijeron S/ 5 a 10 (tras probar), ~S/ 15 y hasta S/ 25 (si además separa gastos y calcula ganancia). Son 3 respuestas habladas, no pagos reales: el precio hay que validarlo con uso real.
- **Costo por usuario:** PENDIENTE de medir. El clasificador por reglas casi no tiene costo; el LLM solo se usa en las líneas que las reglas no entienden.

## 8. Herramientas del curso
| Herramienta | Dónde |
|---|---|
| Document AI / OCR (sesión 10) | [`ai/ocr.py`](ai/ocr.py): lee la captura de Yape (en local, con RapidOCR) |
| Dashboard (sesión 05) | [`app/streamlit_app.py`](app/streamlit_app.py), [`ai/report.py`](ai/report.py) |
| LLM con salidas estructuradas (sesión 08) | [`ai/parser.py`](ai/parser.py): opcional, para líneas que las reglas no entienden; no probado aún con la API real |

Por qué estas: el historial de Yape es una imagen (OCR), el resultado hay que verlo y confirmarlo (dashboard) y el texto desordenado se puede ordenar con un LLM. Dos de las tres están probadas de punta a punta; la del LLM está escrita pero sin probar.

## 9. Qué hizo el agente
Claude Code generó la primera versión del parser, el clasificador, el reporte, la app Streamlit, el lector de capturas (OCR), los datos sintéticos, las pruebas y la plantilla de este README. Yo hice las entrevistas con los usuarios, tomé la captura real con la que se probó el OCR, y decidí el problema, el cliente y el precio. Las reglas de clasificación son una primera propuesta del agente que debo entender y ajustar; las pruebas automáticas están en `tests/`.

## Limitaciones conocidas
- **La clasificación sigue pidiendo trabajo manual.** Sin nombres ni notas (por ejemplo, con nombres tapados) todos los movimientos salen "dudosos". Se reduce con sugerencias, con la lista de familia y recordando respuestas por persona, pero la primera vez el dueño tiene que decidir. No lo he medido: la afirmación "ahorra tiempo" es una hipótesis.
- Los datos de ejemplo se generaron con las mismas palabras que usa el clasificador, así que su porcentaje de aciertos **no** mide qué tan bien funcionaría con datos reales.
- El OCR se probó con **una** captura. Puede fallar con otras resoluciones o recortes.
- La evidencia son 3 conversaciones con conocidos; el precio de S/ 15 es una hipótesis, no un pago real.
- El modo LLM no se ha probado aún contra la API real.
- Ideas descartadas por ahora: importar los contactos del celular (por privacidad y porque los nombres de Yape no coinciden con los guardados).
