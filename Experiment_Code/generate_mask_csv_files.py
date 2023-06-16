# -*- coding: utf-8 -*-
"""
Author: LH
Date: 06.2023
Functionality: Generate CSV files fot stimulation mask (GammaSleep study)
Assumptions:
Notes: Adapted from https://github.com/tscnlab/LiDuSleep/blob/main/07_LightMask/csv/CSVGenerator.ipynb

"""


# %% Environment Setup

## Packages

import csv
import datetime
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats 


## Constants

# Today's date
today = datetime.datetime.now()
date = today.strftime("%Y") + today.strftime("%m") + today.strftime("%d")

# Flicker frequency = 40 Hz
flicker_freq = 40 

# Analog value corresponding to minimum illuminance of 0 lux
min_analog = 0

# Analog value corresponding to stim target illuminance of 20 lux
max_analog = 320 
    
# Frequency at which the Arduino reads CSV rows, in Hz
sample_rate = flicker_freq * 2 # For 40 Hz square-wave flicker, 40x ON + 40x OFF

# Load parameters for linearization of raw analog values
opt_param = np.load('beta_parameters.npy')



# %% Function: header

"""
    Function to create CSV header.
    
    Input
    ----------
    date : str 
	Date of file generation [YYYYMMDD]
    
    sample_rate : int
    Frequency at which the Arduino reads CSV rows in Hz.
    
    nsamples : int
    Nr of CSV rows containing output data.
    
    nrepeat : int
    Nr of times the CSV should be iterated over.

    Output
    -------
    header : dict
	Header of the generated CSV file.

"""

def create_header(date,sample_rate,min_analog,max_analog,nsamples,nrepeat):
    
    header = {
            '% Date [YYYYMMDD]': date,
            '% Experimenter': 'LH',
            '% Experiment': 'GammaSleep',
            '% Condition': 'exp',
            '% Note': '',
            '%  ': '',
            '% Sample rate [Hz]': str(sample_rate),
            '% MinValue': str(min_analog),
            '% MaxValue': str(max_analog),
            '% NSamples': str(nsamples),    
            '% NRepeat': str(nrepeat),
            '% ': ''
        }
    
    return header



# %% Function: generate rampup data

"""
    Function to create stimulation data for rampup routine.
    
    Input
    ----------
    flicker_freq : int
	Flicker frequency (40 Hz).
    
    max_analog : int
    Analog value corresponding to stim target illuminance (20 lux).
    
    sample_rate : int
    Frequency at which the Arduino reads CSV rows, in Hz.

    Output
    -------
    data : ndarray
	CSV file content below header.
    
    nsamples : int
	Nr of CSV rows containing output data.
    
    nrepeat : int
	Nr of times the CSV should be iterated over.

"""

def create_data_rampup(flicker_freq,max_analog,sample_rate):

    ## Compute parameters

    # Duration of data file in sec (=5 min rampup duration)
    data_file_time = 5 * 60
    
    # Nr. of samples for defined stim data duration
    nsamples = int(sample_rate * data_file_time)
    
    # Nr. of flicker cycles for defined stim data duration
    ncycles = flicker_freq * data_file_time

    # Nr. of repetitions (rampup once, then move to flicker)
    nrepeat = 1


    ## Required CSV format elements
    
    # Header row of data
    headers = ['Sample', 'Channel1', 'Channel2', 'Channel3', 'Channel4', 'Channel5', 'Channel6', 'Trigger', 'Note']

    # Sample nrs
    sample_nrs = np.array([i for i in range(1, nsamples+1)])
    
    # Triggers (none)
    triggers = np.zeros((nsamples, 5))
    
    # Notes
    notes = np.array([''] * nsamples)


    ## Generate cosine ramp
    
    # Array of radians between pi (trough) & 2*pi (peak), with nr. of elements = nr. of cycles
    radians = np.array([i for i in np.arange(np.pi, np.pi*2, np.pi/(ncycles-0.5))]) # subtract 0.5 from ncycles to get 12k elements
    
    # Take cosine values of radians, with fitted amplitude & upward shift (for y in cosine shape)
    cosines = np.array([i for i in (max_analog/2) * np.cos(radians) + max_analog/2])

    
    ## Apply linearization of raw analog values to match lux increase
    
    # y values relative to max_analog
    y_rel = np.array([i/max_analog for i in cosines])
    
    # Apply linearization function to relative values
    y_rel_lin = scipy.stats.beta.cdf(y_rel, opt_param[0], opt_param[1])
    
    # Revert to absolute values
    y_abs_lin = np.array([i*max_analog for i in y_rel_lin])
    
    # Round y values, as program only takes int values
    y_abs_lin_int = np.round(y_abs_lin)
     
    
    ## Plot for visual inspection
    
    fig, ax = plt.subplots(1,2)
    
    # Plot 1: uncorrected ramp
    ax[0].plot(np.round(cosines)) # round for better comparison
    ax[0].set_title('Cosine ramp-up, uncorrected', size=30, y=1.05)
    ax[0].set_xlabel('Flicker cycles (0-5 min)', size=20)
    ax[0].set_ylabel('Rounded analog values', size=20)
    
    # Plot 2: linearized ramp
    ax[1].plot(y_abs_lin_int)
    ax[1].set_title('Cosine ramp-up, linearized', size=30, y=1.05)
    ax[1].set_xlabel('Flicker cycles (0-5 min)', size=20)
    ax[1].set_ylabel('Rounded analog values', size=20)


    ## Transform into data array with flicker
    
    # Initialize data array (2 channels)
    ramp_5min = np.zeros((nsamples,2))
    
    # Fill cycles with ON period from cosines_int, leave OFF period at 0
    i = 0
    while i in range(0, ncycles):
        
        ramp_5min[i*2] = y_abs_lin_int[i]
        i += 1
    

    ## Combine arrays
    
    # Sample nrs, data, notes
    data = np.c_[sample_nrs, ramp_5min, triggers, notes]
    
    # Add headers
    data = np.vstack([headers,data])

    return data, nsamples, nrepeat



