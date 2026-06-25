#!/bin/bash

echo "Criando ambientes de Homologacao e Producao..."
docker-compose up -d
docker ps
