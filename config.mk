# =============================================================================
# CONFIGURAÇÕES DO PROJETO MATRIZ-FONTE-STN-DADOSMG
# =============================================================================
# ATENÇÃO: Este arquivo é gerado automaticamente pelo comando 'make config'
# Caso precise alterar sua estrutura, não deixe de verificar os scripts 
# scripts/extract_info.py e scripts/config.py
# Este arquivo deve ser versionado e atualizado a cada nova versão
# Última atualização: 2025-09-27 (commit: auto-generated)
# =============================================================================

# =============================================================================
# CONFIGURAÇÕES GERAIS
# =============================================================================
# Ano de referência para a matriz de fonte STN
ANO_MATRIZ=2022

# =============================================================================
# CONFIGURAÇÕES DOCKER
# =============================================================================
# Tag da imagem Docker (versão)
DOCKER_TAG=matriz-stn2025

# Usuário do Docker Hub
DOCKER_USER=aidsplormg

# Nome da imagem Docker
DOCKER_IMAGE=matriz-fonte-stn-dadosmg

# =============================================================================
# VERSÕES DOS PACOTES R
# =============================================================================
# Relatórios - DCAF
RELATORIOS_VERSION=v0.7.99

# Execução - DCAF
EXECUCAO_VERSION=v0.5.27

# Reestimativa - DCAF
REEST_VERSION=v0.2.8

# =============================================================================
# CONFIGURAÇÕES PARA COMANDO DOCKER
# =============================================================================
# Diretório fonte para montagem no container
DOCKER_SRC_DIR := $(CURDIR)

# Prefixo para Windows (winpty)
WINPTY := ''

# Imagem Docker completa
DOCKER_IMAGE_FULL = $(DOCKER_USER)/$(DOCKER_IMAGE):$(DOCKER_TAG)

# Comando para executar container interativo
DOCKER_RUN_CMD = $(shell echo $(WINPTY) docker run --rm -ti -p 8787:8787 --mount type=bind,source=$(DOCKER_SRC_DIR),target=/project --name matriz-fonte-stn-dadosmg $(DOCKER_IMAGE_FULL) bash)
