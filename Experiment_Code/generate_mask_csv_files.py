# -*- coding: utf-8 -*-
"""
Author: LH
Date: 12.06.2023
Functionality: Generate CSV files fot stimulation mask (GammaSleep study)
Assumptions:
Notes: Adapted from https://github.com/tscnlab/LiDuSleep/blob/main/07_LightMask/csv/CSVGenerator.ipynb

"""


# %% Environment Setup

## Packages
import csv
import datetime
import numpy as np

## Constants
# Today's date
today = datetime.datetime.now()
date = today.strftime("%Y") + today.strftime("%m") + today.strftime("%d")

# Flicker frequency = 40 Hz
flicker_freq = 40 

# Largest analog value still corresponding to the minimum illuminance of 0 lux
min_analog = 80

# Analog value corresponding to stim target illuminance of 20 lux
max_analog = 320 
    
# Frequency at which the Arduino reads CSV rows, in Hz
sample_rate = flicker_freq * 2 # For 40 Hz square-wave flicker, 40x ON + 40x OFF



# %% Functions to write header & CSV file

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

def create_header(date,sample_rate,nsamples,nrepeat):
    
    header = {
            '% Date [YYYYMMDD]': date,
            '% Experimenter': 'LH',
            '% Experiment': 'GammaSleep',
            '% Condition': 'exp',
            '% Note': '',
            '%  ': '',
            '% Sample rate [Hz]': str(sample_rate),
            '% MinValue': '0',
            '% MaxValue': '320',
            '% NSamples': str(nsamples),    
            '% NRepeat': str(nrepeat),
            '% ': ''
        }
    
    return header


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



# %% Functions to generate stimulation routines

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
    # Max. stim time in min (8 hours)
    max_stim_time = 480
    
    # Duration of data file in min
    data_file_time = 1
    
    # Nr. of samples for defined stim data duration
    nsamples = int(sample_rate * 60 * data_file_time)

    # Nr. of repetitions for 8 hours of total stim time
    nrepeat = int(max_stim_time / data_file_time)


    ## Required CSV format elements
    # Header row of data
    titles = ['Sample', 'Channel1', 'Channel2', 'Channel3', 'Channel4', 'Channel5', 'Channel6', 'Trigger', 'Note']

    # Sample nrs
    sample_nrs = np.array([i for i in range(1, nsamples+1)])
    
    # Notes
    notes = np.array([''] * nsamples)
    

    ## Generate data
    # Data for 1 flicker cycle
    cycle_data = np.array([[max_analog,max_analog,0,0,0,1,1], [0,0,0,0,0,0,0]])

    # Data for 1 min
    cycles_1min = np.tile(cycle_data, (flicker_freq*60*data_file_time, 1))
    
    
    ## Combine arrays
    # Sample nrs, data, notes
    data = np.c_[sample_nrs, cycles_1min, notes]
    
    # Add headers
    data = np.vstack([titles,data])

    return data, nsamples, nrepeat



# %% Generate full CSV files

## Flicker
# Generate data
data_flicker, nsamples_flicker, nrepeat_flicker = create_data_flicker(flicker_freq,max_analog,sample_rate)

# Generate header
header_flicker = create_header(date,sample_rate,nsamples_flicker,nrepeat_flicker)

# Generate CSV
write_CSV(2,header_flicker,data_flicker)







