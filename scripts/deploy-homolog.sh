#!/bin/bash

set -e

echo "Atualizando ambiente de Homologacao..."

git checkout develop
git pull origin develop

echo "Removendo containers antigos de Homologacao, se existirem..."
docker-compose stop homolog 2>/dev/null || true
docker-compose rm -f -s homolog 2>/dev/null || true
docker rm -f $(docker ps -aq --filter "name=despesas-homolog") 2>/dev/null || true

echo "Subindo Homologacao atualizada..."
docker-compose up -d --build homolog

docker ps