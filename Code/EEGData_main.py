# -*- coding: utf-8 -*-
"""
Author: Laura Hainke
Date: 07.2023
Functionality: Script to import and process EEG data (Gamma-Sleep study).
Assumptions:
    - Files for exp recording, session 01 (~20 min)
    - Files for whole con recording, session 02 (~8 h)
    - Files for sleep exp recording, session 03 (~8 h)
    - Nihon Kohden files: .eeg (raw EEG), .pnt (metadata), .log (annotations), .21e (channel & electrode info)
    - 1 .txt file with scored epochs for con recording, session 02
    - 1 .txt file with scored epochs for exp recording, session 03
Notes:

"""


# %% Environment Setup

# Import packages
import csv
import mne
import pandas as pd 
import numpy as np
import os

# Define directory
os.chdir('C:/Users/Mitarbeiter/Documents/Gamma_Sleep/Code/Processing/')

# Import custom functions
from EEGData_functions import load_raw, score_sleep, select_annotations, create_epochs, compute_PSD



# %% Paths to files

# Get participant number from user
subject_nr = input("Subject number: ")

# Path to all input folders
path_in = str("C:/Users/Mitarbeiter/Documents/Gamma_Sleep/Data/Raw/" + subject_nr)

# Path to all output folders
path_out = str("C:/Users/Mitarbeiter/Documents/Gamma_Sleep/Data/Derivatives/" + subject_nr)


## Input data: all sessions

# Path to personal data file (located in Derivatives folder)
path_demographics = str(path_in[0:-6] + "Derivatives/" + subject_nr + "/REDCap/" + subject_nr + "_personal-data.csv")

# Path to subjective sleep quality scale file
path_gsqs = str(path_in + "/REDCap/" + subject_nr + "_sleep-quality.csv")

# Path to session 01 EEG data & annotation files
path_ses01_EEG = str(path_in + "/Session01/" + subject_nr + "_session01_raw-EEG.edf")

# Path to session 02 EEG data & annotation files
path_ses02_EEG = str(path_in + "/Session02/" + subject_nr + "_session02_raw-EEG.edf")

# Path to session 03 EEG data & annotation files
path_ses03_EEG = str(path_in + "/Session03/" + subject_nr + "_session03_raw-EEG.edf")


## Output data: control condition (session 02)

# Path to output EEG metrics data file, control condition
path_con_metrics_PSD = str(path_out + "/Control/" + subject_nr + "_control_PSD-output-metrics.csv")
path_con_metrics_SSVEP = str(path_out + "/Control/" + subject_nr + "_control_SSVEP-output-metrics.csv")

# Path to output EEG curves data files, control condition
path_con_spectra_PSD = str(path_out + "/Control/" + subject_nr + "_control_PSD-output-spectra.csv")
path_con_curves_SSVEP = str(path_out + "/Control/" + subject_nr + "_control_SSVEP-output-curves.csv")

# Path to output sleep variables, control condition
path_con_sleep = str(path_out + "/Control/" + subject_nr + "_control_sleep-data.csv")


## Output data: experimental condition (sessions 01 + 03 merged)

# Path to output EEG metrics data file, experimental condition
path_exp_metrics_PSD = str(path_out + "/Experimental/" + subject_nr + "_experimental_PSD-output-metrics.csv")
path_exp_metrics_SSVEP = str(path_out + "/Experimental/" + subject_nr + "_experimental_SSVEP-output-metrics.csv")

# Path to output EEG curves data files, experimental condition
path_exp_spectra_PSD = str(path_out + "/Experimental/" + subject_nr + "_experimental_PSD-output-spectra.csv")
path_exp_curves_SSVEP = str(path_out + "/Experimental/" + subject_nr + "_experimental_SSVEP-output-curves.csv")

# Path to output sleep variables, experimental condition
path_exp_sleep = str(path_out + "/Experimental/" + subject_nr + "_experimental_sleep-data.csv")



# %% Load & process control data

## Load files

# Prompt for bad channels
bads_bool = input("Any bad channels? (y/n)")

# Initialize empty bad channel list
bad_ch_con = []

# Get bad channel names from user
while bads_bool == 'y':
    
    bad_name = input("Enter bad channel name:")
    bad_ch_con.append(bad_name)
    bads_bool = input("Any more bad channels? (y/n)")

# Load data
raw_s02_PSG, raw_s02_EEG = load_raw(path_ses02_EEG, bad_ch_con)

# Print raw info for confirmation
print('\nInfos - PSG dataset:\n')
print(raw_s02_PSG.info)
print('\nInfos - EEG dataset:\n')
print(raw_s02_EEG.info)


## Score sleep, get epochs, store metrics

# Run YASA algorithm
hypno_s02, hypno_up_s02, uncertain_epochs_s02, sleep_stats_s02 = score_sleep(raw_s02_PSG, raw_s02_EEG, bad_ch_con, path_demographics)

