import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora DUSA", layout="centered")

# --- FUNCIONES DE APOYO ---
def formatear_venezuela(valor, decimales=2):
    val = float(valor) if valor else 0.0
    texto = "{:,.{}f}".format(val, decimales)
    return texto.translate(str.maketrans(",.", ".,"))

# --- ENCABEZADO ---
st.image("https://dusa.com.ve/wp-content/uploads/2020/10/Logo-Original.png", width=180)
st.markdown('<h2 style="font-size: 24px; margin-bottom: 0px; margin-top: -20px;">🧮 Calculadora de Mezclas</h2>', unsafe_allow_html=True)
st.markdown("""**Destilerías Unidas, S.A.** *© Edwin Freitez*""")

tab1, tab2 = st.tabs(["📏 Por Volumen (L)", "📊 Explosión de Receta (%)"])

# =========================================================
# PESTAÑA 1: CÁLCULO POR VOLUMEN
# =========================================================
with tab1:
    if 'lista_mezcla' not in st.session_state:
        st.session_state.lista_mezcla = [{"Componente": "Agua", "Volumen (L)": 0, "Grado (°GL)": 0.0}]

    with st.form("nuevo_componente_vol", clear_on_submit=True):
        c1, c2, c3 = st.columns([1.5, 1, 1]) # Ajuste de ancho de inputs
        nombre = c1.text_input("Tipo de Alcohol:")
        vol = c2.number_input("Volumen (L):", min_value=0, step=1, value=None)
        grado = c3.number_input("Grado (°GL):", min_value=0.0, max_value=100.0, step=0.1, value=None)
        if st.form_submit_button("➕ Añadir a la mezcla"):
            if nombre and vol is not None and grado is not None:
                st.session_state.lista_mezcla.append({"Componente": nombre, "Volumen (L)": int(vol), "Grado (°GL)": grado})
            else:
                st.error("Por favor, complete todos los campos.")

    df_v = pd.DataFrame(st.session_state.lista_mezcla)
    v_total_temp = df_v["Volumen (L)"].sum()
    df_v["LAA"] = (df_v["Volumen (L)"] * df_v["Grado (°GL)"]) / 100
    df_v["% Vol"] = df_v["Volumen (L)"].apply(lambda x: (x / v_total_temp * 100) if v_total_temp > 0 else 0.0)

    # AJUSTE ESTÉTICO: Columnas más estrechas para celular
    df_edit_v = st.data_editor(
        df_v, 
        num_rows="dynamic", 
        use_container_width=True, 
        hide_index=True, 
        key="ed_v",
        column_config={
            "Componente": st.column_config.TextColumn("Comp.", width="small"),
            "Volumen (L)": st.column_config.NumberColumn("Vol(L)", format="%d", width="small"),
            "Grado (°GL)": st.column_config.NumberColumn("°GL", format="%.1f", width="small"),
            "LAA": st.column_config.NumberColumn("LAA", format="%.0f", disabled=True, width="small"),
            "% Vol": st.column_config.NumberColumn("%", format="%.1f%%", disabled=True, width="small")
        }
    )
    st.session_state.lista_mezcla = df_edit_v[["Componente", "Volumen (L)", "Grado (°GL)"]].to_dict('records')

    v_tot_v = int(df_edit_v["Volumen (L)"].sum())
    laa_tot_v = df_edit_v["LAA"].sum()
    grado_f_v = (laa_tot_v * 100) / v_tot_v if v_tot_v > 0 else 0.0

    st.write("---")
    t1, t2, t3 = st.columns(3)
    t1.metric("VOL. TOTAL", f"{formatear_venezuela(v_tot_v, 0)} L")
    t2.metric("LAA TOTAL", formatear_venezuela(laa_tot_v, 0))
    t3.metric("GRADO FINAL", f"{formatear_venezuela(grado_f_v, 2)}°")

    st.divider()
    grado_obj = st.number_input("Grado Deseado (°GL):", value=40.0, key="obj_v")
    if st.button("CALCULAR AGUA", use_container_width=True, key="btn_v"):
        vf = (laa_tot_v * 100) / grado_obj
        va = max(0, vf - v_tot_v)
        st.warning(f"### Añadir: {formatear_venezuela(va, 0)} L")

