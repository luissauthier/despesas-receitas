#!/bin/bash

echo "Criando ambiente de Homologacao..."
docker compose up -d homolog
docker ps

