#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: LH
Date: 24 Feb 2023
Functionality: Master script to compute SNR spectrum of an example pilot dataset.
Assumptions:
    - Channels in order: C3, C4, TP10, O1, O2, POz, M-EOG, EOG-PD
    - Sampling rate = 1000 Hz; flicker frequency = 40 Hz
    - 1 photodiode trigger per second
    - BDF recording including one flicker condition
Notes: 
    - Based on MNE tutorial https://mne.tools/stable/auto_tutorials/time-freq/50_ssvep.html
    - Useful info on MNE raw object https://mne.tools/stable/generated/mne.io.Raw.html

"""


# %% Environment Setup

# Libraries
import matplotlib.pyplot as plt
import numpy as np
import mne
from math import trunc
from snr_spectrum import snr_spectrum



# %% Load & preprocess data

# Load full BDF data set
raw = mne.io.read_raw_bdf('eyes_centred_ExG.bdf', preload=True)

# Access raw data, convert from Volts to microVolts
data = raw.get_data() * 1e6

# Extract trigger data
trigger_data = data[7] - data[8]

# Baseline correct
trigger_data = trigger_data - trigger_data.mean()

# Get differential
diff_trigger_data = np.diff(trigger_data)

# Indices for all triggers
idx_triggers = np.where((diff_trigger_data > 200) & (diff_trigger_data < 1000))

# Beginning of stimulation (change 2nd index manually if needed, see plot)
idx_stim_begin = idx_triggers[0][0]

# End of stimulation (change 2nd index manually if needed, see plot)
idx_stim_end = idx_triggers[0][467]

# Plot for confirmation
plt.figure()
plt.plot(trigger_data)
plt.plot(diff_trigger_data)
plt.axvline(x=idx_stim_begin, ymin=0, color='grey', linestyle='dotted', linewidth=2)
plt.axvline(x=idx_stim_end, ymin=0, color='grey', linestyle='dotted', linewidth=2)

# Trim raw data file to include only stimulation period
raw.crop(tmin = raw.times[idx_stim_begin], tmax = raw.times[idx_stim_end]) # full
# raw.crop(tmin = raw.times[idx_stim_begin], tmax = raw.times[151023]) # 1st half
# raw.crop(tmin = raw.times[151023], tmax = raw.times[idx_stim_end]) # 2nd half

# Drop channels not included in ROI
raw.drop_channels(['TimeStamp','ch1','ch2','ch3','ch7','ch8'])

# Apply bandpass filter
raw.filter(l_freq=0.1, h_freq=None, fir_design='firwin', verbose=False)



# %% Calculate PSD and SNR spectra

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
target_bin_hlen = idx_bin_40Hz - idx_bin_lower


# Apply function:
# For every given frequency, ignore neighbouring frequencies +/- 0.5 Hz, use +/- 1.5 Hz around that range as noise
snrs = snr_spectrum(psds_rs, noise_n_neighbor_freqs=target_bin_hlen*3, noise_skip_neighbor_freqs=target_bin_hlen)



# %% Plot PSD and SNR spectra

fig, axes = plt.subplots(2, 1, sharex='all', sharey='none', figsize=(8, 5))
freq_range = range(np.where(np.floor(freqs) == 1.)[0][0], np.where(np.ceil(freqs) == 100 - 1)[0][0])

psds_plot = 10 * np.log10(psds_rs)
psds_mean = psds_plot.mean(axis=(0, 1))[freq_range]
psds_std = psds_plot.std(axis=(0, 1))[freq_range]
axes[0].plot(freqs[freq_range], psds_mean, color='b')
axes[0].fill_between(
    freqs[freq_range], psds_mean - psds_std, psds_mean + psds_std,
    color='b', alpha=.2)
axes[0].set(title="PSD spectrum", ylabel='Power Spectral Density [dB]')

# SNR spectrum
snr_mean = snrs.mean(axis=(0, 1))[freq_range]
snr_std = snrs.std(axis=(0, 1))[freq_range]

axes[1].plot(freqs[freq_range], snr_mean, color='r')
axes[1].fill_between(
    freqs[freq_range], snr_mean - snr_std, snr_mean + snr_std,
    color='r', alpha=.2)
axes[1].set( title="SNR spectrum", xlabel='Frequency [Hz]', ylabel='SNR', ylim=[-2, 30], xlim=[1, 100])
fig.show()



# %% Get SNR value for stimulation frequency

# Get SNRs in defined range around target frequency (allowing for slightly different individual SSVEP frequencies)
snrs_40Hz = snrs[0,:,(idx_bin_40Hz-target_bin_hlen):(idx_bin_40Hz+target_bin_hlen)]

# Average across occipital electrodes
snrs_40Hz_avg = snrs_40Hz.mean(axis=0)

# Get maximum averaged SNR in that range
idx_max_SNR = np.argmax(snrs_40Hz_avg) # index in target frequency subset
max_target_SNR = snrs_40Hz_avg[idx_max_SNR] # corresponding SNR value

# Get exact frequency corresponding to highest SNR
max_SNR_freq = freqs[idx_bin_40Hz - (target_bin_hlen - idx_max_SNR)]

# Print results
print('Max. SNR value: ' + str(round(max_target_SNR,2)))
print('Corresponding frequency (Hz): ' + str(round(max_SNR_freq,2)))






