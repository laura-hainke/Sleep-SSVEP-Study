# -*- coding: utf-8 -*-
'''
Author: Laura Hainke
Date: 01.2024
Functionality: Script to import and process EEG data; Gamma-Sleep study
Assumptions: Files as defined in all_paths[]; GammaSleep_EEG_processing_functions.py in same directory

'''


# %% Environment Setup

# Import packages
import pandas as pd 
import numpy as np
import os
import yasa
import mne
import json

# Define directory containing code
os.chdir('C:/Users/Mitarbeiter/Documents/Gamma_Sleep/Github_Repo/Gamma-Sleep/Code/Processing')

# Import custom functions
from GammaSleep_EEG_processing_functions import load_raw, import_triggers, import_triggers_DC, score_sleep, linear_interpolation, select_annotations, create_epochs, compute_PSD, compute_SSVEP

# Initialize dataframe containing all paths to folders and files
all_paths = {}

# Path to folders with all raw and derivative data 
all_paths['path_raw'] = str('C:/Users/Mitarbeiter/Documents/Gamma_Sleep/Data/Raw/')
all_paths['path_derivatives'] = str('C:/Users/Mitarbeiter/Documents/Gamma_Sleep/Data/Derivatives/')

# Generate subject numbers as strings, to loop over
subject_IDs = [str(i).zfill(2) for i in range(0,10)]

# Mark datasets to remove
datasets_to_exclude = ['03','15']

# Option: apply linear interpolation procedure to all datasets or not (supplementary analyses)
lin_int_apply = input('\nStarting EEG preprocessing pipeline for GammaSleep. \nShould linear interpolation be applied (y/n)? ')
                            
            

# %% Loop over all subjects

for subject_nr in subject_IDs:

    # Skip excluded datasets   
    if subject_nr in datasets_to_exclude:
        continue
     
    print('\nNEW ITERATION\nSUBJECT:', subject_nr)
     
     