# Control condition: subtract 10 min from sleep onset latency (10 min W by design)
sol_orig = sleep_stats_s02['SOL']
sleep_stats_s02['SOL'] = sol_orig - 10

# Turn stages scored with enough confidence into annotations
raw_s02_EEG = select_annotations(raw_s02_EEG, hypno_s02, uncertain_epochs_s02)

# Access GSQS sum score for control night
gsqs = pd.read_csv(path_gsqs)
gsqs_sum_con = gsqs.gsqs_sum_con[0]

# Get subset of sleep metrics of interest 
sleep_data_con = {k: sleep_stats_s02[k] for k in ('SOL','TST','WASO','%N1','%N2','%N3','%REM')}

# Add GSQS score
sleep_data_con['GSQS_sum'] = gsqs_sum_con

# Convert metrics dict into pandas as well
sleep_data_con = pd.DataFrame.from_dict(sleep_data_con, orient='index')


## Loop over stages to compute PSD & SNR

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
        

## Create pandas dataframes for easier export

# Turn array with spectra into pandas dataframe 
PSD_spectra_con = pd.DataFrame(data=PSD_spectra_con)

# Transpose dataframe
PSD_spectra_con = PSD_spectra_con.transpose()

# Add variable names as headers
PSD_spectra_con.columns=['W_PSD','W_SNR','N2_PSD','N2_SNR','N3_PSD','N3_SNR','REM_PSD','REM_SNR']

# Convert metrics dict into pandas as well
PSD_metrics_con = pd.DataFrame.from_dict(PSD_metrics_con, orient='index')


## Loop over stages to compute SSVEP & SNR

# Compute average SSVEP per condition
# SSVEP_curves_con, SSVEP_metrics_con = []






# %% Load & process experimental data

# Load data, select ROI channels
raw_s01 = load_raw(path_ses01_EEG) # Session 01: experimental, wake (20 min)
raw_s03 = load_raw(path_ses03_EEG) # Session 03: experimental, sleep (8 h)

# Assign scored epochs to data
data_epochs_s03 = assign_epochs(raw_s03, path_ses03_epochs)

# Compute average PSD per expdition
PSD_spectra_exp, PSD_metrics_exp = [] 

# Compute average SSVEP per condition
SSVEP_curves_exp, SSVEP_metrics_exp = []



# %% Save output files: Control

## Save processed EEG data file
mne.export.export_raw(path_con_EEG, raw_clean_con, fmt = 'edf')


## Save output metrics: PSD
with open(path_con_metrics_PSD, 'w', newline='') as file:
    
    # Open CSV writer
    writer = csv.writer(file, delimiter=';')

    # Write variable names and metrics
    for key, value in PSD_metrics_con.items():
        
        writer.writerow([key,value])
        

## Save output metrics: SSVEP
with open(path_con_metrics_SSVEP, 'w', newline='') as file:
    
    # Open CSV writer
    writer = csv.writer(file, delimiter=';')

    # Write variable names and metrics
    for key, value in SSVEP_metrics_con.items():
        
        writer.writerow([key,value])


## Save output curves: PSD
with open(path_con_spectra_PSD, 'w', newline='') as file:
    
    # Open CSV writer
    writer = csv.writer(file, delimiter=';')

    # Write headers & data for PSD spectra
    for row in PSD_spectra_con:
        
        writer.writerow(row)


## Save output curves: SSVEP
with open(path_con_curves_SSVEP, 'w', newline='') as file:
    
    # Open CSV writer
    writer = csv.writer(file, delimiter=';')

    # Write headers & data for SSVEP curves
    for row in SSVEP_curves_con:
        
        writer.writerow(row)
    


# %% Save output files: Experimental

## Save processed EEG data file
mne.export.export_raw(path_exp_EEG, raw_clean_exp, fmt = 'edf')


## Save output metrics: PSD
with open(path_exp_metrics_PSD, 'w', newline='') as file:
    
    # Open CSV writer
    writer = csv.writer(file, delimiter=';')

    # Write variable names and metrics
    for key, value in PSD_metrics_exp.items():
        
        writer.writerow([key,value])
        

## Save output metrics: SSVEP
with open(path_exp_metrics_SSVEP, 'w', newline='') as file:
    
    # Open CSV writer
    writer = csv.writer(file, delimiter=';')

    # Write variable names and metrics
    for key, value in SSVEP_metrics_exp.items():
        
        writer.writerow([key,value])


## Save output curves: PSD
with open(path_exp_spectra_PSD, 'w', newline='') as file:
    
    # Open CSV writer
    writer = csv.writer(file, delimiter=';')

    # Write headers & data for PSD spectra
    for row in PSD_spectra_exp:
        
        writer.writerow(row)


## Save output curves: SSVEP
with open(path_exp_curves_SSVEP, 'w', newline='') as file:
    
    # Open CSV writer
    writer = csv.writer(file, delimiter=';')

    # Write headers & data for SSVEP curves
    for row in SSVEP_curves_exp:
        
        writer.writerow(row)
        
        
        
        
        
        
        
        
        
        


