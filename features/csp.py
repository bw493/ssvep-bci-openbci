"""
Common Spatial Pattern (CSP) feature extraction
Implements CSP for spatial filtering and feature extraction
"""

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from typing import Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import N_CSP_COMPONENTS


class CSP(BaseEstimator, TransformerMixin):
    """
    Common Spatial Pattern (CSP) for EEG feature extraction
    
    CSP finds spatial filters that maximize variance for one class
    while minimizing it for another class.
    """
    
    def __init__(self, n_components: int = N_CSP_COMPONENTS):
        """
        Parameters:
        -----------
        n_components : int
            Number of CSP components to use (taken from both ends)
        """
        self.n_components = n_components
        self.filters_ = None
        self.patterns_ = None
        
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'CSP':
        """
        Fit CSP spatial filters
        
        Parameters:
        -----------
        X : ndarray, shape (n_trials, n_channels, n_samples)
            EEG data
        y : ndarray, shape (n_trials,)
            Class labels (must be binary: 0 and 1)
            
        Returns:
        --------
        self : CSP
            Fitted CSP object
        """
        # Separate data by class
        X_class0 = X[y == 0]
        X_class1 = X[y == 1]
        
        # Compute covariance matrices
        cov_class0 = self._compute_covariance(X_class0)
        cov_class1 = self._compute_covariance(X_class1)
        
        # Solve generalized eigenvalue problem
        eigenvalues, eigenvectors = self._solve_eigenvalue_problem(
            cov_class0, cov_class1
        )
        
        # Select filters (m components from each end)
        n = self.n_components
        selected_indices = np.concatenate([
            np.arange(n),  # First n (highest for class 0)
            np.arange(-n, 0)  # Last n (highest for class 1)
        ])
        
        self.filters_ = eigenvectors[:, selected_indices]
        self.patterns_ = np.linalg.pinv(self.filters_).T
        
        return self
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Apply CSP filters and extract features
        
        Parameters:
        -----------
        X : ndarray, shape (n_trials, n_channels, n_samples)
            EEG data
            
        Returns:
        --------
        features : ndarray, shape (n_trials, 2*n_components)
            CSP features (log variance of filtered signals)
        """
        # Apply spatial filters
        X_filtered = np.asarray([
            np.dot(self.filters_.T, trial) for trial in X
        ])
        
        # Compute log variance as features
        features = np.log(np.var(X_filtered, axis=2))
        
        return features
    
    def _compute_covariance(self, X: np.ndarray) -> np.ndarray:
        """
        Compute average normalized covariance matrix
        
        Parameters:
        -----------
        X : ndarray, shape (n_trials, n_channels, n_samples)
            EEG data for one class
            
        Returns:
        --------
        cov : ndarray, shape (n_channels, n_channels)
            Average covariance matrix
        """
        n_trials, n_channels, n_samples = X.shape
        
        # Compute covariance for each trial
        cov_matrices = np.zeros((n_trials, n_channels, n_channels))
        for i, trial in enumerate(X):
            cov_matrices[i] = np.cov(trial)
            # Normalize by trace
            cov_matrices[i] /= np.trace(cov_matrices[i])
        
        # Average across trials
        cov = np.mean(cov_matrices, axis=0)
        
        return cov
    
    def _solve_eigenvalue_problem(self,
                                  cov_class0: np.ndarray,
                                  cov_class1: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Solve generalized eigenvalue problem
        
        Parameters:
        -----------
        cov_class0 : ndarray
            Covariance matrix for class 0
        cov_class1 : ndarray
            Covariance matrix for class 1
            
        Returns:
        --------
        eigenvalues : ndarray
            Eigenvalues sorted in descending order
        eigenvectors : ndarray
            Corresponding eigenvectors
        """
        # Compute composite covariance
        cov_composite = cov_class0 + cov_class1
        
        # Regularize to ensure invertibility
        reg = 1e-6
        cov_composite += reg * np.eye(cov_composite.shape[0])
        
        # Solve generalized eigenvalue problem
        eigenvalues, eigenvectors = np.linalg.eig(
            np.linalg.solve(cov_composite, cov_class0)
        )
        
        # Sort by eigenvalues in descending order
        sort_indices = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[sort_indices]
        eigenvectors = eigenvectors[:, sort_indices]
        
        # Make eigenvalues real (should be real anyway)
        eigenvalues = np.real(eigenvalues)
        eigenvectors = np.real(eigenvectors)
        
        return eigenvalues, eigenvectors


def apply_csp(X_train: np.ndarray,
              y_train: np.ndarray,
              X_test: np.ndarray = None,
              n_components: int = N_CSP_COMPONENTS) -> Tuple[np.ndarray, np.ndarray, CSP]:
    """
    Apply CSP feature extraction
    
    Parameters:
    -----------
    X_train : ndarray, shape (n_trials, n_channels, n_samples)
        Training data
    y_train : ndarray
        Training labels
    X_test : ndarray, optional
        Test data
    n_components : int
        Number of CSP components
        
    Returns:
    --------
    features_train : ndarray
        CSP features for training data
    features_test : ndarray or None
        CSP features for test data (if provided)
    csp : CSP
        Fitted CSP object
    """
    print(f"\n=== Applying CSP ===")
    print(f"Number of components: {n_components}")
    
    # Initialize and fit CSP
    csp = CSP(n_components=n_components)
    csp.fit(X_train, y_train)
    
    # Transform data
    features_train = csp.transform(X_train)
    print(f"Training features shape: {features_train.shape}")
    
    features_test = None
    if X_test is not None:
        features_test = csp.transform(X_test)
        print(f"Test features shape: {features_test.shape}")
    
    print("=== CSP Complete ===\n")
    
    return features_train, features_test, csp


if __name__ == "__main__":
    print("CSP feature extraction module loaded successfully")
    print(f"Default number of components: {N_CSP_COMPONENTS}")
