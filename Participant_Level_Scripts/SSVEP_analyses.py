# -*- coding: utf-8 -*-
"""
Step 5 - Average segments per stage and condition as ERPs and as FFTs

"""


# =============================================================================
# make_SSVEPs_random: get SSVEP segments for permutation, SNR (true vs. random SSVEP), p-value 
# Inputs:
#   - data: 1 row of data
#   - W_triggers, N2_triggers, N3_triggers, REM_triggers: outputs from sort_triggers
#   - num_loops: nr. of repetitions when creating a random SSVEP (e.g., 100, 1000)

# Outputs:
#   - SNR_stages: ratio of true SSVEP amplitude to random SSVEP amplitude, 1 per stage
#   - p_values: significance level for each SNR value
#   - ssvep_W_segments, ssvep_N2_segments, ssvep_N3_segments, ssvep_REM_segments: 1 matrix per stage with all 25 ms segments assigned to it (for permutation tests)
    
# induced_fft: get FFT segments for permutation, SNR()
# Inputs:
#   - data: 1 row of data
#   - W_triggers, N2_triggers, N3_triggers, REM_triggers: outputs from sort_triggers
#   - length: length of FFT segments, default = 10 (1/length = the frequency resolution) 

# Outputs:
#   - induced_fft_stages: averaged FFTs per stage (for plots)
#   - SNR_40peak_stages: ratio of value at 40 Hz to surrounding frequencies, 1 per stage
#   - p_values: significance level for each SNR value
#   - fft_W_segments, fft_N2_segments, fft_N3_segments, fft_REM_segments: 1 matrix per stage with all 10 s segments assigned to it (for permutation tests)

# "other analyses" section: analysis functions currently unused
# =============================================================================


### Libraries
import numpy as np
import random
import matplotlib.pyplot as plt
from scipy import fftpack, signal, stats


