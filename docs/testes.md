# Testes de Segurança

Guia rápido de execução e validação dos testes do firewall.

## Testes Positivos (Fluxos Autorizados)

1. **Acesso HTTP pela LAN:**
   ```bash
   docker compose exec client wget -qO- http://172.21.0.10
   ```
   *Resultado esperado:* Retorno do HTML do portal Web (`HTTP 200 OK`).

2. **Acesso HTTP pela WAN Simulada:**
   ```bash
   docker compose exec pharmacy wget -qO- http://172.21.0.10
   ```
   *Resultado esperado:* Retorno do HTML do portal Web (`HTTP 200 OK`).

## Testes Negativos (Fluxos Bloqueados)

1. **Acesso direto da LAN ao PostgreSQL:**
   ```bash
   docker compose exec client sh -c "nc -zvw 3 172.22.0.20 5432"
   ```
   *Resultado esperado:* Conexão expira ou falha (bloqueio pela política padrão `DROP`).

2. **Isolamento da DMZ em direção à LAN:**
   ```bash
   docker compose exec web wget -T 3 -S -O /dev/null http://172.20.0.10
   ```
   *Resultado esperado:* Timeout (`download timed out`), confirmando que a DMZ não inicia conexões com a Intranet.

## Verificação de Regras e Contadores

```bash
docker compose exec firewall iptables -L FORWARD -n -v
docker compose exec firewall iptables -t nat -L POSTROUTING -n -v
```
