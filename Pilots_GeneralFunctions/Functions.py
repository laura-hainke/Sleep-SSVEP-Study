# -*- coding: utf-8 -*-
"""
Author: LH
Date: 03.23
Functionality: Functions for processing & analysis of Gamma_Sleep data sets

"""

## Libraries
import numpy as np
import random
import math
import matplotlib.pyplot as plt
from scipy import fftpack, signal, stats



# %% Function: get_triggers

# =============================================================================
# Extract photodiode triggers from trigger & EOG channels

# Inputs:
#   - data: output from load_data
#   - sr: sampling rate in kHz
#   - eog_ch: index of EOG channel
#   - trig_ch: index of photodiode trigger channel

# Output:
#   - triggers: indices of data points that are triggers 
# =============================================================================

def get_triggers(data, sr, eog_ch, trig_ch):

    rawdata = np.copy(data)

    # Load photodiode & EOG channels
    photo_diode_data = rawdata[trig_ch]
    EOG_data = rawdata[eog_ch] 
    
    # Subtract to get just the triggers
    trigger_data = photo_diode_data - EOG_data 
    
    # If the channels were the wrong way, it might be necessary to flip the data
    trigger_data = trigger_data * -1
    
    # Baseline correct
    trigger_data = trigger_data - trigger_data.mean() 
    
    # Get differential
    diff_trigger_data = np.diff(trigger_data)
    
    # Plot
    plt.figure()
    plt.plot(trigger_data)
    plt.plot(diff_trigger_data)
    
    triggers = [] # empty list to put triggers into
        
    trigger_count = 0 # counter to keep track of the number of triggers
        
    trigger_time_series = np.zeros([len(trigger_data,)]) # a time series to mark the locations of the triggers, to check the timing is correct
    
    print(' ')
    print('Searching for triggers ...')
        
    k = 15 # change here if to start later
    
    while k < len(trigger_data) - (10*sr):         
        
        if diff_trigger_data[k] > 200: # if the first differential of the trigger data is above a certain threshold, indicating a steep rising edge
        
            trigger_time = np.argmax(diff_trigger_data[k-(10*sr):k+(10*sr)]) + k + 1 + (10*sr)# check for the max value in the +/- 10 data points, to be sure the trigger is the peak
            
            triggers.append(trigger_time) # add to list of triggers
            
            trigger_count += 1 # count number of triggers            
                
            k = k + (10*sr) # skip forward data points, so not to include the same trigger twice
        
        k += 1 # move forward one
            
    
    ## only include triggers that are one second apart, and for each one second trigger make 40 separate triggers
    
    triggers_list = np.array(triggers)
    
    good_triggers_list = []
        
    k = 0
    
    while k < len(triggers_list)-5:
        
        # if np.abs((triggers_list[k+1] - triggers_list[k]) - 1000)<= 2:
            
        relative_trigger_time = 0 # the time of the 40 Hz flicker relative to the trigger
        
        for t in range(0,40):
        
            trigger_time = triggers_list[k]+relative_trigger_time
            good_triggers_list.append(trigger_time)
            trigger_time_series[trigger_time] = 200
            
            relative_trigger_time = relative_trigger_time + (25*sr)
                
        k+=1
        
    
    print(str(len(good_triggers_list)) + ' triggers included')
     
    # convert to numpy array
    good_triggers_list = np.array(good_triggers_list, dtype=int)
    
    plt.plot(trigger_time_series)
     
    # convert to numpy array
    triggers_np = np.array(good_triggers_list, dtype=int)
        
    return triggers_np
             
    

# %% Function: make_SSVEPs_random

# =============================================================================
# get SSVEP segments, plot average, compute SNR (true vs. permuted SSVEP)

# Inputs:
#   - ROIdata: 1 row of data, usually averaged ROI data
#   - triggers: output from get_triggers
# 	- condition: name of condition, for plot
#   - sr: sampling rate in kHz
#   - comp_SNR: optional calculation of SNR (takes a bit longer)
#   - num_loops: nr. of repetitions when creating a random SSVEP (e.g., 100, 1000)

# Outputs:
#   - true_amplitude: true peak-to-peak amplitude of the SSVEP
#   - SNR: ratio of true SSVEP amplitude to random SSVEP amplitude

# =============================================================================

