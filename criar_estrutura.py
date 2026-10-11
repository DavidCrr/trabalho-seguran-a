
from pathlib import Path

# Diretório raiz do projeto: pasta aberta no terminal
ROOT = Path.cwd()

# Estrutura de diretórios e arquivos iniciais
estrutura = {
    "firewall": [
        "Dockerfile",
        "entrypoint.sh",
    ],
    "client": [
        "Dockerfile",
    ],
    "web": [
        "index.html",
    ],
    "database": [
        "init.sql",
    ],
    "docs": [
        "arquitetura.md",
        "matriz-regras.md",
        "testes.md",
    ],
    "relatorio": [
        "trabalho.md",
    ],
}

# Arquivos da raiz
arquivos_raiz = [
    "docker-compose.yml",
    ".gitignore",
]

# Conteúdo inicial dos arquivos
conteudos = {
    "README.md": """# MedTech Firewall

Projeto acadêmico de Segurança da Informação.

## Objetivo

Simular uma infraestrutura de rede segmentada para uma
distribuidora farmacêutica, utilizando Docker, Docker Compose
e iptables.

## Componentes

- LAN: rede dos funcionários.
- Firewall Linux: gateway e filtro de pacotes.
- DMZ: servidor Web.
- Rede privada: banco de dados PostgreSQL.

## Tecnologias

- Docker
- Docker Compose
- Linux
- iptables
- Git e GitHub

## Status

Em desenvolvimento.
""",
    ".gitignore": """# Segredos e variáveis de ambiente
.env
.env.*
!.env.example

# Python
__pycache__/
*.py[cod]
.venv/

# Sistema operacional e IDE
.DS_Store
Thumbs.db
.vscode/
.idea/
""",
    "firewall/Dockerfile": "# Dockerfile do container Firewall Linux\n",
    "firewall/entrypoint.sh": "#!/bin/sh\n# Inicializacao e regras do firewall serao implementadas aqui.\n",
    "client/Dockerfile": "# Dockerfile da estacao de trabalho simulada\n",
    "web/index.html": """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MedTech - Portal de Pedidos</title>
</head>
<body>
    <h1>MedTech - Portal de Pedidos</h1>
    <p>Ambiente demonstrativo de uma distribuidora farmacêutica.</p>
    <p>Projeto acadêmico de Segurança da Informação.</p>
</body>
</html>
""",
    "database/init.sql": """-- Banco demonstrativo da MedTech.
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
""",
    "docs/arquitetura.md": "# Arquitetura da Rede\n\nDiagrama e enderecamento serao documentados aqui.\n",
    "docs/matriz-regras.md": "# Matriz de Regras do Firewall\n\nAs regras implementadas serao documentadas aqui.\n",
    "docs/testes.md": "# Testes de Seguranca\n\nOs testes positivos e negativos serao documentados aqui.\n",
    "relatorio/trabalho.md": "# Relatorio Tecnico - MedTech Firewall\n\n## 1. Definicao do Case\n\n## 2. Diagnostico\n\n## 3. Proposta de Solucao\n\n## 4. Arquitetura da Rede\n\n## 5. Matriz de Regras\n\n## 6. Metodologia de Testes\n\n## 7. Conclusao\n",
}

def criar_arquivo(caminho, conteudo=""):
    arquivo = ROOT / caminho
    arquivo.parent.mkdir(parents=True, exist_ok=True)

    if arquivo.exists():
        print(f"[EXISTE] {caminho} - mantido sem alteracoes")
        return

    arquivo.write_text(conteudo, encoding="utf-8")
    print(f"[CRIADO] {caminho}")

def main():
    print(f"Raiz do projeto: {ROOT}\n")

    for pasta, arquivos in estrutura.items():
        (ROOT / pasta).mkdir(parents=True, exist_ok=True)
        print(f"[PASTA] {pasta}/")

        for nome in arquivos:
            caminho = f"{pasta}/{nome}"
            criar_arquivo(caminho, conteudos.get(caminho, ""))

    for nome in arquivos_raiz:
        criar_arquivo(nome, conteudos.get(nome, ""))

    criar_arquivo("README.md", conteudos["README.md"])

    print("\nEstrutura inicial criada com sucesso!")
    print("Proximo passo: revisar os arquivos e implementar o Docker Compose.")

if __name__ == "__main__":
    main()