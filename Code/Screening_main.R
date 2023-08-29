# Author: LH
# Date: 08.2023
# Functionality: Script to import screening data and evaluate participant suitability.


# Environment Setup ----------------------------------------------------------------------------------------------------

# Packages
library(data.table)
library(lubridate)

# Set working directory
setwd("C:/Users/Mitarbeiter/Documents/Gamma_Sleep/Code/Screening")

# Source functions, file in current directory
source("Screening_functions.r")

# Path to file with all input data
path_in = "C:/Users/Mitarbeiter/Documents/Gamma_Sleep/Study_Enrolment/Screening/REDCap_screening_data.csv"

# Load full data file and format it
data = load_redcap(path_in)

# Get record subset of interest
data = data[56:110,]

# Select current record
record_id = as.numeric(readline(prompt="Record ID:"))

# Get data for this record ID
data_id = data[data$record_id == record_id,]


# Data & exclusion criteria check for individual participant ------------------------------------------------------------------------------------------------------------

# Check: consent granted?
check_data(data_id,"consent")

# Check: are there any columns with unintended NA values?
check_data(data_id,"NA_values")

# Check: any cutoff questions answered with "maybe"?
check_data(data_id,"cutoff_extra")

# Extract & check AUDIT score
audit_score = as.integer(data_id$audit_score[1])
check_score(audit_score,"AUDIT")

# Compute & check uMCTQ score
MSF_sc = score_uMCTQ(data_id)
check_score(MSF_sc,"uMCTQ")

# Compute & check PSQI score
psqi_score = score_PSQI(data_id)
check_score(psqi_score,"PSQI")


