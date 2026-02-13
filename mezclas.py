import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora DUSA", layout="centered")

# --- FUNCIONES DE APOYO ---
def formatear_venezuela(valor, decimales=0):
    val = float(valor) if valor else 0.0
    texto = "{:,.{}f}".format(val, decimales)
    return texto.translate(str.maketrans(",.", ".,"))

# --- ENCABEZADO COMÚN ---
st.image("https://dusa.com.ve/wp-content/uploads/2020/10/Logo-Original.png", width=180)
st.markdown('<h2 style="font-size: 24px; margin-bottom: 0px; margin-top: -20px;">🧮 Calculadora de Mezclas</h2>', unsafe_allow_html=True)
st.markdown("""**Destilerías Unidas, S.A.** *© Edwin Freitez*""")

tab1, tab2 = st.tabs(["📏 Por Volumen (L)", "📊 Explosión de Receta (%)"])

# =========================================================
# PESTAÑA 1: CÁLCULO POR VOLUMEN (Sin cambios)
# =========================================================
with tab1:
    if 'lista_mezcla' not in st.session_state:
        st.session_state.lista_mezcla = [{"Componente": "Agua", "Volumen (L)": 0, "Grado (°GL)": 0.0}]

    with st.form("nuevo_componente_vol", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        nombre = c1.text_input("Tipo de Alcohol:")
        vol = c2.number_input("Volumen (L):", min_value=0, step=1, value=None, key="vol_v")
        grado = c3.number_input("Grado (°GL):", min_value=0.0, max_value=100.0, step=0.1, value=None, key="grado_v")
        if st.form_submit_button("➕ Añadir a la mezcla"):
            if nombre and vol is not None and grado is not None:
                st.session_state.lista_mezcla.append({"Componente": nombre, "Volumen (L)": int(vol), "Grado (°GL)": grado})
            else:
                st.error("Por favor, complete todos los campos.")

    df_v = pd.DataFrame(st.session_state.lista_mezcla)
    vt_v = df_v["Volumen (L)"].sum()
    df_v["LAA"] = (df_v["Volumen (L)"] * df_v["Grado (°GL)"]) / 100
    df_v["% Vol"] = df_v["Volumen (L)"].apply(lambda x: (x / vt_v * 100) if vt_v > 0 else 0.0)

    df_edit_v = st.data_editor(df_v, num_rows="dynamic", use_container_width=True, hide_index=True, key="ed_v",
                               column_config={
                                   "Volumen (L)": st.column_config.NumberColumn(format="%d"),
                                   "Grado (°GL)": st.column_config.NumberColumn(format="%.1f"),
                                   "LAA": st.column_config.NumberColumn(format="%.0f", disabled=True),
                                   "% Vol": st.column_config.NumberColumn(format="%.1f %%", disabled=True)
                               })
    st.session_state.lista_mezcla = df_edit_v[["Componente", "Volumen (L)", "Grado (°GL)"]].to_dict('records')

    v_tot_v = int(df_edit_v["Volumen (L)"].sum())
    laa_tot_v = df_edit_v["LAA"].sum()
    grado_f_v = (laa_tot_v * 100) / v_tot_v if v_tot_v > 0 else 0.0

    st.write("---")
    t1, t2, t3 = st.columns(3)
    t1.metric("VOLUMEN TOTAL", f"{formatear_venezuela(v_tot_v, 0)} L")
    t2.metric("LAA TOTAL", formatear_venezuela(laa_tot_v, 0))
    t3.metric("GRADO FINAL", f"{formatear_venezuela(grado_f_v, 2)} °GL")

    st.divider()
    g_obj_v = st.number_input("Grado Deseado (°GL):", value=40.0, key="obj_v")
    if st.button("CALCULAR AGUA", use_container_width=True, key="btn_v"):
        vf = (laa_tot_v * 100) / g_obj_v
        va = max(0, vf - v_tot_v)
        st.warning(f"### Añadir: {formatear_venezuela(va, 0)} L")

# =========================================================
# PESTAÑA 2: EXPLOSIÓN DE RECETA (%) - LA MEJORA
# =========================================================
with tab2:
    if 'lista_pct' not in st.session_state:
        st.session_state.lista_pct = []

    c_conf1, c_conf2 = st.columns(2)
    tipo_base = c_conf1.selectbox("Base del Porcentaje:", ["% V/V (Volumen Líquido)", "% LAA/LAA (Alcohol Puro)"])
    vol_receta = c_conf2.number_input("Volumen Final Mezcla (L):", min_value=0, value=1000)
    grado_receta = st.number_input("Grado Objetivo de la Receta (°GL):", value=40.0)

    # Calculamos el LAA total que DEBE tener la mezcla final
    laa_objetivo_total = (vol_receta * grado_receta) / 100

    with st.form("nuevo_pct", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        n_p = c1.text_input("Componente:")
        p_p = c2.number_input("% en Receta:", min_value=0.0, max_value=100.0, step=0.1, value=None)
        g_p = c3.number_input("Grado (°GL):", min_value=0.1, max_value=100.0, step=0.1, value=None)
        if st.form_submit_button("➕ Añadir"):
            if n_p and p_p is not None and g_p is not None:
                st.session_state.lista_pct.append({"Componente": n_p, "%": p_p, "Grado (°GL)": g_p})

    df_p = pd.DataFrame(st.session_state.lista_pct)
    
    if not df_p.empty:
        if "V/V" in tipo_base:
            # El % es sobre el volumen total de la mezcla (L)
            df_p["Volumen (L)"] = (df_p["%"] / 100) * vol_receta
            df_p["LAA"] = (df_p["Volumen (L)"] * df_base_p["Grado (°GL)"]) / 100 if 'Grado (°GL)' in df_p else 0
        else:
            # El % es sobre el LAA total objetivo
            df_p["LAA"] = (df_p["%"] / 100) * laa_objetivo_total
            df_p["Volumen (L)"] = (df_p["LAA"] * 100) / df_p["Grado (°GL)"]

        df_p["LAA"] = (df_p["Volumen (L)"] * df_p["Grado (°GL)"]) / 100 # Recalcular para asegurar

        df_ed_p = st.data_editor(df_p, num_rows="dynamic", use_container_width=True, hide_index=True, key="ed_p",
                                   column_config={
                                       "%": st.column_config.NumberColumn("%", format="%.1f %%"),
                                       "Volumen (L)": st.column_config.NumberColumn("Lts a medir", format="%d", disabled=True),
                                       "LAA": st.column_config.NumberColumn("LAA", format="%.1f", disabled=True)
                                   })
        st.session_state.lista_pct = df_ed_p[["Componente", "%", "Grado (°GL)"]].to_dict('records')

        sum_pct = df_ed_p["%"].sum()
        sum_vol_alc = df_ed_p["Volumen (L)"].sum()
        sum_laa_alc = df_ed_p["LAA"].sum()

        if sum_pct > 100.1: st.error(f"¡Cuidado! El total es {sum_pct}%. Excede el 100%.")

        st.write("---")
        # CALCULO DE AGUA AUTOMÁTICO PARA LA RECETA
        agua_necesaria = max(0, vol_receta - sum_vol_alc)
        
        c_res1, c_res2 = st.columns(2)
        c_res1.metric("LITROS DE ALCOHOLES", f"{formatear_venezuela(sum_vol_alc, 0)} L")
        c_res2.metric("AGUA PARA COMPLETAR", f"{formatear_venezuela(agua_necesaria, 0)} L")
        
        st.info(f"💡 Para obtener **{vol_receta}L** a **{grado_receta}°GL**, necesitas un total de **{laa_objetivo_total} LAA**. "
                f"Tus alcoholes aportan **{formatear_venezuela(sum_laa_alc, 1)} LAA**.")

    if st.button("🗑️ Resetear Receta", key="res_p"):
        st.session_state.lista_pct = []
        st.rerun()
