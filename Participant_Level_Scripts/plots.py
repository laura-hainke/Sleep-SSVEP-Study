#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions to generate SSVEP and FFT plots

"""


# =============================================================================
# plot_segs_stage: plot all segments & final SSVEP for 1 stage
# plot_SSVEPs: 1 figure for flicker data set, 4 graphs (1 per stage)
# plot_SSVEPs_blackout: use directly after plot_SSVEPs to plot blackout onto the same figure, or plot blackout alone
# Inputs:
#   - data: one row of data, either 1 channel or an average. E.g., occipital average, POz, EOG1...
#   - W_triggers, N2_triggers, N3_triggers, REM_triggers: outputs from sort_triggers

# plot_SSVEPs_condition: 1 figure for 1 stage (e.g., N2), flicker + blackout
# Inputs:
#   - data_flicker, data_blackout: one row of data each, either 1 channel or an average
#   - triggers_flicker, triggers_blackout: outputs from sort_triggers, same stage
#   - stage: one of W, N2, N3, REM (same as in triggers)

# plot_FFT_stages: 1 figure with 4 subplots, 1 per stage, flicker + blackout
# Inputs:
#   - flicker_fft_stages, blackout_fft_stages: outputs from induced_fft
#   - length: length of FFT segments in seconds, default = 10

# No outputs, functions just return plots
# =============================================================================


### Libraries
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal


### Process data & plot all segments & final SSVEP for 1 stage

def plot_segs_stage(data, triggers, condition):
    
    offset = 0 # use this offset to make sure the trigger artefacts are not at the edge of the SSVEP, this makes linear interpolation easier
    
    plt.figure()
                
    # high pass filter the data to remove slow drifts        
    sample_rate = 1000
    
    high_pass_filter = signal.butter(2, 0.1, 'hp', fs=sample_rate, output='sos')
    data = signal.sosfilt(high_pass_filter, data)
           
    segment_matrix = np.zeros([len(triggers),25]) 
    seg_1sec_matrix = np.zeros([len(triggers),1000]) 
                
    trig_count = 0
    bad_seg_count = 0
    plot_count = 0
    
    for trigger in triggers:
 
        segment = data[trigger-offset:trigger+25-offset] # 25 ms segment for SSVEP       
        
        seg_1sec = data[trigger-500:trigger+500] # 1 sec segment for bad data check
 
        if np.ptp(seg_1sec) > 500: # some segments have large spikes in the data, ignore these. Here, check for bad data in 1 sec segments centred around each trigger
            bad_seg_count += 1
            
        else:
            
            segment = segment - segment.mean() # baseline correct  
            segment_matrix[trig_count,:] = segment # put into matrix            
            
            seg_1sec = seg_1sec - seg_1sec.mean() # baseline correct
            seg_1sec_matrix[trig_count,:] = seg_1sec
            
            if (trig_count % 40) == 0: # plot only every 40th trigger (at least 1000 data points between 2 triggers) to restrain overlap
                plt.plot(seg_1sec, color = 'blue', linewidth=0.5) # plot
                plot_count += 1
            
            trig_count += 1
      
         
    print(str(trig_count) + ' good segments')
    print(str(bad_seg_count) + ' bad segments')
    print(str(plot_count) + ' 1-sec segs plotted')
            
    # SSVEP = segment_matrix[0:trig_count,:].mean(axis=0) # average to make the SSVEP    
    # SSVEP = SSVEP - SSVEP.mean() # baseline correct        
    # plt.plot(SSVEP, color = 'red', linewidth=3)  
    
    avg_seg_1sec = seg_1sec_matrix[0:trig_count,:].mean(axis=0)
    avg_seg_1sec = avg_seg_1sec - avg_seg_1sec.mean()
    plt.plot(avg_seg_1sec, color = 'red', linewidth = 3)
    
    plt.title(condition, size = 30, y=1.03)
    plt.ylabel('Amplitude (' + u"\u03bcV)", size=20)
    plt.yticks(size=20)
    plt.xlabel('Time (ms)', size=20)
    plt.xticks(size=20)
    
    



### Process data & plot SSVEPs per stage (W/N2/N3/REM)

def plot_SSVEPs(data, W_triggers, N2_triggers, N3_triggers, REM_triggers):
    
    offset = 0 # use this offset to make sure the trigger artefacts are not at the edge of the SSVEP, this makes linear interpolation easier
    
    plt.figure()
    
    for sleep_stage in (0,2,3,4): # all stages except N1
    
        print('\nSLEEP - STAGE ' + str(sleep_stage))    
            
        if sleep_stage == 0:
            triggers = W_triggers
        elif sleep_stage == 2:
            triggers = N2_triggers
        elif sleep_stage == 3:
            triggers = N3_triggers
        elif sleep_stage == 4:
            triggers = REM_triggers                
                               
            
        # high pass filter the data to remove slow drifts        
        sample_rate = 1000
        
        high_pass_filter = signal.butter(2, 0.1, 'hp', fs=sample_rate, output='sos')
        data = signal.sosfilt(high_pass_filter, data)
               
        segment_matrix = np.zeros([len(triggers),25]) 
                    
        trig_count = 0
        bad_seg_count = 0
        
        for trigger in triggers:
     
            segment = data[trigger-offset:trigger+25-offset]     
            
            seg_1sec = data[trigger-500:trigger+500] # 1 sec segment for bad data check
     
            if np.ptp(seg_1sec) > 500: # some segments have large spikes in the data, ignore these. Here, check for bad data in 1 sec segments centred around each trigger
                
                bad_seg_count += 1
                
            else:
                segment_matrix[trig_count,:] = segment # put into matrix
                
                trig_count += 1
                
        print(str(trig_count) + ' good segments')
        print(str(bad_seg_count) + ' bad segments')
                
        SSVEP = segment_matrix[0:trig_count,:].mean(axis=0) # average to make the SSVEP
        
        SSVEP = SSVEP - SSVEP.mean() # baseline correct        
        
        
        # Plot current channel
        plt.title('Averaged Segments (SSVEP)', size = 30, y=1.03)
        
        plt.ylabel('Amplitude (' + u"\u03bcV)", size=20)
        plt.yticks(size=20)
        plt.xlabel('Time (ms)', size=20)
        plt.xticks(size=20)
        
        if sleep_stage == 0:
            plt.plot(SSVEP, label = 'W', color = '#FFCC00', linewidth=4)
            print('SSVEP-P2P: ' + str(np.ptp(SSVEP)))
        elif sleep_stage == 2:
            plt.plot(SSVEP, label = 'N2', color = '#999900', linewidth=4)
            print('SSVEP-P2P: ' + str(np.ptp(SSVEP)))
        elif sleep_stage == 3:
            plt.plot(SSVEP, label = 'N3', color = '#006633', linewidth=4)
            print('SSVEP-P2P: ' + str(np.ptp(SSVEP)))
        elif sleep_stage == 4:
            plt.plot(SSVEP, label = 'REM', color = '#0066CC', linewidth=4)    
            print('SSVEP-P2P: ' + str(np.ptp(SSVEP)))      
    
        plt.legend(prop={"size":20})
        
        
        
def plot_SSVEPs_blackout(data, W_triggers, N2_triggers, N3_triggers, REM_triggers):
    
    offset = 0 
    
    # plt.figure()
    
    for sleep_stage in (0,2,3,4): # all stages except N1
    
        print('\nSLEEP - STAGE ' + str(sleep_stage))    
            
        if sleep_stage == 0:
            triggers = W_triggers
        elif sleep_stage == 2:
            triggers = N2_triggers
        elif sleep_stage == 3:
            triggers = N3_triggers
        elif sleep_stage == 4:
            triggers = REM_triggers                
                               
            
        # high pass filter the data to remove slow drifts        
        sample_rate = 1000
        
        high_pass_filter = signal.butter(2, 0.1, 'hp', fs=sample_rate, output='sos')
        data = signal.sosfilt(high_pass_filter, data)
               
        segment_matrix = np.zeros([len(triggers),25]) # first make a one second SSVEP, from each trigger
                    
        trig_count = 0
        bad_seg_count = 0
        
        for trigger in triggers:
     
            segment = data[trigger-offset:trigger+25-offset]       
     
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
        
        
        # Plot current channel
        # plt.title('Averaged Segments (SSVEP)', size = 30, y=1.03)
        
        # plt.ylabel('Amplitude (' + u"\u03bcV)", size=20)
        # plt.yticks(size=20)
        # plt.xlabel('Time (ms)', size=20)
        # plt.xticks(size=20)
        
        if sleep_stage == 0:
            plt.plot(SSVEP, label = 'W_blackout', color = '#FFCC00', alpha = 0.5, linewidth=4)
            print('SSVEP-P2P: ' + str(np.ptp(SSVEP))) 
        elif sleep_stage == 2:
            plt.plot(SSVEP, label = 'N2_blackout', color = '#999900', alpha = 0.5, linewidth=4)
            print('SSVEP-P2P: ' + str(np.ptp(SSVEP))) 
        elif sleep_stage == 3:
            plt.plot(SSVEP, label = 'N3_blackout', color = '#006633', alpha = 0.5, linewidth=4)
            print('SSVEP-P2P: ' + str(np.ptp(SSVEP))) 
        elif sleep_stage == 4:
            plt.plot(SSVEP, label = 'REM_blackout', color = '#0066CC', alpha = 0.5, linewidth=4) 
            print('SSVEP-P2P: ' + str(np.ptp(SSVEP)))                
    
        plt.legend(prop={"size":20})
        
        
        
def plot_SSVEPs_condition(data_flicker, triggers_flicker, data_blackout, triggers_blackout, stage):
    
    offset = 0 # use this offset to make sure the trigger artefacts are not at the edge of the SSVEP, this makes linear interpolation easier
    
    plt.figure()
    
    plt.title('Averaged Segments - ' + stage, size = 30, y=1.03)
        
    plt.ylabel('Amplitude (' + u"\u03bcV)", size=20)
    plt.yticks(size=20)
    plt.xlabel('Time (ms)', size=20)
    plt.xticks(size=20)
    
    for condition in ('flicker','blackout'):     
    
        if condition == 'flicker':
            data = data_flicker
            triggers = triggers_flicker
        elif condition == 'blackout':
            data = data_blackout     
            triggers = triggers_blackout            
            
        # high pass filter the data to remove slow drifts        
        sample_rate = 1000
        
        high_pass_filter = signal.butter(2, 0.1, 'hp', fs=sample_rate, output='sos')
        data = signal.sosfilt(high_pass_filter, data)
               
        segment_matrix = np.zeros([len(triggers),25]) # first make a one second SSVEP, from each trigger
                    
        trig_count = 0
        bad_seg_count = 0
        
        for trigger in triggers:
     
            segment = data[trigger-offset:trigger+25-offset]       
     
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
        
        
        if stage == 'W':
            color = '#FFCC00'
        elif stage == 'N2':
            color = '#999900'
        elif stage == 'N3':
            color = '#006633'
        elif stage == 'REM':
            color = '#0066CC'
        
        if condition == 'flicker':
            plt.plot(SSVEP, label = 'Flicker', color = color, linewidth=4)
        elif condition == 'blackout':
            plt.plot(SSVEP, label = 'Blackout', color = color, alpha = 0.5, linewidth=4)             
    
        plt.legend(prop={"size":20})
            


def plot_FFT_stages(flicker_fft_stages, blackout_fft_stages, length=10):
    
    plt.figure()
    
    ## W
    plt.subplot(2,2,1)

    plt.plot(flicker_fft_stages[0,:], label = 'Flicker', color = '#FFCC00', linewidth = 4)
    plt.plot(blackout_fft_stages[0,:], label = 'Blackout', color = '#FFCC00', alpha = 0.5, linewidth = 4)

    plt.title('Induced FFT - W', size = 20, y=1.03)    
    plt.ylabel('Amplitude', size=18) 
    plt.yticks(size=18, color = 'w')
    plt.xlabel('Frequency', size=18)
    plt.xticks(size=18, color = 'w')
    plt.axvline(x=40*length, ymin=0, color='grey', linestyle='dotted', linewidth=2)
    plt.legend(prop={"size":20})
    plt.axis([350, 450, 200, 1300])
    
    ## N2
    plt.subplot(2,2,2)
    
    plt.plot(flicker_fft_stages[1,:], label = 'Flicker', color = '#999900', linewidth = 4)
    plt.plot(blackout_fft_stages[1,:], label = 'Blackout', color = '#999900', alpha = 0.5, linewidth = 4)
    
    plt.title('Induced FFT - N2', size = 20, y=1.03)       
    plt.ylabel('Amplitude', size=18) 
    plt.yticks(size=18, color = 'w')
    plt.xlabel('Frequency', size=18)
    plt.xticks(size=18, color = 'w')
    plt.axvline(x=40*length, ymin=0, color='grey', linestyle='dotted', linewidth=2)
    plt.legend(prop={"size":20})
    plt.axis([350, 450, 200, 1300])

    ## N3
    plt.subplot(2,2,3)
    
    plt.plot(flicker_fft_stages[2,:], label = 'Flicker', color = '#006633', linewidth = 4)
    plt.plot(blackout_fft_stages[2,:], label = 'Blackout', color = '#006633', alpha = 0.5, linewidth = 4)

    plt.title('Induced FFT - N3', size = 20, y=1.03)       
    plt.ylabel('Amplitude', size=18) 
    plt.yticks(size=18, color = 'w')
    plt.xlabel('Frequency', size=18)
    plt.xticks(size=18, color = 'w')
    plt.axvline(x=40*length, ymin=0, color='grey', linestyle='dotted', linewidth=2)
    plt.legend(prop={"size":20})
    plt.axis([350, 450, 200, 1300])
    
    ## REM
    plt.subplot(2,2,4)
    
    plt.plot(flicker_fft_stages[3,:], label = 'Flicker', color = '#0066CC', linewidth = 4)
    plt.plot(blackout_fft_stages[3,:], label = 'Blackout', color = '#0066CC', alpha = 0.5, linewidth = 4)

    plt.title('Induced FFT - REM', size = 20, y=1.03) 
    plt.ylabel('Amplitude', size=18) 
    plt.yticks(size=18, color = 'w')
    plt.xlabel('Frequency', size=18)
    plt.xticks(size=18, color = 'w')
    plt.axvline(x=40*length, ymin=0, color='grey', linestyle='dotted', linewidth=2)
    plt.legend(prop={"size":20})
    plt.axis([350, 450, 200, 1300])






