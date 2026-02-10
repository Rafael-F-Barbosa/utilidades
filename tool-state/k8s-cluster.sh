#!/usr/bin/env bash
set -e

CLUSTER_NAME="tool-state-cluster"
KIND_CONFIG="k8s/kind-config.yaml"

echo "🔎 Verificando se o cluster já existe..."

if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
  echo "⚠️ Cluster '${CLUSTER_NAME}' já existe. Nada a fazer."
  exit 0
fi

echo "🚀 Criando cluster kind: ${CLUSTER_NAME}"
kind create cluster --name "${CLUSTER_NAME}" --config "${KIND_CONFIG}"

echo "⏳ Aguardando nós ficarem prontos..."
kubectl wait --for=condition=Ready nodes --all --timeout=120s

echo "✅ Cluster criado com sucesso!"
echo
echo "📌 Próximos passos:"
echo "  1) Build da imagem:      ./build-image.sh"
echo "  2) Subir aplicação k8s:  ./k8s-up.sh"
echo "  3) Testar endpoint:      curl http://tool-state.local/tool-state"
