library(relatorios)
library(data.table)

alteracoes2023 <- fread("datapackages/armazem-siafi-2023/data/alteracoes_orcamentarias.csv.gz")
alteracoes2024 <- fread("datapackages/armazem-siafi-2024/data/alteracoes_orcamentarias.csv.gz")

exec_desp <- rbind(alteracoes2023, alteracoes2024)
names(exec_desp) <- toupper(names(exec_desp))
exec_desp[, FONTE_STN_COD := is_fonte_stn_desp(exec_desp)]

matriz_desp <- exec_desp[,
  .(FONTE_STN_COD, ANO, MES_COD, UO_COD, ACAO_COD, GRUPO_COD, FONTE_COD, IPU_COD)
] 

setorderv(matriz_desp)
matriz_desp <- unique(matriz_desp, 
                      by = c("FONTE_STN_COD", "UO_COD", "ACAO_COD", "GRUPO_COD", 
                             "FONTE_COD", "IPU_COD"))

fwrite(matriz_desp, "data/matriz_despesa.csv", sep = ";")
