# -*- coding: utf-8 -*-
"""
Power analysis for Sleep-SSVEP-Study based on the simulation of effect sizes, sample sizes.

Analysis method: paired permutation tests.

Outcomes:
- SSVEP-PTP
- FFT-P40

Procedure per combination:
1. For a given sample size and effect size, generate data which
    a) is a realistic representation of the data you expect to obtain.
    b) has the effect size baked in.
2. Perform your analysis and record whether a significant effect was detected.
3. The power is the proportion of the iterations which detected a significant effect.
5. Generate the plot(s).

Variables:
- sample size
- effect size
- distribution parameters
    --> SSVEP-PTP_exp: mean = 0.3, SD = 0.1, range = [0,0.6] 
    --> FFT-P40_exp: mean = 30, SD = 10, range = [0,60]

"""

#%% Libraries & functions

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import truncnorm
from math import sqrt

from paired_permutation_test import paired_permutation_test

# Random number generator (seed chosen arbitrarily using random.randint())
rng = np.random.default_rng(seed=66)

# Function to calculate Cohen's d, same sd for both groups
def cohens_d(mean_exp, mean_con, sd):
    
    group_diff = mean_exp - mean_con
    sd_pooled = sqrt(sd**2)
    
    # correction = ((n-3)/(n-2.25)) * sqrt((n-2)/n) # adjustment for small sample sizes, but this requires n
    # d = group_diff * correction / sd_pooled
    
    d = group_diff / sd_pooled
    d = round(d,2)
    
    return d
    


#%% Generate plausible data & plot parameters

# Keeping mean of control group constant, not 0 but low
gen_mean_con = 10
# Plausible values for experimental group mean (based on previous pilot data)
gen_mean_exp = [20,30,40,50,60,70,80,90,100]
# Plausible values for standard deviation, same for both groups
gen_sd = [20,30,40]


## Plot sample drawn from one combination in histogram (example): sd=30, n=20, range=[0;150]
# (truncated normal distribution since values <0 don't make sense)
exp_sample_1 = truncnorm.rvs(a=0, b=150, loc=50, scale=30, size=20, random_state=rng) # mean_exp = 50
con_sample_1 = truncnorm.rvs(a=0, b=150, loc=10, scale=30, size=20, random_state=rng) # mean_con = 10

plt.figure()
plt.hist(exp_sample_1, histtype='step')
plt.hist(con_sample_1, histtype='step')


## Calculate effect sizes from plausible data parameters
# Empty matrix to store results
all_gen_effects = np.zeros((len(gen_mean_exp)*len(gen_sd),3))

# Row counter
ij_ctr = 0

# Calculate effect sizes per combination
for i in range(len(gen_sd)):
    
    for j in range(len(gen_mean_exp)):
        
        gen_effect = cohens_d(gen_mean_exp[j], gen_mean_con, gen_sd[i]) 
        
        all_gen_effects[ij_ctr,0] = gen_sd[i]
        all_gen_effects[ij_ctr,1] = gen_mean_exp[j]
        all_gen_effects[ij_ctr,2] = gen_effect
        
        ij_ctr += 1

## Plot results
plt.figure()
plt.title('Power curves by SD', size=30, y=1.03)
plt.xlabel('Mean_exp - Mean_con', size=20)
plt.xticks(size=15)
plt.ylabel('Cohens d', size=20)
plt.yticks(size=15)

for l in range(len(gen_sd)):
    
    sd = gen_sd[l] # get current sd
    
    idx = list(all_gen_effects[:,0]).index(sd) # get first row in results matrix for this sd value
    
    plt.plot(all_gen_effects[idx:idx+9,1]-gen_mean_con, all_gen_effects[idx:idx+9,2], label='sd = '+str(sd), linewidth=4) # plot relation btw. mean_exp and effect size at this sd value

plt.legend(fontsize=20, loc = 'lower right')



#%% Transform generated data to match sd=1 (dividing by sd) but keeping effect sizes

# Initialize new matrix
all_gen_effects_sd1 = np.zeros((len(gen_mean_exp)*len(gen_sd),3))

all_gen_effects_sd1[:,0] = gen_mean_con / all_gen_effects[:,0] # col 0: transformed control means
all_gen_effects_sd1[:,1] = all_gen_effects[:,1] / all_gen_effects[:,0] # col 1: transformed experimental means

