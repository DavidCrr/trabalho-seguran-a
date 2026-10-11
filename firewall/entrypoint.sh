#!/bin/sh
set -eu

echo "[MedTech Firewall] Iniciando..."
echo "[MedTech Firewall] Interfaces de rede:"
ip -brief address

echo "[MedTech Firewall] Conferindo encaminhamento IPv4..."
cat /proc/sys/net/ipv4/ip_forward

echo "[MedTech Firewall] Configurando regras iniciais..."

iptables -F FORWARD
iptables -P FORWARD DROP

iptables -A FORWARD \
  -m conntrack \
  --ctstate ESTABLISHED,RELATED \
  -j ACCEPT

echo "[MedTech Firewall] Regras iniciais aplicadas."
iptables -L FORWARD -n -v


#!/bin/sh
set -eu

echo "[MedTech Firewall] Iniciando..."
echo "[MedTech Firewall] Interfaces de rede:"
ip -brief address

echo "[MedTech Firewall] Conferindo encaminhamento IPv4..."
cat /proc/sys/net/ipv4/ip_forward

echo "[MedTech Firewall] Configurando regras de firewall..."

# Limpa as regras antigas da cadeia FORWARD
iptables -F FORWARD

# Bloqueia por padrao todo trafego encaminhado
iptables -P FORWARD DROP

# Permite respostas de conexoes ja estabelecidas
iptables -A FORWARD \
  -m conntrack \
  --ctstate ESTABLISHED,RELATED \
  -j ACCEPT

# Permite que a rede LAN acesse o servidor web na porta HTTP 80
iptables -A FORWARD \
  -s 172.20.0.0/24 \
  -d 172.21.0.10 \
  -p tcp --dport 80 \
  -m conntrack --ctstate NEW \
  -j ACCEPT

echo "[MedTech Firewall] Regras aplicadas:"
iptables -L FORWARD -n -v

exec tail -f /dev/null