#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Master script for processing & analysis of 1 participant's full data set 
(flicker + blackout conditions)

Script assumptions:
    - Channels in order: C3, C4, TP10, POz, O1, O2, EOG, EOG-PD
    - Sampling rate = 1000 Hz; flicker frequency = 40 Hz
    - 1 photodiode trigger per second
    - Files in directory: EXG_flicker.csv, EXG_flicker.bdf, EXG_blackout.csv, EXG_blackout.bdf

"""



# %% 0. Import functions

from load_data import load_data
from get_triggers import get_triggers
from sleep_staging import sleep_staging
from sort_triggers import sort_triggers
from plots import plot_SSVEPs, plot_SSVEPs_blackout, plot_SSVEPs_condition, plot_FFT_stages, plot_segs_stage
from SSVEP_analyses import make_SSVEPs_random, induced_fft
from permutation_test import permutation_test





# %% 1. Load data

## Flicker
flicker_rawdata = load_data('EXG_flicker.csv', 'Flicker') 

# Note: function load_data takes ~10 min. After running once, the output can be stored & reloaded (uncomment below)
# np.save('flicker_rawdata.npy', flicker_rawdata) # save npy file to save time
# flicker_rawdata = np.load('flicker_rawdata.npy') 


## Select bad data segments manually (optional)
# flicker_rawdata_corr = flicker_rawdata - np.mean(flicker_rawdata, axis=0) # baseline correct all channels for plot
# plt.figure()
# plt.plot(flicker_rawdata_corr)
# Array where every row includes the start and end of a bad segment, in data points
# flicker_bad = np.array([[100,200],[5000,6000]])


## Blackout
blackout_rawdata = load_data('EXG_blackout.csv', 'Blackout')

# Note: function load_data takes ~10 min. After running once, the output can be stored & reloaded (uncomment below)
# np.save('blackout_rawdata.npy', blackout_rawdata)
# blackout_rawdata = np.load('blackout_rawdata.npy')





# %% 2. Get triggers

## Flicker
flicker_all_triggers = get_triggers(flicker_rawdata, 'Flicker')

## Blackout
blackout_all_triggers = get_triggers(blackout_rawdata, 'Blackout')





# %% 3. Sleep staging + timestamps per epoch

## Participant data (for sleep staging)

# Prompt user to modify these variables before continuing
input('Modify participant age and sex before continuing!')
# Age (int)
age = 0
# Gender (bool; True if male, False if female)
male = 0

## Flicker
flicker_sleep_stats, flicker_hypnogram, flicker_epoch_timestamps = sleep_staging('EXG_flicker', age, male) 

## Blackout
blackout_sleep_stats, blackout_hypnogram, blackout_epoch_timestamps = sleep_staging('EXG_blackout', age, male)





# %% 4. Sort triggers into sleep stages

## Flicker
flicker_W_triggers, flicker_N1_triggers, flicker_N2_triggers, flicker_N3_triggers, flicker_REM_triggers = sort_triggers(flicker_all_triggers, flicker_epoch_timestamps, flicker_hypnogram)

## Blackout
blackout_W_triggers, blackout_N1_triggers, blackout_N2_triggers, blackout_N3_triggers, blackout_REM_triggers = sort_triggers(blackout_all_triggers, blackout_epoch_timestamps, blackout_hypnogram)





# %% 5. Plot & analyse SSVEPs


## Plot SSVEPs per stage, separate electrodes

# Flicker POz
plot_SSVEPs(flicker_rawdata[3], flicker_W_triggers, flicker_N2_triggers, flicker_N3_triggers, flicker_REM_triggers)
# Flicker O1
plot_SSVEPs(flicker_rawdata[4], flicker_W_triggers, flicker_N2_triggers, flicker_N3_triggers, flicker_REM_triggers)
# Flicker O2
plot_SSVEPs(flicker_rawdata[5], flicker_W_triggers, flicker_N2_triggers, flicker_N3_triggers, flicker_REM_triggers)
# Flicker EOG1
plot_SSVEPs(flicker_rawdata[6], flicker_W_triggers, flicker_N2_triggers, flicker_N3_triggers, flicker_REM_triggers)

# Blackout POz
plot_SSVEPs(blackout_rawdata[3], blackout_W_triggers, blackout_N2_triggers, blackout_N3_triggers, blackout_REM_triggers)
# Blackout O1
plot_SSVEPs(blackout_rawdata[4], blackout_W_triggers, blackout_N2_triggers, blackout_N3_triggers, blackout_REM_triggers)
# Blackout O2
plot_SSVEPs(blackout_rawdata[5], blackout_W_triggers, blackout_N2_triggers, blackout_N3_triggers, blackout_REM_triggers)
# Blackout EOG1
plot_SSVEPs(blackout_rawdata[6], blackout_W_triggers, blackout_N2_triggers, blackout_N3_triggers, blackout_REM_triggers)



## For further analyses: average data from occipital electrodes 
flicker_occ_avg = (flicker_rawdata[3]+flicker_rawdata[4]+flicker_rawdata[5])/3
blackout_occ_avg = (blackout_rawdata[3]+blackout_rawdata[4]+blackout_rawdata[5])/3

## Re-reference to both mastoids
flicker_occ = flicker_occ_avg - (flicker_rawdata[2]/2) 
blackout_occ = blackout_occ_avg - (blackout_rawdata[2]/2) 



## For flicker, plot all segments + final SSVEP per stage
# W
plot_segs_stage(flicker_occ, flicker_W_triggers, 'W')
# N2
plot_segs_stage(flicker_occ, flicker_N2_triggers, 'N2')
# N3
plot_segs_stage(flicker_occ, flicker_N3_triggers, 'N3')


## Plot occipital average all conditions, flicker  + blackout on top in lighter colours:
plot_SSVEPs(flicker_occ, flicker_W_triggers, flicker_N2_triggers, flicker_N3_triggers, flicker_REM_triggers)
plot_SSVEPs_blackout(blackout_occ, blackout_W_triggers, blackout_N2_triggers, blackout_N3_triggers, blackout_REM_triggers)


## Plot flicker + blackout for every condition
# Flicker vs. blackout: W
plot_SSVEPs_condition(flicker_occ, flicker_W_triggers, blackout_occ, blackout_W_triggers,'W')
# Flicker vs. blackout: N2
plot_SSVEPs_condition(flicker_occ, flicker_N2_triggers, blackout_occ, blackout_N2_triggers,'N2')
# Flicker vs. blackout: N3
plot_SSVEPs_condition(flicker_occ, flicker_N3_triggers, blackout_occ, blackout_N3_triggers,'N3')
# Flicker vs. blackout: REM
plot_SSVEPs_condition(flicker_occ, flicker_REM_triggers, blackout_occ, blackout_REM_triggers,'REM')



## Get segments per stage (for permutation), SNR, p-values of SNR

# Flicker
flicker_p2p_SNR, flicker_p2p_pvalues, flicker_ssvep_W_segments, flicker_ssvep_N2_segments, flicker_ssvep_N3_segments, flicker_ssvep_REM_segments = make_SSVEPs_random(flicker_occ, flicker_W_triggers, flicker_N2_triggers, flicker_N3_triggers, flicker_REM_triggers, 100)

# Blackout
blackout_p2p_SNR, blackout_p2p_pvalues, blackout_ssvep_W_segments, blackout_ssvep_N2_segments, blackout_ssvep_N3_segments, blackout_ssvep_REM_segments = make_SSVEPs_random(blackout_occ, blackout_W_triggers, blackout_N2_triggers, blackout_N3_triggers, blackout_REM_triggers, 100)





# %% 6. Plot & analyse FFTs

## Averaged FFT per stage (for plots), segments per stage (for permutation), SNR, p-values of SNR
# (note: function takes ~ 1 hour to run)

# Flicker
flicker_fft_stages, flicker_40peak_SNR, flicker_FFT_p_values, flicker_fft_W_segments, flicker_fft_N2_segments, flicker_fft_N3_segments, flicker_fft_REM_segments = induced_fft(flicker_occ, flicker_W_triggers, flicker_N2_triggers, flicker_N3_triggers, flicker_REM_triggers)

# Blackout
blackout_fft_stages, blackout_40peak_SNR, blackout_FFT_p_values, blackout_fft_W_segments, blackout_fft_N2_segments, blackout_fft_N3_segments, blackout_fft_REM_segments = induced_fft(blackout_occ, blackout_W_triggers, blackout_N2_triggers, blackout_N3_triggers, blackout_REM_triggers)


## Plot FFT, blackout vs. flicker
plot_FFT_stages(flicker_fft_stages,blackout_fft_stages)





# %% 7. Hypothesis tests with permutation

### Hypothesis 1: blackout < flicker

## SSVEP peak-to-peak amplitudes

# Flicker_W vs. Blackout_W:
permutation_test(flicker_ssvep_W_segments, blackout_ssvep_W_segments, data_type = 'SSVEP')

# Flicker_N2 vs. Blackout_N2: 
permutation_test(flicker_ssvep_N2_segments, blackout_ssvep_N2_segments, data_type = 'SSVEP')

# Flicker_N3 vs. Blackout_N3
permutation_test(flicker_ssvep_N3_segments, blackout_ssvep_N3_segments, data_type = 'SSVEP')

# Flicker_REM vs. Blackout_REM
permutation_test(flicker_ssvep_REM_segments, blackout_ssvep_REM_segments, data_type = 'SSVEP')


## FFT peak values at 40 Hz

# Flicker_W vs. Blackout_W
permutation_test(flicker_fft_W_segments, blackout_fft_W_segments, data_type = 'FFT')

# Flicker_N2 vs. Blackout_N2
permutation_test(flicker_fft_N2_segments, blackout_fft_N2_segments, data_type = 'FFT')

# Flicker_N3 vs. Blackout_N3
permutation_test(flicker_fft_N3_segments, blackout_fft_N3_segments, data_type = 'FFT')

# Flicker_REM vs. Blackout_REM
permutation_test(flicker_fft_REM_segments, blackout_fft_REM_segments, data_type = 'FFT')



### Hypothesis 2: W > REM > N3

## SSVEP peak-to-peak amplitudes

# Flicker_W vs. Flicker_REM
permutation_test(flicker_ssvep_W_segments, flicker_ssvep_REM_segments, data_type = 'SSVEP')

# Flicker_REM vs. Flicker_N3
permutation_test(flicker_ssvep_REM_segments, flicker_ssvep_N3_segments, data_type = 'SSVEP')

# Flicker_W vs. Flicker_N3
permutation_test(flicker_ssvep_W_segments, flicker_ssvep_N3_segments, data_type = 'SSVEP')

## FFT peak values at 40 Hz

# Flicker_W vs. Flicker_REM
permutation_test(flicker_fft_W_segments, flicker_fft_REM_segments, data_type = 'FFT')

# Flicker_REM vs. Flicker_N3
permutation_test(flicker_fft_REM_segments, flicker_fft_N3_segments, data_type = 'FFT')

# Flicker_W vs. Flicker_N3
permutation_test(flicker_fft_W_segments, flicker_fft_N3_segments, data_type = 'FFT')


