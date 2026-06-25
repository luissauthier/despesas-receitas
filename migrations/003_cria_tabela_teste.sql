CREATE TABLE IF NOT EXISTS categoria (
    id INTEGER PRIMARY KEY,
    descricao TEXT NOT NULL UNIQUE
);

INSERT OR IGNORE INTO categoria (id, descricao) VALUES
    (1, 'Alimentação'),
    (2, 'Transporte'),
    (3, 'Lazer');