load_source <- function() {
  exp <- getOption("experiment")
  
  if (exp == "Trust") {
    source("trust_formatter.R")
    source("helpers.R")
  }
  
  else if (exp == "IFREE") {
    source("berry_formatter.R")
    source("helpers.R")
  }
  
  else if (exp == "hyperinflation") {
    source("hyperinflation_formatter.R")
    source("helpers.R")
  }
  
  else if (exp == "PG") {
    source("PG_formatter.R")
    source("helpers.R")
  }
}

parse_raw <- function() {
  command <- paste("csn_parser.py",getOption("experiment"),getOption("raw_folder"),getOption("output_folder"), 0)
  if (!is.na(getOption("python_prefix"))) {
    command <- paste(getOption("python_prefix"),command)
  }
  shell(command)
}


read_parsed <- function() {
  filenames <- getOption("filenames")
  df <- data.frame()
  
  ### Special option for taking all .csv files in working data folder.
  if (filenames == "All") { 
    filenames <- list.files(getOption("output_folder"))
    filenames <- filenames[grep(".csv", filenames)]
  }
  
  for (i in seq_along(filenames)) {
    this_name <- filenames[i]
    print(paste0("Reading ", this_name))
    tmp <- read.table(paste(getOption("output_folder"), this_name, sep="\\"), header=T, sep=",")
    df <- rbind.fill(df, tmp)
    
    ### Only take data that will either be used in the comparison group or the main group to be analyzed
    df <- df[df$Pool_Label %in% c(getOption("group_labels"), getOption("comparison_labels")),] 
  }
  
  assign("df_read", df, envir = .GlobalEnv)
}

format_parsed <- function() {
  load_source()
  df <- format(df_read)
  assign("df_formatted", df, envir = .GlobalEnv)
}

merge_parsed <- function() {
  df <- df_formatted
  
  # Read in already-processed data and filter out only the treatment of interest.
  if (!is.na(getOption("comparison_file"))) {
    df.read <- read.table(getOption("comparison_file"),header=T,sep=",")
    if (!is.na(getOption("comparison_treatments"))) {
      df.read <- df.read[df.read$Treatment %in% getOption("comparison_treatments"),]
    }
    df <- rbind.fill(df,df.read)
  }
  
  assign("df_merged", df, envir = .GlobalEnv)
}

generate_objects <- function() {
  load_source()
  make_objects(df_merged)
}

generate_report <- function() {
  exp <- getOption("experiment")
  
  if (exp == "Trust") {
    command <- paste("trust_template_formatter.py",getOption("show_treatment"))
    if (!is.na(getOption("python_prefix"))) {
      command <- paste(getOption("python_prefix"),command)
    }
    shell(command)
    render("trust_template_filled.Rmd")
  }
  
  else if (exp == "IFREE") {
    command <- paste("IFREE_template_formatter.py")
    if (!is.na(getOption("python_prefix"))) {
      command <- paste(getOption("python_prefix"),command)
    }
    shell(command)
    render("IFREE_template_filled.Rmd")
  }
  
  else if (exp == "hyperinflation") {
    command <- paste("hyperinflation_template_formatter.py")
    if (!is.na(getOption("python_prefix"))) {
      command <- paste(getOption("python_prefix"),command)
    }
    shell(command)
    render("hyperinflation_template_filled.Rmd")
  }
  
  else if (exp == "PG") {
    command <- paste("PG_template_formatter.py")
    if (!is.na(getOption("python_prefix"))) {
      command <- paste(getOption("python_prefix"),command)
    }
    shell(command)
    render("PG_template_filled.Rmd")
  }
}