#!/bin/bash

set -e

DB="./instance_prod/app.db"
MIGRATIONS_DIR="./migrations"

echo "Ajustando permissoes do banco de Producao..."
sudo chown -R jenkins:jenkins ./instance_prod 2>/dev/null || true
sudo chmod -R u+rwX ./instance_prod 2>/dev/null || true

echo "Aplicando migrations no banco de Producao..."

sqlite3 "$DB" "
CREATE TABLE IF NOT EXISTS schema_migrations (
  filename TEXT PRIMARY KEY,
  applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"

echo "Verificando estrutura ja existente no banco..."

sqlite3 "$DB" "
INSERT OR IGNORE INTO schema_migrations (filename)
SELECT '001_schema_inicial.sql'
WHERE EXISTS (
  SELECT 1 FROM sqlite_master WHERE type='table' AND name='usuario'
)
AND EXISTS (
  SELECT 1 FROM sqlite_master WHERE type='table' AND name='lancamento'
);

INSERT OR IGNORE INTO schema_migrations (filename)
SELECT '002_adiciona_observacao_lancamento.sql'
WHERE EXISTS (
  SELECT 1 FROM pragma_table_info('lancamento') WHERE name='observacao'
);

INSERT OR IGNORE INTO schema_migrations (filename)
SELECT '003_cria_tabela_teste.sql'
WHERE EXISTS (
  SELECT 1 FROM sqlite_master WHERE type='table' AND name='teste'
);

INSERT OR IGNORE INTO schema_migrations (filename)
SELECT '004_cria_tabela_categoria.sql'
WHERE EXISTS (
  SELECT 1 FROM sqlite_master WHERE type='table' AND name='categoria'
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

echo "Migrations aplicadas em Producao:"
sqlite3 "$DB" "SELECT filename, applied_at FROM schema_migrations ORDER BY filename;"

echo "Tabelas existentes em Producao:"
sqlite3 "$DB" ".tables"

echo "Quantidade de lancamentos preservados em Producao:"
sqlite3 "$DB" "SELECT COUNT(*) FROM lancamento;"

echo "Migrations finalizadas em Producao."