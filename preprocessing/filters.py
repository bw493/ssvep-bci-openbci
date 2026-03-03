"""
Signal filtering utilities for SSVEP BCI pipeline
Implements notch and bandpass filtering
"""

import mne
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import NOTCH_FREQ, BANDPASS_LOW, BANDPASS_HIGH


def apply_notch_filter(raw: mne.io.Raw, 
                       notch_freq: float = NOTCH_FREQ,
                       notch_width: float = 2.0) -> mne.io.Raw:
    """
    Apply notch filter to remove power line noise
    
    Parameters:
    -----------
    raw : mne.io.Raw
        Raw EEG data
    notch_freq : float
        Frequency to notch out (typically 50 or 60 Hz)
    notch_width : float
        Width of the notch filter
        
    Returns:
    --------
    raw : mne.io.Raw
        Filtered data
    """
    print(f"Applying notch filter at {notch_freq} Hz...")
    raw.notch_filter(freqs=notch_freq, 
                     notch_widths=notch_width,
                     verbose='WARNING')
    return raw


def apply_bandpass_filter(raw: mne.io.Raw,
                          l_freq: float = BANDPASS_LOW,
                          h_freq: float = BANDPASS_HIGH) -> mne.io.Raw:
    """
    Apply bandpass filter to isolate SSVEP-relevant frequencies
    
    Parameters:
    -----------
    raw : mne.io.Raw
        Raw EEG data
    l_freq : float
        Low cutoff frequency (Hz)
    h_freq : float
        High cutoff frequency (Hz)
        
    Returns:
    --------
    raw : mne.io.Raw
        Filtered data
    """
    print(f"Applying bandpass filter: {l_freq}-{h_freq} Hz...")
    raw.filter(l_freq=l_freq, h_freq=h_freq, verbose='WARNING')
    return raw


def apply_filtering_pipeline(raw: mne.io.Raw,
                             notch: bool = True,
                             bandpass: bool = True) -> mne.io.Raw:
    """
    Apply complete filtering pipeline
    
    Parameters:
    -----------
    raw : mne.io.Raw
        Raw EEG data
    notch : bool
        Whether to apply notch filter
    bandpass : bool
        Whether to apply bandpass filter
        
    Returns:
    --------
    raw : mne.io.Raw
        Fully filtered data
    """
    print("\n=== Starting Filtering Pipeline ===")
    
    if notch:
        raw = apply_notch_filter(raw)
    
    if bandpass:
        raw = apply_bandpass_filter(raw)
    
    print("=== Filtering Complete ===\n")
    
    return raw


if __name__ == "__main__":
    print("Filtering module loaded successfully")
    print(f"Default settings:")
    print(f"  Notch frequency: {NOTCH_FREQ} Hz")
    print(f"  Bandpass range: {BANDPASS_LOW}-{BANDPASS_HIGH} Hz")
