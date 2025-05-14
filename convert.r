# Check if 'tidyr' is installed; install if not
if (!requireNamespace("tidyr", quietly = TRUE)) {
  install.packages("tidyr", repos = "https://cloud.r-project.org/")
}

# Load the package
library(tidyr)


file = 'market_info.csv'
csv_sep = ";" # Field separator character in the csv file
 
# Only read the header rows containing the ISIN and the data type:
header = read.csv(file,header=FALSE,skip=1,nrows=2,sep=csv_sep)
instrument = t(header[1,])
datatype = t(header[2,])
# Create column headers for the wide format by combining the datatype and ISIN into one string, e.g. "RI_US5949181045"
col_head = paste(datatype,instrument,sep="_")
col_head[1] = "DATE" # The first column is always the date column
# Read the remaining rows and use col_head as column names:
wide_data = read.csv(file,header=FALSE,skip=4,sep=csv_sep,col.names=col_head,na.strings=c("NA","$$ER: 4540,NO DATA VALUES FOUND","#ERROR",""),dec=",")
 
# Remove columns where the instrument is missing (this takes care of potential "$$ER: E100,INVALID CODE OR EXPRESSION ENTERED" Datastream errors):
is_missing_instrument = is.na(instrument) | instrument == ""
wide_data = wide_data[,!is_missing_instrument]
write.csv(wide_data,"market_hist_data_wide.csv",row.names=FALSE)

print(length(2:ncol(wide_data)))
#print(colnames(wide_data))
# Reshape into long format (panel format) to create one row per date and ISIN
#panel = reshape(wide_data, direction="long", idvar="DATE", varying=2:ncol(wide_data), sep="_", #timevar='INSTRUMENT')
library(dplyr)

panel <- wide_data %>%
  pivot_longer(
    cols = 2:ncol(.),                    # skip the Date column
    names_to = c("Symbol", "ISIN"),      # split col names like "P_0505"
    names_sep = "_",                     # split at underscore
    values_to = "Value"
  ) %>%
  pivot_wider(
    id_cols = c(DATE, ISIN),            # keep Date and ISIN as identifiers
    names_from = Symbol,                # symbols become column names
    values_from = Value                 # fill those with the actual data
  )

rownames(panel) <- NULL
write.csv(panel,"market_hist_data.csv",row.names=FALSE)