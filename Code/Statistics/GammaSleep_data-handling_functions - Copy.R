# Author: LH
# Date: 2023-12-14
# Functionality: Functions for statistics_main.R, for importing and formatting data
# Notes:



# Environment Setup ----------------------------------------------------------------------------------------------------

library(reshape2)
library(tidyr)
library(dplyr)



# Function: initialize_dataframe -------------------------------------------------------------------------------------------
# Initialize a dataframe for a given set of variables.

## INPUT

# df_type : str
# Type of dataframe to be created

## OUTPUT

# custom_dataframe : dataframe
# Empty dataframe with columns matching the specified data types

initialize_dataframe <- function(df_type = c("demographic","sleep_quality","PSD_metrics","SSVEP_metrics")) {
  
  # Get number of participants
  n_IDs = length(list_IDs)
  
  # Create a custom dataframe depending on the variable type
  if (df_type ==  "demographic") {
    custom_dataframe = data.frame(ID = as.factor(list_IDs), # Participant numbers
                                  age = rep(NA, n_IDs),
                                  sex = rep(NA, n_IDs),
                                  gender_match = rep(NA, n_IDs),
                                  handedness = rep(NA, n_IDs),
                                  education = rep(NA, n_IDs),
                                  uMCTQ_score = rep(NA, n_IDs),
                                  PSQI_score = rep(NA, n_IDs))
  } 
  else if (df_type == "sleep_quality") {
    custom_dataframe = data.frame(ID = as.factor(list_IDs), 
                                  # PSG metrics, condition CON 
                                  SOL_con = rep(NA, n_IDs), # Sleep Onset Latency
                                  TST_con = rep(NA, n_IDs), # Total Sleep Time
                                  WASO_con = rep(NA, n_IDs), # Wake After Sleep Onset 
                                  # Time per stage as % of TST, condition CON
                                  perN1_con = rep(NA, n_IDs), # N1
                                  perN2_con = rep(NA, n_IDs), # N2
                                  perN3_con = rep(NA, n_IDs), # N3
                                  perREM_con = rep(NA, n_IDs), # REM
                                  # Subjective sleep quality, condition CON
                                  GSQS_con = rep(NA, n_IDs), # Groeningen Sleep Quality Scale sum score
                                  # PSG metrics, condition EXP 
                                  SOL_exp = rep(NA, n_IDs), 
                                  TST_exp = rep(NA, n_IDs),
                                  WASO_exp = rep(NA, n_IDs),
                                  # Time per stage as % of TST, condition EXP
                                  perN1_exp = rep(NA, n_IDs),
                                  perN2_exp = rep(NA, n_IDs),
                                  perN3_exp = rep(NA, n_IDs),
                                  perREM_exp = rep(NA, n_IDs),
                                  # Subjective sleep quality, condition EXP
                                  GSQS_exp = rep(NA, n_IDs))
  } 
  else if (df_type == "PSD_metrics") {
    custom_dataframe = data.frame(ID = as.factor(list_IDs), 
                                  # Stage W, condition CON
                                  W_nepochs_con = rep(NA, n_IDs), # Nr. of 30 s epochs included in analysis
                                  W_PSD40_con = rep(NA, n_IDs), # PSD value at 40 Hz
                                  W_SNR40_con = rep(NA, n_IDs), # SNR value at 40 Hz
                                  # Stage N2, condition CON
                                  N2_nepochs_con = rep(NA, n_IDs),
                                  N2_PSD40_con = rep(NA, n_IDs),
                                  N2_SNR40_con = rep(NA, n_IDs),
                                  # Stage N3, condition CON
                                  N3_nepochs_con = rep(NA, n_IDs),
                                  N3_PSD40_con = rep(NA, n_IDs),
                                  N3_SNR40_con = rep(NA, n_IDs),
                                  # Stage REM, condition CON
                                  REM_nepochs_con = rep(NA, n_IDs),
                                  REM_PSD40_con = rep(NA, n_IDs),
                                  REM_SNR40_con = rep(NA, n_IDs),
                                  # Stage W, condition EXP
                                  W_nepochs_exp = rep(NA, n_IDs),
                                  W_PSD40_exp = rep(NA, n_IDs),
                                  W_SNR40_exp = rep(NA, n_IDs),
                                  # Stage N2, condition EXP
                                  N2_nepochs_exp = rep(NA, n_IDs),
                                  N2_PSD40_exp = rep(NA, n_IDs),
                                  N2_SNR40_exp = rep(NA, n_IDs),
                                  # Stage N3, condition EXP
                                  N3_nepochs_exp = rep(NA, n_IDs),
                                  N3_PSD40_exp = rep(NA, n_IDs),
                                  N3_SNR40_exp = rep(NA, n_IDs),
                                  # Stage REM, condition EXP
                                  REM_nepochs_exp = rep(NA, n_IDs),
                                  REM_PSD40_exp = rep(NA, n_IDs),
                                  REM_SNR40_exp = rep(NA, n_IDs))
  } 
  else if (df_type == "SSVEP_metrics") {
    custom_dataframe = data.frame(ID = as.factor(list_IDs), 
                                  # Stage W, condition CON
                                  W_nsegments_con = rep(NA, n_IDs), # Nr. of 25 ms segments included in analysis
                                  W_PTA_con = rep(NA, n_IDs), # Peak-to-trough amplitude of SSVEP
                                  W_SNR_con = rep(NA, n_IDs), # SNR value of SSVEP
                                  # Stage N2, condition CON
                                  N2_nsegments_con = rep(NA, n_IDs),
                                  N2_PTA_con = rep(NA, n_IDs),
                                  N2_SNR_con = rep(NA, n_IDs),
                                  # Stage N3, condition CON
                                  N3_nsegments_con = rep(NA, n_IDs),
                                  N3_PTA_con = rep(NA, n_IDs),
                                  N3_SNR_con = rep(NA, n_IDs),
                                  # Stage REM, condition CON
                                  REM_nsegments_con = rep(NA, n_IDs),
                                  REM_PTA_con = rep(NA, n_IDs),
                                  REM_SNR_con = rep(NA, n_IDs),
                                  # Stage W, condition EXP
                                  W_nsegments_exp = rep(NA, n_IDs),
                                  W_PTA_exp = rep(NA, n_IDs),
                                  W_SNR_exp = rep(NA, n_IDs),
                                  # Stage N2, condition EXP
                                  N2_nsegments_exp = rep(NA, n_IDs),
                                  N2_PTA_exp = rep(NA, n_IDs),
                                  N2_SNR_exp = rep(NA, n_IDs),
                                  # Stage N3, condition EXP
                                  N3_nsegments_exp = rep(NA, n_IDs),
                                  N3_PTA_exp = rep(NA, n_IDs),
                                  N3_SNR_exp = rep(NA, n_IDs),
                                  # Stage REM, condition EXP
                                  REM_nsegments_exp = rep(NA, n_IDs),
                                  REM_PTA_exp = rep(NA, n_IDs),
                                  REM_SNR_exp = rep(NA, n_IDs))
  }
  
  return(custom_dataframe)
}



