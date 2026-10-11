# Relatório Técnico — MedTech Firewall

## 1. Definição do Case

O projeto MedTech Firewall consiste na implementação de um ambiente de rede simulado para demonstrar a aplicação de conceitos de segurança da informação, segmentação de redes e filtragem de tráfego por meio de um firewall.

O cenário representa uma organização fictícia da área de tecnologia médica, na qual diferentes serviços precisam se comunicar de forma controlada. Nesse ambiente, existe uma estação cliente utilizada por um funcionário, um servidor web responsável pela disponibilização de páginas e um banco de dados PostgreSQL destinado ao armazenamento de informações.

O principal problema abordado é o risco de comunicação indevida entre os diferentes componentes da infraestrutura. Em uma rede sem controles adequados, a possibilidade de acesso direto entre estações, servidores e bancos de dados pode aumentar a superfície de ataque e facilitar acessos não autorizados.

Dessa forma, o projeto tem como objetivo implementar uma arquitetura segmentada, na qual a comunicação entre as redes seja intermediada por um firewall e somente os fluxos expressamente autorizados sejam permitidos.

O ambiente foi desenvolvido utilizando Docker e Docker Compose, permitindo criar, configurar e reproduzir os componentes da infraestrutura de maneira controlada.

## 2. Diagnóstico

A análise do cenário identificou a necessidade de separar os componentes da infraestrutura em redes distintas, reduzindo a comunicação direta entre sistemas com funções diferentes.

Os principais riscos considerados foram:

* **Acesso indevido ao banco de dados:** um servidor web comprometido poderia tentar estabelecer conexões diretas com o banco de dados.
* **Comunicação excessiva entre redes:** a ausência de regras específicas poderia permitir tráfego desnecessário entre os componentes.
* **Falta de segmentação:** a utilização de uma única rede para todos os serviços aumentaria a exposição entre os sistemas.
* **Dificuldade de auditoria:** sem regras e contadores de tráfego, seria mais difícil verificar quais comunicações foram autorizadas ou descartadas.

Para reduzir esses riscos, foi adotada a segmentação em três redes: LAN, DMZ e rede do banco de dados.

A arquitetura utiliza um firewall com interfaces nas três redes, permitindo controlar o tráfego encaminhado entre elas por meio de regras do iptables.

## 3. Proposta de Solução

A solução consiste na implementação de uma infraestrutura virtualizada em contêineres, utilizando Docker Compose para orquestrar os serviços e redes.

Os componentes implementados são:

* **MedTech Client:** representa a estação de trabalho do usuário interno.
* **MedTech Firewall:** realiza a filtragem do tráfego entre as redes por meio do iptables.
* **MedTech Web:** servidor web baseado em Nginx, disponibilizado na DMZ.
* **MedTech Database:** banco de dados PostgreSQL conectado exclusivamente à rede do banco de dados e ao firewall.

A solução utiliza três redes Docker:

* **LAN:** destinada à estação cliente.
* **DMZ:** destinada ao servidor web.
* **Rede do banco de dados:** destinada ao PostgreSQL, configurada como rede interna do Docker.

O firewall possui uma interface em cada uma dessas redes e está configurado para encaminhar pacotes IPv4. A cadeia `FORWARD` do iptables utiliza a política padrão `DROP`, que descarta o tráfego encaminhado que não corresponda a uma regra de autorização.

Foram implementadas as seguintes regras principais:

1. Permitir pacotes relacionados a conexões já estabelecidas.
2. Permitir novas conexões HTTP originadas na LAN e destinadas ao servidor web da DMZ, pela porta TCP 80.
3. Descartar, pela política padrão, os demais pacotes encaminhados que não possuam uma regra de autorização correspondente.

As regras são configuradas pelo script `firewall/entrypoint.sh` durante a inicialização do contêiner, permitindo sua aplicação automática após a recriação do ambiente.

Essa abordagem segue o princípio do menor privilégio, segundo o qual cada componente deve possuir somente as permissões de comunicação necessárias para sua função.

## 4. Arquitetura da Rede

A infraestrutura é dividida em três segmentos de rede, interligados pelo firewall.

### 4.1. Endereçamento IP

| Componente       | Rede          | Endereço IP | Função                              |
| ---------------- | ------------- | ----------- | ----------------------------------- |
| MedTech Client   | LAN           | 172.20.0.10 | Estação cliente                     |
| Firewall — LAN   | LAN           | 172.20.0.2  | Gateway da estação cliente          |
| MedTech Web      | DMZ           | 172.21.0.10 | Servidor HTTP Nginx                 |
| Firewall — DMZ   | DMZ           | 172.21.0.2  | Gateway do servidor web             |
| MedTech Database | Rede do banco | 172.22.0.20 | Servidor PostgreSQL                 |
| Firewall — banco | Rede do banco | 172.22.0.2  | Interface de acesso à rede do banco |

### 4.2. Sub-redes

