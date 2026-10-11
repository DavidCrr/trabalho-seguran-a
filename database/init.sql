-- Banco demonstrativo da MedTech.
-- Utilizar apenas dados ficticios neste projeto.

CREATE TABLE IF NOT EXISTS produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    estoque INTEGER NOT NULL DEFAULT 0
);

INSERT INTO produtos (nome, estoque)
VALUES
    ('Produto Demonstrativo A', 100),
    ('Produto Demonstrativo B', 50);