def make_SSVEPs_random(ROIdata, triggers, condition, sr=1, comp_SNR=True, num_loops=100):

    data = np.copy(ROIdata)

    ### True SSVEP

    plt.figure()    
    
    # Make real SSVEP        
    segment_matrix = np.zeros([len(triggers),25*sr]) # empty matrix to put segments into        
                    
    trig_count = 0
    bad_seg_count = 0
    
    for trigger in triggers:
 
        segment = data[trigger:trigger+25*sr]       
 
        if np.ptp(segment) > 200: # some segments have large spikes in the data, ignore these
            #print('Bad segment')
            bad_seg_count += 1
        else:
            segment_matrix[trig_count,:] = segment # put into matrix                        
            
            trig_count += 1
            
    print(str(trig_count) + ' good segments')
    print(str(bad_seg_count) + ' bad segments')
            
    SSVEP = segment_matrix[0:trig_count,:].mean(axis=0) # average to make the SSVEP
    
    SSVEP = SSVEP - SSVEP.mean() # baseline correct 
        
    # Plot
    
    if comp_SNR:
        plt.subplot(1,2,1)
        
    plt.title('SSVEP: ' + condition, size = 30, y=1.03)
    plt.ylabel('Amplitude (' + u"\u03bcV)", size=20)
    plt.yticks(size=20)   
    plt.xticks(size=20)
    
    if sr == 1:
        plt.xlabel('Time (ms)', size=20)
    else:
        plt.xlabel('Data points (25 ms)', size=20)
    
    plt.plot(SSVEP, color = '#FFCC00') # plot averaged SSVEP graph
    
    true_amplitude = np.ptp(SSVEP)

    print(condition)
    print('Peak-to-peak amplitude:', round(true_amplitude, 3))

    ### Shuffled SSVEP (SNR)
    ## Signal to noise ratio by randomly shuffling the data points of each segment and then making the SSVEP, compare to true SSVEP - looped               
 
    if comp_SNR: 
        
        # Set seed
        random.seed(1)
 
        random_amplitudes = np.zeros([num_loops,])
        
        for loop in range(0,num_loops):
                      
            shuffled_segment_matrix =  np.zeros([len(triggers), 25*sr])  
            
            # loop through all triggers and put the corresponding segment of data into the matrix
            trig_count = 0
            
            for trigger in triggers:
                
                segment =  data[trigger:trigger+25*sr] 
                
                if np.ptp(segment) < 200: # some segments have large spikes in the data, ignore these
              
                    random.shuffle(segment) # randomly shuffle the data points
                    
                    shuffled_segment_matrix[trig_count,:] = segment
                    
                    trig_count += 1
            
            # Average to make random SSVEP
            random_SSVEP = shuffled_segment_matrix[0:trig_count,:].mean(axis=0) 
            
            random_SSVEP = random_SSVEP - random_SSVEP.mean() # baseline correct
            
            random_amplitudes[loop] = np.ptp(random_SSVEP)
                
        # Plot
        plt.subplot(1,2,2)
        plt.title('Shuffled SSVEP', size = 30, y=1.03)
        plt.ylabel('Amplitude (' + u"\u03bcV)", size=20)
        plt.yticks(size=20)
        plt.xticks(size=20)
        
        if sr == 1:
            plt.xlabel('Time (ms)', size=20)
        else:
            plt.xlabel('Data points (25 ms)', size=20)
        
        plt.plot(random_SSVEP, color = '#FFCC00', alpha = 0.6)
                  
        average_noise = random_amplitudes.mean()         
        
        SNR = true_amplitude/average_noise
    
        print('SNR:', SNR) 
        
    else: 
        
        SNR = 'NaN'

    return true_amplitude, SNR



# %% Function: lin_interpolate

# =============================================================================
# remove flicker artifacts from data series using linear interpolation

# Inputs:
#   - input_data: 1 row of data
#   - triggers: output from get_triggers
#   - time_1: 1st data point in a 25 ms segment that is affected by artifact (LED on)
#   - time_2: 1st data point in 2nd half in a 25 ms segment that is affected by artifact (LED off)
#   - artifact_len: duration of artifact in nr. of data points (longer with higher sampling rate)

# Output:
#   - data: linearly interpolated data

# =============================================================================

def lin_interpolate(input_data, triggers, time_1, time_2, artifact_len):
    
    data = np.copy(input_data)
    
    for trigger in triggers:

        data[trigger+time_1:trigger+time_1+artifact_len+1] = np.linspace(data[trigger+time_1], data[trigger+time_1+artifact_len], num = artifact_len+1)
        data[trigger+time_2:trigger+time_2+artifact_len+1] = np.linspace(data[trigger+time_2], data[trigger+time_2+artifact_len], num = artifact_len+1)
    
    return data



# %% Function: induced_fft

# =============================================================================
# Segment data into segments of a given length, do an FFT on each segment and then average the FFTs.

# Inputs:
#   - data: 1 row of data
#   - triggers: output from get_triggers
# 	- condition: name of condition, for plot
#   - length: length of FFT segments, default = 10 (1/length = the frequency resolution) 
#   - sr: sampling rate in kHz

