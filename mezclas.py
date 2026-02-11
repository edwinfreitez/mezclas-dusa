import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora DUSA", layout="wide")

st.title("🧪 Calculadora de Mezclas DUSA")

# --- LÓGICA DE DATOS ---
if 'datos' not in st.session_state:
    # Fila de agua por defecto (Grado 0)
    st.session_state.datos = pd.DataFrame([
        {"Componente": "Agua", "Volumen (L)": 0.0, "Grado (GL)": 0.0},
        {"Componente": "Alcohol base", "Volumen (L)": 1000.0, "Grado (GL)": 96.0}
    ])

st.info("💧 **Fila 0 (Agua):** Cargue solo el volumen. El grado se mantiene en 0.")

# --- EDITOR DE MATRIZ ---
# Calculamos LAA antes de mostrar para que se vea la columna
df_temp = st.session_state.datos.copy()
df_temp["LAA"] = (df_temp["Volumen (L)"] * df_temp["Grado (GL)"]) / 100

df_editado = st.data_editor(
    df_temp, 
    num_rows="dynamic", 
    use_container_width=True,
    column_config={
        "LAA": st.column_config.NumberColumn("LAA", disabled=True, format="%.2f"),
        "Componente": st.column_config.TextColumn("Componente")
    }
)

# Actualizar el estado con los nuevos datos
st.session_state.datos = df_editado[["Componente", "Volumen (L)", "Grado (GL)"]]

# --- CÁLCULO DE TOTALES (En tiempo real) ---
total_vol = df_editado["Volumen (L)"].sum()
total_laa = (df_editado["Volumen (L)"] * df_editado["Grado (GL)"] / 100).sum()

# Mostrar Totales en una tablita estética
st.write("### 📊 Totales de la Mezcla")
st.table(pd.DataFrame({
    "Volumen Total (L)": [f"{total_vol:,.2f}"],
    "LAA Total": [f"{total_laa:,.2f}"]
}))

st.divider()

# --- BLOQUE DE CÁLCULO FINAL ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("Grado Final")
    if st.button("Calcular Cf"):
        if total_vol > 0:
            cf = (total_laa * 100) / total_vol
            st.metric("Resultado Cf", f"{cf:.2f} GL")
        else:
            st.error("Ingrese volúmenes.")

with c2:
    st.subheader("Ajuste con Agua")
    grado_obj = st.number_input("Grado Objetivo:", value=40.0, step=0.1)
    if st.button("Calcular Agua Necesaria (Va)"):
        if grado_obj > 0:
            vf = (total_laa * 100) / grado_obj
            va = vf - total_vol
            st.metric("Agua a añadir (Va)", f"{max(0, va):,.2f} L", delta_color="inverse")
            st.write(f"Volumen Final esperado: {vf:,.2f} L")
