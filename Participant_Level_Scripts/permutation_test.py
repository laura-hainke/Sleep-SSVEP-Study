#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Step 6 - Statistical test between 2 conditions using permutation (within participant)

"""


# =============================================================================
# Inputs:
#   - condition_1_segments, condition_2_segments: 1 matrix per condition with all segments assigned to it
#   - data_type: 'SSVEP' (default) or 'FFT', to correctly calculate averages
#   - num_loops: nr. of repetitions for the permutation, default = 1000

# Outputs (z-score, p-value) are printed to the console
# =============================================================================


### Libraries
import numpy as np
from random import choice, seed
import scipy.stats


def permutation_test(condition_1_segments, condition_2_segments, data_type = 'SSVEP', num_loops = 1000):    
    
    # Set seed to replicate results
    seed(1)
    
    # Match number of values of the 2 conditions by shortening the longer array at the end
    n_trial_diff = np.shape(condition_1_segments)[0] - np.shape(condition_2_segments)[0]
    
    if n_trial_diff > 0: # if cond 1 has more trials    
        condition_1_segments = condition_1_segments[0:-n_trial_diff,:]
    elif n_trial_diff < 0: # if cond 2 has more trials    
        condition_2_segments = condition_2_segments[0:-abs(n_trial_diff),:]
    
    # Get nr of trials
    n_trials =  np.shape(condition_1_segments)[0] 
    print('Nr. of trials: ' + str(n_trials))
    
    
    ### Permutation of conditions (within subject)
    
    ## True difference between conditions: SSVEP / FFT
    
    # Average of the segments from the first condition
    average_condition_1 = condition_1_segments.mean(axis=0) 
    # Baseline correct
    average_condition_1 = average_condition_1 - average_condition_1.mean()
    
    # Average of the segments from the second condition
    average_condition_2 = condition_2_segments.mean(axis=0) 
    # Baseline correct
    average_condition_2 = average_condition_2 - average_condition_2.mean()
    
    if data_type == 'SSVEP':
        
        p2p_condition_1 = np.ptp(average_condition_1)
        print('Mean PTP condition 1: ' + str(p2p_condition_1))
        p2p_condition_2 = np.ptp(average_condition_2)
        print('Mean PTP condition 2: ' + str(p2p_condition_2))
        # Real difference of means
        true_difference = p2p_condition_1 - p2p_condition_2
        print('True difference: ' + str(true_difference))
        # Duration of segments (1 kHz sampling rate, 40 Hz flicker)
        period = 25
    
    elif data_type == 'FFT': # this assumes the FFT was run on 10 sec segments, hence 400, not 40
        fft_p40_condition_1 = average_condition_1[400]
        print('Mean P40 condition 1: ' + str(fft_p40_condition_1))
        fft_p40_condition_2 = average_condition_2[400]
        print('Mean P40 condition 2: ' + str(fft_p40_condition_2))
        # Real difference of means
        true_difference = fft_p40_condition_1 - fft_p40_condition_2
        print('True difference: ' + str(true_difference))
        # Duration of segments (1 kHz sampling rate, 10 sec segments)
        period = 10000
    
           
        
    ## Permutated difference between conditions
    
    average_shuffled_differences = np.zeros([num_loops,]) # empty array to put the shuffled differences into
    
    for loop in range(0,num_loops):
        
        # two temporary arrays, to put the shuffled segments into
        temp_condition_1 = np.zeros([n_trials,period]) 
        temp_condition_2 = np.zeros([n_trials,period])
        
        for trial in range(0,n_trials): # loop over all segments
            
            decide = choice(['yes', 'no'])  # for each trial, decide to either keep the correct labels, or swap the conditions. 50% chance
            
            if decide == 'yes':
                
                temp_condition_1[trial,:] = condition_1_segments[trial,:] # keep the correct labels
                temp_condition_2[trial,:] = condition_2_segments[trial,:]
        
            elif decide == 'no':
    
                temp_condition_1[trial,:] = condition_2_segments[trial,:] # swap the conditions
                temp_condition_2[trial,:] = condition_1_segments[trial,:]
    
    
        random_average_1 = temp_condition_1.mean(0)
        random_average_2 = temp_condition_2.mean(0)
            
        if data_type == 'SSVEP':

            amplitude_1 = np.ptp(random_average_1)
            amplitude_2 = np.ptp(random_average_2)
    
            difference = amplitude_1 - amplitude_2    
            average_shuffled_differences[loop] = difference
            
        elif data_type == 'FFT':
            
            amplitude_1 = random_average_1[400]
            amplitude_2 = random_average_2[400]
    
            difference = amplitude_1 - amplitude_2    
            average_shuffled_differences[loop] = difference
            
            
  
    ### Statistical comparison of the 2 conditions
    
    # Calculate Z score
    Z_score = (true_difference - average_shuffled_differences.mean()) / np.std(average_shuffled_differences) 
    
    print('Shuffled difference: ' + str(average_shuffled_differences.mean()))
    print('SD shuffled differences: ' + str(np.std(average_shuffled_differences)))
    
    print('Z score = ' + str(np.round(Z_score,2)))
    
    # Convert into p-value
    p_value_one_sided = scipy.stats.norm.sf(Z_score) #one-sided
    
    print('p = ' + str(np.round(p_value_one_sided,5)))
    

          
          
    
         

     