# %% Function: generate flicker data

"""
    Function to create stimulation data for flicker routine.
    
    Input
    ----------
    flicker_freq : int
	Flicker frequency (40 Hz).
    
    max_analog : int
    Analog value corresponding to stim target illuminance (20 lux).
    
    sample_rate : int
    Frequency at which the Arduino reads CSV rows, in Hz.

    Output
    -------
    data : ndarray
	CSV file content below header.
    
    nsamples : int
	Nr of CSV rows containing output data.
    
    nrepeat : int
	Nr of times the CSV should be iterated over.

"""

def create_data_flicker(flicker_freq,max_analog,sample_rate):
    
    ## Compute parameters
    
    # Max. stim time in sec (8 hours)
    max_stim_time = 8 * 60 * 60
    
    # Duration of data file in sec (1 min)
    data_file_time = 60
    
    # Nr. of samples for defined stim data duration
    nsamples = int(sample_rate * data_file_time)

    # Nr. of repetitions for 8 hours of total stim time
    nrepeat = int(max_stim_time / data_file_time)


    ## Required CSV format elements
    
    # Header row of data
    headers = ['Sample', 'Channel1', 'Channel2', 'Channel3', 'Channel4', 'Channel5', 'Channel6', 'Trigger', 'Note']

    # Sample nrs
    sample_nrs = np.array([i for i in range(1, nsamples+1)])
    
    # Notes
    notes = np.array([''] * nsamples)
    

    ## Generate data
    
    # Data for 1 flicker cycle
    cycle_data = np.array([[max_analog,max_analog,0,0,0,1,1], [0,0,0,0,0,0,0]])

    # Data for 1 min
    cycles_1min = np.tile(cycle_data, (flicker_freq*data_file_time, 1))
    
    
    ## Combine arrays
    
    # Sample nrs, data, notes
    data = np.c_[sample_nrs, cycles_1min, notes]
    
    # Add headers
    data = np.vstack([headers,data])

    return data, nsamples, nrepeat



# %% Function: write CSV

"""
    Function to write the full CSV file.
    
    Input
    ----------
    csv_nr : int
	Choose between CSV files 1,2,3.
    
    header : dict
    Output of create_header().
    
    data : np array
    Output of one create_data function.

    Output
    -------
    CSV file stored in directory.

"""

def write_CSV(csv_nr,header,data):
    
    # Defining mandatory filenames
    if csv_nr == 1:
        
        filename = 'rampup.csv'
        
    elif csv_nr == 2:
        
        filename = 'flicker.csv'
        
    elif csv_nr == 3:
        
        filename = 'rampdown.csv'
    
    
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')

        # Write header rows
        for key, value in header.items():
            writer.writerow([key, value, '', '', '', '', '', '', '', ''])

        # Write data rows
        for row in data:
            writer.writerow(row)



# %% Generate full CSV files

## Ramp-up

# Generate data
data_rampup, nsamples_rampup, nrepeat_rampup = create_data_rampup(flicker_freq,max_analog,sample_rate)

# Generate header
header_rampup = create_header(date,sample_rate,min_analog,max_analog,nsamples_rampup,nrepeat_rampup)

# Generate CSV
write_CSV(1,header_rampup,data_rampup)


## Flicker

# Generate data
data_flicker, nsamples_flicker, nrepeat_flicker = create_data_flicker(flicker_freq,max_analog,sample_rate)

# Generate header
header_flicker = create_header(date,sample_rate,min_analog,max_analog,nsamples_flicker,nrepeat_flicker)

# Generate CSV
write_CSV(2,header_flicker,data_flicker)







