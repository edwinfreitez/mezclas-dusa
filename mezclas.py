import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora DUSA", layout="centered")

# 1. Encabezado con Logo, Título y Firma
st.image("https://dusa.com.ve/wp-content/uploads/2020/10/Logo-Original.png", width=200)
st.title("🧮 Calculadora de Mezclas")
st.markdown("""
**Destilerías Unidas S.A.** *© Edwin Freitez*
""")

# 2. Inicialización de la lista
if 'lista_mezcla' not in st.session_state:
    st.session_state.lista_mezcla = [
        {"Componente": "Agua", "Volumen (L)": 0, "Grado (°GL)": 0.0}
    ]

# 3. Formulario de carga (Mejora: Valores en blanco por defecto)
with st.form("nuevo_componente", clear_on_submit=True):
    c1, c2, c3 = st.columns([2, 1, 1])
    nombre = c1.text_input("Tipo de Alcohol:")
    # value=None hace que el campo aparezca vacío
    vol = c2.number_input("Volumen (L):", min_value=0, step=1, value=None)
    grado = c3.number_input("Grado (°GL):", min_value=0.0, max_value=100.0, step=0.1, value=None)
    
    submit = st.form_submit_button("➕ Añadir a la mezcla")
    if submit:
        # Validamos que no estén vacíos antes de añadir
        if nombre and vol is not None and grado is not None:
            st.session_state.lista_mezcla.append({
                "Componente": nombre, 
                "Volumen (L)": int(vol), 
                "Grado (°GL)": grado
            })
        else:
            st.error("Por favor, complete todos los campos.")

# 4. Función de Formateo (Punto miles, Coma decimal)
def formatear_venezuela(valor, decimales=0):
    val = float(valor) if valor else 0.0
    texto = "{:,.{}f}".format(val, decimales)
    return texto.translate(str.maketrans(",.", ".,"))

# 5. Matriz Editable
df_base = pd.DataFrame(st.session_state.lista_mezcla)

# Cálculos informativos previos
v_total_temp = df_base["Volumen (L)"].sum()
df_base["LAA"] = (df_base["Volumen (L)"] * df_base["Grado (°GL)"]) / 100
df_base["% Vol"] = df_base["Volumen (L)"].apply(lambda x: (x / v_total_temp * 100) if v_total_temp > 0 else 0.0)

df_editado = st.data_editor(
    df_base,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "Componente": st.column_config.TextColumn("Componente"),
        "Volumen (L)": st.column_config.NumberColumn("Volumen (L)", format="%d"),
        "Grado (°GL)": st.column_config.NumberColumn("Grado (°GL)", format="%.1f"),
        "LAA": st.column_config.NumberColumn("LAA", format="%.0f", disabled=True),
        "% Vol": st.column_config.NumberColumn("% Vol", format="%.1f %%", disabled=True)
    }
)

# Sincronización
st.session_state.lista_mezcla = df_editado[["Componente", "Volumen (L)", "Grado (°GL)"]].to_dict('records')

# 6. Totales
v_total = int(df_editado["Volumen (L)"].sum())
laa_total = df_editado["LAA"].sum()

t1, t2 = st.columns(2)
t1.metric(label="TOTAL VOLUMEN (L)", value=formatear_venezuela(v_total, 0))
t2.metric(label="TOTAL LAA", value=formatear_venezuela(laa_total, 0))

st.divider()

# 7. Cálculos Finales
col_a, col_b = st.columns(2)

with col_a:
    if st.button("CALCULAR GRADO FINAL"):
        if v_total > 0:
            cf = (laa_total * 100) / v_total
            st.success(f"### {formatear_venezuela(cf, 2)} °GL")

with col_b:
    # El grado deseado suele ser 40.0, lo dejamos por defecto para agilizar
    grado_obj = st.number_input("Grado Deseado (°GL):", value=40.0)
    if st.button("CALCULAR AGUA"):
        if grado_obj > 0:
            vf = (laa_total * 100) / grado_obj
            va = vf - v_total
            st.warning(f"### Añadir: {formatear_venezuela(max(0, va), 0)} L")

if st.button("🗑️ Resetear Matriz"):
    st.session_state.lista_mezcla = [{"Componente": "Agua", "Volumen (L)": 0, "Grado (°GL)": 0.0}]
    st.rerun()
