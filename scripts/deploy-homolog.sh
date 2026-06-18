#!/bin/bash

set -e

echo "Atualizando ambiente de Homologacao..."
git checkout develop
git pull origin develop
docker compose build homolog
docker compose up -d homolog
docker ps
