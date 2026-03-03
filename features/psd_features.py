"""
Power Spectral Density (PSD) feature extraction for SSVEP detection
Computes frequency domain features for classification
"""

import mne
import numpy as np
from scipy import signal
from typing import Tuple, Dict
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import SSVEP_FREQS, SAMPLING_RATE


def compute_psd(epochs: mne.Epochs,
                fmin: float = 5.0,
                fmax: float = 45.0,
                n_fft: int = 512) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute Power Spectral Density using Welch's method
    
    Parameters:
    -----------
    epochs : mne.Epochs
        Epoched data
    fmin : float
        Minimum frequency
    fmax : float
        Maximum frequency
    n_fft : int
        FFT length
        
    Returns:
    --------
    psd : ndarray, shape (n_epochs, n_channels, n_freqs)
        Power spectral density
    freqs : ndarray
        Frequency bins
    """
    print(f"Computing PSD ({fmin}-{fmax} Hz)...")
    
    psd, freqs = mne.time_frequency.psd_welch(
        epochs,
        fmin=fmin,
        fmax=fmax,
        n_fft=n_fft,
        verbose='WARNING'
    )
    
    print(f"PSD shape: {psd.shape}")
    print(f"Frequency resolution: {freqs[1] - freqs[0]:.2f} Hz")
    
    return psd, freqs


def extract_ssvep_power(psd: np.ndarray,
                        freqs: np.ndarray,
                        target_freqs: Dict[str, float] = SSVEP_FREQS,
                        bandwidth: float = 0.5) -> Dict[str, np.ndarray]:
    """
    Extract power at specific SSVEP frequencies
    
    Parameters:
    -----------
    psd : ndarray
        Power spectral density
    freqs : ndarray
        Frequency bins
    target_freqs : dict
        Dictionary of label: frequency pairs
    bandwidth : float
        Bandwidth around target frequency to integrate
        
    Returns:
    --------
    features : dict
        Dictionary of label: power features
    """
    print(f"\nExtracting SSVEP power at target frequencies...")
    
    features = {}
    
    for label, freq in target_freqs.items():
        # Find frequency bins within bandwidth
        freq_mask = (freqs >= freq - bandwidth) & (freqs <= freq + bandwidth)
        
        # Average power in the frequency band
        power = np.mean(psd[:, :, freq_mask], axis=2)
        
        features[label] = power
        print(f"  {label} ({freq} Hz): power shape {power.shape}")
    
    return features


def compute_snr(psd: np.ndarray,
                freqs: np.ndarray,
                target_freq: float,
                bandwidth: float = 0.5,
                noise_bandwidth: float = 2.0) -> np.ndarray:
    """
    Compute Signal-to-Noise Ratio for SSVEP response
    
    Parameters:
    -----------
    psd : ndarray
        Power spectral density
    freqs : ndarray
        Frequency bins
    target_freq : float
        Target SSVEP frequency
    bandwidth : float
        Signal bandwidth
    noise_bandwidth : float
        Noise estimation bandwidth (offset from signal)
        
    Returns:
    --------
    snr : ndarray
        SNR values for each epoch and channel
    """
    # Signal: power at target frequency
    signal_mask = (freqs >= target_freq - bandwidth) & (freqs <= target_freq + bandwidth)
    signal_power = np.mean(psd[:, :, signal_mask], axis=2)
    
    # Noise: power in nearby frequencies
    noise_mask = ((freqs >= target_freq - noise_bandwidth - bandwidth) & 
                  (freqs < target_freq - bandwidth)) | \
                 ((freqs > target_freq + bandwidth) & 
                  (freqs <= target_freq + noise_bandwidth + bandwidth))
    noise_power = np.mean(psd[:, :, noise_mask], axis=2)
    
    # Compute SNR
    snr = signal_power / (noise_power + 1e-10)  # Add small constant to avoid division by zero
    
    return snr


def create_psd_features(epochs: mne.Epochs,
                       use_snr: bool = False) -> np.ndarray:
    """
    Create feature matrix from PSD for classification
    
    Parameters:
    -----------
    epochs : mne.Epochs
        Epoched data
    use_snr : bool
        Whether to use SNR instead of raw power
        
    Returns:
    --------
    features : ndarray, shape (n_epochs, n_features)
        Feature matrix for classification
    """
    print("\n=== Creating PSD Features ===")
    
    # Compute PSD
    psd, freqs = compute_psd(epochs)
    
    # Extract power at SSVEP frequencies
    ssvep_features = extract_ssvep_power(psd, freqs)
    
    # Concatenate features from all frequency bands
    feature_list = []
    for label in sorted(ssvep_features.keys()):
        if use_snr:
            freq = SSVEP_FREQS[label]
            snr = compute_snr(psd, freqs, freq)
            feature_list.append(snr)
        else:
            feature_list.append(ssvep_features[label])
    
    # Flatten features (n_epochs, n_channels * n_freq_bands)
    features = np.concatenate([f.reshape(f.shape[0], -1) for f in feature_list], axis=1)
    
    print(f"Final feature shape: {features.shape}")
    print("=== PSD Features Created ===\n")
    
    return features


if __name__ == "__main__":
    print("PSD feature extraction module loaded successfully")
    print(f"Target SSVEP frequencies: {SSVEP_FREQS}")
