import re

def converte_valor_monetario(valor: str) -> float | None:
    """
    Converte uma string no formato monetário brasileiro para float.
    Aceita:
      - Prefixos: "R$" ou "RS" (maiúsculo ou minúsculo)
      - Sinal negativo antes ou depois do prefixo (ex: "-R$ 1.000,00" ou "R$ -1.000,00")
      - Números com ou sem separador de milhar
    Exemplo:
      "R$ 8.010,24"  -> 8010.24
      "-R$ 8.010,24" -> -8010.24
      "RS -8,01"     -> -8.01
    Retorna None se o formato for inválido.
    """
    if valor is None:
        return None

    s = valor.strip()

    padrao = r'^([+-]?)\s*(R\$|RS)\s*([+-]?)\s*(\d{1,3}(?:\.\d{3})*|\d+),(\d{2})$'
    m = re.match(padrao, s, re.IGNORECASE)

    if not m:
        return None

    sinal_antes = m.group(1)
    sinal_depois = m.group(3)
    numero = m.group(4)
    centavos = m.group(5)

    # Impede dois sinais negativos
    if sinal_antes == '-' and sinal_depois == '-':
        return None

    # Determina o sinal final
    negativo = sinal_antes == '-' or sinal_depois == '-'

    # Remove separadores de milhar e junta com centavos
    valor_limpo = numero.replace('.', '') + '.' + centavos

    try:
        valor_float = float(valor_limpo)
        return -valor_float if negativo else valor_float
    except ValueError:
        return None



def verifica_data_dia_mes(data: str) -> bool:
    if data is None:
        return False

    # Verifica o formato básico dd/mm com regex
    if not re.match(r"^\d{2}/\d{2}$", data):
        return False
    
    try:
        dia, mes = map(int, data.split('/'))
        # Verifica se dia e mês estão dentro dos intervalos válidos
        return 1 <= dia <= 31 and 1 <= mes <= 12
    except ValueError:
        return False
    
def verifica_valor_monetario(valor: str) -> bool:
    """
    Verifica se a string está no formato monetário brasileiro, aceitando:
    - Prefixos: "R$" ou "RS" (case-insensitive)
    - Sinal negativo antes ou depois do prefixo (ex: "-R$ 1.000,00" ou "R$ -1.000,00")
    - Números com ou sem separador de milhar
    - Ex.: "R$ 8.010,24", "RS 8010,24", "-R$ 1.234,56", "R$ -8,01"
    Retorna True se válido, False caso contrário.
    """
    if valor is None:
        return False

    s = valor.strip()

    # Captura: sinal opcional antes, prefixo (R$ ou RS), sinal opcional depois, parte numérica (com/sem milhares) e ,cc
    padrao = r'^([+-]?)\s*(R\$|RS)\s*([+-]?)\s*(\d{1,3}(?:\.\d{3})*|\d+),\d{2}$'
    m = re.match(padrao, s, re.IGNORECASE)

    if not m:
        return False

    sinal_antes = m.group(1)
    sinal_depois = m.group(3)

    # Não permitir dois sinais negativos ao mesmo tempo (ex: "-R$ -1.000,00")
    if sinal_antes == '-' and sinal_depois == '-':
        return False

    return True