#!/bin/bash

set -e

echo "Gerando build Docker..."
docker compose build

echo "Executando testes automatizados no container..."
docker compose run --rm homolog pytest -v

echo "Executando cobertura de testes no container..."
docker compose run --rm homolog sh -c "coverage run -m pytest && coverage report"

echo "Pipeline de integracao finalizado com sucesso."

