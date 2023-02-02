# -*- coding: utf-8 -*-
"""
Power analysis for Sleep-SSVEP-Study, simulation-based.

Analysis method: paired permutation tests.

Outcome variable: FFT value at 40 Hz.

Procedure per combination:
1. For a given sample size, generate data which
    a) is a realistic representation of the expected data;
    b) has the effect size baked in (group means & standard deviations).
2. Perform a permutation test and record whether a significant effect was detected.
3. The power is the proportion of the iterations which detected a significant effect.
4. Generate the plot(s).

Script variables:
- sample sizes
- standard deviations
- control & experimental group means (-> effect sizes)
- nr. of repetitions per combination
- alpha, beta

"""

#%% Libraries & functions

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import truncnorm
from math import sqrt
import time

from paired_permutation_test import paired_permutation_test # custom function for paired samples permutation

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

## Enter data values based on pilot data

# Keeping mean of control group constant, not 0 but low
gen_mean_con = 10
# Plausible values for experimental group mean (based on previous pilot data)
gen_mean_exp = [20,30,40,50,60,70,80,90,100]
# Plausible values for standard deviation, same for both groups
gen_sd = [20,35,50,65]


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
plt.title('Effect sizes by group means & standard deviations', size=30, y=1.03)
plt.xlabel('Mean_exp - Mean_con', size=20)
plt.xticks(size=15)
plt.ylabel('Cohens d', size=20)
plt.yticks(size=15)

for k in range(len(gen_sd)):
    
    # Get current sd
    sd = gen_sd[k] 
        
    # Plot relation between the group mean difference and effect size, at this sd value
    plt.plot(all_gen_effects[all_gen_effects[:,0] == sd,1]-gen_mean_con, all_gen_effects[all_gen_effects[:,0] == sd,2], label='sd = '+str(sd), linewidth=4) 

plt.legend(fontsize=20, loc = 'lower right')



#%% Plot random sample drawn from one combination as histogram (just for visualization)

# Example: sd=45, n=20, range=[0;150] (truncated normal distribution since values <0 don't make sense)
exp_sample_1 = truncnorm.rvs(a=0, b=150, loc=60, scale=45, size=20, random_state=rng) # mean_exp = 60
con_sample_1 = truncnorm.rvs(a=0, b=150, loc=10, scale=45, size=20, random_state=rng) # mean_con = 10

plt.figure()
plt.hist(exp_sample_1, histtype='step')
plt.hist(con_sample_1, histtype='step')



#%% Simulation parameters

# Sample sizes: values deemed plausible based on available resources
sample_sizes = [10, 15, 20, 25]

# Nr. of repetitions per combination
n_repetitions = 1000

# Significance threshold (alpha)
sig = 0.05 # can be changed e.g. in the case of multiple testing

# Desired power level (1-beta)
aim_pow = 0.8 # conventional level or customized

# Get nr. of cases to test per parameter
n_sd = len(gen_sd) # standard deviations
n_effect = len(gen_mean_exp) # effect sizes (same nr. as group means)
n_sample = len(sample_sizes) # sample sizes



#%% Power simulation looping over all parameters
 
# Matrix to store results from each combination (4 columns to input standard deviation, effect size, sample size, power for each iteration)
n_combinations = n_sd * n_effect * n_sample
results = np.zeros((n_combinations,4))

# Combination counter to fill matrix over all loops
combi_ctr = 0

# Start time of simulation
start_time = time.time()

## Loop that iterates over standard deviation values
for i in range(n_sd):
        
    # Select standard deviation value for this iteration
    sd = gen_sd[i]
    
    # Effect sizes: values calculated from generated data
    effect_sizes = all_gen_effects[all_gen_effects[:,0] == sd, 2]
    
    # Experimental group means: values corresponding to effect sizes
    exp_means = all_gen_effects[all_gen_effects[:,0] == sd, 1]
    
    
    ## Loop that iterates over effect sizes / group means
    for j in range(n_effect):
        
        # Select effect size for this iteration
        d = effect_sizes[j] 
        
        # Select group mean for this iteration
        mean_exp = exp_means[j]
        
        
        ## Loop that iterates over sample sizes
        for k in range(n_sample):
            
            # Select sample size for this iteration
            n = sample_sizes[k]
                        
            # Initialize array of p-values for repetitions
            arr_p_values = np.zeros(n_repetitions)  
            
            
            ## Loop that iterates over number of desired repetitions
            for l in range(n_repetitions):         
    
                # Simulate experimental data (drawn from normal distribution)
                sim_exp_data = rng.normal(loc=mean_exp, scale=sd, size=n)
                
                # Simulate control data (drawn from normal distribution)
                sim_con_data = rng.normal(loc=gen_mean_con, scale=sd, size=n)
        
                # Run permutation test with 100 iterations
                p_value = paired_permutation_test(sim_exp_data, sim_con_data, 100, rng)
    
                # Store this iteration's p-value
                arr_p_values[l] = p_value
                
                
            ## When all repetitions for the present combination are done:
                
            # Get the number of simulations where the null hypothesis was rejected
            n_rej = np.sum(arr_p_values < sig)
            
            # Compute the probability of null hypothesis rejection under these circumstances
            prob_rej = n_rej / n_repetitions
            
            # Store the outputs in the results matrix
            results[combi_ctr,0] = sd # Col 0: standard deviation
            results[combi_ctr,1] = d # Col 1: effect size
            results[combi_ctr,2] = n # Col 2: sample size
            results[combi_ctr,3] = prob_rej # Col 3: power
            
            # Increase ctr, move to next combination
            combi_ctr += 1
            
            # Print counter to keep track of algorithm progress
            print('Progress: ' + str(combi_ctr) + '/' + str(n_combinations))
    
   
# End time of simulation
end_time = time.time()
# Total time in minutes
total_time = round((end_time - start_time) / 60, 2)
print('Execution time of simulation loop (' + str(n_combinations) + ' combinations X ' + str(n_repetitions) + ' repetitions): \n' + str(total_time) + ' min')


    
#%% Plot power curves

# Open figure, ensure the plots are evenly spaced apart
plt.figure(layout="constrained")

# 4 subplots, divided by sd
for subplot in range(n_sd):
    
    # Get sd value for current plot
    sd_plot = gen_sd[subplot]
    
    # Subplot aesthetics
    plt.subplot(2,2,subplot+1) # +1 since plt.subplot starts at 1    
    plt.title('Power Curves: σ = ' + str(sd_plot), size=30, y=1.03)
    plt.xlabel('Effect size (d)', size=20)
    plt.xticks(size=15)
    plt.ylabel('Power (1-ß)', size=20)
    plt.yticks(size=15)

    # Get subset of results related to current sd value
    results_subset = results[results[:,0] == sd_plot]

    # Iterate over sample sizes, plot each one
    for s in range(n_sample):
        
        # Get current sample size within subplot
        n_plot = sample_sizes[s] 
        
        # Get effect sizes and power values for this sample size
        subset_sample = results_subset[results_subset[:,2] == n_plot]
        # Sort by effect size
        subset_sample = subset_sample[subset_sample[:, 1].argsort()] # else line plot gets the order wrong
        
        # Plot curve for this sample size: x-axis = effect size, y-axis = power, label = n        
        plt.plot(subset_sample[:,1], subset_sample[:,3], label='n = '+str(n_plot), linewidth=4) # plot result
    
    # Add line for desired power cut-off
    plt.axhline(y = aim_pow, color = 'gray', linestyle = '--')
    # Add legend
    plt.legend(fontsize=20, loc = 'lower right')
        
