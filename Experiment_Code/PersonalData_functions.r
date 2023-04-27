# Author: LH
# Date: 2023-04-19
# Functionality: Functions for the evaluation of personal data (Gamma-Sleep study).



# Libraries -------------------------------------------------------------------------------------------------------

library(Hmisc)
library(mctq)
library(data.table)
library(lubridate)


# Function: load_redcap -------------------------------------------------------------------------------------------
# Load a CSV file from redcap and format it.
# Based on a script provided by REDCap when exporting data for R.

## INPUT

# filename : str
#   Name of the CSV file, including path and extension

## OUTPUT

# data : dataframe [n_variables,2]
#   Formatted dataframe

load_redcap <- function(filename) {

  # Read data
  data = read.csv(filename)
  
  # Set factors
  data$language = factor(data$language,levels=c("en","de"))
  data$volunteer = factor(data$volunteer,levels=c("1","0"))
  data$cutoff_age = factor(data$cutoff_age,levels=c("1","0"))
  data$cutoff_colour = factor(data$cutoff_colour,levels=c("1","0"))
  data$cutoff_neuro = factor(data$cutoff_neuro,levels=c("1","2","0"))
  data$epilepsy_family = factor(data$epilepsy_family,levels=c("1","0"))
  data$cutoff_substances = factor(data$cutoff_substances,levels=c("1","2","0"))
  data$cutoff_sleep = factor(data$cutoff_sleep,levels=c("1","2","0"))
  data$cutoff_psych = factor(data$cutoff_psych,levels=c("1","2","0"))
  data$cutoff_shiftwork = factor(data$cutoff_shiftwork,levels=c("1","0"))
  data$cutoff_travel = factor(data$cutoff_travel,levels=c("1","0"))
  data$exclusion_confirm = factor(data$exclusion_confirm,levels=c("1"))
  data$exclusion_criteria_complete = factor(data$exclusion_criteria_complete,levels=c("0","1","2"))
  data$audit_q1 = factor(data$audit_q1,levels=c("0","1","2","3","4"))
  data$audit_q2 = factor(data$audit_q2,levels=c("0","1","2","3","4"))
  data$audit_q3 = factor(data$audit_q3,levels=c("0","1","2","3","4"))
  data$audit_q4 = factor(data$audit_q4,levels=c("0","1","2","3","4"))
  data$audit_q5 = factor(data$audit_q5,levels=c("0","1","2","3","4"))
  data$audit_q6 = factor(data$audit_q6,levels=c("0","1","2","3","4"))
  data$audit_q7 = factor(data$audit_q7,levels=c("0","1","2","3","4"))
  data$audit_q8 = factor(data$audit_q8,levels=c("0","1","2","3","4"))
  data$audit_q9 = factor(data$audit_q9,levels=c("0","2","4"))
  data$audit_q10 = factor(data$audit_q10,levels=c("0","2","4"))
  data$audit_complete = factor(data$audit_complete,levels=c("0","1","2"))
  # data$psqi_5a = factor(data$psqi_5a,levels=c("0","1","2","3"))
  # data$psqi_5b = factor(data$psqi_5b,levels=c("0","1","2","3"))
  # data$psqi_5c = factor(data$psqi_5c,levels=c("0","1","2","3"))
  # data$psqi_5d = factor(data$psqi_5d,levels=c("0","1","2","3"))
  # data$psqi_5e = factor(data$psqi_5e,levels=c("0","1","2","3"))
  # data$psqi_5f = factor(data$psqi_5f,levels=c("0","1","2","3"))
  # data$psqi_5g = factor(data$psqi_5g,levels=c("0","1","2","3"))
  # data$psqi_5h = factor(data$psqi_5h,levels=c("0","1","2","3"))
  # data$psqi_5i = factor(data$psqi_5i,levels=c("0","1","2","3"))
  # data$psqi_5othera = factor(data$psqi_5othera,levels=c("0","1","2","3"))
  # data$psqi_6 = factor(data$psqi_6,levels=c("0","1","2","3"))
  # data$psqi_7 = factor(data$psqi_7,levels=c("0","1","2","3"))
  # data$psqi_8 = factor(data$psqi_8,levels=c("0","1","2","3"))
  # data$psqi_9 = factor(data$psqi_9,levels=c("0","1","2","3"))
  data$psqi_10 = factor(data$psqi_10,levels=c("0","1","2","3"))
  data$psqi_10a = factor(data$psqi_10a,levels=c("0","1","2","3"))
  data$psqi_10b = factor(data$psqi_10b,levels=c("0","1","2","3"))
  data$psqi_10c = factor(data$psqi_10c,levels=c("0","1","2","3"))
  data$psqi_10d = factor(data$psqi_10d,levels=c("0","1","2","3"))
  data$psqi_10e1 = factor(data$psqi_10e1,levels=c("0","1","2","3"))
  data$psqi_complete = factor(data$psqi_complete,levels=c("0","1","2"))
  data$mumctq_nr_workdays = factor(data$mumctq_nr_workdays,levels=c("0","1","2","3","4","5","6","7"))
  data$mumctq_alarm_free_days = factor(data$mumctq_alarm_free_days,levels=c("1","0"))
  data$mumctq_complete = factor(data$mumctq_complete,levels=c("0","1","2"))
  data$sex = factor(data$sex,levels=c("1","2","3","0"))
  data$gender = factor(data$gender,levels=c("1","2","3","0","4"))
  data$handedness = factor(data$handedness,levels=c("1","2","3"))
  data$education = factor(data$education,levels=c("0","1","2","3","4","5","6","7","8"))
  data$demographics_complete = factor(data$demographics_complete,levels=c("0","1","2"))

  # Change levels of 'language' (en/de on REDCap due to multilanguage management)
  levels(data$language)=c("1","2")
  
  # Save a copy of the dataframe with raw levels
  data_nolevels <- data.frame(data)
  
  # Set answer levels in 'data'
  levels(data$language)=c("English","Deutsch")
  levels(data$volunteer)=c("Yes, lets proceed with the questionnaire.","No, I prefer not to take part.")
  levels(data$cutoff_age)=c("Yes","No")
  levels(data$cutoff_colour)=c("Yes","No")
  levels(data$cutoff_neuro)=c("Yes","Maybe","No")
  levels(data$epilepsy_family)=c("Yes","No")
  levels(data$cutoff_substances)=c("Yes","Maybe","No")
  levels(data$cutoff_sleep)=c("Yes","Maybe","No")
  levels(data$cutoff_psych)=c("Yes","Maybe","No")
  levels(data$cutoff_shiftwork)=c("Yes","No")
  levels(data$cutoff_travel)=c("Yes","No")
  levels(data$exclusion_confirm)=c("Yes")
  levels(data$exclusion_criteria_complete)=c("Incomplete","Unverified","Complete")
  levels(data$audit_q1)=c("Never","Monthly or less","Two to four times a month","Two to three times a week","Four or more times a week")
  levels(data$audit_q2)=c("1 or 2","3 or 4","5 or 6","7 to 9","10 or more")
  levels(data$audit_q3)=c("Never","Less than monthly","Monthly","Weekly","Daily or almost daily")
  levels(data$audit_q4)=c("Never","Less than monthly","Monthly","Weekly","Daily or almost daily")
  levels(data$audit_q5)=c("Never","Less than monthly","Monthly","Weekly","Daily or almost daily")
  levels(data$audit_q6)=c("Never","Less than monthly","Monthly","Weekly","Daily or almost daily")
  levels(data$audit_q7)=c("Never","Less than monthly","Monthly","Weekly","Daily or almost daily")
  levels(data$audit_q8)=c("Never","Less than monthly","Monthly","Weekly","Daily or almost daily")
  levels(data$audit_q9)=c("No","Yes, but not in the last year","Yes, during the last year")
  levels(data$audit_q10)=c("No","Yes, but not in the last year","Yes, during the last year")
  levels(data$audit_complete)=c("Incomplete","Unverified","Complete")
  # levels(data$psqi_5a)=c("Not during the past month","Less than once a week","Once or twice a week","Three or more times a week")
  # levels(data$psqi_5b)=c("Not during the past month","Less than once a week","Once or twice a week","Three or more times a week")
  # levels(data$psqi_5c)=c("Not during the past month","Less than once a week","Once or twice a week","Three or more times a week")
  # levels(data$psqi_5d)=c("Not during the past month","Less than once a week","Once or twice a week","Three or more times a week")
  # levels(data$psqi_5e)=c("Not during the past month","Less than once a week","Once or twice a week","Three or more times a week")
  # levels(data$psqi_5f)=c("Not during the past month","Less than once a week","Once or twice a week","Three or more times a week")
  # levels(data$psqi_5g)=c("Not during the past month","Less than once a week","Once or twice a week","Three or more times a week")
  # levels(data$psqi_5h)=c("Not during the past month","Less than once a week","Once or twice a week","Three or more times a week")
  # levels(data$psqi_5i)=c("Not during the past month","Less than once a week","Once or twice a week","Three or more times a week")
  # levels(data$psqi_5othera)=c("Not during the past month","Less than once a week","Once or twice a week","Three or more times a week")
  # levels(data$psqi_6)=c("Very good","Fairly good","Fairly bad","Very bad")
  # levels(data$psqi_7)=c("Not during the past month","Less than once a week","Once or twice a week","Three or more times a week")
  # levels(data$psqi_8)=c("Not during the past month","Less than once a week","Once or twice a week","Three or more times a week")
  # levels(data$psqi_9)=c("No problem at all","Only a very slight problem","Somewhat of a problem","A very big problem")
  levels(data$psqi_10)=c("No bed partner or room mate","Partner/room mate in other room","Partner in same room, but not same bed","Partner in same bed")
  levels(data$psqi_10a)=c("Not during the past month","Less than once a week","Once or twice a week","Three or more times a week")
  levels(data$psqi_10b)=c("Not during the past month","Less than once a week","Once or twice a week","Three or more times a week")
  levels(data$psqi_10c)=c("Not during the past month","Less than once a week","Once or twice a week","Three or more times a week")
  levels(data$psqi_10d)=c("Not during the past month","Less than once a week","Once or twice a week","Three or more times a week")
  levels(data$psqi_10e1)=c("Not during the past month","Less than once a week","Once or twice a week","Three or more times a week")
  levels(data$psqi_complete)=c("Incomplete","Unverified","Complete")
  levels(data$mumctq_nr_workdays)=c("0","1","2","3","4","5","6","7")
  levels(data$mumctq_alarm_free_days)=c("Yes","No")
  levels(data$mumctq_complete)=c("Incomplete","Unverified","Complete")
  levels(data$sex)=c("female","male","intersex","prefer not to say")
  levels(data$gender)=c("woman","man","non-binary","prefer not to say","other")
  levels(data$handedness)=c("Right-handed","Ambidextrous","Left-handed")
  levels(data$education)=c("Early childhood education","Primary education","Lower secondary education","Upper secondary education","Post-secondary, non-tertiary education","Short-cycle tertiary education","Bachelors or equivalent level","Masters or equivalent level","Doctoral or equivalent level")
  levels(data$demographics_complete)=c("Incomplete","Unverified","Complete")
  
  # Merge dataframes with and without levels, for full labeling of variables and answers
  data = rbind(data, data_nolevels)
  
  # Set variable labels
  label(data$record_id)="Record ID"
  label(data$language)="Preferred language"
  label(data$volunteer)="I have read the information above and consider volunteering for this study."
  label(data$cutoff_age)="Are you between 18 and 35 years old?"
  label(data$cutoff_colour)="Do you have any difficulty distinguishing between red and green (colour-blindness)?"
  label(data$cutoff_neuro)="At any point in your life, have you experienced any of the following:  Uncontrolled shaking movements of your whole body or parts of it, with full or partial loss of consciousness (Epilepsy, Seizures) Pulsating headaches possibly accompanied by nausea, sensitivity to light / sound / smell, visual disturbances (Migraine) Surgery on your brain (e.g., to remove a brain tumor, to perform an implant…) Severe concussion Stroke Other neurological conditions "
  label(data$cutoff_neuro_extra)="Please specify:"
  label(data$epilepsy_family)="Has any of your first-degree relatives been diagnosed with Epilepsy, or experienced seizures?"
  label(data$cutoff_substances)="In the past 2 months, have you consumed any of these substances?  Nicotine Cannabis Psychopharmacological medication Other drugs "
  label(data$cutoff_substances_extra)="Please specify:"
  label(data$cutoff_sleep)="In the past 6 months, have you experienced any of these sleep disturbances? Or has anyone remarked that you do?  Regular difficulty falling or staying asleep (Insomnia) Walking or carrying out complex activities during the night while not fully awake, without remembering them afterward (Sleepwalking) Involuntary habitual grinding of the teeth during sleep (Bruxism) Excessive daytime sleepiness with sudden muscle weakness (Narcolepsy) Unpleasant “creeping” sensation and pain in the lower legs that can be relieved by movement of the legs, such as walking or kicking (Restless Legs Syndrome) Periodically interrupted breathing during sleep that causes gasping or “snorting” noises, more than just snoring (Sleep Apnoea) "
  label(data$cutoff_sleep_extra)="Please specify:"
  label(data$cutoff_psych)="In the past 6 months, have you experienced any of these psychiatric symptoms?  Depressed mood Extreme mood swings Excessive fears or worries Substance abuse Hallucinations or paranoia Suicidal thoughts Other mental issues "
  label(data$cutoff_psych_extra)="Please specify:"
  label(data$cutoff_shiftwork)="In the past month, I have been a shift- or night-worker:"
  label(data$cutoff_travel)="In the past month, I have travelled across two or more time zones:"
  label(data$exclusion_confirm)="Please double-check: Have you correctly chosen the options that apply to you?"
  label(data$exclusion_criteria_complete)="Complete?"
  label(data$audit_q1)="How often do you have a drink containing alcohol?"
  label(data$audit_q2)="How many drinks containing alcohol do you have on a typical day when you are drinking?"
  label(data$audit_q3)="How often do you have six or more drinks on one occasion?"
  label(data$audit_q4)="How often during the last year have you found that you were not able to stop drinking once you had started?"
  label(data$audit_q5)="How often during the last year have you failed to do what was normally expected of you because of drinking?"
  label(data$audit_q6)="How often during the last year have you needed a first drink in the morning to get yourself going after a heavy drinking session?"
  label(data$audit_q7)="How often during the last year have you had a feeling of guilt or remorse after drinking?"
  label(data$audit_q8)="How often during the last year have you been unable to remember what happened the night before because you had been drinking?"
  label(data$audit_q9)="Have you or someone else been injured as a result of your drinking?"
  label(data$audit_q10)="Has a relative or friend, doctor or other health worker been concerned about your drinking or suggested you cut down?"
  label(data$audit_score)="AUDIT summed score"
  label(data$audit_complete)="Complete?"
  label(data$psqi_1)="1. During the past month, at what time have you usually gone to bed at night?"
  label(data$psqi_2)="2. During the past month, how long (in minutes) has it usually taken you to fall asleep each night?"
  label(data$psqi_3)="3. During the past month, at what time have you usually gotten up in the morning?"
  label(data$psqi_4)="4. During the past month, how many hours of actual sleep did you get at night? (This may be different than the number of hours you spent in bed.)"
  label(data$psqi_5a)="5a) Cannot get to sleep within 30 minutes"
  label(data$psqi_5b)="5b) Wake up in the middle of the night or early morning"
  label(data$psqi_5c)="5c) Have to get up to use the bathroom"
  label(data$psqi_5d)="5d) Cannot breathe comfortably"
  label(data$psqi_5e)="5e) Cough or snore loudly"
  label(data$psqi_5f)="5f) Feel too cold"
  label(data$psqi_5g)="5g) Feel too hot"
  label(data$psqi_5h)="5h) Had bad dreams"
  label(data$psqi_5i)="5i) Have pain"
  label(data$psqi_5other)="5j) Other reason(s), please describe"
  label(data$psqi_5othera)="How often during the past month have you had trouble sleeping because of this?"
  label(data$psqi_6)="6. During the past month, how would you rate your sleep quality overall?"
  label(data$psqi_7)="7. During the past month, how often have you taken medicine to help you sleep (prescribed or over the counter)?"
  label(data$psqi_8)="8. During the past month, how often have you had trouble staying awake while driving, eating meals, or engaging in social activity?"
  label(data$psqi_9)="9. During the past month, how much of a problem has it been for you to keep up enough enthusiasm to get things done?"
  label(data$psqi_10)="10. Do you have a bed partner or room mate?"
  label(data$psqi_10a)="10a) Loud snoring"
  label(data$psqi_10b)="10b) Long pauses between breaths while asleep"
  label(data$psqi_10c)="10c) Legs twitching or jerking while you sleep"
  label(data$psqi_10d)="10d) Episodes of disorientation or confusion during sleep"
  label(data$psqi_10e)="10e) Other restlessness while you sleep; please describe"
  label(data$psqi_10e1)="psqi_10e1"
  label(data$psqi_complete)="Complete?"
  label(data$mumctq_nr_workdays)="Normally, I work ___ days / week:"
  label(data$mumctq_fall_sleep_work)="On workdays, I normally fall asleep at:"
  label(data$mumctq_wake_up_work)="On workdays, I normally wake up at:"
  label(data$mumctq_fall_sleep_free)="On work-free days, when I DONT use an alarm clock, I normally fall asleep at:"
  label(data$mumctq_wake_up_free)="On work-free days, when I DONT use an alarm clock, I normally wake up at:"
  label(data$mumctq_alarm_free_days)="On MOST work-free days, do you use an alarm clock?"
  label(data$mumctq_complete)="Complete?"
  label(data$age)="Your age (in years)"
  label(data$sex)="Your sex assigned at birth"
  label(data$gender)="Your gender identity"
  label(data$handedness)="Your handedness"
  label(data$education)="Your level of education"
  label(data$demographics_complete)="Complete?"
  
  # Return formatted dataset as a dataframe
  return(data)

}




