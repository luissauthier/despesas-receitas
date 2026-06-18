#!/bin/bash

echo "=============================="
echo "INICIANDO INFRAESTRUTURA CI/CD"
echo "=============================="

echo "[1/4] Limpando ambiente antigo..."
docker stop $(docker ps -aq) 2>/dev/null
docker rm $(docker ps -aq) 2>/dev/null

echo "[2/4] Subindo Jenkins..."

docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts

echo "[3/4] Verificando containers ativos..."
docker ps

echo "[4/4] Jenkins disponível em:"
echo "http://177.44.248.12:8080"

echo "=============================="
echo "OK - INFRA ESTRUTURA PRONTA"
echo "=============================="
