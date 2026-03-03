"""
Data loading utilities for SSVEP BCI pipeline
Handles loading and initial validation of EEG data
"""

import mne
import numpy as np
from typing import Optional, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import CHANNELS


def load_raw_data(filepath: str, preload: bool = True) -> mne.io.Raw:
    """
    Load raw EEG data from FIF file
    
    Parameters:
    -----------
    filepath : str
        Path to the .fif file
    preload : bool
        Whether to load data into memory immediately
        
    Returns:
    --------
    raw : mne.io.Raw
        Raw EEG data object
    """
    print(f"Loading data from: {filepath}")
    raw = mne.io.read_raw_fif(filepath, preload=preload, verbose='WARNING')
    
    print(f"Data loaded: {raw.info['nchan']} channels, "
          f"{raw.n_times} samples, "
          f"sampling rate: {raw.info['sfreq']} Hz")
    
    return raw


def select_channels(raw: mne.io.Raw, channels: Optional[List[str]] = None) -> mne.io.Raw:
    """
    Select specific EEG channels
    
    Parameters:
    -----------
    raw : mne.io.Raw
        Raw EEG data
    channels : list of str, optional
        List of channel names to keep. If None, uses default from config
        
    Returns:
    --------
    raw : mne.io.Raw
        Data with selected channels only
    """
    if channels is None:
        channels = CHANNELS
    
    # Check which channels are available
    available_channels = [ch for ch in channels if ch in raw.ch_names]
    missing_channels = [ch for ch in channels if ch not in raw.ch_names]
    
    if missing_channels:
        print(f"Warning: Missing channels: {missing_channels}")
    
    print(f"Selecting channels: {available_channels}")
    raw.pick_channels(available_channels)
    
    return raw


def get_data_info(raw: mne.io.Raw) -> dict:
    """
    Extract and display key information about the data
    
    Parameters:
    -----------
    raw : mne.io.Raw
        Raw EEG data
        
    Returns:
    --------
    info_dict : dict
        Dictionary containing data information
    """
    info_dict = {
        'n_channels': raw.info['nchan'],
        'channel_names': raw.ch_names,
        'sampling_rate': raw.info['sfreq'],
        'n_samples': raw.n_times,
        'duration': raw.times[-1],
        'highpass': raw.info['highpass'],
        'lowpass': raw.info['lowpass']
    }
    
    print("\n=== Data Information ===")
    for key, value in info_dict.items():
        print(f"{key}: {value}")
    print("========================\n")
    
    return info_dict


if __name__ == "__main__":
    # Example usage
    test_file = "../data/ssvep_data_raw.fif"
    if os.path.exists(test_file):
        raw = load_raw_data(test_file)
        raw = select_channels(raw)
        info = get_data_info(raw)
    else:
        print(f"Test file not found: {test_file}")
        print("This module is ready to use when you have data available.")
