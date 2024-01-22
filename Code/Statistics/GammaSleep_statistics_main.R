# Author: LH
# Date: 2023-09-21
# Functionality: Load derivative participant data, generate plots, run statistical analysis
# Notes: 



# Environment Setup ----------------------------------------------------------------------------------------------------

# Working directory
setwd("C:\\Users\\Mitarbeiter\\Documents\\Gamma_Sleep\\Github_Repo\\Gamma-Sleep\\Code\\Statistics")

# Function files in current directory
source("GammaSleep_statistics_functions.r")
source("GammaSleep_plots_functions.r")
source("GammaSleep_data-handling_functions.r")

# Libraries
library(pastecs)



## Global variables
# Using global environment (<<- assignment) to avoid redundant function arguments

# Path to folders with derivative data
path_derivatives <<- "C:\\Users\\Mitarbeiter\\Documents\\Gamma_Sleep\\Data\\Derivatives\\" 

# List of folder names in directory, corresponding to participant numbers
list_IDs <<- list.dirs(path = path_derivatives, full.names = FALSE, recursive = FALSE)

# Remove rejected datasets
list_IDs <<- list_IDs[! list_IDs %in% c("03","15")] # subjects 03 and 15 were drop-outs


# Dataframes for Derivative Data ---------------------------------------------------

## Initializing 
data_demo <<- initialize_dataframe("demographic")

data_sleep <<- initialize_dataframe("sleep_quality")

data_PSD <<- initialize_dataframe("PSD_metrics")
                        
data_SSVEP <<- initialize_dataframe("SSVEP_metrics")

## Loading data
load_derivative_data()



# Sample Descriptives ------------------------------------------------------------

# Sample characteristics
stat.desc(data_demo$age)
stat.desc(data_demo$sex)
stat.desc(data_demo$gender_match)
stat.desc(data_demo$handedness)
stat.desc(data_demo$education)
stat.desc(data_demo$PSQI_score)



# Power Spectral Density (power in dB) ------------------------------------------------------

# Conversion to long format
data_PSD_dB_long = dataframe_wide_to_long(data_PSD[,c("ID","W_PSD40_con","N2_PSD40_con","N3_PSD40_con","REM_PSD40_con","W_PSD40_exp","N2_PSD40_exp","N3_PSD40_exp","REM_PSD40_exp")])

# Boxplots
plot_box_2X4(data=data_PSD_dB_long[data_PSD_dB_long$stage=="W",], title_plot="40 Hz Power - Wake", title_y="Power (dB)", ymin=-100, ymax=-150) 
plot_box_2X4(data=data_PSD_dB_long[data_PSD_dB_long$stage!="W",], title_plot="40 Hz Power - Sleep", title_y="Power (dB)", ymin=-100, ymax=-150) 

# Connected scatterplot
plot_scatter_2X4(data=data_PSD_dB_long[data_PSD_dB_long$stage=="W",], title_plot="40 Hz Power - Wake", title_y="Power (dB)", ymin=-100, ymax=-150)
plot_scatter_2X4(data=data_PSD_dB_long[data_PSD_dB_long$stage!="W",], title_plot="40 Hz Power - Sleep", title_y="Power (dB)", ymin=-100, ymax=-150)


## Test H1: W_exp > W_con

# Test parametric assumptions
check_normality(data_PSD$W_PSD40_exp - data_PSD$W_PSD40_con) # OK
check_outliers(data_PSD$W_PSD40_con) # OK
check_outliers(data_PSD$W_PSD40_exp) # OK
# Run statistical test
test_two_levels(data_PSD$W_PSD40_exp, data_PSD$W_PSD40_con, parametric=TRUE, alternative="greater")


## Test H2: N2_exp > N2_con

# Test parametric assumptions
check_normality(data_PSD$N2_PSD40_exp - data_PSD$N2_PSD40_con) # OK
check_outliers(data_PSD$N2_PSD40_con) # OK
check_outliers(data_PSD$N2_PSD40_exp) # OK
# Run statistical test
test_two_levels(data_PSD$N2_PSD40_exp, data_PSD$N2_PSD40_con, parametric=TRUE, alternative="greater")


## Test H3: N3_exp > N3_con

# Test parametric assumptions
check_normality(data_PSD$N3_PSD40_exp - data_PSD$N3_PSD40_con) # OK
check_outliers(data_PSD$N3_PSD40_con) # OK
check_outliers(data_PSD$N3_PSD40_exp) # OK
# Run statistical test
test_two_levels(data_PSD$N3_PSD40_exp, data_PSD$N3_PSD40_con, parametric=TRUE, alternative="greater")


