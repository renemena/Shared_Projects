# VLAN / Network / Profile Validation Tool

Ferramenta em Python para automatizar a validação de VLANs em configurações de **HPE Virtual Connect / BladeSystem**, correlacionando:

- VLANs de uma lista base;
- Networks e Network Ranges presentes na configuração;
- NAGs associados às Networks;
- Profiles informados pelo usuário;
- VLANs configuradas em cada Profile.

O resultado é exportado para uma planilha Excel contendo uma linha por VLAN e uma coluna adicional para cada Profile encontrado.

---

## 1. Objetivo

O script `valida_vlan_enclosure_ehp-v9.py` foi desenvolvido para facilitar a comparação de VLANs em arquivos de configuração do Virtual Connect.

A ferramenta recebe três arquivos de entrada:

1. **Arquivo base de VLANs**
2. **Arquivo de configuração para comparação**
3. **Arquivo com os termos/nome dos Profiles**

Durante a execução, o usuário também escolhe o diretório onde será gravada a planilha de resultado.

A aplicação procura as VLANs do arquivo base na configuração e identifica:

- se a VLAN existe;
- o NAG associado;
- o nome ou prefixo da Network;
- em quais Profiles a VLAN está configurada.

---

## 2. Funcionalidades

A versão atual possui as seguintes funcionalidades:

- Seleção gráfica dos arquivos de entrada;
- Seleção gráfica do diretório de saída;
- Leitura de VLANs individuais;
- Expansão automática de ranges de VLAN;
- Identificação de `add network`;
- Identificação de `add network-range`;
- Captura do campo `NAGs=`;
- Captura do nome da Network;
- Captura do campo `nameprefix=`;
- Busca parcial de Profiles;
- Busca sem diferenciação entre letras maiúsculas e minúsculas;
- Identificação das VLANs associadas aos Profiles;
- Análise de `server-port-map-range`;
- Análise de `server-port-map`;
- Geração automática de planilha Excel;
- Uma coluna por Profile identificado;
- Resultado `VERDADEIRO` ou `FALSO` por VLAN/Profile.

---

## 3. Requisitos

### Sistema operacional

O script foi desenvolvido para execução em ambiente com interface gráfica, como:

- Windows 10;
- Windows 11;
- Linux com ambiente gráfico e suporte ao Tkinter.

### Python

Recomendado:

```text
Python 3.10 ou superior
```

### Bibliotecas Python

O script utiliza:

```text
pandas
openpyxl
tkinter
pathlib
re
```

`pathlib`, `re` e normalmente `tkinter` fazem parte da instalação padrão do Python.

Instale as dependências externas com:

```bash
pip install pandas openpyxl
```

Caso utilize ambiente virtual:

```bash
python -m venv .venv
```

No Windows:

```bash
.venv\Scripts\activate
```

Depois:

```bash
pip install pandas openpyxl
```

---

## 4. Estrutura sugerida do projeto

```text
vlan-profile-validator/
│
├── valida_vlan_enclosure_ehp-v9.py
├── README.md
├── requirements.txt
│
└── exemplos/
    ├── arquivo_base_vlans.txt
    ├── arquivo_base_profiles.txt
    └── enclosure_config.txt
```

Um arquivo `requirements.txt` pode conter:

```text
pandas
openpyxl
```

Para instalar:

```bash
pip install -r requirements.txt
```

---

## 5. Arquivos de entrada

### 5.1 Arquivo base de VLANs

Arquivo texto contendo uma VLAN por linha.

Exemplo:

```text
1000
1001
1002
1003
1004
1005
1006
1007
1008
```

Linhas vazias são ignoradas. VLANs duplicadas no arquivo base são removidas automaticamente durante o processamento.

### 5.2 Arquivo de configuração para comparação

Este deve ser o arquivo contendo a configuração completa do Virtual Connect.

O script analisa diferentes tipos de comando dentro deste arquivo.

#### `add network`

Exemplo:

```text
add network VC5-NAME-VLAN -quiet UplinkSet=UPLINK VLanID=VLAN NAGs=Default
```

O script identifica:

```text
VLAN    = 1000
Network = VC5-NAME-VLAN
NAGs    = Default
```

#### `add network-range`

Exemplo:

