"""
Surface Laplacian (SLA) spatial filtering
Implements spatial sharpening for improved feature extraction
"""

import numpy as np
import mne
from typing import Dict


def compute_laplacian(raw: mne.io.Raw, 
                      neighbors: Dict[str, list] = None) -> mne.io.Raw:
    """
    Apply Surface Laplacian (local average reference) spatial filtering
    
    The Laplacian highlights local activity by subtracting the average
    of neighboring electrodes from each electrode.
    
    Parameters:
    -----------
    raw : mne.io.Raw
        EEG data
    neighbors : dict, optional
        Dictionary mapping each channel to its neighbors
        If None, uses standard 10-20 montage neighbors
        
    Returns:
    --------
    raw_lap : mne.io.Raw
        Laplacian-filtered data
    """
    print("\n=== Applying Surface Laplacian ===")
    
    # Default neighbors for standard electrode positions
    if neighbors is None:
        neighbors = {
            'Cz': ['C3', 'C4', 'CPz'],
            'C3': ['Cz', 'F3', 'P3'],
            'C4': ['Cz', 'F4', 'P4'],
            'CPz': ['Cz', 'P3', 'P4'],
            'F3': ['C3'],
            'F4': ['C4'],
            'P3': ['C3', 'CPz'],
            'P4': ['C4', 'CPz']
        }
    
    # Get data
    data = raw.get_data()
    ch_names = raw.ch_names
    
    # Apply Laplacian
    lap_data = np.zeros_like(data)
    
    for i, ch in enumerate(ch_names):
        if ch in neighbors and neighbors[ch]:
            # Get indices of neighboring channels
            neighbor_indices = [ch_names.index(n) for n in neighbors[ch] 
                              if n in ch_names]
            
            if neighbor_indices:
                # Laplacian: channel - average of neighbors
                lap_data[i] = data[i] - np.mean(data[neighbor_indices], axis=0)
                print(f"  {ch}: using {len(neighbor_indices)} neighbors")
            else:
                # No neighbors available, keep original
                lap_data[i] = data[i]
                print(f"  {ch}: no neighbors found, keeping original")
        else:
            # No neighbors defined, keep original
            lap_data[i] = data[i]
            print(f"  {ch}: no neighbors defined, keeping original")
    
    # Create new Raw object with Laplacian data
    raw_lap = raw.copy()
    raw_lap._data = lap_data
    
    print("=== Surface Laplacian Complete ===\n")
    
    return raw_lap


def apply_small_laplacian(epochs: mne.Epochs,
                         channel_groups: Dict[str, list] = None) -> mne.Epochs:
    """
    Apply small Laplacian filtering to epoched data
    
    Parameters:
    -----------
    epochs : mne.Epochs
        Epoched EEG data
    channel_groups : dict, optional
        Groups of channels for local Laplacian
        
    Returns:
    --------
    epochs_lap : mne.Epochs
        Laplacian-filtered epochs
    """
    print("\n=== Applying Small Laplacian to Epochs ===")
    
    # Default channel groups for motor/visual areas
    if channel_groups is None:
        channel_groups = {
            'central': ['Cz', 'C3', 'C4'],
            'frontal': ['F3', 'F4'],
            'parietal': ['P3', 'P4', 'CPz']
        }
    
    data = epochs.get_data()
    ch_names = epochs.ch_names
    
    # Apply Laplacian to each group
    lap_data = data.copy()
    
    for group_name, channels in channel_groups.items():
        # Get indices for this group
        group_indices = [i for i, ch in enumerate(ch_names) if ch in channels]
        
        if len(group_indices) > 1:
            # Compute local average
            group_mean = np.mean(data[:, group_indices, :], axis=1, keepdims=True)
            
            # Subtract from each channel in group
            for idx in group_indices:
                lap_data[:, idx, :] = data[:, idx, :] - group_mean.squeeze()
            
            print(f"  {group_name}: {len(group_indices)} channels")
    
    # Create new Epochs object
    epochs_lap = epochs.copy()
    epochs_lap._data = lap_data
    
    print("=== Small Laplacian Complete ===\n")
    
    return epochs_lap


if __name__ == "__main__":
    print("Surface Laplacian module loaded successfully")
    print("Implements spatial sharpening for enhanced feature extraction")
