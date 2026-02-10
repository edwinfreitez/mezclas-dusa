import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime

st.set_page_config(page_title="Mezclas DUSA", layout="centered")

def crear_reporte_pdf(tabla, resultados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "DUSA - REPORTE DE MEZCLAS", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Componentes:", ln=True)
    pdf.set_font("Arial", '', 10)
    for _, fila in tabla.iterrows():
        pdf.cell(0, 8, f"- {fila['Componente']}: {fila['Volumen']} L a {fila['GL']} GL", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "RESULTADOS:", ln=True)
    for k, v in resultados.items():
        pdf.cell(0, 8, f"{k}: {v}", ln=True)
    return pdf.output(dest='S').encode('latin-1', 'ignore')

st.title("🧪 Mezcla de Alcoholes DUSA")

if 'tabla_datos' not in st.session_state:
    st.session_state.tabla_datos = pd.DataFrame([
        {"Componente": "Alcohol base", "Volumen": 1000.0, "GL": 96.0},
        {"Componente": "Agua", "Volumen": 0.0, "GL": 0.0}
    ])

df_final = st.data_editor(st.session_state.tabla_datos, num_rows="dynamic")

laa_sum = (df_final['Volumen'] * df_final['GL'] / 100).sum()
vol_sum = df_final['Volumen'].sum()

st.divider()
diccionario_res = {}

c1, c2 = st.columns(2)
with c1:
    if st.button("Calcular Grado Final (Cf)"):
        if vol_sum > 0:
            cf_calc = (laa_sum * 100) / vol_sum
            st.metric("Resultado Cf", f"{cf_calc:.2f} GL")
            diccionario_res = {"Volumen Total": f"{vol_sum} L", "Grado Final": f"{cf_calc:.2f} GL", "Total LAA": f"{laa_sum:.2f}"}

with c2:
    grado_obj = st.number_input("Grado Objetivo (GL):", value=40.0)
    if st.button("Calcular Agua (Va)"):
        if grado_obj > 0:
            vf_calc = (laa_sum * 100) / grado_obj
            va_calc = vf_calc - vol_sum
            st.metric("Agua a añadir (Va)", f"{max(0, va_calc):,.2f} L")
            diccionario_res = {"Agua Necesaria": f"{va_calc:.2f} L", "Volumen Final": f"{vf_calc:.2f} L", "Total LAA": f"{laa_sum:.2f}"}

if diccionario_res:
    pdf_out = crear_reporte_pdf(df_final, diccionario_res)
    st.download_button("📥 Descargar Reporte PDF", pdf_out, "reporte_dusa.pdf", "application/pdf")
