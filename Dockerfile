FROM rocker/r-ver:4.3.2
ARG relatorios_version
ARG execucao_version
ARG reest_version
ARG ano_matriz
ARG docker_tag
ARG docker_user
ARG docker_image

WORKDIR /project

RUN /rocker_scripts/install_python.sh

RUN export DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y git software-properties-common

# Instalar Python 3.11
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils

# Instalar Poetry usando Python 3.11
RUN python3.11 -m pip install poetry

# Copiar arquivos de configuração Python
COPY pyproject.toml poetry.lock* ./

# Configurar Poetry e instalar dependências
RUN poetry config virtualenvs.create false && \
    poetry lock && \
    poetry install --only=main --no-interaction --no-ansi --no-root

# Instalar versão compatível do Frictionless antes de usar dpm
RUN python3.11 -m pip install "frictionless>=5.14,<6"

# Copiar DESCRIPTION para R
COPY DESCRIPTION .
RUN Rscript -e "install.packages('renv')"
RUN Rscript -e "renv::install()"

# Instalar pacotes R necessários
RUN Rscript -e "install.packages(c('dotenv', 'remotes'))"

# Instalar pacotes DCAF
RUN --mount=type=secret,id=secret Rscript -e \
    "dotenv::load_dot_env('/run/secrets/secret'); remotes::install_github('splor-mg/relatorios@$relatorios_version', auth_token = Sys.getenv('GITHUB_TOKEN'))"
RUN --mount=type=secret,id=secret Rscript -e \
    "dotenv::load_dot_env('/run/secrets/secret'); remotes::install_github('splor-mg/execucao@$execucao_version', auth_token = Sys.getenv('GITHUB_TOKEN'))"
RUN --mount=type=secret,id=secret Rscript -e \
    "dotenv::load_dot_env('/run/secrets/secret'); remotes::install_github('splor-mg/reest@$reest_version', auth_token = Sys.getenv('GITHUB_TOKEN'))"

# Copiar arquivos de configuração
COPY data.toml .
COPY datapackage.yaml .

# Garantir compatibilidade do dpm com Frictionless 5.x
# dpm usa System.use_context, presente na API 5.x
RUN python3.11 -m pip install "frictionless>=5.14,<6"

# Instalar dependências de dados usando dpm (carregando o secret como env)
RUN --mount=type=secret,id=secret bash -lc "set -a && . /run/secrets/secret || true && set +a && poetry run dpm install"

# Configurar labels da imagem
LABEL org.opencontainers.image.title="Matriz Fonte STN Dados MG"
LABEL org.opencontainers.image.description="Imagem Docker para processamento de dados da matriz fonte STN"
LABEL org.opencontainers.image.version="$docker_tag"
LABEL org.opencontainers.image.vendor="Splor MG"
LABEL relatorios.version="$relatorios_version"
LABEL execucao.version="$execucao_version"
LABEL reest.version="$reest_version"
LABEL ano.matriz="$ano_matriz"

ENTRYPOINT ["/bin/bash", "-c"]

