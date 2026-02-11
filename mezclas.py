import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora DUSA", layout="centered")

st.title("🧪 Calculadora de Mezclas DUSA")

# 1. Inicialización de la lista de componentes
if 'lista_mezcla' not in st.session_state:
    st.session_state.lista_mezcla = [
        {"Componente": "Agua", "Volumen (L)": 0.0, "Grado (GL)": 0.0, "LAA": 0.0}
    ]

# 2. Formulario para agregar componentes (Evita errores de tipeo y ENTERs infinitos)
with st.expander("➕ Agregar / Editar Componentes", expanded=True):
    with st.form("nuevo_componente", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        nombre = c1.text_input("Nombre del Alcohol:")
        vol = c2.number_input("Volumen (L):", min_value=0.0, step=1.0)
        grado = c3.number_input("Grado (GL):", min_value=0.0, max_value=100.0, step=0.1)
        
        submit = st.form_submit_button("Añadir a la Mezcla")
        if submit:
            laa_calc = (vol * grado) / 100
            st.session_state.lista_mezcla.append({
                "Componente": nombre, 
                "Volumen (L)": vol, 
                "Grado (GL)": grado, 
                "LAA": laa_calc
            })

# 3. Mostrar la Matriz ÚNICA
st.subheader("Matriz de Mezcla Actual")
df_mostrar = pd.DataFrame(st.session_state.lista_mezcla)

# Mostramos la tabla SIN índices y SIN columnas extra
st.dataframe(
    df_mostrar, 
    use_container_width=True, 
    hide_index=True,
    column_config={
        "Volumen (L)": st.column_config.NumberColumn(format="%.2f"),
        "Grado (GL)": st.column_config.NumberColumn(format="%.2f"),
        "LAA": st.column_config.NumberColumn(format="%.2f")
    }
)

# 4. Totales Estéticos (Sin decimales, punto para miles)
v_total = sum(item["Volumen (L)"] for item in st.session_state.lista_mezcla)
laa_total = sum(item["LAA"] for item in st.session_state.lista_mezcla)

st.write("### 📊 Totales")
t1, t2 = st.columns(2)
t1.metric("TOTAL VOLUMEN (L)", f"{int(v_total):,}".replace(",", "."))
t2.metric("TOTAL LAA", f"{int(laa_total):,}".replace(",", "."))

# 5. Cálculos Finales
st.divider()
col_a, col_b = st.columns(2)

with col_a:
    if st.button("CALCULAR GRADO FINAL (Cf)"):
        if v_total > 0:
            cf = (laa_total * 100) / v_total
            st.success(f"### Cf: {cf:.2f} °GL")

with col_b:
    grado_obj = st.number_input("Grado Objetivo (°GL):", value=40.0)
    if st.button("CALCULAR AGUA (Va)"):
        if grado_obj > 0:
            vf = (laa_total * 100) / grado_obj
            va = vf - v_total
            va_fmt = f"{max(0, va):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            st.warning(f"### Añadir: {va_fmt} L")

# Botón para resetear todo
if st.button("🗑️ Borrar toda la mezcla"):
    st.session_state.lista_mezcla = [{"Componente": "Agua", "Volumen (L)": 0.0, "Grado (GL)": 0.0, "LAA": 0.0}]
    st.rerun()
