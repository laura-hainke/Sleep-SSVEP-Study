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
import yasa
import pandas as pd 



# %% Function: load_raw
"""
    Load raw EEG data in EDF format, split into PSG and EEG, perform basic processing.

    Input
    ----------
    filename : str
    Path to the Nihon Kohden files
        
    bad_ch : list
    Names of bad channels identified visually.
    Examples: [] (no bad channels); ['LEMG'] (1 bad channel); ['C3','LEMG'] (more than 1 bad channel)
    
    Output
    -------
    raw_PSG : MNE raw object
    Processed data in MNE format - PSG channels
    
    raw_EEG : MNE raw object
    Processed data in MNE format - EEG channels

"""

def load_raw(filename,bad_ch):

    ## Load raw file    

    # Go to directory containing files (necessary for read_raw_nihon)
    os.chdir(filename[0:55])
    
    # Load metadata of full raw file in EDF format
    # Note: not yet preloading data to save memory
    raw = mne.io.read_raw_edf(filename, preload=False)
    
    # Rename channels whose original names needed to match Neurofax headbox
    raw.rename_channels({'Cz':'Oz', 'P3':'PO3', 'P4':'PO4', 'Pz':'POz', 'PG1':'LEOG', 'PG2':'REOG', 'T1':'LEMG', 'T2':'REMG'})
    
    # Mark bad channels, if any
    raw.info['bads'] = bad_ch
    
    
    ## PSG channels
    
    # Add an exception catcher if something fails (e.g., memory overload)
    try:
    
        # Make a copy of the raw object
        raw_PSG = raw.copy()
        
        # Get the channel subset for PSG
        raw_PSG.pick(['C3','C4','LEOG','REOG','LEMG','REMG','A1','A2'])
        
        # Load data into memory
        raw_PSG.load_data()
        
        # Downsample to 100 Hz for faster computation; assumed for spectrogram
        raw_PSG.resample(100) 
        
        # Apply band-pass filter
        raw_PSG.filter(l_freq=0.1, h_freq=45)
        
        # Re-reference channels to mastoid average
        raw_PSG.set_eeg_reference(ref_channels=['A1','A2'])
        
        # Correctly label EOG and EMG channels
        raw_PSG.set_channel_types({'LEOG':'eog', 'REOG':'eog', 'LEMG':'emg', 'REMG':'emg'})
        
    except:
        
        print('Raw PSG object could not be created properly!')
        raw_PSG = None
    
    
    ## EEG channels
    
    # Add an exception catcher if something fails (e.g., memory overload)
    try:
    
        # Make a copy of the raw object
        raw_EEG = raw.copy()
        
        # Get the channel subset for EEG
        raw_EEG.pick(['PO3','PO4','POz','O1','O2','Oz','A1','A2'])
        
        # Load data into memory
        raw_EEG.load_data()
        
        # Re-reference channels to mastoid average
        raw_EEG.set_eeg_reference(ref_channels=['A1','A2'])
    
    except:
        
        print('Raw EEG object could not be created properly!')
        raw_EEG = None
            
        
    # Move back to main directory
    os.chdir('C:/Users/Mitarbeiter/Documents/Gamma_Sleep/Code/Processing/')
        

    return raw_PSG, raw_EEG


    
# %% Function: score_sleep

"""
    Source code: https://raphaelvallat.com/yasa/build/html/api.html

    Use YASA package to automatically score sleep stages and compute PSG metrics.
    
    Input
    ----------
    raw_PSG : MNE object
    Output of load_raw() for PSG channels
    
    raw_EEG : MNE object
    Output of load_raw() for EEG channels
    
    bad_ch : list
    Names of bad channels identified visually
    
    path_demographics : str
    Path to participant's demographics data file

    Output
    -------
    hypnogram : array
    Array containing epochs scored by YASA
    
    hypno_up : array
    Upsampled hypnogram to match EEG data points
    
    uncertain_epochs : list
    List of epoch indices scored with a certainty below 50 %
        
    sleep_stats : dict
    Dictionary containing calculated PSG metrics

"""

