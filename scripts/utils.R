library(data.table)
library(relatorios)

make_day <- function(year, month) {
  month <- formatC(month, width = 2, flag = "0")
  day <- paste(year, month, "01", sep = "-")
  as.Date(day)
}

enrich <- function(data) {
  data <- data.table::copy(data)
  data[, DATA_REF := make_day(ANO, MES_COD)]
  data <- fonte_stn[
    data, 
    on = .(FONTE_STN_COD, DT_INICIO_VIGENCIA <= DATA_REF, DT_FIM_VIGENCIA > DATA_REF)
  ]
  data <- relatorios::adiciona_desc(data)
  data
}
