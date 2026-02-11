import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Calculadora DUSA", layout="wide")

st.title("🧪 Calculadora de Mezclas DUSA")

# 1. Inicialización de datos
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame([
        {"Componente": "Agua", "Volumen (L)": 0.0, "Grado (GL)": 0.0},
        {"Componente": "Alcohol base", "Volumen (L)": 1000.0, "Grado (GL)": 96.0}
    ])

# 2. Cálculo de LAA para la tabla
df_con_laa = st.session_state.df.copy()
df_con_laa["LAA"] = (df_con_laa["Volumen (L)"] * df_con_laa["Grado (GL)"]) / 100

# 3. EDITOR ÚNICO (Sin columna de números a la izquierda)
st.subheader("Matriz de Mezcla")
df_editado = st.data_editor(
    df_con_laa,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True, # AQUÍ ELIMINAMOS LA FUCKING COLUMNA DE NÚMEROS
    column_config={
        "Componente": st.column_config.TextColumn("Componente", width="medium"),
        "Volumen (L)": st.column_config.NumberColumn("Volumen (L)", format="%.2f"),
        "Grado (GL)": st.column_config.NumberColumn("Grado (GL)", format="%.2f"),
        "LAA": st.column_config.NumberColumn("LAA", format="%.2f", disabled=True),
    }
)

# Guardar cambios sin que se pierdan
st.session_state.df = df_editado[["Componente", "Volumen (L)", "Grado (GL)"]]

# 4. TOTALES (Sin decimales y con punto de miles)
v_total = int(df_editado["Volumen (L)"].sum())
laa_total = int(df_editado["LAA"].sum())

st.write("### 📊 Totales")
c1, c2 = st.columns(2)
# Formato con punto para miles y sin decimales
with c1:
    st.metric("TOTAL VOLUMEN (L)", f"{v_total:,.0f}".replace(",", "."))
with c2:
    st.metric("TOTAL LAA", f"{laa_total:,.0f}".replace(",", "."))

st.divider()

# 5. CÁLCULOS FINALES
col_a, col_b = st.columns(2)

with col_a:
    if st.button("CALCULAR GRADO FINAL (Cf)"):
        if v_total > 0:
            # Aquí sí usamos decimales para el grado porque es precisión de laboratorio
            laa_preciso = (df_editado["Volumen (L)"] * df_editado["Grado (GL)"] / 100).sum()
            cf = (laa_preciso * 100) / df_editado["Volumen (L)"].sum()
            st.success(f"### Cf: {cf:.2f} °GL")

with col_b:
    grado_obj = st.number_input("Grado Objetivo (°GL):", value=40.0)
    if st.button("CALCULAR AGUA NECESARIA (Va)"):
        laa_preciso = (df_editado["Volumen (L)"] * df_editado["Grado (GL)"] / 100).sum()
        vol_act = df_editado["Volumen (L)"].sum()
        if grado_obj > 0:
            vf = (laa_preciso * 100) / grado_obj
            va = vf - vol_act
            # Resultado de agua con punto de miles
            va_formateada = f"{max(0, va):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            st.warning(f"### Añadir: {va_formateada} L de Agua")
