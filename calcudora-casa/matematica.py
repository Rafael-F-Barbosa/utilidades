import pandas as pd


def mensal_rate_from_annual_effective(annual_eff_percent: float) -> float:
    """Converte taxa efetiva anual (em percent) para taxa efetiva mensal (decimal)."""
    return (1 + annual_eff_percent / 100) ** (1 / 12) - 1


def gerar_tabela_sac(financiado: float, n_periodos: int, i_mensal: float):
    """Gera o cronograma SAC como um DataFrame (sem dependências de apresentação).

    Retorna um `pandas.DataFrame` com colunas:
    - Periodo
    - Saldo Devedor (R$)
    - Amortizacao (R$)
    - Juros (R$)
    - Seguro (R$)
    - Parcela (R$)
    """
    amort_const = financiado / n_periodos
    saldo = financiado
    rows = []

    for periodo in range(1, n_periodos + 1):
        juros = saldo * i_mensal
        parcela = amort_const + juros 
        rows.append(
            {
                "Periodo": periodo,
                "Saldo Devedor (R$)": round(saldo, 2),
                "Amortizacao (R$)": round(amort_const, 2),
                "Juros (R$)": round(juros, 2),
                "Parcela (R$)": round(parcela, 2),
            }
        )
        saldo = max(0.0, saldo - amort_const)

    df = pd.DataFrame(rows)
    df["Parcela (R$)"] = df["Parcela (R$)"].astype(float)
    return df
