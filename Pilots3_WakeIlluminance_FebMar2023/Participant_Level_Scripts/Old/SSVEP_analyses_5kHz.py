# -*- coding: utf-8 -*-
"""
Average segments per condition as ERPs and as FFTs

"""


# =============================================================================
# make_SSVEPs_random: get SSVEP segments for permutation, SNR (true vs. random SSVEP), p-value 
# Inputs:
#   - data: 1 row of data
#   - triggers: output from get_triggers
# 	- condition: name of condition, for plot
#   - num_loops: nr. of repetitions when creating a random SSVEP (e.g., 100, 1000)

# Outputs:
#   - true_amplitude: true peak-to-peak amplitude of the SSVEP
#   - SNR: ratio of true SSVEP amplitude to random SSVEP amplitude

# make_SSVEP: same as make_SSVEPs_random, but no SNR, just plot as output
    
# induced_fft: get FFT segments for permutation, SNR()
# Inputs:
#   - data: 1 row of data
#   - triggers: output from get_triggers
# 	- condition: name of condition, for plot
#   - length: length of FFT segments, default = 10 (1/length = the frequency resolution) 

# Outputs:
#   - FFT_40: value of FFT at 40 Hz
# 	- SNR: ratio of 40 Hz value to surrounding values

# linear_interpolation: remove flicker artifacts from data series using linear interpolation
# (copied from James' GitHub)
# Inputs:
#   - data: 1 row of data
#   - triggers: output from get_triggers
#   - time_1: 1st sample in a 25 ms segment that is affected by artifact (LED on)
#   - time_2: 1st sample in 2nd half in a 25 ms segment that is affected by artifact (LED off)
#   - trig_length: duration of artifact in nr. of samples

# =============================================================================


### Libraries
import numpy as np
import random
import matplotlib.pyplot as plt
from scipy import fftpack, signal, stats


def make_SSVEP_5kHz(data, triggers, condition):
    
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
    plt.title('Averaged Segments (SSVEP): ' + condition, size = 30, y=1.03)
    plt.ylabel('Amplitude (' + u"\u03bcV)", size=20)
    plt.yticks(size=20)
    plt.xlabel('Time (ms) * 5', size=20)
    plt.xticks(size=20)
    
    plt.plot(SSVEP, color = '#FFCC00') # plot averaged SSVEP graph


## 2. Induced FFT, peak amplitude at 40 Hz and SNR
# Segment data into segments of a given length, do an FFT on each segment and then average the FFTs.

def induced_fft_5kHz(data, triggers, condition, length=10): 

    plt.figure()
    
    # Convert to float 32 for lower memory load
    data = data.astype(np.float32)
            
    length_of_segment = int(length * 5000) # 5 kHz sample rate
    
    # Empty matrix to put segments into
    segment_matrix = np.zeros([350,length_of_segment], dtype = np.float32) 
    
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

