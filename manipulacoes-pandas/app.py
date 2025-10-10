import pandas as pd
import streamlit as st

import plotly.express as px

def agrupar_fluxos(df: pd.DataFrame):
    resultado = []
    # Agrupa os jobs por fluxo
    grupos = df.groupby("Nome fluxo")["nome job"].apply(list)
    
    # Converte para o formato desejado
    for fluxo, jobs in grupos.items():
        resultado.append({fluxo: jobs})
    
    return resultado

# Exemplo de uso:
dados = {
    "Nome fluxo": ["fluxo-a", "fluxo-a", "fluxo-b"],
    "nome job": ["job-a", "job-b", "job-c"]
}
df = pd.DataFrame(dados)

# Obtém o array agrupado
resultado = agrupar_fluxos(df)

# Converte o array em um dicionário unificado
fluxo_para_jobs = {list(item.keys())[0]: list(item.values())[0] for item in resultado}

# --- INTERFACE STREAMLIT ---
st.title("Seleção de Fluxo e Job")

# Selectbox de fluxo
fluxo_escolhido = st.selectbox(
    "Escolha um fluxo:",
    list(fluxo_para_jobs.keys())
)

# Selectbox de job filtrado
job_escolhido = st.selectbox(
    "Escolha um job:",
    fluxo_para_jobs[fluxo_escolhido]
)

# Exibe o resultado final
st.write("### Seleção final:")
st.success(f"Fluxo: **{fluxo_escolhido}**, Job: **{job_escolhido}**")