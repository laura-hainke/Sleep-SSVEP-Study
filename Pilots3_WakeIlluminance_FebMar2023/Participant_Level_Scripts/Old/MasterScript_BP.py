#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

20.02.2023 pilot: flicker artifact

- setup described in pilot_notes.pdf
- MLX vs. BP (photodiode)
- photodiode vs. TTL (BP)

- MLX channels: AF3, AF4, PO3, PO4, CP3, CP4, trig1, trig2 (REF: Cz)
- BP channels: 1-Fp1, 2-Fp2, 9-O1, 10-O2, 5-trig1, 6-trig2, 7-P3, 8-P4  (REF: FCz)

NOTE:
- for MLX: if including only triggers that are one second apart, most triggers get lost, so deactivated

"""



# %% Preparations

# Import functions
from load_data import load_data
from get_triggers import get_triggers
from get_triggers_5kHz import get_triggers_5kHz
from SSVEP_analyses import make_SSVEP, induced_fft 
from SSVEP_analyses_5kHz import make_SSVEP_5kHz, induced_fft_5kHz

import mne



# %% MLX data & triggers

# Load entire dataset
MLX_rawdata = load_data('sleep_mask_MLX_ExG.csv')   

# Manually extract blackout
MLX_blackout = MLX_rawdata[:,357000:1320000]

# Get triggers
MLX_blackout_triggers = get_triggers(MLX_blackout)

# Manually extract flicker
MLX_flicker = MLX_rawdata[:,1320000:1700000]

# Get triggers
MLX_flicker_triggers = get_triggers(MLX_flicker)



# %% BP data & triggers


## Blackout

# Import the BrainVision data into an MNE Raw object
BP_blackout_mneraw = mne.io.read_raw_brainvision('sleep_mask_trigger_test.vhdr', preload=True)

# Apply bandpass filter
BP_blackout_mneraw.filter(l_freq=0.1, h_freq=None, fir_design='firwin', verbose=False)

# Access raw data
BP_blackout, _ = BP_blackout_mneraw[:]

# Convert from Volts to microVolts
BP_blackout = BP_blackout * 1e6 

# Get photodiode triggers
BP_blackout_triggers = get_triggers_5kHz(BP_blackout)

# Reconstruct the original events from raw object
events, _ = mne.events_from_annotations(BP_blackout_mneraw)

# Get TTL triggers (same length as photodiode triggers list)
triggers_ttl = events[1:-5,0]


## Flicker

# Import the BrainVision data into an MNE Raw object
BP_flicker_mneraw = mne.io.read_raw_brainvision('sleep_mask_full_intensity.vhdr', preload=True)

# Apply bandpass filter
BP_flicker_mneraw.filter(l_freq=0.1, h_freq=None, fir_design='firwin', verbose=False)

# Access raw data
BP_flicker, _ = BP_flicker_mneraw[:]

# Convert from Volts to microVolts
BP_flicker = BP_flicker * 1e6 

# Get photodiode triggers
BP_flicker_triggers = get_triggers_5kHz(BP_flicker)

# Reconstruct the original events from raw object
events_f, _ = mne.events_from_annotations(BP_flicker_mneraw)

# Get TTL triggers (same length as photodiode triggers list)
triggers_ttl_f = events_f[1:-20,0]



# %% Blackout - MLX (photodiode)


## Frontal

# Average
MLX_blackout_fron = (MLX_blackout[0]+MLX_blackout[1])/2

# Compute SSVEP with peak-to-peak amplitude
make_SSVEP(MLX_blackout_fron, MLX_blackout_triggers, 'MLX blackout frontal')

# Compute induced FFT with value at 40 Hz
# NOTE: no peak at 40 Hz
# MLX_blackout_fron_FFT40, MLX_blackout_fron_FFT40_SNR = induced_fft(MLX_blackout_fron, MLX_blackout_triggers, 'MLX blackout frontal')


## Occipital

# Average 
MLX_blackout_occ = (MLX_blackout[2]+MLX_blackout[3])/2

# Compute SSVEP with peak-to-peak amplitude 
make_SSVEP(MLX_blackout_occ, MLX_blackout_triggers, 'MLX blackout occipital')

# Compute induced FFT with value at 40 Hz
# NOTE: no peak at 40 Hz
# MLX_blackout_occ_FFT40, MLX_blackout_occ_FFT40_SNR = induced_fft(MLX_blackout_occ, MLX_blackout_triggers, 'MLX blackout occipital')



# %% Blackout - BP (photodiode)


## Frontal

# Average
BP_blackout_fron = (BP_blackout[0]+BP_blackout[1])/2

# Compute SSVEP with peak-to-peak amplitude
make_SSVEP_5kHz(BP_blackout_fron, BP_blackout_triggers, 'BP blackout frontal')

# Compute induced FFT with value at 40 Hz
# NOTE: no peak at 40 Hz
# BP_blackout_fron_FFT40, BP_blackout_fron_FFT40_SNR = induced_fft_5kHz(BP_blackout_fron, BP_blackout_triggers, 'BP blackout frontal')


## Occipital

# Average 
BP_blackout_occ = (BP_blackout[2]+BP_blackout[3])/2

# Compute SSVEP with peak-to-peak amplitude 
make_SSVEP_5kHz(BP_blackout_occ, BP_blackout_triggers, 'BP blackout occipital')

# Compute induced FFT with value at 40 Hz
# NOTE: no peak at 40 Hz
# BP_blackout_occ_FFT40, BP_blackout_occ_FFT40_SNR = induced_fft_5kHz(BP_blackout_occ, BP_blackout_triggers, 'BP blackout occipital')



# %% Blackout - BP (TTL)


## Frontal

# Compute SSVEP with peak-to-peak amplitude
make_SSVEP_5kHz(BP_blackout_fron, triggers_ttl, 'BP blackout frontal, TTL')

# Compute induced FFT with value at 40 Hz
# NOTE: no peak at 40 Hz
# BP_blackout_TTL_fron_FFT40, BP_blackout_TTL_fron_FFT40_SNR = induced_fft_5kHz(BP_blackout_fron, triggers_ttl, 'BP blackout frontal, TTL')


## Occipital

# Compute SSVEP with peak-to-peak amplitude
make_SSVEP_5kHz(BP_blackout_occ, triggers_ttl, 'BP blackout occipital, TTL')

# Compute induced FFT with value at 40 Hz
# NOTE: no peak at 40 Hz
# BP_blackout_TTL_occ_FFT40, BP_blackout_TTL_occ_FFT40_SNR = induced_fft_5kHz(BP_blackout_occ, triggers_ttl, 'BP blackout occipital, TTL')



# %% Flicker - MLX (photodiode)


## Frontal

# Average
MLX_flicker_fron = (MLX_flicker[0]+MLX_flicker[1])/2

# Compute SSVEP with peak-to-peak amplitude 
make_SSVEP(MLX_flicker_fron, MLX_flicker_triggers, 'MLX flicker frontal')

# Compute induced FFT with value at 40 Hz
MLX_flicker_fron_FFT40, MLX_flicker_fron_FFT40_SNR = induced_fft(MLX_flicker_fron, MLX_flicker_triggers, 'MLX flicker frontal')


## Occipital

# Average
MLX_flicker_occ = (MLX_flicker[2]+MLX_flicker[3])/2

# Compute SSVEP with peak-to-peak amplitude 
make_SSVEP(MLX_flicker_occ, MLX_flicker_triggers, 'MLX flicker occipital')

# Compute induced FFT with value at 40 Hz
MLX_flicker_occ_FFT40, MLX_flicker_occ_FFT40_SNR = induced_fft(MLX_flicker_occ, MLX_flicker_triggers, 'MLX flicker occipital')



# %% Flicker - BP (photodiode)


## Frontal

# Average
BP_flicker_fron = (BP_flicker[0]+BP_flicker[1])/2

# Compute SSVEP with peak-to-peak amplitude
make_SSVEP_5kHz(BP_flicker_fron, BP_flicker_triggers, 'BP flicker frontal')

# Compute induced FFT with value at 40 Hz
BP_flicker_fron_FFT40, BP_flicker_fron_FFT40_SNR = induced_fft_5kHz(BP_flicker_fron, BP_flicker_triggers, 'BP flicker frontal')


## Occipital

# Average 
BP_flicker_occ = (BP_flicker[2]+BP_flicker[3])/2

# Compute SSVEP with peak-to-peak amplitude 
make_SSVEP_5kHz(BP_flicker_occ, BP_flicker_triggers, 'BP flicker occipital')

# Compute induced FFT with value at 40 Hz
BP_flicker_occ_FFT40, BP_flicker_occ_FFT40_SNR = induced_fft_5kHz(BP_flicker_occ, BP_flicker_triggers, 'BP flicker occipital')



# %% Flicker - BP (TTL)


## Frontal

# Compute SSVEP with peak-to-peak amplitude
make_SSVEP_5kHz(BP_flicker_fron, triggers_ttl_f, 'BP flicker frontal, TTL')

# Compute induced FFT with value at 40 Hz
BP_flicker_TTL_fron_FFT40, BP_flicker_TTL_fron_FFT40_SNR = induced_fft_5kHz(BP_flicker_fron, triggers_ttl_f, 'BP flicker frontal, TTL')


## Occipital

# Compute SSVEP with peak-to-peak amplitude 
make_SSVEP_5kHz(BP_flicker_occ, triggers_ttl_f, 'BP flicker occipital, TTL')

# Compute induced FFT with value at 40 Hz
BP_flicker_TTL_occ_FFT40, BP_flicker_TTL_occ_FFT40_SNR = induced_fft_5kHz(BP_flicker_occ, triggers_ttl_f, 'BP flicker occipital, TTL')



