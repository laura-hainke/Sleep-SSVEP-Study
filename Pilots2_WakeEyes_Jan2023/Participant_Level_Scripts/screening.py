# -*- coding: utf-8 -*-
"""
Screening of pilot participants for Sleep-SSVEP Study (2023). 
Load 5 min of data, get triggers, compute SSVEP (plot and SNR).

"""


#%% Requirements
# A 5-min data file in CSV format
# Sampling rate = 1000 Hz; photodiode triggers = 1x / sec; flicker at 40 Hz
# EEG channel positions in order: L-H-EOG, R-V-EOG, TP10, O1, O2, POz, M-EOG, EOG-PD



#%% Libraries
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import random



#%% Load data

file_name = 'screening_ExG.csv'

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




#%% Get triggers

# Load photodiode & EOG channels
photo_diode_data = rawdata[7]
EOG_data = rawdata[6] 

# Subtract to get just the triggers
trigger_data = photo_diode_data - EOG_data 

# Baseline correct
trigger_data = trigger_data - trigger_data.mean() 

# Get differential
diff_trigger_data = np.diff(trigger_data)

# Flip the data
trigger_data = trigger_data * -1

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

while k < len(trigger_data) - 10:                
    
    if diff_trigger_data[k] > 250: # if the first differential of the trigger data is above a certain threshold, indicating a steep rising edge
   
    
        trigger_time = np.argmax(diff_trigger_data[k-10:k+10]) + k + 11# check for the max value in the +/- 10 data points, to be sure the trigger is the peak
        
        triggers.append(trigger_time) # add to list of triggers
        
        trigger_count += 1 # count number of triggers            
            
        k = k + 10 # skip forward data points, so not to include the same trigger twice
    
    k += 1 # move forward one
        

## only include triggers that are one second apart, and for each one second trigger make 40 separate triggers

triggers_list = np.array(triggers)

good_triggers_list = []
    
k = 0

while k < len(triggers_list)-1:
    
    if np.abs((triggers_list[k+1] - triggers_list[k]) - 1000)<= 2:
        
        relative_trigger_time = 0 # the time of the 40 Hz flicker relative to the trigger
        
        for t in range(0,40):
        
            trigger_time = triggers_list[k]+relative_trigger_time
            good_triggers_list.append(trigger_time)
            trigger_time_series[trigger_time] = 200
            
            relative_trigger_time = relative_trigger_time + 25
            
    k+=1
    

print(str(len(good_triggers_list)) + ' triggers found')

plt.plot(trigger_time_series) # plot to check 
 
# convert to numpy array
triggers_np = np.array(good_triggers_list, dtype=int)




#%% Plot SSVEP

# Average of occipital channels, re-referenced to both mastoids
data_occ_reref = ((rawdata[3]+rawdata[4]+rawdata[5])/3) - (rawdata[2]/2)

offset = 0 
        
plt.figure()

# high pass filter the data to remove slow drifts        
high_pass_filter = signal.butter(2, 0.1, 'hp', fs=1000, output='sos')
data_occ_reref = signal.sosfilt(high_pass_filter, data_occ_reref)

segment_matrix = np.zeros([len(triggers_np),25]) 

trig_count = 0

for trigger in triggers_np:

    segment = data_occ_reref[trigger-offset:trigger+25-offset]     

    # If segment does not have a large spike, put into matrix
    if np.ptp(segment) < 200:

        segment_matrix[trig_count,:] = segment 

        trig_count += 1

print(str(trig_count) + ' segments included')

SSVEP = segment_matrix[0:trig_count,:].mean(axis=0) # average to make the SSVEP

SSVEP = SSVEP - SSVEP.mean() # baseline correct        

## Plot SSVEP
plt.subplot(1,2,1)
plt.title('Averaged Segments (SSVEP) - Screening', size = 30, y=1.03)

plt.ylabel('Amplitude (' + u"\u03bcV)", size=20)
plt.yticks(size=20)
plt.xlabel('Time (ms)', size=20)
plt.xticks(size=20)

plt.plot(SSVEP, color = '#FFCC00', linewidth=4)



#%% Compute SNR

## Signal to noise ratio by randomly shuffling the data points of each segment and then making the SSVEP, compare to true SSVEP - looped          

num_loops = 100

random_amplitudes = np.zeros([num_loops,])

for loop in range(0,num_loops):

    shuffled_segment_matrix =  np.zeros([len(triggers_np), 25])  

    # loop through all triggers and put the corresponding segment of data into the matrix
    trig_count = 0

    for trigger in triggers_np:

        segment =  data_occ_reref[trigger:trigger+25] 

        if np.ptp(segment) < 200: # some segments have large spikes in the data, ignore these

            random.shuffle(segment) # randomly shuffle the data points

            shuffled_segment_matrix[trig_count,:] = segment

            trig_count += 1

    # Average to make random SSVEP
    random_SSVEP = shuffled_segment_matrix[0:trig_count,:].mean(axis=0) 

    random_SSVEP = random_SSVEP - random_SSVEP.mean() # baseline correct

    random_amplitudes[loop] = np.ptp(random_SSVEP)


## Plot
plt.subplot(1,2,2)
plt.title('Averaged shuffled segments', size = 30, y=1.03)
plt.ylabel('Amplitude (' + u"\u03bcV)", size=20)
plt.yticks(size=20)
plt.xlabel('Time (ms)', size=20)
plt.xticks(size=20)

plt.plot(random_SSVEP, color = '#FFCC00', alpha = 0.6, linewidth=4)


## Compute & print SNR value
true_amplitude = np.ptp(SSVEP)
average_noise = random_amplitudes.mean()          

SNR = true_amplitude/average_noise
print('SNR = ', round(SNR,3))