# Function: score_uMCTQ --------------------------------------------------------------------------------------------------
# Compute the chronotype based on uMCTQ answers.
# Based on a script by Nik Novik and mctq package documentation.
# Vartanian, D. (2023). {mctq}: tools to process the Munich ChronoType Questionnaire (MCTQ). R package version 
# 0.3.2.9000. https://docs.ropensci.org/mctq/

## INPUT

# data : dataframe [n_variables,2]
#   Output of load_redcap

## OUTPUT

# return : hms
#   Corrected time of mid-sleep on work-free days (MSF_SC)

score_uMCTQ <- function(data) {
  
  ## Format data
  # Get the subset of the dataframe with uMCTQ variables
  data_uMCTQ = data[2,grepl("mumctq",colnames(data))]
  
  # Turn nr. of workdays into an integer
  data_uMCTQ$mumctq_nr_workdays = as.integer(data_uMCTQ$mumctq_nr_workdays)
  
  # Remove 'complete' variable
  data_uMCTQ = data_uMCTQ[1:6]
  
  # Transform date variables into hms objects
  for (var in colnames(data_uMCTQ[2:5])) {
    data_uMCTQ[,var] = hms::parse_hm(data_uMCTQ[,var])
  }
  
  ## Compute variables
  # Sleep duration on workdays
  data_uMCTQ$sd_w = mctq::sdu(data_uMCTQ$mumctq_fall_sleep_work, data_uMCTQ$mumctq_wake_up_work)
  # Sleep duration on free days
  data_uMCTQ$sd_f = mctq::sdu(data_uMCTQ$mumctq_fall_sleep_free, data_uMCTQ$mumctq_wake_up_free)
  
  # Local time of mid_sleep: workdays
  data_uMCTQ$ms_w = mctq::msl(data_uMCTQ$mumctq_fall_sleep_work, data_uMCTQ$sd_w)
  # Local time of mid_sleep: free days
  data_uMCTQ$ms_f = mctq::msl(data_uMCTQ$mumctq_fall_sleep_free, data_uMCTQ$sd_f)
  
  # Average weekly sleep duration
  data_uMCTQ$sd_week = mctq::sd_week(data_uMCTQ$sd_w, data_uMCTQ$sd_f, data_uMCTQ$mumctq_nr_workdays)
  
  # Alarm use on free days as a logical variable
  if (data_uMCTQ$mumctq_alarm_free_days == 0) {
    data_uMCTQ$mumctq_alarm_free_days = FALSE
  } else {
    data_uMCTQ$mumctq_alarm_free_days = TRUE
  }
  
  # Chronotype (or: corrected local time of mid-sleep on work-free days)
  data_uMCTQ$msf_sc = mctq::msf_sc(data_uMCTQ$ms_f, data_uMCTQ$sd_w, data_uMCTQ$sd_f, data_uMCTQ$sd_week, data_uMCTQ$mumctq_alarm_free_days)
  
  
  ## Return output variable: MSF_SC
  return(data_uMCTQ$msf_sc)
  
}





