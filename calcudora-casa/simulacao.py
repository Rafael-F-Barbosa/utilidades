import streamlit as st
import pandas as pd
import numpy as np


def mensal_rate_from_annual_effective(annual_eff_percent: float) -> float:
    return (1 + annual_eff_percent / 100) ** (1 / 12) - 1


@st.cache_data
def gerar_tabela_sac(financiado: float, n_periodos: int, i_mensal: float, cesh_anual_percent: float, incluir_seguro: bool):
    amort_const = financiado / n_periodos
    saldo = financiado
    rows = []
    seguro_mensal_rate = cesh_anual_percent / 100 / 12

    for periodo in range(1, n_periodos + 1):
        juros = saldo * i_mensal
        seguro = saldo * seguro_mensal_rate if incluir_seguro else 0.0
        parcela = amort_const + juros + seguro
        rows.append(
            {
                "Periodo": periodo,
                "Saldo Devedor (R$)": round(saldo, 2),
                "Amortizacao (R$)": round(amort_const, 2),
                "Juros (R$)": round(juros, 2),
                "Seguro (R$)": round(seguro, 2),
                "Parcela (R$)": round(parcela, 2),
            }
        )
        saldo = max(0.0, saldo - amort_const)

    df = pd.DataFrame(rows)
    df["Parcela (R$)"] = df["Parcela (R$)"].astype(float)
    return df


def main():
    st.title("Simulação de Financiamento Imobiliário — SAC")

    st.sidebar.header("Parâmetros do financiamento")
    valor_imovel = st.sidebar.number_input("Valor do imóvel (R$)", value=300000.0, step=1000.0, format="%.2f")
    entrada = st.sidebar.number_input("Entrada (R$)", value=60000.0, step=500.0, format="%.2f")
    financiado = max(0.0, valor_imovel - entrada)
    st.sidebar.markdown(f"**Financiado (R$):** {financiado:,.2f}")

    juros_nominal = st.sidebar.number_input("Juros nominais a.a. (%)", value=8.16, format="%.4f")
    juros_efetivo = st.sidebar.number_input("Juros efetivos a.a. (%)", value=8.47, format="%.4f")
    cet = st.sidebar.number_input("CET a.a. (%)", value=9.22, format="%.4f")
    cesh = st.sidebar.number_input("CESH (seguro habitacional) a.a. (%)", value=2.09, format="%.4f")

    st.sidebar.markdown("---")
    periodo_anos = st.sidebar.slider("Prazo (anos)", min_value=1, max_value=40, value=30)
    n_periodos = int(periodo_anos * 12)
    incluir_seguro = st.sidebar.checkbox("Incluir seguro habitacional (CESH)", value=True)

    st.header("Resumo")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Valor do imóvel (R$)", f"{valor_imovel:,.2f}")
        st.metric("Entrada (R$)", f"{entrada:,.2f}")
    with col2:
        st.metric("Financiado (R$)", f"{financiado:,.2f}")
        st.metric("Prazo (meses)", f"{n_periodos}")
    with col3:
        st.metric("Juros nominais a.a.(%)", f"{juros_nominal:.2f}")
        st.metric("Juros efetivos a.a.(%)", f"{juros_efetivo:.2f}")

    i_mensal = mensal_rate_from_annual_effective(juros_efetivo)
    st.write(f"Taxa efetiva mensal aproximada: {i_mensal * 100:.4f}%")

    df = gerar_tabela_sac(financiado, n_periodos, i_mensal, cesh, incluir_seguro)

    st.header("Cronograma de Parcelas (SAC)")
    st.dataframe(df.style.format("{:.2f}"), height=400)

    soma_parcelas = df["Parcela (R$)"].sum()
    primeira = df.iloc[0]["Parcela (R$)"] if not df.empty else 0.0
    ultima = df.iloc[-1]["Parcela (R$)"] if not df.empty else 0.0

    st.subheader("Totais e indicadores")
    st.write(f"Primeira parcela: R$ {primeira:,.2f}")
    st.write(f"Última parcela: R$ {ultima:,.2f}")
    st.write(f"Soma total das parcelas: R$ {soma_parcelas:,.2f}")
    st.write(f"CET informado: {cet:.2f}% a.a.")
    st.write(f"CESH informado: {cesh:.2f}% a.a.")

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(label="Baixar tabela CSV", data=csv, file_name="tabela_sac.csv", mime="text/csv")

    st.header("Fórmulas utilizadas")
    st.write("As fórmulas usadas para gerar o cronograma SAC:")
    st.latex(r"i_{m} = (1 + i_{a})^{1/12} - 1")
    st.latex(r"A = \frac{PV}{n}")
    st.latex(r"J_t = S_{t-1} \cdot i_m")
    st.latex(r"i_{seg,m} = \frac{CESH}{12}")
    st.latex(r"Seguro_t = S_{t-1} \cdot i_{seg,m}")
    st.latex(r"P_t = A + J_t + Seguro_t")
    st.latex(r"S_t = S_{t-1} - A")
    st.subheader("Legenda")
    st.markdown(
        """
- $i_a$: taxa efetiva anual (ex.: 8.47% → 0.0847)
- $i_m$: taxa efetiva mensal: $i_m = (1 + i_a)^{1/12} - 1$
- $PV$: valor presente / valor financiado (R$)
- $n$: número de parcelas (meses)
- $A$: amortização constante por período (R$) — $A = PV / n$
- $S_{t-1}$: saldo devedor no início do período $t$ (R$)
- $J_t$: juros do período $t$ (R$) — $J_t = S_{t-1} \cdot i_m$
- $CESH$: Custo Efetivo Seguro Habitacional (percentual a.a.)
- $i_{seg,m}$: taxa mensal do seguro — $i_{seg,m} = CESH / 12$
- $Seguro_t$: valor do seguro no período $t$ (R$) — $Seguro_t = S_{t-1} \cdot i_{seg,m}$
- $P_t$: parcela total no período $t$ (R$) — $P_t = A + J_t + Seguro_t$
"""
    )

if __name__ == "__main__":
    main()
