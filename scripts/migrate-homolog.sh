#!/bin/bash

set -e

echo "Aplicando migrations no banco de Homologacao..."

COLUNA_EXISTE=$(sqlite3 ./instance_homolog/app.db "PRAGMA table_info(lancamento);" | grep -c "|observacao|")

if [ "$COLUNA_EXISTE" -eq 0 ]; then
  sqlite3 ./instance_homolog/app.db < migrations/002_adiciona_observacao_lancamento.sql
  echo "Migration 002 aplicada em Homologacao."
else
  echo "Migration 002 ja aplicada em Homologacao."
fi

sqlite3 ./instance_homolog/app.db "PRAGMA table_info(lancamento);"

echo "Migrations finalizadas em Homologacao."
