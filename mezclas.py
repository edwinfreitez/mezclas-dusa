import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Mezclas DUSA", layout="centered")

st.title("🧪 Calculadora de Mezclas DUSA")
st.markdown("---")

# 1. Matriz de Datos Dinámica
st.subheader("1. Carga de Componentes")
st.write("Usa el botón (+) al final de la tabla para agregar filas.")

if 'datos' not in st.session_state:
    st.session_state.datos = pd.DataFrame([
        {"Componente": "Alcohol base", "Volumen (L)": 1000.0, "Grado (GL)": 96.0},
        {"Componente": "Agua", "Volumen (L)": 0.0, "Grado (GL)": 0.0}
    ])

# Editor de la tabla
df_editado = st.data_editor(st.session_state.datos, num_rows="dynamic", use_container_width=True)

# 2. Cálculos Matemáticos (Ecuaciones 1, 2, 3 y 4)
# LAA parcial = (V * GL) / 100
laa_total = (df_editado["Volumen (L)"] * df_editado["Grado (GL)"] / 100).sum()
vol_actual = df_editado["Volumen (L)"].sum()

st.markdown("---")

# 3. Botones de Acción
col1, col2 = st.columns(2)

with col1:
    st.subheader("Calcular Grado Final")
    if st.button("Obtener Cf (Ec. 1)"):
        if vol_actual > 0:
            cf = (laa_total * 100) / vol_actual
            st.success(f"**Grado Final (Cf):** {cf:.2f} °GL")
            st.metric("Total LAA", f"{laa_total:.2f}")
        else:
            st.error("El volumen total debe ser mayor a 0")

with col2:
    st.subheader("Calcular Agua Necesaria")
    grado_deseado = st.number_input("Grado Objetivo (°GL):", value=40.0, step=0.1)
    if st.button("Obtener Va (Ec. 3)"):
        if grado_deseado > 0:
            # Vf = (Sumatoria LAA * 100) / Cf
            vol_final_necesario = (laa_total * 100) / grado_deseado
            # Va = Vf - Vol_ya_cargado
            agua_a_añadir = vol_final_necesario - vol_actual
            
            st.warning(f"**Agua a añadir (Va):** {max(0, agua_a_añadir):,.2f} L")
            st.metric("Volumen Final (Vf)", f"{vol_final_necesario:,.2f} L")
            st.info(f"Total LAA: {laa_total:.2f}")
