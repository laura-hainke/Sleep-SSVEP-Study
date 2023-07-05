# Author: LH
# Date: 06.2023
# Functionality: Functions for the extraction of sleep quality data (Gamma-Sleep study).
# Notes:



# Environment Setup ----------------------------------------------------------------------------------------------------

# Packages
library(Hmisc)
library(pdftools)


# Function: load_gsqs -------------------------------------------------------------------------------------------
# Load a CSV file from redcap, extract GSQS data, and format it.
# Based on a script provided by REDCap when exporting data for R.

## INPUT

# filename : str
#   Name of the CSV file, including path and extension

## OUTPUT

# data : dataframe [n_variables,2]
#   Formatted dataframe

load_gsqs <- function(filename) {
  
  # Read data
  data = read.csv(filename)
  
  # Set factors
  data$gsqs1_con = factor(data$gsqs1_con,levels=c("1","0"))
  data$gsqs2_con = factor(data$gsqs2_con,levels=c("1","0"))
  data$gsqs3_con = factor(data$gsqs3_con,levels=c("1","0"))
  data$gsqs4_con = factor(data$gsqs4_con,levels=c("1","0"))
  data$gsqs5_con = factor(data$gsqs5_con,levels=c("1","0"))
  data$gsqs6_con = factor(data$gsqs6_con,levels=c("1","0"))
  data$gsqs7_con = factor(data$gsqs7_con,levels=c("1","0"))
  data$gsqs8_con = factor(data$gsqs8_con,levels=c("1","0"))
  data$gsqs9_con = factor(data$gsqs9_con,levels=c("1","0"))
  data$gsqs10_con = factor(data$gsqs10_con,levels=c("1","0"))
  data$gsqs11_con = factor(data$gsqs11_con,levels=c("1","0"))
  data$gsqs12_con = factor(data$gsqs12_con,levels=c("1","0"))
  data$gsqs13_con = factor(data$gsqs13_con,levels=c("1","0"))
  data$gsqs14_con = factor(data$gsqs14_con,levels=c("1","0"))
  data$gsqs15_con = factor(data$gsqs15_con,levels=c("1","0"))
  data$gsqs_con_complete = factor(data$gsqs_con_complete,levels=c("0","1","2"))
  data$gsqs1_exp = factor(data$gsqs1_exp,levels=c("1","0"))
  data$gsqs2_exp = factor(data$gsqs2_exp,levels=c("1","0"))
  data$gsqs3_exp = factor(data$gsqs3_exp,levels=c("1","0"))
  data$gsqs4_exp = factor(data$gsqs4_exp,levels=c("1","0"))
  data$gsqs5_exp = factor(data$gsqs5_exp,levels=c("1","0"))
  data$gsqs6_exp = factor(data$gsqs6_exp,levels=c("1","0"))
  data$gsqs7_exp = factor(data$gsqs7_exp,levels=c("1","0"))
  data$gsqs8_exp = factor(data$gsqs8_exp,levels=c("1","0"))
  data$gsqs9_exp = factor(data$gsqs9_exp,levels=c("1","0"))
  data$gsqs10_exp = factor(data$gsqs10_exp,levels=c("1","0"))
  data$gsqs11_exp = factor(data$gsqs11_exp,levels=c("1","0"))
  data$gsqs12_exp = factor(data$gsqs12_exp,levels=c("1","0"))
  data$gsqs13_exp = factor(data$gsqs13_exp,levels=c("1","0"))
  data$gsqs14_exp = factor(data$gsqs14_exp,levels=c("1","0"))
  data$gsqs15_exp = factor(data$gsqs15_exp,levels=c("1","0"))
  data$gsqs_exp_complete = factor(data$gsqs_exp_complete,levels=c("0","1","2"))
  
  # Save a copy of the dataframe with raw levels
  data_nolevels <- data.frame(data)
  
  # Set answer levels in 'data'
  levels(data$gsqs1_con)=c("True","False")
  levels(data$gsqs2_con)=c("True","False")
  levels(data$gsqs3_con)=c("True","False")
  levels(data$gsqs4_con)=c("True","False")
  levels(data$gsqs5_con)=c("True","False")
  levels(data$gsqs6_con)=c("True","False")
  levels(data$gsqs7_con)=c("True","False")
  levels(data$gsqs8_con)=c("True","False")
  levels(data$gsqs9_con)=c("True","False")
  levels(data$gsqs10_con)=c("True","False")
  levels(data$gsqs11_con)=c("True","False")
  levels(data$gsqs12_con)=c("True","False")
  levels(data$gsqs13_con)=c("True","False")
  levels(data$gsqs14_con)=c("True","False")
  levels(data$gsqs15_con)=c("True","False")
  levels(data$gsqs_con_complete)=c("Incomplete","Unverified","Complete")
  levels(data$gsqs1_exp)=c("True","False")
  levels(data$gsqs2_exp)=c("True","False")
  levels(data$gsqs3_exp)=c("True","False")
  levels(data$gsqs4_exp)=c("True","False")
  levels(data$gsqs5_exp)=c("True","False")
  levels(data$gsqs6_exp)=c("True","False")
  levels(data$gsqs7_exp)=c("True","False")
  levels(data$gsqs8_exp)=c("True","False")
  levels(data$gsqs9_exp)=c("True","False")
  levels(data$gsqs10_exp)=c("True","False")
  levels(data$gsqs11_exp)=c("True","False")
  levels(data$gsqs12_exp)=c("True","False")
  levels(data$gsqs13_exp)=c("True","False")
  levels(data$gsqs14_exp)=c("True","False")
  levels(data$gsqs15_exp)=c("True","False")
  levels(data$gsqs_exp_complete)=c("Incomplete","Unverified","Complete")
  
  # Merge dataframes with and without levels, for full labeling of variables and answers
  data = rbind(data, data_nolevels)
  
  # Set variable labels
  label(data$gsqs1_con)="I had a deep sleep last night"
  label(data$gsqs2_con)="I feel like I slept poorly last night"
  label(data$gsqs3_con)="It took me more than half an hour to fall asleep last night"
  label(data$gsqs4_con)="I felt tired after waking up this morning"
  label(data$gsqs5_con)="I woke up several times last night"
  label(data$gsqs6_con)="I feel like I didnt get enough sleep last night"
  label(data$gsqs7_con)="I got up in the middle of the night"
  label(data$gsqs8_con)="I felt rested after waking up this morning"
  label(data$gsqs9_con)="I feel like I only had a couple hours of sleep last night"
  label(data$gsqs10_con)="I feel I slept well last night"
  label(data$gsqs11_con)="I didnt sleep a wink last night"
  label(data$gsqs12_con)="I didnt have any trouble falling asleep last night"
  label(data$gsqs13_con)="After I woke up last night, I had trouble falling asleep again"
  label(data$gsqs14_con)="I tossed and turned all night last night"
  label(data$gsqs15_con)="I didnt get more than 5 hours sleep last night"
  label(data$gsqs_sum_con)="GSQS_con total score:"
  label(data$gsqs_con_complete)="Complete?"
  label(data$gsqs1_exp)="I had a deep sleep last night"
  label(data$gsqs2_exp)="I feel like I slept poorly last night"
  label(data$gsqs3_exp)="It took me more than half an hour to fall asleep last night"
  label(data$gsqs4_exp)="I felt tired after waking up this morning"
  label(data$gsqs5_exp)="I woke up several times last night"
  label(data$gsqs6_exp)="I feel like I didnt get enough sleep last night"
  label(data$gsqs7_exp)="I got up in the middle of the night"
  label(data$gsqs8_exp)="I felt rested after waking up this morning"
  label(data$gsqs9_exp)="I feel like I only had a couple hours of sleep last night"
  label(data$gsqs10_exp)="I feel I slept well last night"
  label(data$gsqs11_exp)="I didnt sleep a wink last night"
  label(data$gsqs12_exp)="I didnt have any trouble falling asleep last night"
  label(data$gsqs13_exp)="After I woke up last night, I had trouble falling asleep again"
  label(data$gsqs14_exp)="I tossed and turned all night last night"
  label(data$gsqs15_exp)="I didnt get more than 5 hours sleep last night"
  label(data$gsqs_sum_exp)="GSQS_exp total score:"
  label(data$gsqs_exp_complete)="Complete?"
  
  return(data)
  
}



