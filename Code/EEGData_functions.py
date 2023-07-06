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
import matplotlib.pyplot as plt



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
    
    # Rename channels (original channel names needed to match Neurofax headbox)
    raw.rename_channels({'Cz':'Oz', 'P3':'PO3', 'P4':'PO4', 'Pz':'POz'})
    
    # Re-reference all ROI channels to Fz
    raw.set_eeg_reference(ref_channels=['Fz'])
    
    # Keep only ROI channels
    raw.pick_channels(['O1','O2','Oz','PO3','PO4','POz'], ordered=True)
    
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
    
    epoch_len : int
    Length of scored epochs
    
    filename : str
	 Path to epoch report file in .txt format

    Output
    -------
    data : ndarray
	 Array containing data points and assigned stages
    
    raw : MNE object
    Original raw object with added annotations for epochs

""" 

def assign_epochs(raw, epoch_len, filename):
    
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
            
        elif stage == 'N1': # Sleep stage 1 
            
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
    
    
    
# %% Function: select_epochs

"""
    Construct and select epochs for PSD analysis.
    
    Input
    ----------
    raw : MNE Raw object
	Output of assign_epochs()
    
    epoch_len : int
    Length of scored epochs
    
    event_id : list of int
    List of stages to include in epoch selection. 0=wake, 1=N1, 2=N2, 3=N3, 4=REM

    Output
    -------
    epochs : MNE Epochs object
	Selection of 30 s trials for PSD analyses

"""

def select_epochs(raw, epoch_len, event_id):
    
    # Turn annotations into events
    events, _ = mne.events_from_annotations(raw, verbose=False)
    
    # Create epochs
    epochs = mne.Epochs(
        raw,
        events=events,
        event_id=event_id, # events to consider; here, sleep stages 
        tmin=0, # start trials at beginning of scored epochs
        tmax=epoch_len, # end trials at end of scored epochs
        reject=dict(eeg = 0.001),  # Trial rejection criterion: 1 mV peak to peak
        baseline=None,
        verbose=False
    )
    
    
    return epochs



# %% Function: compute_PSD
"""
    Source code: https://mne.tools/stable/auto_tutorials/time-freq/50_ssvep.html

    Compute PSD spectra and SNR values of epochs, then plot them.
    
    Input
    ----------
    epochs : MNE Epochs object
    Output of select_epochs()
    
    epoch_len : int
    Length of scored epochs
    
    stage : int
    Stage the epochs are assigned to (for plot title)

    Output
    -------
    PSD_40Hz : int
    Absolute PSD value at / near 40 Hz in dB
    
    SNR_40Hz : int
    Absolute SNR value corresponding to PSD_40Hz
    
    PSD_spectrum : array
    Average PSD spectrum across epochs and channels
    
    SNR_spectrum : array
    Average SNR spectrum of PSD values across epochs and channels