## Test H4: REM_exp > REM_con

# Test parametric assumptions
check_normality(data_PSD$REM_PSD40_exp - data_PSD$REM_PSD40_con) # Not OK
check_outliers(data_PSD$REM_PSD40_con) # OK
check_outliers(data_PSD$REM_PSD40_exp) # OK
# Run statistical test
test_two_levels(data_PSD$REM_PSD40_exp, data_PSD$REM_PSD40_con, parametric=FALSE, alternative="greater")


## Test H5: W_exp =/= N2_exp =/= N3_exp =/= REM_exp

# Get data subset
data_anova_PSD_dB = subset(data_PSD_dB_long, condition=="exp", select=c(ID,stage,value))
# Test normality assumption for each cell
check_normality(data_PSD$W_PSD40_exp) # OK
check_normality(data_PSD$N2_PSD40_exp) # OK
check_normality(data_PSD$N3_PSD40_exp) # OK
check_normality(data_PSD$REM_PSD40_exp) # OK
# Test for outliers in each cell
check_outliers(data_PSD$W_PSD40_exp) # OK
check_outliers(data_PSD$N2_PSD40_exp) # OK
check_outliers(data_PSD$N3_PSD40_exp) # OK
check_outliers(data_PSD$REM_PSD40_exp) # OK
# Test for sphericity assumption
check_sphericity(data_PSD[,c("W_PSD40_exp","N2_PSD40_exp","N3_PSD40_exp","REM_PSD40_exp")]) # Not OK
# Run statistical test
test_multiple_levels(data_anova_PSD_dB, parametric=TRUE, sphericity_correction="greenhouse-geisser")



# Power Spectral Density (SNR) ------------------------------------------------------

# Conversion to long format
data_PSD_SNR_long = dataframe_wide_to_long(data_PSD[,c("ID","W_SNR40_con","N2_SNR40_con","N3_SNR40_con","REM_SNR40_con","W_SNR40_exp","N2_SNR40_exp","N3_SNR40_exp","REM_SNR40_exp")])

# Boxplots
plot_box_2X4(data=data_PSD_SNR_long[data_PSD_SNR_long$stage=="W",], title_plot="SNR of 40 Hz Power - Wake", title_y="SNR", ymin=0, ymax=350) 
plot_box_2X4(data=data_PSD_SNR_long[data_PSD_SNR_long$stage!="W",], title_plot="SNR of 40 Hz Power - Sleep", title_y="SNR", ymin=0, ymax=18) 

# Connected scatterplot
plot_scatter_2X4(data=data_PSD_SNR_long[data_PSD_SNR_long$stage=="W",], title_plot="SNR of 40 Hz Power - Wake", title_y="SNR", ymin=0, ymax=350)
plot_scatter_2X4(data=data_PSD_SNR_long[data_PSD_SNR_long$stage!="W",], title_plot="SNR of 40 Hz Power - Sleep", title_y="SNR", ymin=0, ymax=18)

# Median SNR values per condition
medians_PSD_SNR = aggregate(value ~ stage * condition, data_PSD_SNR_long, median) # mean likely biased by outliers
print(medians_PSD_SNR)



# Steady-State Visually Evoked Potentials (amplitude in uV) ------------------------------------------------------

# Conversion to long format
data_SSVEP_uV_long = dataframe_wide_to_long(data_SSVEP[,c("ID","W_PTA_con","N2_PTA_con","N3_PTA_con","REM_PTA_con","W_PTA_exp","N2_PTA_exp","N3_PTA_exp","REM_PTA_exp")])

# Boxplots
plot_box_2X4(data=data_SSVEP_uV_long[data_SSVEP_uV_long$stage=="W",], title_plot="SSVEP Amplitude - Wake", title_y="Amplitude (uV)", ymin=0, ymax=4)
plot_box_2X4(data=data_SSVEP_uV_long[data_SSVEP_uV_long$stage!="W",], title_plot="SSVEP Amplitude - Sleep", title_y="Amplitude (uV)", ymin=0, ymax=0.9)

# Connected scatterplot
plot_scatter_2X4(data=data_SSVEP_uV_long[data_SSVEP_uV_long$stage=="W",], title_plot="SSVEP Amplitude - Wake", title_y="Amplitude (uV)", ymin=0, ymax=4)
plot_scatter_2X4(data=data_SSVEP_uV_long[data_SSVEP_uV_long$stage!="W",], title_plot="SSVEP Amplitude - Sleep", title_y="Amplitude (uV)", ymin=0, ymax=0.9)


## Test H1: W_exp > W_con

