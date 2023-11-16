# Author: LH
# Date: 2023-09-21
# Functionality: Load derivative participant data, generate plots, run statistical analysis
# Notes:



# Environment Setup ----------------------------------------------------------------------------------------------------

# Working directory
setwd("C:\\Users\\Mitarbeiter\\Documents\\Gamma_Sleep\\Code\\Statistics")

# Function files in current directory
source("Statistics_functions.r")
source("Plots_functions.r")

# Libraries
library("pastecs")

# Path to folders with derivative data
path_derivatives = "C:\\Users\\Mitarbeiter\\Documents\\Gamma_Sleep\\Data\\Derivatives\\"

# List of folder names in directory, corresponding to participant numbers
list_IDs = list.dirs(path = path_derivatives, full.names = FALSE, recursive = FALSE)

# Remove rejected datasets (& for debugging, datasets not yet collected)
list_IDs = list_IDs[-c(3,15,19:22,25:32)]



# Initialize dataframes for derivative data ---------------------------------------------------

# To be used in statistical analysis
data_demo = initialize_dataframe(list_IDs, "demographic")

data_sleep = initialize_dataframe(list_IDs, "sleep_quality")

data_PSD = initialize_dataframe(list_IDs, "PSD_metrics")
                        
data_SSVEP = initialize_dataframe(list_IDs, "SSVEP_metrics")



# Load all derivative participant data into dataframes ------------------------------------------------------------------------------------------------------------

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
      data_demo[data_demo$ID == i,2:6] = data_csv[2,1:5] # Segmenting import to skip variable time_lab_arrival, not relevant for analyses
      data_demo[data_demo$ID == i,7:8] = data_csv[2,7:8]
    } else if (filename_substrings$file_name[j] == "_control_sleep-data.csv") {
      data_sleep[data_sleep$ID == i,2:9] = data_csv[,2]
    } else if (filename_substrings$file_name[j] == "_experimental_sleep-data.csv") {
      data_sleep[data_sleep$ID == i,10:17] = data_csv[,2]
    } else if (filename_substrings$file_name[j] == "_control_PSD-output-metrics.csv") {
      data_PSD[data_PSD$ID == i,2:13] = data_csv[,2]
    } else if (filename_substrings$file_name[j] == "_experimental_PSD-output-metrics.csv") {
      data_PSD[data_PSD$ID == i,14:25] = data_csv[,2]
    } else if (filename_substrings$file_name[j] == "_control_SSVEP-output-metrics.csv") {
      data_SSVEP[data_SSVEP$ID == i,2:13] = data_csv[,2]
    } else if (filename_substrings$file_name[j] == "_experimental_SSVEP-output-metrics.csv") {
      data_SSVEP[data_SSVEP$ID == i,14:25] = data_csv[,2]
    }
    
  }
  
}



# Descriptives ------------------------------------------------------------

# Sample characteristics
stat.desc(data_demo$age)
stat.desc(data_demo$sex)
stat.desc(data_demo$gender_match)
stat.desc(data_demo$handedness)
stat.desc(data_demo$education)
stat.desc(data_demo$PSQI_score)
stat.desc(data_demo$uMCTQ_score) # not working yet



# Plots: GSQS ----------------------------------------------------------

# Violin plot
plot_violin(data=data_sleep[,c("ID","GSQS_con","GSQS_exp")], title_plot="Subjective Sleep Quality", title_y="GSQS Sum Score")

# Connected scatterplot
plot_scatter(data=data_sleep[,c("ID","GSQS_con","GSQS_exp")], title_plot="Subjective Sleep Quality", title_y="GSQS Sum Score")

# Violin plots of paired values
plot_violin_paired(data=data_sleep[,c("ID","GSQS_con","GSQS_exp")], title_plot="Subjective Sleep Quality", title_y="GSQS Sum Score")


# Plots: TST ----------------------------------------------------------

# Violin plot
plot_violin(data=data_sleep[,c("ID","TST_con","TST_exp")], title_plot="Total Sleep Time", title_y="TST (min)")

# Connected scatterplot
plot_scatter(data=data_sleep[,c("ID","TST_con","TST_exp")], title_plot="Total Sleep Time", title_y="TST (min)")



# Plots: WASO ----------------------------------------------------------

# Violin plot
plot_violin(data=data_sleep[,c("ID","WASO_con","WASO_exp")], title_plot="Wake After Sleep Onset", title_y="WASO (min)")

# Connected scatterplot
plot_scatter(data=data_sleep[,c("ID","WASO_con","WASO_exp")], title_plot="Wake After Sleep Onset", title_y="WASO (min)")



# Plots: SOL, % of time per stage --------------------------------------------------------

# Violin plot of SOL
plot_violin(data=data_sleep[,c("ID","SOL_con","SOL_exp")], title_plot="Sleep Onset Latency", title_y="SOL (min)")

# Connected scatterplot
plot_scatter(data=data_sleep[,c("ID","SOL_con","SOL_exp")], title_plot="Sleep Onset Latency", title_y="SOL (min)")

# Stacked bar graph of % time per stage
plot_bar_stack(data_sleep[,c("ID","perN1_con","perN2_con","perN3_con","perREM_con","perN1_exp","perN2_exp","perN3_exp","perREM_exp")])



# Plots: PSD metrics ------------------------------------------------------

# Boxplots
plot_box_anova(data_PSD[,c(1,3,6,9,12,15,18,21,24)], title_plot="40 Hz Power", title_y = "PSD (dB)")

# Connected scatterplot: PSD 40 Hz value
plot_scatter_main(data=data_PSD[,c("ID","W_PSD40_con","N2_PSD40_con","N3_PSD40_con","REM_PSD40_con","W_PSD40_exp","N2_PSD40_exp","N3_PSD40_exp","REM_PSD40_exp")],
                    title_plot="PSD 40 Hz Value", title_y="Power (dB)", ymin=-100, ymax=-150)


# Connected scatterplot: SNR
plot_scatter_SNR(data=data_PSD[,c("ID","W_SNR40_con","N2_SNR40_con","N3_SNR40_con","REM_SNR40_con","W_SNR40_exp","N2_SNR40_exp","N3_SNR40_exp","REM_SNR40_exp")],
                    title_plot="PSD 40 Hz Value - SNR", title_y="SNR")



# Plots: SSVEP metrics ------------------------------------------------------

# Boxplots
plot_box_anova(data_SSVEP[,c(1,3,6,9,12,15,18,21,24)], title_plot="SSVEP Amplitude", title_y = "Amplitude (uV)")


# Connected scatterplot: SSVEP peak-to-peak amplitude
plot_scatter_main(data=data_SSVEP[,c("ID","W_PTA_con","N2_PTA_con","N3_PTA_con","REM_PTA_con","W_PTA_exp","N2_PTA_exp","N3_PTA_exp","REM_PTA_exp")],
                  title_plot="SSVEP Amplitude", title_y="Amplitude (uV)", ymin=0, ymax=2.3)

# Connected scatterplot: SNR
plot_scatter_SNR(data=data_SSVEP[,c("ID","W_SNR_con","N2_SNR_con","N3_SNR_con","REM_SNR_con","W_SNR_exp","N2_SNR_exp","N3_SNR_exp","REM_SNR_exp")],
                    title_plot="SSVEP Amplitude - SNR", title_y="SNR")



# Plots: SSVEPs -----------------------------------------------------------




