# -*- coding: utf-8 -*-
"""
Author: LH
Date: 28 Feb 2023
Functionality: Set of functions for data processing (SSVEP and PSD), pilot 3
Notes: 

"""


# %% Environment Setup

# Libraries
import numpy as np
import mne
import random
from math import trunc
import matplotlib.pyplot as plt



# %% Function: compute PSD spectrum

def psd_spectrum(raw):
    
    """
    Source code: https://mne.tools/stable/auto_tutorials/time-freq/50_ssvep.html
    """

    # Get sampling frequency
    sfreq = raw.info['sfreq']

    # Get stimulation duration in seconds
    len_stim = trunc(raw.n_times/sfreq)

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
    
    return max_abs_PSD, max_SNR_freq



# %% Function: compute SSVEP and corresponding SNR

def make_SSVEP_5kHz(data, triggers, condition, num_loops = 50):
    
    """
    Source code: https://github.com/JamesDowsettNeuroscience/flicker_analysis_code
    """
    
    ### True SSVEP

    plt.figure()    
    
    # Make real SSVEP        
    segment_matrix = np.zeros([len(triggers),125]) # empty matrix to put segments into        
                    
    trig_count = 0
    bad_seg_count = 0
    
    for trigger in triggers:
 
        segment = data[trigger:trigger+125]
 
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
    plt.subplot(1,2,1)
    plt.title('Averaged Segments (SSVEP): ' + condition, size = 30, y=1.03)
    plt.ylabel('Amplitude (' + u"\u03bcV)", size=20)
    plt.yticks(size=20)
    plt.xlabel('Data points (25 ms)', size=20)
    plt.xticks(size=20)
    
    plt.plot(SSVEP, color = '#FFCC00') # plot averaged SSVEP graph
    
    
    ### Shuffled SSVEP (SNR)
    ## Signal to noise ratio by randomly shuffling the data points of each segment and then making the SSVEP, compare to true SSVEP - looped               
 
    random_amplitudes = np.zeros([num_loops,])
    
    for loop in range(0,num_loops):
                  
        shuffled_segment_matrix =  np.zeros([len(triggers), 125])  
        
        # loop through all triggers and put the corresponding segment of data into the matrix
        trig_count = 0
        
        for trigger in triggers:
            
            segment =  data[trigger:trigger+125] 
            
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
    plt.title('Averaged shuffled segments', size = 30, y=1.03)
    plt.ylabel('Amplitude (' + u"\u03bcV)", size=20)
    plt.yticks(size=20)
    plt.xlabel('Data points (25 ms)', size=20)
    plt.xticks(size=20)
    
    plt.plot(random_SSVEP, color = '#FFCC00', alpha = 0.6)
    
    true_amplitude = np.ptp(SSVEP)   
    average_noise = random_amplitudes.mean()         
    
    SNR = true_amplitude/average_noise
    
    print('Peak-to-trough amplitude ('+ u"\u03bcV):", round(true_amplitude, 2))
    print('SSVEP SNR:', round(SNR,2))       

    return true_amplitude, SNR


# %% Function: linearly interpolate data

def linear_interpolation(data, triggers, time_1, time_2, trig_length):
    
    """
    Source code: https://github.com/JamesDowsettNeuroscience/flicker_analysis_code
    """
    
    for trigger in triggers:

        data[trigger+time_1:trigger+time_1+trig_length+1] = np.linspace(data[trigger+time_1], data[trigger+time_1+trig_length], num = trig_length+1)
        data[trigger+time_2:trigger+time_2+trig_length+1] = np.linspace(data[trigger+time_2], data[trigger+time_2+trig_length], num = trig_length+1)
    
    return data
