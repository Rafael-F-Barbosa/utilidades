import streamlit as st
import pandas as pd
import plotly.express as px
import time

# Título da dashboard
st.set_page_config(page_title="Dashboard Exemplo", layout="wide")
st.title("📊 Dashboard de Vendas (Dados Fictícios)")

# Botão para recarregar os dados
if st.button("🔄 Recarregar Dados"):
    st.session_state["dados_cache"] = None  # Invalida o cache

# Função de geração de dados com cache condicional
@st.cache_data(show_spinner=True)
def gerar_dados():
    print("Gerando dados novamente!\n\n")
    time.sleep(5)

    datas = pd.date_range(start="2024-01-01", periods=12, freq="ME")
    vendas_por_mes = pd.DataFrame({
        "Mês": datas,
        "Vendas": [200 + i*50 + (i%3)*30 for i in range(12)]
    })

    categorias = ["Eletrônicos", "Roupas", "Alimentos", "Livros"]
    vendas_categoria = pd.DataFrame({
        "Categoria": categorias,
        "Vendas": [1200, 950, 600, 300]
    })

    regioes = ["Sul", "Sudeste", "Nordeste", "Norte", "Centro-Oeste"]
    vendas_regiao = pd.DataFrame({
        "Região": regioes,
        "Vendas": [400, 800, 300, 150, 250]
    })

    return vendas_por_mes, vendas_categoria, vendas_regiao

# Limpa o cache se solicitado
if "dados_cache" not in st.session_state or st.session_state["dados_cache"] is None:
    vendas_mes, vendas_categoria, vendas_regiao = gerar_dados()
    st.session_state["dados_cache"] = (vendas_mes, vendas_categoria, vendas_regiao)
else:
    vendas_mes, vendas_categoria, vendas_regiao = st.session_state["dados_cache"]

# Visualizações
vendas_mes = vendas_mes.reset_index(drop=True)
st.subheader("📈 Vendas Mensais")
fig_linha = px.line(vendas_mes, x="Mês", y="Vendas", markers=True)
st.plotly_chart(fig_linha, use_container_width=True)

st.subheader("📊 Vendas por Categoria")
fig_barras = px.bar(vendas_categoria, x="Categoria", y="Vendas", color="Categoria")
st.plotly_chart(fig_barras, use_container_width=True)

st.subheader("🍩 Distribuição de Vendas por Região")
fig_donut = px.pie(vendas_regiao, names="Região", values="Vendas", hole=0.5)
st.plotly_chart(fig_donut, use_container_width=True)