# %% Loop over both conditions

    for condition in ['con','exp']:
         
        print('\nCONDITION:', condition)
         
         
         
        # %% Paths to files
        
        try: 
        
            all_paths['path_in'] = all_paths['path_raw'] + subject_nr
            all_paths['path_out'] = all_paths['path_derivatives'] + subject_nr
        
            ## Input   
            
            # Personal data file (located in Derivatives folder)
            all_paths['path_in_demographics'] = str(all_paths['path_out'] + '/REDCap/' + subject_nr + '_personal-data.csv')
            
            # Subjective sleep quality scale file
            all_paths['path_in_gsqs'] = str(all_paths['path_in'] + '/REDCap/' + subject_nr + '_sleep-quality.csv')
            
            # EEG data
            all_paths['path_in_ses01_EEG'] = str(all_paths['path_in'] + '/Session01/' + subject_nr + '_session01_raw-EEG.edf')
            all_paths['path_in_ses02_EEG'] = str(all_paths['path_in'] + '/Session02/' + subject_nr + '_session02_raw-EEG.edf')
            all_paths['path_in_ses03_EEG'] = str(all_paths['path_in'] + '/Session03/' + subject_nr + '_session03_raw-EEG.edf')
            
            # Annotations
            all_paths['path_in_ses01_annotations'] = str(all_paths['path_in'] + '/Session01/' + subject_nr + '_session01_raw-EEG_annotations.edf')
            all_paths['path_in_ses02_annotations'] = str(all_paths['path_in'] + '/Session02/' + subject_nr + '_session02_raw-EEG_annotations.edf')
            all_paths['path_in_ses03_annotations'] = str(all_paths['path_in'] + '/Session03/' + subject_nr + '_session03_raw-EEG_annotations.edf')
            
            # JSON metadata
            all_paths['path_in_ses02_metadata'] = str(all_paths['path_in'] + '/Session02/' + subject_nr + '_session02_metadata.json')
            all_paths['path_in_ses03_metadata'] = str(all_paths['path_in'] + '/Session03/' + subject_nr + '_session03_metadata.json')
            
            ## Output 
            
            if condition == 'con':
                all_paths['path_substrings'] = ['/Control/', '_control']
            elif condition == 'exp':
                all_paths['path_substrings'] = ['/Experimental/', '_experimental']
                
            # Path to output EEG metrics data files
            all_paths['path_out_metrics_PSD'] = str(all_paths['path_out'] + all_paths['path_substrings'][0] + subject_nr + all_paths['path_substrings'][1] + '_PSD-output-metrics.csv')
            all_paths['path_out_metrics_SSVEP'] = str(all_paths['path_out'] + all_paths['path_substrings'][0] + subject_nr + all_paths['path_substrings'][1] + '_SSVEP-output-metrics.csv')
            
            # Path to output EEG curves data files
            all_paths['path_out_spectra_PSD'] = str(all_paths['path_out'] + all_paths['path_substrings'][0] + subject_nr + all_paths['path_substrings'][1] + '_PSD-output-spectra.csv')
            all_paths['path_out_curves_SSVEP'] = str(all_paths['path_out'] + all_paths['path_substrings'][0] + subject_nr + all_paths['path_substrings'][1] + '_SSVEP-output-curves.csv')
            
            # Path to output sleep variables
            all_paths['path_out_sleep'] = str(all_paths['path_out'] + all_paths['path_substrings'][0] + subject_nr + all_paths['path_substrings'][1] + '_sleep-data.csv')
            
        except:
            
            print('\nERROR: subject',subject_nr,', condition',condition,', section: paths\n')
        
    
    
        # %% Load raw EEG file
        
        try:
            
            if condition == 'con':
                
                # Access metadata
                with open(all_paths['path_in_ses02_metadata'], 'r') as openfile:
                    metadata = json.load(openfile)
                
                # Load s02 data, get PSG and EEG raw objects for overnight data
                raw_PSG, raw_EEG = load_raw(all_paths['path_in_ses02_EEG'], metadata['bad_channels'])
            
            elif condition == 'exp':
                
                # Access metadata
                with open(all_paths['path_in_ses03_metadata'], 'r') as openfile:
                    metadata = json.load(openfile)
                
                # Exception for subject 02, recording for session 01 was paused. Merging into one EDF file did not work
                if subject_nr == '02':
                    _, raw_s01a_EEG = load_raw(str(all_paths['path_in_ses01_EEG'][0:-12]+'a_raw-EEG.edf'), metadata['bad_channels'])
                    _, raw_s01b_EEG = load_raw(str(all_paths['path_in_ses01_EEG'][0:-12]+'b_raw-EEG.edf'), metadata['bad_channels'])
                    raw_s01_EEG = mne.concatenate_raws([raw_s01a_EEG.copy(),raw_s01b_EEG.copy()])
                else:
                    # Load s01 data, get raw object for EEG data (no PSG needed, since all W)
                    _, raw_s01_EEG = load_raw(all_paths['path_in_ses01_EEG'], metadata['bad_channels'])
                
                # Load s03 data, get PSG and EEG raw objects for overnight data
                raw_PSG, raw_EEG = load_raw(all_paths['path_in_ses03_EEG'], metadata['bad_channels'])
            
        except:
            
            print('\nERROR: subject',subject_nr,', condition',condition,', section: loading raw data\n')
            
        
        
        # %% Access triggers
        
        try: 
            
            if metadata['exception_trigger_source'] == True: # import triggers from DC channel (exception)
            
                # Threshold for DC channel trigger in mV, valid for all affected datasets
                threshold_mV = 300
            
                if condition == 'con':      
                        
                    triggers = import_triggers_DC(all_paths['path_in_ses02_EEG'], threshold_mV)
                    
                elif condition == 'exp':
                    
                    if subject_nr == '02': # exception: 2 files, getting triggers for each
                        triggers_s01a = import_triggers_DC(str(all_paths['path_in_ses01_EEG'][0:-12]+'a_raw-EEG.edf'), threshold_mV)
                        triggers_s01b = import_triggers_DC(str(all_paths['path_in_ses01_EEG'][0:-12]+'b_raw-EEG.edf'), threshold_mV)
                        # triggers of 1st half, directly followed by triggers of 2nd half shifted by length of 1st half
                        triggers_s01 = np.concatenate((triggers_s01a, triggers_s01b+len(raw_s01a_EEG))) 
                    else:
                        triggers_s01 = import_triggers_DC(all_paths['path_in_ses01_EEG'], threshold_mV)
                        
                    triggers = import_triggers_DC(all_paths['path_in_ses03_EEG'], threshold_mV)
                    
            else: # import triggers from annotations file (default)
                
                if condition == 'con':
                    triggers = import_triggers(None, all_paths['path_in_ses02_annotations'], raw_EEG)
                elif condition == 'exp':
                    triggers_s01, triggers = import_triggers(all_paths['path_in_ses01_annotations'], all_paths['path_in_ses03_annotations'], raw_EEG)
                    
        except:
            
            print('\nERROR: subject',subject_nr,', condition',condition,', section: accessing triggers\n')
        
        
        
        # %% Exclude triggers from overnight data
        
        try:
            
            if metadata['exception_trigger_exclusion'] == True:
                
                # Get start and end points of period to be excluded
                exclusion_start_min = metadata['trigger_exclusion_start_min']
                exclusion_end_min = metadata['trigger_exclusion_end_min']
                
                # Transform into data points
                exclusion_start_point = int(exclusion_start_min)*60*1000
                exclusion_end_point = int(exclusion_end_min)*60*1000
                
                # Find triggers closest to indicated data points
                exclusion_start = (abs(triggers - exclusion_start_point)).argmin()
                exclusion_end = (abs(triggers - exclusion_end_point)).argmin()
                
                # Keep only intended triggers
                triggers = np.concatenate((triggers[0:exclusion_start], triggers[exclusion_end:]))
        
        except:
            
            print('\nERROR: subject',subject_nr,', condition',condition,', section: excluding triggers\n')
            
        
        
        # %% Apply linear interpolation (if indicated by user)
            
        try:
            
            if lin_int_apply == 'y':
                
                if condition == 'exp':
                    # Run linear interpolation, S01
                    print('Applying linear interpolation to S01...')
                    raw_s01_EEG = linear_interpolation(raw_s01_EEG, triggers_s01)
                
                # Run linear interpolation, S02 or S03
                print('Applying linear interpolation to overnight data...')
                raw_EEG = linear_interpolation(raw_EEG, triggers)
        
        except:
            
            print('\nERROR: subject',subject_nr,', condition',condition,', section: linear interpolation\n')
        
        
        
        # %% Score sleep, get epochs, store metrics
        
        try:
            
        ## Session 01 (wake exp only)
            if condition == 'exp':
                # Get nr. of epochs in recording
                n_wake_epochs = np.floor(raw_s01_EEG.__len__() / raw_s01_EEG.info['sfreq'] / 30)
                
                # Create a 'hypnogram' containing only stage 0
                hypno_s01 = np.zeros(int(n_wake_epochs), dtype=int) 
                
                # Upsample to match data (needed for SSVEP analysis)
                hypno_up_s01 = yasa.hypno_upsample_to_data(hypno_s01, sf_hypno=1/30, data=raw_s01_EEG)
                
                # Turn stages into annotations, no uncertain epochs
                raw_s01_EEG = select_annotations(raw_s01_EEG, hypno_s01, [])
            
            
            ## Full night (session 02 or 03)
            
            # Run YASA algorithm
            hypno, hypno_up, uncertain_epochs, sleep_stats = score_sleep(raw_PSG, raw_EEG, metadata['bad_channels'], all_paths['path_in_demographics'])
            
            # Turn stages scored with enough confidence into annotations
            raw_EEG = select_annotations(raw_EEG, hypno, uncertain_epochs)
            
            
            ## Metrics
            
            # Get subset of sleep metrics of interest 
            sleep_data = {k: sleep_stats[k] for k in ('SOL','TST','WASO','%N1','%N2','%N3','%REM')}
            
            # Access GSQS sum score
            gsqs = pd.read_csv(all_paths['path_in_gsqs'])
            if condition == 'con':
                gsqs_sum = gsqs.gsqs_sum_con[0]
            elif condition == 'exp':
                gsqs_sum = gsqs.gsqs_sum_exp[0]
            
            sleep_data['GSQS_sum'] = gsqs_sum
            
            # Control condition: subtract 12 min from sleep onset latency (10 min W by design + 2 min to lay down)
            if condition == 'con':
                # Set to 0 if negative. This happens if the person drifted into N1 during the 10 min they were meant to stay awake
                if sleep_data['SOL'] - 10 < 0:
                    sleep_data['SOL'] = 0
                else: 
                    sleep_data['SOL'] = sleep_data['SOL'] - 12
            
            # Convert metrics dict into panda, save to CSV
            sleep_data = pd.DataFrame.from_dict(sleep_data, orient='index')
            sleep_data.to_csv(all_paths['path_out_sleep'], header=False)
            
        except:
            
            print('\nERROR: subject',subject_nr,', condition',condition,', section: sleep scoring\n')
                


        # %% Loop over stages to compute PSD & SNR
        
        try:
            
            # Initialize dict for output metrics
            PSD_metrics = dict()
            
            # Initialize array for spectra
            PSD_spectra = []
            
            # Loop
            for stage in [0,2,3,4]:
                
                # Select correct raw object and triggers
                if stage == 0 and condition == 'exp':
                    
                    raw_loop = raw_s01_EEG # for stage 0 exp, only data from s01 is of interest
                    triggers_loop = triggers_s01
                    
                else:
                    
                    raw_loop = raw_EEG
                    triggers_loop = triggers
                
                # Create and select epochs (=30 sec trials) for PSD analyses of current stage
                epochs_stage = create_epochs(raw_loop, triggers_loop, event_id=stage)
                
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
                
                # Store metrics in dict
                if stage == 0: # Wake
                    
                    PSD_metrics['PSD_ntrials_W'] = PSD_ntrials
                    PSD_metrics['PSD_40Hz_W'] = PSD_40Hz
                    PSD_metrics['PSD_SNR_W'] = SNR_40Hz
                    
                elif stage == 2: # N2
                
                    PSD_metrics['PSD_ntrials_N2'] = PSD_ntrials
                    PSD_metrics['PSD_40Hz_N2'] = PSD_40Hz
                    PSD_metrics['PSD_SNR_N2'] = SNR_40Hz
                    
                elif stage == 3: # N3
                
                    PSD_metrics['PSD_ntrials_N3'] = PSD_ntrials
                    PSD_metrics['PSD_40Hz_N3'] = PSD_40Hz
                    PSD_metrics['PSD_SNR_N3'] = SNR_40Hz
                    
                elif stage == 4: # REM
                
                    PSD_metrics['PSD_ntrials_REM'] = PSD_ntrials
                    PSD_metrics['PSD_40Hz_REM'] = PSD_40Hz
                    PSD_metrics['PSD_SNR_REM'] = SNR_40Hz
            
                # Store spectra in array
                PSD_spectra.append(np.ndarray.tolist(PSD_spectrum))
                PSD_spectra.append(np.ndarray.tolist(SNR_spectrum))
                    
            
            ## Create pandas dataframes to export PSD results
            
            # Turn array with spectra into pandas dataframe, transpose
            PSD_spectra = pd.DataFrame(data=PSD_spectra)
            PSD_spectra = PSD_spectra.transpose()
            
            # Add variable names as headers
            PSD_spectra.columns=['W_PSD','W_SNR','N2_PSD','N2_SNR','N3_PSD','N3_SNR','REM_PSD','REM_SNR']
            
            # Convert metrics dict into pandas as well
            PSD_metrics = pd.DataFrame.from_dict(PSD_metrics, orient='index')
            
            # Save to CSV
            PSD_metrics.to_csv(all_paths['path_out_metrics_PSD'], header=False)
            PSD_spectra.to_csv(all_paths['path_out_spectra_PSD'])
            
        except:
            
            print('\nERROR: subject',subject_nr,', condition',condition,', section: PSD computation\n')
        

        
        # %% Loop over stages to compute SSVEP & SNR
        
        try:
            
            # Define ROI channels, without bad channels
            roi_ch = ['PO3','PO4','POz','O1','O2','Oz']
            [i for i in roi_ch if i not in metadata['bad_channels']]
            
            # Access raw ROI data as array, convert from Volts to microVolts; get average of the ROI channels
            if condition == 'exp':
                data_s01 = raw_s01_EEG.get_data(picks=roi_ch) * 1e6
                data_s01 = np.mean(data_s01, axis=0)
            
            data = raw_EEG.get_data(picks=roi_ch) * 1e6
            data = np.mean(data, axis=0) 
            
            # Initialize dict for output metrics
            SSVEP_metrics = dict()
            
            # Initialize array for SSVEP curves
            SSVEP_curves = []
            
            # Compute average SSVEP per condition
            for stage in [0,2,3,4]:
                
                # Select correct raw object and triggers
                if stage == 0 and condition == 'exp':
                    
                    data_loop = data_s01 # for stage 0 exp, only data from s01 is of interest
                    triggers_loop = triggers_s01
                    hypno_up_loop = hypno_up_s01
                    
                else:
                    
                    data_loop = data
                    triggers_loop = triggers
                    hypno_up_loop = hypno_up
                 
                # Compute SSVEP and SNR for current stage + metrics
                SSVEP_amp, SSVEP_SNR, SSVEP_ntrials, SSVEP_curve = compute_SSVEP(data_loop, triggers_loop, hypno_up_loop, stage, computeSNR=True)
            
                # Store metrics in dict
                if stage == 0: # Wake
                    
                    SSVEP_metrics['SSVEP_ntrials_W'] = SSVEP_ntrials
                    SSVEP_metrics['SSVEP_PTA_W'] = SSVEP_amp
                    SSVEP_metrics['SSVEP_SNR_W'] = SSVEP_SNR
                    
                elif stage == 2: # N2
                
                    SSVEP_metrics['SSVEP_ntrials_N2'] = SSVEP_ntrials
                    SSVEP_metrics['SSVEP_PTA_N2'] = SSVEP_amp
                    SSVEP_metrics['SSVEP_SNR_N2'] = SSVEP_SNR
                    
                elif stage == 3: # N3
                
                    SSVEP_metrics['SSVEP_ntrials_N3'] = SSVEP_ntrials
                    SSVEP_metrics['SSVEP_PTA_N3'] = SSVEP_amp
                    SSVEP_metrics['SSVEP_SNR_N3'] = SSVEP_SNR
                    
                elif stage == 4: # REM
                
                    SSVEP_metrics['SSVEP_ntrials_REM'] = SSVEP_ntrials
                    SSVEP_metrics['SSVEP_PTA_REM'] = SSVEP_amp
                    SSVEP_metrics['SSVEP_SNR_REM'] = SSVEP_SNR
            
                # Store spectra in array
                SSVEP_curves.append(np.ndarray.tolist(SSVEP_curve))
            
            
            ## Create pandas dataframes to export SSVEP results
            
            # Turn array with spectra into pandas dataframe, transpose
            SSVEP_curves = pd.DataFrame(data=SSVEP_curves)
            SSVEP_curves = SSVEP_curves.transpose()
            
            # Add variable names as headers
            SSVEP_curves.columns=['W_SSVEP','N2_SSVEP','N3_SSVEP','REM_SSVEP']
            
            # Convert metrics dict into pandas as well
            SSVEP_metrics = pd.DataFrame.from_dict(SSVEP_metrics, orient='index')
            
            # Save to CSV
            SSVEP_metrics.to_csv(all_paths['path_out_metrics_SSVEP'], header=False)
            SSVEP_curves.to_csv(all_paths['path_out_curves_SSVEP'])
    
        except:
            
            print('\nERROR: subject',subject_nr,', condition',condition,', section: SSVEP computation\n')




