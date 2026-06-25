#!/bin/bash

set -e

echo "Criando ambiente de Homologacao..."
docker-compose up -d homolog
docker ps
