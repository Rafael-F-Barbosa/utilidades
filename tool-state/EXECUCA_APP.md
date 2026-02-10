# EXECUCA_APP

Este documento descreve os passos para executar e testar a aplicação localmente, incluindo a stack de monitoração (Prometheus, Grafana).

Pré-requisitos
- Java 21
- Maven
- Docker (se for criar imagem)
- kind + kubectl (para rodar a stack em Kubernetes)

Passos rápidos - modo desenvolvimento (mais rápido)

1. Rode a aplicação em modo dev (a aplicação expõe métricas via Micrometer/Prometheus):

```bash
./mvnw quarkus:dev
```

3. Execute um POST para salvar um estado (exemplo):

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"tool":"api","status":"UP","timestamp":'"$(date +%s)"'}' \
  http://localhost:8080/tool-state
```

4. Verifique as métricas expostas pela aplicação (ex.: via port-forward do serviço Prometheus ou da aplicação direta):

```bash
# se aplicação em cluster, port-forward do serviço prom por exemplo ou da aplicação
kubectl port-forward svc/prometheus 9090:9090
curl http://localhost:9090/metrics | grep app_errors_total -n || true
# ou consultar diretamente a aplicação (se expõe /metrics):
curl http://localhost:8080/metrics | grep app_errors_total -n || true
```

Passos rápidos - rodando a stack no Kind (Kubernetes)

1. (Opcional) Crie um cluster kind se não existir:

```bash
./k8s-cluster.sh
```

2. Build da aplicação e da imagem (ou use `build-image.sh`):

```bash
./mvnw -DskipTests package
./build-image.sh
```

3. Suba os manifests (há um script que carrega a imagem e aplica os manifests):

```bash
./k8s-up.sh
```

4. Aguarde os pods ficarem prontos e verifique:

```bash
kubectl get pods,svc -l app=prometheus
kubectl get pods,svc -l app=grafana
kubectl get pods,svc -l app=tool-state
```

5. Para testar localmente sem expor ingresses, faça port-forward:

```bash
kubectl port-forward svc/prometheus 9090:9090
kubectl port-forward svc/grafana 3000:3000
kubectl port-forward svc/tool-state 8080:80
```

6. Agora você pode postar um estado para a aplicação (se a app estiver rodando no cluster ou local) e verificar métricas conforme em "modo desenvolvimento".

Remoção da stack

```bash
./k8s-down.sh
```

Observações
 - Arquivo do dashboard para import no Grafana: `dashboard.json` (import pelo UI ou provisionar via ConfigMap).
 - A aplicação expõe métricas via Micrometer; Prometheus coleta diretamente `app_errors_total` no endpoint `/metrics`.
