# Documentação Técnica

## Pré-requisitos

O dpckan necessita da versão v4 do frictionless-py para funcionar corretamente (vide [dpckan#202](https://github.com/transparencia-mg/dpckan/issues/202)).

```
docker build --secret id=secret,src=.env --tag matriz-fonte-stn-dadosmg .
docker run -e CKAN_HOST=$CKAN_HOST -e CKAN_KEY=$CKAN_KEY -e GITHUB_TOKEN=$GITHUB_TOKEN -it --rm --mount type=bind,source=$PWD,target=/project matriz-fonte-stn-dadosmg bash
```

## Uso

A publicação inicial do conjunto de dados deve ser realizada manualmente. Primeiro crie o arquivo `.env` com as variáveis de ambiente:

```
CKAN_HOST=https://homologa.cge.mg.gov.br
CKAN_KEY=ayJ5eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJsaDBsV29TVEN6Q01LeFVuWW90TW5oeVJMc2QtcTdXMk40MDVBUzY4MkpmUW82SHo5cVdYRks0ck1FSUxxM05FTUNvV0NESk05dzRYS3lQMCIsImlhdCI6MTY4MDAyMzQ2Pn0.WFgWR5i5bheI-p_aVnXrVwrkaRZjp5tw9Ua1COe3_JE
```

Os valores adequados devem ser obtidos na sua página de usuário do CKAN (eg. https://homologa.cge.mg.gov.br/user/fjunior).

Para efetivamente criar o conjunto execute

```bash
dpckan --datapackage datapackage.yaml dataset create
```

Para atualizar o conjunto execute

```bash
make all
```

---


## 🚀 Maiores orientações sobre o projeto

### 1. Configuração Inicial

```bash
# Instalar dependências Python
poetry install

# Configurar variáveis Docker
make config

# Criar arquivo de ambiente
cp env.example .env
# Editar .env com suas credenciais
```

### 2. Construir e Executar

```bash
# Construir imagem Docker
make docker-build

# Executar localmente
docker run -it --rm -v $(pwd):/project aidsplormg/matriz-fonte-stn-dadosmg:matriz-stn2025

# Ou executar comando específico
docker run -it --rm -v $(pwd):/project aidsplormg/matriz-fonte-stn-dadosmg:matriz-stn2025 make all
```

### 3. Enviar para Docker Hub

```bash
# Enviar imagem (após build)
make docker-push

# Ou construir e enviar em um comando
make docker-build-and-push
```

## 📋 Comandos Disponíveis

### Configuração
- `make config` - Configura variáveis Docker interativamente
- `make extract-info` - Extrai versões dos pacotes da imagem Docker
- `make pacotes-check-version` - Verifica e atualiza versões dos pacotes DCAF no GitHub
- `make update-ano` - Atualiza anos nos arquivos do projeto

### Docker
- `make docker-build` - Constrói a imagem Docker
- `make docker-push` - Envia imagem para Docker Hub
- `make docker-build-and-push` - Constrói e envia imagem para Docker Hub

### Processamento de Dados
- `make all` - Executa pipeline completo
- `make extract` - Instala dependências de dados (dpm install)
- `make transform` - Processa dados
- `make check` - Valida dados
- `make publish` - Publica dados
- `make push` - Envia para repositório

### Utilitários
- `make session-info` - Mostra informações da sessão
- `make clean` - Limpa arquivos temporários

## 🔧 Configuração

### Arquivo `config.mk`

Contém as configurações principais do projeto:

```makefile
# Ano da matriz
ANO_MATRIZ=2025

# Configurações Docker
DOCKER_TAG=matriz-stn2025
DOCKER_USER=aidsplormg
DOCKER_IMAGE=matriz-fonte-stn-dadosmg

# Versões dos pacotes R
RELATORIOS_VERSION=v0.7.99
EXECUCAO_VERSION=v0.5.27
REEST_VERSION=v0.2.8
```

### Arquivo `.env`

Variáveis de ambiente necessárias:

```bash
# GitHub
GITHUB_TOKEN=seu_token_github

# CKAN
CKAN_HOST=https://www.dados.mg.gov.br
CKAN_KEY=seu_token_ckan
```

## 🐳 Imagem Docker

A imagem Docker inclui:

- **R 4.3.2** com pacotes necessários
- **Python 3.8+** com dependências
- **dpm** para gerenciamento de dados
- **Pacotes DCAF** pré-instalados:
  - `relatorios`
  - `execucao` 
  - `reest`

### Labels da Imagem

A imagem inclui labels com informações de versão:

```dockerfile
LABEL relatorios.version="v0.7.99"
LABEL execucao.version="v0.5.27"
LABEL reest.version="v0.2.8"
LABEL ano.matriz="2025"
```

## 🔄 Workflow GitHub Actions

### Workflow Principal (`main.yaml`)
Executa:

1. **Verificação de versões** dos pacotes DCAF
2. **Build da imagem** com pacotes pré-instalados
3. **Push para Docker Hub** como `aidsplormg/matriz-fonte-stn-dadosmg:latest`
4. **Execução do pipeline** usando a imagem
5. **Publicação dos dados** no CKAN
6. **Commit e push** dos resultados

### Workflow de Verificação (`update-versions.yaml`)
Executa:

1. **Atualização do poetry.lock**
2. **Verificação de versões** dos pacotes DCAF
3. **Atualização automática** do `config.mk`
4. **Commit e push** das mudanças
5. **Disparo do workflow principal** se houver mudanças

### Workflow de Atualização de Ano (`update-year.yaml`)
Executa:

1. **Atualização automática** de anos nos arquivos
2. **Commit e push** das mudanças
3. **Disparo do workflow principal**

### Agendamento

- **Workflow Principal**: Segunda a sexta, 07:14 (Brasília)
- **Verificação de Versões**: Segunda-feira, 08:00 (Brasília)
- **Atualização de Ano**: 1º de fevereiro, 17:01 (Brasília)
- **Disparo Automático**: Quando há mudanças de versão

## 📦 Estrutura do Projeto

```
matriz-fonte-stn-dadosmg/
├── scripts/                 # Scripts Python
│   ├── config.py           # Configuração interativa
│   ├── docker_build.py     # Build da imagem
│   ├── docker_push.py      # Push para Docker Hub
│   ├── extract_info.py     # Extração de versões
│   ├── pacotes_check_version.py  # Verificação de versões
│   └── ano_update.py       # Atualização de anos
├── data.toml               # Configuração de dados
├── datapackage.yaml        # Esquema dos dados
├── config.mk              # Configurações do projeto
├── Dockerfile             # Imagem Docker
├── Makefile              # Comandos disponíveis
├── pyproject.toml        # Configuração Python
└── env.example           # Exemplo de variáveis de ambiente
```

## 🛠️ Desenvolvimento

### Adicionando Novos Scripts

1. Crie o script em `scripts/`
2. Adicione entrada no `pyproject.toml`:
   ```toml
   [tool.poetry.scripts]
   meu-script = "scripts.meu_script:main"
   ```
3. Adicione comando no `Makefile`:
   ```makefile
   meu-script: ## Descrição do comando
   	@poetry run meu-script
   ```

### Atualizando Versões

```bash
# Extrair versões da imagem atual
make extract-info

# Verificar versões no GitHub
make pacotes-check-version

# Atualizar anos nos arquivos
make update-ano
```

### Scripts Disponíveis

#### `config.py`
Configuração interativa das variáveis Docker.

#### `docker_build.py`
Constrói a imagem Docker com argumentos do `config.mk`.

#### `docker_push.py`
Envia a imagem Docker para o Docker Hub.

#### `extract_info.py`
Extrai versões dos pacotes R da imagem Docker e atualiza `config.mk`.

#### `pacotes_check_version.py`
Verifica versões dos pacotes DCAF no GitHub e atualiza `config.mk`.

#### `ano_update.py`
Atualiza anos nos arquivos do projeto (config.mk e scripts R).

## 🐛 Troubleshooting

### Erro de Build

```bash
# Verificar se .env existe
ls -la .env

# Verificar se Docker está rodando
docker version

# Build com verbose
make docker-build --verbose
```

### Erro de Push

```bash
# Fazer login no Docker Hub
docker login

# Verificar imagem local
docker images | grep matriz-fonte-stn-dadosmg
```

### Erro de Execução

```bash
# Verificar se imagem existe
docker images aidsplormg/matriz-fonte-stn-dadosmg

# Executar com debug
docker run -it --rm -v $(pwd):/project aidsplormg/matriz-fonte-stn-dadosmg:latest bash
```

### Erro de Dependências

```bash
# Reinstalar dependências
poetry install

# Atualizar poetry.lock
poetry lock

# Verificar dependências
poetry show
```

### Erro de Scripts

```bash
# Verificar se script está instalado
poetry run script-name

# Executar script diretamente
python scripts/script_name.py
```

## 📚 Referências

- [Docker Documentation](https://docs.docker.com/)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [dpm Documentation](https://github.com/splor-mg/dpm)
- [Portaria STN 710/2021](https://www.in.gov.br/en/web/dou/-/portaria-n-710-de-25-de-fevereiro-de-2021-305389863)