```text
add network-range -quiet UplinkSet=UPLINK nameprefix=NAME- vlanids=1000,1001,1002-1005,1006-1010 NAGs=Default SmartLink=Enabled
```

O script identifica:

```text
Network = NAME-
NAGs    = Default
```

E expande automaticamente os ranges.

Por exemplo:

```text
1006-1010
```

é convertido em:

```text
1006
1007
1008
1009
1010
```

Da mesma forma:

```text
1003-1004
```

é convertido em:

```text
1003
1004
```

Também são aceitas listas contendo VLANs individuais e ranges:

```text
1000,1001,1002-1005,1006-1010
```

### 5.3 Arquivo de Profiles

O arquivo de Profiles funciona como uma **lista de termos de pesquisa**.

Exemplo:

```text
esxi0001
esxi0002
esxi0003
```

Não é necessário informar o nome completo do Profile.

Por exemplo, o termo:

```text
esxi0001
```

pode localizar:

```text
PROD-ESXi0001
```

A busca:

- considera o termo em qualquer parte do nome;
- não diferencia maiúsculas de minúsculas.

Portanto, os seguintes termos podem localizar o mesmo Profile:

```text
esxi0001
ESXi0001
Esxi0001
PROD-ESXi0001
```

Desde que o valor informado esteja contido no nome do Profile presente no arquivo de configuração.

---

## 6. Como os Profiles são identificados

Primeiro, o programa localiza os comandos:

```text
add profile
```

Exemplo:

```text
add profile PROD-ESXi0001 -NoDefaultEnetConn -NoDefaultFcConn -NoDefaultFcoeConn -quiet NAG=Default
```

Se o arquivo de Profiles possuir:

```text
esxi0001
```

o Profile completo:

```text
PROD-ESXi0001
```

será selecionado para análise.

---

## 7. Como as VLANs dos Profiles são identificadas

Depois que o Profile é encontrado, o programa procura as VLANs associadas a ele no mesmo arquivo de configuração.

### 7.1 `server-port-map-range`

Exemplo:

```text
add server-port-map-range PROD-ESXi0001:3 UplinkSet=UPLINK vlanids=1000,1001,1002-1005,1006,1007,1008-1010 MatchUplinkSet=true
```

As VLANs são extraídas do campo:

```text
vlanids=
```

Ranges também são expandidos.

Por exemplo:

```text
1002-1006
```

resulta em:

```text
1002
1003
1004
1005
1006
```

### 7.2 `server-port-map`

O programa também suporta configurações que associam diretamente uma Network ao Profile.

Exemplo:

```text
add server-port-map PROD-ESXi0001:7 VC5-NAME-VLAN UplinkSet=UPLINK Untagged=false
```

Nesse caso, o programa:

1. identifica o nome da Network;
2. procura essa Network entre as Networks previamente mapeadas;
3. identifica a VLAN correspondente;
4. adiciona a VLAN ao Profile.

---

## 8. Executando o programa

Execute:

```bash
python valida_vlan_enclosure_ehp-v9.py
```

No Windows, dependendo da instalação:

```bash
py valida_vlan_enclosure_ehp-v9.py
```

Ao iniciar, serão apresentadas janelas para seleção dos arquivos.

---

## 9. Ordem das seleções

O programa solicitará, nesta ordem:

### Passo 1 — Arquivo base de VLANs

Selecione o arquivo contendo uma VLAN por linha.

Exemplo:

```text
arquivo_base_vlans.txt
```

### Passo 2 — Arquivo de comparação

Selecione o arquivo contendo a configuração completa do Virtual Connect.

Exemplo:

```text
enclosure_vlans_config_compare_ehp18.txt
```

### Passo 3 — Arquivo de Profiles

Selecione o arquivo contendo os Profiles ou termos de busca.

Exemplo:

```text
arquivo_base_profiles_ehp18.txt
```

### Passo 4 — Diretório de saída

Selecione a pasta onde será criada a planilha.

---

## 10. Arquivo de saída

O arquivo gerado possui o nome:

```text
resultado_comparacao_profiles.xlsx
```

Ele será salvo no diretório escolhido pelo usuário.

---

## 11. Estrutura da planilha de saída

As primeiras colunas são fixas:

