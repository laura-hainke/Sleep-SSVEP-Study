# -*- coding: utf-8 -*-
"""
Author: Laura Hainke
Date: 07.2023
Functionality: Script to import and process EEG data; Gamma-Sleep study, control condition
Assumptions: Files as defined in section %% Paths to files
Notes: In progress

"""


# %% Environment Setup

# Import packages
import csv
import mne
import pandas as pd 
import numpy as np
import os

# Define directory containing code
os.chdir('C:/Users/Mitarbeiter/Documents/Gamma_Sleep/Code/Processing/')

# Import custom functions
from EEGData_functions import load_raw, score_sleep, select_annotations, create_epochs, compute_PSD, compute_SSVEP



# %% Paths to files

# Get participant number from user
subject_nr = input("Subject number: ")

# Path to all input folders
path_in = str("C:/Users/Mitarbeiter/Documents/Gamma_Sleep/Data/Raw/" + subject_nr)

# Path to all output folders
path_out = str("C:/Users/Mitarbeiter/Documents/Gamma_Sleep/Data/Derivatives/" + subject_nr)


## Input data

# Path to personal data file (located in Derivatives folder)
path_demographics = str(path_in[0:-6] + "Derivatives/" + subject_nr + "/REDCap/" + subject_nr + "_personal-data.csv")

# Path to subjective sleep quality scale file
path_gsqs = str(path_in + "/REDCap/" + subject_nr + "_sleep-quality.csv")

# Path to session 02 EEG data
path_ses02_EEG = str(path_in + "/Session02/" + subject_nr + "_session02_raw-EEG.edf")

# Path to session 03 annotations
path_ses03_annotations = str(path_in + "/Session03/" + subject_nr + "_session03_annotations.edf")


## Output data

# Path to output EEG metrics data file, control condition
path_con_metrics_PSD = str(path_out + "/Control/" + subject_nr + "_control_PSD-output-metrics.csv")
path_con_metrics_SSVEP = str(path_out + "/Control/" + subject_nr + "_control_SSVEP-output-metrics.csv")

# Path to output EEG curves data files, control condition
path_con_spectra_PSD = str(path_out + "/Control/" + subject_nr + "_control_PSD-output-spectra.csv")
path_con_curves_SSVEP = str(path_out + "/Control/" + subject_nr + "_control_SSVEP-output-curves.csv")

# Path to output sleep variables, control condition
path_con_sleep = str(path_out + "/Control/" + subject_nr + "_control_sleep-data.csv")



# %% Load raw EEG file

# Initialize empty bad channel list
bad_ch_con = []

# Prompt for bad channels
bads_bool = input("Any bad channels? (y/n)")

# If 'yes' was selected, get bad channel names from user
while bads_bool == 'y':
    
    bad_name = input("Enter bad channel name:")
    bad_ch_con.append(bad_name)
    bads_bool = input("Any more bad channels? (y/n)")

# Load data, split into 2 raw objects
raw_s02_PSG, raw_s02_EEG = load_raw(path_ses02_EEG, bad_ch_con)

# Print raw info for confirmation
print('\nInfos - PSG dataset:\n')
print(raw_s02_PSG.info)
print('\nInfos - EEG dataset:\n')
print(raw_s02_EEG.info)



# %% Import triggers from experimental session

# NOTE: needs annotations from s01

# Import annotations from EDF file
trig_annotations = mne.read_annotations(path_ses03_annotations, sfreq=1000)

# Add to raw object (necessary for next step)
raw_s02_PSG.set_annotations(trig_annotations, emit_warning=True)  

# Create events from trigger annotations only
events, _ = mne.events_from_annotations(raw_s02_PSG, event_id={'DC trigger 12':1}) 

# Access data points containing triggers
all_triggers = events[:,0]

# Get length of control data file
len_data_con = raw_s02_EEG.__len__()

# Keep only triggers that fit within file, ensuring last segment is not cropped
all_triggers = np.asarray([trig for trig in all_triggers if trig < len_data_con - 25])



# %% Score sleep, get epochs, store metrics

