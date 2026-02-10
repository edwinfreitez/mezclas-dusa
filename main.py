import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime

st.set_page_config(page_title="Mezclas DUSA", layout="centered")

# --- LÓGICA DEL PDF ---
def crear_pdf(datos, resumen):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "DUSA - REPORTE DE MEZCLAS", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='R')
    pdf.ln(5)
    
    # Tabla
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(60, 10, "Componente", 1)
    pdf.cell(40, 10, "Volumen (L)", 1)
    pdf.cell(40, 10, "Grado (GL)", 1)
    pdf.ln()
    
    pdf.set_font("Arial", '', 10)
    for _, fila in datos.iterrows():
        pdf.cell(60, 10, str(fila['Tipo']), 1)
        pdf.cell(40, 10, str(fila['Volumen']), 1)
        pdf.cell(40, 10, str(fila['GL']), 1)
        pdf.ln()
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "RESULTADOS:", ln=True)
    pdf.set_font("Arial", '', 11)
    for k, v in resumen.items():
        pdf.cell(0, 8, f"{k}: {v}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
st.title("🧪 Mezcla de Alcoholes DUSA")

# Tabla de entrada
if 'datos' not in st.session_state:
    st.session_state.datos = pd.DataFrame([{"Tipo": "Alcohol Etilico", "Volumen": 1000.0, "GL": 96.0}])

df_ed = st.data_editor(st.session_state.datos, num_rows="dynamic")

# Cálculos rápidos
laa_total = (df_ed['Volumen'] * df_ed['GL'] / 100).sum()
vol_total = df_ed['Volumen'].sum()

st.divider()
res = {}

col1, col2 = st.columns(2)
with col1:
    if st.button("Calcular Grado Final (Cf)"):
        if vol_total > 0:
            cf = (laa_total * 100) / vol_total
            st.metric("Grado Final", f"{cf:.2f} GL")
            res = {"Volumen Total": vol_total, "Grado Final": f"{cf:.2f} GL", "Total LAA": laa_total}

with col2:
    target = st.number_input("Grado Objetivo:", value=40.0)
    if st.button("Calcular Agua (Va)"):
        vf = (laa_total * 100) / target
        va = vf - vol_total
        st.metric("Agua a añadir", f"{max(0, va):.2f} L")
        res = {"Agua a añadir": f"{va:.2f} L", "Volumen Final": vf, "Total LAA": laa_total}

if res:
    reporte = crear_pdf(df_ed, res)
    st.download_button("📥 Descargar PDF", reporte, "mezcla_dusa.pdf", "application/pdf")
