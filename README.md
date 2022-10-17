# Sleep-SSVEP-Study

This repository contains the materials used for an ongoing study on Steady-State Visually Evoked Potentials (SSVEPs) in sleep.

Setup:
- Mobile EEG Mentalab Explore, used in offline mode
- Mentalab EEG cap (size M or L)
- Customized sleep mask, with in-built red LEDs wired to an Arduino Nano
- EEG channels: C3, C4, TP10, POz, O1, O2, EOG, EOG + photodiode
- Sampling rate = 1000 Hz; red LED flicker frequency = 40 Hz
- 1 photodiode trigger per second, digitally segmented into 40 / sec

Conditions:
- Session 1: Blackout. 4.5 hours of recording starting at bedtime, with the Arduino on and a black cloth preventing LED light from reaching the subject's eyes (control condition).
- Session 2: Flicker. 4.5 hours of recording starting at bedtime, light stimulation visible (experimental condition).
- Condition order is kept equal across participants; at least 1 night between recordings.

Anonymized participant data and scripts for statistical group analysis will be uploaded after study completion.

Sr. Researcher: JamesDowsettNeuroscience
