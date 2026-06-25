#!/bin/bash

set -e

echo "Atualizando ambiente de Producao..."

git checkout develop
git pull origin develop

echo "Removendo container antigo de Producao, se existir..."
docker rm -f despesas-prod 2>/dev/null || true

echo "Subindo Producao atualizada..."
docker-compose up -d --build prod

docker ps