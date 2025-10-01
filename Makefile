.PHONY: all all-with-build check-image extract transform check publish push session-info config docker-build docker-push extract-info help

include config.mk

all: check-image session-info extract transform check publish

all-with-build: docker-build-push session-info extract transform check publish

extract:
	poetry run dpm install

transform: data/matriz_receita.csv data/matriz_receita_desc.xlsx data/matriz_despesa.csv data/matriz_despesa_desc.xlsx data/fonte_stn.csv

data/matriz_receita.csv: scripts/matriz_receita.R datapackages/armazem-siafi-2024/datapackage.json datapackages/armazem-siafi-2023/datapackage.json
	Rscript $<

data/matriz_despesa.csv: scripts/matriz_despesa.R datapackages/armazem-siafi-2024/datapackage.json datapackages/armazem-siafi-2023/datapackage.json
	Rscript $<

data/fonte_stn.csv: scripts/fonte_stn.R data-raw/fonte_stn.yaml
	Rscript $<

data/matriz_receita_desc.xlsx: scripts/matriz_receita_desc.R data/matriz_receita.csv data/fonte_stn.csv
	Rscript $<

data/matriz_despesa_desc.xlsx: scripts/matriz_despesa_desc.R data/matriz_despesa.csv data/fonte_stn.csv
	Rscript $<

check:
	frictionless validate datapackage.yaml

publish:
	dpckan --datapackage datapackage.yaml dataset update

push:
	git add data/*.csv data/*.xlsx
	git commit --author="Automated <actions@users.noreply.github.com>" -m "Update data package at: $$(date +%Y-%m-%dT%H:%M:%SZ)" || exit 0
	git push

session-info:
	poetry run dpm --version
	Rscript -e "packageVersion('relatorios')"

clean:
	rm -f data/*.csv data/*.xlsx

check-image:
	@echo "🔍 Verificando se imagem Docker existe..."
	@if [ "$$CI" = "true" ]; then \
		echo "✅ Executando no CI - pulando verificação de imagem"; \
	elif ! docker image inspect aidsplormg/$(DOCKER_IMAGE):latest >/dev/null 2>&1; then \
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

# =============================================================================
# CONFIGURAÇÃO E DOCKER
# =============================================================================

config: ## Configura interativamente as variáveis Docker
	@poetry run config

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
