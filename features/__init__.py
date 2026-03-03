"""
Feature extraction module for SSVEP BCI pipeline

Includes:
- PSD (Power Spectral Density) features
- CSP (Common Spatial Pattern) features
- Surface Laplacian spatial filtering
"""

from .psd_features import compute_psd, extract_ssvep_power, create_psd_features
from .csp import CSP, apply_csp
from .laplacian import compute_laplacian, apply_small_laplacian

__all__ = [
    'compute_psd',
    'extract_ssvep_power',
    'create_psd_features',
    'CSP',
    'apply_csp',
    'compute_laplacian',
    'apply_small_laplacian'
]
