#!/usr/bin/env bash
set -e

echo "🧹 Removendo recursos do Kubernetes..."

kubectl delete ingress tool-state-ingress --ignore-not-found
kubectl delete service tool-state --ignore-not-found
kubectl delete deployment tool-state --ignore-not-found
kubectl delete pvc tool-state-pvc --ignore-not-found
kubectl delete configmap prometheus-config --ignore-not-found
kubectl delete deployment prometheus --ignore-not-found
kubectl delete service prometheus --ignore-not-found
kubectl delete configmap grafana-datasources --ignore-not-found
kubectl delete deployment grafana --ignore-not-found
kubectl delete service grafana --ignore-not-found

echo "✅ Ambiente limpo."
