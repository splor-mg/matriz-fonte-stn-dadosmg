library(reest)
library(relatorios)
library(data.table)

exec_rec <- ler_exec_rec("data-raw/exec_rec_prev_inicial.xlsx")
exec_rec[, FONTE_STN_COD := is_fonte_stn_rec(exec_rec)]

matriz_rec <- exec_rec[,
  .(FONTE_STN_COD, ANO, MES_COD, UO_COD, FONTE_COD, RECEITA_COD)
] 

setorderv(matriz_rec)
matriz_rec <- unique(matriz_rec, 
                     by = c("FONTE_STN_COD", "UO_COD", "FONTE_COD", "RECEITA_COD"))

fwrite(matriz_rec, "data/matriz_receita.csv", sep = ";")
