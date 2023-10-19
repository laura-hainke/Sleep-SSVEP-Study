# Author: LH
# Date: 2023-09-21
# Functionality: Load derivative participant data, run statistical analysis
# Notes:



# Environment Setup ----------------------------------------------------------------------------------------------------

# Working directory
setwd("C:\\Users\\Mitarbeiter\\Documents\\Gamma_Sleep\\Code\\Statistics")

# Source functions, files in current directory
source("Statistics_functions.r")
source("Plots_functions.r")


# Libraries
library("pastecs")

# Path to folders with derivative data
path_derivatives = "C:\\Users\\Mitarbeiter\\Documents\\Gamma_Sleep\\Data\\Derivatives\\"

# List of folder names in directory, corresponding to participant numbers
list_IDs = list.dirs(path = path_derivatives, full.names = FALSE, recursive = FALSE)

# Eliminate template folder & rejected datasets
# 
# For debugging: only complete datasets
list_IDs = list_IDs[c(2,3,5,6,7,10,12,13,15,19)]

# Get number of participants
n_IDs = length(list_IDs)



# Initialize dataframes ---------------------------------------------------

# Initialize dataframe with demographic data from all participants
data_demo = data.frame(ID = list_IDs, # Participant numbers
                      age = rep(NA, n_IDs),
                      sex = rep(NA, n_IDs),
                      gender_match = rep(NA, n_IDs),
                      handedness = rep(NA, n_IDs),
                      education = rep(NA, n_IDs),
                      uMCTQ_score = rep(NA, n_IDs),
                      PSQI_score = rep(NA, n_IDs))

# Initialize dataframe with sleep quality data from all participants
data_sleep = data.frame(ID = list_IDs, 
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
                        GSQS_sum_con = rep(NA, n_IDs), # Groeningen Sleep Quality Scale sum score
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
                        GSQS_sum_exp = rep(NA, n_IDs))

