.PHONY: all transform check publish

all: transform check publish

transform: data/matriz_receita.csv data/matriz_receita_desc.xlsx data/matriz_despesa.csv data/matriz_despesa_desc.xlsx data/fonte_stn.csv

data/matriz_receita.csv: scripts/matriz_receita.R data-raw/exec_rec_prev_inicial.xlsx
	Rscript $<

data/matriz_despesa.csv: scripts/matriz_despesa.R data-raw/exec_desp.xlsx
	Rscript $<

data/fonte_stn.csv: scripts/fonte_stn.R data-raw/fonte_stn.yaml
	Rscript $<

data/matriz_receita_desc.xlsx: scripts/matriz_receita_desc.R data/matriz_receita.csv
	Rscript $<

data/matriz_despesa_desc.xlsx: scripts/matriz_despesa_desc.R data/matriz_despesa.csv
	Rscript $<

check:
	frictionless validate datapackage.yaml

publish:
	dpckan --datapackage datapackage.yaml dataset update
