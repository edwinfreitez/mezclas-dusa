import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora DUSA", layout="centered")

st.title("🧪 Calculadora de Mezclas")

# 1. Inicialización de la lista
if 'lista_mezcla' not in st.session_state:
    st.session_state.lista_mezcla = [
        {"Componente": "Agua", "Volumen (L)": 0, "Grado (GL)": 0.0}
    ]

# 2. Formulario de carga
with st.expander("➕ Añadir nuevo componente", expanded=True):
    with st.form("nuevo_componente", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        nombre = c1.text_input("Tipo del Alcohol:")
        vol = c2.number_input("Volumen (L):", min_value=0, step=1)
        grado = c3.number_input("Grado (GL):", min_value=0.0, max_value=100.0, step=0.1)
        
        submit = st.form_submit_button("Añadir a la mezcla")
        if submit:
            st.session_state.lista_mezcla.append({
                "Componente": nombre, 
                "Volumen (L)": int(vol), 
                "Grado (°GL)": grado
            })

# 3. Procesamiento de datos para la Matriz
df_base = pd.DataFrame(st.session_state.lista_mezcla)
v_total = df_base["Volumen (L)"].sum()

# Cálculos de LAA y %
df_base["LAA"] = (df_base["Volumen (L)"] * df_base["Grado (GL)"]) / 100
if v_total > 0:
    df_base["% Vol"] = (df_base["Volumen (L)"] / v_total) * 100
else:
    df_base["% Vol"] = 0.0

# 4. Matriz de Mezcla Actual con opción de ELIMINAR
st.subheader("Matriz de Mezcla Actual")
st.info("Para eliminar una fila, selecciónela y pulse la tecla 'Suprimir' o use el menú del editor.")

# Formateo de números al estilo solicitado (Punto miles, Coma decimal)
# Nota: Streamlit usa formatos locales, pero aquí forzamos la visualización
df_editado = st.data_editor(
    df_base,
    num_rows="dynamic", # Permite borrar filas seleccionándolas
    use_container_width=True,
    hide_index=True,
    column_config={
        "Componente": st.column_config.TextColumn("Componente"),
        "Volumen (L)": st.column_config.NumberColumn("Volumen (L)", format="%d"), # Sin decimales
        "Grado (GL)": st.column_config.NumberColumn("Grado (GL)", format="%.1f"),
        "LAA": st.column_config.NumberColumn("LAA", format="%.2f"),
        "% Vol": st.column_config.NumberColumn("% Vol", format="%.1f %%")
    }
)

# Sincronizar cambios (por si borras filas en el editor)
st.session_state.lista_mezcla = df_editado[["Componente", "Volumen (L)", "Grado (GL)"]].to_dict('records')

# 5. Totales
laa_total = df_editado["LAA"].sum()

st.write("### 📊 Totales")
t1, t2 = st.columns(2)

# Función para formatear a miles con punto
def fmt_vzla(valor, decimales=0):
    formato = "{:,.0f}" if decimales == 0 else "{:,.2f}"
    # Cambiamos la convención americana (,) por (.) y (.) por (,)
    res = formato.format(valor).replace(",", "X").replace(".", ",").replace("X", ".")
    return res

t1.metric("TOTAL VOLUMEN (L)", fmt_vzla(v_total))
t2.metric("TOTAL LAA", fmt_vzla(laa_total, 0))

st.divider()

# 6. Cálculos Finales
col_a, col_b = st.columns(2)

with col_a:
    if st.button("CALCULAR GRADO FINAL"):
        if v_total > 0:
            cf = (laa_total * 100) / v_total
            st.success(f"###  {fmt_vzla(cf, 2)} °GL")

with col_b:
    grado_obj = st.number_input("Grado deseado (°GL):", value=40.0)
    if st.button("CALCULAR AGUA"):
        if grado_obj > 0:
            vf = (laa_total * 100) / grado_obj
            va = vf - v_total
            st.warning(f"### Añadir: {fmt_vzla(max(0, va))} L")

if st.button("🗑️ Resetear Matriz"):
    st.session_state.lista_mezcla = [{"Componente": "Agua", "Volumen (L)": 0, "Grado (GL)": 0.0}]
    st.rerun()