# Test parametric assumptions
check_normality(data_SSVEP$W_PTA_exp - data_SSVEP$W_PTA_con) # Not OK
check_outliers(data_SSVEP$W_PTA_con) # Outlier: S23
check_outliers(data_SSVEP$W_PTA_exp) # Outlier: S08
# Run statistical test
test_two_levels(data_SSVEP$W_PTA_exp, data_SSVEP$W_PTA_con, parametric=FALSE, alternative="greater")


## Test H2: N2_exp > N2_con

# Test parametric assumptions
check_normality(data_SSVEP$N2_PTA_exp - data_SSVEP$N2_PTA_con) # Not OK
check_outliers(data_SSVEP$N2_PTA_con) # Outlier: S17
check_outliers(data_SSVEP$N2_PTA_exp) # Outlier: S04
# Run statistical test
test_two_levels(data_SSVEP$N2_PTA_exp, data_SSVEP$N2_PTA_con, parametric=FALSE, alternative="greater")


## Test H3: N3_exp > N3_con

# Test parametric assumptions
check_normality(data_SSVEP$N3_PTA_exp - data_SSVEP$N3_PTA_con) # OK
check_outliers(data_SSVEP$N3_PTA_con) # OK
check_outliers(data_SSVEP$N3_PTA_exp) # OK
# Run statistical test
test_two_levels(data_SSVEP$N3_PTA_exp, data_SSVEP$N3_PTA_con, parametric=TRUE, alternative="greater")


## Test H4: REM_exp > REM_con

# Test parametric assumptions
check_normality(data_SSVEP$REM_PTA_exp - data_SSVEP$REM_PTA_con) # Not OK
check_outliers(data_SSVEP$REM_PTA_con) # Outliers: S04, S17
check_outliers(data_SSVEP$REM_PTA_exp) # Outlier: S11
# Run statistical test
test_two_levels(data_SSVEP$REM_PTA_exp, data_SSVEP$REM_PTA_con, parametric=FALSE, alternative="greater")


## Test H5: W_exp =/= N2_exp =/= N3_exp =/= REM_exp

# Get data subset
data_anova_SSVEP_uV = subset(data_SSVEP_uV_long, condition=="exp", select=c(ID,stage,value))
# Test normality assumption for each cell
check_normality(data_SSVEP$W_PTA_exp) # Not OK
check_normality(data_SSVEP$N2_PTA_exp) # Not OK
check_normality(data_SSVEP$N3_PTA_exp) # Not OK
check_normality(data_SSVEP$REM_PTA_exp) # Not OK
# Test for outliers in each cell
check_outliers(data_SSVEP$W_PTA_exp) # Outlier: S08
check_outliers(data_SSVEP$N2_PTA_exp) # Outlier: S04
check_outliers(data_SSVEP$N3_PTA_exp) # OK
check_outliers(data_SSVEP$REM_PTA_exp) # Outlier: S11
# Test for sphericity assumption
check_sphericity(data_SSVEP[,c("W_PTA_exp","N2_PTA_exp","N3_PTA_exp","REM_PTA_exp")]) # Not OK
# Run statistical test
test_multiple_levels(data_anova_SSVEP_uV, parametric=FALSE, sphericity_correction="none")



# Steady-State Visually Evoked Potentials (SNR) ------------------------------------------------------

# Conversion to long format
data_SSVEP_SNR_long = dataframe_wide_to_long(data_SSVEP[,c("ID","W_SNR_con","N2_SNR_con","N3_SNR_con","REM_SNR_con","W_SNR_exp","N2_SNR_exp","N3_SNR_exp","REM_SNR_exp")])

# Boxplots
plot_box_2X4(data=data_SSVEP_SNR_long[data_SSVEP_SNR_long$stage=="W",], title_plot="SNR of SSVEP - Wake", title_y="SNR", ymin=0, ymax=30)
plot_box_2X4(data=data_SSVEP_SNR_long[data_SSVEP_SNR_long$stage!="W",], title_plot="SNR of SSVEP - Sleep", title_y="SNR", ymin=0, ymax=18)

# Connected scatterplot: SSVEP SNR
plot_scatter_2X4(data=data_SSVEP_SNR_long[data_SSVEP_SNR_long$stage=="W",], title_plot="SNR of SSVEP - Wake", title_y="SNR", ymin=0, ymax=30)
plot_scatter_2X4(data=data_SSVEP_SNR_long[data_SSVEP_SNR_long$stage!="W",], title_plot="SNR of SSVEP - Sleep", title_y="SNR", ymin=0, ymax=18)