# Function: load_derivative_data -------------------------------------------------------------------------------------------
# Load all derivative participant data into dataframes created in initialize_dataframe()

## INPUT

# none (only global variables)

## OUTPUT

# Updated global dataframes: data_demo, data_sleep, data_PSD, data_SSVEP

load_derivative_data <- function() {
  
  # Subfolders & substrings of the filenames to be imported
  filename_substrings = data.frame(subfolder=c("\\REDCap\\","\\Control\\","\\Experimental\\","\\Control\\","\\Experimental\\","\\Control\\","\\Experimental\\"), file_name=c("_personal-data.csv","_control_sleep-data.csv","_experimental_sleep-data.csv","_control_PSD-output-metrics.csv","_experimental_PSD-output-metrics.csv","_control_SSVEP-output-metrics.csv","_experimental_SSVEP-output-metrics.csv"))
  
  # Loop over all subjects
  for (i in list_IDs) { 
    
    # Loop over all CSV files to be imported
    for (j in 1:nrow(filename_substrings)) {
      
      # Get filename
      filename = paste(path_derivatives, i, filename_substrings$subfolder[j], i, filename_substrings$file_name[j], sep = "")
      
      # Read CSV file
      data_csv = read.csv(filename, header=FALSE)
      
      # Write data to corresponding dataframe
      if (filename_substrings$file_name[j] == "_personal-data.csv") { 
        data_demo[data_demo$ID == i,2:6] <<- data_csv[2,1:5] # Segmenting import to skip variable time_lab_arrival, not relevant for analyses
        data_demo[data_demo$ID == i,7:8] <<- data_csv[2,7:8]
      } else if (filename_substrings$file_name[j] == "_control_sleep-data.csv") {
        data_sleep[data_sleep$ID == i,2:9] <<- data_csv[,2]
      } else if (filename_substrings$file_name[j] == "_experimental_sleep-data.csv") {
        data_sleep[data_sleep$ID == i,10:17] <<- data_csv[,2]
      } else if (filename_substrings$file_name[j] == "_control_PSD-output-metrics.csv") {
        data_PSD[data_PSD$ID == i,2:13] <<- data_csv[,2]
      } else if (filename_substrings$file_name[j] == "_experimental_PSD-output-metrics.csv") {
        data_PSD[data_PSD$ID == i,14:25] <<- data_csv[,2]
      } else if (filename_substrings$file_name[j] == "_control_SSVEP-output-metrics.csv") {
        data_SSVEP[data_SSVEP$ID == i,2:13] <<- data_csv[,2]
      } else if (filename_substrings$file_name[j] == "_experimental_SSVEP-output-metrics.csv") {
        data_SSVEP[data_SSVEP$ID == i,14:25] <<- data_csv[,2]
      }
    }
  }
  
  # Convert demographic data into numeric format
  data_demo <<- data_demo %>% mutate_at(c("age","sex","gender_match","handedness","education","PSQI_score"), as.numeric)
  
}



