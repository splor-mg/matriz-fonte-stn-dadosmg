library(data.table)
library(yaml)

fonte_stn <- yaml.load_file("data-raw/fonte_stn.yaml") |> rbindlist()
names(fonte_stn) <- toupper(names(fonte_stn))
fonte_stn[, FONTE_STN_DESCRICAO := toupper(FONTE_STN_DESCRICAO)]
readr::write_excel_csv2(fonte_stn, "data/fonte_stn.csv", quote = "needed")
