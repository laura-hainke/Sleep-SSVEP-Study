# Author: LH
# Date: 2023-04-19
# Functionality: Script to import, process and evaluate personal data (Gamma-Sleep study).
# Notes:



# Environment Setup ----------------------------------------------------------------------------------------------------

# Packages
library(data.table)
library(lubridate)

# Source functions
source("PersonalData_functions.r")

# Get participant number from user
subject_nr <- readline(prompt="Subject number: ")


# Data & exclusion criteria check ------------------------------------------------------------------------------------------------------------

## Load data file and format it
imp_filename = paste(subject_nr, "exampledata.csv", sep = "_")
data = load_redcap(imp_filename)


## Check: are there any columns with unintended NA values?
check_data(data,'NA_values')


## Check: consent granted?
check_data(data,'consent')


## Check: any cutoff questions answered with 'maybe'?
check_data(data,'cutoff_extra')



# Questionnaires --------------------------------------------------------------------------------------------------

## Extract & check AUDIT score
audit_score = as.integer(data$audit_score[2])

check_score(audit_score,'AUDIT')


## Compute & check uMCTQ score
MSF_sc = score_uMCTQ(data)

check_score(MSF_sc,'uMCTQ')


## Compute & check PSQI score
psqi_score = score_PSQI(data)

check_score(psqi_score,'PSQI')


## Time to schedule arrival at sleep lab, 2 hours before usual bedtime on free days
lab_arrival = strptime(data$mumctq_fall_sleep_free[2], format = "%H:%M") - hours(2)
lab_arrival = format(lab_arrival, "%H:%M") # format to include only hours and minutes




# Export outputs --------------------------------------------------------------------------------------------------

# Initialize dataframe for desired output values
outputs = data.frame(matrix(ncol = 8, nrow = 1))
colnames(outputs) = c("age","sex","gender_match","handedness","education","time_lab_arrival","uMCTQ_score","PSQI_score")

# Gender: compute if gender matches sex or not
if (data$sex[2] == 1 & data$gender[2] == 1) { # female & woman
  gender_match = 1
} else if (data$sex[2] == 2 & data$gender[2] == 2) { # male & man
  gender_match = 1
} else { # all other cases, including intersex, transgender, non-binary, 'prefer not to say'; check individual case
  gender_match = 0
}

# Fill dataframe with output values in correct formats
outputs$age = as.numeric(data$age[2]) # num
outputs$sex = as.numeric(as.character(data$sex[2])) # num
outputs$gender_match = gender_match # num
outputs$handedness = as.numeric(as.character(data$handedness[2])) # num
outputs$education = as.numeric(as.character(data$education[2])) # num
outputs$time_lab_arrival = hms::parse_hm(lab_arrival) # hms
outputs$uMCTQ_score = hms::parse_hm(MSF_sc) # hms
outputs$PSQI_score = psqi_score # num

# Export as CSV
exp_filename = paste(subject_nr, "PersonalData.csv", sep = "_")
write.csv(outputs, file=exp_filename)




