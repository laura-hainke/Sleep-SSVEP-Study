# -*- coding: utf-8 -*-
"""

Step 3 - function to load sleep recording (BDF), perform automated sleep staging using YASA, predict sleep statistics / hypnogram / spectrogram, get epochs above 70 % probability

"""


# =============================================================================
# Inputs:
#   - file_name: 'EXG_flicker' or 'EXG_blackout' (common file name for csv and bdf)
#   - age: integer age of participant 
#   - male: True or False

# Outputs:
#   - sleep_stats: sleep statistics calculated by YASA (e.g., % of time per stage)
#   - hypnogram_np: array with 1 predicted stage per epoch (0 = Wake; 1 = N1 sleep; 2 = N2 sleep; 3 = N3 sleep; 4 = REM sleep), to assign segments to stages
#   - ts_epoch_start_np: array of timestamps, one for the start of each epoch
# =============================================================================


### Libraries

import mne # to load BDF files
import yasa # main library
import numpy as np # for data structures
import pandas as pd # for writing to csv


def sleep_staging(file_name, age, male):
        
    ### Data import
    
    # Load the EDF file - in Explore, since it's 24 bit, it's a BDF+ file
    # Note: after converting BIN file using bin2edf, change the extension manually from edf to bdf and use read_raw_bdf instead of read_raw_edf
    raw = mne.io.read_raw_bdf(file_name + '.bdf', preload=True)
    
    # Drop unnecessary channels: time stamps & photodiode channel
    raw.drop_channels(['TimeStamp','ch8'])
    
    # Redefine channel names
    ch_names = {'ch1':'C3', 'ch2':'C4', 'ch3':'TP10', 'ch4':'POz', 'ch5':'O1', 'ch6':'O2', 'ch7':'EOG'}
    # Rename channels
    raw.rename_channels(ch_names)
    
    # Downsample to 100 Hz for faster computation / assumed for spectrogram
    raw.resample(100)        
    
    # Access data
    data = raw.get_data() * 1e6 # convert from Volts to microVolts
    # Get channel names
    chan = raw.ch_names
    
    
    ### Automated sleep staging
    
    # Create object
    sls = yasa.SleepStaging(raw, eeg_name='C4', eog_name='EOG', metadata=dict(age=age, male=male))
    # Note: data are automatically downsampled to 100 Hz for faster computation
    # Predict the sleep stages
    hypnogram = sls.predict()
    # Convert "W" to 0, "N1" to 1, etc; 4 is REM
    hypnogram = yasa.hypno_str_to_int(hypnogram)
    
    # Predicted probabilities of each sleep stage at each epoch
    sls.predict_proba()
    # Extract a confidence level (ranging from 0 to 1) for each epoch
    confidence = sls.predict_proba().max(1)
    # Plot it
    # sls.plot_predict_proba()
    # Get list of uncertain epochs (below 70 % probability)
    uncertain_epochs = confidence.loc[confidence < 0.7]
    uncertain_epochs = list(uncertain_epochs.index)
    print(len(uncertain_epochs), 'epochs below 70 % probability')
    
    
    ### Analyses
    
    ## Sleep statistics
    sleep_stats = yasa.sleep_statistics(hypnogram, sf_hyp=1/30) # SR of hypnogram is one value every 30-seconds (staged epochs)
    
    ## Create spectrogram
    # Upsample back to 100 Hz
    hypno_up = yasa.hypno_upsample_to_data(hypnogram, sf_hypno=1/30, data=raw)
    # Plot spectrogram for 1 channel
    yasa.plot_spectrogram(data[chan.index("C4")], 100, hypno_up, fmin=0.5, fmax=25)
            
    
    ### Epochs for SSVEPs
    
    # Get timestamps for beginning of each epoch
    timestamps = pd.read_csv(file_name + '.csv', usecols=[0], dtype=np.float64)
    timestamps = timestamps.squeeze()
    # BDF not giving the correct values (for timestamps only), thus using CSV
    
    # Loop through nr. of epochs, get timestamps for beginning of each epoch (every 30 s)
    ts_epoch_start = []
    for ctr in range(len(hypnogram)+1):
        
        # Include only epochs with enough probability
        if (ctr not in uncertain_epochs):
            ts_epoch_start.append(timestamps[ctr*30000])
    
    # Convert to numpy & save
    ts_epoch_start_np = np.array(ts_epoch_start)
    
    # Same for hypnogram
    hypnogram_np = np.array(hypnogram)
    
    # Display time per stage
    print('\n', file_name[4:], ' - time spent per sleep stage:\n')
    print('N2:', sleep_stats.get('%N2'), '%')
    print('N3:', sleep_stats.get('%N3'), '%')
    print('REM:', sleep_stats.get('%REM'), '%')    
    
    return sleep_stats, hypnogram_np, ts_epoch_start_np
    
    
    
    
    
