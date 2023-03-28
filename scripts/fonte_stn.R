library(data.table)
library(readxl)

fonte_stn <- read_excel("data-raw/fonte_stn.xlsx")
readr::write_excel_csv2(fonte_stn, "data/fonte_stn.csv", quote = "needed")