"""

def compute_PSD(epochs, epoch_len, stage):
    
    ## Compute PSD
    
    # Get sampling rate
    sfreq = epochs.info["sfreq"]
    
    # Compute average PSD spectra per stage
    spectrum = epochs.compute_psd(
        "welch",
        n_fft=int(sfreq * epoch_len), # length of FFT
        tmin=0,
        tmax=epoch_len,
        fmin=1, # min. frequency to include in spectra
        fmax=100, # max. frequency to include in spectra
        window='hamming',
        verbose=False
    )
    
    # Access spectra
    # psds: ndarray with shape (n_epochs, n_channels, n_freqs)
    # freqs: array with all frequency levels
    psds, freqs = spectrum.get_data(return_freqs=True)
    
    # Find index of frequency bin closest to stimulation frequency (here, 40 Hz)
    idx_bin_40Hz = np.argmin(abs(freqs - 40))
    
    # Find index of lower boundary for target frequency range (here, 39.5 Hz)
    idx_bin_lower = np.argmin(abs(freqs - 39.5))

    # Half length of target frequency range (in nr. of frequencies)
    bin_len = idx_bin_40Hz - idx_bin_lower

    
    ## Compute SNR
    
    # Nr. of neighboring frequencies used to compute noise level, on each side (here, 'noise' = [38-39.5 Hz] + [40.5-42 Hz])
    noise_n_neighbor_freqs = bin_len*3

    # Exclude immediately neighboring frequency bins in noise level calculation (here, 'signal' = [39.5-40.5 Hz])
    noise_skip_neighbor_freqs = bin_len
    
    # Construct a kernel that calculates the mean of the neighboring frequencies
    averaging_kernel = np.concatenate((
        np.ones(noise_n_neighbor_freqs),
        np.zeros(2 * noise_skip_neighbor_freqs + 1),
        np.ones(noise_n_neighbor_freqs)))
    averaging_kernel /= averaging_kernel.sum()

    # Calculate the mean of the neighboring frequencies by convolving with the averaging kernel
    mean_noise = np.apply_along_axis(
        lambda psd_: np.convolve(psd_, averaging_kernel, mode='valid'),
        axis=-1, arr=psds
    )

    # The mean is not defined on the edges so we will pad it with nas. The
    # padding needs to be done for the last dimension only so we set it to
    # (0, 0) for the other ones.
    edge_width = noise_n_neighbor_freqs + noise_skip_neighbor_freqs
    pad_width = [(0, 0)] * (mean_noise.ndim - 1) + [(edge_width, edge_width)]
    mean_noise = np.pad(
        mean_noise, pad_width=pad_width, constant_values=np.nan
    )
    
    # Compute SNR spectra
    snrs = psds / mean_noise
    
    
    ## Plot spectra
    
    fig, axes = plt.subplots(2, 1, sharex='all', sharey='none', figsize=(8, 5))
    freq_range = range(np.where(np.floor(freqs) == 1.)[0][0], np.where(np.ceil(freqs) == 100 - 1)[0][0])
    
    # PSD spectrum
    psds_plot = 10 * np.log10(psds)
    psds_mean = psds_plot.mean(axis=(0, 1))[freq_range]
    psds_std = psds_plot.std(axis=(0, 1))[freq_range]
    axes[0].plot(freqs[freq_range], psds_mean, color='b')
    axes[0].fill_between(
        freqs[freq_range], psds_mean - psds_std, psds_mean + psds_std,
        color='b', alpha=.2)
    axes[0].set(title="PSD spectrum, stage "+str(stage), ylabel='Power Spectral Density [dB]')
    
    # SNR spectrum
    snr_mean = snrs.mean(axis=(0, 1))[freq_range]
    snr_std = snrs.std(axis=(0, 1))[freq_range]
    
    axes[1].plot(freqs[freq_range], snr_mean, color='r')
    axes[1].fill_between(
        freqs[freq_range], snr_mean - snr_std, snr_mean + snr_std,
        color='r', alpha=.2)
    axes[1].set( title="SNR spectrum, stage "+str(stage), xlabel='Frequency [Hz]', ylabel='SNR', ylim=[-2, 30], xlim=[1, 100])
    fig.show()
    
    
    ## Get metrics
    
    # Get SNRs in defined range around target frequency (allowing for slightly different individual SSVEP frequencies)
    snrs_40Hz = snrs[0,:,(idx_bin_40Hz-bin_len):(idx_bin_40Hz+bin_len)]

    # Average across occipital electrodes
    snrs_40Hz_avg = snrs_40Hz.mean(axis=0)

    # Get maximum averaged SNR in that range
    idx_max_SNR = np.argmax(snrs_40Hz_avg) # index in target frequency subset

    # Get exact frequency corresponding to highest SNR (in case it's not exactly 40 Hz)
    max_SNR_freq = freqs[idx_bin_40Hz - (bin_len - idx_max_SNR)]
    
    # Absolute PSD value at / near 40 Hz in dB
    PSD_40Hz = psds_mean[idx_bin_40Hz - (bin_len - idx_max_SNR)]
    
    # Absolute SNR value corresponding to PSD_40Hz
    SNR_40Hz = snrs_40Hz_avg[idx_max_SNR]
    
    # Average PSD spectrum across epochs and channels
    PSD_spectrum = psds_mean
    
    # Average SNR spectrum across epochs and channels
    SNR_spectrum = snr_mean
    
    
    ## Print & return results
    
    print('PSD SNR: ' + str(round(SNR_40Hz,2)))
    print('Absolute PSD value (dB): ' + str(round(PSD_40Hz,2)))
    print('Corresponding frequency (Hz): ' + str(round(max_SNR_freq,2)))
    
    return PSD_40Hz, SNR_40Hz, PSD_spectrum, SNR_spectrum
    
    
    
    
    
    
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
    
    
    