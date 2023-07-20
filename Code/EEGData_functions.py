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
import scipy
import random



# %% Function: load_raw
"""
    Load raw EEG data, split into PSG and EEG, perform basic processing.

    Input
    ----------
    filename : str
    Path to the EEG data file in EDF format
        
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


# %% Function: import_triggers

"""
    Access triggers from experimental sessions, optionally merge into one trigger set (control condition).
    
    Input
    ----------
    filename1 : str
    Path to annotations of experimental session 01
    
    filename2 : str
    Path to annotations of experimental session 03
    
    raw_EEG : MNE raw object
    Output of load_raw()
    
    condition : str
    Specify if currently analyzing control ('con') or experimental ('exp') data

    Output
    -------
    all_triggers : array
    Array containing trigger data points from both exp sessions
    
    triggers_s01 : array
    Array containing trigger data points from session 01
    
    triggers_s03 : array
    Array containing trigger data points from session 03

"""

def import_triggers(filename1, filename2, raw_EEG, condition):
    
    # Clone raw object, just a placeholder to access annotations
    raw_copy = raw_EEG.copy()
    
    
    ## Access triggers from session 01: wake exp
    
    # Import annotations from EDF file, session 01
    annotations_s01 = mne.read_annotations(filename1, sfreq=1000)

    # Add to raw object (necessary for next step)
    raw_copy.set_annotations(annotations_s01, emit_warning=True)  

    # Create events from trigger annotations only
    events_s01, _ = mne.events_from_annotations(raw_copy, event_id={'DC trigger 12':1}) 

    # Access data points containing triggers
    triggers_s01 = events_s01[:,0]
    
    
    ## Access triggers from session 03: sleep exp
    
    # Import annotations from EDF file, session 03
    annotations_s03 = mne.read_annotations(filename2, sfreq=1000)
    
    # Add to raw object (necessary for next step); overwrites s01 annotations
    raw_copy.set_annotations(annotations_s03, emit_warning=True)
    
    # Create events from trigger annotations only
    events_s03, _ = mne.events_from_annotations(raw_copy, event_id={'DC trigger 12':1}) 

    # Access data points containing triggers
    triggers_s03 = events_s03[:,0]
    

    ## Return correct set of triggers
    
    # For control condition only: merge two trigger sets
    if condition == 'con':

        # Shift triggers from s03 by length of s01 (last trigger)
        triggers_s03_shift = triggers_s03 + triggers_s01[-1] + 25 # add length of one segment (25 ms), to prevent any overlap
        
        # Stack both trigger arrays
        all_triggers = np.hstack((triggers_s01, triggers_s03_shift))
    
        # Get length of control data file
        len_data_con = raw_EEG.__len__()
    
        # Keep only triggers that fit within file, ensuring last segment is not cropped
        all_triggers = np.asarray([trig for trig in all_triggers if trig < len_data_con - 25])
        
        # Print nr. of triggers included
        print('\nNr. of triggers found:', len(all_triggers))
    
        return all_triggers

    # Experimental condition: return trigger sets separately
    elif condition == 'exp':
        
        return triggers_s01, triggers_s03
    
    # Any other input is wrong
    else: 
        
        print('Condition must be con or exp')



# %% Function: score_sleep

"""
    Source code: https://raphaelvallat.com/yasa/build/html/api.html

    Use YASA package to automatically score sleep stages and compute PSG metrics.
    
    Input
    ----------
    raw_PSG : MNE raw object
    Output of load_raw() for PSG channels
    
    raw_EEG : MNE raw object
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
    Turn sleep stages into annotations, for PSD analyses.
    
    Input
    ----------
    raw_EEG : raw object
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
    
    # Get length of hypnogram in seconds (this excludes the last epoch if incomplete)
    len_hypno = len(hypnogram) * 30 
    
    # Onset of annotations: every 30 sec, for whole hypnogram
    onset = range(0, len_hypno, 30)
    
    # Array with epoch onsets (in seconds) + all stages
    all_stages = np.column_stack((np.asarray(onset),hypnogram))
    
    # Remove uncertain epochs
    clean_stages = np.delete(all_stages,uncertain_epochs,axis=0)
    
    # Create anotations with scored stages as markers
    annotations = mne.Annotations(onset=clean_stages[:,0], duration=30, description=clean_stages[:,1])  
    
    # Add to raw object
    raw_EEG.set_annotations(annotations, emit_warning=True)  
    
    
    return raw_EEG
    
    
    
