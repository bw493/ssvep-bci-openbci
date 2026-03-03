#!/usr/bin/env python3
"""
Generate synthetic SSVEP data for testing the pipeline
Creates a .fif file with simulated EEG data containing SSVEP responses
"""

import numpy as np
import mne
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import *


def generate_ssvep_signal(freq: float,
                         duration: float,
                         sfreq: float,
                         amplitude: float = 1.0,
                         noise_level: float = 0.5) -> np.ndarray:
    """
    Generate a synthetic SSVEP signal at a specific frequency
    
    Parameters:
    -----------
    freq : float
        SSVEP frequency (Hz)
    duration : float
        Signal duration (seconds)
    sfreq : float
        Sampling frequency (Hz)
    amplitude : float
        Signal amplitude
    noise_level : float
        Noise standard deviation
        
    Returns:
    --------
    signal : ndarray
        Synthetic SSVEP signal
    """
    n_samples = int(duration * sfreq)
    t = np.arange(n_samples) / sfreq
    
    # Generate sinusoidal signal at target frequency
    signal = amplitude * np.sin(2 * np.pi * freq * t)
    
    # Add harmonics for more realistic SSVEP
    signal += 0.3 * amplitude * np.sin(2 * np.pi * 2 * freq * t)
    signal += 0.1 * amplitude * np.sin(2 * np.pi * 3 * freq * t)
    
    # Add noise
    noise = noise_level * np.random.randn(n_samples)
    signal += noise
    
    return signal


def create_synthetic_data(output_file: str = '../data/ssvep_data_raw.fif'):
    """
    Create synthetic SSVEP dataset for testing
    
    Parameters:
    -----------
    output_file : str
        Output file path
    """
    print("\n=== Generating Synthetic SSVEP Data ===")
    
    # Parameters
    sfreq = SAMPLING_RATE
    n_channels = len(CHANNELS)
    n_trials = N_TRIALS
    trial_duration = TRIAL_DURATION
    
    # Calculate total duration
    inter_trial_interval = 2.0  # seconds between trials
    total_duration = n_trials * (trial_duration + inter_trial_interval)
    n_samples = int(total_duration * sfreq)
    
    print(f"Sampling rate: {sfreq} Hz")
    print(f"Channels: {n_channels}")
    print(f"Trials: {n_trials}")
    print(f"Trial duration: {trial_duration} seconds")
    print(f"Total duration: {total_duration:.1f} seconds")
    
    # Initialize data array
    data = np.zeros((n_channels, n_samples))
    
    # Create events array
    events = []
    
    # Generate data for each trial
    for trial_idx in range(n_trials):
        # Randomly choose OPEN or CLOSE
        condition = np.random.choice(['OPEN', 'CLOSE'])
        event_id = 1 if condition == 'OPEN' else 2
        freq = SSVEP_FREQS[condition]
        
        # Trial start time
        trial_start = trial_idx * (trial_duration + inter_trial_interval)
        start_sample = int(trial_start * sfreq)
        
        # Add event marker
        events.append([start_sample, 0, event_id])
        
        # Generate SSVEP signal for each channel
        for ch_idx, ch_name in enumerate(CHANNELS):
            # Channels have different sensitivities
            # Visual channels (P3, P4) have stronger SSVEP
            if ch_name in ['P3', 'P4']:
                amplitude = 2.0
            elif ch_name in ['CPz', 'Cz']:
                amplitude = 1.5
            else:
                amplitude = 1.0
            
            # Generate signal
            ssvep_signal = generate_ssvep_signal(
                freq, trial_duration, sfreq,
                amplitude=amplitude,
                noise_level=0.8
            )
            
            # Add to data
            end_sample = start_sample + len(ssvep_signal)
            data[ch_idx, start_sample:end_sample] += ssvep_signal
        
        if (trial_idx + 1) % 8 == 0:
            print(f"  Generated {trial_idx + 1}/{n_trials} trials...")
    
    # Add baseline noise to entire recording
    baseline_noise = 0.3 * np.random.randn(n_channels, n_samples)
    data += baseline_noise
    
    # Convert events to numpy array
    events = np.array(events, dtype=int)
    
    print(f"\nCreated data shape: {data.shape}")
    print(f"Events: {len(events)}")
    print(f"  OPEN trials: {np.sum(events[:, 2] == 1)}")
    print(f"  CLOSE trials: {np.sum(events[:, 2] == 2)}")
    
    # Create MNE info structure
    info = mne.create_info(
        ch_names=CHANNELS,
        sfreq=sfreq,
        ch_types='eeg'
    )
    
    # Create Raw object
    raw = mne.io.RawArray(data, info)
    
    # Add events as annotations
    event_dict = {1: 'OPEN', 2: 'CLOSE'}
    annotations = mne.annotations_from_events(
        events, sfreq, event_desc=event_dict
    )
    raw.set_annotations(annotations)
    
    # Add stimulus channel
    stim_data = np.zeros((1, n_samples))
    for event in events:
        stim_data[0, event[0]] = event[2]
    
    stim_info = mne.create_info(['STI 014'], sfreq, ['stim'])
    stim_raw = mne.io.RawArray(stim_data, stim_info)
    raw.add_channels([stim_raw], force_update_info=True)
    
    # Save to file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    raw.save(output_file, overwrite=True, verbose='WARNING')
    
    print(f"\n✓ Synthetic data saved to: {output_file}")
    print("=== Data Generation Complete ===\n")
    
    return raw


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate synthetic SSVEP data')
    parser.add_argument('--output', type=str, default='../data/ssvep_data_raw.fif',
                       help='Output file path')
    
    args = parser.parse_args()
    
    # Generate data
    raw = create_synthetic_data(args.output)
    
    print("To run the pipeline with this data:")
    print(f"  python scripts/run_pipeline.py --data {args.output}")
