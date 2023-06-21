# -*- coding: utf-8 -*-
"""
Author: Laura Hainke
Date: 28.04.2023
Functionality: Functions for EEG data processing (Gamma-Sleep Study).
Assumptions:
Notes:

"""


# %% Environment Setup

# Libraries
import mne


# %% Function: load_edf
"""
    Load EDF file and perform basic processing.

    Input
    ----------
    filename : str
    	Path to the EDF file
        
    bad_ch : list
        Names of bad channels identified visually
    
    Output
    -------
    raw : MNE raw object
    	Processed data in MNE format

"""

def load_edf(filename,bad_ch=None):

    # Load raw data
    raw = mne.io.read_raw_edf(filename, preload=True)
    
    # Keep only ROI channels
    raw.pick_channels(['O1-Fz','O2-Fz','Cz-Fz','P3-Fz','P4-Fz','Pz-Fz'])
    
    # Rename channels
    raw.rename_channels({'O1-Fz':'O1', 'O2-Fz':'O2', 'Cz-Fz':'Oz', 'P3-Fz':'PO3', 'P4-Fz':'PO4', 'Pz-Fz':'POz'})
    
    # Mark bad channels, if any
    if len(bad_ch) == 1:
        
        raw.info['bads'].append(bad_ch)
        
    elif len(bad_ch) > 1:
        
        raw.info['bads'].extend(bad_ch)
        
    # Print channels included in ROI
    print('Channels included in analysis: ')
    raw.info['ch_names']
        
    return raw
    
    
    
    
    
    
    
# %% SCRATCHPAD

# For PSD metrics:
PSD_metrics_con = {'PSD_ntrials_W':,
 'PSD_ntrials_N2':,
 'PSD_ntrials_N3':,
 'PSD_ntrials_REM':,
 'PSD_40Hz_W':,
 'PSD_40Hz_N2':,
 'PSD_40Hz_N3':,
 'PSD_40Hz_REM':,
 'PSD_SNR_W':,
 'PSD_SNR_N2':,
 'PSD_SNR_N3':,
 'PSD_SNR_REM':}

SSVEP_metrics_con = {'SSVEP_ntrials_W','SSVEP_ntrials_N2','SSVEP_ntrials_N3','SSVEP_ntrials_REM',
'SSVEP_PTA_W','SSVEP_PTA_N2','SSVEP_PTA_N3','SSVEP_PTA_REM',
'SSVEP_SNR_W','SSVEP_SNR_N2','SSVEP_SNR_N3','SSVEP_SNR_REM'}
    
    
    