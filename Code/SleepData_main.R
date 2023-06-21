# Author: LH
# Date: 06.2023
# Functionality: Script to import, process and evaluate sleep data (Gamma-Sleep study).
# Notes:



# Environment Setup ----------------------------------------------------------------------------------------------------

# Source functions, file in current directory
source("SleepData_functions.r")

# Get participant number from user
subject_nr = readline(prompt="Subject number: ")

# Path to folders with input data
path_in = paste("D:/Documents/Gamma_Sleep/Data/Raw/", subject_nr, sep="")

# Paths to files in input data folders
path_gsqs = paste(path_in, "/REDCap/", subject_nr, "_sleep-quality.csv", sep="") # File: GSQS, con + exp
path_psg_con = paste(path_in, "/Session02/", subject_nr, "_session02_PSG-report.pdf", sep="") # File: PSG, control
path_psg_exp = paste(path_in, "/Session03/", subject_nr, "_session03_PSG-report.pdf", sep="") # File: PSG, experimental

# Path to folders with output data
path_out = paste("D:/Documents/Gamma_Sleep/Data/Derivatives/", subject_nr, sep="")

# Path to files in output data folders
path_out_con = paste(path_out, "/Control/", subject_nr, "_session02_sleep-data.csv", sep="") # File: all outputs, control
path_out_exp = paste(path_out, "/Experimental/", subject_nr, "_session03_sleep-data.csv", sep="") # File: all outputs, experimental



# Subjective sleep quality  --------------------------------------------------------------------------------------------

# Load and format GSQS file - control + experimental
gsqs_data = load_gsqs(path_gsqs)



# Objective sleep parameters --------------------------------------------------------------------------------------

# Load PSG file & extract parameters - control
psg_data_con = load_psg(path_psg_con)

# Load PSG file & extract parameters - experimental
psg_data_exp = load_psg(path_psg_exp)



# Export outputs --------------------------------------------------------------------------------------------------

# Loop over control and experimental conditions, save output data in CSV files
for (cond in c("con","exp")) {
  
  
  # Get correct values for current condition
  if (cond == "con") { # control
    
    gsqs_sum = as.integer(gsqs_data$gsqs_sum_con[2]) # GSQS sum score
    psg_data = psg_data_con # PSG parameters
    path = path_out_con # Output filename
    
	# Only in control condition: subtracting 10 min from sleep latency
	# This is due to the instruction to stay awake for 10 min, to ensure a minimal number of W epochs in the control condition
	psg_data$sleep_lat = psg_data$sleep_lat - 10
	
  } else if (cond == "exp") { # experimental
    
    gsqs_sum = as.integer(gsqs_data$gsqs_sum_exp[2]) # GSQS sum score
    psg_data = psg_data_exp # PSG parameters
    path = path_out_exp # Output filename
    
  }
  
  
  # Initialize dataframe for desired output values, starting with GSQS
  outputs = data.frame(GSQS_sum = gsqs_sum)
  
  # Add dataframe with PSG data
  outputs = cbind(outputs,psg_data)
  
  # Export as CSV
  write.csv(outputs, file=path)
  
}






