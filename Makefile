.PHONY: all extract transform check publish sync session-info

all: session-info extract transform check publish

extract:
	dpm install

transform: data/matriz_receita.csv data/matriz_receita_desc.xlsx data/matriz_despesa.csv data/matriz_despesa_desc.xlsx data/fonte_stn.csv

data/matriz_receita.csv: scripts/matriz_receita.R datapackages/**/datapackage.json
	Rscript $<

data/matriz_despesa.csv: scripts/matriz_despesa.R datapackages/**/datapackage.json
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

sync:
	git add data/*.csv data/*.xlsx
	git commit --author="Automated <actions@users.noreply.github.com>" -m "Update data package at: $$(date +%Y-%m-%dT%H:%M:%SZ)" || exit 0

session-info:
	dpm --version
	Rscript -e "packageVersion('relatorios')"

clean:
	rm -f data/*.csv data/*.xlsx
