.PHONY: all all-with-build check-image extract transform check publish push session-info session-info-docker config docker-build docker-push extract-info docker help

# Execução via scripts/run.sh centraliza .env, variáveis e docker run
MAKEFLAGS += --no-print-directory
SHELL := /bin/bash

include config.mk


# =============================================================================
# 1) COMANDOS PRINCIPAIS
# =============================================================================

all: deps pacotes-check-version check-image session-info extract transform check publish

all-with-build: deps pacotes-check-version docker-build-push session-info extract transform check publish

# Prepara dependências Python localmente (fail-fast antes de Docker)
deps: ## Verifica e instala dependências Python com Poetry
	@echo "🐍 poetry check"
	@poetry check
	@echo "🐍 poetry install"
	@poetry install --no-interaction --no-ansi --no-root

# =============================================================================
# 2) PROCESSAMENTO DE DADOS
# =============================================================================

extract: ## Baixa e instala datapackages necessários
	@echo "[inside] 🔍 Executando extract..."
	@bash scripts/run.sh "dpm install"

transform: data/matriz_receita.csv data/matriz_receita_desc.xlsx data/matriz_despesa.csv data/matriz_despesa_desc.xlsx data/fonte_stn.csv ## Processa dados e gera arquivos de saída

data/matriz_receita.csv: scripts/matriz_receita.R | extract
	@echo "[inside] ▶ Rscript $<"
	@bash scripts/run.sh "Rscript $<"

data/matriz_despesa.csv: scripts/matriz_despesa.R | extract
	@echo "[inside] ▶ Rscript $<"
	@bash scripts/run.sh "Rscript $<"

data/fonte_stn.csv: scripts/fonte_stn.R data-raw/fonte_stn.yaml | extract
	@echo "[inside] ▶ Rscript $<"
	@bash scripts/run.sh "Rscript $<"

data/matriz_receita_desc.xlsx: scripts/matriz_receita_desc.R data/matriz_receita.csv data/fonte_stn.csv | extract
	@echo "[inside] ▶ Rscript $<"
	@bash scripts/run.sh "Rscript $<"

data/matriz_despesa_desc.xlsx: scripts/matriz_despesa_desc.R data/matriz_despesa.csv data/fonte_stn.csv | extract
	@echo "[inside] ▶ Rscript $<"
	@bash scripts/run.sh "Rscript $<"

# =============================================================================
# 3) VALIDAÇÃO E PUBLICAÇÃO
# =============================================================================

check: ## Valida saídas com Frictionless (ignora colunas extras nas fontes)
	@echo "[inside] ✅ frictionless validate (arquivos gerados)"
	@bash scripts/run.sh "poetry run frictionless validate data/matriz_receita.csv"
	@bash scripts/run.sh "poetry run frictionless validate data/matriz_despesa.csv"
	@bash scripts/run.sh "poetry run frictionless validate data/matriz_receita_desc.xlsx"
	@bash scripts/run.sh "poetry run frictionless validate data/matriz_despesa_desc.xlsx"
	@bash scripts/run.sh "poetry run frictionless validate data/fonte_stn.csv"

publish: ## Publica dados no CKAN
	@echo "[inside] 🚀 publish-ckan"
	@bash scripts/run.sh "poetry run publish-ckan --datapackage datapackage.yaml"

push: ## Commita e envia dados processados para o repositório
	git add data/*.csv data/*.xlsx
	git commit --author="Automated <actions@users.noreply.github.com>" -m "Update data package at: $$(date +%Y-%m-%dT%H:%M:%SZ)" || exit 0
	git push

# =============================================================================
# 4) UTILITÁRIOS E INFORMAÇÕES
# =============================================================================

session-info: ## Mostra informações da sessão (versões dos pacotes)
	@echo "[inside] ℹ️  session-info"
	@bash scripts/run.sh "poetry run dpm --version && Rscript -e \"packageVersion('relatorios')\""

session-info-docker: ## Executa session-info dentro do Docker
	@echo "[inside] ℹ️  session-info"
	@bash scripts/run.sh "poetry run dpm --version && Rscript -e \"packageVersion('relatorios')\""

# Alvo genérico: rodar qualquer alvo dentro do container
inside/%:
	@echo "[inside] make $*"
	@bash scripts/run.sh "make $*"

clean: ## Remove arquivos de dados processados
	rm -f data/*.csv data/*.xlsx

# =============================================================================
# 5) DOCKER E CONFIGURAÇÃO
# =============================================================================

check-image: ## Verifica se a imagem Docker existe localmente
	@echo "🔍 Verificando se imagem Docker existe..."
# Teste se exuta no Actions, se não, verifica se existe localmente
	@if [ "$$CI" = "true" ]; then \
		echo "✅ Executando no CI - pulando verificação de imagem"; \
	elif ! docker image inspect aidsplormg/$(DOCKER_IMAGE):$(DOCKER_TAG) >/dev/null 2>&1; then \
		echo "❌ Imagem Docker não encontrada localmente"; \
		echo "Construir e publicar imagem agora? (y/N)"; \
		read -r response; \
		if [ "$$response" = "y" ] || [ "$$response" = "Y" ]; then \
			echo "🔨 Construindo e publicando imagem..."; \
			$(MAKE) docker-build-push; \
		else \
			echo "⚠️  Continuando sem imagem Docker (pode falhar)"; \
		fi; \
	else \
		echo "✅ Imagem Docker encontrada localmente"; \
		echo "Atualizar imagem (rebuild + push)? (y/N)"; \
		read -r response; \
		if [ "$$response" = "y" ] || [ "$$response" = "Y" ]; then \
			echo "🔨 Atualizando imagem..."; \
			$(MAKE) docker-build-push; \
		else \
			echo "✅ Usando imagem existente"; \
		fi; \
	fi

config: ## Configura interativamente as variáveis Docker
	@poetry run config

docker: check-image ## Cria um container interativo para desenvolvimento e processamento de dados
	@if [ TRUE ]; then \
		$(DOCKER_RUN_CMD) -c "poetry install --no-interaction --no-ansi --no-root && bash"; \
	fi

docker-build: ## Constrói a imagem Docker
	@poetry run docker-build

docker-push: ## Envia a imagem Docker para o Docker Hub
	@poetry run docker-push

docker-build-push: ## Constrói e envia a imagem Docker para o Docker Hub
	@echo "🔨 Construindo imagem Docker..."
	@poetry run docker-build
	@echo "📤 Enviando imagem para Docker Hub..."
	@poetry run docker-push
	@echo "✅ Build e push concluídos com sucesso!"

extract-info: ## Extrai informações de versões da imagem Docker
	@poetry run extract-info

pacotes-check-version: ## Verifica e atualiza versões dos pacotes DCAF no GitHub
	@poetry run pacotes-check-version || true

update-ano: ## Atualiza anos nos arquivos do projeto (config.mk e scripts R)
	@poetry run update-ano

help: ## Mostra comandos disponíveis
	@echo "Comandos disponíveis:"; \
	awk 'BEGIN { FS=":.*?## " } \
	/^[ \t]*# [0-9]+\) / { sec=$$0; gsub(/^[ \t]*# /, "", sec); next } \
	/^[a-zA-Z0-9_-]+:.*## .*$$/ { \
	  if (sec == "") sec="Outros"; \
	  if (!printed[sec]) { printf "\n\033[1m%s\033[0m\n", sec; printed[sec]=1 } \
	  printf "\033[36m%-22s\033[0m %s\n", $$1, $$2 \
	}' Makefile
