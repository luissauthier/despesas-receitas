#!/bin/bash

echo "Executando testes automatizados..."
pytest -v

echo "Executando cobertura de testes..."
coverage run -m pytest
coverage report

echo "Gerando build Docker..."
docker compose build
