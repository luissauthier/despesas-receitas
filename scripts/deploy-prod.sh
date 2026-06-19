#!/bin/bash

set -e

echo "Atualizando ambiente de Producao..."
git checkout main
git pull origin main
docker compose build prod
docker compose up -d prod
docker ps

echo "Ajustando permissoes das pastas de banco..."
sudo chown -R univates:jenkins /home/univates/despesas-receitas/instance_prod 2>/dev/null || true
sudo chmod -R g+rwX /home/univates/despesas-receitas/instance_prod 2>/dev/null || true