import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora DUSA", layout="wide")

st.title("🧪 Calculadora de Mezclas DUSA")

# 1. Inicialización de datos (La primera fila siempre es Agua)
if 'df_mezcla' not in st.session_state:
    st.session_state.df_mezcla = pd.DataFrame([
        {"Componente": "Agua", "Volumen (L)": 0.0, "Grado (GL)": 0.0},
        {"Componente": "Alcohol base", "Volumen (L)": 1000.0, "Grado (GL)": 96.0}
    ])

# 2. Interfaz de edición
st.subheader("Carga de Componentes")
st.info("La columna LAA se calcula automáticamente. Use el (+) para añadir más alcoholes.")

# El editor de datos: ocultamos la columna de índice ("_index") para que no estorbe
df_editado = st.data_editor(
    st.session_state.df_mezcla,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True, # AQUÍ QUITAMOS LA COLUMNA QUE NO SABÍAS QUÉ ERA
    column_config={
        "Componente": st.column_config.TextColumn("Componente", width="medium"),
        "Volumen (L)": st.column_config.NumberColumn("Volumen (L)", format="%.2f"),
        "Grado (GL)": st.column_config.NumberColumn("Grado (GL)", format="%.2f"),
    }
)

# Guardamos los cambios en el estado
st.session_state.df_mezcla = df_editado

# 3. CÁLCULOS AUTOMÁTICOS (Esto ocurre cada vez que tocas un número)
# Calculamos LAA para cada fila: (V * GL) / 100
df_resultado = df_editado.copy()
df_resultado["LAA"] = (df_resultado["Volumen (L)"] * df_resultado["Grado (GL)"]) / 100

# Calculamos Totales
total_v = df_resultado["Volumen (L)"].sum()
total_laa = df_resultado["LAA"].sum()

# 4. Mostrar la tabla con los LAA calculados
st.write("### Vista Previa de Cálculos por Fila")
st.dataframe(df_resultado, use_container_width=True, hide_index=True)

# 5. FILA DE TOTALES (Estilo resumen rápido)
st.markdown("---")
c_tot1, c_tot2 = st.columns(2)
with c_tot1:
    st.metric("TOTAL VOLUMEN (L)", f"{total_v:,.2f}")
with c_tot2:
    st.metric("TOTAL LAA", f"{total_laa:,.2f}")

st.divider()

# 6. BLOQUE DE RESULTADOS FINALES
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Obtener Grado Final")
    if st.button("Calcular Cf"):
        if total_v > 0:
            cf = (total_laa * 100) / total_v
            st.success(f"**Grado Final: {cf:.2f} °GL**")
        else:
            st.error("Faltan datos de volumen.")

with col2:
    st.subheader("2. Ajustar a Grado Objetivo")
    grado_obj = st.number_input("Grado Deseado (°GL):", value=40.0, step=0.1)
    if st.button("Calcular Agua a Añadir"):
        if grado_obj > 0:
            vf_necesario = (total_laa * 100) / grado_obj
            va = vf_necesario - total_v
            st.warning(f"**Añadir: {max(0, va):,.2f} Litros de Agua**")
            st.info(f"Volumen Final: {vf_necesario:,.2f} L")
