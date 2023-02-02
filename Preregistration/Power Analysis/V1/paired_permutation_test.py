# -*- coding: utf-8 -*-
"""
Run paired permutation test. 2 samples per subject (experimental vs. control condition)

Assumption: both conditions have the same amount of cases

"""

import numpy as np
from random import choice
import scipy.stats


def paired_permutation_test(exp_condition_values, con_condition_values, n_loops, rng):
    
    ## True comparison of conditions
    
    # Average of values per condition
    avg_exp_condition = exp_condition_values.mean()  # experimental
    avg_con_condition = con_condition_values.mean()  # control
    
    # True difference of means
    true_difference = avg_exp_condition - avg_con_condition
    
    # Number of cases
    nr_subjects = len(exp_condition_values)
    
    
    ## Permutation  
    
    # Empty array to put the shuffled differences into
    average_shuffled_differences = np.zeros([n_loops,]) 
    
    for loop in range(0,n_loops):
        
        # Two temporary arrays to put the shuffled values into
        temp_condition_1 = np.zeros([nr_subjects,]) 
        temp_condition_2 = np.zeros([nr_subjects,])
        
        for subject in range(0,nr_subjects): # loop through each subject
            
            # For each subject, either keep the correct labels, or swap the conditions (50 % chance)
            decide = rng.choice(['yes', 'no'])  
            
            if decide == 'yes':
                
                temp_condition_1[subject] = exp_condition_values[subject] # keep the correct labels
                temp_condition_2[subject] = con_condition_values[subject]
        
            elif decide == 'no':
    
                temp_condition_1[subject] = con_condition_values[subject] # swap the conditions
                temp_condition_2[subject] = exp_condition_values[subject]
    
        # Average the two shuffled conditions
        average_shuffled_differences[loop] = temp_condition_1.mean() - temp_condition_2.mean() 
        
        
    ## Compute & return p-value
    
    Z_score = (true_difference - average_shuffled_differences.mean()) / np.std(average_shuffled_differences)
    
    p_value_one_sided = scipy.stats.norm.sf(abs(Z_score)) 
    
    return p_value_one_sided