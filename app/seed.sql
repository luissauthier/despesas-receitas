-- SQLite seed script

DELETE FROM lancamento;
DELETE FROM usuario;

INSERT INTO usuario (id, nome, login, senha, situacao)
VALUES (1, 'Admin', 'admin', 'admin123', 'ATIVO');

INSERT INTO lancamento (id, descricao, data_lancamento, valor, tipo_lancamento, situacao) VALUES
(1, 'Salário', '2026-03-01', 5500.00, 'RECEITA', 'PAGO'),
(2, 'Aluguel', '2026-03-05', 1800.00, 'DESPESA', 'PAGO'),
(3, 'Supermercado', '2026-03-06', 420.35, 'DESPESA', 'PAGO'),
(4, 'Internet', '2026-03-07', 119.90, 'DESPESA', 'PAGO'),
(5, 'Freelance', '2026-03-08', 900.00, 'RECEITA', 'EM_ABERTO'),
(6, 'Transporte', '2026-03-09', 160.00, 'DESPESA', 'PAGO'),
(7, 'Restaurante', '2026-03-10', 95.70, 'DESPESA', 'PAGO'),
(8, 'Energia', '2026-03-11', 210.18, 'DESPESA', 'EM_ABERTO'),
(9, 'Venda (OLX)', '2026-03-12', 250.00, 'RECEITA', 'PAGO'),
(10, 'Academia', '2026-03-15', 89.90, 'DESPESA', 'EM_ABERTO');

