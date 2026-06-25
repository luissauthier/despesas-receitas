#!/bin/bash

set -e

echo "Atualizando ambiente de Producao..."

git checkout develop
git pull origin develop

echo "Removendo containers antigos de Producao, se existirem..."
docker-compose stop prod 2>/dev/null || true
docker-compose rm -f -s prod 2>/dev/null || true
docker rm -f $(docker ps -aq --filter "name=despesas-prod") 2>/dev/null || true

echo "Subindo Producao atualizada..."
docker-compose up -d --build prod

docker ps