# Function: load_psg ----------------------------------------------------------------------------------------------
# Load a PDF file from Polysmith, extract PSG data into a dataframe.

## INPUT

# filename : str
#   Name of the PDF file, including path and extension

## OUTPUT

# data : dataframe 
#   Dataframe that contains all PSG parameters.

load_psg <- function(filename) {
  
  # Load PDF file
  file = pdf_data(filename)
  
  # Access text
  text = file[[1]]$text
  
  ## Sanity check: do filename & participant ID in PDF match?
  
  # Get subject IDs
  id_pdf = text[21] # Subject ID of PDF file
  id_folder = substr(filename, 53, 54) # Subject ID of folder
  
  # Print warning if not matching
  if (id_pdf != id_folder) {
    print('Subject IDs not matching, check if files are correct!')
  }
  
  # Initialize output dataframe
  data = data.frame(matrix(ncol = 9, nrow = 1))
  colnames(data) = c("time_lightsoff","time_lightson","sleep_lat","TST","WASO","perN1","perN2","perN3","perREM")
  
  # Fill in correct values
  # NOTE: this was written based on an example PDF file. Quick check recommended for 'real' recordings
  
  data$time_lightsoff = text[44] # str; HMS
  data$time_lightson = text[48] # str; HMS
  data$WASO = as.numeric(text[152]) # min
  data$sleep_lat = as.numeric(text[154]) # min
  data$TST = as.numeric(text[77]) # min
  data$perN1 = as.numeric(text[172]) # % of TST
  data$perN2 = as.numeric(text[173]) # % of TST
  data$perN3 = as.numeric(text[174]) # % of TST
  data$perREM = as.numeric(text[175]) # % of TST
  
  return(data)
  
}

