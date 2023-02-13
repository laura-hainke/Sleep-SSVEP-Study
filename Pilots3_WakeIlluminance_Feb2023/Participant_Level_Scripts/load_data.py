#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Function to load CSV data, 1 channel at a time; convert to numpy array

"""


# =============================================================================
# Inputs: 
#   - file_name

# Output:
#   - rawdata: numpy array with 1 row per channel, nr of columns = nr of data points in total (1st "channel", i.e., timestamps, is skipped)
# =============================================================================


## Libraries
import numpy as np
import matplotlib.pyplot as plt


def load_data(file_name):

    for chan in range(0,8): # loop through each channel and save the data
        
        chan_data = []        
                
        f = open(file_name) # open the csv file, call it "f"
        
        # use readline() to read the first line 
        line = f.readline()
        line = f.readline() # skip one more line
               
        comma_locations = [i for i, letter in enumerate(line) if letter == ',']                
        
        # Use the read line to read further
        # If the file is not empty keep reading one line at a time, until the end
        while line:
            
            line = f.readline() # use readline() to read next line
              
            comma_locations = [i for i, letter in enumerate(line) if letter == ',']
            
            if len(comma_locations) == 8:
                
                if chan < 7:
                    value = float(line[comma_locations[chan]+1:comma_locations[chan+1]])
                else:
                    value = float(line[comma_locations[chan]+1:])
                
                chan_data.append(value)            
            
        
        f.close() # close the file  
        
        length_of_file = len(chan_data)
        
        print('Chan ' + str(chan) + '  '  + str(length_of_file) + ' data points = ' + str(np.round(length_of_file/60000,1)) + ' mins')
        
        # convert to numpy array
        data = np.array(chan_data, dtype=float)        
        
        # ndarray to save raw data
        if chan == 0:
            rawdata = data
        else:
            rawdata = np.vstack((rawdata,data))        

    return rawdata
