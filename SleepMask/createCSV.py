# -*- coding: utf-8 -*-
"""
Author: LH
Date: 14.03.23
Functionality: Create example CSV file for input into sleep mask
Assumptions:
    - fade-in: flicker in linearly increasing intensity over 5 min
    - stimulation: constant flicker at max intensity over 5 min
    - CSV file: 1 case = 1 ms
    - triggers: 1 at the beginning of each flicker cycle 
    - length of flicker cycle = 25 ms, length of trigger = 1 ms
    - square-wave flicker, 40 Hz
    - 0 = mask off; 1023 = proxy for max. desired illuminance level (e.g., 20 lux)

"""


# %% Environment Setup

# Packages & functions
import numpy as np



# %% Compute & store CSV file


## Fade-in from 0 to max over approx. 5 min, already with flicker

# Placeholder value for max. lux level
max_lux = 1023

# Integer values of lux placeholder steps
steps_int = np.arange(1, max_lux+1, 1)

# Initialize array for lux placeholder values
lux_array = 0

# Add flicker cycles with fade-in intensity
for i in range(max_lux):
    
    # 1 flicker cycle, square wave, approx. 50 % duty cycle
    light_on = np.repeat(steps_int[i], 13) # 13 ms
    light_off = np.repeat(0, 12) # 12 ms
    flicker_cycle = np.concatenate([light_on, light_off])
    
    # Per placeholder value, run 12 flicker cycles -> 300 ms (*max_lux, adds up to ca. 5 min in total)
    this_intensity_12_cycles = np.tile(flicker_cycle, 12)
    
    # Add flicker cycles to lux array
    lux_array = np.append(lux_array, [this_intensity_12_cycles])
    
# Get length of fade-in
fade_len = len(lux_array)


## Flicker at max. intensity for 5 min

# Nr. of flicker cycles in 5 min
nr_flicker = 5 * 60 * 40

# 1 flicker cycle, square wave, approx. 50 % duty cycle
flicker_cycle = np.append([np.repeat(max_lux, 13)], [np.repeat(0, 12)]) # 13 ms on, 12 ms off

# Array with all flicker cycles
all_cycles = np.tile(flicker_cycle, nr_flicker)

# Add all flicker cycles at max. intensity to lux array
lux_array = np.append(lux_array, [all_cycles])


## Add triggers

# Initialize trigger array: no triggers during fade-in
trigger_array = np.zeros(fade_len)

# For each cycle, set a trigger in the first ms
trigger_cycle = np.append(1, [np.repeat(0, 24)])

# Array with all trigger cycles (same as amount of flicker cycles)
all_triggers = np.tile(trigger_cycle, nr_flicker)

# Add all trigger cycles to trigger array
trigger_array = np.append(trigger_array, [all_triggers])


## Export final array

# Stack lux and trigger arrays
csv_array = np.stack((lux_array, trigger_array))

# Save in CSV, format = int
np.savetxt('example_flicker_trigger_matrix.csv', csv_array, delimiter = ",", fmt='%f')





