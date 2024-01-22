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
library(superb)



# Function: check_normality -------------------------------------------------------------------------------------------
# Evaluate parametric test assumption of distribution normality, via visual inspection & statistical test.

## INPUT

# data_vector : vector
# Paired observation scores differences (for t-test) or scores of one cell of the design (for ANOVA)

check_normality <- function(data_vector) {
  
  # Visual inspection
  hist(data_vector)
  
  # Shapiro-Wilk test
  results_shapiro = shapiro.test(data_vector)
  shapiro_p_value = results_shapiro$p.value
  
  if (shapiro_p_value < 0.05){
    print("Assumption of normality violated: Shapiro-Wilk test significant")
  } else {
    print("Assumption of normality OK: Shapiro-Wilk test not significant")
  }

}



# Function: check_outliers ------------------------------------------------------------------------------------------------------------
# Check if there are any outliers in the data.

## INPUT

# data_vector : vector

check_outliers <- function(data_vector){
  
  # Visual inspection
  boxplot(data_vector)
  mtext(paste("Outliers: ", paste(boxplot.stats(data_vector)$out, collapse = ", ")))
  
  # Print data points below or above 3 standard deviations
  z_scores = scale(data_vector)
  
  idx_lower = which(z_scores < -3)
  print("Data points < -3 SD: Subject(s)")
  print(list_IDs[idx_lower])
  
  idx_upper = which(z_scores > 3)
  print("Data points > 3 SD: Subject(s)")
  print(list_IDs[idx_upper])
}



# Function: check_sphericity ------------------------------------------------------------------------------------------------
# Evaluate test assumption of sphericity (equal variances of the differences between all combinations of related groups)

## INPUT

# data_wide : dataframe
# Dataframe in wide format containing all cells of the design


check_sphericity <- function(data_wide){
  
  result_mauchly = MauchlySphericityTest(data_wide)
  
  if (result_mauchly < 0.05){
    print("Assumption of sphericity violated: Mauchly test significant")
  } else {
    print("Assumption of sphericity OK: Mauchly test not significant")
  }
  
}



# Function: test_two_levels -----------------------------------------------------------------------------------------------
# Statistical test of a two-level factor, repeated measures (t-test or wilcox test).

## INPUT

# data_level1 : vector
# Values for independent variable level 1

# data_level2 : vector
# Values for independent variable level 2

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

test_two_levels <- function(data_level1, data_level2, parametric, alternative) {
  
  # Run paired test & calculate effect size
  if (parametric == TRUE){
    
    cat("RESULTS: PAIRED T-TEST\n")

    results = t.test(x=data_level1, y=data_level2, paired=TRUE, alternative=alternative, conf.level=0.95)
    effect = repeated_measures_d(x=data_level1, y=data_level2, method="z") # Cohen's d standardized by difference score variance
    effect_size = effect$d_z
    
  } else {
    
    cat("RESULTS: PAIRED WILCOXON SIGNED RANK TEST\n")
    
    results = wilcox.test(x=data_level1, y=data_level2, paired=TRUE, alternative=alternative, conf.int=TRUE, conf.level=0.95)     
    effect = rank_biserial(x=data_level1, y=data_level2, paired=TRUE, alternative=alternative, ci=0.95) # rank-biserial correlation
    effect_size = effect$r_rank_biserial
    
  }
  
  p_value = results$p.value
  cat("\nP-value:",p_value,"\n")
  
  cat("\nEffect size:\n")
  print(effect)

  # return(list(p_value, effect_size, confidence_interval[1], confidence_interval[2]))
  
}



# Function: test_multiple_levels ---------------------------------------
# Statistical test of a factor with multiple levels, repeated measures (rmANOVA or Friedman ANOVA).

## INPUT

# data_ID_factor_value : dataframe 
# Long format; column 1 = subject IDs, column 2 = independent variable, column 3 = dependent variable

# parametric : bool
# Indicate if the test should be parametric (TRUE for rmANOVA) or not (FALSE for Friedman ANOVA).

# sphericity_correction : chr
# If a sphericity correction is to be applied, specify "greenhouse-geisser"; else, specify "none"

## OUTPUT

# results : list
# Test result parameters

# effect_size : float
# Test effect size (partial eta-squared or kendall's w)

# post_hoc_tests : list
# Results of the pairwise post-hoc tests on factor levels

test_multiple_levels <- function(data_ID_factor_value, parametric, sphericity_correction) {
  
  # Change column names for formula format
  colnames(data_ID_factor_value) = c("ID","factor","value")
  
  if (parametric == TRUE){
    
    cat("RESULTS: REPEATED-MEASURES ANOVA\n")
    
    # Model
    results = lme(value~factor, random=~1|ID, data=data_ID_factor_value, method="ML") 
    
    # Table for interpretation of results
    anova_table = Anova(results, type="III", correction=sphericity_correction) 
    
    p_value = anova_table["factor","Pr(>Chisq)"]
    cat("\nP-value:",p_value,"\n\n")
    
    effect = eta_squared(results, partial=TRUE) # Partial eta-squared
    effect_size = effect$Eta2_partial
    
    print(effect[,2:4]) # ignore first column

    post_hoc_tests = pairwise.t.test(data_ID_factor_value$value, data_ID_factor_value$factor, alternative=c("two.sided"), p.adj="bonf")
  
  } else {
    
    cat("RESULTS: FRIEDMAN TEST\n")
    
    # Model
    results = friedman.test(value~factor|ID, data=data_ID_factor_value)
    
    p_value = results$p.value
    cat("\nP-value:",p_value,"\n\n")
    
    effect = kendalls_w(value~factor|ID, data=data_ID_factor_value) # Kendall's W
    effect_size = effect$Kendalls_W
    
    print(effect)
    
    post_hoc_tests = pairwise.wilcox.test(data_ID_factor_value$value, data_ID_factor_value$factor, alternative=c("two.sided"), p.adj = "bonf")
  }
  
  cat("\n\nBonferroni-corrected post-hoc tests:\n")
  print(post_hoc_tests$p.value)
  
  # return(list(results, effect_size, post_hoc_tests))
}




