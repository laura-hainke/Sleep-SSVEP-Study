# -*- coding: utf-8 -*-
"""
Author: Laura Hainke
Date: 07.2023
Functionality: Script to import and process EEG data; Gamma-Sleep study, experimental condition
Assumptions: Files as defined in section %% Paths to files
Notes: V1

"""


# %% Environment Setup

# Import packages
import pandas as pd 
import numpy as np
import os
import yasa

# Define directory containing code
os.chdir('C:/Users/Mitarbeiter/Documents/Gamma_Sleep/Code/Processing/')

# Import custom functions
from EEGData_functions import load_raw, import_triggers, score_sleep, select_annotations, create_epochs, compute_PSD, compute_SSVEP



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

# Path to EEG data, sessions 01 and 03
path_ses01_EEG = str(path_in + "/Session01/" + subject_nr + "_session01_raw-EEG.edf")
path_ses03_EEG = str(path_in + "/Session03/" + subject_nr + "_session03_raw-EEG.edf")

# Path to annotations, sessions 01 & 03
path_ses01_annotations = str(path_in + "/Session01/" + subject_nr + "_session01_annotations.edf")
path_ses03_annotations = str(path_in + "/Session03/" + subject_nr + "_session03_annotations.edf")


## Output data: experimental condition (sessions 01 + 03 merged)

# Path to output EEG metrics data file, experimental condition
path_exp_metrics_PSD = str(path_out + "/Experimental/" + subject_nr + "_experimental_PSD-output-metrics.csv")
path_exp_metrics_SSVEP = str(path_out + "/Experimental/" + subject_nr + "_experimental_SSVEP-output-metrics.csv")

# Path to output EEG curves data files, experimental condition
path_exp_spectra_PSD = str(path_out + "/Experimental/" + subject_nr + "_experimental_PSD-output-spectra.csv")
path_exp_curves_SSVEP = str(path_out + "/Experimental/" + subject_nr + "_experimental_SSVEP-output-curves.csv")

# Path to output sleep variables, experimental condition
path_exp_sleep = str(path_out + "/Experimental/" + subject_nr + "_experimental_sleep-data.csv")



# %% Load raw EEG file & triggers

# Initialize empty bad channel list
bad_ch_exp = []

# Prompt for bad channels
bads_bool = input("Any bad channels? (y/n) ")

# If 'yes' was selected, get bad channel names from user
while bads_bool == 'y':
    
    bad_name = input("Enter bad channel name: ")
    bad_ch_exp.append(bad_name)
    bads_bool = input("Any more bad channels? (y/n) ")

# Load s01 data, get raw object for EEG data (no PSG needed, since all W)
_, raw_s01_EEG = load_raw(path_ses01_EEG, bad_ch_exp)

# Load s03 data, get PSG and EEG raw objects
raw_s03_PSG, raw_s03_EEG = load_raw(path_ses03_EEG, bad_ch_exp)

# Print raw info for confirmation
print('\nInfos - S01 EEG dataset:\n')
print(raw_s01_EEG.info)
print('\nInfos - S03 PSG dataset:\n')
print(raw_s03_PSG.info)
print('\nInfos - S03 EEG dataset:\n')
print(raw_s03_EEG.info)

# Import triggers from both experimental sessions
triggers_s01, triggers_s03 = import_triggers(path_ses01_annotations, path_ses03_annotations, raw_s03_EEG, 'exp')



# %% Score sleep, get epochs, store metrics

## Session 01: wake only

# Get nr. of epochs in recording
n_wake_epochs = np.floor(raw_s01_EEG.__len__() / raw_s01_EEG.info['sfreq'] / 30)

# Create a "hypnogram" containing only stage 0
hypno_s01 = np.zeros(int(n_wake_epochs), dtype=int) 

# Upsample to match data (needed for SSVEP analysis)
hypno_up_s01 = yasa.hypno_upsample_to_data(hypno_s01, sf_hypno=1/30, data=raw_s01_EEG)

# Turn stages into annotations, no uncertain epochs
raw_s01_EEG = select_annotations(raw_s01_EEG, hypno_s01, [])


## Session 03: full night

# Run YASA algorithm
hypno_s03, hypno_up_s03, uncertain_epochs_s03, sleep_stats_s03 = score_sleep(raw_s03_PSG, raw_s03_EEG, bad_ch_exp, path_demographics)

# Turn stages scored with enough confidence into annotations
raw_s03_EEG = select_annotations(raw_s03_EEG, hypno_s03, uncertain_epochs_s03)


## Metrics

