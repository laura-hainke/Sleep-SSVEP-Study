#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Master script for processing & analysis of 1 participant's partial data set 
(flicker condition only)

Script assumptions:
    - Channels in order: C3, C4, TP10, POz, O1, O2, EOG, EOG-PD
    - Sampling rate = 1000 Hz; flicker frequency = 40 Hz
    - 1 photodiode trigger per second
    - Files in directory: EXG_flicker.csv, EXG_flicker.bdf

"""



# %% 0. Import functions

from load_data import load_data
from get_triggers import get_triggers
from sleep_staging import sleep_staging
from sort_triggers import sort_triggers
from plots import plot_SSVEPs, plot_segs_stage
from SSVEP_analyses import make_SSVEPs_random, induced_fft





# %% 1. Load data

## Flicker
flicker_rawdata = load_data('EXG_flicker.csv', 'Flicker') 

# Note: function load_data takes ~10 min. After running once, the output can be stored & reloaded (uncomment below)
# np.save('flicker_rawdata.npy', flicker_rawdata) # save npy file to save time
# flicker_rawdata = np.load('flicker_rawdata.npy') 




# %% 2. Get triggers

## Flicker
flicker_all_triggers = get_triggers(flicker_rawdata, 'Flicker')




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




# %% 4. Sort triggers into sleep stages

## Flicker
flicker_W_triggers, flicker_N1_triggers, flicker_N2_triggers, flicker_N3_triggers, flicker_REM_triggers = sort_triggers(flicker_all_triggers, flicker_epoch_timestamps, flicker_hypnogram)




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


## For further analyses: average data from occipital electrodes 
flicker_occ_avg = (flicker_rawdata[3]+flicker_rawdata[4]+flicker_rawdata[5])/3

## Re-reference to both mastoids
flicker_occ = flicker_occ_avg - (flicker_rawdata[2]/2) 



## For flicker, plot all segments + final SSVEP per stage
# W
plot_segs_stage(flicker_occ, flicker_W_triggers, 'W')
# N2
plot_segs_stage(flicker_occ, flicker_N2_triggers, 'N2')
# N3
plot_segs_stage(flicker_occ, flicker_N3_triggers, 'N3')


## Plot occipital average all conditions, flicker
plot_SSVEPs(flicker_occ, flicker_W_triggers, flicker_N2_triggers, flicker_N3_triggers, flicker_REM_triggers)


## Get segments per stage (for permutation), SNR, p-values of SNR

# Flicker
flicker_p2p_SNR, flicker_p2p_pvalues, flicker_ssvep_W_segments, flicker_ssvep_N2_segments, flicker_ssvep_N3_segments, flicker_ssvep_REM_segments = make_SSVEPs_random(flicker_occ, flicker_W_triggers, flicker_N2_triggers, flicker_N3_triggers, flicker_REM_triggers, 100)




# %% 6. Plot & analyse FFTs

## Averaged FFT per stage (for plots), segments per stage (for permutation), SNR, p-values of SNR
# (note: function takes ~ 1 hour to run)

# Flicker
flicker_fft_stages, flicker_40peak_SNR, flicker_FFT_p_values, flicker_fft_W_segments, flicker_fft_N2_segments, flicker_fft_N3_segments, flicker_fft_REM_segments = induced_fft(flicker_occ, flicker_W_triggers, flicker_N2_triggers, flicker_N3_triggers, flicker_REM_triggers)