# Run YASA algorithm
hypno_s02, hypno_up_s02, uncertain_epochs_s02, sleep_stats_s02 = score_sleep(raw_s02_PSG, raw_s02_EEG, bad_ch_con, path_demographics)

# Turn stages scored with enough confidence into annotations
raw_s02_EEG = select_annotations(raw_s02_EEG, hypno_s02, uncertain_epochs_s02)

# Control condition: subtract 10 min from sleep onset latency (10 min W by design)
sol_orig = sleep_stats_s02['SOL']
sleep_stats_s02['SOL'] = sol_orig - 10

# Get subset of sleep metrics of interest 
sleep_data_con = {k: sleep_stats_s02[k] for k in ('SOL','TST','WASO','%N1','%N2','%N3','%REM')}

# Access GSQS sum score for control night
gsqs = pd.read_csv(path_gsqs)
gsqs_sum_con = gsqs.gsqs_sum_con[0]

# Add GSQS score to sleep metrics dict
sleep_data_con['GSQS_sum'] = gsqs_sum_con

# Convert metrics dict into pandas as well
sleep_data_con = pd.DataFrame.from_dict(sleep_data_con, orient='index')



# %% Loop over stages to compute PSD & SNR

# NOTE: needs epoch selection by stim

# Initialize dict for output metrics
PSD_metrics_con = dict()

# Initialize array for spectra
PSD_spectra_con = []

# Loop
for stage in [0,2,3,4]:
    
    # Create and select epochs (=30 sec trials) for PSD analyses of current stage
    epochs_s02 = create_epochs(raw_s02_EEG, event_id=stage)
    
    # Print nr. of epochs recorded at this stage
    print('\nNr. of epochs recorded, stage ' + str(stage) + ': ' + str(len(epochs_s02.events)))

    # Compute PSD and SNR spectra for current stage + metrics
    PSD_40Hz, SNR_40Hz, PSD_spectrum, SNR_spectrum = compute_PSD(epochs_s02, stage)
    
    # Get nr. of trials factoring into PSD analyses for current stage
    try:
        PSD_ntrials = len(epochs_s02) # only works when bad epochs have been dropped
    except:
        PSD_ntrials = len(epochs_s02.events) # full list of events in case no epochs have been dropped
        
    # Print nr. of epochs used for analysis
    print('Nr. of epochs used in analysis: ' + str(PSD_ntrials))
    
    # Store metrics in dict
    if stage == 0: # Wake
        
        PSD_metrics_con['PSD_ntrials_W'] = PSD_ntrials
        PSD_metrics_con['PSD_40Hz_W'] = PSD_40Hz
        PSD_metrics_con['PSD_SNR_W'] = SNR_40Hz
        
    elif stage == 2: # N2
    
        PSD_metrics_con['PSD_ntrials_N2'] = PSD_ntrials
        PSD_metrics_con['PSD_40Hz_N2'] = PSD_40Hz
        PSD_metrics_con['PSD_SNR_N2'] = SNR_40Hz
        
    elif stage == 3: # N3
    
        PSD_metrics_con['PSD_ntrials_N3'] = PSD_ntrials
        PSD_metrics_con['PSD_40Hz_N3'] = PSD_40Hz
        PSD_metrics_con['PSD_SNR_N3'] = SNR_40Hz
        
    elif stage == 4: # REM
    
        PSD_metrics_con['PSD_ntrials_REM'] = PSD_ntrials
        PSD_metrics_con['PSD_40Hz_REM'] = PSD_40Hz
        PSD_metrics_con['PSD_SNR_REM'] = SNR_40Hz

    # Store spectra in array
    PSD_spectra_con.append(np.ndarray.tolist(PSD_spectrum))
    PSD_spectra_con.append(np.ndarray.tolist(SNR_spectrum))
        
    

# %% Create pandas dataframes to export PSD results

# Turn array with spectra into pandas dataframe 
PSD_spectra_con = pd.DataFrame(data=PSD_spectra_con)

# Transpose dataframe
PSD_spectra_con = PSD_spectra_con.transpose()

