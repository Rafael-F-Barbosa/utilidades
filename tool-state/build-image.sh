#!/usr/bin/env bash
set -e

IMAGE_BASE="tool-state"

echo "🔨 Buildando aplicação Quarkus..."
./mvnw clean package -DskipTests

echo "🔎 Descobrindo última versão da imagem..."

LAST_TAG=$(docker images --format "{{.Repository}}:{{.Tag}}" \
  | grep "^$IMAGE_BASE:[0-9]\+\.[0-9]\+$" \
  | sed "s/$IMAGE_BASE://g" \
  | sort -V \
  | tail -n 1)

if [ -z "$LAST_TAG" ]; then
  NEW_TAG="1.0"
else
  MAJOR=$(echo $LAST_TAG | cut -d. -f1)
  MINOR=$(echo $LAST_TAG | cut -d. -f2)

  MINOR=$((MINOR + 1))
  NEW_TAG="$MAJOR.$MINOR"
fi

echo "📦 Nova versão: $NEW_TAG"

echo "🐳 Buildando imagem Docker..."
docker build -t $IMAGE_BASE:$NEW_TAG .

echo "🏷️ Atualizando tag latest..."
docker tag $IMAGE_BASE:$NEW_TAG $IMAGE_BASE:latest

echo "✅ Imagem criada:"
docker images | grep $IMAGE_BASE
