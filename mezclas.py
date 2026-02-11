import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora DUSA", layout="centered")

st.title("🧪 Calculadora de Mezclas")

# 1. Inicialización de la lista
if 'lista_mezcla' not in st.session_state:
    st.session_state.lista_mezcla = [
        {"Componente": "Agua", "Volumen (L)": 0, "Grado (°GL)": 0.0}
    ]

# 2. Formulario de carga
with st.form("nuevo_componente", clear_on_submit=True):
    c1, c2, c3 = st.columns([2, 1, 1])
    nombre = c1.text_input("Tipo de Alcohol:")
    vol = c2.number_input("Volumen (L):", min_value=0, step=1)
    grado = c3.number_input("Grado (°GL):", min_value=0.0, max_value=100.0, step=0.1)
    
    submit = st.form_submit_button("➕ Añadir a la mezcla")
    if submit:
        st.session_state.lista_mezcla.append({
            "Componente": nombre, 
            "Volumen (L)": int(vol), 
            "Grado (°GL)": grado
        })

# 3. Procesamiento de datos y Cálculos
df_base = pd.DataFrame(st.session_state.lista_mezcla)

# --- MEJORA 1: Matriz editable para colocar volumen al Agua y borrar filas ---
# Usamos data_editor como única tabla, permitiendo añadir/borrar y editar el volumen
df_editado = st.data_editor(
    df_base,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "Componente": st.column_config.TextColumn("Componente"),
        "Volumen (L)": st.column_config.NumberColumn("Volumen (L)", format="%d"),
        "Grado (°GL)": st.column_config.NumberColumn("Grado (°GL)", format="%.1f")
    }
)

# Sincronizamos cambios (esto permite que lo que edites se mantenga)
st.session_state.lista_mezcla = df_editado.to_dict('records')

# Cálculos basados en la tabla editada
v_total = int(df_editado["Volumen (L)"].sum())
df_editado["LAA"] = (df_editado["Volumen (L)"] * df_editado["Grado (°GL)"]) / 100

if v_total > 0:
    df_editado["% Vol"] = (df_editado["Volumen (L)"] / v_total) * 100
else:
    df_editado["% Vol"] = 0.0

# --- FUNCIÓN DE FORMATEO BLINDADA (Punto para miles, Coma para decimales) ---
def formatear_venezuela(valor, decimales=0):
    val = float(valor) if valor else 0.0
    if decimales == 0:
        texto = "{:,.0f}".format(val)
    else:
        texto = "{:,.{}f}".format(val, decimales)
    tabla = str.maketrans(",.", ".,")
    return texto.translate(tabla)

# Matriz Visual (La que mostramos para lectura con los puntos y comas)
# Nota: Mostramos df_editado pero con formato visual para LAA y %
df_visual = df_editado.copy()
df_visual["Volumen (L)"] = df_visual["Volumen (L)"].apply(lambda x: formatear_venezuela(x, 0))
df_visual["Grado (°GL)"] = df_visual["Grado (°GL)"].apply(lambda x: formatear_venezuela(x, 1))
df_visual["LAA"] = df_visual["LAA"].apply(lambda x: formatear_venezuela(x, 0))
df_visual["% Vol"] = df_visual["% Vol"].apply(lambda x: formatear_venezuela(x, 1) + " %")

# --- MEJORA 4: Eliminado subtítulo Matriz de Mezcla Actual ---
# Mostramos la tabla formateada (estática para lectura perfecta)
st.dataframe(df_visual, use_container_width=True, hide_index=True)

# 5. TOTALES CORREGIDOS
laa_total = df_editado["LAA"].sum()

# --- MEJORA 3: Eliminado subtítulo TOTALES ---
t1, t2 = st.columns(2)
t1.metric(label="TOTAL VOLUMEN (L)", value=formatear_venezuela(v_total, 0))
t2.metric(label="TOTAL LAA", value=formatear_venezuela(laa_total, 0))

st.divider()

# 6. Cálculos Finales
col_a, col_b = st.columns(2)

with col_a:
    if st.button("CALCULAR GRADO FINAL"):
        if v_total > 0:
            cf = (laa_total * 100) / v_total
            st.success(f"### {formatear_venezuela(cf, 2)} °GL")

with col_b:
    grado_obj = st.number_input("Grado Deseado (°GL):", value=40.0)
    if st.button("CALCULAR AGUA"):
        if grado_obj > 0:
            vf = (laa_total * 100) / grado_obj
            va = vf - v_total
            st.warning(f"### Añadir: {formatear_venezuela(max(0, va), 0)} L")

if st.button("🗑️ Resetear Matriz"):
    st.session_state.lista_mezcla = [{"Componente": "Agua", "Volumen (L)": 0, "Grado (°GL)": 0.0}]
    st.rerun()
