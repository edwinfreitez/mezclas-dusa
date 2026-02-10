import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime

# Configuración profesional
st.set_page_config(page_title="Mezcla de Alcoholes DUSA", layout="centered")

# Función para el PDF (Simplificada para evitar errores de codificación)
def generar_pdf(df, resultados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="REPORTE DE MEZCLA DE ALCOHOLES - DUSA", ln=True, align='C')
    
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, txt=f"Fecha: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='R')
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Detalle de Componentes:", ln=True)
    
    # Encabezados de tabla
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(60, 10, "Tipo de Alcohol", 1)
    pdf.cell(40, 10, "Volumen (Lts)", 1)
    pdf.cell(40, 10, "Grado GL", 1)
    pdf.cell(40, 10, "LAA", 1)
    pdf.ln()
    
    # Contenido de la tabla
    pdf.set_font("Arial", size=10)
    for _, row in df.iterrows():
        laa = (float(row['Volumen (Lts)']) * float(row['GL'])) / 100
        pdf.cell(60, 10, str(row['Tipo de Alcohol']), 1)
        pdf.cell(40, 10, f"{row['Volumen (Lts)']:,.2f}", 1)
        pdf.cell(40, 10, f"{row['GL']:,.2f}", 1)
        pdf.cell(40, 10, f"{laa:,.2f}", 1)
        pdf.ln()
        
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="RESULTADOS FINALES:", ln=True)
    pdf.set_font("Arial", size=11)
    for k, v in resultados.items():
        pdf.cell(0, 8, txt=f"{k}: {v}", ln=True)
        
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- INTERFAZ ---
st.title("🧪 SISTEMA DE MEZCLAS DUSA")

# Inicialización de tabla
if 'df_mezcla' not in st.session_state:
    st.session_state.df_mezcla = pd.DataFrame(
        [{"Tipo de Alcohol": "Alcohol Etilico", "Volumen (Lts)": 1000.0, "GL": 96.0}],
    )

st.write("Edita la tabla para agregar alcoholes o agua (Grado 0):")
df_editor = st.data_editor(st.session_state.df_mezcla, num_rows="dynamic")

# Limpieza y cálculos (Ec. 4)
df_editor['LAA'] = (df_editor['Volumen (Lts)'] * df_editor['GL']) / 100
total_laa = df_editor['LAA'].sum()
total_vol = df_editor['Volumen (Lts)'].sum()

st.divider()

res_dict = {}

# MODO 1: Concentración Final (Ec. 1)
if st.button("CALCULAR GRADO FINAL (Cf)"):
    if total_vol > 0:
        cf = (total_laa * 100) / total_vol
        st.subheader(f"Resultado: {cf:.2f} GL")
        res_dict = {"Volumen Final": f"{total_vol:,.2f} Lts", "Grado Final": f"{cf:.2f} GL", "Total LAA": f"{total_laa:,.2f}"}
    else:
        st.error("Ingresa volúmenes válidos.")

st.divider()

# MODO 2: Agua necesaria (Ec. 2 y 3)
cf_deseada = st.number_input("Grado Deseado (GL):", value=40.0)
if st.button("CALCULAR AGUA NECESARIA (Va)"):
    if cf_deseada > 0:
        vf = (total_laa * 100) / cf_deseada
        va = vf - total_vol
        st.subheader(f"Agua a añadir: {max(0, va):,.2f} Lts")
        st.write(f"Volumen Final esperado: {vf:,.2f} Lts")
        res_dict = {"Agua a añadir": f"{max(0, va):,.2f} Lts", "Volumen Final": f"{vf:,.2f} Lts", "Grado Deseado": f"{cf_deseada} GL", "Total LAA": f"{total_laa:,.2f}"}

# Botón PDF
if res_dict:
    try:
        pdf_out = generar_pdf(df_editor, res_dict)
        st.download_button("📥 Descargar Reporte PDF", data=pdf_out, file_name="mezcla_dusa.pdf", mime="application/pdf")
    except Exception as e:
        st.error(f"Error generando PDF: {e}")
