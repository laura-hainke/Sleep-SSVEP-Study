# -*- coding: utf-8 -*-
"""
Power analysis for Sleep-SSVEP-Study, simulation-based.

Analysis method: paired t-tests.

Outcome variable: FFT value at 40 Hz.

Procedure per combination:
1. For a given sample size, generate data which
    a) is a realistic representation of the expected data;
    b) has the effect size baked in.
2. Perform the statistical test and record whether a significant effect was detected.
3. The power is the proportion of the iterations which detected a significant effect.
4. Generate the plot(s).

Script variables:
- sample sizes
- effect sizes (based on control & experimental group means, standard deviation)
- nr. of repetitions per combination
- alpha, beta

"""

#%% Libraries & functions

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from math import sqrt
import time

# Random number generator (random seed chosen using random.randint())
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
# Plausible standard deviation value -> only one, since it is cancelled out in cohen's d formula; 
# Choosing medium-large value in relation to experimental group means to cover a large range of effect sizes
gen_sd = 50
# Plausible values for experimental group mean (based on previous pilot data)
gen_mean_exp = np.arange(start=15, stop=90, step=5, dtype = int)


## Calculate effect sizes from plausible data parameters

# Empty matrix to store results
gen_effects = np.zeros((len(gen_mean_exp),2))

# Calculate effect sizes per experimental mean value
for i in range(len(gen_mean_exp)):
    
    effect = cohens_d(gen_mean_exp[i], gen_mean_con, gen_sd) 
    
    gen_effects[i,0] = gen_mean_exp[i]
    gen_effects[i,1] = effect
    

## Plot linear relation between the group mean difference and effect size
plt.figure()
plt.title('Effect size by group mean difference', size=30, y=1.03)

plt.xlabel('Mean_exp - Mean_con', size=20)
plt.xticks(size=15)
plt.ylabel('Cohens d', size=20)
plt.yticks(size=15)
        
plt.plot(gen_effects[:,0]-gen_mean_con, gen_effects[:,1], linewidth=4) 



#%% Plot random sample drawn from one combination as histogram (just for visualization)

# Example: sd=50, n=20, range=[0;150] (truncated normal distribution since values <0 don't make sense)
exp_sample_1 = stats.truncnorm.rvs(a=0, b=150, loc=35, scale=50, size=20, random_state=rng) # mean_exp = 35
con_sample_1 = stats.truncnorm.rvs(a=0, b=150, loc=10, scale=50, size=20, random_state=rng) # mean_con = 10

plt.figure()
plt.hist(exp_sample_1, histtype='step')
plt.hist(con_sample_1, histtype='step')



#%% Simulation parameters

# Sample sizes: values deemed plausible based on available resources
sample_sizes = [15, 20, 25, 30]

# Nr. of repetitions per combination
n_repetitions = 1000

# Significance threshold (alpha)
sig = 0.05 # can be changed e.g. in the case of multiple testing

# Desired power level (1-beta)
aim_pow = 0.8 # conventional level or customized

# Get nr. of cases to test per parameter
n_effect = len(gen_mean_exp) # effect sizes (same nr. as group means)
n_sample = len(sample_sizes) # sample sizes

# Statistic test: pairwise t-test 't-test' / Wilcoxon signed rank 'wilcox'
stat_test = 't-test'



#%% Power simulation looping over all parameters
 
# Matrix to store results from each combination (3 columns to input effect size, sample size, power for each iteration)
n_combinations = n_effect * n_sample
results = np.zeros((n_combinations,3))

# Combination counter to fill matrix over all loops
combi_ctr = 0

# Start time of simulation
start_time = time.time()
    
    
## Loop that iterates over sample sizes
for j in range(n_sample):
    
    # Select sample size for this iteration
    n = sample_sizes[j]
                
    
    ## Loop that iterates over effect sizes / group means
    for k in range(n_effect):
        
        # Select group mean for this iteration
        mean_exp = gen_effects[k,0] 
        
        # Select corresponding effect size
        d = gen_effects[k,1] 
        
        # Initialize array of p-values for repetitions
        arr_p_values = np.zeros(n_repetitions) 
 
        
        ## Loop that iterates over number of desired repetitions
        for l in range(n_repetitions):         

            # Simulate experimental data (drawn from normal distribution)
            sim_exp_data = rng.normal(loc=mean_exp, scale=gen_sd, size=n)
            
            # Simulate control data (drawn from normal distribution)
            sim_con_data = rng.normal(loc=gen_mean_con, scale=gen_sd, size=n)
    
            # Run statistical test
            if stat_test == 't-test':
                
                test_statistic, p_value = stats.ttest_rel(sim_exp_data, sim_con_data, alternative='greater')
                
            elif stat_test == 'wilcox':
            
                test_statistic, p_value = stats.wilcoxon(sim_exp_data, sim_con_data, alternative='greater')

            # Store this iteration's p-value
            arr_p_values[l] = p_value
            
            
        ## When all repetitions for the present combination are done:
            
        # Get the number of simulations where the null hypothesis was rejected
        n_rej = np.sum(arr_p_values < sig)
        
        # Compute the probability of null hypothesis rejection under these circumstances
        prob_rej = n_rej / n_repetitions
        
        # Store the outputs in the results matrix
        results[combi_ctr,0] = n # Col 0: sample size
        results[combi_ctr,1] = d # Col 1: effect size
        results[combi_ctr,2] = prob_rej # Col 2: power
        
        # Increase ctr, move to next combination
        combi_ctr += 1
        
        # Print counter to keep track of algorithm progress
        print('Progress: ' + str(combi_ctr) + '/' + str(n_combinations))
    
   
# End time of simulation
end_time = time.time()
# Total time in minutes
total_time = round((end_time - start_time) / 60, 2)
print('Execution time of simulation loop (' + str(n_combinations) + ' combinations X ' + str(n_repetitions) + ' repetitions): \n' + str(total_time) + ' min')

# Save results in a npy file
# res_filename = 'results_' + stat_test + '.npy'
# np.save(res_filename, results)


    
#%% Plot power curves

# Open figure, let plot take up whole space
plt.figure(layout="constrained")

# Plot aesthetics
plt.title('Power Curves: Pairwise t-Test', size=30, y=1.03)
plt.xlabel('Effect size (d)', size=20)
plt.xticks(size=15)
plt.ylabel('Power (1-ß)', size=20)
plt.yticks(size=15)

# Iterate over sample sizes, plot each one
for s in range(n_sample):
    
    # Get current sample size
    n_plot = sample_sizes[s] 
    
    # Get effect sizes and power values for this sample size
    subset_sample = results[results[:,0] == n_plot]
    
    # Plot curve for this sample size: x-axis = effect size, y-axis = power, label = n        
    plt.plot(subset_sample[:,1], subset_sample[:,2], label='n = '+str(n_plot), linewidth=4) # plot result

# Add line for desired power cut-off
plt.axhline(y = aim_pow, color = 'gray', linestyle = '--')
# Add legend
plt.legend(fontsize=20, loc = 'lower right')

# Save plot 
# plt_filename = 'power-curves_' + stat_test + '.png'
# plt.savefig(plt_filename)
    