# Median SNR values per condition
medians_SSVEP_SNR = aggregate(value ~ stage * condition, data_SSVEP_SNR_long, median) # mean likely biased by outliers
print(medians_SSVEP_SNR)



# GSQS ----------------------------------------------------------

# Conversion to long format
data_GSQS_long = dataframe_wide_to_long(data_sleep[,c("ID","GSQS_con","GSQS_exp")])

# Plot
plot_violin_paired(data=data_GSQS_long, title_plot="Subjective Sleep Quality", title_y="GSQS Sum Score")


## Test: GSQS_con =/= GSQS_exp

# Test parametric assumptions
check_normality(data_sleep$GSQS_exp - data_sleep$GSQS_con) # OK
check_outliers(data_sleep$GSQS_con) # OK
check_outliers(data_sleep$GSQS_exp) # OK
# Run statistical test
test_two_levels(data_sleep$GSQS_exp, data_sleep$GSQS_con, parametric=TRUE, alternative="two.sided")



# TST ----------------------------------------------------------

# Conversion to long format
data_TST_long = dataframe_wide_to_long(data_sleep[,c("ID","TST_con","TST_exp")])

# Plot
plot_violin_paired(data=data_TST_long, title_plot="Total Sleep Time", title_y="Minutes")


## Test: TST_con =/= TST_exp

# Test parametric assumptions
check_normality(data_sleep$TST_exp - data_sleep$TST_con) # OK
check_outliers(data_sleep$TST_con) # OK
check_outliers(data_sleep$TST_exp) # Outlier: S10
# Run statistical test
test_two_levels(data_sleep$TST_exp, data_sleep$TST_con, parametric=TRUE, alternative="two.sided")



# WASO ----------------------------------------------------------

# Conversion to long format
data_WASO_long = dataframe_wide_to_long(data_sleep[,c("ID","WASO_con","WASO_exp")])

# Plot
plot_violin_paired(data=data_WASO_long, title_plot="Wake After Sleep Onset", title_y="Minutes")


## Test: WASO_con =/= WASO_exp

# Test parametric assumptions
check_normality(data_sleep$WASO_exp - data_sleep$WASO_con) # OK
check_outliers(data_sleep$WASO_con) # Outlier: S25
check_outliers(data_sleep$WASO_exp) # OK
# Run statistical test
test_two_levels(data_sleep$WASO_exp, data_sleep$WASO_con, parametric=TRUE, alternative="two.sided")



# SOL -----------------------------------------------------------------------------------------------------------------------

# Conversion to long format
data_SOL_long = dataframe_wide_to_long(data_sleep[,c("ID","SOL_con","SOL_exp")])

# Plot
plot_violin_paired(data=data_SOL_long, title_plot="Sleep Onset Latency", title_y="Minutes")

# Descriptives
stat.desc(data_sleep$SOL_con)
stat.desc(data_sleep$SOL_exp)



# % of Time per Stage --------------------------------------------------------

# Conversion to long format
data_percent_stages_long = dataframe_wide_to_long(data_sleep[,c("ID","perN1_con","perN2_con","perN3_con","perREM_con","perN1_exp","perN2_exp","perN3_exp","perREM_exp")])

# Stacked bar graph of % time per stage
plot_bar_stack(data_percent_stages_long)

# Get mean and SD of % time per stage, by condition
means_percent_stage = aggregate(value ~ variable * condition, data_percent_stages_long, mean)
SDs_percent_stage = aggregate(value ~ variable * condition, data_percent_stages_long, sd)



# Stimulation Time Plot ----------------------------------------------------------------------------------------------------

# Conversion to long format
data_nr_epochs_long = dataframe_wide_to_long(data_PSD[,c("ID","N2_nepochs_exp","N3_nepochs_exp","REM_nepochs_exp")])

# Convert nr. of epochs into minutes 
data_nr_epochs_long$value = data_nr_epochs_long$value/2

plot_box_1X4(data_nr_epochs_long, title_plot="Stimulation Duration per Stage", title_y="Minutes", ymin=0, ymax=250, limits=c(240,96,120))



# SSVEP Plots ---------------------------------------------------------------------------------------------------------------

# All SSVEP time series data in long format
timeseries_SSVEPs = import_SSVEPs_to_long_dataframe()


## Subset data, plot 1 condition X 1 stage at a time, for all subjects

# Control
data_SSVEPs_W_con = subset(timeseries_SSVEPs, subset=(stage=="W" & condition=="con"), select=c(ID,time,value))
plot_n_SSVEPs(data_SSVEPs_W_con, 
              title_plot="Individual SSVEPs: Stage W, Control Condition", 
              colour=colour_scheme$con, 
              ymax=0.2)

