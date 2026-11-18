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
from ai.report import a_dataframe, por_dia, resumen

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample_movimientos.txt"

st.set_page_config(page_title="Yape Contable", page_icon="🧾", layout="wide")
st.title("🧾 Yape Contable")
st.caption("Separa lo del negocio de lo personal en tu historial de Yape. Datos de demo: inventados.")

if "labels" not in st.session_state:
    st.session_state.labels = {}

with st.sidebar:
    st.header("1. Tu historial")
    fuente = st.radio("Origen", ["Subir captura de Yape", "Datos de ejemplo", "Pegar texto"])
    usar_llm = st.checkbox("Usar LLM para lineas que no entiendo", value=False,
                           help="Requiere ANTHROPIC_API_KEY en el entorno.")
    if st.button("Olvidar lo que confirme"):
        st.session_state.labels = {}

@st.cache_data(show_spinner="Leyendo la captura en tu computador...")
def leer_captura_cacheada(datos: bytes, dia_captura: date):
    from ai.ocr import parse_captura  # import perezoso: carga el OCR solo si se usa
    return parse_captura(datos, dia_captura)


movs, no_leidas = [], []
if fuente == "Subir captura de Yape":
    dia = st.sidebar.date_input("¿Qué día tomaste la captura? (para entender 'Ayer')", value=date.today())
    st.sidebar.caption("La captura se lee en tu computador: no se envía a ningún servidor.")
    archivos = st.file_uploader("Sube la(s) captura(s) de la pantalla 'Movimientos' de Yape",
                                type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    for archivo in archivos or []:
        m, n = leer_captura_cacheada(archivo.getvalue(), dia)
        movs.extend(m)
        no_leidas.extend(n)
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

df = a_dataframe(clasificar(movs, st.session_state.labels))
r = resumen(df)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Ventas del negocio", f"S/ {r['ventas']:,.2f}")
c2.metric("Gastos del negocio", f"S/ {r['gastos']:,.2f}")
c3.metric("Utilidad", f"S/ {r['utilidad']:,.2f}")
c4.metric("Personal (excluido)", f"S/ {r['personal']:,.2f}")

dudosos = df[df.categoria == "dudoso"]
st.subheader(f"2. Confirma lo dudoso ({len(dudosos)})")
if dudosos.empty:
    st.success("No hay movimientos dudosos.")
else:
    st.caption("Tu respuesta se recuerda por persona: la proxima vez no se vuelve a preguntar.")
    editor = dudosos[["fecha", "hora", "tipo", "contraparte", "monto", "nota"]].copy()
    editor["tu_respuesta"] = None
    editado = st.data_editor(
        editor, hide_index=True, width="stretch",
        column_config={"tu_respuesta": st.column_config.SelectboxColumn("¿Qué es?", options=CATEGORIAS)},
        disabled=["fecha", "hora", "tipo", "contraparte", "monto", "nota"],
    )
    if st.button("Aplicar mis respuestas"):
        for _, fila in editado.dropna(subset=["tu_respuesta"]).iterrows():
            mov = Movimiento(fila["fecha"], fila["hora"], fila["tipo"], fila["contraparte"],
                             float(fila["monto"]), fila["nota"])
            st.session_state.labels[clave_label(mov)] = fila["tu_respuesta"]
        st.rerun()

st.subheader("3. Ventas y gastos por dia")
tabla = por_dia(df)
if not tabla.empty:
    st.bar_chart(tabla)

with st.expander("Ver todos los movimientos clasificados y por que"):
    st.dataframe(df.drop(columns=["fecha_dt"]), width="stretch", hide_index=True)

st.download_button("Descargar reporte (CSV)", df.drop(columns=["fecha_dt"]).to_csv(index=False).encode("utf-8"),
                   file_name="reporte_yape_contable.csv")
