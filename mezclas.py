import streamlit as st

st.title("Prueba de Conexión DUSA")
st.write("Si puedes leer esto, la app funciona. ¡El problema era el código anterior!")

vol = st.number_input("Prueba un número:", value=100)
st.write(f"Escribiste: {vol}")
