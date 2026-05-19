CREATE TABLE usuario (
	id INTEGER NOT NULL, 
	nome VARCHAR(120) NOT NULL, 
	login VARCHAR(80) NOT NULL, 
	senha VARCHAR(255) NOT NULL, 
	situacao VARCHAR(20) NOT NULL, email TEXT, 
	PRIMARY KEY (id), 
	UNIQUE (login)
);
CREATE TABLE lancamento (
	id INTEGER NOT NULL, 
	descricao VARCHAR(255) NOT NULL, 
	data_lancamento DATE NOT NULL, 
	valor NUMERIC(12, 2) NOT NULL, 
	tipo_lancamento VARCHAR(20) NOT NULL, 
	situacao VARCHAR(20) NOT NULL, 
	PRIMARY KEY (id)
);