def make_SSVEPs_random(data, W_triggers, N2_triggers, N3_triggers, REM_triggers, num_loops):

    plt.figure()    

    for stage in ('W', 'N2', 'N3', 'REM'):
        
        if stage == 'W':
            triggers = W_triggers
        elif stage == 'N2':
            triggers = N2_triggers
        elif stage == 'N3':
            triggers = N3_triggers
        elif stage == 'REM':
            triggers = REM_triggers


        # high pass filter the data to remove slow drifts        
        high_pass_filter = signal.butter(2, 0.1, 'hp', fs=1000, output='sos')
        data = signal.sosfilt(high_pass_filter, data)
        
        # Make real SSVEP        
        segment_matrix = np.zeros([len(triggers),25]) # empty matrix to put segments into        
                        
        trig_count = 0
        bad_seg_count = 0
        
        plt.subplot(1,2,2)
        
        for trigger in triggers:
     
            segment = data[trigger:trigger+25]       
     
            if np.ptp(segment) > 200: # some segments have large spikes in the data, ignore these
                #print('Bad segment')
                bad_seg_count += 1
            else:
                segment_matrix[trig_count,:] = segment # put into matrix                        
                
                trig_count += 1
                
        print('\n Stage ' + stage)
        print(str(trig_count) + ' good segments')
        print(str(bad_seg_count) + ' bad segments')
                
        SSVEP = segment_matrix[0:trig_count,:].mean(axis=0) # average to make the SSVEP
        
        SSVEP = SSVEP - SSVEP.mean() # baseline correct 
        
        
        # Plot
        plt.subplot(1,2,1)
        plt.title('Averaged Segments (SSVEP)', size = 30, y=1.03)
        plt.ylabel('Amplitude (' + u"\u03bcV)", size=20)
        plt.yticks(size=20)
        plt.xlabel('Time (ms)', size=20)
        plt.xticks(size=20)
        
        if stage == 'W':
            plt.plot(SSVEP, label = 'W', color = '#FFCC00')
            ssvep_W_segments = np.copy(segment_matrix[0:trig_count,:])
        elif stage == 'N2':
            plt.plot(SSVEP, label = 'N2', color = '#99CC99')
            ssvep_N2_segments = np.copy(segment_matrix[0:trig_count,:])
        elif stage == 'N3':
            plt.plot(SSVEP, label = 'N3', color = '#006633')
            ssvep_N3_segments = np.copy(segment_matrix[0:trig_count,:])
        elif stage == 'REM':
            plt.plot(SSVEP, label = 'REM', color = '#0066CC')          
            ssvep_REM_segments = np.copy(segment_matrix[0:trig_count,:])
        
        plt.legend(prop={"size":20})


        ## Signal to noise ratio by randomly shuffling the data points of each segment and then making the SSVEP, compare to true SSVEP - looped               
     
        random_amplitudes = np.zeros([num_loops,])
        
        for loop in range(0,num_loops):
                      
            shuffled_segment_matrix =  np.zeros([len(triggers), 25])  
            
            # loop through all triggers and put the corresponding segment of data into the matrix
            trig_count = 0
            
            for trigger in triggers:
                
                segment =  data[trigger:trigger+25] 
                
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
        plt.xlabel('Time (ms)', size=20)
        plt.xticks(size=20)
        
        if stage == 'W':
            plt.plot(random_SSVEP, label = 'W', color = '#FFCC00')
        elif stage == 'N2':
            plt.plot(random_SSVEP, label = 'N2', color = '#99CC99')
        elif stage == 'N3':
            plt.plot(random_SSVEP, label = 'N3', color = '#006633')
        elif stage == 'REM':
            plt.plot(random_SSVEP, label = 'REM', color = '#0066CC')                
        
        plt.legend(prop={"size":20})

        
        true_amplitude = np.ptp(SSVEP)
        # print('True amplitude = ', true_amplitude)
        
        average_noise = random_amplitudes.mean()
        # print('Amplitude of noise = ', average_noise)
        
        # Z score
        std_noise = np.std(random_amplitudes)                
        Z_score  = (true_amplitude-average_noise) / std_noise   

        # P value
        p_value = stats.norm.sf(abs(Z_score)) #one-sided             
        
        # SNR
        SNR = true_amplitude/average_noise
        
        # Save SNRs and display
        if stage == 'W':
            p2p_W = np.ptp(SSVEP)
            SNR_W = np.copy(SNR)
            p_W = np.copy(p_value)
            
            print('Peak-to-peak amplitude awake:', round(p2p_W, 3))
            print('SNR awake:', SNR_W)
            print('Z_score = ', Z_score)
            print('p-value = ', p_value)
            
        elif stage == 'N2':
            p2p_N2 = np.ptp(SSVEP)
            SNR_N2 = np.copy(SNR)
            p_N2 = np.copy(p_value)
            
            print('Peak-to-peak amplitude N2:', round(p2p_N2, 3))
            print('SNR N2:', SNR_N2)
            print('Z_score = ', Z_score)
            print('p-value = ', p_value)
            
        elif stage == 'N3':
            p2p_N3 = np.ptp(SSVEP)
            SNR_N3 = np.copy(SNR)
            p_N3 = np.copy(p_value)
            
            print('Peak-to-peak amplitude N3:', round(p2p_N3, 3))
            print('SNR N3:', SNR_N3)
            print('Z_score = ', Z_score)
            print('p-value = ', p_value)
            
        elif stage == 'REM':
            p2p_REM = np.ptp(SSVEP)
            SNR_REM = np.copy(SNR)  
            p_REM = np.copy(p_value)
            
            print('Peak-to-peak amplitude REM:', round(p2p_REM, 3))
            print('SNR REM:', SNR_REM)
            print('Z_score = ', Z_score)
            print('p-value = ', p_value)
        
    # Prevent plot overlap
    plt.tight_layout()
        
    # Save outcome variables
    SNR_stages = np.array([SNR_W, SNR_N2, SNR_N3, SNR_REM])
    p_values = np.array([p_W, p_N2, p_N3, p_REM])

    return SNR_stages, p_values, ssvep_W_segments, ssvep_N2_segments, ssvep_N3_segments, ssvep_REM_segments



