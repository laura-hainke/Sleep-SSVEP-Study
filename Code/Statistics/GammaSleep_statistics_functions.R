# Author: LH
# Date: 2023-09-24
# Functionality: Functions for statistics_main.R, running statistical tests
# Notes:



# Environment Setup ----------------------------------------------------------------------------------------------------

library(emmeans)
library(stringr)



# Function: t_test_or_wilcox -----------------------------------------------------------------------------------------------
# Statistical comparison of 2 variables (t-test or wilcox test).

## INPUT

# var1 : vector
# Data for variable 1

# var2 : vector
# Data for variable 2

# parametric : bool
# Indicate if the test should be parametric (TRUE for t-test) or not (FALSE for wilcox test).

# alternative : str
# "greater" for one-sided test, else "two.sided" 

## OUTPUT

# p_value : float
# Test's p-value

# effect_size : float
# Test effect size (cohen's d)

# confidence_interval : float
# Confidence interval for mean appropriate to specified alternative hypothesis

t_test_or_wilcox <- function(var1, var2, parametric, alternative) {

  # Run one-sided, paired test, calculate effect size
  if (parametric == TRUE){
    
    cat("\nT-TEST\n")

    result = t.test(var1, var2, paired = TRUE, alternative = alternative, conf.level=0.95)
    effect_size = (mean(var1) - mean(var2)) / sd(var1)
    
  } else {
    
    cat("\nWILCOX-TEST\n")
    
    result = wilcox.test(var1, var2, paired = TRUE, alternative = alternative, conf.int = TRUE, conf.level = 0.95) 
    effect_size = wilcox_result.statistic / sqrt(length(var1))
    
  }
  
  # Get p-value and confidence interval
  p_value = result$p.value
  confidence_interval = result$conf.int
  
  # Return outputs
  cat("\nP-value:",p_value)
  cat("\nCohen's d:",effect_size)
  cat("\nConfidence interval:",confidence_interval)
  
  return(p_value, effect_size, confidence_interval)
  
}



# Function: test_variable_group ---------------------------------------
# Statistical comparison of a group of variable pairs (rmANOVA or Friedman ANOVA).

## INPUT

# data : dataframe
# Data in long format

# dependent_variable : chr
# Name of the dependent variable column in the dataframe

# factor1 : chr
# Name of the first factor column in the dataframe

# factor2 : chr
# Name of the second factor column in the dataframe


# parametric : bool
# Indicate if the test should be parametric (TRUE for rmANOVA) or not (FALSE for Friedman ANOVA).

## OUTPUT



anova_or_friedman <- function(data, dependent_variable, factor1, factor2, parametric) {
  
  if (parametric == TRUE){
    
    cat("\nREPEATED-MEASURES ANOVA\n")
    
    results = aov(dependent_variable ~ factor1 * factor2 + Error(ID/(factor1*factor2)), data = data)
  
  } else {
    
    cat("\nFRIEDMAN TEST\n")
    
    results = friedman.test(value ~ factor1 * factor2 | ID, data = data)
    
    
  }
  
  summary(results)
  
  # For p-values, confidence intervals, and effect sizes
  em <- emmeans(results, specs = c(factor1,factor2))
  summary(em)
    
}




