.PHONY: all all-with-build check-image extract transform check publish push session-info session-info-docker config docker-build docker-push extract-info docker help

include config.mk

# Wrapper para executar comandos dentro do container
DOCKER_ENV_FILE :=
ifneq (,$(wildcard .env))
DOCKER_ENV_FILE := --env-file .env
endif

DOCKER_RUN = docker run --rm $(DOCKER_ENV_FILE) \
	-e GITHUB_TOKEN="$(GITHUB_TOKEN)" \
	-e CKAN_HOST="$(CKAN_HOST)" \
	-e CKAN_KEY="$(CKAN_KEY)" \
	-v $(PWD):/project \
	$(DOCKER_USER)/$(DOCKER_IMAGE):$(DOCKER_TAG) \
	bash -lc

# =============================================================================
# 1) COMANDOS PRINCIPAIS
# =============================================================================

all: check-image session-info extract transform check publish

all-with-build: docker-build-push session-info extract transform check publish

# =============================================================================
# 2) PROCESSAMENTO DE DADOS
# =============================================================================

extract: ## Baixa e instala datapackages necessários
	@echo "[inside] 🔍 Executando extract dentro do Docker..."
	@$(DOCKER_RUN) "poetry run dpm install"

transform: data/matriz_receita.csv data/matriz_receita_desc.xlsx data/matriz_despesa.csv data/matriz_despesa_desc.xlsx data/fonte_stn.csv ## Processa dados e gera arquivos de saída

data/matriz_receita.csv: scripts/matriz_receita.R datapackages/armazem-siafi-2024/datapackage.json datapackages/armazem-siafi-2025/datapackage.json
	@echo "[inside] ▶ Rscript $<"
	@$(DOCKER_RUN) "Rscript $<"

data/matriz_despesa.csv: scripts/matriz_despesa.R datapackages/armazem-siafi-2024/datapackage.json datapackages/armazem-siafi-2025/datapackage.json
	@echo "[inside] ▶ Rscript $<"
	@$(DOCKER_RUN) "Rscript $<"

data/fonte_stn.csv: scripts/fonte_stn.R data-raw/fonte_stn.yaml
	@echo "[inside] ▶ Rscript $<"
	@$(DOCKER_RUN) "Rscript $<"

data/matriz_receita_desc.xlsx: scripts/matriz_receita_desc.R data/matriz_receita.csv data/fonte_stn.csv
	@echo "[inside] ▶ Rscript $<"
	@$(DOCKER_RUN) "Rscript $<"

data/matriz_despesa_desc.xlsx: scripts/matriz_despesa_desc.R data/matriz_despesa.csv data/fonte_stn.csv
	@echo "[inside] ▶ Rscript $<"
	@$(DOCKER_RUN) "Rscript $<"

# =============================================================================
# 3) VALIDAÇÃO E PUBLICAÇÃO
# =============================================================================

check: ## Valida datapackage.yaml com frictionless
	@echo "[inside] ✅ frictionless validate"
	@$(DOCKER_RUN) "poetry run frictionless validate datapackage.yaml"

publish: ## Publica dados no CKAN
	@echo "[inside] 🚀 publish-ckan"
	@$(DOCKER_RUN) "poetry run publish-ckan --datapackage datapackage.yaml"

push: ## Commita e envia dados processados para o repositório
	git add data/*.csv data/*.xlsx
	git commit --author="Automated <actions@users.noreply.github.com>" -m "Update data package at: $$(date +%Y-%m-%dT%H:%M:%SZ)" || exit 0
	git push

# =============================================================================
# 4) UTILITÁRIOS E INFORMAÇÕES
# =============================================================================

session-info: ## Mostra informações da sessão (versões dos pacotes)
	@echo "[inside] ℹ️  session-info"
	@$(DOCKER_RUN) "poetry run dpm --version && Rscript -e \"packageVersion('relatorios')\""

session-info-docker: ## Executa session-info dentro do Docker
	@echo "[inside] ℹ️  session-info"
	@$(DOCKER_RUN) "poetry run dpm --version && Rscript -e \"packageVersion('relatorios')\""

# Alvo genérico: rodar qualquer alvo dentro do container
inside/%:
	@echo "[inside] make $*"
	@$(DOCKER_RUN) "make $*"

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
		$(DOCKER_RUN_CMD) -c "poetry install && bash"; \
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
	@poetry run pacotes-check-version

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