# Function: dataframe_wide_to_long ------------------------------------------------------------------------------------------
# Convert a wide dataframe with 2 factors into long format.

## INPUT

# data_wide : dataframe
# Original dataframe in wide formatW

## OUTPUT

# data_long2 : dataframe
# Dataframe converted into long format

dataframe_wide_to_long <- function(data_wide) {
  
  # Infer number of factors from number of underscores in variable name
  n_factors = str_count(colnames(data_wide[2]), "_")
  
  # Apply first conversion step
  data_long1 = melt(data_wide, id.vars="ID", variable.name="condition", value.name="value")
  
  # Column "stage" only for more than 1 factor
  if (n_factors > 1) { 
    colnames = c("stage","variable","condition")
  } else {
    colnames = c("variable","condition")
  }
  
  # Apply second conversion step
  data_long2 = separate_wider_delim(data_long1, cols = condition, delim = "_", names = colnames)
  
  # Set all columns as factors except for value
  data_long2[,c(1:length(colnames)+1)] = lapply(data_long2[,c(1:length(colnames)+1)], as.factor)
  
  # Output 
  return(data_long2)
  
}



# Function: import_SSVEPs_to_long_dataframe -------------------------------------------------------------------------------------------
# Import CSV files with SSVEP data for all participants, put into a dataframe in long format for plots.

## INPUT

# none (only global variables)

## OUTPUT

# data_SSVEPs_group : dataframe
# Dataframe in long format including all participants' SSVEP time series data

import_SSVEPs_to_long_dataframe <- function() { 
  
  # Number of datapoints of SSVEP with 25 ms period, at 1 kHz sampling rate
  nr_datapoints_SSVEP = 25
  
  # Initialize dataframe to import CSV data for one participant
  data_SSVEPs_individual = data.frame(ID = character(nr_datapoints_SSVEP),
                                      time = seq(1,nr_datapoints_SSVEP),
                                      W_con = numeric(nr_datapoints_SSVEP),
                                      N2_con = numeric(nr_datapoints_SSVEP),
                                      N3_con = numeric(nr_datapoints_SSVEP),
                                      REM_con = numeric(nr_datapoints_SSVEP),
                                      W_exp = numeric(nr_datapoints_SSVEP),
                                      N2_exp = numeric(nr_datapoints_SSVEP),
                                      N3_exp = numeric(nr_datapoints_SSVEP),
                                      REM_exp = numeric(nr_datapoints_SSVEP))
  
  # Length of final data frame
  nr_conditions = 2
  nr_stages = 4
  length_dataframe_group = length(list_IDs) * nr_datapoints_SSVEP * nr_conditions * nr_stages
  
  # Initialize dataframe in long format, to store all participants' data
  data_SSVEPs_group = data.frame(ID = character(length_dataframe_group),
                                 time = numeric(length_dataframe_group),
                                 stage = character(length_dataframe_group),
                                 condition = character(length_dataframe_group),
                                 value = numeric(length_dataframe_group))
  
  # Loop over all subjects
  for (i in c(1:length(list_IDs))) { 
    
    # Import data for individual participant, load into dataframe
    filename_con = paste(path_derivatives, list_IDs[i], "\\Control\\", list_IDs[i], "_control_SSVEP-output-curves.csv", sep = "")
    filename_exp = paste(path_derivatives, list_IDs[i], "\\Experimental\\", list_IDs[i], "_experimental_SSVEP-output-curves.csv", sep = "")
    
    data_con = read.csv(filename_con, header=TRUE)
    data_exp = read.csv(filename_exp, header=TRUE)
    
    data_SSVEPs_individual$ID = list_IDs[i]               
    data_SSVEPs_individual[,3:6] = data_con[2:5]                 
    data_SSVEPs_individual[,7:10] = data_exp[2:5]                 
    
    # Convert dataframe to long format
    data_individual_long = melt(data_SSVEPs_individual, id.vars=c("ID","time"), variable.name="condition", value.name="value")
    data_individual_long = separate_wider_delim(data_individual_long, cols = condition, delim = "_", names = c("stage","condition"))                 
    
    # Fill group dataframe with individual data
    idx_end = nrow(data_individual_long) * i
    idx_start = idx_end - nrow(data_individual_long) + 1
    data_SSVEPs_group[idx_start:idx_end,] = data_individual_long
  }        
  
  return(data_SSVEPs_group)
}



