import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import os

# if not st.user.is_logged_in:
#     if st.button("Log in"):
#         st.login()
# else:
#     if st.button("Log out"):
#         st.logout()
#     st.write(f"Hello, {st.user.name}!")

load_dotenv('/home/rafael/utilidades/projeto-dash-python/.env')


# Config da página
st.set_page_config(page_title="Dashboard Exemplo", layout="wide")
st.title(f"📊 {os.environ.get('VARIAVEL_NECESSARIA')} (Dados Fictícios)")

# Aba simulada via st.radio
aba = st.radio("Escolha uma aba:", ["Resumo", "Por Categoria", "Por Região"], horizontal=True)

# Botão para recarregar
if st.button("🔄 Recarregar Dados"):
    st.cache_data.clear()  # Limpa todo cache de dados

# Funções separadas com cache
@st.cache_data(show_spinner=True)
def gerar_dados_mensais():
    # time.sleep(4)
    datas = pd.date_range(start="2024-01-01", periods=12, freq="ME")
    return pd.DataFrame({
        "Mês": datas,
        "Vendas": [200 + i * 50 + (i % 3) * 30 for i in range(12)]
    })

@st.cache_data(show_spinner=True)
def gerar_dados_categoria():
    # time.sleep(4)
    return pd.DataFrame({
        "Categoria": ["Eletrônicos", "Roupas", "Alimentos", "Livros"],
        "Vendas": [1200, 950, 600, 300]
    })

@st.cache_data(show_spinner=True)
def gerar_dados_regiao():
    # time.sleep(4)
    return pd.DataFrame({
        "Região": ["Sul", "Sudeste", "Nordeste", "Norte", "Centro-Oeste"],
        "Vendas": [400, 800, 300, 150, 250]
    })


if aba == "Resumo":
    vendas_mes = gerar_dados_mensais()
    vendas_categoria = gerar_dados_categoria()
    vendas_regiao = gerar_dados_regiao()

    col1, col2 = st.columns(2)
    with col1:
        st.title(f"Vendas totais: {vendas_mes['Vendas'].sum()} unidades")
        st.title(f"Categorias: {', '.join(vendas_categoria['Categoria'])}")
        st.title(f"Regiões: {', '.join(vendas_regiao['Região'])}")

    with col2:
        st.subheader("📈 Vendas Mensais")
        fig = px.line(vendas_mes, x="Mês", y="Vendas", markers=True)
        st.plotly_chart(fig, use_container_width=True)

elif aba == "Por Categoria":
    vendas_categoria = gerar_dados_categoria()
    st.subheader("📊 Vendas por Categoria")
    fig = px.bar(vendas_categoria, x="Categoria", y="Vendas", color="Categoria")
    st.plotly_chart(fig, use_container_width=True)

elif aba == "Por Região":
    vendas_regiao = gerar_dados_regiao()
    st.subheader("🍩 Distribuição por Região")
    fig = px.pie(vendas_regiao, names="Região", values="Vendas", hole=0.5)
    st.plotly_chart(fig, use_container_width=True)