# Outputs:
#   - FFT_40: value of FFT at 40 Hz
# 	- SNR: ratio of 40 Hz value to surrounding values
# =============================================================================
    
def induced_fft(input_data, triggers, condition, sr, length=10): 

    data = np.copy(input_data)

    plt.figure()
    
    # Convert to float 32 for lower memory load
    data = data.astype(np.float32)
    
    # Nr. of data points per segment        
    length_of_segment = int(length * 1000 * sr) 
    
    # Max. amount of segments
    n_segs = math.floor(len(data) / (1000*sr*length))
    
    # Empty matrix to put segments into
    segment_matrix = np.zeros([n_segs,length_of_segment], dtype = np.float32) 
    
    seg_count = 0
   
    k = 0
    
    while k < len(data) - length_of_segment: # loop until the end of data
    
        if k in triggers: # if data point is a trigger
        
            segment = data[k:k+length_of_segment] # get a segment of data
    
            segment = segment - segment.mean() # baseline correct
                
            segment_hanning = segment * np.hanning(length_of_segment) # multiply by hanning window
                
            fft_segment = np.abs(fftpack.fft(segment_hanning)) # FFT                
    
            segment_matrix[seg_count,:] = fft_segment # put into matrix        
    
            seg_count+=1
            
            k = k + length_of_segment # move forward the length of the segment, so segments are not overlapping
    
        k+=1    
    
    # Final averaged FFT
    fft_spectrum = segment_matrix[0:seg_count,:].mean(axis=0)
    
    # Get standard error for each point in FFT
    stand_errors = np.zeros((1,length_of_segment))
    
    for pt in range(len(segment_matrix[0])):
        stand_errors[0,pt] = stats.sem(segment_matrix[:,pt])
    
    # Get 40 Hz value
    FFT_40 = fft_spectrum[40*length]
    print('40 Hz value: ' + str(FFT_40))
    
    # SNR of 40 Hz peak
    peak_values = fft_spectrum[39*length:41*length]
    near_values = np.concatenate([fft_spectrum[38*length:39*length], fft_spectrum[41*length:42*length]])
    SNR = peak_values.mean() / near_values.mean()
         
    print('SNR of 40 Hz value: ' + str(SNR))
    
    # Plot
    plt.title('Induced FFT: ' + condition, size = 20, y=1.03)
    plt.plot(fft_spectrum)
    plt.ylabel('Amplitude', size=18) 
    plt.yticks(size=18)
    plt.xlabel('Frequency', size=18)
    plt.xticks(size=18)
    plt.axvline(x=40*length, ymin=0, color='grey', linestyle='dotted', linewidth=2)
        
    return FFT_40, SNR



# %% Function: compute PSD spectrum

def psd_spectrum(raw):
    
    """
    Source code: https://mne.tools/stable/auto_tutorials/time-freq/50_ssvep.html
    """

    # Get sampling frequency
    sfreq = raw.info['sfreq']

    # Get stimulation duration in seconds
    len_stim = math.trunc(raw.n_times/sfreq)

    # Compute PSDs
    spectrum = raw.compute_psd('welch', n_fft=int(sfreq * len_stim), n_overlap=0, n_per_seg=None, fmin=1, fmax=100, window='hamming', verbose=False)

    # Access PSD values and corresponding frequencies
    psds, freqs = spectrum.get_data(return_freqs=True)

    # Reshape to 3d array for SNR function
    psds_rs = psds.reshape((1, psds.shape[0], psds.shape[1]))

    # Find index of frequency bin closest to stimulation frequency (here, 40 Hz)
    idx_bin_40Hz = np.argmin(abs(freqs - 40))

    # Find index of lower bound for target frequency range (here, 39.5 Hz)
    idx_bin_lower = np.argmin(abs(freqs - 39.5))

    # Half length of target frequency range (in nr. of frequencies)
    bin_len = idx_bin_40Hz - idx_bin_lower
    
    return psds_rs, bin_len, freqs, idx_bin_40Hz



# %% Function: compute SNR spectrum