# =========================================================
# PESTAÑA 2: EXPLOSIÓN DE RECETA (%)
# =========================================================
with tab2:
    if 'lista_pct' not in st.session_state:
        st.session_state.lista_pct = []

    c_conf1, c_conf2 = st.columns(2)
    vol_final_deseado = c_conf1.number_input("Vol. Final (L):", min_value=1, value=1000)
    grado_final_deseado = c_conf2.number_input("°GL Final:", value=40.0)
    
    tipo_base = st.radio("Base del %:", ["% V/V", "% LAA/LAA"], horizontal=True)

    laa_total_requerido = (vol_final_deseado * grado_final_deseado) / 100

    with st.form("nuevo_pct", clear_on_submit=True):
        # DETALLE ESTÉTICO 1: Acortamos el campo Componente en el formulario
        c1, c2, c3 = st.columns([1.5, 1, 1]) 
        n_p = c1.text_input("Componente:")
        p_p = c2.number_input("%:", min_value=0.0, max_value=100.0, step=0.1, value=None)
        g_p = c3.number_input("°GL:", min_value=0.1, max_value=100.0, step=0.1, value=None)
        if st.form_submit_button("➕ Añadir"):
            if n_p and p_p is not None and g_p is not None:
                st.session_state.lista_pct.append({"Componente": n_p, "%": p_p, "Grado (°GL)": g_p})

    df_p = pd.DataFrame(st.session_state.lista_pct)
    
    if not df_p.empty:
        suma_pct = df_p["%"].sum()
        if "% V/V" in tipo_base:
            grado_mezcla_sin_agua = (df_p["%"] * df_p["Grado (°GL)"]).sum() / suma_pct if suma_pct > 0 else 0
            vol_total_alc = (laa_total_requerido * 100) / grado_mezcla_sin_agua if grado_mezcla_sin_agua > 0 else 0
            df_p["Volumen (L)"] = vol_total_alc * (df_p["%"] / suma_pct)
            df_p["LAA"] = (df_p["Volumen (L)"] * df_p["Grado (°GL)"]) / 100
        else:
            df_p["LAA"] = laa_total_requerido * (df_p["%"] / suma_pct)
            df_p["Volumen (L)"] = (df_p["LAA"] * 100) / df_p["Grado (°GL)"]
            vol_total_alc = df_p["Volumen (L)"].sum()
            laa_total_calc = df_p["LAA"].sum()
            grado_mezcla_sin_agua = (laa_total_calc * 100) / vol_total_alc if vol_total_alc > 0 else 0

        # DETALLE ESTÉTICO 2: Columnas con ancho optimizado para móvil
        df_ed_p = st.data_editor(df_p, num_rows="dynamic", use_container_width=True, hide_index=True, key="ed_p",
                                   column_config={
                                       "Componente": st.column_config.TextColumn("Comp.", width="small"),
                                       "%": st.column_config.NumberColumn("%", format="%.1f%%", width="small"),
                                       "Grado (°GL)": st.column_config.NumberColumn("°GL", format="%.1f", width="small"),
                                       "Volumen (L)": st.column_config.NumberColumn("Lts", format="%.1f", disabled=True, width="small"),
                                       "LAA": st.column_config.NumberColumn("LAA", format="%.1f", disabled=True, width="small")
                                   })
        
        st.session_state.lista_pct = df_ed_p[["Componente", "%", "Grado (°GL)"]].to_dict('records')
        vol_total_alcoholes = df_ed_p["Volumen (L)"].sum()
        agua_a_añadir = max(0.0, vol_final_deseado - vol_total_alcoholes)

        st.write("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("LTS ALC.", f"{formatear_venezuela(vol_total_alcoholes, 1)}")
        m2.metric("LTS AGUA", f"{formatear_venezuela(agua_a_añadir, 1)}")
        m3.metric("°GL BASE", f"{formatear_venezuela(grado_mezcla_sin_agua, 1)}")
        m4.metric("LAA REQ.", f"{formatear_venezuela(laa_total_requerido, 1)}")

    if st.button("🗑️ Resetear", key="res_p"):
        st.session_state.lista_pct = []
        st.rerun()
