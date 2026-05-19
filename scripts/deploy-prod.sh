#!/bin/bash

echo "Atualizando ambiente de Producao..."
git pull origin main
docker compose build prod
docker compose up -d prod
docker ps

