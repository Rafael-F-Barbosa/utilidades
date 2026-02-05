#!/bin/bash

# Gera um número aleatório de 0 a 100
timestamp_random=$(( $RANDOM % 101 ))

# Criando registro com o novo timestamp
echo "Salvando registro: "
# Nota: Aspas simples em volta da variável $timestamp_random no JSON 
# não funcionariam, então usamos aspas duplas escapadas.
registro="{\"tool\":\"api\",\"status\":\"UP\",\"timestamp\":$timestamp_random}"
echo $registro

curl -X POST tool-state.local/tool-state \
 -H "Content-Type: application/json" \
 -d "$registro"

echo -e "\n..."

echo "Recuperando registros: "
resposta_completa=$(curl -X GET -s -w "%{http_code}" tool-state.local/tool-state)

# Separa o StatusCode e o Corpo
status_code="${resposta_completa: -3}"
corpo="${resposta_completa%???}"

echo "StatusCode: $status_code"
echo "Resposta: $corpo"
