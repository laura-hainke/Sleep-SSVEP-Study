#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Master script to load, plot & store individual participant data. Cohort: pilot sample 3 of Sleep-SSVEP Study.

Script assumptions:
    - Channels in order: L-H-EOG, R-V-EOG, TP10, O1, O2, POz, M-EOG, EOG-PD
    - Sampling rate = 1000 Hz; flicker frequency = 40 Hz
    - 1 photodiode trigger per second

"""



# %% Preparations

# Import functions
from load_data import load_data
from get_triggers import get_triggers
from SSVEP_analyses import make_SSVEP, make_SSVEPs_random, induced_fft, linear_interpolation
import numpy as np

# Initialize master file with outputs from all 6 conditions, in order as below
all_outputs = np.zeros((7,4))



# %% Condition: 12 lux

# Load data
lux12_rawdata = load_data('lux12_ExG.csv') 

# Get triggers
lux12_triggers = get_triggers(lux12_rawdata)

# For analyses, average occipital data and re-reference to both mastoids
lux12_occ = (lux12_rawdata[3]+lux12_rawdata[4]+lux12_rawdata[5])/3 - (lux12_rawdata[2]/2)

# Compute SSVEP with peak-to-peak amplitude and SNR
make_SSVEP(lux12_occ, lux12_triggers, '12 lux')

# Prompt researcher: is there a clear flicker artifact?
artifact = input('Is there a flicker artifact? Y/N ')

if artifact == 'Y':
    # Run a linear interpolation on all occipital data
    lux12_occ_int = linear_interpolation(lux12_occ, lux12_triggers, 1, 16, 4)
    # Define linearly interpolated data as the set for analysis
    lux12_data = lux12_occ_int  
else:
    # Define NOT linearly interpolated data as the set for analysis
    lux12_data = lux12_occ
        
# Compute SNR from shuffled SSVEP
lux12_PTP, lux12_PTP_SNR = make_SSVEPs_random(lux12_data, lux12_triggers, '12 lux')

# Compute induced FFT with value at 40 Hz
lux12_FFT40, lux12_FFT40_SNR = induced_fft(lux12_data, lux12_triggers, '12 lux')



# %% Condition: 40 lux

# Load data
lux40_rawdata = load_data('lux40_ExG.csv') 

# Get triggers
lux40_triggers = get_triggers(lux40_rawdata)

# For analyses, average occipital data and re-reference to both mastoids
lux40_occ = (lux40_rawdata[3]+lux40_rawdata[4]+lux40_rawdata[5])/3 - (lux40_rawdata[2]/2)

# Compute SSVEP with peak-to-peak amplitude and SNR
make_SSVEP(lux40_occ, lux40_triggers, '40 lux')

# Prompt researcher: is there a clear flicker artifact?
artifact = input('Is there a flicker artifact? Y/N ')

if artifact == 'Y':
    # Run a linear interpolation on all occipital data
    lux40_occ_int = linear_interpolation(lux40_occ, lux40_triggers, 1, 16, 4)
    # Define linearly interpolated data as the set for analysis
    lux40_data = lux40_occ_int  
else:
    # Define NOT linearly interpolated data as the set for analysis
    lux40_data = lux40_occ
        
# Compute SNR from shuffled SSVEP
lux40_PTP, lux40_PTP_SNR = make_SSVEPs_random(lux40_data, lux40_triggers, '40 lux')

# Compute induced FFT with value at 40 Hz
lux40_FFT40, lux40_FFT40_SNR = induced_fft(lux40_data, lux40_triggers, '40 lux')



# %% Condition: 70 lux

# Load data
lux70_rawdata = load_data('lux70_ExG.csv') 

# Get triggers
lux70_triggers = get_triggers(lux70_rawdata)

# For analyses, average occipital data and re-reference to both mastoids
lux70_occ = (lux70_rawdata[3]+lux70_rawdata[4]+lux70_rawdata[5])/3 - (lux70_rawdata[2]/2)

# Compute SSVEP with peak-to-peak amplitude and SNR
make_SSVEP(lux70_occ, lux70_triggers, '70 lux')

# Prompt researcher: is there a clear flicker artifact?
artifact = input('Is there a flicker artifact? Y/N ')

if artifact == 'Y':
    # Run a linear interpolation on all occipital data
    lux70_occ_int = linear_interpolation(lux70_occ, lux70_triggers, 1, 16, 4)
    # Define linearly interpolated data as the set for analysis
    lux70_data = lux70_occ_int  
else:
    # Define NOT linearly interpolated data as the set for analysis
    lux70_data = lux70_occ
        
# Compute SNR from shuffled SSVEP
lux70_PTP, lux70_PTP_SNR = make_SSVEPs_random(lux70_data, lux70_triggers, '70 lux')

# Compute induced FFT with value at 40 Hz
lux70_FFT40, lux70_FFT40_SNR = induced_fft(lux70_data, lux70_triggers, '70 lux')



# %% Condition: 100 lux

# Load data
lux100_rawdata = load_data('lux100_ExG.csv') 

# Get triggers
lux100_triggers = get_triggers(lux100_rawdata)

# For analyses, average occipital data and re-reference to both mastoids
lux100_occ = (lux100_rawdata[3]+lux100_rawdata[4]+lux100_rawdata[5])/3 - (lux100_rawdata[2]/2)

# Compute SSVEP with peak-to-peak amplitude and SNR
make_SSVEP(lux100_occ, lux100_triggers, '100 lux')

# Prompt researcher: is there a clear flicker artifact?
artifact = input('Is there a flicker artifact? Y/N ')

if artifact == 'Y':
    # Run a linear interpolation on all occipital data
    lux100_occ_int = linear_interpolation(lux100_occ, lux100_triggers, 1, 16, 4)
    # Define linearly interpolated data as the set for analysis
    lux100_data = lux100_occ_int  
else:
    # Define NOT linearly interpolated data as the set for analysis
    lux100_data = lux100_occ
        
# Compute SNR from shuffled SSVEP
lux100_PTP, lux100_PTP_SNR = make_SSVEPs_random(lux100_data, lux100_triggers, '100 lux')

# Compute induced FFT with value at 40 Hz
lux100_FFT40, lux100_FFT40_SNR = induced_fft(lux100_data, lux100_triggers, '100 lux')



# %% Condition: horizontal eye movements, 45 bpm

# Load data
eyemove_hor_rawdata = load_data('eyemove_hor_ExG.csv') 

# Get triggers
eyemove_hor_triggers = get_triggers(eyemove_hor_rawdata)

# For analyses, average occipital data and re-reference to both mastoids
eyemove_hor_occ = (eyemove_hor_rawdata[3]+eyemove_hor_rawdata[4]+eyemove_hor_rawdata[5])/3 - (eyemove_hor_rawdata[2]/2)

# Compute SSVEP with peak-to-peak amplitude and SNR
make_SSVEP(eyemove_hor_occ, eyemove_hor_triggers, 'EyeMove Hor.')

# Prompt researcher: is there a clear flicker artifact?
artifact = input('Is there a flicker artifact? Y/N ')

if artifact == 'Y':
    # Run a linear interpolation on all occipital data
    eyemove_hor_occ_int = linear_interpolation(eyemove_hor_occ, eyemove_hor_triggers, 1, 16, 4)
    # Define linearly interpolated data as the set for analysis
    eyemove_hor_data = eyemove_hor_occ_int  
else:
    # Define NOT linearly interpolated data as the set for analysis
    eyemove_hor_data = eyemove_hor_occ
        
# Compute SNR from shuffled SSVEP
eyemove_hor_PTP, eyemove_hor_PTP_SNR = make_SSVEPs_random(eyemove_hor_data, eyemove_hor_triggers, 'EyeMove Hor.')

# Compute induced FFT with value at 40 Hz
eyemove_hor_FFT40, eyemove_hor_FFT40_SNR = induced_fft(eyemove_hor_data, eyemove_hor_triggers, 'EyeMove Hor.')



# %% Condition: vertical eye movements, 45 bpm

# Load data
eyemove_ver_rawdata = load_data('eyemove_ver_ExG.csv') 

# Get triggers
eyemove_ver_triggers = get_triggers(eyemove_ver_rawdata)

# For analyses, average occipital data and re-reference to both mastoids
eyemove_ver_occ = (eyemove_ver_rawdata[3]+eyemove_ver_rawdata[4]+eyemove_ver_rawdata[5])/3 - (eyemove_ver_rawdata[2]/2)

# Compute SSVEP with peak-to-peak amplitude and SNR
make_SSVEP(eyemove_ver_occ, eyemove_ver_triggers, 'EyeMove Ver.')

# Prompt researcher: is there a clear flicker artifact?
artifact = input('Is there a flicker artifact? Y/N ')

if artifact == 'Y':
    # Run a linear interpolation on all occipital data
    eyemove_ver_occ_int = linear_interpolation(eyemove_ver_occ, eyemove_ver_triggers, 1, 16, 4)
    # Define linearly interpolated data as the set for analysis
    eyemove_ver_data = eyemove_ver_occ_int  
else:
    # Define NOT linearly interpolated data as the set for analysis
    eyemove_ver_data = eyemove_ver_occ
        
# Compute SNR from shuffled SSVEP
eyemove_ver_PTP, eyemove_ver_PTP_SNR = make_SSVEPs_random(eyemove_ver_data, eyemove_ver_triggers, 'EyeMove Ver.')

# Compute induced FFT with value at 40 Hz
eyemove_ver_FFT40, eyemove_ver_FFT40_SNR = induced_fft(eyemove_ver_data, eyemove_ver_triggers, 'EyeMove Ver.')



# %% Condition: blackout

# Load data
blackout_rawdata = load_data('blackout_ExG.csv') 

# Get triggers
blackout_triggers = get_triggers(blackout_rawdata)

# For analyses, average occipital data and re-reference to both mastoids
blackout_occ = (blackout_rawdata[3]+blackout_rawdata[4]+blackout_rawdata[5])/3 - (blackout_rawdata[2]/2)

# Compute SSVEP with peak-to-peak amplitude and SNR
make_SSVEP(blackout_occ, blackout_triggers, 'blackout')

# Prompt researcher: is there a clear flicker artifact?
artifact = input('Is there a flicker artifact? Y/N ')

if artifact == 'Y':
    # Run a linear interpolation on all occipital data
    blackout_occ_int = linear_interpolation(blackout_occ, blackout_triggers, 1, 16, 4)
    # Define linearly interpolated data as the set for analysis
    blackout_data = blackout_occ_int  
else:
    # Define NOT linearly interpolated data as the set for analysis
    blackout_data = blackout_occ
        
# Compute SNR from shuffled SSVEP
blackout_PTP, blackout_PTP_SNR = make_SSVEPs_random(blackout_data, blackout_triggers, 'blackout')

# Compute induced FFT with value at 40 Hz
blackout_FFT40, blackout_FFT40_SNR = induced_fft(blackout_data, blackout_triggers, 'blackout')



# %% Save outputs in a numpy file

## Store outputs in master ndarray
# Row 0: 12 lux
all_outputs[0,:] = [lux12_PTP, lux12_PTP_SNR, lux12_FFT40, lux12_FFT40_SNR] 
# Row 1: 40 lux
all_outputs[1,:] = [lux40_PTP, lux40_PTP_SNR, lux40_FFT40, lux40_FFT40_SNR] 
# Row 2: 70 lux
all_outputs[2,:] = [lux70_PTP, lux70_PTP_SNR, lux70_FFT40, lux70_FFT40_SNR]
# Row 3: 100 lux
all_outputs[3,:] = [lux100_PTP, lux100_PTP_SNR, lux100_FFT40, lux100_FFT40_SNR]
# Row 4: horizontal eye movements
all_outputs[4,:] = [eyemove_hor_PTP, eyemove_hor_PTP_SNR, eyemove_hor_FFT40, eyemove_hor_FFT40_SNR]
# Row 5: vertical eye movements
all_outputs[5,:] = [eyemove_ver_PTP, eyemove_ver_PTP_SNR, eyemove_ver_FFT40, eyemove_ver_FFT40_SNR]
# Row 6: blackout
all_outputs[6,:] = [blackout_PTP, blackout_PTP_SNR, blackout_FFT40, blackout_FFT40_SNR]


## Save numpy file
participant_nr = input('Enter participant nr: ') # prompt for participant nr to save npy file
file_name = participant_nr + ('_all_outputs.npy') # create file name

np.save(file_name, all_outputs)

