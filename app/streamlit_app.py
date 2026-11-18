"""App Streamlit: pega tu historial -> clasifica -> confirma lo dudoso -> reporte.
Ejecutar desde la raiz del repo:  streamlit run app/streamlit_app.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from datetime import date

import pandas as pd
import streamlit as st

from ai.classifier import CATEGORIAS, clasificar, clave_label
from ai.parser import Movimiento, parse
from ai.report import a_dataframe, costo_trabajadores, dias_del_periodo, por_dia, resumen

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample_movimientos.txt"

st.set_page_config(page_title="Yape Contable", page_icon="🧾", layout="wide")

# Evita que el traductor automatico del navegador rompa la pagina (error 'removeChild').
st.components.v1.html(
    "<script>const d = window.parent.document;"
    "d.documentElement.setAttribute('translate','no'); d.documentElement.classList.add('notranslate');"
    "if(!d.querySelector('meta[name=google]')){const m=d.createElement('meta');"
    "m.name='google'; m.content='notranslate'; d.head.appendChild(m);}</script>",
    height=0,
)
st.title("🧾 Yape Contable")
st.caption("Separa lo del negocio de lo personal en tu historial de Yape. Datos de demo: inventados.")

if "labels" not in st.session_state:
    st.session_state.labels = {}

with st.sidebar:
    st.header("1. Tu historial")
    fuente = st.radio("Origen", ["Subir captura de Yape", "Datos de ejemplo", "Pegar texto"])
    usar_llm = st.checkbox("Usar LLM para lineas que no entiendo", value=False,
                           help="Requiere ANTHROPIC_API_KEY en el entorno.")
    st.header("2. Tu familia")
    familia_txt = st.text_area("Nombres de familia o personas que NO son clientes (separa con comas)",
                               placeholder="Teresa Diaz, Mario Diaz", height=80)
    familia = {n.strip().lower() for n in familia_txt.split(",") if n.strip()}
    if st.button("Olvidar lo que confirme"):
        st.session_state.labels = {}

@st.cache_data(show_spinner="Leyendo la captura en tu computador...")
def leer_captura_cacheada(datos: bytes, dia_captura: date):
    from ai.ocr import parse_captura  # import perezoso: carga el OCR solo si se usa
    return parse_captura(datos, dia_captura)


movs, no_leidas = [], []
if fuente == "Subir captura de Yape":
    dia = st.sidebar.date_input("¿Qué día tomaste la captura? (para entender 'Ayer')", value=date.today())
    st.sidebar.caption("Privacidad: en la versión en línea la captura se procesa en el servidor de Streamlit. "
                       "Usa capturas de ejemplo o con los nombres tapados. Si corres la app en tu "
                       "computador, la captura no sale de él.")
    archivos = st.file_uploader("Sube la(s) captura(s) de la pantalla 'Movimientos' de Yape",
                                type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    for archivo in archivos or []:
        m, n = leer_captura_cacheada(archivo.getvalue(), dia)
        movs.extend(m)
        no_leidas.extend(n)
    completar_demo = st.sidebar.checkbox(
        "Completar con historial FICTICIO de ejemplo", value=True,
        help="Una captura trae pocos días. Esto agrega ~400 movimientos inventados (bodega 'Don Lucho') "
             "para que el reporte y el gráfico se vean completos. Desmárcalo para ver solo tu captura.")
    if completar_demo and movs:
        from ai.demo import completar
        movs = completar(movs)
else:
    if fuente == "Datos de ejemplo":
        texto = SAMPLE.read_text(encoding="utf-8") if SAMPLE.exists() else ""
    else:
        texto = st.text_area("Pega aqui los movimientos (una linea por movimiento)", height=200,
                             placeholder="12/10/2026 08:15 | recibido | Rosa Quispe | S/ 6.50 | pan")
    movs, no_leidas = parse(texto, use_llm=usar_llm)
if not movs:
    st.info("Carga o pega un historial para empezar.")
    st.stop()
if no_leidas:
    st.warning(f"{len(no_leidas)} linea(s) no se pudieron leer.")
    with st.expander("Ver lineas no leidas"):
        st.code("\n".join(no_leidas))

df = a_dataframe(clasificar(movs, st.session_state.labels, familia))
r = resumen(df)

n_fict = int((df["origen"] == "ficticio").sum())
if n_fict:
    st.warning(f"Esta vista incluye **{n_fict} movimientos FICTICIOS** (datos de ejemplo inventados) junto con "
               f"{len(df) - n_fict} de tu captura. Las cifras mezclan ambos. "
               "Para ver solo tu captura, desmarca la opción en la barra lateral.")

dias_periodo = dias_del_periodo(df)
with st.expander("👷 Pago a trabajadores (opcional): ajusta cuánto ganan por hora y cuántos días van"):
    st.caption("Esto NO sale de Yape: lo escribes tú. Costo = pago por hora × horas por día × días trabajados "
               f"(días por semana × {dias_periodo} días del periodo ÷ 7). Las filas de abajo son un EJEMPLO inventado; "
               "edítalas, agrega o borra filas. Si alguien no va todos los días, baja sus 'días por semana'.")
    base = pd.DataFrame({"trabajador": ["Trabajador 1 (ejemplo)", "Trabajador 2 (ejemplo)"],
                         "pago_hora": [6.0, 5.0], "horas_dia": [8.0, 4.0], "dias_semana": [6.0, 3.0]})
    trab = st.data_editor(base, num_rows="dynamic", hide_index=True, width="stretch", key="trabajadores",
                          column_config={"trabajador": "Nombre", "pago_hora": st.column_config.NumberColumn("S/ por hora", min_value=0.0),
                                         "horas_dia": st.column_config.NumberColumn("Horas por día", min_value=0.0, max_value=24.0),
                                         "dias_semana": st.column_config.NumberColumn("Días por semana", min_value=0.0, max_value=7.0)})
    costo_t = costo_trabajadores(trab, dias_periodo)
    pago_trab = round(float(costo_t["costo"].sum()), 2)
    if not costo_t.empty:
        st.dataframe(costo_t[["trabajador", "dias_trabajados", "costo"]], hide_index=True, width="stretch")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Ventas del negocio", f"S/ {r['ventas']:,.2f}")
c2.metric("Gastos del negocio", f"S/ {r['gastos']:,.2f}")
c3.metric("Utilidad (ventas − gastos)", f"S/ {r['utilidad']:,.2f}")
c4.metric("Personal de la familia (excluido)", f"S/ {r['personal']:,.2f}")
d1, d2 = st.columns(2)
d1.metric("Pago a trabajadores", f"S/ {pago_trab:,.2f}")
d2.metric("Utilidad después de pagar trabajadores", f"S/ {r['utilidad'] - pago_trab:,.2f}")

dudosos = df[df.categoria == "dudoso"]
st.subheader(f"3. Confirma lo dudoso ({len(dudosos)})")
if dudosos.empty:
    st.success("No hay movimientos dudosos.")
else:
    st.caption("Tu respuesta se recuerda por persona: la proxima vez no se vuelve a preguntar.")
    editor = dudosos[["origen", "fecha", "hora", "tipo", "contraparte", "monto", "nota"]].copy()
    # Sugerencias para que solo corrijas excepciones (son una adivinanza, no un dato).
    st.caption("Ya puse una sugerencia: lo que recibes suele ser venta. Cámbiala donde no sea cierto.")
    rapido = st.selectbox("Atajo para lo que ENVIASTE", ["(elegir uno por uno)", "personal", "gasto_negocio"])
    editor["tu_respuesta"] = [
        "venta" if t == "recibido" else (None if rapido.startswith("(") else rapido) for t in editor["tipo"]
    ]
    editado = st.data_editor(
        editor, hide_index=True, width="stretch", key=f"editor_dudosos_{rapido}",
        column_config={"tu_respuesta": st.column_config.SelectboxColumn("¿Qué es?", options=CATEGORIAS)},
        disabled=["origen", "fecha", "hora", "tipo", "contraparte", "monto", "nota"],
    )
    if st.button("Aplicar mis respuestas"):
        for _, fila in editado.dropna(subset=["tu_respuesta"]).iterrows():
            mov = Movimiento(fila["fecha"], fila["hora"], fila["tipo"], fila["contraparte"],
                             float(fila["monto"]), fila["nota"])
            st.session_state.labels[clave_label(mov)] = fila["tu_respuesta"]
        st.rerun()

st.subheader("4. Ventas y gastos por dia")
tabla = por_dia(df)
if not tabla.empty:
    st.bar_chart(tabla)

with st.expander("Ver todos los movimientos clasificados y por que"):
    st.dataframe(df.drop(columns=["fecha_dt"]), width="stretch", hide_index=True)

st.download_button("Descargar reporte (CSV)", df.drop(columns=["fecha_dt"]).to_csv(index=False).encode("utf-8"),
                   file_name="reporte_yape_contable.csv")