def score_sleep(raw_PSG, raw_EEG, bad_ch, path_demographics):

    ## Define input channels; right side as default, left side as backup
    
    # Central EEG (minimal requirement)
    if 'C4' in bad_ch:
        eeg = 'C3'
    else:
        eeg = 'C4'
        
    # EOG
    if 'REOG' in bad_ch and 'LEOG' not in bad_ch: # if only LEOG is good
        eog = 'LEOG'
    elif 'REOG' in bad_ch and 'LEOG' in bad_ch: # if both EOG are bad
        eog = None
    else: # default: REOG
        eog = 'REOG'
        
    # EMG
    if 'REMG' in bad_ch and 'LEMG' not in bad_ch: # if only LEMG is good
        emg = 'LEMG'
    elif 'REMG' in bad_ch and 'LEMG' in bad_ch: # if both EMG are bad
        emg = None
    else: # default: REMG
        emg = 'REMG'
        
        
    ## Demographic data
    
    # Load data from CSV file
    demographics = pd.read_csv(path_demographics)
    
    # Extract age
    age = demographics.age[0]
    
    # Extract sex, code as boolean for SleepStaging function
    if demographics.sex[0] == 1: # sex = female
        male = False
    elif demographics.sex[0] == 2: # sex = male
        male = True
    else: # sex = 'intersex' or 'prefer not to say'
        male = None
        
        
    ## Automated sleep staging
    
    # Create YASA object
    if male is not None: # default: sex variable is defined as either female or male (only valid inputs in YASA)
        sls = yasa.SleepStaging(raw_PSG, eeg_name=eeg, eog_name=eog, emg_name=emg, metadata=dict(age=age, male=male))
    else: # alternative: run the algorithm without sex variable
        sls = yasa.SleepStaging(raw_PSG, eeg_name=eeg, eog_name=eog, emg_name=emg, metadata=dict(age=age))
        
    # Predict the sleep stages
    hypnogram = sls.predict()
    
    # Convert "W" to 0, "N1" to 1, etc; 4 is REM
    hypnogram = yasa.hypno_str_to_int(hypnogram)
    
    # Upsample hypnogram to match EEG data
    # Note: 'data' is an empty array with nr. of samples of 
    hypno_up = yasa.hypno_upsample_to_data(hypnogram, sf_hypno=1/30, data=raw_EEG)
    
    # Predicted probabilities of each sleep stage at each epoch
    sls.predict_proba()
    
    # Extract a confidence level (ranging from 0 to 1) for each epoch
    confidence = sls.predict_proba().max(1)
    
    # Get list of uncertain epochs (below 50 % probability)
    uncertain_epochs = confidence.loc[confidence < 0.5]
    uncertain_epochs = list(uncertain_epochs.index)
    print('\nStages scored;', len(uncertain_epochs), 'epochs out of', len(hypnogram), 'below 50 % probability')
    
    
    ### Metrics & plot
    
    # Sleep statistics
    sleep_stats = yasa.sleep_statistics(hypnogram, sf_hyp=1/30) # SR of hypnogram is one value every 30-seconds (staged epochs)
    
    # Upsample hypnogram to match data, for plot
    hypno_plot = yasa.hypno_upsample_to_data(hypnogram, sf_hypno=1/30, data=raw_PSG)
    
    # Access data of central derivation channel used for prediction
    data_plot = raw_PSG.get_data(picks=eeg)
    
    # Plot spectrogram for chosen EEG channel
    yasa.plot_spectrogram(data_plot[0], 100, hypno_plot, fmin=0.5, fmax=25)


    return hypnogram, hypno_up, uncertain_epochs, sleep_stats


    
# %% Function: select_annotations
   
"""
    Turn stages scored with enough confidence into annotations.
    
    Input
    ----------
    raw_EEG : MNE object
    Output of load_raw() for EEG channels
    
    hypnogram : array
    Output of score_sleep()
    
    uncertain_epochs : list
    Output of score_sleep()

    Output
    -------
    raw_EEG : MNE raw object
    Processed data in MNE format (EEG channels) with selected stage annotations

""" 

def select_annotations(raw_EEG, hypnogram, uncertain_epochs):
    
    ## For PSD analyses: stage info as annotations
    
    # Get sampling rate
    sfreq = raw_EEG.info['sfreq']
    
    # Get recording duration in seconds
    rec_len = raw_EEG._raw_lengths[0]/sfreq
    rec_len = int(np.floor(rec_len)) # round down, convert to int
    
    # Onset of annotations: every 30 sec, for whole recording
    onset = range(0, rec_len, 30)
    
    # Array with epoch onsets (in seconds) + all stages
    all_stages = np.column_stack((np.asarray(onset),hypnogram))
    
    # Remove uncertain epochs
    clean_stages = np.delete(all_stages,uncertain_epochs,axis=0)
    
    # Create anotations: every 30 sec, each lasting 30 sec, with scored stages as markers
    annotations = mne.Annotations(onset=clean_stages[:,0], duration=30, description=clean_stages[:,1])  
    
    # Add to raw object
    raw_EEG.set_annotations(annotations)  
    
    
    return raw_EEG
    
    
    