## 2. Induced FFT, peak amplitude at 40 Hz and SNR
# Segment data into segments of a given length, do an FFT on each segment and then average the FFTs.

def induced_fft(data, W_triggers, N2_triggers, N3_triggers, REM_triggers, length=10): 

    plt.figure()
    
    # Convert to float 32 for lower memory load
    data = data.astype(np.float32)

    for stage in ('W', 'N2', 'N3', 'REM'):        
        
        if stage == 'W':
            triggers = W_triggers
        elif stage == 'N2':
            triggers = N2_triggers
        elif stage == 'N3':
            triggers = N3_triggers
        elif stage == 'REM':
            triggers = REM_triggers
            
        length_of_segment = int(length * 1000) # 1 kHz sample rate
        
        # Empty matrix to put segments into; 1000 as maximal expected value for 4,5 hours recording, keeping memory load low
        segment_matrix = np.zeros([1000,length_of_segment], dtype = np.float32) 
        
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
        
        print('40 Hz value: ' + str(fft_spectrum[40*length]))
        
        # SNR of 40 Hz peak
        peak_values = fft_spectrum[39*length:41*length]
        near_values = np.concatenate([fft_spectrum[38*length:39*length], fft_spectrum[41*length:42*length]])
        SNR = peak_values.mean() / near_values.mean()
        
        # Z score
        std_near = np.std(near_values)                
        Z_score  = (peak_values.mean()-near_values.mean()) / std_near  
        
        # P value
        p_value = stats.norm.sf(abs(Z_score)) #one-sided          
        
        # Save FFTs and plot
        if stage == 'W':
            fft_W = np.copy(fft_spectrum)
            fft_W_segments = np.copy(segment_matrix[0:seg_count,:])
            SNR_W = np.copy(SNR)
            p_W = np.copy(p_value)
            
            print('Nr. of segments W: ' + str(np.shape(fft_W_segments)[0]))
            print('SNR awake:', SNR_W)
            print('Z_score = ', Z_score)
            print('p-value = ', p_value)
                      
            plt.subplot(2,2,1)
            plt.title('Induced FFT awake', size = 20, y=1.03)
            plt.plot(fft_W)
            plt.ylabel('Amplitude', size=18) 
            plt.yticks(size=18)
            plt.xlabel('Frequency', size=18)
            plt.xticks(size=18)
            plt.axvline(x=40*length, ymin=0, color='grey', linestyle='dotted', linewidth=2)
            
        elif stage == 'N2':
            fft_N2 = np.copy(fft_spectrum)
            fft_N2_segments = np.copy(segment_matrix[0:seg_count,:])
            SNR_N2 = np.copy(SNR)
            p_N2 = np.copy(p_value)
            
            print('Nr. of segments N2: ' + str(np.shape(fft_N2_segments)[0]))
            print('SNR N2:', SNR_N2)
            print('Z_score = ', Z_score)
            print('p-value = ', p_value)
            
            plt.subplot(2,2,2)
            plt.title('Induced FFT N2', size = 20, y=1.03)
            plt.plot(fft_N2)
            plt.ylabel('Amplitude', size=18) 
            plt.yticks(size=18)
            plt.xlabel('Frequency', size=18)
            plt.xticks(size=18)
            plt.axvline(x=40*length, ymin=0, color='grey', linestyle='dotted', linewidth=2)        
            
        elif stage == 'N3':
            fft_N3 = np.copy(fft_spectrum)
            fft_N3_segments = np.copy(segment_matrix[0:seg_count,:])
            SNR_N3 = np.copy(SNR)
            p_N3 = np.copy(p_value)
            
            print('Nr. of segments N3: ' + str(np.shape(fft_N3_segments)[0]))
            print('SNR N3:', SNR_N3)
            print('Z_score = ', Z_score)
            print('p-value = ', p_value)
            
            plt.subplot(2,2,3)
            plt.title('Induced FFT N3', size = 20, y=1.03)
            plt.plot(fft_N3)
            plt.ylabel('Amplitude', size=18) 
            plt.yticks(size=18)
            plt.xlabel('Frequency', size=18)
            plt.xticks(size=18)
            plt.axvline(x=40*length, ymin=0, color='grey', linestyle='dotted', linewidth=2)
            
        elif stage == 'REM':
            fft_REM = np.copy(fft_spectrum)
            fft_REM_segments = np.copy(segment_matrix[0:seg_count,:])
            SNR_REM = np.copy(SNR)
            p_REM = np.copy(p_value)
            
            print('Nr. of segments REM: ' + str(np.shape(fft_REM_segments)[0]))
            print('SNR REM:', SNR_REM)
            print('Z_score = ', Z_score)
            print('p-value = ', p_value)
            
            plt.subplot(2,2,4)
            plt.title('Induced FFT REM', size = 20, y=1.03)
            plt.plot(fft_REM)
            plt.ylabel('Amplitude', size=18) 
            plt.yticks(size=18)
            plt.xlabel('Frequency', size=18)
            plt.xticks(size=18)
            plt.axvline(x=40*length, ymin=0, color='grey', linestyle='dotted', linewidth=2)
     
    # Save outcome variables
    induced_fft_stages = np.array([fft_W, fft_N2, fft_N3, fft_REM])
    SNR_40peak_stages = np.array([SNR_W, SNR_N2, SNR_N3, SNR_REM])
    p_values = np.array([p_W, p_N2, p_N3, p_REM])
    
    return induced_fft_stages, SNR_40peak_stages, p_values, fft_W_segments, fft_N2_segments, fft_N3_segments, fft_REM_segments




