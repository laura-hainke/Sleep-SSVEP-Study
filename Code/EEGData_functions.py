# -*- coding: utf-8 -*-
"""
Author: Laura Hainke
Date: 07.2023
Functionality: Functions for EEG data processing (Gamma-Sleep Study).
Assumptions:
Notes:

"""


# %% Environment Setup

# Libraries
import mne
import os
import numpy as np


# %% Function: load_raw
"""
    Load raw EEG file in Nihon Kohden format and perform basic processing.

    Input
    ----------
    filename : str
    	Path to the Nihon Kohden file
        
    bad_ch : list
    Names of bad channels identified visually
    
    Output
    -------
    raw : MNE raw object
    	Processed data in MNE format

"""

def load_raw(filename,bad_ch=None):

    # Go to directory containing files (necessary for read_raw_nihon)
    os.chdir(filename[0:55])
    
    # Load raw data in Nihon Kohden format (Note: takes ~25 min for a full night)
    raw = mne.io.read_raw_nihon(filename, preload=True)
    
    # Rename channels
    raw.rename_channels({'Cz':'Oz', 'P3':'PO3', 'P4':'PO4', 'Pz':'POz'})
    
    # Re-reference all ROI channels to Fz
    raw.set_eeg_reference(ref_channels=['Fz'])
    
    # Keep only ROI channels
    raw.pick_channels(['O1','O2','Cz','P3','P4','Pz'], ordered=True)
    
    # Mark bad channels, if any
    if bad_ch:
    
        if len(bad_ch) == 1:
        
            raw.info['bads'].append(bad_ch)
        
        elif len(bad_ch) > 1:
        
            raw.info['bads'].extend(bad_ch)
        
    # Move back to main directory
    os.chdir('C:/Users/Mitarbeiter/Documents/Gamma_Sleep/Code/Processing/')
    
    return raw
    
    
    
# %% Function: assign_epochs
   
"""
    Match scored epochs to data points.
    
    Input
    ----------
    raw : MNE object
    Output of load_raw()
    
    filename : str
	Path to epoch report file in .txt format

    Output
    -------
    data : ndarray
	Array containing data points and assigned stages
    
    raw : MNE object
    Original raw object with added annotations for epochs

""" 

def assign_epochs(raw, filename):
    
    # Load the .txt file containing the epochs
    with open(filename, 'r') as f:
        
        file = f.readlines()
     
        
    ## Extract info on stages
    
    # Delete file header
    file = file[22:]
    
    # Delete empty rows
    file = [row for row in file if row != "\n"]
    
    # Delete table header rows
    file = [row for row in file if "Chin" not in row]
    
    # Get nr. of epochs from file and print
    n_epochs = len(file)
    print('Nr. of epochs reported:', n_epochs)
        
    # Initialize array of epoch stages
    epoch_stages = np.zeros(n_epochs, dtype=int)
    
    # Get relevant data points
    i = 0
    while i < len(file):
        
        # Split file row into substrings
        split = file[i].split()
        
        # Second-to-last element = stage
        stage = split[-2]
          
        # Convert stage name into int, add to epoch_stages array
        if stage == 'L': # Lights on (will be ignored in analyses)
            
            epoch_stages[i] = 99
            
        elif stage == 'W': # Wake
            
            epoch_stages[i] = 0
            
        elif stage == 'N1': # Sleep stage 1 (will be ignored in analyses)
            
            epoch_stages[i] = 1
            
        elif stage == 'N2': # Sleep stage 2
            
            epoch_stages[i] = 2
            
        elif stage == 'N3': # Sleep stage 3
            
            epoch_stages[i] = 3
            
        elif stage == 'R': # REM sleep
            
            epoch_stages[i] = 4
            
        elif stage == 'M': # Movement (will be ignored in analyses)
        
            epoch_stages[i] = 99
           
        # Move to next line
        i += 1


    ## Get recording info

    # Define epoch duration (AASM standard, 30 sec)
    epoch_len = 30
    
    # Get sampling rate
    sfreq = raw.info['sfreq']
    
    # Get recording duration in seconds
    rec_len = raw._raw_lengths[0]/sfreq
    rec_len = int(np.floor(rec_len)) # round down, convert to int
    

    ## For PSD analyses: stage info as annotations
    
    # Onset of annotations: every 30 sec, for whole recording
    onset = list(range(0, rec_len, 30))
    
    # Create anotations
    annotations = mne.Annotations(onset=onset, duration=epoch_len, description=epoch_stages)  
    
    # Add to raw object
    raw.set_annotations(annotations)  
    
    
    ## For SSVEP analyses: stage info as column in data array

    # Access raw data, convert from Volts to microVolts
    data = raw.get_data() * 1e6
    
    # Transpose to vertical format for better readability
    data = np.transpose(data)
    
    # Sanity check: print nr. of epochs recorded
    print('Nr. of epochs recorded:', len(data)/sfreq/epoch_len)
    
    # Initialize empty column for stage values
    stages = np.full(len(data),np.nan)
    
    # Add stage info to each data point
    for i in range(len(epoch_stages)):
        
        # Data point index of current epoch start
        epoch_start = int(i * sfreq * epoch_len)
        
        # Data point index of current epoch end
        epoch_end = int(epoch_start + sfreq * epoch_len)
        
        # Add stage value to selected data points
        stages[epoch_start:epoch_end] = epoch_stages[i]
        
    # Merge stages array with data array
    data = np.c_[data, stages]
    
    
    return raw, data
    
    
# %% SCRATCHPAD

# # For PSD metrics:
# PSD_metrics_con = {'PSD_ntrials_W':,
#  'PSD_ntrials_N2':,
#  'PSD_ntrials_N3':,
#  'PSD_ntrials_REM':,
#  'PSD_40Hz_W':,
#  'PSD_40Hz_N2':,
#  'PSD_40Hz_N3':,
#  'PSD_40Hz_REM':,
#  'PSD_SNR_W':,
#  'PSD_SNR_N2':,
#  'PSD_SNR_N3':,
#  'PSD_SNR_REM':}

# SSVEP_metrics_con = {'SSVEP_ntrials_W','SSVEP_ntrials_N2','SSVEP_ntrials_N3','SSVEP_ntrials_REM',
# 'SSVEP_PTA_W','SSVEP_PTA_N2','SSVEP_PTA_N3','SSVEP_PTA_REM',
# 'SSVEP_SNR_W','SSVEP_SNR_N2','SSVEP_SNR_N3','SSVEP_SNR_REM'}
    
    
    