# Function: score_PSQI -------------------------------------------------------------------------------------------
# Compute the subscales and final score of the Pittsburgh Sleep Quality Index (PSQI)

## INPUT

# data : dataframe [n_variables,2]
#   Output of load_redcap

## OUTPUT

# PSQI_score : int
#   Total PSQI score

score_PSQI <- function(data) {
  
  # Get the subset of the dataframe with PSQI variables
  data_PSQI = data[2,grepl("psqi",colnames(data))]
  
  
  ## Sleep duration
  # Convert points
  if (data_PSQI$psqi_4 > 6) {
    data_PSQI$durat = 0
  } else if (data_PSQI$psqi_4 < 7 & data_PSQI$psqi_4 > 5) {
    data_PSQI$durat = 1
  } else if (data_PSQI$psqi_4 < 6 & data_PSQI$psqi_4 > 4) {
    data_PSQI$durat = 2
  } else if (data_PSQI$psqi_4 < 5) {
    data_PSQI$durat = 3
  }
  
  
  ## Sleep disturbance
  # Sum of questions between Q5b and Q5i
  q5_sum = sum(data_PSQI[6:13])
  # If 'other' question is not NA, add point from 'othera'
  if (is.na(data_PSQI$psqi_5other) == FALSE) {
    q5_sum = q5_sum + data_PSQI$psqi_5othera
  }
  
  # Convert points
  if (q5_sum == 0) {
    data_PSQI$distb = 0
  } else if (q5_sum > 0 & q5_sum < 10) {
    data_PSQI$distb = 1
  } else if (q5_sum > 9 & q5_sum < 19) {
    data_PSQI$distb = 2
  } else if (q5_sum > 18) {
    data_PSQI$distb = 3
  }    
  
  
  ## Sleep latency
  # Recode Q2
  if (data_PSQI$psqi_2 < 16) {
    q2_new = 0
  } else if (data_PSQI$psqi_2 > 15 & data_PSQI$psqi_2 < 31) {
    q2_new = 1
  } else if (data_PSQI$psqi_2 > 30 & data_PSQI$psqi_2 < 61) {
    q2_new = 2
  } else if (data_PSQI$psqi_2 > 60) {
    q2_new = 3
  }
  # Add to Q5a
  q2q5a = q2_new + data_PSQI$psqi_5a
  
  # Convert points
  if (q2q5a == 0) {
    data_PSQI$laten = 0
  } else if (q2q5a > 0 & q2q5a < 3) {
    data_PSQI$laten = 1
  } else if (q2q5a > 2 & q2q5a < 5) {
    data_PSQI$laten = 2
  } else if (q2q5a > 4) {
    data_PSQI$laten = 3
  } 
  
  
  ## Day dysfunction due to sleepiness
  # Sum of Q8 and Q9
  q8q9 = data_PSQI$psqi_8 + data_PSQI$psqi_9
  
  # Convert points
  if (q8q9 == 0) {
    data_PSQI$daydis = 0
  } else if (q8q9 > 0 & q8q9 < 3) {
    data_PSQI$daydis = 1
  } else if (q8q9 > 2 & q8q9 < 5) {
    data_PSQI$daydis = 2
  } else if (q8q9 > 4) {
    data_PSQI$daydis = 3
  }
  
  
  ## Sleep efficiency
  # Difference in seconds between getting in and out of bed
  diffsec = strptime(data_PSQI$psqi_3, format = "%H:%M") - strptime(data_PSQI$psqi_1, format = "%H:%M")
  # Absolute value of diffsec / 3600
  diffhour = as.integer(diffsec[1]) / 3600
  # Correct for day transition, as in scoring instructions
  if (diffhour > 24) {
    newtib = diffhour - 24
  } else {
    newtib = diffhour
  }
  # Calculate sleep efficiency
  tmphse = (data_PSQI$psqi_4 / newtib) * 100
  
  # Convert points
  if (tmphse > 84) {
    data_PSQI$hse = 0
  } else if (tmphse > 74 & tmphse < 85) {
    data_PSQI$hse = 1
  } else if (tmphse > 64 & tmphse < 75) {
    data_PSQI$hse = 2
  } else if (tmphse < 65) {
    data_PSQI$hse = 3
  }
  
  
  ## Sleep quality
  # Equivalent to question 6
  data_PSQI$slpqual = data_PSQI$psqi_6
  
  
  ## Need meds to sleep
  # Equivalent to question 7
  data_PSQI$meds = data_PSQI$psqi_7
  
  
  ## Total score
  PSQI_score = data_PSQI$durat + data_PSQI$distb + data_PSQI$laten + data_PSQI$daydis + data_PSQI$hse + data_PSQI$slpqual + data_PSQI$meds
  
  return(PSQI_score)
}



