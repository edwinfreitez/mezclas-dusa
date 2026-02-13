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
# PESTAÑA 1: CÁLCULO POR VOLUMEN (Sin cambios)
# =========================================================
with tab1:
    if 'lista_mezcla' not in st.session_state:
        st.session_state.lista_mezcla = [{"Componente": "Agua", "Volumen (L)": 0, "Grado (°GL)": 0.0}]

    with st.form("nuevo_componente_vol", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        nombre = c1.text_input("Tipo de Alcohol:")
        vol = c2.number_input("Volumen (L):", min_value=0, step=1, value=None)
        grado = c3.number_input("Grado (°GL):", min_value=0.0, max_value=100.0, step=0.1, value=None)
        if st.form_submit_button("➕ Añadir"):
            if nombre and vol is not None and grado is not None:
                st.session_state.lista_mezcla.append({"Componente": nombre, "Volumen (L)": int(vol), "Grado (°GL)": grado})

    df_v = pd.DataFrame(st.session_state.lista_mezcla)
    vt_v = df_v["Volumen (L)"].sum()
    df_v["LAA"] = (df_v["Volumen (L)"] * df_v["Grado (°GL)"]) / 100
    
    df_edit_v = st.data_editor(df_v, num_rows="dynamic", use_container_width=True, hide_index=True, key="ed_v")
    st.session_state.lista_mezcla = df_edit_v[["Componente", "Volumen (L)", "Grado (°GL)"]].to_dict('records')

    v_tot_v = int(df_edit_v["Volumen (L)"].sum())
    laa_tot_v = df_edit_v["LAA"].sum()
    grado_f_v = (laa_tot_v * 100) / v_tot_v if v_tot_v > 0 else 0.0

    st.write("---")
    t1, t2, t3 = st.columns(3)
    t1.metric("VOLUMEN TOTAL", f"{formatear_venezuela(v_tot_v, 0)} L")
    t2.metric("LAA TOTAL", formatear_venezuela(laa_tot_v, 2))
    t3.metric("GRADO FINAL", f"{formatear_venezuela(grado_f_v, 2)} °GL")

# =========================================================
# PESTAÑA 2: EXPLOSIÓN DE RECETA (%) - LÓGICA CORREGIDA
# =========================================================
with tab2:
    if 'lista_pct' not in st.session_state:
        st.session_state.lista_pct = []

    c_conf1, c_conf2 = st.columns(2)
    vol_final_deseado = c_conf1.number_input("Volumen Final Mezcla (L):", min_value=1, value=1000)
    grado_final_deseado = c_conf2.number_input("Grado Final Deseado (°GL):", value=40.0)

    # El LAA total que debe contener la mezcla para cumplir el objetivo
    laa_total_requerido = (vol_final_deseado * grado_final_deseado) / 100

    with st.form("nuevo_pct", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        n_p = c1.text_input("Componente:")
        p_p = c2.number_input("% en la base:", min_value=0.0, max_value=100.0, step=0.1, value=None)
        g_p = c3.number_input("Grado del componente (°GL):", min_value=0.1, max_value=100.0, step=0.1, value=None)
        if st.form_submit_button("➕ Añadir"):
            if n_p and p_p is not None and g_p is not None:
                st.session_state.lista_pct.append({"Componente": n_p, "%": p_p, "Grado (°GL)": g_p})

    df_p = pd.DataFrame(st.session_state.lista_pct)
    
    if not df_p.empty:
        # 1. Calculamos el Grado Promedio Ponderado de la base de alcoholes (Grado Mezcla Alcoholes)
        # Grado Mezcla = Suma( %_i * Grado_i ) / Suma( %_i )
        suma_productos = (df_p["%"] * df_p["Grado (°GL)"]).sum()
        suma_pct = df_p["%"].sum()
        grado_mezcla_alcoholes = suma_productos / suma_pct if suma_pct > 0 else 0

        # 2. Calculamos cuánto LAA debe aportar cada componente
        # LAA_i = LAA_Total_Requerido * ( %_i / Suma_Total_% )
        df_p["LAA"] = laa_total_requerido * (df_p["%"] / suma_pct)
        
        # 3. Calculamos el Volumen (L) de cada componente para dar ese LAA
        # Vol_i = LAA_i * 100 / Grado_i
        df_p["Volumen (L)"] = (df_p["LAA"] * 100) / df_p["Grado (°GL)"]

        df_ed_p = st.data_editor(df_p, num_rows="dynamic", use_container_width=True, hide_index=True, key="ed_p",
                                   column_config={
                                       "%": st.column_config.NumberColumn("% Relativo", format="%.1f %%"),
                                       "Volumen (L)": st.column_config.NumberColumn("Lts a añadir", format="%.2f"),
                                       "LAA": st.column_config.NumberColumn("LAA aporte", format="%.2f", disabled=True)
                                   })
        
        st.session_state.lista_pct = df_ed_p[["Componente", "%", "Grado (°GL)"]].to_dict('records')

        vol_total_alcoholes = df_ed_p["Volumen (L)"].sum()
        agua_a_añadir = max(0.0, vol_final_deseado - vol_total_alcoholes)

        st.write("---")
        if abs(suma_pct - 100) > 0.1:
            st.warning(f"⚠️ La suma de porcentajes es {suma_pct}%. Se recomienda que sumen 100% para evitar confusiones.")

        c_res1, c_res2, c_res3 = st.columns(3)
        c_res1.metric("VOL. ALCOHOLES", f"{formatear_venezuela(vol_total_alcoholes, 2)} L")
        c_res2.metric("AGUA A AÑADIR", f"{formatear_venezuela(agua_a_añadir, 2)} L")
        c_res3.metric("LAA TOTAL", f"{formatear_venezuela(laa_total_requerido, 2)}")

        st.success(f"✅ Para obtener **{vol_final_deseado} L** a **{grado_final_deseado}°GL**, mezcle los alcoholes arriba indicados y complete con **{formatear_venezuela(agua_a_añadir, 2)} L** de agua.")

    if st.button("🗑️ Resetear Pestaña", key="res_p"):
        st.session_state.lista_pct = []
        st.rerun()
