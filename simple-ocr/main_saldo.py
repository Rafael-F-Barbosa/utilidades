import csv
import json

lista_gastos_formatada = []
with open('Extrato.csv', newline='', encoding='utf-8') as arquivo:
    leitor = csv.reader(arquivo)
    next(leitor)  # <-- Pula a primeira linha (cabeçalho)
    for linha in leitor:
        print(linha)

        if  not linha[1].startswith('Saldo') and\
            not linha[1].startswith('S A L D') and\
            not linha[1].startswith('Pix - Rec') and\
            not linha[1].startswith('Recebimento de Prov') and\
            not linha[1].startswith('Pagto cart'): 

            lista_gastos_formatada.append({
                    "nome": linha[1] + " | " + linha[2] + " | " + linha[3] + " | "+linha[5],
                    "valor": -1 * float(linha[4].replace(".", "").replace(",", ".")),
                    "data": linha[0]
                }
            )

with open("dados-extrato.json", "w", encoding="utf-8") as f:
    json.dump(lista_gastos_formatada, f, indent=4, ensure_ascii=False)