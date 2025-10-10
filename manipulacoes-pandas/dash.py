import pandas as pd

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

print(agrupar_fluxos(df))
