#!/bin/bash

set -e

echo "Atualizando ambiente de Producao..."
git checkout main
git pull origin main
docker compose build prod
docker compose up -d prod
docker ps
