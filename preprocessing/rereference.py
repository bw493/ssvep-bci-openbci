"""
Re-referencing utilities for SSVEP BCI pipeline
Implements Common Average Reference (CAR)
"""

import mne
import numpy as np


def apply_common_average_reference(raw: mne.io.Raw) -> mne.io.Raw:
    """
    Apply Common Average Reference (CAR) to EEG data
    
    The CAR subtracts the average of all channels from each channel,
    improving spatial resolution and reducing common noise.
    
    Parameters:
    -----------
    raw : mne.io.Raw
        Raw EEG data
        
    Returns:
    --------
    raw : mne.io.Raw
        Re-referenced data
    """
    print("Applying Common Average Reference (CAR)...")
    
    # Store original reference for info
    orig_ref = raw.info.get('custom_ref_applied', 'unknown')
    print(f"Original reference: {orig_ref}")
    
    # Apply CAR
    raw.set_eeg_reference('average', projection=False, verbose='WARNING')
    
    print(f"New reference: Common Average Reference")
    print(f"Number of channels used in average: {raw.info['nchan']}")
    
    return raw


def verify_reference(raw: mne.io.Raw) -> None:
    """
    Verify that re-referencing was applied correctly
    
    Parameters:
    -----------
    raw : mne.io.Raw
        Re-referenced data
    """
    # Check if the average across channels is close to zero
    data = raw.get_data()
    channel_average = np.mean(data, axis=0)
    overall_mean = np.mean(np.abs(channel_average))
    
    print(f"\nRe-referencing verification:")
    print(f"Mean absolute value across channels: {overall_mean:.2e}")
    
    if overall_mean < 1e-10:
        print("✓ Re-referencing verified: channel average is effectively zero")
    else:
        print("⚠ Warning: channel average is not close to zero")
    

if __name__ == "__main__":
    print("Re-referencing module loaded successfully")
    print("Implements Common Average Reference (CAR)")
