# Author: LH
# Date: 2023-09-24
# Functionality: Functions for statistics_main.R, running statistical tests
# Notes:



# Environment Setup ----------------------------------------------------------------------------------------------------

library(emmeans)
library(stringr)
library(effectsize)
library(car)
library(nlme)



# Function: evaluate_shapiro -------------------------------------------------------------------------------------------
# Run and evaluate Shapiro-Wilk test (distribution normality)

## INPUT

# data_vector : vector
# Difference between paired observation scores (for t-test) or between observed values and model prediction, i.e., residuals (for ANOVA)

## OUTPUT

# shapiro_p_value : numeric
# P-value of the Shapiro-Wilk test

evaluate_shapiro <- function(data_vector) {
  
  results_shapiro = shapiro.test(data_vector)
  shapiro_p_value = results_shapiro$p.value
  
  if (shapiro_p_value < 0.05){
    print("Assumption of normality violated: Shapiro-Wilk test significant")
  } else {
    print("Assumption of normality OK: Shapiro-Wilk test not significant")
  }
  
  # return(shapiro_p_value)
}



# Function: evaluate_levene -------------------------------------------------------------------------------------------
# Run and evaluate Levene test (homoscedasticity)

## INPUT

# data_factor_value : dataframe
# Long format; column 1 = independent variable, column 2 = dependent variable

## OUTPUT

# levene_p_value : numeric
# P-value of the Levene test

evaluate_levene <- function(data_factor_value) {
  
  # Change column names for better code readability
  colnames(data_factor_value) = c("factor","value")
  
  # Compute Levene test and extract p-value
  results_levene = leveneTest(data_factor_value$value ~ data_factor_value$factor) 
  levene_p_value = results_levene$"Pr(>F)"[1]
  
  cat("\nLEVENE TEST\n")
  
  if (levene_p_value < 0.05){
    print("Significant = assumption of homoscedasticity violated!")
  } else {
    print("Not significant = assumption of homoscedasticity OK")
  }
  
  # return(levene_p_value)
}



# Function: test_two_levels -----------------------------------------------------------------------------------------------
# Statistical test of a two-level factor, repeated measures (t-test or wilcox test).

## INPUT

# data_level1_level2 : dataframe
# Data in wide format; column 1 = values for independent variable level 1, column 2 = values for independent variable level 2

# parametric : bool
# Indicate if the test should be parametric (TRUE for t-test) or not (FALSE for wilcox test).

# alternative : str
# "greater" for one-sided test (level1 > level2), else "two.sided" (level1 =/= level2)

## OUTPUT

# p_value : float
# Test's p-value

# effect_size : float
# Test effect size (cohen's d or r)

# confidence_interval : float
# Confidence interval for difference of means

test_two_levels <- function(data_level1_level2, parametric, alternative) {

  # Change column names for better code readability
  colnames(data_level1_level2) = c("level1","level2")
  
  # Run paired test & calculate effect size
  if (parametric == TRUE){
    
    cat("\nT-TEST\n")

    results = t.test(x=data_level1_level2$level1, y=data_level1_level2$level2, paired=TRUE, alternative=alternative, conf.level=0.95)
    effect = repeated_measures_d(x=data_level1_level2$level1, y=data_level1_level2$level2, method="z") # Difference Score Variance d_z - akin to computing difference scores for each individual and then computing a one-sample Cohen's d
    effect_size = effect$d_z
    
  } else {
    
    cat("\nWILCOX-TEST\n")
    
    results = wilcox.test(x=data_level1_level2$level1, y=data_level1_level2$level2, paired=TRUE, alternative=alternative, conf.int=TRUE, conf.level=0.95)     
    effect = rank_biserial(x=data_level1_level2$level1, y=data_level1_level2$level2, paired=TRUE, alternative=alternative, ci=0.95) # rank-biserial correlation
    effect_size = effect$r_rank_biserial
    
  }
  
  print(results)
  print(effect)
  
  # Get p-value and confidence interval
  p_value = results$p.value
  confidence_interval = results$conf.int
  
  # Return outputs
  # cat("\nP-value:",p_value)
  # cat("\nEffect size:",effect_size)
  # cat("\nConfidence interval:",confidence_interval)
  
  # return(list(p_value, effect_size, confidence_interval))
  
}



# Function: test_multiple_levels ---------------------------------------
# Statistical test of a factor with multiple levels, repeated measures (rmANOVA or Friedman ANOVA).

## INPUT

# data_ID_factor_value : dataframe 
# Long format; column 1 = subject IDs, column 2 = independent variable, column 3 = dependent variable

# parametric : bool
# Indicate if the test should be parametric (TRUE for rmANOVA) or not (FALSE for Friedman ANOVA).

## OUTPUT

# results : list
# Test result parameters

# effect_size : float
# Test effect size (partial eta-squared or kendall's w)

# post_hoc_tests : emmGrid or list
# Results of the pairwise post-hoc tests on factor levels

test_multiple_levels <- function(data_ID_factor_value, parametric) {
  
  # Change column names for formula format
  colnames(data_ID_factor_value) = c("ID","factor","value")
  
  if (parametric == TRUE){
    
    cat("\nREPEATED-MEASURES ANOVA\n")
    
    results = lme(value~factor, random=~1|ID/factor, data=data_ID_factor_value, method="ML") # using LME to ignore any sphericity deviations
    effect = eta_squared(results, partial=TRUE) # Partial eta-squared
    effect_size = effect$Eta2_partial
    
    post_hoc_em = emmeans(results, "factor", data=data_ID_factor_value)
    post_hoc_tests = pairs(post_hoc_em, adjust="tukey")
    
    summary(results) # more readable
  
  } else {
    
    cat("\nFRIEDMAN TEST\n")
    
    results = friedman.test(value~factor|ID, data=data_ID_factor_value)
    effect = kendalls_w(value~factor|ID, data=data_ID_factor_value) # Kendall's W
    effect_size = effect$Kendalls_W
    
    post_hoc_tests = pairwise.wilcox.test(data_ID_factor_value$value, data_ID_factor_value$factor, p.adj = "bonf")
    
    print(results) # summary() does not work for friedman test
    
  }
  
  # Display test results
  print(effect)
  print(post_hoc_tests)
  
  # return(list(results, effect_size, post_hoc_tests))
}




