import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora DUSA", layout="wide")

st.title("🧪 Calculadora de Mezclas DUSA")

# 1. Configuración de la sesión para los datos
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame([
        {"Componente": "Agua", "Volumen (L)": 0.0, "Grado (GL)": 0.0},
        {"Componente": "Alcohol base", "Volumen (L)": 1000.0, "Grado (GL)": 96.0}
    ])

st.write("### Matriz de Mezcla")

# 2. Lógica de cálculo EN LA MISMA TABLA
# Creamos una copia para mostrar los LAA calculados
df_calculado = st.session_state.df.copy()
df_calculado["LAA"] = (df_calculado["Volumen (L)"] * df_calculado["Grado (GL)"]) / 100

# 3. EL EDITOR ÚNICO (Aquí es donde cargas y ves los LAA)
df_editado = st.data_editor(
    df_calculado,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "Componente": st.column_config.TextColumn("Componente", width="medium"),
        "Volumen (L)": st.column_config.NumberColumn("Volumen (L)", format="%.2f"),
        "Grado (GL)": st.column_config.NumberColumn("Grado (GL)", format="%.2f"),
        "LAA": st.column_config.NumberColumn("LAA", format="%.2f", disabled=True), # BLOQUEADO para que no se tipee
    }
)

# Guardar cambios
st.session_state.df = df_editado[["Componente", "Volumen (L)", "Grado (GL)"]]

# 4. FILA DE TOTALES DINÁMICA
v_total = df_editado["Volumen (L)"].sum()
laa_total = df_editado["LAA"].sum()

# Mostramos totales como tarjetas elegantes
c_v, c_l = st.columns(2)
with c_v:
    st.metric("TOTAL VOLUMEN (L)", f"{v_total:,.2f}")
with c_l:
    st.metric("TOTAL LAA", f"{laa_total:,.2f}")

st.divider()

# 5. CÁLCULOS FINALES
col1, col2 = st.columns(2)

with col1:
    if st.button("CALCULAR GRADO FINAL (Cf)"):
        if v_total > 0:
            cf = (laa_total * 100) / v_total
            st.success(f"### Cf: {cf:.2f} °GL")

with col2:
    grado_obj = st.number_input("Grado Objetivo (°GL):", value=40.0)
    if st.button("CALCULAR AGUA NECESARIA (Va)"):
        if grado_obj > 0:
            vf = (laa_total * 100) / grado_obj
            va = vf - v_total
            st.warning(f"### Agua a añadir: {max(0, va):,.2f} L")
            st.write(f"Volumen final será: {vf:,.2f} L")
