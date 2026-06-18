#!/bin/bash

set -e

DB="./instance_homolog/app.db"
MIGRATIONS_DIR="./migrations"

echo "Aplicando migrations no banco de Homologacao..."

sqlite3 "$DB" "
CREATE TABLE IF NOT EXISTS schema_migrations (
  filename TEXT PRIMARY KEY,
  applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"

for migration in "$MIGRATIONS_DIR"/*.sql; do
  filename=$(basename "$migration")

  ja_aplicada=$(sqlite3 "$DB" "SELECT COUNT(*) FROM schema_migrations WHERE filename = '$filename';")

  if [ "$ja_aplicada" -eq 0 ]; then
    echo "Aplicando $filename..."

    sqlite3 "$DB" < "$migration"

    sqlite3 "$DB" "INSERT INTO schema_migrations (filename) VALUES ('$filename');"

    echo "$filename aplicada com sucesso."
  else
    echo "$filename ja aplicada. Pulando."
  fi
done

echo "Migrations aplicadas em Homologacao:"
sqlite3 "$DB" "SELECT filename, applied_at FROM schema_migrations ORDER BY filename;"

echo "Tabelas existentes em Homologacao:"
sqlite3 "$DB" ".tables"

echo "Quantidade de lancamentos preservados em Homologacao:"
sqlite3 "$DB" "SELECT COUNT(*) FROM lancamento;"

echo "Migrations finalizadas em Homologacao."