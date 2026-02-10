import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime

# Configuración de página
st.set_page_config(page_title="Mezcla de Alcoholes - DUSA", layout="centered")

# --- FUNCIONES ADICIONALES ---
def generar_pdf(df, resultados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="REPORTE DE MEZCLA DE ALCOHOLES - DUSA", ln=True, align='C')
    
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Fecha: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='R')
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Detalle de Componentes:", ln=True)
    
    # Tabla de componentes
    pdf.set_font("Arial", size=10)
    pdf.cell(60, 10, "Tipo", 1)
    pdf.cell(40, 10, "Volumen (Lts)", 1)
    pdf.cell(40, 10, "Grado (GL)", 1)
    pdf.cell(40, 10, "LAA", 1)
    pdf.ln()
    
    for _, row in df.iterrows():
        pdf.cell(60, 10, str(row['Tipo de Alcohol']), 1)
        pdf.cell(40, 10, f"{row['Volumen (Lts)']:,.2f}", 1)
        pdf.cell(40, 10, f"{row['°GL']:,.2f}", 1)
        laa = (row['Volumen (Lts)'] * row['°GL']) / 100
        pdf.cell(40, 10, f"{laa:,.2f}", 1)
        pdf.ln()
        
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="RESULTADOS FINALES:", ln=True)
    pdf.set_font("Arial", size=11)
    for k, v in resultados.items():
        pdf.cell(200, 8, txt=f"{k}: {v}", ln=True)
        
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
st.title("SISTEMA DE MEZCLAS DUSA")

if 'df_mezcla' not in st.session_state:
    st.session_state.df_mezcla = pd.DataFrame(
        [{"Tipo de Alcohol": "Alcohol Fino", "Volumen (Lts)": 1000.0, "°GL": 96.0}],
    )

df_editor = st.data_editor(st.session_state.df_mezcla, num_rows="dynamic")

# Cálculos Base
df_editor['LAA'] = (df_editor['Volumen (Lts)'] * df_editor['°GL']) / 100
total_laa = df_editor['LAA'].sum()
total_vol = df_editor['Volumen (Lts)'].sum()

st.divider()

col_btn1, col_btn2 = st.columns(2)
resultados_pdf = {}

with col_btn1:
    if st.button("MODO 1: Calcular Grado Final (Cf)"):
        if total_vol > 0:
            cf = (total_laa * 100) / total_vol
            st.metric("Grado Final (Cf)", f"{cf:.2f} °GL")
            st.metric("Total LAA", f"{total_laa:.2f}")
            resultados_pdf = {"Volumen Total": f"{total_vol} Lts", "Grado Final": f"{cf:.2f} °GL", "Total LAA": f"{total_laa:.2f}"}

with col_btn2:
    cf_deseada = st.number_input("Grado Deseado (°GL):", value=40.0)
    if st.button("MODO 2: Calcular Agua Necesaria (Va)"):
        vf = (total_laa * 100) / cf_deseada
        va = vf - total_vol
        st.metric("Agua a añadir (Va)", f"{max(0, va):,.2f} Lts")
        st.metric("Volumen Final (Vf)", f"{vf:,.2f} Lts")
        resultados_pdf = {"Agua Añadida": f"{va:.2f} Lts", "Volumen Final": f"{vf:.2f} Lts", "Grado Deseado": f"{cf_deseada} °GL", "Total LAA": f"{total_laa:.2f}"}

# Botón de Reporte
if resultados_pdf:
    pdf_data = generar_pdf(df_editor, resultados_pdf)
    st.download_button(label="📥 Descargar Reporte PDF", data=pdf_data, file_name="reporte_mezcla_dusa.pdf", mime="application/pdf")
