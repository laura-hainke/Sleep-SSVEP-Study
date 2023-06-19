# -*- coding: utf-8 -*-
"""
Author: LH / MS
Date: 06.2023
Functionality: Assign mask analog values to lux, fit a function for extrapolation
Assumptions: 
        - 3 folders with baseline measurements
        - 1 folder with validation measurements
Notes: All credit to Marcelo Stegmann; source for this code under 
https://github.com/tscnlab/LiDuSleep/tree/main

"""

# Packages & functions
import os
import numpy as np
import luxpy
import scipy
from matplotlib import pyplot as plt

# Path names where the three baseline measurements are to be found
path1 = '/Users/Mitarbeiter/Documents/Gamma_Sleep/Preparations/Stim_Mask/Marcelo_Calibration/Calibration_Adapted/Baseline Measurements/1'
path2 = '/Users/Mitarbeiter/Documents/Gamma_Sleep/Preparations/Stim_Mask/Marcelo_Calibration/Calibration_Adapted/Baseline Measurements/2'
path3 = '/Users/Mitarbeiter/Documents/Gamma_Sleep/Preparations/Stim_Mask/Marcelo_Calibration/Calibration_Adapted/Baseline Measurements/3'

# Path name where the validation measurements after the transformation are to be found
path_validation = '/Users/Mitarbeiter/Documents/Gamma_Sleep/Preparations/Stim_Mask/Marcelo_Calibration/Calibration_Adapted/Validation Measurements'

# Create an empty list to store file names
file_names = []

# Loop through the files in the directory in order to determine the analogue input used
for file in os.listdir(path1):
    # Check if the current file is a file (not a directory) and starts with the desired prefix
    if os.path.isfile(os.path.join(path1, file)):
        # Append the file name to the list
        file_names.append(file)


# Sort the list of file names based on the number they start with
file_names = sorted([f for f in file_names if f.split('.')[0].isdigit()], key=lambda x: int(x.split('.')[0]))

# 2) iterate through all files and calculate the illuminance for each input value for the three different baseline measurements
output = [] # output containing the beasline measurements
output_validation = []  # output containing the validation measurements
input = []
abs_illuminance1 = []
abs_illuminance2 = []
abs_illuminance3 = []


for file in file_names:
    # load baseline and validation files
    current_file1 = np.loadtxt(path1 + '/' + file, delimiter='\t', skiprows=17).transpose()
    current_file2 = np.loadtxt(path2 + '/' + file, delimiter='\t', skiprows=17).transpose()
    current_file3 = np.loadtxt(path3 + '/' + file, delimiter='\t', skiprows=17).transpose()
    current_file_validation = np.loadtxt(path_validation + '/' + file, delimiter='\t', skiprows=17).transpose()
    
    # convert µW/cm2/nm to W/m2/nm
    current_file1[1] = current_file1[1]*0.01
    current_file2[1] = current_file2[1]*0.01
    current_file3[1] =current_file3[1]*0.01
    current_file_validation[1] = current_file_validation[1]*0.01

    # calculate illuminance in lux
    illuminance1 = int(luxpy.spd_to_power(current_file1,ptype='pu'))
    illuminance2 = int(luxpy.spd_to_power(current_file2,ptype='pu'))
    illuminance3 = int(luxpy.spd_to_power(current_file3,ptype='pu'))
    illuminance_validation = int(luxpy.spd_to_power(current_file_validation,ptype='pu'))  

    abs_illuminance1.append(illuminance1)
    abs_illuminance2.append(illuminance2)
    abs_illuminance3.append(illuminance3)
    input.append(int(file.split('.')[0]))
    output_validation.append(illuminance_validation)


# 3) Calculate the model with the best fit
# Input-output dataset
x = [i/max(input) for i in input]

rel_illuminance1 = [i / max(abs_illuminance1) for i in abs_illuminance1]
rel_illuminance2 = [i / max(abs_illuminance2) for i in abs_illuminance2]
rel_illuminance3 = [i / max(abs_illuminance3) for i in abs_illuminance3]

# Absolute values for plotting later on 
abs_y = np.mean([abs_illuminance1,abs_illuminance2,abs_illuminance3], axis = 0)
abs_error = np.std([abs_illuminance1,abs_illuminance2,abs_illuminance3], axis = 0)