# Function: check_data -------------------------------------------------------------------------------------------
# Perform a data check specific to the input parameter (NA values, consent, or 'maybe' answers)

## INPUT

# data : dataframe [n_variables,2]
#   Output of load_redcap

# check : str
#   String specifying which parameter to check: 'NA_values', 'consent', or 'cutoff_extra'

## OUTPUT

# None; prints results to the console

check_data <- function(data,check) {
  
  # Columns that can have NA: cutoff_[...]_extra, exclusion_confirm, psqi_5other/a, psqi_10[a-e1]
  ok_na = c("cutoff_neuro_extra","cutoff_substances_extra","cutoff_sleep_extra","cutoff_psych_extra","exclusion_confirm",
            "psqi_5other","psqi_5othera","psqi_10a","psqi_10b","psqi_10c","psqi_10d","psqi_10e","psqi_10e1")
  
  
  ## Data check for NA values
  if (check == 'NA_values') {
    
    # Columns with NA in this dataset
    data_na = names(which(sapply(data, anyNA)))
    
    # If any NA values are not in the OK list, print them
    if (any(data_na[!(data_na %in% ok_na)])) {
      cat("\nWARNING: columns with NA values")
      data_na[!(data_na %in% ok_na)]
    } else {
      cat("\nNo unintended NA values")
    }
    
  }
  
  
  ## Data check for consent
  if (check == 'consent') {
    
    if (data$volunteer[2] != 1) {
      cat("\nERROR - consent not granted!")
    } else {
      cat("\nConsent OK")
    }
    
  }
  
  
  ## Data check for cutoff questions answered with 'maybe'
  if (check == 'cutoff_extra') {
    
    cat("\nCutoff extra info columns:\n")
    data[1,ok_na[1:4]]
    
  }
  
}