| Coluna | Descrição |
|---|---|
| VLAN | VLAN proveniente do arquivo base |
| Encontrado | Informa se a VLAN foi encontrada nas definições de Network |
| NAGs | Valor de `NAGs=` encontrado na configuração |
| Network | Nome da Network ou `nameprefix` correspondente |

Depois destas colunas, o programa adiciona uma coluna para cada Profile encontrado.

Exemplo:

| VLAN | Encontrado | NAGs | Network | PROD-ESXi0001 | PROD-ESXi0002 | PROD-ESXi0003 |
|---:|---|---|---|---|---|---|
| 1001 | VERDADEIRO | Default | VC5_NAME-VLAN | VERDADEIRO | VERDADEIRO | VERDADEIRO |
| 1002 | VERDADEIRO | Default | VC5-NAME-VLAN | VERDADEIRO | VERDADEIRO | VERDADEIRO |
| 1003 | VERDADEIRO | Default | VC5-NAME-VLAN | VERDADEIRO | VERDADEIRO | VERDADEIRO |
| 1004 | FALSO |  |  | FALSO | FALSO | FALSO |

> Os valores acima são apenas uma representação do formato esperado da planilha.

---

## 12. Significado de `Encontrado`

A coluna `Encontrado` refere-se à presença da VLAN nas definições:

```text
add network
```

ou:

```text
add network-range
```

Os valores possíveis são:

```text
VERDADEIRO
FALSO
```

---

## 13. Significado das colunas de Profile

Cada Profile identificado gera uma nova coluna.

Exemplo:

```text
PROD-ESXi0001
```

Para cada VLAN:

```text
VERDADEIRO
```

significa que a VLAN foi identificada naquele Profile.

```text
FALSO
```

significa que a VLAN não foi identificada naquele Profile.

---

## 14. Regras de interpretação das VLANs

O script suporta:

### VLAN única

```text
VLanID=1001
```

### Lista de VLANs

```text
vlanids=1001,1002,1003
```

### Range

```text
vlanids=1004-1006
```

### Lista com ranges

```text
vlanids=1001,1002,1003,1004-1006,1007,1008-1010
```

O resultado interno será:

```text
1001
1002
1003
1004
1005
1006
1007
1008
1009
1010
```

---

## 15. Regras para Network

### Para `add network`

O valor imediatamente após `add network` é utilizado na coluna `Network`.

Exemplo:

```text
add network VC5-NAME-VLAN ...
```

Resultado:

```text
Network = VC5-NAME-VLAN
```

### Para `add network-range`

É utilizado o valor de `nameprefix=`.

Exemplo:

```text
nameprefix=VC5-NAME-
```

Resultado:

```text
Network = VC5-NAME-
```

---

## 16. Regras para NAGs

O script procura o campo `NAGs=` na mesma linha da definição da Network.

Exemplo:

```text
NAGs=Default
```

Resultado:

```text
Default
```

---

## 17. Resumo exibido após a execução

Ao finalizar, o programa apresenta uma mensagem contendo informações como:

```text
Arquivo gerado com sucesso
VLANs do arquivo base
VLANs mapeadas em Networks
Termos de Profile pesquisados
Profiles completos identificados
VLANs identificadas por Profile
```

Caso algum termo informado no arquivo de Profiles não tenha correspondência, ele também será apresentado na mensagem final.

Exemplo:

```text
Termos de Profile sem correspondência:
  - esx99999
```

---

## 18. Exemplo de fluxo completo

### Arquivo de VLANs

```text
1000
1002
1003
1004
1005
1006
```

### Arquivo de Profiles

```text
esxi0001
esxi0002
```

### Configuração

O programa encontra:

```text
add profile PROD-ESXi0001 ...
add profile PROD-ESXi0002 ...
```

Em seguida localiza comandos como:

```text
add server-port-map-range PROD-ESXi0001:11 UplinkSet=UPLINK vlanids=1000,1001,1002,1004-1006,1007,1008-1010 MatchUplinkSet=true
```

e:

```text
add server-port-map PROD-ESXi0001:7 VC5-NAME-VLAN UplinkSet=UPLINK Untagged=false
```

O resultado terá colunas semelhantes a:

```text
VLAN
Encontrado
NAGs
Network
PROD-ESXi0001
PROD-ESXi0002
PROD-ESXi0003
```

---

## 19. Troubleshooting

### Erro `No module named pandas`

