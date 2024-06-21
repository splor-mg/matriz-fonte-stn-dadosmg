library(data.table)

matriz_receita <- fread("data/matriz_receita.csv")
matriz_receita[, N := .N, .(UO_COD, FONTE_COD, RECEITA_COD)]
matriz_receita[N > 1]


matriz_despesa <- fread("data/matriz_despesa.csv")
matriz_despesa[, N := .N, .(UO_COD, ACAO_COD, GRUPO_COD, FONTE_COD, IPU_COD)]
matriz_despesa[N > 1]
