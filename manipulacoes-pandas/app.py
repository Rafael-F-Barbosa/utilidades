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


import pandas as pd
import plotly.express as px
import streamlit as st

# Exemplo de dados de execução
dados = {
    "timestamp_inicio": [
        "2025-10-10 08:00:00",
        "2025-10-10 09:30:00",
        "2025-10-10 10:15:00",
        "2025-10-11 07:50:00",
        "2025-10-11 08:45:00",
    ],
    "timestamp_termino": [
        "2025-10-10 08:45:00",
        "2025-10-10 10:00:00",
        "2025-10-10 11:00:00",
        "2025-10-11 08:30:00",
        "2025-10-11 09:15:00",
    ],
    "status": [1, 2, 3, 1, 2],
}

# Cria o DataFrame
df = pd.DataFrame(dados)

# Converte para datetime
df["timestamp_inicio"] = pd.to_datetime(df["timestamp_inicio"])
df["timestamp_termino"] = pd.to_datetime(df["timestamp_termino"])

# Cria coluna de "dia"
df["dia"] = df["timestamp_inicio"].dt.date

# Mapeia status -> cor e legenda
cores = {1: "green", 2: "red", 3: "orange"}
labels_status = {1: "Sucesso", 2: "Falha", 3: "Em andamento"}

# Substitui status numérico pelo texto para o gráfico
df["status_desc"] = df["status"].map(labels_status)

# --- INTERFACE STREAMLIT ---
st.title("📊 Monitoramento de Execuções")

# Filtro opcional por dia
dias = sorted(df["dia"].unique())
dia_escolhido = st.selectbox("Selecione o dia:", ["Todos"] + [str(d) for d in dias])

if dia_escolhido != "Todos":
    df_filtrado = df[df["dia"] == pd.to_datetime(dia_escolhido).date()]
else:
    df_filtrado = df

# Cria gráfico de Gantt simplificado
fig = px.timeline(
    df_filtrado,
    x_start="timestamp_inicio",
    x_end="timestamp_termino",
    y="dia",
    color="status_desc",
    color_discrete_map={"Sucesso": "green", "Falha": "red", "Em andamento": "orange"},
    title="Execuções por dia e horário",
    labels={"dia": "Dia da Execução", "status_desc": "Status"},
)

# Ajusta layout
fig.update_yaxes(categoryorder="category ascending")
fig.update_layout(
    xaxis_title="Hora",
    yaxis_title="Dia da Execução",
    bargap=0.3,
    height=500,
)

st.plotly_chart(fig, use_container_width=True)
