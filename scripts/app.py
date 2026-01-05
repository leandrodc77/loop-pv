import streamlit as st
import pandas as pd
from src.cli import compute_variables, plot_loop_pv

st.set_page_config(page_title="Loop PV - Método de Chen", layout="centered")

st.title("🫀 Loop Pressão–Volume (Método de Chen)")
st.write("Interface web para cálculo e visualização do Loop PV")

st.header("📥 Dados de Entrada")

PAS = st.number_input("PAS (mmHg)", value=120.0)
PAD = st.number_input("PAD (mmHg)", value=70.0)
VDF = st.number_input("VDF (mL)", value=67.35)
VSF = st.number_input("VSF (mL)", value=34.35)
PET = st.number_input("PET (ms)", value=100.0)
ET  = st.number_input("ET (ms)", value=300.0)
Ees = st.number_input("Ees (mmHg/mL)", value=2.39)
V0  = st.number_input("V0 (mL)", value=-8.21)

if st.button("▶️ Rodar cálculo"):
    data = {
        "PAS": PAS, "PAD": PAD, "VDF": VDF, "VSF": VSF,
        "PET": PET, "ET": ET, "Ees": Ees, "V0": V0
    }

    df = pd.DataFrame([data])
    result = compute_variables(data)

    st.header("📊 Resultados Numéricos")
    st.dataframe(pd.DataFrame([result]))

    st.header("📈 Loop Pressão–Volume")
    fig = plot_loop_pv(data)
    st.pyplot(fig)
