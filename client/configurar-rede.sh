
#!/bin/sh
set -eu

echo "[MedTech Client] Configurando gateway..."

ip route replace default via 172.20.0.2

echo "[MedTech Client] Rotas configuradas:"
ip route

echo "[MedTech Client] Configuracao concluida."