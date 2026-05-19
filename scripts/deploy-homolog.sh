#!/bin/bash

echo "Atualizando ambiente de Homologacao..."
git pull origin develop
docker compose build homolog
docker compose up -d homolog
docker ps
