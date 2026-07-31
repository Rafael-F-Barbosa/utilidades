

from matematica import mensal_rate_from_annual_effective


i_anual = 11
i_mensal = mensal_rate_from_annual_effective(i_anual)
print(f"Juros mensal: {i_mensal:.6f}")

financiamento = 240000
n_periodos = 360

amort_const = financiamento / n_periodos

primeira_parcela = amort_const + financiamento * i_mensal
print(f"Valor da primeira parcela: R$ {primeira_parcela:.2f}")
