# Author: LH
# Date: 2023-09-24
# Functionality: Functions for statistics_main.R, statistical tests
# Notes:



# Environment Setup ----------------------------------------------------------------------------------------------------

library("ez")




# Function: initialize_dataframe -------------------------------------------------------------------------------------------
# Initialize a dataframe for a given set of variables.

## INPUT

# list_IDs : list of chr
#   List of subjects IDs with fully collected datasets

# df_type : str
#   Type of dataframe to be created

## OUTPUT

# custom_dataframe : dataframe
#   Empty dataframe with columns matching the specified data types

initialize_dataframe <- function(list_IDs, df_type = c("demographic","sleep_quality","PSD_metrics","SSVEP_metrics")) {
  
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
  else {
    warning("ERROR: Most likely, dataframe type not accepted")
  }
  
  return(custom_dataframe)
}



# Function: paired t-test ------------------------------------------------------------------------------------------------------------
# Run a paired t-test on 2 variables.

## INPUT

# var1 : vector
#   Data for variable 1

# var2 : vector
#   Data for variable 2

## OUTPUT

# ttest_result : dataframe
#   Test results

# effect_size : int
#   Test effect size (cohen's d)

paired_ttest <- function(var1, var2) {

  # One-sided, paired t-test + confidence interval
  ttest_result = t.test(var1, var2, paired = TRUE, alternative = "greater")
  
  # Display results
  print("T-test:")
  print(ttest_result)
  
  # Effect size
  effect_size = (mean(var1) - mean(var2)) / sd(var1)

  # Display
  print("Cohen's d:")
  print(effect_size)
  
  # Return outputs
  return(ttest_result, effect_size)
  
}



# Function: Wilcoxon signed rank test ------------------------------------------------------------------------------------------------------------
# Run a Wilcoxon test on 2 variables.

## INPUT

# var1 : vector
#   Data for variable 1

# var2 : vector
#   Data for variable 2

## OUTPUT

# wilcox_result : dataframe
#   Test results

# effect_size : int
#   Test effect size (cohen's d)

wilcox_test <- function(var1, var2) {
  
  # One-sided, paired t-test + confidence interval
  wilcox_result = wilcox.test(var1, var2, paired = TRUE, alternative = "greater", conf.int = TRUE)
  
  # Display results
  print("Wilcox-test:")
  print(wilcox_result)
  
  # Effect size
  effect_size = wilcox_result.statistic / sqrt(length(var1))
  
  # Display
  print("Effect size r:")
  print(effect_size)
  
  # Return outputs
  return(wilcox_result, effect_size)
  
}



# Function: repeated-measures ANOVA ---------------------------------------

# ezANOVA

