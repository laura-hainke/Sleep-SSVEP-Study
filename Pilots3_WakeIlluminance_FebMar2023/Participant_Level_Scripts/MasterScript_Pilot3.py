#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: LH
Date: 28 Feb 2023
Functionality: Master script for Gamma-Sleep study pilot 3
Assumptions: 
    - Recordings with BrainProducts BrainAmp, 5 kHz, stimulation time only
    - For each condition, .eeg /.vhdr / .vmrk files
    - Channels: REF Cz, vEOG, hEOG, O1, O2, Oz, PO3, PO4, POz
    - 1 TTL pulse per flicker
Notes:

"""


# %% Environment Setup

# Packages & functions
from AnalysisFunctions import make_SSVEP_5kHz, psd_spectrum, snr_spectrum, plot_psd_snr, linear_interpolation
import mne
import numpy as np

# Input array
all_conditions = ['lux12','lux40','lux70','lux100','eye_hor','eye_ver','blackout']

# Nr. of conditions
nr_cond = len(all_conditions)

# Output array for all metrics
all_outputs = np.zeros((nr_cond,4))

# Output array for the SSVEPs (for group plot)
all_ssvep = np.zeros((2,nr_cond,125))



# %% Loop through all conditions

for i in range(nr_cond):
    
    # Get condition for current loop
    i_cond = all_conditions[i]
    
    # Print to console
    print('\nCondition: ' + i_cond)
    
    ## Load & segment data
    
    # Load data
    raw = mne.io.read_raw_brainvision(i_cond + '.vhdr', preload=True)
    
    # Drop channels not included in ROI
    raw.drop_channels(['vEOG','hEOG'])
    
    # Apply high-pass filter
    raw.filter(l_freq=0.1, h_freq=None, fir_design='firwin', verbose=False)
    
    # Reconstruct the original events from raw object
    events, _ = mne.events_from_annotations(raw)
    
    # Get TTL triggers (exclude last one, last segment may be cut off)
    triggers = events[1:-1,0]
    
    
    ## SSVEP 
    
    # Access raw data, convert from Volts to microVolts
    data = raw.get_data() * 1e6
    
    # Average data across ROI
    ROI_data = data.mean(axis=0)
    
    # Run linear interpolation on data; CHANGE PARAMETERS DEPENDING ON SSVEP
    ROI_data = linear_interpolation(ROI_data, triggers, time_1=0, time_2=60, trig_length=8)
    
    # Compute SSVEP with peak-to-trough amplitude 
    SSVEP_PTA, SSVEP_SNR, SSVEP_avg, SSVEP_std = make_SSVEP_5kHz(ROI_data, triggers, i_cond)
    
    
    ## PSD & SNR
    
    # Compute PSD spectrum
    PSDs, bin_len, freqs, idx_bin_40Hz = psd_spectrum(raw)
    
    # Compute SNR spectrum
    SNRs = snr_spectrum(PSDs, noise_n_neighbor_freqs=bin_len*3, noise_skip_neighbor_freqs=bin_len)
    
    # Plot both spectra, get target SNR value & absolute PSD value at 40 Hz
    max_abs_PSD, PSD_SNR = plot_psd_snr(PSDs, SNRs, freqs, bin_len, idx_bin_40Hz, i_cond)
    
    
    ## Save outputs 
    all_outputs[i,:] = [SSVEP_PTA, SSVEP_SNR, max_abs_PSD, PSD_SNR] 
    
    all_ssvep[0,i,:] = SSVEP_avg
    all_ssvep[1,i,:] = SSVEP_std


## Save output file as numpy; CHANGE PARTICIPANT NUMBER
np.save('VPXX_P3_outputs.npy', all_outputs)

np.save('VPXX_P3_ssveps.npy', all_ssvep)











