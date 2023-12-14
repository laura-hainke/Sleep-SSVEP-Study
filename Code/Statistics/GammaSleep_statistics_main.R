# Author: LH
# Date: 2023-09-21
# Functionality: Load derivative participant data, generate plots, run statistical analysis
# Notes: 



# Environment Setup ----------------------------------------------------------------------------------------------------

# Working directory
setwd("C:\\Users\\Mitarbeiter\\Documents\\Gamma_Sleep\\Code\\Statistics")

# Function files in current directory
source("GammaSleep_statistics_functions.r")
source("GammaSleep_plots_functions.r")
source("GammaSleep_data-handling_functions.R")

# Libraries
library("pastecs")


## Global variables
# Using global environment (<<- assignment) to avoid redundant function arguments

# Path to folders with derivative data
path_derivatives <<- "C:\\Users\\Mitarbeiter\\Documents\\Gamma_Sleep\\Data\\Derivatives\\" 

# List of folder names in directory, corresponding to participant numbers
list_IDs <<- list.dirs(path = path_derivatives, full.names = FALSE, recursive = FALSE)

# Remove rejected datasets (& for debugging, datasets not yet collected)
list_IDs <<- list_IDs[-c(3,15,26:27,31:32)] 



# Dataframes for derivative data ---------------------------------------------------

## Initializing 
data_demo <<- initialize_dataframe("demographic")

data_sleep <<- initialize_dataframe("sleep_quality")

data_PSD <<- initialize_dataframe("PSD_metrics")
                        
data_SSVEP <<- initialize_dataframe("SSVEP_metrics")

## Loading data
load_derivative_data()



# Descriptives ------------------------------------------------------------

# Sample characteristics
stat.desc(data_demo$age)
stat.desc(data_demo$sex)
stat.desc(data_demo$gender_match)
stat.desc(data_demo$handedness)
stat.desc(data_demo$education)
stat.desc(data_demo$PSQI_score)
stat.desc(data_demo$uMCTQ_score) # not working yet



# Power Spectral Density (power in dB) ------------------------------------------------------

# Conversion to long format
data_PSD_dB_long = dataframe_wide_to_long(data_PSD[,c("ID","W_PSD40_con","N2_PSD40_con","N3_PSD40_con","REM_PSD40_con","W_PSD40_exp","N2_PSD40_exp","N3_PSD40_exp","REM_PSD40_exp")])

# Boxplots
plot_box_2X4(data=data_PSD_dB_long, title_plot="40 Hz Spectral Power", title_y="Power (dB)", ymin=-100, ymax=-150)

# Connected scatterplot
plot_scatter_2X4(data=data_PSD_dB_long, title_plot="40 Hz Spectral Power", title_y="Power (dB)", ymin=-100, ymax=-150)



# Power Spectral Density (SNR) ------------------------------------------------------

# Conversion to long format
data_PSD_SNR_long = dataframe_wide_to_long(data_PSD[,c("ID","W_SNR40_con","N2_SNR40_con","N3_SNR40_con","REM_SNR40_con","W_SNR40_exp","N2_SNR40_exp","N3_SNR40_exp","REM_SNR40_exp")])

# Boxplots
plot_box_2X4(data=data_PSD_SNR_long, title_plot="Signal-to-Noise Ratio of 40 Hz Power", title_y="SNR", ymin=0, ymax=85)

# Connected scatterplot
plot_scatter_2X4(data=data_PSD_SNR_long, title_plot="Signal-to-Noise Ratio of 40 Hz Power", title_y="SNR", ymin=0, ymax=85)



# Steady-State Visually Evoked Potentials (amplitude in uV) ------------------------------------------------------

# Conversion to long format
data_SSVEP_uV_long = dataframe_wide_to_long(data_SSVEP[,c("ID","W_PTA_con","N2_PTA_con","N3_PTA_con","REM_PTA_con","W_PTA_exp","N2_PTA_exp","N3_PTA_exp","REM_PTA_exp")])

# Boxplots
plot_box_2X4(data=data_SSVEP_uV_long, title_plot="SSVEP Peak-to-Trough Amplitude", title_y="Amplitude (uV)", ymin=0, ymax=2.3)

# Connected scatterplot
plot_scatter_2X4(data=data_SSVEP_uV_long, title_plot="SSVEP Peak-to-Trough Amplitude", title_y="Amplitude (uV)", ymin=0, ymax=2.3)



# Steady-State Visually Evoked Potentials (SNR)

# Conversion to long format
data_SSVEP_SNR_long = dataframe_wide_to_long(data_SSVEP[,c("ID","W_SNR_con","N2_SNR_con","N3_SNR_con","REM_SNR_con","W_SNR_exp","N2_SNR_exp","N3_SNR_exp","REM_SNR_exp")])

# Boxplots
plot_box_2X4(data=data_SSVEP_SNR_long, title_plot="Signal-to-Noise Ratio of SSVEP", title_y="SNR", ymin=0, ymax=45)

# Connected scatterplot: SSVEP SNR
plot_scatter_2X4(data=data_SSVEP_SNR_long, title_plot="Signal-to-Noise Ratio of SSVEP", title_y="SNR", ymin=0, ymax=45)



# GSQS ----------------------------------------------------------

# Conversion to long format
data_GSQS_long = dataframe_wide_to_long(data_sleep[,c("ID","GSQS_con","GSQS_exp")])

# Plot
plot_violin_paired(data=data_GSQS_long, title_plot="Subjective Sleep Quality", title_y="GSQS Sum Score")


# TST ----------------------------------------------------------

# Conversion to long format
data_TST_long = dataframe_wide_to_long(data_sleep[,c("ID","TST_con","TST_exp")])

# Plot
plot_violin_paired(data=data_TST_long, title_plot="Total Sleep Time", title_y="TST (min)")



# WASO ----------------------------------------------------------

# Conversion to long format
data_WASO_long = dataframe_wide_to_long(data_sleep[,c("ID","WASO_con","WASO_exp")])

# Plot
plot_violin_paired(data=data_WASO_long, title_plot="Wake After Sleep Onset", title_y="WASO (min)")



# SOL -----------------------------------------------------------------------------------------------------------------------

# Conversion to long format
data_SOL_long = dataframe_wide_to_long(data_sleep[,c("ID","SOL_con","SOL_exp")])

# Plot
plot_violin_paired(data=data_SOL_long, title_plot="Sleep Onset Latency", title_y="SOL (min)")



# % of time per stage --------------------------------------------------------

# Stacked bar graph of % time per stage
plot_bar_stack(data_sleep[,c("ID","perN1_con","perN2_con","perN3_con","perREM_con","perN1_exp","perN2_exp","perN3_exp","perREM_exp")])