# Relative values for determining the CDF
y = np.mean([rel_illuminance1,rel_illuminance2,rel_illuminance3],axis=0)  # make the output into a probability distribution
error = abs_error/max(abs_illuminance1 + abs_illuminance2 + abs_illuminance3) # make the output into a probability distribution

# Fit a CDF to the dataset
best_fit_name = None
best_fit_params = None
best_fit_cdf = []
best_fit_sse = np.inf

# List of candidate distributions to fit
candidate_distributions = [
    scipy.stats.norm,         # Normal distribution
    scipy.stats.expon,        # Exponential distribution
    scipy.stats.lognorm,      # Log-normal distribution
    scipy.stats.gamma,        # Gamma distribution
    scipy.stats.beta          # Beta distribution
]

# Iterate through candidate distributions and fit the best one
for distribution in candidate_distributions:
    # Curve fitting function
    def func(x, a, b):
        return distribution.cdf(x, a, b)   
    
    popt, pcov, infodict, mesg, ier = scipy.optimize.curve_fit(distribution.ppf, x, y, p0=[2.0, 1.0], full_output=True)  # probability point function instead of cumulative distribution function to make sure that we invert the result
    popt_cdf,pcov_cdf = scipy.optimize.curve_fit(distribution.cdf, x,y,p0=[2.0,1.0])

    ypred = func(x, *popt)
    ypred_cdf = func(x,*popt_cdf)

    
# Calculate the sum of squared errors (SSE) between the CDF and the data
    sse = np.sum((ypred - y) ** 2)

    # Check if this distribution has a lower SSE than the previous best fit
    if sse < best_fit_sse:
        best_fit_name = distribution.name
        best_dist = distribution
        best_fit_ypred = ypred
        best_fit_ypred_cdf = ypred_cdf
        best_fit_sse = sse

        # Last distribution with best fit = beta
        print(distribution.name)

# set the default font family to Arial
plt.rcParams['font.family'] = 'Arial'

# Create figures
fig, ax = plt.subplots(1,3,figsize=(12,3))
fig.suptitle('Linearization of analogue-input to lux-output', y=1.1, size = 15)

# Plot calibration measurements
ax[0].errorbar(input,abs_y,yerr=abs_error, fmt = 'o', color = 'red',markersize=3)
ax[0].set_xlabel('Analogue input')
ax[0].set_ylabel('Photopic Illuminance [lux]')
ax[0].set_title('Calibration measurements (n = 3)')
ax[0].grid()
ax[0].set_box_aspect(1)

# Plot best-fit CDF
ax[1].errorbar(x,y,yerr=error, fmt = 'o', color = 'red',markersize=3)
ax[1].plot(x,best_fit_ypred_cdf, label = 'Best-fit CDF ({})'.format(best_fit_name))
ax[1].set_ylabel('Relative output')
ax[1].set_xlabel('Relative input')
ax[1].set_title('Fitted calibration curve ({} CDF)'.format(best_fit_name))
ax[1].grid()
ax[1].set_box_aspect(1)

# Plot transformed measurements
ax[2].scatter(x,output_validation, s = 10, color = 'red')
ax[2].plot([0,1],[0,max(output_validation)],'--',color='gray')
ax[2].set_xlabel('Relative input')
ax[2].set_ylabel('Photopic Illuminance [lux]')
ax[2].set_title('Validation measurement (n = 1)')
ax[2].grid()
ax[2].set_box_aspect(1)

plt.show()



# %% Extract relevant info for CSV generation

# 1) Create array with analog inputs and corresponding illuminance (both abs + rel)

# input: analog values tested
# x: equivalent to input, transformed to percentage of max analog value tested
# abs_y: measured lux values corresponding to analog values, avg. across 3 measurements
# y: equivalent to abs_y, transformed to percentage of max lux measured
export = np.c_[input, x, abs_y, y]
export = np.float32(export) # harmonize to float32

# Store as csv file
np.savetxt("analog_to_lux.csv", export, delimiter=";", fmt="%.2f", header='analog; rel_analog; lux; rel_lux')

## 2) Store parameters of function for extrapolation as numpy
np.save('beta_parameters.npy', popt)