# %% Other analyses


## SNR: true vs. random SSVEP
# signal to noise ratio by randomly shuffling the data points of each segment and then making the SSVEP, compare to true SSVEP
# instead of peak to peak amplitude, use a time range around the peak

def SNR_random(data, W_triggers, N2_triggers, N3_triggers, REM_triggers):
    
    for stage in ('W', 'N2', 'N3', 'REM'):
        
        if stage == 'W':
            triggers = W_triggers
        elif stage == 'N2':
            triggers = N2_triggers
        elif stage == 'N3':
            triggers = N3_triggers
        elif stage == 'REM':
            triggers = REM_triggers
    
        segment_matrix = np.zeros([len(triggers), 25]) # empty matrix to put segments into
        random_segment_matrix = np.zeros([len(triggers), 25]) # empty matrix to put the randomly shuffled segments into
        seg_count = 0 # keep track of the number of segments
        
        # loop through all triggers and put the corresponding segment of data into the matrix
        for trigger in triggers:
            
            # select a segment of data the lenght of the flicker period, starting from the trigger time 
            segment =  data[trigger:trigger+25] 
            segment_matrix[seg_count,:] = segment
            
            random.shuffle(segment)
    
            random_segment_matrix[seg_count,:] = segment
    
            seg_count += 1
        
        true_SSVEP = segment_matrix.mean(axis=0) # average to make SSVEP
        random_SSVEP = random_segment_matrix.mean(axis=0) # average to make SSVEP of the randomly shuffled data
    
        true_SSVEP = true_SSVEP - true_SSVEP.mean() # baseline correct
        random_SSVEP = random_SSVEP - random_SSVEP.mean()
       # plt.plot(random_SSVEP, '--k')
    
        for condition in ('true', 'random'):
            
            if condition == 'true':
                SSVEP = np.copy(true_SSVEP)
            elif condition == 'random':
                SSVEP = np.copy(random_SSVEP)
    
            SSVEP_repeated = np.tile(SSVEP, 2) # repeat the SSVEP in case the peak area is too near the beginning or end, loops around to the start  
        
            max_SSVEP_index = np.argmax(SSVEP) # get the index of the peak of the SSVEP
            
            ## get the average of the 5 data points around the peak of the SSVEP
            if (len(SSVEP) - max_SSVEP_index) <= 2: # if the peak is near the end of the SSVEP, 
                average_peak_area = SSVEP_repeated[max_SSVEP_index-2:max_SSVEP_index+3].mean()
            elif max_SSVEP_index <= 2: # if the peak index is near the begining of the SSVEP, repeat the SSVEP and move forward by the length of the SSVEP
                average_peak_area = SSVEP_repeated[max_SSVEP_index+len(SSVEP)-2:max_SSVEP_index+len(SSVEP)+3].mean()
            else: # otherwise, just average the area around the peak
                average_peak_area = SSVEP[max_SSVEP_index-2:max_SSVEP_index+3].mean()
            
            min_SSVEP_index = np.argmin(SSVEP) # get the index of the trough of the SSVEP
            
            ## get the average of the 5 data points around the trough of the SSVEP
            if (len(SSVEP) - min_SSVEP_index) <= 2: # if the trough is near the end of the SSVEP, 
                average_trough_area = SSVEP_repeated[min_SSVEP_index-2:min_SSVEP_index+3].mean()
            elif min_SSVEP_index <= 2: # if the trough index is near the begining of the SSVEP, move forward by the length of the SSVEP
                average_trough_area = SSVEP_repeated[min_SSVEP_index+len(SSVEP)-2:min_SSVEP_index+len(SSVEP)+3].mean()
            else: # otherwise, just average the area around the trough
                average_trough_area = SSVEP[min_SSVEP_index-2:min_SSVEP_index+3].mean()
        
        
            SSVEP_range = np.abs(average_peak_area - average_trough_area)
    
            if condition == 'true':
                true_SSVEP_range = np.copy(SSVEP_range)
            elif condition == 'random':
                random_SSVEP_range = np.copy(SSVEP_range)
        
        SNR = np.float(true_SSVEP_range/random_SSVEP_range)
        
        # Save SNRs and display
        if stage == 'W':
            SNR_W = np.copy(SNR)
            print('SNR awake:', SNR_W)
        elif stage == 'N2':
            SNR_N2 = np.copy(SNR)
            print('SNR N2:', SNR_N2)
        elif stage == 'N3':
            SNR_N3 = np.copy(SNR)
            print('SNR N3:', SNR_N3)
        elif stage == 'REM':
            SNR_REM = np.copy(SNR)   
            print('SNR REM:', SNR_REM)
        
    SNR_stages = np.array([SNR_W, SNR_N2, SNR_N3, SNR_REM])

    return SNR_stages



