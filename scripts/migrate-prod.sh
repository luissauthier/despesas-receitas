#!/bin/bash

set -e

echo "Aplicando migrations no banco de Producao..."
sqlite3 ./instance_prod/app.db < migrations/002_adiciona_observacao_lancamento.sql
sqlite3 ./instance_prod/app.db "PRAGMA table_info(lancamento);"
echo "Migrations aplicadas em Producao."
