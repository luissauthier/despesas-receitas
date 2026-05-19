#!/bin/bash

echo "Criando ambiente de Producao..."
docker compose up -d prod
docker ps
