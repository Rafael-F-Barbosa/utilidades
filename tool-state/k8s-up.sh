#!/usr/bin/env bash
set -e

CLUSTER_NAME="tool-state-cluster"
IMAGE_NAME="tool-state:latest"

echo "📦 Carregando imagem no kind..."
kind load docker-image $IMAGE_NAME --name $CLUSTER_NAME

echo "🚀 Aplicando manifests..."
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/prometheus-configmap.yaml
kubectl apply -f k8s/prometheus-deployment.yaml
kubectl apply -f k8s/grafana-deployment.yaml

echo "⏳ Aguardando pod ficar pronto..."
kubectl rollout status deployment/tool-state

echo "🌐 Teste:"
echo "curl http://tool-state.local/tool-state"