| Rede                   | Sub-rede      | Finalidade                     |
| ---------------------- | ------------- | ------------------------------ |
| LAN                    | 172.20.0.0/24 | Comunicação da estação cliente |
| DMZ                    | 172.21.0.0/24 | Hospedagem do servidor web     |
| Rede do banco de dados | 172.22.0.0/24 | Comunicação com o PostgreSQL   |

A rede do banco de dados foi configurada com a opção `internal: true` no Docker Compose, restringindo sua conectividade externa direta por meio da rede Docker.

O firewall possui três interfaces de rede e funciona como ponto de controle para o tráfego entre os segmentos.

A topologia lógica pode ser representada da seguinte maneira:

```text
                 LAN
          172.20.0.0/24
                 |
          MedTech Client
           172.20.0.10
                 |
          Firewall — LAN
            172.20.0.2
                 |
          MEDTECH FIREWALL
                 |
          Firewall — DMZ
            172.21.0.2
                 |
           MedTech Web
           172.21.0.10
                 |
         Rede do banco de dados
          172.22.0.0/24
                 |
          Firewall — banco
            172.22.0.2
                 |
         MedTech Database
           172.22.0.20
```

**Observação:** o diagrama é uma representação lógica dos segmentos conectados ao firewall. Ele não significa que o servidor web possua conexão direta com a rede do banco de dados. O servidor web está conectado à DMZ, enquanto o PostgreSQL está conectado à rede interna do banco. A comunicação entre esses segmentos depende das regras do firewall.

## 5. Matriz de Regras

A matriz apresenta as principais políticas implementadas para o tráfego encaminhado pela cadeia `FORWARD` do iptables.

| Origem                                 | Destino                      | Serviço                                             | Política                                                        |
| -------------------------------------- | ---------------------------- | --------------------------------------------------- | --------------------------------------------------------------- |
| LAN — 172.20.0.0/24                    | Web — 172.21.0.10            | HTTP, TCP 80                                        | Permitir novas conexões                                         |
| Qualquer origem encaminhada            | Qualquer destino encaminhado | Respostas de conexões estabelecidas ou relacionadas | Permitir                                                        |
| Web — 172.21.0.10                      | Banco — 172.22.0.20          | PostgreSQL, TCP 5432                                | Bloqueado pela política padrão, na ausência de regra específica |
| Demais origens e destinos encaminhados | Demais serviços              | Não autorizado explicitamente                       | Bloquear por padrão                                             |

A política padrão da cadeia `FORWARD` é `DROP`. Isso significa que o tráfego encaminhado que não corresponder a uma regra de autorização é descartado.

A regra `ESTABLISHED,RELATED` permite o tráfego de retorno associado a conexões existentes ou relacionadas. Ela não concede, por si só, autorização para iniciar qualquer nova conexão.

A regra HTTP autoriza novas conexões TCP com destino ao endereço `172.21.0.10`, na porta 80, quando originadas na sub-rede LAN `172.20.0.0/24`.

**Limitação importante:** a matriz descreve as regras implementadas na cadeia `FORWARD`. Ela não representa uma auditoria completa de todas as cadeias do iptables, como `INPUT` e `OUTPUT`, nem de todas as possíveis formas de comunicação dentro de cada segmento.

## 6. Metodologia de Testes

Os testes foram realizados com os contêineres em execução, utilizando comandos executados pelo Docker Compose e verificações de conectividade entre os componentes.

O objetivo foi verificar a comunicação entre a LAN, a DMZ e a rede do banco de dados, além de observar o comportamento das regras de filtragem.

### 6.1. Teste 1 — Conectividade entre cliente e firewall

**Objetivo:** verificar se a estação cliente consegue alcançar o endereço do firewall conectado à LAN.

Comando utilizado:

```bash
docker compose exec client ping -c 3 172.20.0.2
```

**Resultado:** o cliente conseguiu alcançar o endereço `172.20.0.2`.

**Interpretação:** o resultado confirmou a conectividade entre o cliente e a interface LAN do firewall.

### 6.2. Teste 2 — Conectividade entre firewall e servidor web

**Objetivo:** verificar se o firewall consegue alcançar o servidor web conectado à DMZ.

Comando utilizado:

```bash
docker compose exec firewall ping -c 3 172.21.0.10
```

**Resultado:** foi confirmada a conectividade entre o firewall e o servidor web.

Também foi realizado um teste HTTP a partir do firewall, utilizando o endereço `172.21.0.10`.

**Resultado HTTP:** `HTTP/1.1 200 OK`.

**Interpretação:** o servidor Nginx estava acessível e respondendo às requisições HTTP.

### 6.3. Teste 3 — Acesso HTTP autorizado da LAN para a DMZ

**Objetivo:** verificar se o cliente consegue acessar o servidor web por meio do firewall, utilizando a regra de autorização para TCP na porta 80.

Comando utilizado:

```bash
docker compose exec client curl -I --max-time 5 http://172.21.0.10
```

**Resultado:** o servidor respondeu com `HTTP/1.1 200 OK`.

**Interpretação:** o resultado confirmou que o cliente conseguiu acessar o servidor web e que a comunicação HTTP autorizada estava funcionando após a configuração das regras e a recriação do ambiente.

