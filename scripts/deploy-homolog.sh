#!/bin/bash

set -e

echo "Atualizando ambiente de Homologacao..."

git checkout develop
git pull origin develop

echo "Removendo container antigo de Homologacao, se existir..."
docker rm -f despesas-homolog 2>/dev/null || true

echo "Subindo Homologacao atualizada..."
docker-compose up -d --build homolog

docker ps