## Evoked FFT
# Segment data into non-overlapping segments of a given length, each time locked to a trigger. Then do an FFT on the averaged segments.

def evoked_fft(data, W_triggers, N2_triggers, N3_triggers, REM_triggers, length=1): # length = length of segment to use in seconds (1/length = the frequency resolution)
    
    for stage in ('W', 'N2', 'N3', 'REM'):
        
        if stage == 'W':
            triggers = W_triggers
        elif stage == 'N2':
            triggers = N2_triggers
        elif stage == 'N3':
            triggers = N3_triggers
        elif stage == 'REM':
            triggers = REM_triggers
    
        length_of_segment = int(length * 1000) # 1 kHz sampling rate
        
        segment_matrix = np.zeros([len(triggers), length_of_segment]) # empty matrix to put segments into
        
        seg_count = 0
       
        k = 0
        
        while k < len(data) - length_of_segment: # loop until the end of data
        
            if k in triggers: # if data point is a trigger
            
                segment = data[k:k+length_of_segment] # get a segment of data
        
                segment_matrix[seg_count,:] = segment # put into matrix
        
                seg_count+=1
                
                k = k + length_of_segment # move forward the length of the segment, so segments are not overlapping
        
            k+=1
        
        SSVEP = segment_matrix[0:seg_count,:].mean(axis=0)       
        
        SSVEP = SSVEP - SSVEP.mean() # baseline correct
            
        SSVEP_hanning = SSVEP * np.hanning(length_of_segment) # multiply by hanning window
            
        fft_SSVEP = np.abs(fftpack.fft(SSVEP_hanning)) # FFT
        
        # Save FFTs and plot
        if stage == 'W':
            fft_W = np.copy(fft_SSVEP)
            plt.figure()
            plt.subplot(2,2,1)
            plt.title('Evoked FFT awake')
            plt.plot(fft_W)
        elif stage == 'N2':
            fft_N2 = np.copy(fft_SSVEP)
            plt.subplot(2,2,2)
            plt.title('Evoked FFT N2')
            plt.plot(fft_N2)
        elif stage == 'N3':
            fft_N3 = np.copy(fft_SSVEP)
            plt.subplot(2,2,3)
            plt.title('Evoked FFT N3')
            plt.plot(fft_N3)
        elif stage == 'REM':
            fft_REM = np.copy(fft_SSVEP)
            plt.subplot(2,2,4)
            plt.title('Evoked FFT REM')
            plt.plot(fft_REM)
            
    evoked_fft_stages = np.array([fft_W, fft_N2, fft_N3, fft_REM])

    return evoked_fft_stages
            


