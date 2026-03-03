"""
Independent Component Analysis (ICA) for artifact removal
Implements ICA-based artifact correction for EEG data
"""

import mne
from mne.preprocessing import ICA
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import ICA_N_COMPONENTS, ICA_METHOD, ICA_RANDOM_STATE


def fit_ica(raw: mne.io.Raw,
            n_components: float = ICA_N_COMPONENTS,
            method: str = ICA_METHOD,
            random_state: int = ICA_RANDOM_STATE) -> ICA:
    """
    Fit ICA to the data for artifact separation
    
    Parameters:
    -----------
    raw : mne.io.Raw
        Preprocessed EEG data (should be filtered first)
    n_components : float or int
        Number of components to use. If float < 1, represents variance to explain
    method : str
        ICA method ('fastica', 'infomax', 'picard')
    random_state : int
        Random seed for reproducibility
        
    Returns:
    --------
    ica : ICA
        Fitted ICA object
    """
    print(f"\n=== Fitting ICA ===")
    print(f"Method: {method}")
    print(f"Components: {n_components}")
    
    # Initialize ICA
    ica = ICA(n_components=n_components,
              method=method,
              random_state=random_state,
              max_iter=200)
    
    # Fit ICA
    print("Fitting ICA (this may take a moment)...")
    ica.fit(raw, verbose='WARNING')
    
    print(f"ICA fitted with {ica.n_components_} components")
    print(f"Explained variance: {ica.pca_explained_variance_.sum():.2%}")
    
    return ica


def detect_artifact_components(ica: ICA, 
                               raw: mne.io.Raw,
                               method: str = 'auto') -> list:
    """
    Automatically detect artifact components
    
    Parameters:
    -----------
    ica : ICA
        Fitted ICA object
    raw : mne.io.Raw
        Raw data used for ICA fitting
    method : str
        Detection method ('auto', 'eog', 'ecg')
        
    Returns:
    --------
    exclude_idx : list
        Indices of components to exclude
    """
    print(f"\nDetecting artifact components (method: {method})...")
    
    exclude_idx = []
    
    if method == 'auto':
        # Simple heuristic: flag components with very high variance
        # or unusual spatial patterns
        sources = ica.get_sources(raw).get_data()
        
        for idx in range(sources.shape[0]):
            component = sources[idx]
            
            # Check for excessive variance (potential artifacts)
            if np.std(component) > 3 * np.median([np.std(sources[i]) 
                                                   for i in range(sources.shape[0])]):
                exclude_idx.append(idx)
                print(f"  Component {idx}: High variance (likely artifact)")
    
    if not exclude_idx:
        print("  No automatic artifact detection. Manual inspection recommended.")
    else:
        print(f"\nIdentified {len(exclude_idx)} artifact component(s): {exclude_idx}")
    
    return exclude_idx


def apply_ica(raw: mne.io.Raw,
              ica: ICA,
              exclude: list = None) -> mne.io.Raw:
    """
    Apply ICA to remove artifact components from data
    
    Parameters:
    -----------
    raw : mne.io.Raw
        Raw data to clean
    ica : ICA
        Fitted ICA object
    exclude : list
        Indices of components to exclude
        
    Returns:
    --------
    raw_clean : mne.io.Raw
        Cleaned data with artifacts removed
    """
    if exclude is None:
        exclude = []
    
    print(f"\nApplying ICA to remove {len(exclude)} component(s)...")
    
    # Apply ICA and remove components
    raw_clean = raw.copy()
    ica.exclude = exclude
    ica.apply(raw_clean, verbose='WARNING')
    
    print("ICA applied successfully")
    
    return raw_clean


def run_ica_pipeline(raw: mne.io.Raw,
                     auto_detect: bool = True,
                     manual_exclude: list = None) -> tuple:
    """
    Run complete ICA pipeline
    
    Parameters:
    -----------
    raw : mne.io.Raw
        Preprocessed data
    auto_detect : bool
        Whether to automatically detect artifacts
    manual_exclude : list
        Manually specified components to exclude
        
    Returns:
    --------
    raw_clean : mne.io.Raw
        Cleaned data
    ica : ICA
        Fitted ICA object (for inspection)
    """
    print("\n=== Starting ICA Pipeline ===")
    
    # Fit ICA
    ica = fit_ica(raw)
    
    # Detect artifacts
    exclude = []
    if auto_detect:
        exclude = detect_artifact_components(ica, raw)
    
    if manual_exclude:
        exclude.extend(manual_exclude)
        exclude = list(set(exclude))  # Remove duplicates
    
    # Apply ICA
    raw_clean = apply_ica(raw, ica, exclude)
    
    print("=== ICA Pipeline Complete ===\n")
    
    return raw_clean, ica


if __name__ == "__main__":
    print("ICA module loaded successfully")
    print(f"Default settings:")
    print(f"  Method: {ICA_METHOD}")
    print(f"  Components: {ICA_N_COMPONENTS}")
