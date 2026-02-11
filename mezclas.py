import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora DUSA", layout="centered")

# 1. Encabezado con Logo y Título Reducido
st.image("https://dusa.com.ve/wp-content/uploads/2020/10/Logo-Original.png", width=180)

st.markdown('<h2 style="font-size: 24px; margin-bottom: 0px; margin-top: -20px;">🧮 Calculadora de Mezclas</h2>', unsafe_allow_html=True)
st.markdown("""
**Destilerías Unidas S.A.** *© Edwin Freitez*
""")

# 2. Inicialización de la lista
if 'lista_mezcla' not in st.session_state:
    st.session_state.lista_mezcla = [
        {"Componente": "Agua", "Volumen (L)": 0, "Grado (°GL)": 0.0}
    ]

# 3. Formulario de carga
with st.form("nuevo_componente", clear_on_submit=True):
    c1, c2, c3 = st.columns([2, 1, 1])
    nombre = c1.text_input("Tipo de Alcohol:")
    vol = c2.number_input("Volumen (L):", min_value=0, step=1, value=None)
    grado = c3.number_input("Grado (°GL):", min_value=0.0, max_value=100.0, step=0.1, value=None)
    
    submit = st.form_submit_button("➕ Añadir a la mezcla")
    if submit:
        if nombre and vol is not None and grado is not None:
            st.session_state.lista_mezcla.append({
                "Componente": nombre, 
                "Volumen (L)": int(vol), 
                "Grado (°GL)": grado
            })
        else:
            st.error("Complete todos los campos.")

# 4. Función de Formateo para Métricas y Alertas
def formatear_venezuela(valor, decimales=0):
    val = float(valor) if valor else 0.0
    texto = "{:,.{}f}".format(val, decimales)
    return texto.translate(str.maketrans(",.", ".,"))

# 5. Matriz Editable y Cálculos
df_base = pd.DataFrame(st.session_state.lista_mezcla)
v_total_temp = df_base["Volumen (L)"].sum()
df_base["LAA"] = (df_base["Volumen (L)"] * df_base["Grado (°GL)"]) / 100
df_base["% Vol"] = df_base["Volumen (L)"].apply(lambda x: (x / v_total_temp * 100) if v_total_temp > 0 else 0.0)

# CONFIGURACIÓN DE COLUMNAS (Punto 1: Formato Venezuela en la Matriz)
# Nota: Streamlit usa formato de lenguaje. 'de-DE' usa punto para miles y coma para decimal.
df_editado = st.data_editor(
    df_base,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "Componente": st.column_config.TextColumn("Componente"),
        "Volumen (L)": st.column_config.NumberColumn("Volumen (L)", format="%.d", help="Use puntos para miles si es necesario"),
        "Grado (°GL)": st.column_config.NumberColumn("Grado (°GL)", format="%.1f"),
        "LAA": st.column_config.NumberColumn("LAA", format="%.2f", disabled=True),
        "% Vol": st.column_config.NumberColumn("% Vol", format="%.1f %%", disabled=True)
    }
)

st.session_state.lista_mezcla = df_editado[["Componente", "Volumen (L)", "Grado (°GL)"]].to_dict('records')

# 6. PANEL DE CONTROL
v_total = int(df_editado["Volumen (L)"].sum())
laa_total = df_editado["LAA"].sum()
grado_final = (laa_total * 100) / v_total if v_total > 0 else 0.0

st.write("---")
t1, t2, t3 = st.columns(3)
t1.metric(label="TOTAL VOLUMEN", value=f"{formatear_venezuela(v_total, 0)} L")
t2.metric(label="TOTAL LAA", value=formatear_venezuela(laa_total, 0))
t3.metric(label="GRADO FINAL", value=f"{formatear_venezuela(grado_final, 2)} °GL")

st.divider()

# 7. Cálculo de Agua (Punto 2: Reorganizado debajo del input)
col_calc = st.columns(1)[0] # Usamos una sola columna para que todo sea vertical

with col_calc:
    grado_obj = st.number_input("Grado Deseado (°GL):", value=40.0)
    
    if st.button("CALCULAR AGUA (Va)", use_container_width=True):
        if grado_obj > 0:
            vf = (laa_total * 100) / grado_obj
            va = max(0, vf - v_total)
            st.warning(f"### Añadir: {formatear_venezuela(va, 0)} L")

st.write("") # Espaciador
if st.button("🗑️ Resetear Matriz"):
    st.session_state.lista_mezcla = [{"Componente": "Agua", "Volumen (L)": 0, "Grado (°GL)": 0.0}]
    st.rerun()
