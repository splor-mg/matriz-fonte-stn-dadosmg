library(reest)
library(relatorios)
library(data.table)

exec_desp <- ler_exec_rec("data-raw/exec_desp.xlsx")
exec_desp[, FONTE_STN_COD := is_fonte_stn_desp(exec_desp)]

matriz_desp <- exec_desp[,
  .(FONTE_STN_COD, ANO, MES_COD, UO_COD, ACAO_COD, GRUPO_COD, FONTE_COD, IPU_COD)
] 

setorderv(matriz_desp)
matriz_desp <- unique(matriz_desp, 
                      by = c("FONTE_STN_COD", "UO_COD", "ACAO_COD", "GRUPO_COD", 
                             "FONTE_COD", "IPU_COD"))

fwrite(matriz_desp, "data/matriz_despesa.csv", sep = ";")