# Sanity check if effect sizes remained the same
for k in range(len(all_gen_effects_sd1)):        
    all_gen_effects_sd1[k,2] = cohens_d(all_gen_effects_sd1[k,1], all_gen_effects_sd1[k,0], 1) # col 2: effect sizes
all_gen_effects[:,2] == all_gen_effects_sd1[:,2]



#%% Simulation parameters

# Sample sizes: values deemed plausible based on available resources
sample_sizes = [10, 15, 20, 25]

# Nr. of repetitions per combination
n_repetitions = 500



#%% Loop over the standard deviation values chosen to generate data

for sd_value in range(len(gen_sd)):
        
    # Effect sizes: values calculated from generated data
    subset = range(sd_value*len(gen_mean_exp):(sd_value*len(gen_mean_exp)+len(gen_mean_exp))
    effect_sizes = all_gen_effects_sd1[,2]
    
    # Nr. of combinations tested
    n_combinations = len(sample_sizes)*len(effect_sizes)
    
    
    #%% Power simulation: normal distribution
    
    # Matrix to store results from each combination (3 columns to input sample size, effect size, p-value)
    norm_dis_results = np.zeros((n_combinations,3))
    
    # Combination counter
    combi_ctr = 0
    
    ### Main loop
    
    ## Loop 1 iterates over sample sizes
    for i in range(len(sample_sizes)): 
        
        # Select sample size for this iteration
        i_sample_size = sample_sizes[i] 
        
        
        ## Loop 2 iterates over effect sizes
        for j in range(len(effect_sizes)): 
            
            # Select effect size for this iteration
            j_effect_size = effect_sizes[j] 
            
            
            ## Loop 3 iterates over number of desired repetitions
            for k in range(n_repetitions):
    
                # Initialize array of p-values            
                arr_p_values = np.zeros(n_repetitions)
    
                # Compute mean of exp_data distribution given the desired effect size and standard deviation
                # -> derived from cohen's d formula, if M2=0: d = (M1-M2)/SDpool
                # mean_exp_data = sd * j_effect_size            
    
                # Simulate experimental data
                sim_exp_data = rng.normal(loc=mean_exp_data, scale=sd, size=i_sample_size)
                
                # Simulate control data
                sim_con_data = rng.normal(loc=0, scale=sd, size=i_sample_size)
        
                # Run permutation test with 100 iterations
                k_p_value = paired_permutation_test(sim_exp_data, sim_con_data, 100, rng)
    
                # Store this iteration's p-value
                arr_p_values[k] = k_p_value
                
                
            ## When all repetitions for the present combination of sample size & effect size are done:
                
            # Get the number of simulations where the null hypothesis was rejected
            n_rej = np.sum(arr_p_values < 0.05)
            
            # Compute the probability of null hypothesis rejection under these circumstances
            prob_rej = n_rej / n_repetitions
            
            # Store the outputs in the results matrix
            norm_dis_results[combi_ctr,0] = int(i_sample_size) # Col 0: sample size
            norm_dis_results[combi_ctr,1] = j_effect_size # Col 1: effect size
            norm_dis_results[combi_ctr,2] = prob_rej # Col 2: power
            
            # Increase ctr, move to next combination
            combi_ctr += 1
    
    
    #%% Plot power curves
    
    ## Plot aesthetics
    
    plt.figure()
    plt.title('Power curves by sample size (normal distribution)', size=30, y=1.03)
    plt.xlabel('Effect size (d)', size=20)
    plt.xticks(size=15)
    plt.ylabel('Power (ß)', size=20)
    plt.yticks(size=15)
    
    ## Plot data
    
    # Turn 1st column of results matrix into list for indexing
    norm_dis_results_col1 = list(norm_dis_results[:,0]) 
    
    # Iterate over sample sizes tested, plot each one
    for l in range(len(sample_sizes)):
        
        n = sample_sizes[l] # get current sample size
        
        idx = norm_dis_results_col1.index(n) # get first row in results matrix for this sample size
        
        plt.plot(norm_dis_results[idx:idx+5,1], norm_dis_results[idx:idx+5,2], label='n = '+str(n), linewidth=4) # plot result
    
    # Add legend
    plt.legend(fontsize=20, loc = 'lower right')
    
    
