source("scripts/utils.R")

fonte_stn <- data.table::fread("data/fonte_stn.csv")
matriz_receita <- data.table::fread("data/matriz_receita.csv")
matriz_receita <- enrich(matriz_receita)
matriz_receita <- matriz_receita[
  ,
  .(FONTE_STN_COD, FONTE_STN_DESCRICAO, UO_COD, UO_SIGLA, FONTE_COD, FONTE_DESC, RECEITA_COD, RECEITA_DESC)
]

writexl::write_xlsx(matriz_receita, "data/matriz_receita_desc.xlsx")