# Initialize dataframe with PSD data from all participants
data_PSD = data.frame(ID = list_IDs, 
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
                        
# Initialize dataframe with SSVEP data from all participants
data_SSVEP = data.frame(ID = list_IDs, 
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
                        


# Load all derivative participant data ------------------------------------------------------------------------------------------------------------

for (i in list_IDs) { 
  
  ## Load demographic data
  
  # Get filename
  file_demo = paste(path_derivatives, i, "\\REDCap\\", i, "_personal-data.csv", sep = "")
  
  # Read CSV file
  data_demo_i = read.csv(file_demo)
  
  # Write data to main dataframe
  # Note: Segmenting import to skip variable time_lab_arrival, which was relevant for planning only
  data_demo[data_demo$ID == i,2:6] = data_demo_i[1:5] 
  data_demo[data_demo$ID == i,7:8] = data_demo_i[7:8]
  
  
  ## Load sleep data, CON
  
  # Get filename
  file_sleep_con = paste(path_derivatives, i, "\\Control\\", i, "_control_sleep-data.csv", sep = "")
  
  # Read CSV file
  data_sleep_con_i = read.csv(file_sleep_con, header=FALSE)
  
  # Write data to main dataframe
  data_sleep[data_sleep$ID == i,2:9] = data_sleep_con_i[,2]
  
  
  ## Load sleep data, EXP
  
  # Get filename
  file_sleep_exp = paste(path_derivatives, i, "\\Experimental\\", i, "_experimental_sleep-data.csv", sep = "")
  
  # Read CSV file
  data_sleep_exp_i = read.csv(file_sleep_exp, header=FALSE)
  
  # Write data to main dataframe
  data_sleep[data_sleep$ID == i,10:17] = data_sleep_exp_i[,2]
  
  
  ## Load PSD data, CON
  
  # Get filename
  file_PSD_con = paste(path_derivatives, i, "\\Control\\", i, "_control_PSD-output-metrics.csv", sep = "")
  
  # Read CSV file
  data_PSD_con_i = read.csv(file_PSD_con, header=FALSE)
  
  # Write data to main dataframe
  data_PSD[data_PSD$ID == i,2:13] = data_PSD_con_i[,2]
  
  
  ## Load PSD data,EXP
  
  # Get filename
  file_PSD_exp = paste(path_derivatives, i, "\\Experimental\\", i, "_experimental_PSD-output-metrics.csv", sep = "")
  
  # Read CSV file
  data_PSD_exp_i = read.csv(file_PSD_exp, header=FALSE)
  
  # Write data to main dataframe
  data_PSD[data_PSD$ID == i,14:25] = data_PSD_exp_i[,2]
  
  
  ## Load SSVEP data, CON
  
  # Get filename
  file_SSVEP_con = paste(path_derivatives, i, "\\Control\\", i, "_control_SSVEP-output-metrics.csv", sep = "")
  
  # Read CSV file
  data_SSVEP_con_i = read.csv(file_SSVEP_con, header=FALSE)
  
  # Write data to main dataframe
  data_SSVEP[data_SSVEP$ID == i,2:13] = data_SSVEP_con_i[,2]
  
  
  ## Load SSVEP data, EXP
  
  # Get filename
  file_SSVEP_exp = paste(path_derivatives, i, "\\Experimental\\", i, "_experimental_SSVEP-output-metrics.csv", sep = "")
  
  # Read CSV file
  data_SSVEP_exp_i = read.csv(file_SSVEP_exp, header=FALSE)
  
  # Write data to main dataframe
  data_SSVEP[data_SSVEP$ID == i,14:25] = data_SSVEP_exp_i[,2]
 
}

# Remove variables from environment that were only needed in the for loop
rm(list = ls(pattern = "file_"))
rm(list = ls(pattern = "_i"))



# Descriptives ------------------------------------------------------------

# Sample characteristics
stat.desc(data_demo$age)
stat.desc(data_demo$sex)
stat.desc(data_demo$gender_match)
stat.desc(data_demo$handedness)
stat.desc(data_demo$education)
stat.desc(data_demo$PSQI_score)
stat.desc(data_demo$uMCTQ_score) # not working yet



# Analysis: GSQS ----------------------------------------------------------

# Violin plot
plot_violin(data=data_sleep[,c("ID","GSQS_sum_con","GSQS_sum_exp")], title_plot="Subjective Sleep Quality", title_y="GSQS Sum Score")

# Connected scatterplot
plot_scatter(data=data_sleep[,c("ID","GSQS_sum_con","GSQS_sum_exp")], title_plot="Subjective Sleep Quality", title_y="GSQS Sum Score")



# Analysis: TST ----------------------------------------------------------

# Violin plot
plot_violin(data=data_sleep[,c("ID","TST_con","TST_exp")], title_plot="Total Sleep Time", title_y="TST (min)")

# Connected scatterplot
plot_scatter(data=data_sleep[,c("ID","TST_con","TST_exp")], title_plot="Total Sleep Time", title_y="TST (min)")



# Analysis: WASO ----------------------------------------------------------

# Violin plot
plot_violin(data=data_sleep[,c("ID","WASO_con","WASO_exp")], title_plot="Wake After Sleep Onset", title_y="WASO (min)")

# Connected scatterplot
plot_scatter(data=data_sleep[,c("ID","WASO_con","WASO_exp")], title_plot="Wake After Sleep Onset", title_y="WASO (min)")



# Descriptive: SOL, % of time per stage --------------------------------------------------------

# Violin plot of SOL
plot_violin(data=data_sleep[,c("ID","SOL_con","SOL_exp")], title_plot="Sleep Onset Latency", title_y="SOL (min)")

# Connected scatterplot
plot_scatter(data=data_sleep[,c("ID","SOL_con","SOL_exp")], title_plot="Sleep Onset Latency", title_y="SOL (min)")

# Stacked bar graph of % time per stage
plot_bar_stack(data_sleep[,c("ID","perN1_con","perN2_con","perN3_con","perREM_con","perN1_exp","perN2_exp","perN3_exp","perREM_exp")])



# Analysis: PSD ------------------------------------------------------

# Bar plot
# plot_bar_anova(data_PSD[,c(1,3,6,9,12,15,18,21,24)], title_plot="40 Hz Power", title_y = "PSD (- dB)")

# Connected scatterplot: PSD 40 Hz value
plot_scatter_main(data=data_PSD[,c("ID","W_PSD40_con","N2_PSD40_con","N3_PSD40_con","REM_PSD40_con","W_PSD40_exp","N2_PSD40_exp","N3_PSD40_exp","REM_PSD40_exp")],
                    title_plot="PSD 40 Hz Value", title_y="Power (dB)", ymin=-100, ymax=-150)


# Connected scatterplot: SNR
plot_scatter_SNR(data=data_PSD[,c("ID","W_SNR40_con","N2_SNR40_con","N3_SNR40_con","REM_SNR40_con","W_SNR40_exp","N2_SNR40_exp","N3_SNR40_exp","REM_SNR40_exp")],
                    title_plot="PSD 40 Hz Value - SNR", title_y="SNR")



# Analysis: SSVEP ------------------------------------------------------

# Connected scatterplot: SSVEP peak-to-peak amplitude
plot_scatter_main(data=data_SSVEP[,c("ID","W_PTA_con","N2_PTA_con","N3_PTA_con","REM_PTA_con","W_PTA_exp","N2_PTA_exp","N3_PTA_exp","REM_PTA_exp")],
                  title_plot="SSVEP Amplitude", title_y="Amplitude (uV)", ymin=0, ymax=2.3)

# Connected scatterplot: SNR
plot_scatter_SNR(data=data_SSVEP[,c("ID","W_SNR_con","N2_SNR_con","N3_SNR_con","REM_SNR_con","W_SNR_exp","N2_SNR_exp","N3_SNR_exp","REM_SNR_exp")],
                    title_plot="SSVEP Amplitude - SNR", title_y="SNR")