# Get subset of sleep metrics of interest 
sleep_data_exp = {k: sleep_stats_s03[k] for k in ('SOL','TST','WASO','%N1','%N2','%N3','%REM')}

# Access GSQS sum score for experimental night
gsqs = pd.read_csv(path_gsqs)
gsqs_sum_exp = gsqs.gsqs_sum_exp[0]

# Add GSQS score to sleep metrics dict
sleep_data_exp['GSQS_sum'] = gsqs_sum_exp

# Convert metrics dict into pandas as well
sleep_data_exp = pd.DataFrame.from_dict(sleep_data_exp, orient='index')



# %% Loop over stages to compute PSD & SNR

# Initialize dict for output metrics
PSD_metrics_exp = dict()

# Initialize array for spectra
PSD_spectra_exp = []

# Loop
for stage in [0,2,3,4]:
    
    # Select correct raw object and triggers
    if stage == 0:
        
        raw = raw_s01_EEG # for stage 0, only data from s01 is of interest
        triggers = triggers_s01
        
    else:
        
        raw = raw_s03_EEG
        triggers = triggers_s03
    
    # Exception catcher in case analysis cannot be run for a given stage
    try:
    
        # Create and select epochs (=30 sec trials) for PSD analyses of current stage
        epochs_stage = create_epochs(raw, triggers, event_id=stage)
        
        # Print nr. of epochs recorded at this stage
        print('\nNr. of epochs recorded, stage ' + str(stage) + ': ' + str(len(epochs_stage.events)))
    
        # Compute PSD and SNR spectra for current stage + metrics
        PSD_40Hz, SNR_40Hz, PSD_spectrum, SNR_spectrum = compute_PSD(epochs_stage, stage)
        
        # Get nr. of trials factoring into PSD analyses for current stage
        try:
            PSD_ntrials = len(epochs_stage) # only works when bad epochs have been dropped
        except:
            PSD_ntrials = len(epochs_stage.events) # full list of events in case no epochs have been dropped
            
        # Print nr. of epochs used for analysis
        print('Nr. of epochs used in analysis: ' + str(PSD_ntrials))
        
    # Alternative
    except:
        
        # Display warning
        print('\nWARNING: Could not run PSD analysis for stage', stage)
        
        # Mark variables as NaN
        PSD_40Hz = float('NaN')
        SNR_40Hz = float('NaN')
        PSD_ntrials = 0
        PSD_spectrum = np.full((2971), np.nan)
        SNR_spectrum = np.full((2971), np.nan)
        
    
    # Store metrics in dict
    if stage == 0: # Wake
        
        PSD_metrics_exp['PSD_ntrials_W'] = PSD_ntrials
        PSD_metrics_exp['PSD_40Hz_W'] = PSD_40Hz
        PSD_metrics_exp['PSD_SNR_W'] = SNR_40Hz
        
    elif stage == 2: # N2
    
        PSD_metrics_exp['PSD_ntrials_N2'] = PSD_ntrials
        PSD_metrics_exp['PSD_40Hz_N2'] = PSD_40Hz
        PSD_metrics_exp['PSD_SNR_N2'] = SNR_40Hz
        
    elif stage == 3: # N3
    
        PSD_metrics_exp['PSD_ntrials_N3'] = PSD_ntrials
        PSD_metrics_exp['PSD_40Hz_N3'] = PSD_40Hz
        PSD_metrics_exp['PSD_SNR_N3'] = SNR_40Hz
        
    elif stage == 4: # REM
    
        PSD_metrics_exp['PSD_ntrials_REM'] = PSD_ntrials
        PSD_metrics_exp['PSD_40Hz_REM'] = PSD_40Hz
        PSD_metrics_exp['PSD_SNR_REM'] = SNR_40Hz

    # Store spectra in array
    PSD_spectra_exp.append(np.ndarray.tolist(PSD_spectrum))
    PSD_spectra_exp.append(np.ndarray.tolist(SNR_spectrum))
        
    

# %% Create pandas dataframes to export PSD results

# Turn array with spectra into pandas dataframe 
PSD_spectra_exp = pd.DataFrame(data=PSD_spectra_exp)

# Transpose dataframe
PSD_spectra_exp = PSD_spectra_exp.transpose()

# Add variable names as headers
PSD_spectra_exp.columns=['W_PSD','W_SNR','N2_PSD','N2_SNR','N3_PSD','N3_SNR','REM_PSD','REM_SNR']

# Convert metrics dict into pandas as well
PSD_metrics_exp = pd.DataFrame.from_dict(PSD_metrics_exp, orient='index')



# %% Loop over stages to compute SSVEP & SNR