# %% Function: create_epochs

"""
    Construct and select epochs for PSD analysis based on chosen stage.
    
    Input
    ----------
    raw : MNE Raw object
	Output of select_annotations()
    
    event_id : list of int
    List of stages to include in epoch selection. 0=wake, 1=N1, 2=N2, 3=N3, 4=REM

    Output
    -------
    epochs : MNE Epochs object
	Selection of 30 s trials for PSD analyses

"""

def create_epochs(raw, event_id):
    
    # Turn annotations of currently selected stage into events
    events, _ = mne.events_from_annotations(raw, event_id = {str(event_id):event_id}, verbose=False)
    
    # Create epochs
    epochs = mne.Epochs(
        raw,
        events=events,
        tmin=0, # start trials at beginning of scored epochs
        tmax=30, # end trials at end of scored epochs
        reject=dict(eeg = 0.001),  # trial rejection criterion: 1 mV peak to peak
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

def compute_PSD(epochs, stage):
    
    ## Compute PSD
    
    # Get sampling rate
    sfreq = epochs.info["sfreq"]
    
    # Compute average PSD spectra for this stage's epochs
    # Note: only at this point do bad epochs get rejected
    spectrum = epochs.compute_psd(
        "welch",
        n_fft=int(sfreq * 30), # length of FFT
        tmin=0,
        tmax=30,
        fmin=0, # min. frequency to include in spectra (Hz)
        fmax=100, # max. frequency to include in spectra (Hz)
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

    # Half length of target frequency range (in nr. of frequency bins)
    bin_len = idx_bin_40Hz - idx_bin_lower

    
    ## Compute SNR
    
    # Nr. of neighboring frequency bins used to compute noise level, on each side (here, 'noise' = [38-39.5 Hz] + [40.5-42 Hz])
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
    # snrs: ndarray with shape (n_epochs, n_channels, n_freqs)
    snrs = psds / mean_noise
    
    
    ## Plot spectra
    
    fig, axes = plt.subplots(2, 1, sharex='all', sharey='none', figsize=(8, 5))
    freq_range = range(np.where(np.floor(freqs) == 0)[0][0], np.where(np.ceil(freqs) == 100)[0][0])
    
    # PSD spectrum
    psds_plot = 10 * np.log10(psds) # in dB
    psds_mean = psds_plot.mean(axis=(0, 1))[freq_range] # across channels and epochs
    psds_std = psds_plot.std(axis=(0, 1))[freq_range] # add standard deviation
    axes[0].plot(freqs[freq_range], psds_mean, color='b')
    axes[0].fill_between(
        freqs[freq_range], psds_mean - psds_std, psds_mean + psds_std,
        color='b', alpha=.2)
    axes[0].set(title="PSD spectrum, stage "+str(stage), ylabel='Power Spectral Density [dB]')
    
    # SNR spectrum
    snr_mean = snrs.mean(axis=(0, 1))[freq_range] # across channels and epochs
    snr_std = snrs.std(axis=(0, 1))[freq_range] # add standard deviation
    
    axes[1].plot(freqs[freq_range], snr_mean, color='r')
    axes[1].fill_between(
        freqs[freq_range], snr_mean - snr_std, snr_mean + snr_std,
        color='r', alpha=.2)
    axes[1].set( title="SNR spectrum, stage "+str(stage), xlabel='Frequency [Hz]', ylabel='SNR', ylim=[-1, 50], xlim=[1, 100])
    fig.show()
    
    
    ## Get metrics
    
    # Get SNRs in defined range around target frequency 
    # (allowing for slightly different individual SSVEP frequencies / inconsistencies in flicker)
    snrs_40Hz = snrs[:,:,(idx_bin_40Hz-bin_len):(idx_bin_40Hz+bin_len)]

    # Average across epochs & channels
    snrs_40Hz_avg = snrs_40Hz.mean(axis=(0, 1))

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
    
    
    
    
    
    