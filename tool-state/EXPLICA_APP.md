# EXPLICA_APP

Resumo do fluxo da aplicação

1. A aplicação expõe um endpoint para salvar o estado (`ToolState`).
2. `ToolStateService.save(...)` persiste o estado localmente (arquivo/repósitorio em memória) e, imediatamente após, aciona o `ErrorMetrics` para contabilizar a ocorrência apropriada.
3. `ErrorMetrics` registra contadores (`Counter`) usando o `MeterRegistry` do Micrometer. Cada tipo (`ErroThresholdInferior`, `ErroThresholdSuperior`, `AplicacaoEstavel`) possui um contador `app_errors_total{type="..."}`.
4. O Prometheus está configurado para `scrape` a aplicação diretamente (endpoint `/metrics`) e armazena os contadores no seu TSDB.
5. O Grafana consulta o Prometheus (datasource) e exibe painéis/dashboards com os contadores `app_errors_total` por `type`.

Detalhes de cada componente

 - Prometheus: faz scrapes periódicos da aplicação (conforme `prometheus.yml`) e armazena o histórico.
 - Grafana: consome as métricas do Prometheus e renderiza dashboards/painéis.

Como o salvamento e push funcionam (passo-a-passo técnico)

1. A camada de apresentação (REST) chama `ToolStateService.save(state)`.
2. `ToolStateService` chama `repository.save(state)` para persistir.
3. Em seguida a aplicação avalia o `timestamp` e chama `errorMetrics.countError(type)` com um dos três tipos:

 - `ErroThresholdInferior` — quando `timestamp < 50`
 - `ErroThresholdSuperior` — quando `timestamp > 100`
 - `AplicacaoEstavel` — quando `50 <= timestamp <= 100`

4. `ErrorMetrics.countError(type)` cria/usa um `Counter` chamado `app_errors_total` com a tag `type=<tipo>` e incrementa o contador (não bloqueante).

Como o Prometheus passa a ver a métrica

1. Após a aplicação incrementar os contadores, o endpoint `/metrics` expõe `app_errors_total{type="..."}` no formato Prometheus.
2. O Prometheus, configurado para scrappear a aplicação, coleta os contadores no próximo ciclo de scrape e os armazena como time series.
3. No Prometheus UI, você pode consultar:

```
app_errors_total{type="AplicacaoEstavel"}
```

Como visualizar no Grafana

1. Abra o Grafana (por exemplo via port-forward `kubectl port-forward svc/grafana 3000:3000`) e confirme que a `Data Source` Prometheus está funcionando.
2. Importe o dashboard fornecido em `dashboard.json` (Dashboard → + → Import → cole o JSON). O JSON contém painéis para os totais por tipo e uma série temporal de `increase(app_errors_total[5m])`.
3. Queries úteis:
   - Total de eventos estáveis: `sum(app_errors_total{type="AplicacaoEstavel"})`
   - Aumento em 5 minutos por tipo: `increase(app_errors_total{type="ErroThresholdInferior"}[5m])`
3. Queries úteis:
   - Último valor (legível): `tool_timestamp{app="tool-state"}`
   - Tempo desde a última métrica: `time() - tool_timestamp{app="tool-state"}`

Dicas de debug

- Se a aplicação estiver rodando fora do cluster, garanta que o Prometheus / seu ambiente de testes consiga acessar o endpoint `/metrics` da aplicação (use `kubectl port-forward svc/tool-state 8080:80` ou exponha outro caminho).
- Verifique logs da aplicação para mensagens de contagem (os `Counter` não lançam erros; falhas serão registradas no log da aplicação em caso de problemas com o registry).
- No Prometheus, use o UI (`/graph`) para verificar se o scrape target está ativo e quando foi o último scrape.

Provisionamento do dashboard (opcional)

Para provisionar automaticamente o dashboard no Grafana via Kubernetes, crie um `ConfigMap` contendo `dashboard.json` e monte-o no container do Grafana em `/var/lib/grafana/dashboards/` e ajuste as variáveis de provisioning. Se quiser, eu crio os manifests e atualizo o `k8s/grafana-deployment.yaml` para montar esse ConfigMap.

---
Arquivo do dashboard: `dashboard.json` (já disponível no repositório na raiz).
