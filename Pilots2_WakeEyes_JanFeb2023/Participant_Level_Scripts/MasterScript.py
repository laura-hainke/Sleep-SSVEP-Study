#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Master script to load, plot & store individual participant data. Cohort: pilot sample 2 of Sleep-SSVEP Study.

Script assumptions:
    - Channels in order: L-H-EOG, R-V-EOG, TP10, O1, O2, POz, M-EOG, EOG-PD
    - Sampling rate = 1000 Hz; flicker frequency = 40 Hz
    - 1 photodiode trigger per second

"""



# %% Preparations

# Import functions
from load_data import load_data
from get_triggers import get_triggers
from SSVEP_analyses import make_SSVEPs_random, induced_fft
import numpy as np

# Initialize master file with outputs from all 12 conditions, in order as below
all_outputs = np.zeros((12,4))



# %% Condition: eyes open

# Load data
eyesopen_rawdata = load_data('screening_ExG.csv') 

# Get triggers
eyesopen_triggers = get_triggers(eyesopen_rawdata)

# For analyses, average occipital data and re-reference to both mastoids
eyesopen_occ = (eyesopen_rawdata[3]+eyesopen_rawdata[4]+eyesopen_rawdata[5])/3 - (eyesopen_rawdata[2]/2)

# Compute SSVEP with peak-to-peak amplitude and SNR
eyesopen_PTP, eyesopen_PTP_SNR = make_SSVEPs_random(eyesopen_occ, eyesopen_triggers, 'Eyes Open')

# Compute induced FFT with value at 40 Hz
eyesopen_FFT40, eyesopen_FFT40_SNR = induced_fft(eyesopen_occ, eyesopen_triggers, 'Eyes Open')



# %% Condition: eyes centred

# Load data
eyescentred_rawdata = load_data('eyes_centred_ExG.csv') 

# Get triggers
eyescentred_triggers = get_triggers(eyescentred_rawdata)

# For analyses, average occipital data and re-reference to both mastoids
eyescentred_occ = (eyescentred_rawdata[3]+eyescentred_rawdata[4]+eyescentred_rawdata[5])/3 - (eyescentred_rawdata[2]/2)

# Compute SSVEP with peak-to-peak amplitude and SNR
eyescentred_PTP, eyescentred_PTP_SNR = make_SSVEPs_random(eyescentred_occ, eyescentred_triggers, 'Eyes Centred')

# Compute induced FFT with value at 40 Hz
eyescentred_FFT40, eyescentred_FFT40_SNR = induced_fft(eyescentred_occ, eyescentred_triggers, 'Eyes Centred')



# %% Condition: eyes left

# Load data
eyesleft_rawdata = load_data('eyes_left_ExG.csv') 

# Get triggers
eyesleft_triggers = get_triggers(eyesleft_rawdata)

# For analyses, average occipital data and re-reference to both mastoids
eyesleft_occ = (eyesleft_rawdata[3]+eyesleft_rawdata[4]+eyesleft_rawdata[5])/3 - (eyesleft_rawdata[2]/2)

# Compute SSVEP with peak-to-peak amplitude and SNR
eyesleft_PTP, eyesleft_PTP_SNR = make_SSVEPs_random(eyesleft_occ, eyesleft_triggers, 'Eyes Left')

# Compute induced FFT with value at 40 Hz
eyesleft_FFT40, eyesleft_FFT40_SNR = induced_fft(eyesleft_occ, eyesleft_triggers, 'Eyes Left')



# %% Condition: eyes right

# Load data
eyesright_rawdata = load_data('eyes_right_ExG.csv') 

# Get triggers
eyesright_triggers = get_triggers(eyesright_rawdata)

# For analyses, average occipital data and re-reference to both mastoids
eyesright_occ = (eyesright_rawdata[3]+eyesright_rawdata[4]+eyesright_rawdata[5])/3 - (eyesright_rawdata[2]/2)

# Compute SSVEP with peak-to-peak amplitude and SNR
eyesright_PTP, eyesright_PTP_SNR = make_SSVEPs_random(eyesright_occ, eyesright_triggers, 'Eyes Right')

# Compute induced FFT with value at 40 Hz
eyesright_FFT40, eyesright_FFT40_SNR = induced_fft(eyesright_occ, eyesright_triggers, 'Eyes Right')



# %% Condition: eyes up

# Load data
eyesup_rawdata = load_data('eyes_up_ExG.csv') 

# Get triggers
eyesup_triggers = get_triggers(eyesup_rawdata)

# For analyses, average occipital data and re-reference to both mastoids
eyesup_occ = (eyesup_rawdata[3]+eyesup_rawdata[4]+eyesup_rawdata[5])/3 - (eyesup_rawdata[2]/2)

# Compute SSVEP with peak-to-peak amplitude and SNR
eyesup_PTP, eyesup_PTP_SNR = make_SSVEPs_random(eyesup_occ, eyesup_triggers, 'Eyes Up')

# Compute induced FFT with value at 40 Hz
eyesup_FFT40, eyesup_FFT40_SNR = induced_fft(eyesup_occ, eyesup_triggers, 'Eyes Up')



# %% Condition: eyes down

# Load data
eyesdown_rawdata = load_data('eyes_down_ExG.csv') 

# Get triggers
eyesdown_triggers = get_triggers(eyesdown_rawdata)

# For analyses, average occipital data and re-reference to both mastoids
eyesdown_occ = (eyesdown_rawdata[3]+eyesdown_rawdata[4]+eyesdown_rawdata[5])/3 - (eyesdown_rawdata[2]/2)

# Compute SSVEP with peak-to-peak amplitude and SNR
eyesdown_PTP, eyesdown_PTP_SNR = make_SSVEPs_random(eyesdown_occ, eyesdown_triggers, 'Eyes Down')

# Compute induced FFT with value at 40 Hz
eyesdown_FFT40, eyesdown_FFT40_SNR = induced_fft(eyesdown_occ, eyesdown_triggers, 'Eyes Down')



# %% Condition: on-off

# Load data
onoff_rawdata = load_data('onoff_ExG.csv') 

# Get triggers
onoff_triggers = get_triggers(onoff_rawdata)

# For analyses, average occipital data and re-reference to both mastoids
onoff_occ = (onoff_rawdata[3]+onoff_rawdata[4]+onoff_rawdata[5])/3 - (onoff_rawdata[2]/2)

# Compute SSVEP with peak-to-peak amplitude and SNR
onoff_PTP, onoff_PTP_SNR = make_SSVEPs_random(onoff_occ, onoff_triggers, 'On-Off')

# Compute induced FFT with value at 40 Hz
onoff_FFT40, onoff_FFT40_SNR = induced_fft(onoff_occ, onoff_triggers, 'On-Off')



# %% Condition: horizontal slow

# Load data
horslow_rawdata = load_data('hor_slow_ExG.csv') 

# Get triggers
horslow_triggers = get_triggers(horslow_rawdata)

# For analyses, average occipital data and re-reference to both mastoids
horslow_occ = (horslow_rawdata[3]+horslow_rawdata[4]+horslow_rawdata[5])/3 - (horslow_rawdata[2]/2)

# Compute SSVEP with peak-to-peak amplitude and SNR
horslow_PTP, horslow_PTP_SNR = make_SSVEPs_random(horslow_occ, horslow_triggers, 'Horizontal Slow')

# Compute induced FFT with value at 40 Hz
horslow_FFT40, horslow_FFT40_SNR = induced_fft(horslow_occ, horslow_triggers, 'Horizontal Slow')



# %% Condition: horizontal fast

# Load data
horfast_rawdata = load_data('hor_fast_ExG.csv') 

# Get triggers
horfast_triggers = get_triggers(horfast_rawdata)

# For analyses, average occipital data and re-reference to both mastoids
horfast_occ = (horfast_rawdata[3]+horfast_rawdata[4]+horfast_rawdata[5])/3 - (horfast_rawdata[2]/2)

# Compute SSVEP with peak-to-peak amplitude and SNR
horfast_PTP, horfast_PTP_SNR = make_SSVEPs_random(horfast_occ, horfast_triggers, 'Horizontal Fast')

# Compute induced FFT with value at 40 Hz
horfast_FFT40, horfast_FFT40_SNR = induced_fft(horfast_occ, horfast_triggers, 'Horizontal Fast')



# %% Condition: vertical slow

# Load data
verslow_rawdata = load_data('ver_slow_ExG.csv') 

# Get triggers
verslow_triggers = get_triggers(verslow_rawdata)

# For analyses, average occipital data and re-reference to both mastoids
verslow_occ = (verslow_rawdata[3]+verslow_rawdata[4]+verslow_rawdata[5])/3 - (verslow_rawdata[2]/2)

# Compute SSVEP with peak-to-peak amplitude and SNR
verslow_PTP, verslow_PTP_SNR = make_SSVEPs_random(verslow_occ, verslow_triggers, 'Vertical Slow')

# Compute induced FFT with value at 40 Hz
verslow_FFT40, verslow_FFT40_SNR = induced_fft(verslow_occ, verslow_triggers, 'Vertical Slow')



# %% Condition: vertical fast

# Load data
verfast_rawdata = load_data('ver_fast_ExG.csv') 

# Get triggers
verfast_triggers = get_triggers(verfast_rawdata)

# For analyses, average occipital data and re-reference to both mastoids
verfast_occ = (verfast_rawdata[3]+verfast_rawdata[4]+verfast_rawdata[5])/3 - (verfast_rawdata[2]/2)

# Compute SSVEP with peak-to-peak amplitude and SNR
verfast_PTP, verfast_PTP_SNR = make_SSVEPs_random(verfast_occ, verfast_triggers, 'Vertical Fast')

# Compute induced FFT with value at 40 Hz
verfast_FFT40, verfast_FFT40_SNR = induced_fft(verfast_occ, verfast_triggers, 'Vertical Fast')



# %% Condition: blackout

# Load data
blackout_rawdata = load_data('blackout_ExG.csv') 

# Get triggers
blackout_triggers = get_triggers(blackout_rawdata)

# For analyses, average occipital data and re-reference to both mastoids
blackout_occ = (blackout_rawdata[3]+blackout_rawdata[4]+blackout_rawdata[5])/3 - (blackout_rawdata[2]/2)

# Compute SSVEP with peak-to-peak amplitude and SNR
blackout_PTP, blackout_PTP_SNR = make_SSVEPs_random(blackout_occ, blackout_triggers, 'Blackout')

# Compute induced FFT with value at 40 Hz
blackout_FFT40, blackout_FFT40_SNR = induced_fft(blackout_occ, blackout_triggers, 'Blackout')



# %% Save outputs in a numpy file

## Store outputs in master ndarray
# Row 0: eyes open
all_outputs[0,:] = [eyesopen_PTP, eyesopen_PTP_SNR, eyesopen_FFT40, eyesopen_FFT40_SNR] 
# Row 1: eyes centred
all_outputs[1,:] = [eyescentred_PTP, eyescentred_PTP_SNR, eyescentred_FFT40, eyescentred_FFT40_SNR] 
# Row 2: eyes left
all_outputs[2,:] = [eyesleft_PTP, eyesleft_PTP_SNR, eyesleft_FFT40, eyesleft_FFT40_SNR]
# Row 3: eyes right
all_outputs[3,:] = [eyesright_PTP, eyesright_PTP_SNR, eyesright_FFT40, eyesright_FFT40_SNR]
# Row 4: eyes up
all_outputs[4,:] = [eyesup_PTP, eyesup_PTP_SNR, eyesup_FFT40, eyesup_FFT40_SNR]
# Row 5: eyes down
all_outputs[5,:] = [eyesdown_PTP, eyesdown_PTP_SNR, eyesdown_FFT40, eyesdown_FFT40_SNR]
# Row 6: on-off
all_outputs[6,:] = [onoff_PTP, onoff_PTP_SNR, onoff_FFT40, onoff_FFT40_SNR]
# Row 7: horizontal slow
all_outputs[7,:] = [horslow_PTP, horslow_PTP_SNR, horslow_FFT40, horslow_FFT40_SNR]
# Row 8: horizontal fast
all_outputs[8,:] = [horfast_PTP, horfast_PTP_SNR, horfast_FFT40, horfast_FFT40_SNR]
# Row 9: vertical slow
all_outputs[9,:] = [verslow_PTP, verslow_PTP_SNR, verslow_FFT40, verslow_FFT40_SNR]
# Row 10: vertical fast
all_outputs[10,:] = [verfast_PTP, verfast_PTP_SNR, verfast_FFT40, verfast_FFT40_SNR]
# Row 11: blackout
all_outputs[11,:] = [blackout_PTP, blackout_PTP_SNR, blackout_FFT40, blackout_FFT40_SNR]


## Save numpy file
participant_nr = input('Enter participant nr: ') # prompt for participant nr to save npy file
file_name = participant_nr + ('_all_outputs.npy') # create file name

np.save(file_name, all_outputs)