# Function: check_score -------------------------------------------------------------------------------------------
# Perform a data check specific to the input parameter (NA values, consent, or 'maybe' answers)

## INPUT

# score : int or hms
#   The sum score of AUDIT, uMCTQ or PSQI

# check : str
#   String specifying which score to check: 'AUDIT', 'uMCTQ', or 'PSQI'

## OUTPUT

# None; prints results to the console

check_score <- function(score,check) {
  
  ## Score check for AUDIT
  if (check == 'AUDIT') {
    
    # If AUDIT score is above 15, issue a warning
    if (score < 16) {
      cat("\nAUDIT score OK:", score)
    } else {
      cat("\nWARNING: AUDIT score above threshold!")
    }
    
  }
  
  
  ## Score check for uMCTQ
  if (check == 'uMCTQ') {
    
    # If corrected midsleep time is below 01:30 or above 06:00, issue a warning
    if (as.ITime(score) >= as.ITime("01:30:00") & as.ITime(score) <= as.ITime("06:00:00")) {
      cat("\nMidsleep time OK:", as.character(score))
    } else {
      cat("\nWARNING: Midsleep time outside normal range!", as.character(score))
    }
    
  }
  
  
  ## Score check for PSQI
  if (check == 'PSQI') {
    
    # If total score is higher than 4, issue a warning
    if (score < 5) {
      cat("\nPSQI score OK:", score)
    } else {
      cat("\nWARNING: PSQI score above threshold!", score)
    }
    
  }
  
}


