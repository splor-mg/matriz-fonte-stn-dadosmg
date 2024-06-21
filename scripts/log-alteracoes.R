library(data.table)
library(dplyr)
library(writexl)

old_rec <- fread("https://raw.githubusercontent.com/splor-mg/matriz-fonte-stn-dadosmg/e920183d65644b248c8bce1445d072f6ab12ce33/data/matriz_receita.csv")
new_rec <- fread("https://raw.githubusercontent.com/splor-mg/matriz-fonte-stn-dadosmg/main/data/matriz_receita.csv")
write_xlsx(anti_join(new_rec, old_rec), "alteracoes_matriz_receita.xlsx")


old_desp <- fread("https://raw.githubusercontent.com/splor-mg/matriz-fonte-stn-dadosmg/e920183d65644b248c8bce1445d072f6ab12ce33/data/matriz_despesa.csv")
new_desp <- fread("https://raw.githubusercontent.com/splor-mg/matriz-fonte-stn-dadosmg/main/data/matriz_despesa.csv")
write_xlsx(anti_join(new_desp, old_desp), "alteracoes_matriz_despesa.xlsx")