def snr_spectrum(psd, noise_n_neighbor_freqs=1, noise_skip_neighbor_freqs=1):
    
    """
    Source code: https://mne.tools/stable/auto_tutorials/time-freq/50_ssvep.html
    
    Compute SNR spectrum from PSD spectrum using convolution.

    Parameters
    ----------
    psd : ndarray, shape ([n_trials, n_channels,] n_frequency_bins)
        Data object containing PSD values. Works with arrays as produced by
        MNE's PSD functions or channel/trial subsets.
    noise_n_neighbor_freqs : int
        Number of neighboring frequencies used to compute noise level.
        increment by one to add one frequency bin ON BOTH SIDES
    noise_skip_neighbor_freqs : int
        set this >=1 if you want to exclude the immediately neighboring
        frequency bins in noise level calculation

    Returns
    -------
    snr : ndarray, shape ([n_trials, n_channels,] n_frequency_bins)
        Array containing SNR for all epochs, channels, frequency bins.
        NaN for frequencies on the edges, that do not have enough neighbors on
        one side to calculate SNR.
    """
    # Construct a kernel that calculates the mean of the neighboring
    # frequencies
    averaging_kernel = np.concatenate((
        np.ones(noise_n_neighbor_freqs),
        np.zeros(2 * noise_skip_neighbor_freqs + 1),
        np.ones(noise_n_neighbor_freqs)))
    averaging_kernel /= averaging_kernel.sum()

    # Calculate the mean of the neighboring frequencies by convolving with the
    # averaging kernel.
    mean_noise = np.apply_along_axis(
        lambda psd_: np.convolve(psd_, averaging_kernel, mode='valid'),
        axis=-1, arr=psd
    )

    # The mean is not defined on the edges so we will pad it with nas. The
    # padding needs to be done for the last dimension only so we set it to
    # (0, 0) for the other ones.
    edge_width = noise_n_neighbor_freqs + noise_skip_neighbor_freqs
    pad_width = [(0, 0)] * (mean_noise.ndim - 1) + [(edge_width, edge_width)]
    mean_noise = np.pad(
        mean_noise, pad_width=pad_width, constant_values=np.nan
    )

    return psd / mean_noise



# %% Function: plot PSD and SNR spectra, print target values

def plot_psd_snr(PSDs, SNRs, freqs, bin_len, idx_bin_40Hz, condition):
    
    """
    Source code: https://mne.tools/stable/auto_tutorials/time-freq/50_ssvep.html
    """
    
    ## Plots
    
    fig, axes = plt.subplots(2, 1, sharex='all', sharey='none', figsize=(8, 5))
    freq_range = range(np.where(np.floor(freqs) == 1.)[0][0], np.where(np.ceil(freqs) == 100 - 1)[0][0])
    
    # PSD spectrum
    psds_plot = 10 * np.log10(PSDs)
    psds_mean = psds_plot.mean(axis=(0, 1))[freq_range]
    psds_std = psds_plot.std(axis=(0, 1))[freq_range]
    axes[0].plot(freqs[freq_range], psds_mean, color='b')
    axes[0].fill_between(
        freqs[freq_range], psds_mean - psds_std, psds_mean + psds_std,
        color='b', alpha=.2)
    axes[0].set(title="PSD spectrum "+condition, ylabel='Power Spectral Density [dB]')
    
    # SNR spectrum
    snr_mean = SNRs.mean(axis=(0, 1))[freq_range]
    snr_std = SNRs.std(axis=(0, 1))[freq_range]
    
    axes[1].plot(freqs[freq_range], snr_mean, color='r')
    axes[1].fill_between(
        freqs[freq_range], snr_mean - snr_std, snr_mean + snr_std,
        color='r', alpha=.2)
    axes[1].set( title="SNR spectrum "+condition, xlabel='Frequency [Hz]', ylabel='SNR', ylim=[-2, 30], xlim=[1, 100])
    fig.show()
    
    
    ## Values
    
    # Get SNRs in defined range around target frequency (allowing for slightly different individual SSVEP frequencies)
    snrs_40Hz = SNRs[0,:,(idx_bin_40Hz-bin_len):(idx_bin_40Hz+bin_len)]

    # Average across occipital electrodes
    snrs_40Hz_avg = snrs_40Hz.mean(axis=0)

    # Get maximum averaged SNR in that range
    idx_max_SNR = np.argmax(snrs_40Hz_avg) # index in target frequency subset
    max_target_SNR = snrs_40Hz_avg[idx_max_SNR] # corresponding SNR value

    # Get exact frequency corresponding to highest SNR
    max_SNR_freq = freqs[idx_bin_40Hz - (bin_len - idx_max_SNR)]
    
    # Get absolute PSD value at frequency with highest SNR (in dB)
    max_abs_PSD = psds_mean[idx_bin_40Hz - (bin_len - idx_max_SNR)]

    # Print results
    print('PSD SNR: ' + str(round(max_target_SNR,2)))
    print('Absolute PSD value (dB): ' + str(round(max_abs_PSD,2)))
    print('Corresponding frequency (Hz): ' + str(round(max_SNR_freq,2)))
    
    return max_abs_PSD, max_target_SNR