Instale:

```bash
pip install pandas
```

### Erro relacionado ao `openpyxl`

Instale:

```bash
pip install openpyxl
```

### A planilha não é gerada

Verifique:

- se o diretório de saída existe;
- se há permissão de escrita;
- se o arquivo `resultado_comparacao_profiles.xlsx` não está aberto no Excel;
- se os três arquivos de entrada foram selecionados corretamente.

### Nenhum Profile foi encontrado

Verifique o arquivo de Profiles. Ele deve possuir um termo por linha:

```text
esxI0001
esxI0002
esxI0003
```

Depois procure esses valores no arquivo de configuração.

Por exemplo, `esxI0001` deverá aparecer dentro de algo como:

```text
add profile PROD-ESXi0001 ...
```

A busca não diferencia maiúsculas e minúsculas.

### Profile encontrado, mas todas as VLANs aparecem como FALSO

Verifique se existem linhas como:

```text
add server-port-map-range NOME-DO-PROFILE:porta ... vlanids=...
```

ou:

```text
add server-port-map NOME-DO-PROFILE:porta NOME-DA-NETWORK ...
```

O nome do Profile usado nessas linhas deve corresponder ao Profile identificado pelo programa.

### Network ou NAGs aparecem vazios

Verifique se a VLAN existe em uma linha:

```text
add network
```

ou:

```text
add network-range
```

A coluna `Encontrado` indica especificamente se a VLAN foi encontrada nessas definições.

### Range de VLAN não foi reconhecido

Utilize o formato:

```text
1000-1006
```

ou:

```text
1000,1001,1002,1004,1005,1006
```

---

## 20. Observações importantes

O script foi construído considerando a sintaxe encontrada nas configurações de HPE Virtual Connect analisadas durante o desenvolvimento.

Mudanças significativas no formato dos comandos exportados pelo equipamento podem exigir ajustes nas expressões regulares utilizadas pelo programa.

Antes de utilizar o resultado em mudanças de produção, recomenda-se validar uma amostra das VLANs diretamente contra a configuração original.

---

## 21. Segurança

O script:

- não altera a configuração dos equipamentos;
- não realiza acesso remoto;
- não executa comandos em switches, blades ou Virtual Connect;
- trabalha somente com arquivos locais selecionados pelo usuário;
- cria apenas a planilha de resultado no diretório escolhido.

Mesmo assim, arquivos de configuração podem conter informações sensíveis.

Antes de publicá-los ou adicioná-los ao GitHub, revise informações como:

- endereços IP;
- nomes internos;
- usuários;
- comunidades SNMP;
- dados de autenticação;
- informações de infraestrutura.

Evite versionar arquivos de configuração reais contendo dados sensíveis.

Exemplo de `.gitignore`:

```gitignore
*.xlsx
*.log

# Arquivos locais de configuração
config/
input/
output/

# Ambientes Python
.venv/
venv/
__pycache__/
*.pyc
```

---

## 22. Execução rápida

```bash
git clone <URL_DO_REPOSITORIO>
cd <DIRETORIO_DO_REPOSITORIO>

python -m venv .venv
.venv\Scripts\activate

pip install pandas openpyxl

python valida_vlan_enclosure_ehp-v9.py
```

No Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install pandas openpyxl

python3 valida_vlan_enclosure_ehp-v9.py
```

---

## 23. Licença

Defina a licença do projeto conforme a política do repositório ou da organização responsável.

Exemplos comuns:

- MIT
- Apache-2.0
- Uso interno / proprietário

---

## 24. Histórico

### v9

- Seleção interativa dos arquivos;
- Busca de VLANs base;
- Identificação de `add network`;
- Identificação de `add network-range`;
- Suporte a ranges de VLAN;
- Captura de Network;
- Captura de NAGs;
- Arquivo separado com termos de Profiles;
- Busca parcial e case-insensitive de Profiles;
- Correlação dos Profiles com `server-port-map-range`;
- Correlação dos Profiles com `server-port-map`;
- Criação dinâmica de uma coluna para cada Profile;
- Exportação para Excel.

---

## Autor / Projeto

Ferramenta desenvolvida para automação de validação de configurações de rede e infraestrutura.

Para melhorias ou correções, utilize **Issues** e **Pull Requests** no repositório GitHub.