# %% Function: create_epochs

"""
    Construct and select epochs for PSD analysis based on chosen stage.
    
    Input
    ----------
    raw : MNE raw object
	Output of select_annotations()
    
    all_triggers : array
    Output of import_triggers(); merged trigger set or from one session
    
    event_id : int
    Stage to include in epoch selection. 0=wake, 1=N1, 2=N2, 3=N3, 4=REM

    Output
    -------
    epochs : MNE epochs object
	Selection of 30 s trials for PSD analyses

"""

def create_epochs(raw, all_triggers, event_id):
    
    # Turn annotations of currently selected stage into events
    events, _ = mne.events_from_annotations(raw, event_id = {str(event_id):event_id}, verbose=False)
    
    
    ## Select epochs with triggers
    
    # Define minimal nr. of triggers required for a stimulation epoch (40 Hz, 25 sec)
    min_n_triggers = 40 * 25
    
    # Initialize list of non-stim epochs
    not_stim = []
    
    # Loop over events
    for e in range(len(events)):
        
        # Get epoch start (data point)
        epoch_start = events[e,0]
        
        # Define epoch end after 30 sec
        epoch_end = int(epoch_start + raw.info['sfreq'] * 30)
    
        # Get all triggers recorded between epoch start & end, if any
        epoch_triggers = [t for t in all_triggers if t >= epoch_start and t <= epoch_end]
        
        # Get nr. of triggers in this epoch
        n_epoch_triggers = len(epoch_triggers)
        
        # If the epoch does not contain enough triggers, mark for removal
        if n_epoch_triggers < min_n_triggers:
            
            not_stim.append(e)
            
    # Remove all epochs without a sufficient nr. of triggers from events
    events_clean = np.delete(events, not_stim, axis=0)
    
    
    ## Create epochs object
    
    epochs = mne.Epochs(
        raw,
        events=events_clean,
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

    Compute PSD spectra and SNR values for current stage and plot.
    
    Input
    ----------
    epochs : MNE epochs object
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
    Average PSD spectrum across channels and epochs in current stage 
    
    SNR_spectrum : array
    Average SNR spectrum of PSD values across channels and epochs in current stage

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
    
    
    
# %% Function: compute_SSVEP

"""
    Source code: https://github.com/JamesDowsettNeuroscience/flicker_analysis_code
    
    Get SSVEP segments for current stage, plot average, compute SNR.

    Input
    ----------
    data : array
    1 row, averaged ROI data
    
    all_triggers : array
    Output of import_triggers(); merged trigger set or from one session
    
    condition : int
    Number of current condition: 0=wake, 1=N1, 2=N2, 3=N3, 4=REM
    
    hypno_up : array
    Output of score_sleep()
        
    SNR : bool
    Optional calculation of SNR

    Output
    ----------
    true_amplitude : int
    Peak-to-trough amplitude of the averaged SSVEP
    
    SNR : int
    Ratio of true SSVEP peak-to-trough amplitude to random SSVEP peak-to-trough amplitude
    
    n_trials : int
    Nr. of trials (=25 ms segments) included in average SSVEP
    
    SSVEP : array
    Final averaged SSVEP curve
    
"""

def compute_SSVEP(data, all_triggers, hypno_up, condition, computeSNR=True):
        
    ## Compute "true" SSVEP
    
    # Initialize array for trigger subset
    triggers = []
    
    # Select subset of triggers for current stage
    for i in range(len(all_triggers)):
        
        trig = all_triggers[i] # current trigger
        
        if hypno_up[trig] == condition: # if current trigger matches current stage
            
            triggers.append(trig) # add trigger to list   
    
    # Initialize empty matrix to put segments into        
    segment_matrix = np.zeros([len(triggers),25])         
                    
    # Counters
    trig_count = 0
    
    # Loop over trigger subset
    for trigger in triggers:
 
        segment = data[trigger:trigger+25] # current segment
 
        # Include only segments with a peak-to-trough amplitude below 100 uV
        if np.ptp(segment) < 100: 
        
            segment_matrix[trig_count,:] = segment # put into matrix                        
            
            trig_count += 1 # update counter
            
    # Get nr. of segments included
    n_trials = trig_count
    
    # Display nr. of segments included
    print('\nStage', condition, '\n')
    print(trig_count, 'good segments of', len(triggers))
                
    # Average to make the SSVEP
    SSVEP = segment_matrix[0:trig_count,:].mean(axis=0) 
    
    # Baseline correct 
    SSVEP = SSVEP - SSVEP.mean() 
    
    # Get peak-to-trough amplitude
    true_amplitude = np.ptp(SSVEP) 
    
    # Initialize array for standard error values
    stand_errors = np.zeros(25)
    
    # Get standard error for each point in SSVEP
    for pt in range(len(segment_matrix[0])):
        
        stand_errors[pt] = scipy.stats.sem(segment_matrix[:,pt])
       
    
    ## Plot
    
    # Open figure
    plt.figure() 
        
    # Plot aesthetics
    plt.title('Averaged Segments (SSVEP): stage ' + str(condition), size = 30, y=1.03)
    plt.ylabel('Amplitude (' + u"\u03bcV)", size=20)
    plt.yticks(size=20)
    plt.xlabel('Time (ms)', size=20)
    plt.xticks(size=20)
    
    # Plot averaged SSVEP 
    plt.plot(SSVEP, color = 'black') 
    
    # Plot shaded error region
    plt.fill_between(range(0,25), SSVEP-stand_errors, SSVEP+stand_errors, alpha = 0.3) 
    
    
    ## Compute SNR (optional)
    # Note: compute by randomly shuffling the data points of each segment and then making the SSVEP, compare to true SSVEP - looped               
    # Skip to quickly check SSVEP; this takes a few minutes, depending on num_loops
    
    if computeSNR: 
        
        print('Computing SNR...')
        
        # Define nr. of iterations for SNR calculation
        num_loops = 100
        
        # Initialize array for shuffled peak-to-trough amplitudes
        random_amplitudes = np.zeros([num_loops,])
        
        # Loop over defined nr. of iterations
        for loop in range(0,num_loops):
            
            # Initialize array for shuffled segments
            shuffled_segment_matrix =  np.zeros([len(triggers), 25])  
            
            # Loop over all triggers for this stage 
            trig_count = 0
            
            for trigger in triggers:
                
                segment =  data[trigger:trigger+25] # select current segment
                
                if np.ptp(segment) < 100: # as in "true" SSVEP, include only good segments
              
                    random.shuffle(segment) # randomly shuffle the data points
                    
                    shuffled_segment_matrix[trig_count,:] = segment # add segment to matrix
                    
                    trig_count += 1 # update counter
            
            # Average to make random SSVEP
            random_SSVEP = shuffled_segment_matrix[0:trig_count,:].mean(axis=0) 
            
            # Baseline correct
            random_SSVEP = random_SSVEP - random_SSVEP.mean() 
            
            # Store peak-to-trough amplitude for this iteration
            random_amplitudes[loop] = np.ptp(random_SSVEP)
               
        # Get mean of random peak-to-trough amplitude  s      
        average_noise = random_amplitudes.mean()         
    
        # Compute SNR
        SNR = true_amplitude/average_noise
        
        print('SSVEP SNR:', round(SNR,2))
        
    else: # if SNR not computed, assign NaN
        
        SNR = float('NaN')
            
    print('Peak-to-trough amplitude ('+ u"\u03bcV):", round(true_amplitude, 2))          


    return true_amplitude, SNR, n_trials, SSVEP

    
    