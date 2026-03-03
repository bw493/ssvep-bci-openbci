"""
Preprocessing module for SSVEP BCI pipeline

Includes:
- Data loading
- Filtering (notch and bandpass)
- Re-referencing (Common Average Reference)
- ICA for artifact removal
"""

from .load_data import load_raw_data, select_channels, get_data_info
from .filters import apply_notch_filter, apply_bandpass_filter, apply_filtering_pipeline
from .rereference import apply_common_average_reference, verify_reference
from .ica import fit_ica, detect_artifact_components, apply_ica, run_ica_pipeline

__all__ = [
    'load_raw_data',
    'select_channels',
    'get_data_info',
    'apply_notch_filter',
    'apply_bandpass_filter',
    'apply_filtering_pipeline',
    'apply_common_average_reference',
    'verify_reference',
    'fit_ica',
    'detect_artifact_components',
    'apply_ica',
    'run_ica_pipeline'
]
