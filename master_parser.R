library(rmarkdown)
library(plyr)
library(dplyr)

### Generic options for any experiment.
options(
  experiment = "hyperinflation",
  working_path = "C:\\Users\\csn\\Dropbox\\HSW_2015_Documentation\\Hyperinflation\\Pipeline",
  python_prefix = "python", # If the shell needs a command-line prefix to run a Python script, put it here.
  raw_folder = "workingData",
  output_folder = "Results",
  filenames = c("1_1.csv","1_2.csv","1_3.csv","2_1.csv","2_2.csv","2_3.csv"), # These are the results files to be read into the dataset.
  group_labels = c("Demo","Run"), # These are the pool labels whose data will be seperately modeled
  comparison_labels = NA, # This is the label where comparison data will be derived from, if applicable.
  comparison_treatments = NA, # These are the treatment conditions from the comparison data that will be used, if applicable.
  comparison_file = NA # If this exists in the working directory, this file will be loaded and appended on as containing preprocessed comparison data.
)

### Particular options for this experiment.
options(
)

setwd(getOption("working_path"))
source("pipeline.R")

parse_raw() # First, take any raw data that needs to be processed and do so.
read_parsed() # Read processed raw data in.
format_parsed()  # Format the processed raw data.
merge_parsed() # Take the formatted data and merge it with already-processed data, if necessary.
generate_objects() # Take formatted data and generate objects from it for the report.
generate_report() # Generate the report.