data_SSVEPs_N2_con = subset(timeseries_SSVEPs, subset=(stage=="N2" & condition=="con"), select=c(ID,time,value))
plot_n_SSVEPs(data_SSVEPs_N2_con, 
              title_plot="Individual SSVEPs: Stage N2, Control Condition", 
              colour=colour_scheme$con, 
              ymax=0.2)

data_SSVEPs_N3_con = subset(timeseries_SSVEPs, subset=(stage=="N3" & condition=="con"), select=c(ID,time,value))
plot_n_SSVEPs(data_SSVEPs_N3_con, 
              title_plot="Individual SSVEPs: Stage N3, Control Condition", 
              colour=colour_scheme$con, 
              ymax=0.2)

data_SSVEPs_REM_con = subset(timeseries_SSVEPs, subset=(stage=="REM" & condition=="con"), select=c(ID,time,value))
plot_n_SSVEPs(data_SSVEPs_REM_con, 
              title_plot="Individual SSVEPs: Stage REM, Control Condition", 
              colour=colour_scheme$con, 
              ymax=0.2)

# Experimental
data_SSVEPs_W_exp = subset(timeseries_SSVEPs, subset=(stage=="W" & condition=="exp"), select=c(ID,time,value))
plot_n_SSVEPs(data_SSVEPs_W_exp, 
              title_plot="Individual SSVEPs: Stage W, Experimental Condition", 
              colour=colour_scheme$exp, 
              ymax=2.2)

data_SSVEPs_N2_exp = subset(timeseries_SSVEPs, subset=(stage=="N2" & condition=="exp"), select=c(ID,time,value))
plot_n_SSVEPs(data_SSVEPs_N2_exp, 
              title_plot="Individual SSVEPs: Stage N2, Experimental Condition", 
              colour=colour_scheme$exp, 
              ymax=0.25)

data_SSVEPs_N3_exp = subset(timeseries_SSVEPs, subset=(stage=="N3" & condition=="exp"), select=c(ID,time,value))
plot_n_SSVEPs(data_SSVEPs_N3_exp, 
              title_plot="Individual SSVEPs: Stage N3, Experimental Condition", 
              colour=colour_scheme$exp, 
              ymax=0.25)

data_SSVEPs_REM_exp = subset(timeseries_SSVEPs, subset=(stage=="REM" & condition=="exp"), select=c(ID,time,value))
plot_n_SSVEPs(data_SSVEPs_REM_exp, 
              title_plot="Individual SSVEPs: Stage REM, Experimental Condition", 
              colour=colour_scheme$exp, 
              ymax=0.5)


## Plot grand average SSVEPs by stage, compare conditions

# Collapse data over subjects
data_SSVEPs_avg = timeseries_SSVEPs %>% group_by(time,stage,condition) %>% summarise_at(vars("value"), mean)

# Separate stage W
data_SSVEPs_avg_wake = data_SSVEPs_avg[data_SSVEPs_avg$stage=="W",]
data_SSVEPs_avg_sleep = data_SSVEPs_avg[data_SSVEPs_avg$stage!="W",]

# Plot sleep & wake
plot_avg_SSVEPs_stage(data_SSVEPs_avg_wake, title_plot="Average SSVEPs - Wake")
plot_avg_SSVEPs_stage(data_SSVEPs_avg_sleep, title_plot="Average SSVEPs - Sleep")


## Plot grand average SSVEPs by stage & condition, on top of subject-level averaged SSVEPs

plot_SSVEPs_n_avg(timeseries_SSVEPs[timeseries_SSVEPs$stage=="W",],
                  data_SSVEPs_avg_wake,
                  "Average SSVEPs, Stage W")
plot_SSVEPs_n_avg(timeseries_SSVEPs[timeseries_SSVEPs$stage=="N2",],
                  data_SSVEPs_avg_sleep[data_SSVEPs_avg_sleep$stage=="N2",],
                  "Average SSVEPs, Stage N2")
plot_SSVEPs_n_avg(timeseries_SSVEPs[timeseries_SSVEPs$stage=="N3",],
                  data_SSVEPs_avg_sleep[data_SSVEPs_avg_sleep$stage=="N3",],
                  "Average SSVEPs, Stage N3")
plot_SSVEPs_n_avg(timeseries_SSVEPs[timeseries_SSVEPs$stage=="REM",],
                  data_SSVEPs_avg_sleep[data_SSVEPs_avg_sleep$stage=="REM",],
                  "Average SSVEPs, Stage REM")








