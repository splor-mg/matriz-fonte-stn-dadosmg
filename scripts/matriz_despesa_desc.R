source("scripts/utils.R")

fonte_stn <- data.table::fread("data/fonte_stn.csv")
matriz_despesa <- data.table::fread("data/matriz_despesa.csv")
matriz_despesa <- enrich(matriz_despesa)
matriz_despesa <- matriz_despesa[
  ,
  .(FONTE_STN_COD, FONTE_STN_DESCRICAO, UO_COD, UO_SIGLA, ACAO_COD, ACAO_DESC, GRUPO_COD, FONTE_COD, FONTE_DESC, IPU_COD)
]

writexl::write_xlsx(matriz_despesa, "data/matriz_despesa_desc.xlsx")
