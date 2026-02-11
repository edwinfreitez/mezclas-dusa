import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora DUSA", layout="centered")

st.title("🧪 Calculadora de Mezclas DUSA")

if 'datos' not in st.session_state:
    st.session_state.datos = pd.DataFrame([
        {"Componente": "Alcohol base", "Volumen (L)": 1000.0, "Grado (GL)": 96.0}
    ])

df_editado = st.data_editor(st.session_state.datos, num_rows="dynamic")

laa_total = (df_editado["Volumen (L)"] * df_editado["Grado (GL)"] / 100).sum()
vol_total = df_editado["Volumen (L)"].sum()

st.divider()

c1, c2 = st.columns(2)
with c1:
    if st.button("Calcular Grado Final (Cf)"):
        if vol_total > 0:
            cf = (laa_total * 100) / vol_total
            st.metric("Grado Final (Cf)", f"{cf:.2f} GL")

with c2:
    grado_obj = st.number_input("Grado Objetivo:", value=40.0)
    if st.button("Calcular Agua (Va)"):
        if grado_obj > 0:
            vf = (laa_total * 100) / grado_obj
            va = vf - vol_total
            st.metric("Agua a añadir (Va)", f"{max(0, va):,.2f} L")
