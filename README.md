# MedTech Firewall

Projeto acadêmico de Segurança da Informação — implementação de um firewall Linux para segmentação e controle de tráfego em uma infraestrutura simulada de uma distribuidora farmacêutica.

## 1. Objetivo

Desenvolver e testar uma infraestrutura de rede segmentada utilizando Docker, Docker Compose e iptables, aplicando regras de filtragem de pacotes para controlar a comunicação entre os diferentes segmentos da rede.

O cenário representa uma distribuidora farmacêutica que precisa disponibilizar um portal HTTP, manter o banco de dados isolado e controlar o acesso entre estações internas e redes externas.

## 2. Arquitetura da rede

O ambiente é dividido em quatro segmentos de rede:

| Segmento      | Rede            | Equipamentos e endereços IP                       | Finalidade                    |
| ------------- | --------------- | ------------------------------------------------- | ----------------------------- |
| LAN           | `172.20.0.0/24` | Firewall: `172.20.0.2`; Cliente: `172.20.0.10`    | Rede interna dos funcionários |
| DMZ           | `172.21.0.0/24` | Firewall: `172.21.0.2`; Web: `172.21.0.10`        | Hospedagem do portal HTTP     |
| Rede do banco | `172.22.0.0/24` | Firewall: `172.22.0.2`; PostgreSQL: `172.22.0.20` | Armazenamento isolado         |
| WAN simulada  | `172.23.0.0/24` | Firewall: `172.23.0.2`; Farmácia: `172.23.0.10`   | Origem externa para testes    |

**Observação:** o firewall possui interfaces conectadas aos quatro segmentos de rede. Cada interface utiliza um endereço IP pertencente à respectiva sub-rede. Portanto, os diferentes endereços IP do firewall representam suas interfaces de rede, e não equipamentos distintos.

### Fluxo de comunicação

* **LAN → DMZ:** acesso HTTP permitido ao portal Web.
* **WAN simulada → DMZ:** acesso HTTP permitido para simular o acesso externo ao portal.
* **DMZ → LAN:** novas conexões bloqueadas (isolamento da DMZ).
* **LAN → banco de dados:** acesso direto bloqueado pelas regras de encaminhamento.
* **WAN simulada → banco de dados:** acesso direto não autorizado.
* **Tráfego de retorno:** conexões estabelecidas e relacionadas são permitidas pelas regras do firewall.

## 3. Componentes

* **Firewall Linux:** gateway responsável pelo encaminhamento de pacotes e pela aplicação das regras de filtragem com iptables.
* **Cliente:** representa uma estação de trabalho da rede interna.
* **Servidor Web:** disponibiliza o portal HTTP na DMZ utilizando Nginx.
* **Banco de dados:** serviço PostgreSQL conectado à rede privada do banco.
* **Farmácia:** representa uma origem externa simulada para os testes de conectividade.

## 4. Tecnologias utilizadas

* Docker
* Docker Compose
* Linux
* iptables
* Nginx
* PostgreSQL
* Git e GitHub

## 5. Regras de segurança

O firewall utiliza uma política padrão de bloqueio para o encaminhamento de pacotes (`FORWARD DROP`), permitindo apenas os fluxos definidos pelas regras.

| Origem                                     | Destino                          | Serviço                   | Ação                                        |
| ------------------------------------------ | -------------------------------- | ------------------------- | ------------------------------------------- |
| Conexões estabelecidas ou relacionadas     | Redes encaminhadas pelo firewall | Conforme conexão original | Permitir                                    |
| LAN                                        | Servidor Web na DMZ              | TCP/80 (HTTP)             | Permitir                                    |
| WAN simulada                               | Servidor Web na DMZ              | TCP/80 (HTTP)             | Permitir                                    |
| DMZ                                        | LAN (Intranet)                   | Qualquer                  | Bloquear novas conexões                     |
| LAN ou WAN simulada                        | Banco de dados                   | Acesso direto             | Bloquear por ausência de regra de permissão |
| Outros fluxos encaminhados não autorizados | Qualquer destino                 | Qualquer serviço          | Bloquear pela política padrão               |

O bloqueio de acesso ao banco de dados decorre da política padrão de encaminhamento, não de uma regra específica de bloqueio da porta 5432.

**Isolamento da DMZ:** o servidor Web localizado na DMZ não pode iniciar conexões em direção à rede interna (LAN). Essa restrição reduz o risco de que um servidor comprometido seja utilizado para acessar estações de trabalho internas. O firewall permite o tráfego de retorno de conexões previamente estabelecidas e autorizadas, mas não libera novas conexões originadas na DMZ em direção à Intranet.

## 6. Como executar

É necessário ter o Docker Desktop instalado e em execução, com suporte ao Docker Compose.

Clone o repositório e acesse a pasta do projeto:

```bash
git clone https://github.com/DavidCrr/trabalho-seguran-a.git
cd trabalho-seguran-a
```

Construa as imagens e inicie os serviços:

```bash
docker compose up -d --build
```

Verifique o estado dos contêineres:

```bash
docker compose ps
```

Para consultar os registros do firewall:

```bash
docker compose logs firewall
```

## 7. Testes e validação

Os testes verificam se as regras de filtragem estão funcionando conforme o esperado.

### 7.1 Teste positivo: acesso HTTP pela LAN

```bash
docker compose exec client wget -qO- http://172.21.0.10
```

**Resultado esperado:** o comando retorna o conteúdo HTML do portal Web.

### 7.2 Teste positivo: acesso HTTP pela WAN simulada

```bash
docker compose exec pharmacy wget -qO- http://172.21.0.10
```

**Resultado esperado:** o comando retorna o conteúdo HTML do portal Web.

### 7.3 Teste negativo: acesso direto ao PostgreSQL

```bash
docker compose exec client sh -c "nc -zvw 3 172.22.0.20 5432"
```

**Resultado esperado:** a conexão expira ou falha, demonstrando que o acesso direto ao banco não está autorizado pelas regras de encaminhamento.

### 7.4 Verificação das regras

Consultar as regras de encaminhamento:

```bash
docker compose exec firewall iptables -L FORWARD -n -v
```

Consultar as regras de tradução de endereços:

```bash
docker compose exec firewall iptables -t nat -L POSTROUTING -n -v
```

Os contadores de pacotes e bytes ajudam a verificar se o tráfego dos testes corresponde às regras configuradas.

## 8. Estrutura do projeto

```text
trabalho-seguran-a/
├── client/
│   └── Dockerfile
├── database/
│   └── init.sql
├── docs/
│   └── matriz-regras.md
├── firewall/
│   ├── Dockerfile
│   └── entrypoint.sh
├── relatorio/
│   └── trabalho.md
├── web/
│   └── index.html
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 9. Encerramento do ambiente

Para parar e remover os contêineres e as redes criadas pelo Compose:

```bash
docker compose down
```

## 10. Status do projeto

Projeto acadêmico em desenvolvimento, com ambiente Docker Compose executável, segmentação de rede, regras de filtragem com iptables e testes de conectividade realizados.

## 11. Finalidade acadêmica

Este projeto tem finalidade educacional e demonstra conceitos de segmentação de redes, filtragem de pacotes, isolamento de serviços e validação de regras de firewall em um ambiente controlado.