# Define ROI channels
roi_ch = ['PO3', 'PO4', 'POz', 'O1', 'O2', 'Oz']

# Remove any bad channels from selection
if len(bad_ch_exp) > 0:
    for ch in range(len(bad_ch_exp)): # loop over list of bad channels
        roi_ch.remove(bad_ch_exp[ch]) # remove given element from ROI selection

# Access raw ROI data as array, convert from Volts to microVolts
data_s01 = raw_s01_EEG.get_data(picks=roi_ch) * 1e6
data_s03 = raw_s03_EEG.get_data(picks=roi_ch) * 1e6

# Get average of the ROI channels
data_s01 = np.mean(data_s01, axis=0)
data_s03 = np.mean(data_s03, axis=0)

# Initialize dict for output metrics
SSVEP_metrics_exp = dict()

# Initialize array for SSVEP curves
SSVEP_curves_exp = []

# Compute average SSVEP per condition
for stage in [0,2,3,4]:
    
    # Select correct raw object and triggers
    if stage == 0:
        
        data = data_s01 # for stage 0, only data from s01 is of interest
        triggers = triggers_s01
        hypno_up = hypno_up_s01
        
    else:
        
        data = data_s03
        triggers = triggers_s03
        hypno_up = hypno_up_s03
    
    # Exception catcher in case analysis cannot be run for a given stage
    try:
        
        # Compute SSVEP and SNR for current stage + metrics
        SSVEP_amp, SSVEP_SNR, SSVEP_ntrials, SSVEP_curve = compute_SSVEP(data, triggers, hypno_up, stage, computeSNR=True)

    # Alternative
    except:
        
        # Display warning
        print('\nWARNING: Could not run SSVEP analysis for stage', stage)
        
        # Mark variables as NaN
        SSVEP_amp = float('NaN')
        SSVEP_SNR = float('NaN')
        SSVEP_ntrials = 0
        SSVEP_curve = np.full((25), np.nan)

    # Store metrics in dict
    if stage == 0: # Wake
        
        SSVEP_metrics_exp['SSVEP_ntrials_W'] = SSVEP_ntrials
        SSVEP_metrics_exp['SSVEP_PTA_W'] = SSVEP_amp
        SSVEP_metrics_exp['SSVEP_SNR_W'] = SSVEP_SNR
        
    elif stage == 2: # N2
    
        SSVEP_metrics_exp['SSVEP_ntrials_N2'] = SSVEP_ntrials
        SSVEP_metrics_exp['SSVEP_PTA_N2'] = SSVEP_amp
        SSVEP_metrics_exp['SSVEP_SNR_N2'] = SSVEP_SNR
        
    elif stage == 3: # N3
    
        SSVEP_metrics_exp['SSVEP_ntrials_N3'] = SSVEP_ntrials
        SSVEP_metrics_exp['SSVEP_PTA_N3'] = SSVEP_amp
        SSVEP_metrics_exp['SSVEP_SNR_N3'] = SSVEP_SNR
        
    elif stage == 4: # REM
    
        SSVEP_metrics_exp['SSVEP_ntrials_REM'] = SSVEP_ntrials
        SSVEP_metrics_exp['SSVEP_PTA_REM'] = SSVEP_amp
        SSVEP_metrics_exp['SSVEP_SNR_REM'] = SSVEP_SNR

    # Store spectra in array
    SSVEP_curves_exp.append(np.ndarray.tolist(SSVEP_curve))



# %% Create pandas dataframes to export SSVEP results

# Turn array with spectra into pandas dataframe 
SSVEP_curves_exp = pd.DataFrame(data=SSVEP_curves_exp)

# Transpose dataframe
SSVEP_curves_exp = SSVEP_curves_exp.transpose()

# Add variable names as headers
SSVEP_curves_exp.columns=['W_SSVEP','N2_SSVEP','N3_SSVEP','REM_SSVEP']

# Convert metrics dict into pandas as well
SSVEP_metrics_exp = pd.DataFrame.from_dict(SSVEP_metrics_exp, orient='index')



# %% Save output files

## PSD

# Save output metrics
PSD_metrics_exp.to_csv(path_exp_metrics_PSD, header=False)

# Save output curves
PSD_spectra_exp.to_csv(path_exp_spectra_PSD)


## SSVEP

# Save output metrics
SSVEP_metrics_exp.to_csv(path_exp_metrics_SSVEP, header=False)

# Save output curves
SSVEP_curves_exp.to_csv(path_exp_curves_SSVEP)


## Sleep metrics

# Path to output sleep variables, experimental condition
sleep_data_exp.to_csv(path_exp_sleep, header=False)