# Add variable names as headers
PSD_spectra_con.columns=['W_PSD','W_SNR','N2_PSD','N2_SNR','N3_PSD','N3_SNR','REM_PSD','REM_SNR']

# Convert metrics dict into pandas as well
PSD_metrics_con = pd.DataFrame.from_dict(PSD_metrics_con, orient='index')



# %% Loop over stages to compute SSVEP & SNR

# Define ROI channels
roi_ch = ['PO3', 'PO4', 'POz', 'O1', 'O2', 'Oz']

# Remove any bad channels from selection
if len(bad_ch_con) > 0:
    for ch in range(len(bad_ch_con)): # loop over list of bad channels
        roi_ch.remove(bad_ch_con[ch]) # remove given element from ROI selection

# Access raw ROI data as array, convert from Volts to microVolts
data_s02 = raw_s02_EEG.get_data(picks=roi_ch) * 1e6

# Get average of the ROI channels
data_s02 = np.mean(data_s02, axis=0)

# Initialize dict for output metrics
SSVEP_metrics_con = dict()

# Initialize array for SSVEP curves
SSVEP_curves_con = []

# Compute average SSVEP per condition
for stage in [0,2,3,4]:
    
    # Compute SSVEP and SNR for current stage + metrics
    SSVEP_amp, SSVEP_SNR, SSVEP_ntrials, SSVEP_curve = compute_SSVEP(data_s02, all_triggers, hypno_up_s02, stage, computeSNR=True)

    # Store metrics in dict
    if stage == 0: # Wake
        
        SSVEP_metrics_con['SSVEP_ntrials_W'] = SSVEP_ntrials
        SSVEP_metrics_con['SSVEP_PTA_W'] = SSVEP_amp
        SSVEP_metrics_con['SSVEP_SNR_W'] = SSVEP_SNR
        
    elif stage == 2: # N2
    
        SSVEP_metrics_con['SSVEP_ntrials_N2'] = SSVEP_ntrials
        SSVEP_metrics_con['SSVEP_PTA_N2'] = SSVEP_amp
        SSVEP_metrics_con['SSVEP_SNR_N2'] = SSVEP_SNR
        
    elif stage == 3: # N3
    
        SSVEP_metrics_con['SSVEP_ntrials_N3'] = SSVEP_ntrials
        SSVEP_metrics_con['SSVEP_PTA_N3'] = SSVEP_amp
        SSVEP_metrics_con['SSVEP_SNR_N3'] = SSVEP_SNR
        
    elif stage == 4: # REM
    
        SSVEP_metrics_con['SSVEP_ntrials_REM'] = SSVEP_ntrials
        SSVEP_metrics_con['SSVEP_PTA_REM'] = SSVEP_amp
        SSVEP_metrics_con['SSVEP_SNR_REM'] = SSVEP_SNR

    # Store spectra in array
    SSVEP_curves_con.append(np.ndarray.tolist(SSVEP_curve))



# %% Create pandas dataframes to export SSVEP results

# Turn array with spectra into pandas dataframe 
SSVEP_curves_con = pd.DataFrame(data=SSVEP_curves_con)

# Transpose dataframe
SSVEP_curves_con = SSVEP_curves_con.transpose()

# Add variable names as headers
SSVEP_curves_con.columns=['W_SSVEP','N2_SSVEP','N3_SSVEP','REM_SSVEP']

# Convert metrics dict into pandas as well
SSVEP_metrics_con = pd.DataFrame.from_dict(SSVEP_metrics_con, orient='index')



# %% Save output files

## PSD

# Save output metrics
PSD_metrics_con.to_csv(path_con_metrics_PSD, header=False)

# Save output curves
PSD_spectra_con.to_csv(path_con_spectra_PSD)


## SSVEP

# Save output metrics
SSVEP_metrics_con.to_csv(path_con_metrics_SSVEP, header=False)

# Save output curves
SSVEP_curves_con.to_csv(path_con_curves_SSVEP)


## Sleep metrics

# Path to output sleep variables, control condition
sleep_data_con.to_csv(path_con_sleep, header=False)