## 50/50 split & correlation of SSVEPs
# Randomly split the triggers from one condition to create two SSVEPs and return the correlation between the two
def compare_SSVEPs_split(data, W_triggers, N2_triggers, N3_triggers, REM_triggers):
    
    for stage in ('W', 'N2', 'N3', 'REM'):
    
        if stage == 'W':
            triggers = W_triggers
        elif stage == 'N2':
            triggers = N2_triggers
        elif stage == 'N3':
            triggers = N3_triggers
        elif stage == 'REM':
            triggers = REM_triggers
    

        seg_nums = np.arange(0,len(triggers)) # an index for seach segment
     
        random.shuffle(seg_nums) # randomize the order
        
        for random_half in range(0,2): # select the first half, and then the second half, of the randomized segments, and make an SSVEP of each
    
            if random_half == 0:
                random_half_triggers = triggers[seg_nums[0:int(len(triggers)/2)]]
            elif random_half == 1:
                random_half_triggers = triggers[seg_nums[int(len(triggers)/2):]]
    
            segment_matrix = np.zeros([len(random_half_triggers), 25]) # empty matrix to put the segments into
            seg_count = 0 # keep track of the number of segments
       
            for trigger in random_half_triggers:
                segment =  data[trigger:trigger+25] 
                segment_matrix[seg_count,:] = segment
                seg_count += 1
    
            SSVEP = segment_matrix[0:seg_count,:].mean(axis=0) # average to make SSVEP
            
            SSVEP = SSVEP - SSVEP.mean() # baseline correct
    
            if random_half == 0:
                SSVEP_1 = np.copy(SSVEP)
            elif random_half == 1:
                SSVEP_2 = np.copy(SSVEP)
       
        correlation = np.corrcoef(SSVEP_1, SSVEP_2)[0,1]
        
        # Save correlation values and display
        if stage == 'W':
            corr_W = np.copy(correlation)
            print('Correlation awake:', corr_W)
        elif stage == 'N2':
            corr_N2 = np.copy(correlation)
            print('Correlation N2:', corr_N2)
        elif stage == 'N3':
            corr_N3 = np.copy(correlation)
            print('Correlation N3:', corr_N3)
        elif stage == 'REM':
            corr_REM = np.copy(correlation)   
            print('Correlation REM:', corr_REM)
        
    correlations_stages = np.array([corr_W, corr_N2, corr_N3, corr_REM])

    return correlations_stages


    