### 6.4. Teste 4 — Tentativa de acesso ao banco de dados

**Objetivo:** verificar o comportamento da política de segurança diante de uma tentativa de comunicação do servidor web com o PostgreSQL.

A tentativa foi realizada a partir do contêiner web, utilizando o endereço `172.22.0.20` e a porta TCP 5432.

O comando utilizado foi:

```bash
docker compose exec web wget -T 3 -S -O /dev/null http://172.22.0.20:5432
```

**Resultado:** a tentativa terminou em timeout, sem estabelecer uma comunicação HTTP bem-sucedida.

**Interpretação:** o resultado é compatível com o bloqueio do tráfego entre a DMZ e a rede do banco de dados. Entretanto, como o `wget` é um cliente HTTP e o PostgreSQL utiliza seu próprio protocolo, o timeout isoladamente não comprova que o firewall foi a única causa da falha.

### 6.5. Teste 5 — Verificação dos contadores do firewall

**Objetivo:** observar os contadores da cadeia `FORWARD` durante uma nova tentativa de acesso ao banco de dados.

Inicialmente, os contadores foram zerados:

```bash
docker compose exec firewall iptables -Z FORWARD
```

Em seguida, foi repetida a tentativa de acesso à porta 5432 a partir do contêiner web. Por fim, foram consultadas as regras e seus contadores:

```bash
docker compose exec firewall iptables -L FORWARD -n -v
```

**Resultado observado:** a política padrão `DROP` registrou três pacotes descartados, totalizando 180 bytes. As duas regras de autorização exibiram zero pacotes durante essa medição.

**Interpretação:** o registro de pacotes descartados é uma evidência adicional de que houve tráfego bloqueado pela política padrão durante o período do teste. Entretanto, os contadores da política `DROP` são agregados e, sozinhos, não identificam o destino ou a origem de cada pacote descartado. Portanto, não é possível afirmar apenas com essa medição que os três pacotes eram necessariamente a tentativa de acesso ao PostgreSQL.

### 6.6. Teste 6 — Persistência da configuração após reinicialização

**Objetivo:** verificar se as regras do firewall são aplicadas automaticamente quando o ambiente é recriado.

Foram executados os seguintes comandos:

```bash
docker compose down
docker compose up -d --build
```

Depois da recriação, foi consultado o estado dos contêineres e das regras do firewall.

**Resultado:** os contêineres foram iniciados e as regras da cadeia `FORWARD` voltaram a aparecer conforme definido no script de inicialização.

**Interpretação:** o teste confirmou que a configuração das regras é executada automaticamente pelo script `firewall/entrypoint.sh` durante a inicialização do contêiner. Isso evita a necessidade de inserir manualmente as regras a cada recriação do ambiente.

### 6.7. Resumo dos resultados

| Teste                          | Resultado                                              | Avaliação                                                                                     |
| ------------------------------ | ------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| Cliente → firewall LAN         | Conectividade confirmada                               | Aprovado                                                                                      |
| Firewall → servidor web        | Conectividade confirmada                               | Aprovado                                                                                      |
| Cliente → servidor web, TCP 80 | HTTP 200 OK                                            | Aprovado                                                                                      |
| Web → banco, TCP 5432          | Timeout                                                | Compatível com o bloqueio esperado; requer teste específico de TCP para confirmação adicional |
| Contadores do `FORWARD`        | 3 pacotes e 180 bytes descartados pela política padrão | Evidência adicional de descarte                                                               |
| Reinicialização do ambiente    | Regras reaplicadas automaticamente                     | Aprovado                                                                                      |

## 7. Conclusão

O projeto MedTech Firewall demonstrou a implementação de uma infraestrutura de rede segmentada, utilizando Docker, Docker Compose e iptables para controlar o tráfego entre a LAN, a DMZ e a rede do banco de dados.

Os testes confirmaram o funcionamento da conectividade entre os componentes e o acesso HTTP autorizado do cliente ao servidor web, que retornou o código `HTTP/1.1 200 OK`.

A tentativa de comunicação entre o servidor web e o PostgreSQL terminou em timeout, e a consulta aos contadores do firewall registrou pacotes descartados pela política padrão `DROP`. Esses resultados são compatíveis com a política de restrição de tráfego implementada, embora testes adicionais sejam necessários para atribuir de forma conclusiva os descartes à tentativa específica de acesso ao banco.

A configuração também foi validada após a recriação do ambiente, demonstrando que o script de inicialização reaplica automaticamente as regras de filtragem.

Como próximos passos, recomenda-se realizar testes específicos de conectividade TCP para os serviços protegidos, avaliar separadamente as cadeias `INPUT` e `OUTPUT`, revisar os acessos administrativos e implementar mecanismos adicionais de registro e monitoramento.

Conclui-se que o laboratório atende ao objetivo de demonstrar os conceitos fundamentais de segmentação de rede, filtragem de tráfego e aplicação do princípio do menor privilégio. A solução constitui uma base didática para o estudo de segurança de redes, não devendo ser considerada, sem controles e validações adicionais, uma infraestrutura pronta para utilização em produção.
