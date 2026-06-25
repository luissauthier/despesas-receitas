#!/bin/bash

set -e

echo "Atualizando ambiente de Homologacao..."
git checkout develop
git pull origin develop
docker-compose build homolog
docker-compose up -d homolog
docker ps

echo "Ajustando permissoes das pastas de banco..."
sudo chown -R univates:jenkins /home/univates/despesas-receitas/instance_homolog 2>/dev/null || true
sudo chmod -R g+rwX /home/univates/despesas-receitas/instance_homolog 2>/dev/null || true