# -*- coding: utf-8 -*-
"""
Author: Laura Hainke
Date: 06.2023
Functionality: Script to import and process EEG data (Gamma-Sleep study).
Assumptions:
    - 1 EDF file for exp recording, session 01 (~20 min)
    - 1 EDF file for whole con recording, session 02 (~8 h)
    - 1 EDF file for sleep exp recording, session 03 (~8 h)
    - 1 .txt file with scored epochs for con recording, session 02
    - 1 .txt file with scored epochs for exp recording, session 03
Notes:

"""


# %% Environment Setup

# Import custom functions
from EEGData_functions import load_edf, assign_epochs

# Import packages
import csv
import mne



# %% Paths to files

# Get participant number from user
subject_nr = input("Subject number: ")


## Input data

# Path to folders
path_in = ["D:/Documents/Gamma_Sleep/Data/Raw/" + subject_nr]

# Path to session 01 EEG data file
path_ses01_EEG = [path_in + "/Session01/" + subject_nr + "_session01_raw-EEG.edf"]

# Path to session 02 EEG data file
path_ses02_EEG = [path_in + "/Session02/" + subject_nr + "_session02_raw-EEG.edf"]

# Path to session 02 epoch report file
path_ses02_epochs = [path_in + "/Session02/" + subject_nr + "_session02_epoch-report.edf"]

# Path to session 03 EEG data file
path_ses03_EEG = [path_in + "/Session03/" + subject_nr + "_session03_raw-EEG.edf"]

# Path to session 03 epoch report file
path_ses03_epochs = [path_in + "/Session03/" + subject_nr + "_session03_epoch-report.edf"]


## Output data
# NOTE: sessions 01 and 03 are merged into an 'experimental' condition; session 02 = 'control'

# Path to folders
path_out = ["D:/Documents/Gamma_Sleep/Data/Derivatives/" + subject_nr]

# Path to processed EEG data file, control condition
path_con_EEG = [path_out + "/Control/" + subject_nr + "_control_processed-EEG.edf"]

# Path to output EEG metrics data file, control condition
path_con_metrics_PSD = [path_out + "/Control/" + subject_nr + "_control_PSD-output-metrics.csv"]
path_con_metrics_SSVEP = [path_out + "/Control/" + subject_nr + "_control_SSVEP-output-metrics.csv"]

# Path to output EEG curves data files, control condition
path_con_spectra_PSD = [path_out + "/Control/" + subject_nr + "_control_PSD-output-spectra.csv"]
path_con_curves_SSVEP = [path_out + "/Control/" + subject_nr + "_control_SSVEP-output-curves.csv"]

# Path to processed EEG data file, experimental condition
path_exp_EEG = [path_out + "/Experimental/" + subject_nr + "_experimental_processed-EEG.edf"]

# Path to output EEG metrics data file, experimental condition
path_exp_metrics_PSD = [path_out + "/Experimental/" + subject_nr + "_experimental_PSD-output-metrics.csv"]
path_exp_metrics_SSVEP = [path_out + "/Experimental/" + subject_nr + "_experimental_SSVEP-output-metrics.csv"]

# Path to output EEG curves data files, experimental condition
path_exp_spectra_PSD = [path_out + "/Experimental/" + subject_nr + "_experimental_PSD-output-spectra.csv"]
path_exp_curves_SSVEP = [path_out + "/Experimental/" + subject_nr + "_experimental_SSVEP-output-curves.csv"]



# %% Load & process control data

# Load data, select ROI channels
raw_s02 = load_edf(path_ses02_EEG)

# Assign scored epochs to data
data_epochs_s02 = assign_epochs(raw_s02, path_ses02_epochs)

# Reject bad epochs
raw_clean_con = []

# Compute average PSD per condition
PSD_spectra_con, PSD_metrics_con = [] 

# Compute average SSVEP per condition
SSVEP_curves_con, SSVEP_metrics_con = []



# %% Load & process experimental data

# Load data, select ROI channels
raw_s01 = load_edf(path_ses01_EEG) # Session 01: experimental, wake (20 min)
raw_s03 = load_edf(path_ses03_EEG) # Session 03: experimental, sleep (8 h)

# Assign scored epochs to data
data_epochs_s03 = assign_epochs(raw_s03, path_ses03_epochs)

# Reject bad epochs
raw_clean_exp = []

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
        
        
        
        
        
        
        
        
        
        


