CREATE TABLE IF NOT EXISTS teste3 (
    id INTEGER PRIMARY KEY,
    descricao TEXT NOT NULL UNIQUE
);

INSERT OR IGNORE INTO teste3 (id, descricao) VALUES
    (1, 'Alimentação'),
    (2, 'Transporte'),
    (3, 'Lazer');