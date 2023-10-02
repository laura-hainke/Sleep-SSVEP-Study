# Author: LH
# Date: 2023-09-24
# Functionality: Functions for statistics_main.R, statistical tests
# Notes:



# Environment Setup ----------------------------------------------------------------------------------------------------

library("ez")



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

