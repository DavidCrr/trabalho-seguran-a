# Matriz de Regras do Firewall

O firewall utiliza uma política padrão de bloqueio para o encaminhamento de pacotes (`FORWARD DROP`), permitindo apenas os fluxos expressamente definidos pelas regras de filtragem.

## Matriz de Regras de Encaminhamento (FORWARD)

| Origem                                     | Destino                             | Serviço                   | Ação                                        | Justificativa / Descrição                                      |
| ------------------------------------------ | ----------------------------------- | ------------------------- | ------------------------------------------- | -------------------------------------------------------------- |
| Conexões estabelecidas ou relacionadas     | Redes encaminhadas pelo firewall    | Conforme conexão original | Permitir (`ACCEPT`)                         | Respostas e fluxos autorizados de conexões previamente abertas |
| LAN (`172.20.0.0/24`)                      | Servidor Web na DMZ (`172.21.0.10`) | TCP/80 (HTTP)             | Permitir (`ACCEPT`)                         | Acesso interno dos colaboradores ao portal HTTP                |
| WAN simulada (`172.23.0.0/24`)             | Servidor Web na DMZ (`172.21.0.10`) | TCP/80 (HTTP)             | Permitir (`ACCEPT`)                         | Acesso externo simulado ao portal HTTP                         |
| DMZ (`172.21.0.0/24`)                      | LAN / Intranet (`172.20.0.0/24`)    | Qualquer                  | Bloquear novas conexões (`DROP`)            | Isolamento da DMZ para evitar movimentação lateral para a LAN  |
| LAN ou WAN simulada                        | Banco de dados (`172.22.0.20`)      | Acesso direto (TCP/5432)  | Bloquear por ausência de regra de permissão | Impede acesso direto ao banco, isolando os dados               |
| Outros fluxos encaminhados não autorizados | Qualquer destino                    | Qualquer serviço          | Bloquear pela política padrão (`DROP`)      | Princípio do menor privilégio                                  |

### Detalhamento das Políticas

* **Bloqueio ao Banco de Dados:** o bloqueio de acesso ao banco de dados decorre da política padrão de encaminhamento, não de uma regra específica de bloqueio da porta 5432.
* **Isolamento da DMZ:** o servidor Web localizado na DMZ não pode iniciar conexões em direção à rede interna (LAN). Essa restrição reduz o risco de que um servidor comprometido seja utilizado para acessar estações de trabalho internas. O firewall permite o tráfego de retorno de conexões previamente estabelecidas e autorizadas, mas não libera novas conexões originadas na DMZ em direção à Intranet.

## Regras de Tradução de Endereços (NAT / SNAT)

Na tabela `nat`, cadeia `POSTROUTING`, são aplicadas regras de SNAT para viabilizar o retorno correto das respostas do servidor Nginx na DMZ:

| Origem                         | Destino                             | Serviço       | Ação (SNAT)                   |
| ------------------------------ | ----------------------------------- | ------------- | ----------------------------- |
| LAN (`172.20.0.0/24`)          | Servidor Web na DMZ (`172.21.0.10`) | TCP/80 (HTTP) | Traduzir para IP `172.21.0.2` |
| WAN simulada (`172.23.0.0/24`) | Servidor Web na DMZ (`172.21.0.10`) | TCP/80 (HTTP) | Traduzir para IP `172.21.0.2` |
