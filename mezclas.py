import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime

# 1. Configuración de la interfaz (Identidad DUSA)
st.set_page_config(page_title="Mezclas DUSA", layout="centered")

# 2. Función para generar el reporte PDF
def crear_reporte_pdf(tabla, resultados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "DUSA - REPORTE DE MEZCLAS", ln=True, align='C')
    pdf.ln(10)
    
    # Detalle de la mezcla
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Detalle de los Componentes:", ln=True)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(60, 10, "Componente", 1)
    pdf.cell(40, 10, "Volumen (L)", 1)
    pdf.cell(40, 10, "Grado (GL)", 1)
    pdf.ln()
    
    pdf.set_font("Arial", '', 10)
    for _, fila in tabla.iterrows():
        pdf.cell(60, 10, str(fila['Componente']), 1)
        pdf.cell(40, 10, f"{fila['Volumen']:.2f}", 1)
        pdf.cell(40, 10, f"{fila['GL']:.2f}", 1)
        pdf.ln()
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "RESULTADOS FINALES:", ln=True)
    pdf.set_font("Arial", '', 11)
    for k, v in resultados.items():
        pdf.cell(0, 8, f"{k}: {v}", ln=True)
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# 3. Interfaz de la Aplicación
st.title("🧪 Mezcla de Alcoholes DUSA")
st.write("Agregue líneas para alcoholes o agua (0 GL).")

# Matriz de entrada dinámica
if 'tabla_datos' not in st.session_state:
    st.session_state.tabla_datos = pd.DataFrame([
        {"Componente": "Alcohol base", "Volumen": 1000.0, "GL": 96.0},
        {"Componente": "Agua", "Volumen": 0.0, "GL": 0.0}
    ])

df_final = st.data_editor(st.session_state.tabla_datos, num_rows="dynamic")

# Ecuaciones de mezcla
# LAA = Volumen * GL / 100
laa_sum = (df_final['Volumen'] * df_final['GL'] / 100).sum()
vol_sum = df_final['Volumen'].sum()

st.divider()
diccionario_res = {}

# Botones de Acción
c1, c2 = st.columns(2)

with c1:
    st.subheader("Modo 1: Final")
    if st.button("Calcular Grado Final (Cf)"):
        if vol_sum > 0:
            cf_calc = (laa_sum * 100) / vol_sum
            st.metric("Resultado Cf", f"{cf_calc:.2f} GL")
            st.metric("Total LAA", f"{laa_sum:.2f}")
            diccionario_res = {
                "Volumen Total (Vf)": f"{vol_sum:,.2f} L",
                "Grado Final (Cf)": f"{cf_calc:.2f} GL",
                "Total LAA": f"{laa_sum:.2f}"
            }

with c2:
    st.subheader("Modo 2: Ajuste")
    grado_obj = st.number_input("Grado Objetivo (GL):", value=40.0, step=0.1)
    if st.button("Calcular Agua Necesaria (Va)"):
        if grado_obj > 0:
            # Vf = LAA_totales * 100 / Cf_deseada
            vf_calc = (laa_sum * 100) / grado_obj
            # Va = Vf - V_ya_existente
            va_calc = vf_calc - vol_sum
            
            st.metric("Agua a añadir (Va)", f"{max(0, va_calc):,.2f} L")
            st.metric("Volumen Final (Vf)", f"{vf_calc:,.2f} L")
            diccionario_res = {
                "Agua Necesaria (Va)": f"{max(0, va_calc):,.2f} L",
                "Volumen Final (Vf)": f"{vf_calc:,.2f} L",
                "Grado Objetivo": f"{grado_obj:.2f} GL",
                "Total LAA": f"{laa_sum:.2f}"
            }

# Generación del reporte
if diccionario_res:
    st.divider()
    try:
        archivo_pdf = crear_reporte_pdf(df_final, diccionario_res)
        st.download_button(
            label="📥 Descargar Reporte PDF",
            data=archivo_pdf,
            file_name=f"reporte_mezcla_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Error al generar PDF: {e}")
