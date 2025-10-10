import streamlit as st
import pandas as pd
import plotly.express as px

# Título do app
st.title("📊 Execuções - Status por Período")

# Exemplo de dados (pode ser substituído pelo seu DataFrame real)
data = {
    "execucao": ["Execução 1", "Execução 2", "Execução 3", "Execução 4"],
    "timestamp_inicio": [
        "2025-10-10 08:00:00",
        "2025-10-10 09:30:00",
        "2025-10-10 10:00:00",
        "2025-10-10 10:15:00",
    ],
    "timestamp_termino": [
        "2025-10-10 08:45:00",
        "2025-10-10 10:10:00",
        "2025-10-10 11:00:00",
        "2025-10-10 10:45:00",
    ],
    "status": [1, 2, 1, 3],
}

# Cria DataFrame
df = pd.DataFrame(data)

# Converte colunas para datetime
df["timestamp_inicio"] = pd.to_datetime(df["timestamp_inicio"])
df["timestamp_termino"] = pd.to_datetime(df["timestamp_termino"])

# Mapeia status para texto e cores
status_map = {1: "Sucesso", 2: "Falha", 3: "Em andamento"}
color_map = {"Sucesso": "green", "Falha": "red", "Em andamento": "orange"}

df["status_label"] = df["status"].map(status_map)

# Cria o gráfico tipo "timeline" (semelhante a Gantt)
fig = px.timeline(
    df,
    x_start="timestamp_inicio",
    x_end="timestamp_termino",
    y="execucao",
    color="status_label",
    color_discrete_map=color_map,
    title="Linha do tempo de execuções",
)

# Ajusta layout (eixo X como tempo)
fig.update_layout(
    xaxis_title="Horário",
    yaxis_title="Execução",
    xaxis=dict(showgrid=True),
    yaxis=dict(autorange="reversed"),  # inverte para deixar a 1ª execução em cima
    legend_title="Status",
    hovermode="x unified"
)

# Exibe no Streamlit
st.plotly_chart(fig, use_container_width=True)
