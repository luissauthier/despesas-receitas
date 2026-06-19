CREATE TABLE IF NOT EXISTS teste4 (
    id INTEGER PRIMARY KEY,
    descricao TEXT NOT NULL UNIQUE
);

INSERT OR IGNORE INTO teste4 (id, descricao) VALUES
    (1, 'Alimentação'),
    (2, 'Transporte'),
    (3, 'Lazer');