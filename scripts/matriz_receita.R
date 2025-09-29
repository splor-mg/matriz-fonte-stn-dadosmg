library(relatorios)
library(data.table)

receitaAnoAnterior <- fread("datapackages/armazem-siafi-2024/data/receita.csv.gz")
receitaAnoCorrente <- fread("datapackages/armazem-siafi-2025/data/receita.csv.gz")

exec_rec <- rbind(receitaAnoAnterior, receitaAnoCorrente)
names(exec_rec) <- toupper(names(exec_rec))
exec_rec[, FONTE_STN_COD := is_fonte_stn_rec(exec_rec)]

matriz_rec <- exec_rec[,
  .(FONTE_STN_COD, ANO, MES_COD, UO_COD, FONTE_COD, RECEITA_COD)
] 

setorderv(matriz_rec)
matriz_rec <- unique(matriz_rec, 
                     by = c("FONTE_STN_COD", "UO_COD", "FONTE_COD", "RECEITA_COD"))

fwrite(matriz_rec, "data/matriz_receita.csv", sep = ";")
