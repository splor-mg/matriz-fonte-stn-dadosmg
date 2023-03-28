.PHONY: transform

transform: data/matriz_receita.csv data/matriz_despesa.csv data/fonte_stn.csv

data/matriz_receita.csv: scripts/matriz_receita.R data-raw/exec_rec_prev_inicial.xlsx
	Rscript $<

data/matriz_despesa.csv: scripts/matriz_despesa.R data-raw/exec_desp.xlsx
	Rscript $<

data/fonte_stn.csv: scripts/fonte_stn.R data-raw/fonte_stn.xlsx
	Rscript $<
