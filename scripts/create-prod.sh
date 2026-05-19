#!/bin/bash

set -e

echo "Criando ambiente de Producao..."
docker compose up -d prod
docker ps
