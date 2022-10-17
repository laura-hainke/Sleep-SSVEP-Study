#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 4 - function to assign triggers to predicted stages

"""


# =============================================================================
# Inputs: 
#   - all_triggers: output from get_triggers
#   - epoch_timestamps, hypnogram: outputs from sleep_staging

# Outputs:
#   - stage_0_triggers, stage_1_triggers, stage_2_triggers, stage_3_triggers, stage_4_triggers: one array per stage with indices of trigger data points assigned to it
# =============================================================================


### Libraries
import numpy as np


def sort_triggers(all_triggers, epoch_timestamps, hypnogram):
    
    epoch_timestamps = epoch_timestamps *1000 # convert to ms
    
    epoch_timestamps = epoch_timestamps.astype(int) # convert to int
    
    epoch_timestamps = epoch_timestamps - epoch_timestamps[0] # convert to relative time (vs. start point)
    
        
    ## Sort triggers into sleep stages
    
    # Initiate at stage 0 = awake
    sleep_stage = 0
    
    # empty lists for triggers
    stage_0 = [] 
    stage_1 = [] 
    stage_2 = [] 
    stage_3 = [] 
    stage_4 = [] 
    
    
    for trigger in all_triggers:
        
        # start times of each epoch relative to current trigger
        relative_val_array = epoch_timestamps - trigger 
        
        # just the negative values (epochs before trigger)
        neg_relative_val_array = relative_val_array[relative_val_array<0] 
    
        # find the closest value
        smallest_difference_index = neg_relative_val_array.argmax() 
        
        # get sleep stage corresponding to epoch
        sleep_stage = hypnogram[smallest_difference_index] 
    
        # add trigger time to corresponding sleep stage list
        if sleep_stage == 0:
            stage_0.append(trigger)
        elif sleep_stage == 1:
            stage_1.append(trigger)
        elif sleep_stage == 2:
            stage_2.append(trigger)            
        elif sleep_stage == 3:
            stage_3.append(trigger)
        elif sleep_stage == 4:
            stage_4.append(trigger)         
    
    
    
    ## Display & return results
        
    # Convert to numpy arrays
    stage_0_triggers = np.array(stage_0, dtype=int)    
    stage_1_triggers = np.array(stage_1, dtype=int) 
    stage_2_triggers = np.array(stage_2, dtype=int) 
    stage_3_triggers = np.array(stage_3, dtype=int) 
    stage_4_triggers = np.array(stage_4, dtype=int) 
        
    # Print nrs of triggers per stage
    print('Awake: ' + str(len(stage_0_triggers)) + ' triggers')
    print('N1: ' + str(len(stage_1_triggers)) + ' triggers')
    print('N2: ' + str(len(stage_2_triggers)) + ' triggers')
    print('N3: ' + str(len(stage_3_triggers)) + ' triggers')
    print('N4: ' + str(len(stage_4_triggers)) + ' triggers')
    
    return stage_0_triggers, stage_1_triggers, stage_2_triggers, stage_3_triggers, stage_4_triggers
    
    
